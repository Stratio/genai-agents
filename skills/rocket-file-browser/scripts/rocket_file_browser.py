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
    ROCKET_API_URL   Base URL incl. the ``/rocket`` prefix. Required.
                     e.g. https://rocket.s000001-rocket.svc.fifteen.int:7777/rocket
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
            "ROCKET_API_URL not set. Expected the Rocket mutual-TLS base URL incl. "
            "the /rocket prefix, e.g. "
            "https://rocket.<tenant>-rocket.svc.<cluster-domain>:7777/rocket"
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
    return parser


def main(argv: "list[str] | None" = None) -> None:
    args = build_parser().parse_args(argv)
    {"filesystems": cmd_filesystems, "download": cmd_download, "upload": cmd_upload}[args.command](args)


if __name__ == "__main__":
    main()
