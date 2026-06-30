#!/usr/bin/env python3
"""
rocket_file_browser.py — Move files between the Stratio sandbox and Rocket's HDFS
File Browser, authenticating with the sandbox client certificate over mTLS.

The sandbox already mounts a client X.509 certificate whose CN is the operating
user (e.g. ``s000001-user``); Rocket runs in ``Oauth2Mutual`` mode and exposes a
mutual-TLS listener on port 7777. This client talks to that listener directly, so
every call runs with the operating user's own permissions (no impersonation).

MVP subcommands: ``filesystems``, ``download``, ``upload``.

ENVIRONMENT
    ROCKET_API_URL   Base URL (host:port) of the mutual listener, no path. Required.
                     e.g. https://rocket.s000001-rocket:7777
    USER_CERT_PATH   Client certificate (default /vault/secrets/cert.crt)
    USER_KEY_PATH    Client private key   (default /vault/secrets/cert.key)
    CA_CERT_PATH     CA bundle            (default /stratio/certs/ca.crt)
    ROCKET_TLS_VERIFY  "true" to verify the server cert against CA_CERT_PATH;
                     anything else (default) skips verification — the 7777 server
                     cert SAN usually does not cover the in-cluster service name,
                     same reason OpenCode runs with NODE_TLS_REJECT_UNAUTHORIZED=0.

USAGE
    python3 rocket_file_browser.py filesystems
    python3 rocket_file_browser.py download <hdfs_path> <local_dest> [--fs id:type]
    python3 rocket_file_browser.py upload   <local_src> <hdfs_dir>   [--fs id:type]

    --fs is "<id>:<type>" (e.g. hdfs1.s000001-datastores:HDFS). When omitted, the
    target filesystem is auto-resolved via the ``filesystems`` endpoint: if exactly
    one exists it is used; if several exist you must pass --fs explicitly.

On any non-2xx response the HTTP status and body are printed verbatim and the
process exits non-zero. This client never silently retries except for HTTP 420
on the upload commit phase (Rocket signals "upload already in progress").
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

# Rocket rejects File Browser operations on these reserved roots.
RESTRICTED_PREFIXES = (
    "/extensions",
    "/mockData",
    "/backups",
    "/mlProjectModelArtifacts",
    "/mlProjectExecutionsArtifacts",
)

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 180
UPLOAD_COMMIT_RETRIES = 5
UPLOAD_COMMIT_BACKOFF = 3  # seconds, linear


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def fail(msg: str, code: int = 1) -> "None":
    log(f"ERROR: {msg}")
    sys.exit(code)


def base_url() -> str:
    url = os.environ.get("ROCKET_API_URL", "").rstrip("/")
    if not url:
        fail(
            "ROCKET_API_URL not set. Expected the Rocket mutual-TLS base URL "
            "(host:port, no path), e.g. "
            "https://<rocket-instance>.<rocket-namespace>:7777"
        )
    return url


def tls_config() -> "tuple[tuple[str, str], object]":
    cert = os.environ.get("USER_CERT_PATH", "/vault/secrets/cert.crt")
    key = os.environ.get("USER_KEY_PATH", "/vault/secrets/cert.key")
    ca = os.environ.get("CA_CERT_PATH", "/stratio/certs/ca.crt")
    for label, path in (("USER_CERT_PATH", cert), ("USER_KEY_PATH", key)):
        if not Path(path).is_file():
            fail(f"{label} not found at {path}")
    verify: object = False
    if os.environ.get("ROCKET_TLS_VERIFY", "").lower() == "true":
        if not Path(ca).is_file():
            fail(f"ROCKET_TLS_VERIFY=true but CA_CERT_PATH not found at {ca}")
        verify = ca
    if verify is False:
        # SAN of the 7777 server cert usually does not cover the service name.
        from urllib3.exceptions import InsecureRequestWarning  # noqa: PLC0415
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # type: ignore[attr-defined]
    return (cert, key), verify


def request(method: str, path: str, **kwargs) -> requests.Response:
    cert, verify = tls_config()
    kwargs.setdefault("timeout", (CONNECT_TIMEOUT, READ_TIMEOUT))
    return requests.request(
        method, f"{base_url()}{path}", cert=cert, verify=verify, **kwargs
    )


def show_http_error(resp: requests.Response) -> "None":
    body = resp.text
    fail(f"HTTP {resp.status_code} from {resp.request.method} {resp.url}\n{body}")


def parse_fs(spec: "str | None") -> "dict | None":
    if not spec:
        return None
    if ":" not in spec:
        fail(f"--fs must be '<id>:<type>', got {spec!r}")
    fs_id, fs_type = spec.split(":", 1)
    return {"id": fs_id, "type": fs_type}


def list_filesystems() -> list:
    resp = request("GET", "/fileBrowser/getFilesystems", headers={"Accept": "application/json"})
    if not resp.ok:
        show_http_error(resp)
    return resp.json()


def resolve_target_fs(spec: "str | None") -> "dict | None":
    """Explicit --fs wins; otherwise auto-resolve when exactly one FS exists."""
    explicit = parse_fs(spec)
    if explicit is not None:
        return explicit
    systems = list_filesystems()
    if len(systems) == 1:
        fs = systems[0]
        log(f"Using filesystem {fs['id']} ({fs['type']})")
        return {"id": fs["id"], "type": fs["type"]}
    ids = ", ".join(f"{fs['id']}:{fs['type']}" for fs in systems)
    fail(f"Several filesystems available — pass --fs explicitly. Options: {ids}")
    return None  # unreachable


def guard_path(hdfs_path: str) -> None:
    norm = "/" + hdfs_path.strip("/")
    for prefix in RESTRICTED_PREFIXES:
        if norm == prefix or norm.startswith(prefix + "/"):
            fail(f"Path {hdfs_path} is under a Rocket-restricted root ({prefix}); refused.")


def cmd_filesystems(_args: argparse.Namespace) -> None:
    print(json.dumps(list_filesystems(), indent=2, ensure_ascii=False))


def cmd_download(args: argparse.Namespace) -> None:
    guard_path(args.hdfs_path)
    target_fs = resolve_target_fs(args.fs)
    payload: dict = {"pathHdfs": args.hdfs_path}
    if target_fs is not None:
        payload["targetFilesystem"] = target_fs

    dest = Path(args.local_dest)
    if dest.is_dir():
        dest = dest / Path(args.hdfs_path).name

    resp = request(
        "POST", "/fileBrowser/download",
        headers={"Content-Type": "application/json"},
        json=payload, stream=True,
    )
    if not resp.ok:
        show_http_error(resp)
    dest.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=1 << 16):
            if chunk:
                fh.write(chunk)
                written += len(chunk)
    print(f"Downloaded {args.hdfs_path} -> {dest} ({written} bytes)")


def cmd_upload(args: argparse.Namespace) -> None:
    src = Path(args.local_src)
    if not src.is_file():
        fail(f"Local source not found: {src}")
    guard_path(args.hdfs_dir)
    target_fs = resolve_target_fs(args.fs)

    # Phase 1 — push the bytes to a temp path on the Rocket pod.
    with open(src, "rb") as fh:
        resp = request(
            "POST", "/fileBrowser/uploadLocalFile",
            headers={"Accept": "application/json"},
            files={"binary": (src.name, fh)},
        )
    if not resp.ok:
        show_http_error(resp)
    docker_path = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text.strip().strip('"')
    if isinstance(docker_path, str):
        docker_path = docker_path.strip('"')
    log(f"Phase 1 OK: staged at {docker_path}")

    # Phase 2 — commit the staged file into HDFS. Retries on HTTP 420.
    payload = {"pathHdfs": args.hdfs_dir, "dockerPath": docker_path}
    if target_fs is not None:
        payload["targetFilesystem"] = target_fs

    for attempt in range(1, UPLOAD_COMMIT_RETRIES + 1):
        resp = request(
            "POST", "/fileBrowser/putLocalFileToHadoopFs",
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        if resp.status_code == 420:
            wait = UPLOAD_COMMIT_BACKOFF * attempt
            log(f"HTTP 420 (upload in progress); retry {attempt}/{UPLOAD_COMMIT_RETRIES} in {wait}s")
            time.sleep(wait)
            continue
        if not resp.ok:
            show_http_error(resp)
        print(f"Uploaded {src} -> {args.hdfs_dir}/{src.name}")
        return
    fail(f"Upload commit kept returning HTTP 420 after {UPLOAD_COMMIT_RETRIES} attempts.")


def _with_fs(payload: dict, target_fs: "dict | None") -> dict:
    if target_fs is not None:
        payload["targetFilesystem"] = target_fs
    return payload


def _post_boolean(method: str, path: str, payload: dict, success_msg: str) -> None:
    """For endpoints that return a boolean / OK on success."""
    resp = request(method, path, headers={"Content-Type": "application/json"}, json=payload)
    if not resp.ok:
        show_http_error(resp)
    print(success_msg)


def cmd_ls(args: argparse.Namespace) -> None:
    guard_path(args.hdfs_path)
    target_fs = resolve_target_fs(args.fs)
    resp = request(
        "POST", "/fileBrowser/findByPath",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=_with_fs({"pathHdfs": args.hdfs_path}, target_fs),
    )
    if not resp.ok:
        show_http_error(resp)
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


def cmd_mkdir(args: argparse.Namespace) -> None:
    guard_path(args.hdfs_path)
    target_fs = resolve_target_fs(args.fs)
    _post_boolean(
        "POST", "/fileBrowser/createDir",
        _with_fs({"pathHdfs": args.hdfs_path}, target_fs),
        f"Created directory {args.hdfs_path}",
    )


def cmd_rm(args: argparse.Namespace) -> None:
    for p in args.hdfs_paths:
        guard_path(p)
    target_fs = resolve_target_fs(args.fs)
    _post_boolean(
        "DELETE", "/fileBrowser/delete",
        _with_fs({"files": [{"path": p} for p in args.hdfs_paths]}, target_fs),
        f"Deleted: {', '.join(args.hdfs_paths)}",
    )


def cmd_cp(args: argparse.Namespace) -> None:
    guard_path(args.src)
    guard_path(args.dst)
    target_fs = resolve_target_fs(args.fs)
    _post_boolean(
        "PUT", "/fileBrowser/copy",
        _with_fs({"files": [{"path": args.src, "newPath": args.dst}]}, target_fs),
        f"Copied {args.src} -> {args.dst}",
    )


def cmd_mv(args: argparse.Namespace) -> None:
    guard_path(args.src)
    guard_path(args.dst)
    target_fs = resolve_target_fs(args.fs)
    _post_boolean(
        "PUT", "/fileBrowser/update",
        _with_fs({"files": [{"path": args.src, "newPath": args.dst}]}, target_fs),
        f"Moved {args.src} -> {args.dst}",
    )


def cmd_compress(args: argparse.Namespace) -> None:
    for p in args.sources:
        guard_path(p)
    guard_path(args.archive)
    target_fs = resolve_target_fs(args.fs)
    log(
        "Note: Rocket appends the codec extension to the archive name "
        f"(e.g. {args.archive} -> {args.archive}.<ext>). Use that full name to extract."
    )
    _post_boolean(
        "PUT", "/fileBrowser/compress",
        _with_fs(
            {
                "files": list(args.sources),
                "compressedFile": args.archive,
                "compressionCodec": args.codec,
            },
            target_fs,
        ),
        f"Compressed {len(args.sources)} item(s) -> {args.archive} ({args.codec})",
    )


def cmd_extract(args: argparse.Namespace) -> None:
    guard_path(args.archive)
    entry = {"path": args.archive}
    if args.dest:
        guard_path(args.dest)
        entry["newPath"] = args.dest
    target_fs = resolve_target_fs(args.fs)
    _post_boolean(
        "PUT", "/fileBrowser/extract",
        _with_fs({"files": [entry]}, target_fs),
        f"Extracted {args.archive}" + (f" -> {args.dest}" if args.dest else ""),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rocket File Browser client (mTLS).")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("filesystems", help="List available filesystems (id/type/defaultPath).")

    p_dl = sub.add_parser("download", help="Download an HDFS file to the local workspace.")
    p_dl.add_argument("hdfs_path")
    p_dl.add_argument("local_dest", help="Local file path or directory.")
    p_dl.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_up = sub.add_parser("upload", help="Upload a local file into an HDFS directory.")
    p_up.add_argument("local_src")
    p_up.add_argument("hdfs_dir", help="Target HDFS directory.")
    p_up.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_ls = sub.add_parser("ls", help="List the contents of an HDFS path.")
    p_ls.add_argument("hdfs_path")
    p_ls.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_mkdir = sub.add_parser("mkdir", help="Create a directory in HDFS.")
    p_mkdir.add_argument("hdfs_path")
    p_mkdir.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_rm = sub.add_parser("rm", help="Delete one or more HDFS files/directories.")
    p_rm.add_argument("hdfs_paths", nargs="+", help="One or more HDFS paths.")
    p_rm.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_cp = sub.add_parser("cp", help="Copy an HDFS file/directory to a new path.")
    p_cp.add_argument("src")
    p_cp.add_argument("dst")
    p_cp.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_mv = sub.add_parser("mv", help="Move/rename an HDFS file/directory.")
    p_mv.add_argument("src")
    p_mv.add_argument("dst")
    p_mv.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_cmp = sub.add_parser("compress", help="Compress HDFS files into a new archive.")
    p_cmp.add_argument("archive", help="Target compressed file path in HDFS.")
    p_cmp.add_argument("sources", nargs="+", help="One or more HDFS paths to compress.")
    p_cmp.add_argument(
        "--codec",
        default="Zip",
        choices=["ZStandard", "Lz4", "Snappy", "Gzip", "Bzip2", "Zip", "TarGz"],
        help="Compression codec (default: Zip).",
    )
    p_cmp.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")

    p_ext = sub.add_parser("extract", help="Extract an HDFS archive.")
    p_ext.add_argument("archive", help="HDFS archive path to extract.")
    p_ext.add_argument("--dest", help="Optional target HDFS directory.")
    p_ext.add_argument("--fs", help="Target filesystem as '<id>:<type>'.")
    return parser


def main(argv: "list[str] | None" = None) -> None:
    args = build_parser().parse_args(argv)
    {
        "filesystems": cmd_filesystems,
        "download": cmd_download,
        "upload": cmd_upload,
        "ls": cmd_ls,
        "mkdir": cmd_mkdir,
        "rm": cmd_rm,
        "cp": cmd_cp,
        "mv": cmd_mv,
        "compress": cmd_compress,
        "extract": cmd_extract,
    }[args.command](args)


if __name__ == "__main__":
    main()
