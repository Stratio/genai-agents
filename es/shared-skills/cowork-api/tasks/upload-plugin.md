# Task: subir un bundle de plugin a Stratio Cowork

Registra un ZIP de plugin funcional empaquetado en Stratio Cowork (`genai-api`).

Un bundle de plugin es un ZIP envoltorio que contiene uno o varios sub-ZIPs (agentes y/o skills). Esta task abre el envoltorio, lee el `plugin.yaml` agregado y reparte cada sub-ZIP al endpoint correspondiente de `genai-api` reusando la lógica de `tasks/upload-agent.md` y `tasks/upload-skill.md`.

## Endpoints utilizados

Esta task no llama a un único endpoint de plugin — reparte los sub-bundles:

| Tipo de sub-bundle | Endpoint | Campo multipart | Sub-task a seguir |
|---|---|---|---|
| `agent` | `POST /v1/agents/bundle/import` | `bundle_zip` | `tasks/upload-agent.md` |
| `skills` | `POST /v1/agents/skills/bundle/import` | `file` | `tasks/upload-skill.md` |

## Layout esperado del envoltorio

```
{plugin}-stratio-cowork-{version}.zip
├── plugin.yaml                      # requerido, contiene catálogo bundles[]
├── README.md                        # documentación user-facing
├── agents/                          # opcional; un sub-zip por agente (agents/v1)
│   └── {agent}-stratio-cowork.zip
└── shared-skills/                   # opcional; un sub-zip con bundle de skills
    └── {plugin}-skills.zip
```

`plugin.yaml` declara `bundles[]` — cada entrada tiene `path`, `type` (`agent` o `skills`), `endpoint` y `sha256`. La task lee este catálogo para saber qué subir y dónde.

## Procedimiento

1. **Pre-check** — sigue `skills-guides/external-api-calls.md` §2 (`preflight_external_api`). Si falla, para y reporta los prerequisitos que faltan textualmente — no rechaces con un mensaje genérico.

2. **Abre el envoltorio** en un directorio temporal. Lee `plugin.yaml` y valida que `bundles[]` está presente y no vacío.

3. **Pregunta al usuario** qué estrategia de conflictos aplicar globalmente (usa la convención de preguntas que provee el entorno; en otro caso presenta opciones numeradas):

   > 1. `new_version` — si algún agente/skill ya existe, crea una nueva versión **(recomendado)**
   > 2. `overwrite` — reemplaza la versión draft existente
   > 3. `fail` — para al primer conflicto
   > 4. cancelar

   La estrategia se aplica a cada sub-ZIP. El parámetro `version` para skills no se pregunta intencionadamente.

4. **Reparte cada sub-bundle** en el orden en que aparecen en `bundles[]`. Verifica que el SHA-256 del fichero coincide con el de la entrada del manifest antes de subirlo; si no coincide, aborta y reporta bundle corrupto.

   Para cada entrada:

   ```bash
   USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
   USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
   CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
   GENAI_API_URL="${GENAI_API_URL%/}"

   ON_CONFLICT="<estrategia elegida>"
   SUB_PATH="<bundle.path>"      # p. ej. agents/governance-officer-stratio-cowork.zip
   SUB_TYPE="<bundle.type>"      # "agent" o "skills"
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

5. **Agrega los resultados**. Recoge `imported`, `conflicts`, `errors` y (para uploads de agentes) `unresolved_mcps` de cada respuesta. Si la estrategia es `on_conflict=fail` y algún sub-bundle devolvió conflicto, deja de despachar los restantes y reporta.

## Aviso de atomicidad

Esta task delega N llamadas independientes a endpoints. Si un sub-bundle falla a mitad, los anteriores ya están registrados — **no hay rollback server-side**. El reporte agregado deja explícito el estado parcial para que el usuario decida si reintenta, revierte manualmente o acepta la instalación parcial.

La futura API `plugins/v1` (fase 2) proveerá instalación atómica a nivel plugin; esta task se actualizará para preferirla cuando esté disponible.

## Reporte agregado

Devuelve al usuario un único resumen que cubra todos los sub-bundles, con esta forma:

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

Si algún sub-bundle devolvió un código HTTP no-2xx, expón el código y el body literalmente junto al resumen agregado. Ver `skills-guides/external-api-calls.md` §5 sobre cómo interpretar códigos comunes (`401/403` = mTLS o RBAC; `400/422` = validación).

## Script reutilizable

Si quien llama prefiere un script de un disparo, materializa esta plantilla (delega por-bundle):

```bash
#!/bin/bash
# Sube un bundle de plugin de Stratio Cowork a genai-api.
set -euo pipefail

ZIP_PATH="${1:?Uso: $0 <plugin-stratio-cowork.zip> [on_conflict]}"
ON_CONFLICT="${2:-new_version}"

: "${GENAI_API_URL:?GENAI_API_URL no establecido}"
USER_CERT_PATH="${USER_CERT_PATH:-/vault/secrets/cert.crt}"
USER_KEY_PATH="${USER_KEY_PATH:-/vault/secrets/cert.key}"
CA_CERT_PATH="${CA_CERT_PATH:-/stratio/certs/ca.crt}"
GENAI_API_URL="${GENAI_API_URL%/}"

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
unzip -q "$ZIP_PATH" -d "$WORK"

[ -f "$WORK/plugin.yaml" ] || { echo "ERROR: plugin.yaml ausente en el bundle" >&2; exit 1; }

# Itera bundles[] con python
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
            sys.exit(f"ERROR: SHA-256 mismatch para {entry['path']}")
    field = "bundle_zip" if entry["type"] == "agent" else "file"
    url = f"{base_url}{entry['endpoint']}?on_conflict={on_conflict}"
    print(f"--- Subiendo {entry['type']}: {entry['path']}")
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
