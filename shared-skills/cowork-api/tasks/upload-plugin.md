# Task: upload a plugin bundle to Stratio Cowork

Register a packaged functional plugin ZIP into Stratio Cowork (`genai-api`).

A plugin bundle is a wrapper ZIP that contains one or more sub-ZIPs (agents and/or skills). This task opens the wrapper, reads the aggregated `plugin.yaml`, and dispatches each sub-ZIP to the matching `genai-api` endpoint reusing the logic of `tasks/upload-agent.md` and `tasks/upload-skill.md`.

## Endpoints used

This task does not call a single plugin endpoint — it dispatches the sub-bundles:

| Sub-bundle type | Endpoint | Multipart field | Sub-task to follow |
|---|---|---|---|
| `agent` | `POST /v1/agents/bundle/import` | `bundle_zip` | `tasks/upload-agent.md` |
| `skills` | `POST /v1/agents/skills/bundle/import` | `file` | `tasks/upload-skill.md` |

## Expected wrapper layout

```
{plugin}-stratio-cowork-{version}.zip
├── plugin.yaml                      # required, contains bundles[] catalogue
├── README.md                        # user-facing documentation
├── agents/                          # optional; one sub-zip per agent (agents/v1)
│   └── {agent}-stratio-cowork.zip
└── shared-skills/                   # optional; one sub-zip with skills bundle
    └── {plugin}-skills.zip
```

`plugin.yaml` declares `bundles[]` — each entry has `path`, `type` (`agent` or `skills`), `endpoint` and `sha256`. The task reads this catalogue to know what to upload and where.

## Procedure

1. **Pre-check** — follow `skills-guides/external-api-calls.md` §2 (`preflight_external_api`). If it fails, stop and surface the missing prerequisites verbatim — do not refuse with a generic "I can't".

2. **Open the wrapper** in a temporary directory. Read `plugin.yaml` and validate that `bundles[]` is present and non-empty.

3. **Ask the user** which conflict strategy to apply globally (use the question convention provided by the environment; otherwise present numbered options):

   > 1. `new_version` — if any agent/skill already exists, create a new version **(recommended)**
   > 2. `overwrite` — replace the existing draft version
   > 3. `fail` — stop on first conflict
   > 4. cancel

   The strategy applies to every sub-ZIP. The `version` query for skills is intentionally not asked.

4. **Dispatch each sub-bundle** in the order they appear in `bundles[]`. Verify the file's SHA-256 matches the manifest entry before uploading; if it doesn't, abort and report a corrupted bundle.

   For each entry:

   ```bash
   USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
   USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
   CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
   GENAI_API_URL="${GENAI_API_URL%/}"

   ON_CONFLICT="<chosen strategy>"
   SUB_PATH="<bundle.path>"      # e.g. agents/governance-officer-stratio-cowork.zip
   SUB_TYPE="<bundle.type>"      # "agent" or "skills"
   SUB_ENDPOINT="<bundle.endpoint>"

   case "$SUB_TYPE" in
     agent)
       FIELD="bundle_zip"
       QUERY="on_conflict=${ON_CONFLICT}"
       ;;
     skills)
       FIELD="file"
       QUERY="on_conflict=${ON_CONFLICT}"
       ;;
   esac

   curl -sS --connect-timeout 10 --max-time 180 \
     --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
     -X POST \
     -H "Accept: application/json" \
     -F "${FIELD}=@${SUB_PATH}" \
     -w "\nHTTP %{http_code}\n" \
     "${GENAI_API_URL}${SUB_ENDPOINT}?${QUERY}"
   ```

5. **Aggregate the results**. Collect `imported`, `conflicts`, `errors` and (for agent uploads) `unresolved_mcps` from every response. If `on_conflict=fail` was chosen and any sub-bundle returned a conflict, stop dispatching the remaining ones and report.

## Atomicity warning

This task delegates to N independent endpoint calls. If a sub-bundle fails midway, the previously-uploaded ones are already registered — there is **no server-side rollback**. The aggregated report makes the partial state explicit so the user can decide whether to retry, revert manually or accept the partial install.

The future `plugins/v1` API (phase 2) will provide atomic plugin-level installation; this task will be updated to prefer it once available.

## Aggregated reporting

Surface to the user a single summary covering all sub-bundles, in this shape:

```
Plugin: <plugin-name>
  Agents:
    imported: ["governance-officer", "data-quality"]
    conflicts: []
    errors: []
  Skills:
    imported: ["pdf-writer", "docx-writer"]
    conflicts: ["web-craft"]
    errors: []
  Unresolved MCPs (warnings): ["Stratio_Data"]
```

If any sub-bundle returned a non-2xx HTTP code, surface the code and the body verbatim alongside the aggregated summary. See `skills-guides/external-api-calls.md` §5 for how to interpret common codes (`401/403` = mTLS or RBAC; `400/422` = validation).

## Reusable script

If the caller prefers a one-shot script, materialize this template (delegates per-bundle):

```bash
#!/bin/bash
# Uploads a Stratio Cowork plugin bundle to genai-api.
set -euo pipefail

ZIP_PATH="${1:?Usage: $0 <plugin-stratio-cowork.zip> [on_conflict]}"
ON_CONFLICT="${2:-new_version}"

: "${GENAI_API_URL:?GENAI_API_URL not set}"
USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
GENAI_API_URL="${GENAI_API_URL%/}"

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
unzip -q "$ZIP_PATH" -d "$WORK"

[ -f "$WORK/plugin.yaml" ] || { echo "ERROR: plugin.yaml missing in bundle" >&2; exit 1; }

# Use python to iterate bundles[]
python3 - "$WORK" "$ON_CONFLICT" "$GENAI_API_URL" "$USER_CERT_PATH" "$USER_KEY_PATH" "$CA_CERT_PATH" <<'PY'
import sys, subprocess, hashlib, yaml
from pathlib import Path

work, on_conflict, base_url, cert, key, cacert = sys.argv[1:7]
manifest = yaml.safe_load((Path(work)/"plugin.yaml").read_text()) or {}
for entry in manifest.get("bundles") or []:
    p = Path(work) / entry["path"]
    if entry.get("sha256"):
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            sys.exit(f"ERROR: SHA-256 mismatch for {entry['path']}")
    field = "bundle_zip" if entry["type"] == "agent" else "file"
    url = f"{base_url}{entry['endpoint']}?on_conflict={on_conflict}"
    print(f"--- Uploading {entry['type']}: {entry['path']}")
    subprocess.run([
        "curl", "-sS", "--connect-timeout", "10", "--max-time", "180",
        "--cert", cert, "--key", key, "--cacert", cacert,
        "-X", "POST", "-H", "Accept: application/json",
        "-F", f"{field}=@{p}",
        "-w", "\nHTTP %{http_code}\n",
        url,
    ], check=True)
PY
```
