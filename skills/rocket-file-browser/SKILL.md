---
name: rocket-file-browser
description: "Manage files in Rocket's HDFS File Browser from the Stratio sandbox: download, upload, list, copy, move/rename, delete, mkdir, compress and extract. Use when the user wants to operate on Rocket's HDFS — phrases like 'baja este fichero de Rocket', 'sube este archivo al HDFS', 'lista la carpeta', 'borra/copia/mueve en HDFS', 'comprime estos ficheros', 'download from the file browser', 'upload to Rocket'. Talks to Rocket's mutual-TLS API (/rocket/fileBrowser/*) with the sandbox client certificate, so it runs with the operating user's own Rocket permissions."
argument-hint: "[download|upload|ls|cp|mv|rm|mkdir|compress|extract] [paths...]"
---

# Skill: Rocket File Browser (HDFS upload/download)

Router skill. Each capability lives in its own file under `tasks/`. **This file is
intentionally minimal** — when the agent performs a task, load and follow the
matching sub-file in full. Do not improvise the request from this index.

All operations are served by a single Python client, `scripts/rocket_file_browser.py`,
which handles mTLS, the two-phase upload, and the HTTP 420 retry.

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
| Download a file | Bring a file from Rocket's HDFS into the sandbox workspace. | `tasks/download.md` |
| Upload a file | Push a local sandbox file into a Rocket HDFS directory. | `tasks/upload.md` |
| List a path | Show the contents of an HDFS directory. | `tasks/ls.md` |
| Copy | Copy an HDFS file/directory to a new path. | `tasks/cp.md` |
| Move / rename | Move or rename an HDFS file/directory. | `tasks/mv.md` |
| Delete | Remove HDFS files/directories (destructive — confirm first). | `tasks/rm.md` |
| Create directory | Make a new HDFS directory. | `tasks/mkdir.md` |
| Compress | Compress HDFS files into an archive. | `tasks/compress.md` |
| Extract | Extract an HDFS archive. | `tasks/extract.md` |

Helper (no sub-file needed): list filesystems with
`python3 scripts/rocket_file_browser.py filesystems` to discover the `id`/`type`
to pass as `--fs`. The script auto-resolves the filesystem when exactly one exists.

## Routing rules

1. Identify the capability from the user's intent. If none of the index entries matches
   (e.g. publishing views, querying data), this skill cannot help — say so.
2. Run the pre-check above. If it fails, stop and report.
3. Load the matching sub-file and follow it end-to-end.
4. After the call, surface the result (or the HTTP code + body verbatim on failure)
   to the user, per `guides/external-api-calls.md` §5.

## Adding a new capability

Drop a `tasks/<capability>.md` (when to use, the exact `rocket_file_browser.py`
invocation, expected output, error cases), add a subcommand to the script, add a row to
the index above, and mirror both files under `es/skills/rocket-file-browser/`.
