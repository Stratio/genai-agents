# Task: upload an agent bundle to Stratio Cowork

Register a packaged agent ZIP (`agents/v1` container) into Stratio Cowork (`genai-api`).

## Endpoint

| | |
|---|---|
| Method | `POST` |
| Path | `/v1/agents/bundle/import` |
| Content type | `multipart/form-data` |
| Multipart field | `bundle_zip` (the container ZIP) |

## Query parameters

| Parameter | Required | Default | Allowed values | Notes |
|---|---|---|---|---|
| `on_conflict` | no | `new_version` | `new_version` \| `overwrite` \| `fail` | Strategy when an agent with the same name already exists. |
| `name` | only for plain ZIPs without manifest | — | string | The bundles produced by `agent-creator/agent-packager` always include `metadata.yaml` with `name`, so this parameter is **not** needed for them. Only used as a fallback for bundles that do not carry a manifest. |
| `description` | no | (taken from `metadata.yaml`) | string | Only for `.md`-only imports. |
| `model_group_name` | no | — | string | Only for `.md`-only imports. |

## Expected ZIP layout (`agents/v1`)

The container ZIP must follow the format documented in the `agent-packager` skill:

```
{name}-stratio-cowork.zip
├── metadata.yaml                         # required, format_version: "agents/v1"
├── {name}-opencode-agent.zip             # required, agent files
└── {name}-shared-skills.zip              # optional, only if shared skills exist
```

`metadata.yaml` declares `format_version: "agents/v1"`, `name`, `agent_zip`, optional `skills_zip`, and `description`. The server reads `name` from there.

## Procedure

1. **Pre-check** — follow `skills-guides/external-api-calls.md` §2 (`preflight_external_api`). The pre-check is an environment health check (env vars, certificate paths). If it fails, stop and report to the user which prerequisites are missing — do not silence the failure and do not refuse with a generic "I can't". The bundle is already packaged correctly; only the deployment step did not complete, and the user can decide how to proceed.

2. **Ask the user** which conflict strategy to apply (use the question convention provided by the environment; otherwise present numbered options):

   > 1. `new_version` — if the agent already exists, create a new version **(recommended)**
   > 2. `overwrite` — replace the existing draft version
   > 3. `fail` — stop if the agent already exists
   > 4. cancel

3. **Run the call**:

   ```bash
   USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
   USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
   CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
   GENAI_API_URL="${GENAI_API_URL%/}"

   ZIP_PATH="<path to the agent container ZIP>"
   ON_CONFLICT="<chosen strategy>"

   curl -sS --connect-timeout 10 --max-time 180 \
     --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
     -X POST \
     -H "Accept: application/json" \
     -F "bundle_zip=@${ZIP_PATH}" \
     -w "\nHTTP %{http_code}\n" \
     "${GENAI_API_URL}/v1/agents/bundle/import?on_conflict=${ON_CONFLICT}"
   ```

## Expected response

`HTTP 200` with a JSON body of the shape:

```json
{
  "agent": {
    "imported": ["my-agent"],
    "conflicts": [],
    "errors": []
  },
  "skills": {
    "imported": ["skill-1", "skill-2"],
    "conflicts": [],
    "errors": []
  }
}
```

- `agent.imported` — name of the registered agent (typically one).
- `skills.imported` — names of any shared skills that travelled inside the bundle and were registered alongside.
- `*.conflicts` — names already present, skipped because `on_conflict=fail` was used.
- `*.errors` — `{"name": "...", "error": "..."}` for entries the server rejected.
- The response may also include `unresolved_mcps` when MCP servers referenced in `metadata.yaml` are not registered on the platform; this is a warning, not a fatal error.

## Reporting back to the user

- On 2xx: summarize `agent.imported`, any `skills.imported`, and `conflicts`/`errors` if non-empty. If the response contains `unresolved_mcps`, mention them so the user can configure those MCPs from the web interface.
- On non-2xx: surface HTTP code and body verbatim. See `skills-guides/external-api-calls.md` §5 for how to interpret common codes (`401/403` = mTLS or RBAC; `400/422` = validation; `400` with metadata details = malformed `metadata.yaml`).

## Reusable script

If the caller prefers a one-shot script (e.g. to leave on disk for the user to re-run), materialize it from this template:

```bash
#!/bin/bash
# Uploads an agents/v1 bundle ZIP to Stratio Cowork (genai-api).
set -euo pipefail

ZIP_PATH="${1:?Usage: $0 <agent-cowork.zip> [on_conflict] [name]}"
ON_CONFLICT="${2:-new_version}"
NAME_OVERRIDE="${3:-}"

: "${GENAI_API_URL:?GENAI_API_URL not set}"
USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"

GENAI_API_URL="${GENAI_API_URL%/}"
QUERY="on_conflict=${ON_CONFLICT}"
[ -n "$NAME_OVERRIDE" ] && QUERY="${QUERY}&name=${NAME_OVERRIDE}"

curl -sS --connect-timeout 10 --max-time 180 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -X POST \
  -H "Accept: application/json" \
  -F "bundle_zip=@${ZIP_PATH}" \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/agents/bundle/import?${QUERY}"
```
