# Tarea: subir un bundle de skill a Stratio Cowork

Registrar un ZIP de skill empaquetado en Stratio Cowork (`genai-api`).

## Endpoint

| | |
|---|---|
| Método | `POST` |
| Path | `/v1/agents/skills/bundle/import` |
| Content type | `multipart/form-data` |
| Campo multipart | `file` (el ZIP de la skill) |

## Parámetros de query

| Parámetro | Requerido | Por defecto | Valores permitidos | Notas |
|---|---|---|---|---|
| `on_conflict` | no | `new_version` | `new_version` \| `overwrite` \| `fail` | Estrategia cuando ya existe una skill con el mismo nombre. |
| `version` | no | (lo decide el servidor) | versión semántica (p. ej. `1.2.3`, `1.2.3-SNAPSHOT`) | Avanzado: SNAPSHOT sobrescribe el draft in-situ; las versiones fijas auto-publican al cambiar el checksum. |

## Estructura esperada del ZIP

El ZIP es una carpeta de skill autocontenida; la API admite ambos layouts:

```
my-skill.zip                       my-skill.zip
└── SKILL.md                       └── my-skill/
    otros ficheros...                  ├── SKILL.md
                                       └── otros ficheros...
```

La API extrae el contenido, parsea cualquier `SKILL.md` que encuentre (uno o varios) y registra cada uno como una versión de skill.

## Procedimiento

1. **Pre-check** — sigue `skills-guides/external-api-calls.md` §2 (`preflight_external_api`). El pre-check es un health check del entorno (variables de entorno, rutas de certificados). Si falla, detente y reporta al usuario qué prerequisites faltan — no silencies el fallo y no rechaces con un genérico "no puedo". El bundle ya está empaquetado correctamente; solo el paso de despliegue no se completó, y el usuario puede decidir cómo proceder.

2. **Pregunta al usuario** qué estrategia de conflicto aplicar (usa la convención de preguntas que provea el entorno; en su defecto, presenta opciones numeradas):

   > 1. `new_version` — si la skill ya existe, crea una nueva versión **(recomendado)**
   > 2. `overwrite` — sobrescribe la versión draft existente
   > 3. `fail` — detente si la skill ya existe
   > 4. cancelar

   El query `version` deliberadamente no se pregunta — tiene una semántica matizada (SNAPSHOT vs. fija) que no encaja en un flujo conversacional. El script lo acepta como tercer argumento posicional para uso manual avanzado.

3. **Ejecuta la llamada**:

   ```bash
   USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
   USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
   CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
   GENAI_API_URL="${GENAI_API_URL%/}"

   ZIP_PATH="<ruta al ZIP de la skill>"
   ON_CONFLICT="<estrategia elegida>"
   VERSION=""   # déjalo vacío salvo que se pida explícitamente

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

## Respuesta esperada

`HTTP 200` con un cuerpo JSON con esta forma:

```json
{
  "imported": ["my-skill"],
  "conflicts": [],
  "errors": []
}
```

- `imported` — nombres de las skills registradas correctamente (una por cada `SKILL.md` encontrado en el ZIP).
- `conflicts` — nombres que ya existían y no se registraron porque se usó `on_conflict=fail`.
- `errors` — entradas con la forma `{"name": "...", "error": "..."}` para skills que el servidor rechazó.

## Cómo reportar al usuario

- En 2xx: resume `imported`, `conflicts` y `errors`. Si `errors` no está vacío, muéstralo tal cual.
- En no-2xx: muestra el código HTTP y el cuerpo tal cual. Consulta `skills-guides/external-api-calls.md` §5 para interpretar códigos comunes (`401/403` = mTLS o RBAC; `400/422` = validación).

## Script reutilizable

Si el caller prefiere un script de un solo uso (p. ej. para dejarlo en disco y que el usuario lo reutilice), materialízalo a partir de esta plantilla:

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
