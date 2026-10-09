---
name: rocket-file-browser
description: "Manage files in Rocket's File Browser from the Stratio sandbox, on any filesystem Rocket exposes — its HDFS and the S3 buckets configured in it: download, upload, list, copy, move/rename, delete, mkdir, compress, extract, and choose or switch the filesystem. Use when the user wants to operate on Rocket's HDFS or S3 — phrases like 'baja este fichero de Rocket', 'sube este archivo al HDFS', 'súbelo al bucket', 'lista la carpeta de S3', 'borra/copia/mueve en HDFS', 'comprime estos ficheros', 'cambia al otro filesystem', 'download from the file browser', 'upload to Rocket'. Talks to Rocket's mutual-TLS API (/fileBrowser/*) with the sandbox client certificate, so it runs with the operating user's own Rocket permissions."
argument-hint: "[download|upload|ls|cp|mv|rm|mkdir|compress|extract] [paths...]"
---

# Skill: Rocket File Browser (HDFS and S3)

Router skill. Each capability lives in its own file under `tasks/`. **This file is
intentionally minimal** — when the agent performs a task, load and follow the
matching sub-file in full. Do not improvise the request from this index.

All operations are served by a single Python client, `scripts/rocket_file_browser.py`,
which handles mTLS, the target filesystem, the one-request upload
(`POST /fileBrowser/upload`) and its fallback to the legacy two-request flow with the
HTTP 420 retry on older Rocket versions.

## Several filesystems — read before any operation

One Rocket can browse **several filesystems**: its internal one (HDFS, or S3 when Rocket
runs on S3) plus every **S3 bucket** an admin configured. Rocket keeps no current
filesystem — each call names its own — and a path means a different file on each
filesystem. So:

- Settle the filesystem **before the first operation** with `tasks/filesystems.md`:
  list them, use the only one, or **ask the user** when there are several and the
  request does not name one. Never guess.
- Pass the chosen one as `--fs <id>:<type>` on **every** call of the conversation, and
  switch only when the user asks (say so in one line).
- Name the filesystem whenever you report a path or ask for a confirmation
  ("`/landing/a.csv` in bucket `sales-landing`"), not just the path.
- Operations never cross filesystems: copy/move between them = download + upload
  (`tasks/filesystems.md` §Moving data between filesystems).

## Prerequisites — read first

Authentication is **mTLS only**, the same model as `guides/external-api-calls.md`
(§1 environment, §3/§4 templates, §5 error table). The differences from that guide:

- The base URL is **`ROCKET_API_URL`** (not `GENAI_API_URL`). It is the **host:port**
  of Rocket's **mutual-TLS** listener (port 7777) with **no path** — the skill calls
  `/fileBrowser/...` directly. Use the in-cluster short service name (resolved via the
  pod search domain), e.g. `https://<rocket-instance>.<rocket-namespace>:7777`
  (e.g. `https://rocket.s000001-rocket:7777`). The public
  ingress (443) is oauth2/cookie only and will **not** accept the certificate.
- The client cert (`/vault/secrets/cert.crt`, CN = the operating user) is the
  identity Rocket authorizes with. No token, no impersonation — calls run with the
  user's own File Browser permissions.

**Pre-check before any call:**

1. `ROCKET_API_URL` is set (otherwise the script stops cleanly and says so).
2. `USER_CERT_PATH` / `USER_KEY_PATH` exist (defaults `/vault/secrets/cert.{crt,key}`).

If a prerequisite is missing, stop and tell the user exactly which one — do not refuse
with a generic message.

## Capability index

| Capability | When to use | Sub-file to load |
|---|---|---|
| Choose / switch filesystem | First operation of the conversation, several filesystems, the user names a bucket or "the other filesystem", or data must go from one filesystem to another. | `tasks/filesystems.md` |
| Download a file | Bring a file from Rocket (HDFS or S3) into the sandbox workspace. | `tasks/download.md` |
| Upload a file | Push a local sandbox file into a Rocket directory (HDFS or S3). | `tasks/upload.md` |
| List a path | Show the contents of a directory. | `tasks/ls.md` |
| Copy | Copy a file/directory to a new path in the same filesystem. | `tasks/cp.md` |
| Move / rename | Move or rename a file/directory in the same filesystem (confirm first). | `tasks/mv.md` |
| Delete | Remove files/directories (destructive — confirm first). | `tasks/rm.md` |
| Create directory | Make a new directory. | `tasks/mkdir.md` |
| Compress | Compress files into an archive. | `tasks/compress.md` |
| Extract | Extract an archive. | `tasks/extract.md` |

## Routing rules

1. Identify the capability from the user's intent. If none of the index entries matches
   (e.g. publishing views, querying data), this skill cannot help — say so.
2. Run the pre-check above. If it fails, stop and report.
3. If the filesystem for this conversation is not settled yet, follow
   `tasks/filesystems.md` first.
4. Load the matching sub-file and follow it end-to-end.
5. After the call, surface the result (or the HTTP code + body verbatim on failure)
   to the user, per `guides/external-api-calls.md` §5.

## Using this skill inside an agent workflow

- **Downloads land in the current task's working folder.** When the agent keeps a
  per-task folder (an analysis or report folder), download into it — not into the
  workspace root — so the file sits next to the work that uses it.
- **Never publish on your own initiative.** Upload, copy or move into Rocket only when
  the user asks for it. Producing a deliverable locally does not imply uploading it.
- **Confirm the destination before an upload.** State the filesystem, the directory and
  the final file name; the upload is refused if that name already exists, so check with `ls` and
  ask the user how to proceed (rename, or delete the old one with `rm`) instead of
  deleting on your own.
- **Destructive operations always need explicit confirmation** — `rm` and `mv` (a move
  or rename breaks every path that pointed at the original), listing the exact paths
  and the filesystem they live in.

## Adding a new capability

Drop a `tasks/<capability>.md` (when to use, the exact `rocket_file_browser.py`
invocation, expected output, error cases), add a subcommand to the script, add a row to
the index above, and mirror both files under `es/skills/rocket-file-browser/`.
