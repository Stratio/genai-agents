---
name: rocket-file-browser
description: "Upload and download files between the Stratio sandbox and Rocket's HDFS File Browser. Use when the user wants to move a file to or from Rocket's HDFS — phrases like 'baja este fichero de Rocket', 'sube este archivo al HDFS', 'download from the file browser', 'upload to Rocket', 'get/put a file in HDFS'. Talks to Rocket's mutual-TLS API (/rocket/fileBrowser/*) with the sandbox client certificate, so it runs with the operating user's own Rocket permissions."
argument-hint: "[download|upload] [paths...]"
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

- The base URL is **`ROCKET_API_URL`** (not `GENAI_API_URL`). It must include the
  `/rocket` prefix and point at Rocket's **mutual-TLS** listener (port 7777), e.g.
  `https://rocket.<tenant>-rocket.svc.<cluster-domain>:7777/rocket`. The public
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

Helper (no sub-file needed): list filesystems with
`python3 scripts/rocket_file_browser.py filesystems` to discover the `id`/`type`
to pass as `--fs`. The script auto-resolves the filesystem when exactly one exists.

## Routing rules

1. Identify the capability from the user's intent. If it is not download or upload,
   this MVP cannot help — say so (full File Browser coverage is a planned extension).
2. Run the pre-check above. If it fails, stop and report.
3. Load the matching sub-file and follow it end-to-end.
4. After the call, surface the result (or the HTTP code + body verbatim on failure)
   to the user, per `guides/external-api-calls.md` §5.

## Adding a new capability

Drop a `tasks/<capability>.md` (when to use, the exact `rocket_file_browser.py`
invocation, expected output, error cases), add a row to the index above, and mirror
both files under `es/skills/rocket-file-browser/`. The planned full scope adds
`ls`, `cp`, `mv`, `rm`, `mkdir`, `compress`, `extract`.
