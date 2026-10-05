#!/usr/bin/env python3
"""Command-line access to Stratio artifacts, for use from inside a Cowork sandbox.

Standard library only: nothing guarantees httpx or requests in the agent's
environment, and the bootstrap client this mirrors uses urllib for the same reason.

Authentication is the pod's own certificate. Its CN is the run-as identity — for a
project, its owner — so this script already *is* the user. Three rules follow:

* never send X-Client-UID. The API honours it, and forging it from inside a sandbox
  would be a privilege escalation;
* never call the genai-proxy. GENAI_API_URL points at the api role; the proxy is
  read-only and is not reachable under that name;
* never build an artifact link. The API answers `public_url`, the genai-ui page the
  user opens, from its own configuration.
"""

import argparse
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import NoReturn

DEFAULT_CERT = "/vault/secrets/cert.crt"
DEFAULT_KEY = "/vault/secrets/cert.key"
DEFAULT_CA = "/stratio/certs/ca.crt"

_UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
# Both the genai-ui page (`.../artifacts/<id>`) and the legacy genai-proxy link
# (`.../v1/artifacts/<id>/content`) carry the id right after an `artifacts` segment.
_LINKED_ID = re.compile(rf"/artifacts/({_UUID})(?=[/?#]|$)")
_BARE_ID = re.compile(rf"^{_UUID}$")

_FORBIDDEN = (
    "Your role on this artifact does not allow this. A reader can only read it; an "
    "editor can also change its content, title and tags; only an owner can share "
    "or delete it. Do not retry."
)


def _context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(os.environ.get("CA_CERT_PATH", DEFAULT_CA))
    ctx.load_cert_chain(
        os.environ.get("USER_CERT_PATH", DEFAULT_CERT),
        os.environ.get("USER_KEY_PATH", DEFAULT_KEY),
    )
    return ctx


def _base() -> str:
    base = os.environ.get("GENAI_API_URL")
    if not base:
        _die("GENAI_API_URL is not set; this script only runs inside a sandbox.")
    return base.rstrip("/")


def _die(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def _call(method: str, path: str, payload=None, raw: bytes = None, content_type=None):
    url = f"{_base()}{path}"
    headers = {"Accept": "application/json"}
    body = raw
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(
            request, context=_context(), timeout=60
        ) as response:
            content = response.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        if e.code == 403 and method != "GET":
            _die(f"{method} {path} was refused (403). {_FORBIDDEN} {detail}")
        _die(f"{method} {path} failed with {e.code}: {detail}")
    except urllib.error.URLError as e:
        _die(f"{method} {path} could not reach the API: {e.reason}")
    if not content:
        return None
    try:
        return json.loads(content)
    except ValueError:
        return content.decode("utf-8", "replace")


# The images a page may show, stored next to it. The API checks the bytes as well.
_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")


def _is_image(file_path: str) -> bool:
    return file_path.lower().endswith(_IMAGE_EXTENSIONS)


def _multipart(filename: str, content: bytes) -> tuple[bytes, str]:
    """A one-file multipart/form-data body, as /upload expects it."""
    boundary = f"----stratio-artifact-{uuid.uuid4().hex}"
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename.replace(chr(34), "")}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    return head + content + f"\r\n--{boundary}--\r\n".encode("utf-8"), (
        f"multipart/form-data; boundary={boundary}"
    )


def _upload(artifact_id: str, stored_path: str, local_path: str):
    with open(local_path, "rb") as handle:
        body, content_type = _multipart(os.path.basename(stored_path), handle.read())
    return _call(
        "POST",
        f"/v1/artifacts/{artifact_id}/upload/{_quote(stored_path)}",
        raw=body,
        content_type=content_type,
    )


def _quote(file_path: str) -> str:
    return urllib.parse.quote(file_path, safe="/")


def _emit(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def _tags(value: str) -> list:
    """`a, b,,a` -> ["a", "b"]. An empty string is an empty list, i.e. no tags."""
    return list(dict.fromkeys(t.strip() for t in value.split(",") if t.strip()))


def _summary(artifact: dict) -> dict:
    """The fields the agent acts on. `public_url` is the link to hand the user."""
    return {
        key: artifact.get(key)
        for key in (
            "id",
            "title",
            "type",
            "access_role",
            "can_edit",
            "can_manage",
            "link_access",
            "tags",
            "is_pinned",
            "file_count",
            "updated_at",
            "public_url",
        )
    }


def _listing(result) -> list:
    if not isinstance(result, dict) or "artifacts" not in result:
        _die(f"Unexpected response from the artifacts API: {result!r}")
    return [_summary(a) for a in result["artifacts"]]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_list(args):
    query = urllib.parse.urlencode(
        {
            k: v
            for k, v in (
                ("scope", args.scope),
                ("search", args.search),
                ("tags", ",".join(_tags(args.tags)) if args.tags else None),
                ("type", args.type),
                ("pinned", "true" if args.pinned else None),
                ("page", args.page),
                ("page_size", args.page_size),
            )
            if v
        }
    )
    _emit(_listing(_call("GET", f"/v1/artifacts?{query}")))


def _stored_path(local_path: str, base: str) -> str:
    """Where a local file lands inside the artifact.

    Relative to --base when it sits under it, so `--base . --file data/notes.md`
    keeps its directory; just the file name otherwise. Keeping the directory is the
    only way an artifact created in one call is multi-file in any structured sense.
    """
    relative = os.path.relpath(os.path.abspath(local_path), os.path.abspath(base))
    if relative.startswith(".."):
        return os.path.basename(local_path)
    return relative.replace(os.sep, "/")


def cmd_create(args):
    paths = args.file or []
    if args.rename and len(paths) != 1:
        _die("--rename renames one file; pass exactly one --file with it.")
    files, images = [], []
    for path in paths:
        name = args.rename or _stored_path(path, args.base or os.curdir)
        if _is_image(name):
            # Binary: it goes up once the artifact exists, through /upload.
            images.append((name, path))
            continue
        with open(path, "r", encoding="utf-8") as handle:
            files.append({"file_path": name, "content": handle.read()})
    if images and not files:
        _die("An artifact is a page: pass its .html or .md file along with the images.")
    payload = {
        "title": args.title,
        "type": args.type,
        "description": args.description,
        "files": files,
    }
    if args.tags:
        payload["tags"] = _tags(args.tags)
    if args.entry_path:
        payload["entry_path"] = args.entry_path
    elif files:
        payload["entry_path"] = files[0]["file_path"]
    # Provenance. The agent is the only thing that knows the conversation, so if it
    # does not send it the column is dead and so is the listing filter over it.
    if os.environ.get("PROJECT_ID"):
        payload["origin_project_id"] = os.environ["PROJECT_ID"]
    conversation = args.conversation or os.environ.get("CONVERSATION_ID")
    if conversation:
        payload["origin_conversation_id"] = conversation
    created = _call("POST", "/v1/artifacts", payload)
    if not images:
        _emit(created)
        return
    for name, path in images:
        try:
            _upload(created["id"], name, path)
        except SystemExit:
            print(
                f"Artifact {created['id']} was created without {name} and any image "
                "after it: upload them with `upload`.",
                file=sys.stderr,
            )
            raise
    _emit(_call("GET", f"/v1/artifacts/{created['id']}"))


def cmd_get(args):
    _emit(_call("GET", f"/v1/artifacts/{args.artifact_id}"))


def cmd_files(args):
    _emit(_call("GET", f"/v1/artifacts/{args.artifact_id}/files"))


def cmd_read(args):
    result = _call("GET", f"/v1/artifacts/{args.artifact_id}/files/{_quote(args.path)}")
    # Raw, not JSON: this is what gets edited and written back.
    sys.stdout.write(result["content"])


def cmd_write(args):
    if args.from_file:
        with open(args.from_file, "r", encoding="utf-8") as handle:
            content = handle.read()
    else:
        content = sys.stdin.read()
    _emit(
        _call(
            "PUT",
            f"/v1/artifacts/{args.artifact_id}/files/{_quote(args.path)}",
            {"content": content},
        )
    )


def cmd_upload(args):
    """Add or replace one of the images a page shows (png, jpg, gif, webp, svg)."""
    if not _is_image(args.path):
        _die(
            f"{args.path} is not an image. `upload` carries the images a page shows "
            "(" + ", ".join(_IMAGE_EXTENSIONS) + "); write a page with `write`."
        )
    _emit(_upload(args.artifact_id, args.path, args.from_file))


def cmd_rm(args):
    _emit(
        _call("DELETE", f"/v1/artifacts/{args.artifact_id}/files/{_quote(args.path)}")
    )


def cmd_delete(args):
    _emit(_call("DELETE", f"/v1/artifacts/{args.artifact_id}"))


def cmd_rename(args):
    _emit(_call("PATCH", f"/v1/artifacts/{args.artifact_id}", {"title": args.title}))


def cmd_tag(args):
    tags = [] if args.clear else _tags(args.set)
    _emit(_call("PATCH", f"/v1/artifacts/{args.artifact_id}", {"tags": tags}))


def cmd_copy(args):
    payload = {"title": args.title} if args.title else {}
    _emit(_summary(_call("POST", f"/v1/artifacts/{args.artifact_id}/copy", payload)))


def cmd_members(args):
    _emit(_call("GET", f"/v1/artifacts/{args.artifact_id}/members"))


def _members(current: list, ids: list, role: str, remove: bool) -> list:
    """The share list after this call: `ids` taken off it, or added at `role`.

    An id already on the list keeps its place but takes the new role, so sharing
    again is also how someone's role changes.
    """
    merged = {m["id"]: m["role"] for m in current}
    for member_id in ids:
        if remove:
            merged.pop(member_id, None)
        else:
            merged[member_id] = role
    return [{"id": k, "role": v} for k, v in merged.items()]


def cmd_share(args):
    ids = {
        "users": list(dict.fromkeys(args.user or [])),
        "groups": list(dict.fromkeys(args.group or [])),
    }
    named = ids["users"] or ids["groups"]
    if args.remove and not named:
        _die("--remove needs the --user/--group ids to take off the share list.")
    if not (named or args.link or args.replace):
        _die("Nothing to share: pass --user, --group or --link.")
    # The endpoint replaces the whole share list, so adding one person without
    # merging first would silently un-share the artifact from everybody else. A
    # bare --link change needs the merge too, for the same reason.
    current = (
        {}
        if args.replace
        else _call("GET", f"/v1/artifacts/{args.artifact_id}/members")
    )
    body = {
        kind: _members(current.get(kind, []), ids[kind], args.role, args.remove)
        for kind in ("users", "groups")
    }
    if args.link:
        body["link_access"] = "reader" if args.link == "on" else "none"
    _emit(_call("PUT", f"/v1/artifacts/{args.artifact_id}/members", body))


def cmd_url(args):
    artifact = _call("GET", f"/v1/artifacts/{args.artifact_id}")
    if not artifact.get("public_url"):
        _die("No link available: the API returned no public_url for this artifact.")
    print(artifact["public_url"])


def _artifact_id(ref: str):
    """The id a link or a bare id names; None when `ref` is neither."""
    ref = ref.strip()
    if _BARE_ID.match(ref):
        return ref.lower()
    linked = _LINKED_ID.search(ref)
    return linked.group(1).lower() if linked else None


def cmd_resolve(args):
    """Turn whatever the user gave (a link, an id, a name) into artifacts to act on.

    Always a list: one entry for a link or an id, every candidate for a name, so a
    name that matches several can be put to the user instead of guessed.
    """
    artifact_id = _artifact_id(args.ref)
    if artifact_id:
        _emit([_summary(_call("GET", f"/v1/artifacts/{artifact_id}"))])
        return
    if re.match(r"^[a-z][a-z0-9+.-]*://", args.ref.strip(), re.IGNORECASE):
        _die(f"{args.ref} is not a link to an artifact: it names no artifact id.")
    query = urllib.parse.urlencode(
        {"search": args.ref.strip(), "scope": "all", "page_size": 10}
    )
    candidates = _listing(_call("GET", f"/v1/artifacts?{query}"))
    if not candidates:
        _die(f"No artifact you can see matches {args.ref!r}.")
    _emit(candidates)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stratio artifacts")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list")
    p.add_argument("--scope", choices=("mine", "shared", "all"), default="all")
    p.add_argument("--search", help="Free text; also matches tags")
    p.add_argument("--tags", help="Comma-separated; an artifact must carry them all")
    p.add_argument("--type", choices=("markdown", "html"))
    p.add_argument("--pinned", action="store_true", help="Only pinned artifacts")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", dest="page_size", type=int, default=50)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("resolve")
    p.add_argument("ref", help="A genai-ui link, an artifact id, or a name to search")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.add_argument("--type", choices=("markdown", "html"), default="html")
    p.add_argument("--description")
    p.add_argument("--tags", help="Comma-separated, e.g. ventas,q3,informe")
    p.add_argument("--entry-path", dest="entry_path")
    p.add_argument("--rename", help="Store a single --file under this path instead")
    p.add_argument(
        "--base",
        help="Directory the --file paths are stored relative to (default: cwd)",
    )
    p.add_argument("--conversation", help="Conversation this artifact came from")
    p.add_argument("--file", action="append")
    p.set_defaults(func=cmd_create)

    for name, func in (
        ("get", cmd_get),
        ("files", cmd_files),
        ("members", cmd_members),
        ("delete", cmd_delete),
    ):
        p = sub.add_parser(name)
        p.add_argument("artifact_id")
        p.set_defaults(func=func)

    for name, func in (("read", cmd_read), ("rm", cmd_rm)):
        p = sub.add_parser(name)
        p.add_argument("artifact_id")
        p.add_argument("path")
        p.set_defaults(func=func)

    p = sub.add_parser("write")
    p.add_argument("artifact_id")
    p.add_argument("path")
    p.add_argument("--from-file", dest="from_file")
    p.set_defaults(func=cmd_write)

    p = sub.add_parser("upload")
    p.add_argument("artifact_id")
    p.add_argument("path", help="Where the image goes in the artifact, e.g. img/logo.png")
    p.add_argument("--from-file", dest="from_file", required=True)
    p.set_defaults(func=cmd_upload)

    p = sub.add_parser("rename")
    p.add_argument("artifact_id")
    p.add_argument("title")
    p.set_defaults(func=cmd_rename)

    p = sub.add_parser("tag")
    p.add_argument("artifact_id")
    tags = p.add_mutually_exclusive_group(required=True)
    tags.add_argument("--set", help="Comma-separated; replaces every current tag")
    tags.add_argument("--clear", action="store_true", help="Remove every tag")
    p.set_defaults(func=cmd_tag)

    p = sub.add_parser("copy")
    p.add_argument("artifact_id")
    p.add_argument("--title", help="Title of the copy (default: the API's choice)")
    p.set_defaults(func=cmd_copy)

    p = sub.add_parser("share")
    p.add_argument("artifact_id")
    p.add_argument("--user", action="append")
    p.add_argument("--group", action="append")
    p.add_argument(
        "--role",
        choices=("reader", "editor", "owner"),
        default="reader",
        help="Role for the --user/--group ids of this call (default: reader)",
    )
    p.add_argument(
        "--link",
        choices=("on", "off"),
        help="on: any authenticated Stratio user with the link can read it",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--replace",
        action="store_true",
        help="Replace the share list instead of adding to it",
    )
    mode.add_argument(
        "--remove",
        action="store_true",
        help="Take the given --user/--group ids off the share list",
    )
    p.set_defaults(func=cmd_share)

    p = sub.add_parser("url")
    p.add_argument("artifact_id")
    p.set_defaults(func=cmd_url)
    return parser


def main(argv=None) -> None:
    args = _parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
