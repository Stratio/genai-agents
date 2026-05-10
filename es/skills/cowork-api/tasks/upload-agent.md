# Tarea: subir un bundle de agente a Stratio Cowork

Registrar un ZIP de agente empaquetado (contenedor `agents/v1`) en Stratio Cowork (`genai-api`).

## Endpoint

| | |
|---|---|
| Método | `POST` |
| Path | `/v1/agents/bundle/import` |
| Content type | `multipart/form-data` |
| Campo multipart | `bundle_zip` (el ZIP contenedor) |

## Parámetros de query

| Parámetro | Requerido | Por defecto | Valores permitidos | Notas |
|---|---|---|---|---|
| `on_conflict` | no | `new_version` | `new_version` \| `overwrite` \| `fail` | Estrategia cuando ya existe un agente con el mismo nombre. |
| `name` | solo para ZIPs "plain" sin manifiesto | — | string | Los bundles que produce `agent-creator/agent-packager` siempre incluyen `metadata.yaml` con `name`, así que este parámetro **no** es necesario para ellos. Solo se usa como fallback para bundles sin manifiesto. |
| `description` | no | (se toma del `metadata.yaml`) | string | Solo para imports `.md`. |
| `model_group_name` | no | — | string | Solo para imports `.md`. |

## Estructura esperada del ZIP (`agents/v1`)

El ZIP contenedor debe seguir el formato documentado en la skill `agent-packager`:

```
{name}-stratio-cowork.zip
├── metadata.yaml                         # requerido, format_version: "agents/v1"
├── {name}-opencode-agent.zip             # requerido, ficheros del agente
└── {name}-skills.zip              # opcional, solo si hay shared skills
```

`metadata.yaml` declara `format_version: "agents/v1"`, `name`, `agent_zip`, `skills_zip` opcional y `description`. El servidor lee `name` de ahí.

## Procedimiento

1. **Pre-check** — sigue `skills-guides/external-api-calls.md` §2 (`preflight_external_api`). El pre-check es un health check del entorno (variables de entorno, rutas de certificados). Si falla, detente y reporta al usuario qué prerequisites faltan — no silencies el fallo y no rechaces con un genérico "no puedo". El bundle ya está empaquetado correctamente; solo el paso de despliegue no se completó, y el usuario puede decidir cómo proceder.

2. **Pregunta al usuario** qué estrategia de conflicto aplicar (usa la convención de preguntas que provea el entorno; en su defecto, presenta opciones numeradas):

   > 1. `new_version` — si el agente ya existe, crea una nueva versión **(recomendado)**
   > 2. `overwrite` — sobrescribe la versión draft existente
   > 3. `fail` — detente si el agente ya existe
   > 4. cancelar

3. **Ejecuta la llamada**:

   ```bash
   USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
   USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
   CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
   GENAI_API_URL="${GENAI_API_URL%/}"

   ZIP_PATH="<ruta al ZIP contenedor del agente>"
   ON_CONFLICT="<estrategia elegida>"

   curl -sS --connect-timeout 10 --max-time 180 \
     --cert "$USER_CERT_PATH" --key "$USER_KEY_PATH" --cacert "$CA_CERT_PATH" \
     -X POST \
     -H "Accept: application/json" \
     -F "bundle_zip=@${ZIP_PATH}" \
     -w "\nHTTP %{http_code}\n" \
     "${GENAI_API_URL}/v1/agents/bundle/import?on_conflict=${ON_CONFLICT}"
   ```

## Respuesta esperada

`HTTP 200` con un cuerpo JSON con esta forma:

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

- `agent.imported` — nombre del agente registrado (típicamente uno).
- `skills.imported` — nombres de las shared skills que viajaron dentro del bundle y se registraron a la vez.
- `*.conflicts` — nombres ya presentes, omitidos porque se usó `on_conflict=fail`.
- `*.errors` — `{"name": "...", "error": "..."}` para entradas que el servidor rechazó.
- La respuesta puede incluir además `unresolved_mcps` cuando los servidores MCP referenciados en `metadata.yaml` no están registrados en la plataforma; es un warning, no un error fatal.

## Cómo reportar al usuario

- En 2xx: resume `agent.imported`, cualquier `skills.imported` y `conflicts`/`errors` si no están vacíos. Si la respuesta incluye `unresolved_mcps`, menciónalos para que el usuario los configure desde la interfaz web.
- En no-2xx: muestra el código HTTP y el cuerpo tal cual. Consulta `skills-guides/external-api-calls.md` §5 para interpretar códigos comunes (`401/403` = mTLS o RBAC; `400/422` = validación; `400` con detalles de metadata = `metadata.yaml` malformado).

## Script reutilizable

Si el caller prefiere un script de un solo uso (p. ej. para dejarlo en disco y que el usuario lo reutilice), materialízalo a partir de esta plantilla:

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
