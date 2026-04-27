# Llamadas a APIs externas desde el sandbox de Stratio

Referencia para skills y agentes que necesiten llamar a servicios HTTPS (APIs REST) desde dentro del sandbox de Stratio. Cubre el entorno que provee la imagen del sandbox y plantillas listas para copiar de `curl` y Python.

## 1. Qué provee el sandbox

La imagen del sandbox de Stratio (`genai-agents-sandbox`) monta dentro del contenedor un certificado X.509 de cliente, su clave privada y un certificado de CA. mTLS es la **única** autenticación necesaria para llamar a APIs REST internas de Stratio — sin tokens Bearer, sin API keys.

### Variables de entorno

| Variable | Requerida | Valor por defecto en el sandbox | Propósito |
|---|---|---|---|
| `GENAI_API_URL` | depende del caller | `https://<host>` (sin barra final por convención; normalizar con `${VAR%/}`) | URL base de `genai-api` (REST API de gestión de Stratio Cowork). |
| `USER_CERT_PATH` | sí (para mTLS) | `/vault/secrets/cert.crt` | Certificado de cliente (mTLS). |
| `USER_KEY_PATH` | sí (para mTLS) | `/vault/secrets/cert.key` | Clave privada del cliente. |
| `CA_CERT_PATH` | sí | `/stratio/certs/ca.crt` | CA usada para validar el certificado del servidor. |

Si falta alguna variable el sandbox arranca igualmente — tu script debe hacer pre-check y degradar con elegancia (p. ej. omitir la llamada e informar al usuario).

### Ficheros ya en su sitio

- `~/.curlrc` se genera al arrancar el contenedor con `cert = "/vault/secrets/cert.crt"` y `key = "/vault/secrets/cert.key"`. Cualquier invocación de `curl` dentro del sandbox ya usa mTLS por defecto — solo hace falta añadir `--cacert "$CA_CERT_PATH"`.
- El certificado de CA también está instalado a nivel de sistema en `/usr/local/share/ca-certificates/stratio-ca.crt` y se ha ejecutado `update-ca-certificates`, así que las librerías HTTP que leen el trust store del sistema (Python `requests` con `verify=True`) confían en hosts internos de Stratio sin configuración adicional.

## 2. Pre-check antes de cualquier llamada externa

Verifica siempre que el sandbox provee lo que necesitas antes de emitir una petición. Si el pre-check falla, no llames a la API — informa al usuario de que la operación requiere el sandbox de Stratio.

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

## 3. Plantillas de curl

Resuelve los certificados con valores por defecto explícitos para que el script funcione con o sin las env vars exportadas:

```bash
USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
GENAI_API_URL="${GENAI_API_URL%/}"   # quita barra final si la hay
```

### GET (JSON)

```bash
curl -sS --connect-timeout 10 --max-time 30 \
  --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
  -H "Accept: application/json" \
  -w "\nHTTP %{http_code}\n" \
  "${GENAI_API_URL}/v1/some/path"
```

### POST (cuerpo JSON)

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

### POST (multipart, subida de fichero)

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

Se recomienda añadir `-w "\nHTTP %{http_code}\n"` en cada llamada para que el caller pueda separar el cuerpo del código de estado en la salida. Usar `--max-time` proporcional a la operación: 30s para lecturas de metadatos, 60s para escrituras JSON, 120-180s para subidas de ZIP.

## 4. Plantillas en Python

El virtual environment del sandbox (`/opt/venv`) trae `requests` y `httpx`. Elige el que encaje — `requests` es más simple, `httpx` añade async por si se necesita.

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

# Subida multipart
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

## 5. Errores comunes y cómo leerlos

| Síntoma | Causa probable | Acción |
|---|---|---|
| curl exit 6 | Resolución DNS fallida | Comprobar el host de `GENAI_API_URL`; el sandbox puede haber perdido red. |
| curl exit 7 | Connection refused / inalcanzable | Servicio caído o puerto incorrecto. |
| curl exit 28 | Timeout | Subir `--max-time`; comprobar si la operación es lenta por diseño (p. ej. subida de un ZIP grande). |
| curl exit 35 | TLS handshake fallido | Ruta de certificado incorrecta, expirado o CA no coincide. Re-ejecutar el pre-check. |
| HTTP 401 / 403 | mTLS rechazado, o RBAC/whitelist denegó | La identidad del certificado del usuario no tiene el rol requerido. Mostrar el cuerpo de la respuesta — suele indicar el rol que falta. |
| HTTP 400 | Error de validación | Comprobar la forma del payload; mostrar el JSON al usuario. |
| HTTP 422 | Error de esquema/formato | Igual que 400, lo usa FastAPI para violaciones de tipo/campo. |
| HTTP 5xx | Problema del servidor | No es accionable desde el cliente — mostrar la respuesta y sugerir reintentar más tarde. |

Cuando algo falla, **muestra siempre al usuario el código HTTP y el cuerpo de la respuesta tal cual**. No tragues errores en silencio — el cuerpo suele contener la información accionable.

## 6. Lo que esta guía deliberadamente NO cubre

- Catálogo de endpoints concretos — viven en cada skill consumidora (p. ej. `cowork-api/tasks/`).
- Proxy de LiteLLM en `127.0.0.1:3002` — eso es para llamadas a modelos, no para APIs REST.
- Flujos de autenticación basados en token — las APIs internas de Stratio usan solo mTLS.
- Estrategias de retry/backoff — se deja al caller, ya que la política correcta depende de la operación.
