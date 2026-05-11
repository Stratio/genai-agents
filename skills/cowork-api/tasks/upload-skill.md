# Task: upload a skill bundle to Stratio Cowork

Register a packaged skill ZIP into Stratio Cowork (`genai-api`).

## Endpoint

| | |
|---|---|
| Method | `POST` |
| Path | `/v1/agents/skills/bundle/import` |
| Content type | `multipart/form-data` |
| Multipart field | `file` (the skill ZIP) |

## Query parameters

| Parameter | Required | Default | Allowed values | Notes |
|---|---|---|---|---|
| `on_conflict` | no | `new_version` | `new_version` \| `overwrite` \| `fail` | Strategy when a skill with the same name already exists. |
| `version` | no | (server decides) | semantic version (e.g. `1.2.3`, `1.2.3-SNAPSHOT`) | Advanced: SNAPSHOT overwrites the draft in place; fixed versions auto-publish on checksum change. |

## Expected ZIP layout

The ZIP is a self-contained skill folder; the API accepts both layouts:

```
my-skill.zip                       my-skill.zip
└── SKILL.md                       └── my-skill/
    other files...                     ├── SKILL.md
                                       └── other files...
```

The API extracts the contents, parses any `SKILL.md` it finds (one or more), and registers each as a skill version.

## Procedure

1. **Pre-check** — follow `guides/external-api-calls.md` §2 (`preflight_external_api`). The pre-check is an environment health check (env vars, certificate paths). If it fails, stop and report to the user which prerequisites are missing — do not silence the failure and do not refuse with a generic "I can't". The bundle is already packaged correctly; only the deployment step did not complete, and the user can decide how to proceed.

2. **Ask the user** which conflict strategy to apply (use the question convention provided by the environment; otherwise present numbered options):

   > 1. `new_version` — if the skill already exists, create a new version **(recommended)**
   > 2. `overwrite` — replace the existing draft version
   > 3. `fail` — stop if the skill already exists
   > 4. cancel

   The `version` query is intentionally not asked — it has nuanced semantics (SNAPSHOT vs. fixed) that do not belong in a conversational flow. The script accepts it as a third positional argument for advanced manual use.

3. **Run the call**:

   ```bash
   USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
   USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
   CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
   GENAI_API_URL="${GENAI_API_URL%/}"

   ZIP_PATH="<path to the skill ZIP>"
   ON_CONFLICT="<chosen strategy>"
   VERSION=""   # leave empty unless explicitly requested

   QUERY="on_conflict=${ON_CONFLICT}"
   [ -n "$VERSION" ] && QUERY="${QUERY}&version=${VERSION}"

   curl -sS --connect-timeout 10 --max-time 180 \
     --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
     -X POST \
     -H "Accept: application/json" \
     -F "file=@${ZIP_PATH}" \
     -w "\nHTTP %{http_code}\n" \
     "${GENAI_API_URL}/v1/agents/skills/bundle/import?${QUERY}"
   ```

## Expected response

`HTTP 200` with a JSON body of the shape:

```json
{
  "imported": ["my-skill"],
  "conflicts": [],
  "errors": []
}
```

- `imported` — names of skills successfully registered (one per `SKILL.md` found in the ZIP).
- `conflicts` — names that already existed and were not registered because `on_conflict=fail` was used.
- `errors` — entries with the shape `{"name": "...", "error": "..."}` for skills the server rejected.

## Reporting back to the user

- On 2xx: summarize `imported`, `conflicts`, and `errors`. If `errors` is non-empty, show each verbatim.
- On non-2xx: surface HTTP code and body verbatim. See `guides/external-api-calls.md` §5 for how to interpret common codes (`401/403` = mTLS or RBAC; `400/422` = validation).

## Reusable script

If the caller prefers a one-shot script (e.g. to leave on disk for the user to re-run), materialize it from this template:

```bash
#!/bin/bash
# Uploads a skill ZIP to Stratio Cowork (genai-api).
set -euo pipefail

ZIP_PATH="${1:?Usage: $0 <skill.zip> [on_conflict] [version]}"
ON_CONFLICT="${2:-new_version}"
VERSION="${3:-}"

: "${GENAI_API_URL:?GENAI_API_URL not set}"
USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"

GENAI_API_URL="${GENAI_API_URL%/}"
QUERY="on_conflict=${ON_CONFLICT}"
[ -n "$VERSION" ] && QUERY="${QUERY}&version=${VERSION}"

curl -sS --connect-timeout 10 --max-time 180 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -X POST \
  -H "Accept: application/json" \
  -F "file=@${ZIP_PATH}" \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/agents/skills/bundle/import?${QUERY}"
```
