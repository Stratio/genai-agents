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

Inside a project every call also names it, in X-Genai-Project-Id, and the
conversation, in X-Genai-Conversation-Id, so the API remembers which artifacts this
project read, edited or created across all its conversations, and in which one each
was last touched; `recent` lists them. The API decides which calls count, not this
script.
"""

import argparse
import html
import json
import os
import re
import ssl
import sys
import unicodedata
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
    if os.environ.get("PROJECT_ID"):
        headers["X-Genai-Project-Id"] = os.environ["PROJECT_ID"]
    if os.environ.get("CONVERSATION_ID"):
        headers["X-Genai-Conversation-Id"] = os.environ["CONVERSATION_ID"]
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


# The binary files a page uses, stored next to it: images, fonts, audio and video.
# They go up through /upload; pages, stylesheets, scripts and subtitles are text and
# go in the JSON. The API checks the bytes as well.
_BINARY_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".woff2", ".woff", ".ttf", ".otf",
    ".mp4", ".webm", ".mp3", ".m4a", ".ogg", ".wav",
)  # fmt: skip
_PAGE_EXTENSIONS = (".html", ".htm", ".md", ".markdown")


def _is_binary(file_path: str) -> bool:
    return file_path.lower().endswith(_BINARY_EXTENSIONS)


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


def _summary(artifact: dict, extra: tuple = ()) -> dict:
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
            "is_favorite",
            "file_count",
            "updated_at",
            "public_url",
            *extra,
        )
    }


def _listing(result, extra: tuple = ()) -> list:
    if not isinstance(result, dict) or "artifacts" not in result:
        _die(f"Unexpected response from the artifacts API: {result!r}")
    return [_summary(a, extra) for a in result["artifacts"]]


def _page(result, args, extra: tuple = ()) -> list:
    """One page of a listing. stdout holds only that page, so when more follow it
    says so on stderr — otherwise the agent takes the first page for all of them."""
    page = _listing(result, extra)
    total = result.get("total", 0)
    if (args.page - 1) * args.page_size + len(page) < total:
        print(
            f"Page {args.page}: {len(page)} of {total} artifacts. "
            f"More with --page {args.page + 1}.",
            file=sys.stderr,
        )
    return page


# ---------------------------------------------------------------------------
# Working folder
# ---------------------------------------------------------------------------


def _workdir_root() -> str:
    """Where every artifact's working folder lives: ARTIFACT_WORKDIR, which the sandbox
    sets to $USER_WORKSPACE/project/.artifact. An older sandbox does not set it, so the
    same path is built here. Always under project/: the folder the person sees in the
    file browser, and the one OpenCode writes to without a permission prompt."""
    root = os.environ.get("ARTIFACT_WORKDIR")
    if not root:
        workspace = os.environ.get("USER_WORKSPACE") or "/root"
        root = os.path.join(workspace, "project", ".artifact")
    return os.path.abspath(root)


def _slug(name: str) -> str:
    """'Informe de ventas Q3' -> 'informe-de-ventas-q3'."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")
    return slug[:60].strip("-") or "artifact"


# ---------------------------------------------------------------------------
# Page checks
#
# What the viewer's sandbox breaks silently, and the slips that cost most in a review of
# real runs, caught before a page is stored. Heuristics over the text, not a browser:
# each finding says what to change, and a page can keep one when the person asked for it.
# ---------------------------------------------------------------------------

_CDN_HOSTS = (
    "cdnjs.cloudflare.com", "cdn.jsdelivr.net", "unpkg.com", "cdn.plot.ly",
    "cdn.tailwindcss.com", "code.jquery.com", "fonts.googleapis.com", "fonts.gstatic.com",
)  # fmt: skip
_FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
_COLOR = re.compile(
    r"#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3,4}\b|\b(?:rgba?|hsla?|oklch|oklab)\("
)
_NAMED_COLOR = re.compile(
    r"\b(?:color|background(?:-color)?|fill|stroke|border(?:-color)?)\s*:\s*(?:white|black)\b", re.I
)
_ROOT_BLOCK = re.compile(r":root\b[^{]*\{[^{}]*\}")
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF✀-➿]")
_TITLE_SEPARATOR = re.compile(r"\s[-–—|·]\s|[:|—–]")
_VERSIONED = re.compile(r"@v?\d+\.\d+\.\d+|/v?\d+\.\d+\.\d+(?:/|$)|[-.]v?\d+\.\d+\.\d+")


def _without_minmax(tracks: str) -> str:
    """A grid track list without its minmax(…) tracks, nested min()/calc() included:
    what is left are the tracks whose minimum is the content's own width."""
    previous = None
    while previous != tracks:
        previous = tracks
        tracks = re.sub(r"\b(?:min|max|clamp|calc)\([^()]*\)", "0", tracks)
    return re.sub(r"minmax\([^()]*\)", "", tracks)


def _strip_comments(text: str) -> str:
    return re.sub(r"(?s)/\*.*?\*/", "", re.sub(r"(?s)<!--.*?-->", "", text))


def _blocks(markup: str, tag: str) -> str:
    return "\n".join(re.findall(rf"(?is)<{tag}\b(?![^>]*\bsrc=)[^>]*>(.*?)</{tag}>", markup))


def _local_assets(markup: str, base_dir: str) -> tuple[str, str]:
    """The stylesheets and scripts the page names by relative path, as the viewer would
    put them inside it."""
    css, js = [], []
    for pattern, sink in (
        (r'(?i)<link\b[^>]*rel=["\']?stylesheet[^>]*href=["\']([^"\']+)', css),
        (r'(?i)<script\b[^>]*\bsrc=["\']([^"\']+)', js),
    ):
        for ref in re.findall(pattern, markup):
            if re.match(r"(?i)^(?:[a-z][a-z0-9+.-]*:|//)", ref):
                continue
            path = os.path.join(base_dir, ref.split("?")[0].split("#")[0])
            if os.path.isfile(path):
                with open(path, encoding="utf-8", errors="replace") as handle:
                    sink.append(handle.read())
    return "\n".join(css), "\n".join(js)


def _loaded_urls(markup: str, css: str) -> list:
    """Absolute URLs the page loads (not the links a reader may follow)."""
    no_anchors = re.sub(r"(?is)<a\b[^>]*>", "<a>", markup)
    urls = re.findall(r'(?i)<(?:script|link|img|source|video|audio|track|iframe)\b[^>]*?\s(?:src|href)=["\'](https?://[^"\']+)', no_anchors)
    urls += re.findall(r"(?i)url\(\s*['\"]?(https?://[^'\")\s]+)", css)
    urls += re.findall(r"(?i)@import\s+(?:url\()?\s*['\"]?(https?://[^'\")\s;]+)", css)
    urls += re.findall(r"(?i)\b(?:fetch|import)\(\s*['\"](https?://[^'\"]+)", markup)
    return list(dict.fromkeys(urls))


def _url_exists(url: str):
    """True or False when the CDN answered; None when it could not be asked."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "stratio-artifacts-check"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status < 400
    except urllib.error.HTTPError as e:
        return e.code < 400 if e.code != 405 else None
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _page_findings(text, base_dir=".", title=None, sources=None, verify=False) -> list:
    """Findings for one HTML page: [{"rule", "message"}]. `sources` are the hosts the
    installation lets a page load from (None: do not check hosts); `verify` asks each
    CDN whether the library URL exists."""
    findings = []

    def add(rule, message):
        findings.append({"rule": rule, "message": message})

    markup = _strip_comments(text)
    linked_css, linked_js = _local_assets(markup, base_dir)
    css = _blocks(markup, "style") + "\n" + _strip_comments(linked_css)
    scripts = _blocks(markup, "script") + "\n" + linked_js

    if not re.match(r"(?is)\s*<!doctype html", text):
        add("document", "Start with <!doctype html>: the file is served as it is.")
    for rule, pattern, what in (
        ("document", r"(?i)<meta[^>]+charset", '<meta charset="utf-8">'),
        ("document", r'(?i)<meta[^>]+name=["\']viewport', "the viewport <meta>"),
    ):
        if not re.search(pattern, markup):
            add(rule, f"Missing {what}.")
    found = re.search(r"(?is)<title[^>]*>(.*?)</title>", markup)
    page_title = re.sub(r"\s+", " ", html.unescape(found.group(1))).strip() if found else ""
    if not page_title:
        add("title", "Missing <title>: write it first and pass the same string as --title.")
    elif title is not None and page_title != title.strip():
        add("title", f"<title> is {page_title!r} but --title is {title!r}: use one string for both.")
    for name in {page_title, (title or "").strip()} - {""}:
        if _TITLE_SEPARATOR.search(name):
            add("title", f"{name!r} has a separator: a title is a 2-4 word name, the rest goes in --description.")
        if len(name.split()) > 4:
            add("title", f"{name!r} has {len(name.split())} words: a title is 2-4.")

    if not re.search(r"prefers-color-scheme\s*:\s*dark", css):
        add("dark-mode", "No @media (prefers-color-scheme: dark) block redefining the tokens.")
    outside = _ROOT_BLOCK.sub("", css)
    styles = " ".join(re.findall(r'(?i)\sstyle=["\']([^"\']*)', markup))
    svg_attrs = " ".join(re.findall(r'(?i)\s(?:fill|stroke|stop-color|color)=["\'](#[0-9a-f]{3,8})', markup))
    script_colors = re.findall(r"['\"](#[0-9a-fA-F]{3,8}|(?:rgba?|hsla?)\([^'\"]*\))['\"]", scripts)
    colors = (
        _COLOR.findall(outside) + _NAMED_COLOR.findall(outside) + _COLOR.findall(styles)
        + _NAMED_COLOR.findall(styles) + _COLOR.findall(svg_attrs) + script_colors
    )
    if colors:
        sample = ", ".join(dict.fromkeys(c.strip() for c in colors))
        add("colors", f"{len(colors)} colors outside the token block ({sample[:120]}): use var(--…) in "
            "CSS, style attributes and SVG, --on-primary/--on-accent for text on fills, and in a chart "
            "script read the tokens with getComputedStyle(document.documentElement).")

    if re.search(r"(?i)<form\b|type=[\"']?submit\b", markup):
        add("form", "The viewer blocks form submission before the submit event, so a submit handler "
            "never runs, not even with preventDefault(). Put the fields in a <div> and use "
            '<button type="button">.')
    if re.search(r"(?i)target=[\"']?_blank|window\.open\(", markup):
        add("new-tab", "target=_blank and window.open do nothing in the viewer: write external URLs as visible text.")
    if re.search(r"(?:\bwindow\.|(?<![\w.$]))(?:alert|confirm|prompt)\s*\(", scripts):
        add("dialog", "alert/confirm/prompt: use inline UI instead.")
    if re.search(r"(?i)<a\b[^>]*\sdownload\b|\.download\s*=", markup):
        add("download", "Downloads are blocked in the viewer.")
    if re.search(r"(?i)<iframe\b", markup):
        add("iframe", "No <iframe> of another page.")
    if re.search(r"\b(?:localStorage|sessionStorage|indexedDB)\b|document\.cookie", scripts) and not re.search(r"\btry\s*\{", scripts):
        add("storage", "Storage throws in the viewer's opaque origin: keep state in memory, and wrap any storage access in try/catch.")
    if re.search(r"(?i)<table\b[^>]*class=[\"'][^\"']*\bscroll-x\b", markup):
        add("responsive", 'The .scroll-x class goes on a wrapper, not on the table: <div class="scroll-x"><table>…</table></div>.')
    if re.search(r"(?i)<pre\b", markup):
        # A bare 1fr track is minmax(auto, 1fr): a <pre> inside it widens the column.
        bare = [v.strip() for v in re.findall(r"grid-template-columns\s*:\s*([^;}{]+)", css)
                if re.search(r"\d*\.?\d+fr\b", _without_minmax(v))]
        if bare:
            add("responsive", f"grid-template-columns: {bare[0]} can widen past a 400 px pane when a cell "
                "holds code or a table: use minmax(0, 1fr) tracks and min-width: 0 on those children.")
    if re.search(r"(?:min-)?height\s*:\s*100d?vh", css):
        add("hero", "A 100vh block: the header fits its content.")
    if re.search(r"opacity\s*:\s*0\s*[;}]", css) and "IntersectionObserver" in scripts:
        add("reveal", "Content waits at opacity: 0 for a scroll: everything meant to be read is visible on load.")
    if re.search(r"(?i)genai-ui[\w-]*/artifacts/|/v1/artifacts/", markup):
        add("link", "A GenAI UI or API address inside the page: write the other artifact's title and id instead.")
    for heading in re.findall(r"(?is)<h[1-6]\b[^>]*>(.*?)</h[1-6]>", markup):
        if _EMOJI.search(heading):
            add("emoji", "Emojis as section markers read as machine-made.")
            break

    urls = _loaded_urls(markup, css)
    if sources is not None:
        allowed = {urllib.parse.urlsplit(s).hostname for s in sources if urllib.parse.urlsplit(s).hostname}
        for url in urls:
            host = urllib.parse.urlsplit(url).hostname
            if host not in allowed:
                where = "nothing outside the artifact" if not allowed else ", ".join(sorted(allowed))
                add("host", f"{url}: this installation lets a page load from {where}.")
    for url in urls:
        host = urllib.parse.urlsplit(url).hostname or ""
        if host in _CDN_HOSTS and host not in _FONT_HOSTS:
            path = urllib.parse.urlsplit(url).path
            if host != "cdn.tailwindcss.com" and not _VERSIONED.search(path):
                add("pin", f"{url}: pin the exact version.")
            elif verify and _url_exists(url) is False:
                add("cdn", f"{url} does not exist on that CDN: copy the URL from the library table in SKILL.md.")
    return findings


def _report_findings(label: str, findings: list) -> None:
    for finding in findings:
        print(f"check: {label}: [{finding['rule']}] {finding['message']}", file=sys.stderr)


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
                ("favorite", "true" if args.favorite else None),
                ("page", args.page),
                ("page_size", args.page_size),
            )
            if v
        }
    )
    _emit(_page(_call("GET", f"/v1/artifacts?{query}"), args))


def cmd_recent(args):
    """What this project read, edited or created, in any of its conversations, last
    touched first. Listing an artifact or looking at its metadata does not count."""
    project_id = os.environ.get("PROJECT_ID")
    if not project_id:
        _die("PROJECT_ID is not set: `recent` lists a project's artifacts, and this "
             "sandbox does not run a project.")
    query = urllib.parse.urlencode(
        {"project_id": project_id, "page": args.page, "page_size": args.page_size}
    )
    _emit(
        _page(
            _call("GET", f"/v1/artifacts/accessed?{query}"),
            args,
            extra=("last_access", "last_accessed_at", "last_conversation_id"),
        )
    )


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
    files, binaries, local = [], [], {}
    for path in paths:
        name = args.rename or _stored_path(path, args.base or os.curdir)
        if _is_binary(name):
            # It goes up once the artifact exists, through /upload.
            binaries.append((name, path))
            continue
        with open(path, "r", encoding="utf-8") as handle:
            files.append({"file_path": name, "content": handle.read()})
        local[name] = path
    if paths and not any(f["file_path"].lower().endswith(_PAGE_EXTENSIONS) for f in files):
        _die(
            "An artifact is a page: pass its .html or .md file along with the files "
            "it uses."
        )
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
    # Warnings, never a refusal: the person may have asked for what a check flags.
    if not args.description:
        print("check: no --description: pass one sentence that says what it is.", file=sys.stderr)
    tags = payload.get("tags") or []
    if not 3 <= len(tags) <= 5 or any(t != t.lower() for t in tags):
        print("check: --tags: 3 to 5 short lowercase topic tags find it later.", file=sys.stderr)
    for f in files:
        if f["file_path"].lower().endswith((".html", ".htm")):
            title = args.title if f["file_path"] == payload.get("entry_path") else None
            _report_findings(
                f["file_path"],
                _page_findings(f["content"], os.path.dirname(local[f["file_path"]]) or ".", title),
            )
    # Provenance. The agent is the only thing that knows the conversation, so if it
    # does not send it the column is dead and so is the listing filter over it. The
    # sandbox sets CONVERSATION_ID in every shell to the conversation's root OpenCode
    # session id; the API names the project itself.
    if os.environ.get("PROJECT_ID"):
        payload["origin_project_id"] = os.environ["PROJECT_ID"]
    conversation = args.conversation or os.environ.get("CONVERSATION_ID")
    if conversation:
        payload["origin_conversation_id"] = conversation
    created = _call("POST", "/v1/artifacts", payload)
    if not binaries:
        _emit(created)
        return
    for name, path in binaries:
        try:
            _upload(created["id"], name, path)
        except SystemExit:
            print(
                f"Artifact {created['id']} was created without {name} and any file "
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
    if args.path.lower().endswith((".html", ".htm")):
        base_dir = os.path.dirname(args.from_file) if args.from_file else "."
        _report_findings(args.path, _page_findings(content, base_dir or "."))
    _emit(
        _call(
            "PUT",
            f"/v1/artifacts/{args.artifact_id}/files/{_quote(args.path)}",
            {"content": content},
        )
    )


def cmd_upload(args):
    """Add or replace one of the binary files a page uses: an image, a font, audio
    or video."""
    if not _is_binary(args.path):
        _die(
            f"{args.path} is not an image, a font, audio or video. `upload` carries "
            "those (" + ", ".join(_BINARY_EXTENSIONS) + "); write a page, a "
            "stylesheet, a script or subtitles with `write`."
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


def cmd_workdir(args):
    """Create the artifact's working folder, named after its title, and print it."""
    path = os.path.join(_workdir_root(), _slug(args.name))
    os.makedirs(path, exist_ok=True)
    print(path)


def cmd_check(args):
    """Check pages before `create` or `write`: what the viewer breaks, and the rules
    SKILL.md asks for. The first page is the entry: it is the one --title applies to.
    Hosts are checked against the public CDNs the viewer allows, and each library URL
    is asked for on its CDN when there is a network to ask over."""
    sources = [f"https://{host}" for host in _CDN_HOSTS]
    report = []
    for index, path in enumerate(args.files):
        if not os.path.isfile(path):
            _die(f"{path} does not exist.")
        if not path.lower().endswith((".html", ".htm")):
            report.append({"file": path, "findings": []})
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            content = handle.read()
        findings = _page_findings(
            content,
            os.path.dirname(path) or ".",
            title=args.title if index == 0 else None,
            sources=sources,
            verify=True,
        )
        report.append({"file": path, "findings": findings})
    _emit(report)


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
    p.add_argument(
        "--favorite", action="store_true", help="Only the user's favorite artifacts"
    )
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", dest="page_size", type=int, default=50)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("recent")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", dest="page_size", type=int, default=20)
    p.set_defaults(func=cmd_recent)

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
    p.add_argument(
        "--conversation",
        help="OpenCode session id of the conversation it came from "
        "(default: CONVERSATION_ID, which the sandbox sets)",
    )
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
    p.add_argument(
        "path", help="Where the file goes in the artifact, e.g. img/logo.png or media/demo.mp4"
    )
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

    p = sub.add_parser("workdir")
    p.add_argument("name", help="The artifact's title; its folder is named after it")
    p.set_defaults(func=cmd_workdir)

    p = sub.add_parser("check")
    p.add_argument("files", nargs="+", help="The entry page first, then any other page")
    p.add_argument("--title", help="The --title it gets: the entry's <title> must match")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("url")
    p.add_argument("artifact_id")
    p.set_defaults(func=cmd_url)
    return parser


def main(argv=None) -> None:
    args = _parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
