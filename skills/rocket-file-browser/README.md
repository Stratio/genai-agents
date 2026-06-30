# rocket-file-browser

Shared skill that moves files between the Stratio sandbox and **Rocket's HDFS File
Browser** (`/rocket/fileBrowser/*`), so an agent can pull a dataset/document out of
Rocket into the workspace or push a generated file back into HDFS — without the manual
roundtrip through the Rocket web UI.

Designed as a **router** (like `cowork-api`): a minimal `SKILL.md` indexes the
capabilities and points to one self-contained file under `tasks/` per capability. A
single Python client, `scripts/rocket_file_browser.py`, does the HTTP work.

## What it does

- **download** — `POST /fileBrowser/download`, streaming the raw bytes to a local path.
- **upload** — two phases: `POST /fileBrowser/uploadLocalFile` (multipart) then
  `POST /fileBrowser/putLocalFileToHadoopFs`, with automatic retry on HTTP 420.
- **ls** — `POST /fileBrowser/findByPath` (directory listing / file stat).
- **cp** / **mv** — `PUT /fileBrowser/copy` / `PUT /fileBrowser/update`.
- **rm** — `DELETE /fileBrowser/delete` (one or more paths).
- **mkdir** — `POST /fileBrowser/createDir`.
- **compress** / **extract** — `PUT /fileBrowser/compress` (codecs: ZStandard, Lz4,
  Snappy, Gzip, Bzip2, Zip, TarGz) / `PUT /fileBrowser/extract`.
- **filesystems** helper — `GET /fileBrowser/getFilesystems` to discover `id`/`type`.

## Authentication & identity

mTLS only. Rocket runs in `Oauth2Mutual` and exposes a mutual-TLS listener on port
7777; the sandbox's mounted client certificate (`/vault/secrets/cert.crt`, CN = the
operating user, e.g. `s000001-user`) is the identity Rocket authorizes with via Gosec.
**No token, no impersonation** — the skill runs with the user's own File Browser
permissions, the same ones they see in the Rocket UI.

The public ingress (`:443`) is oauth2/cookie only and ignores the certificate. Point
`ROCKET_API_URL` at the **mutual** listener, reachable in-cluster by service DNS:
`https://rocket.<tenant>-rocket.svc.<cluster-domain>:7777/rocket`.

## Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `ROCKET_API_URL` | yes | — | Base URL incl. `/rocket`, on the 7777 mutual listener |
| `USER_CERT_PATH` | yes | `/vault/secrets/cert.crt` | Client cert (mTLS) |
| `USER_KEY_PATH` | yes | `/vault/secrets/cert.key` | Client key |
| `CA_CERT_PATH` | when verifying | `/stratio/certs/ca.crt` | CA to validate the server cert |
| `ROCKET_TLS_VERIFY` | no | `false` | `true` to verify the server cert; otherwise skipped (the 7777 server cert SAN usually doesn't cover the service name — same reason OpenCode uses `NODE_TLS_REJECT_UNAUTHORIZED=0`) |

## Shared guides

- `external-api-calls.md` — declared in `guides`. Cert paths, the pre-check, the
  curl/Python templates and the error table. This skill reuses all of it; the only
  delta is `ROCKET_API_URL` (vs `GENAI_API_URL`) on the mutual-TLS port.

## Python dependencies

- `requests` — already present in the sandbox `/opt/venv`.

## System dependencies

- None beyond the venv. The script reads the cert paths from the environment and
  negotiates mTLS itself.

## Notes

- Never silently retries except HTTP 420 on the upload commit phase (Rocket signals a
  concurrent upload). Every other failure is surfaced with HTTP code + body verbatim.
- Reserved roots (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
  `/mlProjectExecutionsArtifacts`) are refused client-side before any call.
- `download` uses the POST variant (supports named datastores); the `GET ...?pathHdfs=`
  form forces the internal filesystem and is not used.
