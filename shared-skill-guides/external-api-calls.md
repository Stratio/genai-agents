# External API calls from the Stratio sandbox

Reference for skills and agents that need to call HTTPS services (REST APIs) from inside the Stratio sandbox. Covers the environment provided by the sandbox image and ready-to-copy templates for `curl` and Python.

## 1. What the sandbox provides

The Stratio sandbox image (`genai-agents-sandbox`) mounts a client X.509 certificate, its private key, and a CA certificate inside the container. mTLS is the **only** authentication required to call internal Stratio REST APIs — no Bearer tokens, no API keys.

### Environment variables

| Variable | Required | Default in sandbox | Purpose |
|---|---|---|---|
| `GENAI_API_URL` | depends on caller | `https://<host>` (no trailing slash convention; normalize with `${VAR%/}`) | Base URL of `genai-api` (Stratio Cowork management REST API). |
| `USER_CERT_PATH` | yes (for mTLS) | `/vault/secrets/cert.crt` | Client certificate (mTLS). |
| `USER_KEY_PATH` | yes (for mTLS) | `/vault/secrets/cert.key` | Client private key. |
| `CA_CERT_PATH` | yes | `/stratio/certs/ca.crt` | CA used to validate the server certificate. |

If a variable is missing, the sandbox still starts — your script must pre-check and degrade gracefully (e.g. skip the API call and inform the user).

### Files already in place

- `~/.curlrc` is generated at container start with `cert = "/vault/secrets/cert.crt"` and `key = "/vault/secrets/cert.key"`. Any `curl` invocation inside the sandbox already uses mTLS by default — you only need to add `--cacert "$CA_CERT_PATH"`.
- The CA certificate is also installed system-wide at `/usr/local/share/ca-certificates/stratio-ca.crt` and `update-ca-certificates` has been run, so HTTP libraries that read the system trust store (Python `requests` with default `verify=True`) trust internal Stratio hosts out of the box.

## 2. Pre-check before any external call

Always verify the sandbox provides what you need before issuing a request. If the pre-check fails, do not call the API — inform the user that the operation requires the Stratio sandbox.

```bash
preflight_external_api() {
  local url="${1:-${GENAI_API_URL:-}}"

  if [ -z "$url" ]; then
    echo "ERROR: target API URL not set (e.g. GENAI_API_URL)." >&2
    return 1
  fi
  for var in USER_CERT_PATH USER_KEY_PATH CA_CERT_PATH; do
    local path
    path="${!var:-}"
    case "$var" in
      USER_CERT_PATH) path="${path:-/vault/secrets/cert.crt}" ;;
      USER_KEY_PATH)  path="${path:-/vault/secrets/cert.key}" ;;
      CA_CERT_PATH)   path="${path:-/stratio/certs/ca.crt}" ;;
    esac
    if [ ! -f "$path" ]; then
      echo "ERROR: ${var} not found at ${path}" >&2
      return 1
    fi
  done
  return 0
}
```

## 3. curl templates

Resolve certificates with explicit defaults so the script works whether or not the env vars are exported:

```bash
USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
GENAI_API_URL="${GENAI_API_URL%/}"   # strip trailing slash if present
```

### GET (JSON)

```bash
curl -sS --connect-timeout 10 --max-time 30 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -H "Accept: application/json" \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/some/path"
```

### POST (JSON body)

```bash
curl -sS --connect-timeout 10 --max-time 60 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "$JSON_BODY" \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/some/path"
```

### POST (multipart, file upload)

```bash
curl -sS --connect-timeout 10 --max-time 180 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -X POST \
  -H "Accept: application/json" \
  -F "file=@${ZIP_PATH}" \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/upload/path?on_conflict=new_version"
```

### PATCH

```bash
curl -sS --connect-timeout 10 --max-time 30 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -X PATCH \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/some/resource/${ID}"
```

`-w "\nHTTP %{http_code}\n"` is recommended on every call so the caller can split body and status code in the output. Use `--max-time` proportional to the operation: 30s for metadata reads, 60s for JSON writes, 120-180s for ZIP uploads.

## 4. Python templates

The sandbox virtual environment (`/opt/venv`) ships `requests` and `httpx`. Pick whichever fits — `requests` is simpler, `httpx` adds async if you ever need it.

### `requests`

```python
import os
import requests

GENAI_API_URL = os.environ["GENAI_API_URL"].rstrip("/")
USER_CERT_PATH = os.environ.get("USER_CERT_PATH", "/vault/secrets/cert.crt")
USER_KEY_PATH = os.environ.get("USER_KEY_PATH", "/vault/secrets/cert.key")
CA_CERT_PATH = os.environ.get("CA_CERT_PATH", "/stratio/certs/ca.crt")

def call(method: str, path: str, **kwargs) -> requests.Response:
    return requests.request(
        method,
        f"{GENAI_API_URL}{path}",
        cert=(USER_CERT_PATH, USER_KEY_PATH),
        verify=CA_CERT_PATH,
        timeout=kwargs.pop("timeout", 30),
        **kwargs,
    )

# GET JSON
resp = call("GET", "/v1/some/path", headers={"Accept": "application/json"})
resp.raise_for_status()
data = resp.json()

# Multipart upload
with open(zip_path, "rb") as f:
    resp = call(
        "POST",
        "/v1/upload/path",
        params={"on_conflict": "new_version"},
        files={"file": (os.path.basename(zip_path), f, "application/zip")},
        timeout=180,
    )
resp.raise_for_status()
print(resp.json())
```

### `httpx`

```python
import os
import httpx

client = httpx.Client(
    base_url=os.environ["GENAI_API_URL"].rstrip("/"),
    cert=(
        os.environ.get("USER_CERT_PATH", "/vault/secrets/cert.crt"),
        os.environ.get("USER_KEY_PATH", "/vault/secrets/cert.key"),
    ),
    verify=os.environ.get("CA_CERT_PATH", "/stratio/certs/ca.crt"),
    timeout=30.0,
)

resp = client.get("/v1/some/path", headers={"Accept": "application/json"})
resp.raise_for_status()
data = resp.json()
```

## 5. Common errors and how to read them

| Symptom | Likely cause | Action |
|---|---|---|
| curl exit 6 | DNS resolution failed | Check `GENAI_API_URL` host; the sandbox may have lost network. |
| curl exit 7 | Connection refused / unreachable | Service down or wrong port. |
| curl exit 28 | Timeout | Bump `--max-time`; check if the operation is slow by design (e.g. large ZIP upload). |
| curl exit 35 | TLS handshake failed | Certificate path wrong, expired, or CA mismatch. Re-run the pre-check. |
| HTTP 401 / 403 | mTLS rejected, or RBAC/whitelist denied | The user's certificate identity does not have the required role. Surface the response body — it usually names the missing role. |
| HTTP 400 | Validation error | Check payload shape; surface the JSON body to the user. |
| HTTP 422 | Schema/format error | Same as 400, often used by FastAPI for type/field violations. |
| HTTP 5xx | Server-side issue | Not actionable from the client — surface the response and suggest retrying later. |

When something fails, **always show the user the HTTP status and the response body verbatim**. Do not silently swallow errors — the body usually contains the actionable information.

## 6. What this guide intentionally does NOT cover

- Catalog of specific endpoints — those live in each consumer skill (e.g. `cowork-api/tasks/`).
- LiteLLM proxy at `127.0.0.1:3002` — that is for model calls, not for REST APIs.
- Token-based authentication flows — internal Stratio APIs use mTLS only.
- Retry/backoff strategies — leave that to the caller, since the right policy depends on the operation.
