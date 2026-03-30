#!/usr/bin/env bash
# pack_stratio_cowork.sh — Genera un ZIP compuesto con dos sub-ZIPs para OpenCode:
#   1. {name}-opencode-agent.zip    → agente sin las shared skills declaradas
#   2. {name}-shared-skills.zip       → shared skills del agente (autocontenidas)
#   Resultado: dist/{name}-stratio-cowork.zip
#
# Uso: bash pack_stratio_cowork.sh --agent <path> [--name <nombre-kebab>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Fase 0 — Parseo y validación
# ---------------------------------------------------------------------------
AGENT_PATH=""
AGENT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_PATH="$2"; shift 2 ;;
    --name)  AGENT_NAME="$2"; shift 2 ;;
    *) echo "ERROR: argumento desconocido: $1" >&2
       echo "Uso: bash pack_stratio_cowork.sh --agent <path> [--name <nombre-kebab>]" >&2
       exit 1 ;;
  esac
done

if [[ -z "$AGENT_PATH" ]]; then
  echo "ERROR: --agent es obligatorio" >&2
  echo "Uso: bash pack_stratio_cowork.sh --agent <path> [--name <nombre-kebab>]" >&2
  exit 1
fi

# Resolver ruta absoluta
if [[ -d "$SCRIPT_DIR/$AGENT_PATH" ]]; then
  AGENT_ABS="$(cd "$SCRIPT_DIR/$AGENT_PATH" && pwd)"
elif [[ -d "$AGENT_PATH" ]]; then
  AGENT_ABS="$(cd "$AGENT_PATH" && pwd)"
else
  echo "ERROR: directorio del agente no encontrado: $AGENT_PATH" >&2
  exit 1
fi

# Nombre por defecto: basename del directorio
if [[ -z "$AGENT_NAME" ]]; then
  AGENT_NAME="$(basename "$AGENT_ABS")"
fi

# Validar formato kebab-case
KEBAB_RE='^[a-z][a-z0-9]*(-[a-z0-9]+)*$'
if [[ ! "$AGENT_NAME" =~ $KEBAB_RE ]]; then
  echo "ERROR: el nombre '$AGENT_NAME' no es kebab-case válido (ej: mi-agente, data-analytics)" >&2
  exit 1
fi

echo "==> Generando bundle OpenCode para '$AGENT_NAME'"
echo "    Fuente : $AGENT_ABS"

# ---------------------------------------------------------------------------
# Fase 1 — Leer manifiesto de shared skills
# ---------------------------------------------------------------------------
SHARED_SKILLS=()

if [[ -f "$AGENT_ABS/shared-skills" ]]; then
  while IFS= read -r skill_name || [[ -n "$skill_name" ]]; do
    [[ -z "$skill_name" || "$skill_name" == \#* ]] && continue
    # Solo incluir skills que realmente existen en shared-skills/
    if [[ -d "$MONOREPO_ROOT/shared-skills/$skill_name" ]]; then
      SHARED_SKILLS+=("$skill_name")
    else
      echo "    WARN: shared skill '$skill_name' no encontrada en shared-skills/ — omitida" >&2
    fi
  done < "$AGENT_ABS/shared-skills"
fi

if [[ ${#SHARED_SKILLS[@]} -eq 0 ]]; then
  echo "    WARN: no hay shared skills declaradas para este agente" >&2
fi

echo "    [1] ${#SHARED_SKILLS[@]} shared skill(s) detectadas: ${SHARED_SKILLS[*]:-ninguna}"

# ---------------------------------------------------------------------------
# Fase 2 — Empaquetar agente completo con pack_opencode.sh
# ---------------------------------------------------------------------------
echo "    [2] Ejecutando pack_opencode.sh..."
bash "$MONOREPO_ROOT/pack_opencode.sh" --agent "$AGENT_ABS" --name "$AGENT_NAME"

STAGING_FULL="$AGENT_ABS/dist/opencode/$AGENT_NAME"

if [[ ! -d "$STAGING_FULL" ]]; then
  echo "ERROR: staging de pack_opencode.sh no encontrado en $STAGING_FULL" >&2
  exit 1
fi
echo "    [2] Staging completo listo en $STAGING_FULL"

# ---------------------------------------------------------------------------
# Fase 3 — Clonar staging y eliminar shared skills del clon
# ---------------------------------------------------------------------------
echo "    [3] Clonando staging para versión sin shared skills..."
STAGING_NO_SHARED=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED"' EXIT

cp -r "$STAGING_FULL/." "$STAGING_NO_SHARED/"

N_REMOVED=0
for skill_name in "${SHARED_SKILLS[@]}"; do
  skill_dst="$STAGING_NO_SHARED/.opencode/skills/$skill_name"
  if [[ -d "$skill_dst" ]]; then
    rm -rf "$skill_dst"
    N_REMOVED=$((N_REMOVED + 1))
    echo "    [3] Skill '$skill_name' eliminada del staging"
  else
    echo "    [3] WARN: '$skill_name' no encontrada en el staging (posiblemente overrideada por local)" >&2
  fi
done

# Si skills-guides/ quedó vacío tras eliminar las shared skills, limpiarlo
SKILLS_GUIDES_DIR="$STAGING_NO_SHARED/skills-guides"
if [[ -d "$SKILLS_GUIDES_DIR" ]]; then
  # Comprobar si las skills locales usan algún guide de skills-guides/
  # Los guides de shared-skills están embebidos dentro de cada carpeta de skill,
  # no en skills-guides/ — pero shared-guides del agente sí se copian ahí.
  # Por tanto no tocamos skills-guides/: puede contener guides del agente.
  echo "    [3] skills-guides/ conservado (puede contener guides propios del agente)"
fi

echo "    [3] $N_REMOVED skill(s) eliminadas del clon"

# ---------------------------------------------------------------------------
# Fase 4 — Sub-ZIP del agente sin shared skills
# ---------------------------------------------------------------------------
BUNDLE_STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED" "$BUNDLE_STAGING"' EXIT

mkdir -p "$BUNDLE_STAGING"

ZIP_NO_SHARED="${AGENT_NAME}-opencode-agent.zip"
echo "    [4] Generando $ZIP_NO_SHARED..."
(cd "$STAGING_NO_SHARED" && zip -r "$BUNDLE_STAGING/$ZIP_NO_SHARED" . -q)
ZIP_SIZE=$(du -sh "$BUNDLE_STAGING/$ZIP_NO_SHARED" | cut -f1)
echo "    [4] $ZIP_NO_SHARED generado ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Fase 5 — Sub-ZIP de shared skills del agente
# ---------------------------------------------------------------------------
ZIP_SHARED="${AGENT_NAME}-shared-skills.zip"
echo "    [5] Generando $ZIP_SHARED..."

SKILLS_STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED" "$BUNDLE_STAGING" "$SKILLS_STAGING"' EXIT

N_SKILLS_PACKED=0
N_GUIDES_PACKED=0

for skill_name in "${SHARED_SKILLS[@]}"; do
  skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
  skill_dst="$SKILLS_STAGING/$skill_name"

  mkdir -p "$skill_dst"
  cp -r "$skill_src/." "$skill_dst/"

  # Embeber guides declarados en skill-guides
  if [[ -f "$skill_src/skill-guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$skill_dst/$guide"
        N_GUIDES_PACKED=$((N_GUIDES_PACKED + 1))
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$skill_dst/$guide"
        N_GUIDES_PACKED=$((N_GUIDES_PACKED + 1))
      else
        echo "    WARN: guide '$guide' no encontrado — omitido" >&2
      fi
    done < "$skill_src/skill-guides"
  fi

  # Eliminar el manifiesto skill-guides del output
  rm -f "$skill_dst/skill-guides"

  N_SKILLS_PACKED=$((N_SKILLS_PACKED + 1))
done

# Sustituciones de rutas
find "$SKILLS_STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|skills-guides/||g' {} \;
find "$SKILLS_STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|shared-skill-guides/||g' {} \;

(cd "$SKILLS_STAGING" && zip -r "$BUNDLE_STAGING/$ZIP_SHARED" . -q)
ZIP_SIZE=$(du -sh "$BUNDLE_STAGING/$ZIP_SHARED" | cut -f1)
echo "    [5] $ZIP_SHARED generado ($N_SKILLS_PACKED skill(s), $N_GUIDES_PACKED guide(s)) ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Fase 5.5 — Incluir fichero mcps (si existe en el agente)
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/mcps" ]]; then
  cp "$AGENT_ABS/mcps" "$BUNDLE_STAGING/mcps"
  echo "    [5.5] Fichero mcps incluido"
else
  echo "    [5.5] Sin fichero mcps — omitido"
fi

# ---------------------------------------------------------------------------
# Fase 6 — ZIP contenedor
# ---------------------------------------------------------------------------
mkdir -p "$MONOREPO_ROOT/dist"
BUNDLE_ZIP="$MONOREPO_ROOT/dist/${AGENT_NAME}-stratio-cowork.zip"
rm -f "$BUNDLE_ZIP"
(cd "$BUNDLE_STAGING" && zip -r "$BUNDLE_ZIP" . -q)
BUNDLE_SIZE=$(du -sh "$BUNDLE_ZIP" | cut -f1)
echo "    [6] Bundle generado: dist/${AGENT_NAME}-stratio-cowork.zip ($BUNDLE_SIZE)"

# ---------------------------------------------------------------------------
# Fase 7 — Verificación de integridad
# ---------------------------------------------------------------------------
echo "    [7] Verificando integridad..."
ERRORS=0

# Ambos sub-ZIPs deben estar dentro del bundle
BUNDLE_CONTENTS=$(unzip -Z1 "$BUNDLE_ZIP" 2>/dev/null) || true
if ! echo "$BUNDLE_CONTENTS" | grep -q "$ZIP_NO_SHARED"; then
  echo "    ERROR: $ZIP_NO_SHARED no encontrado en el bundle" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$BUNDLE_CONTENTS" | grep -q "$ZIP_SHARED"; then
  echo "    ERROR: $ZIP_SHARED no encontrado en el bundle" >&2
  ERRORS=$((ERRORS + 1))
fi

# Sub-ZIP del agente debe contener AGENTS.md
AGENT_ZIP_CONTENTS=$(unzip -Z1 "$BUNDLE_STAGING/$ZIP_NO_SHARED" 2>/dev/null) || true
if ! echo "$AGENT_ZIP_CONTENTS" | grep -q 'AGENTS\.md'; then
  echo "    ERROR: AGENTS.md no encontrado en $ZIP_NO_SHARED" >&2
  ERRORS=$((ERRORS + 1))
fi

# Sub-ZIP del agente NO debe contener las shared skills eliminadas
for skill_name in "${SHARED_SKILLS[@]}"; do
  if echo "$AGENT_ZIP_CONTENTS" | grep -q "\.opencode/skills/$skill_name/"; then
    echo "    ERROR: skill '$skill_name' aún presente en $ZIP_NO_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# Sub-ZIP de skills debe contener SKILL.md por cada skill
for skill_name in "${SHARED_SKILLS[@]}"; do
  SKILLS_ZIP_CONTENTS=$(unzip -Z1 "$BUNDLE_STAGING/$ZIP_SHARED" 2>/dev/null) || true
  if ! echo "$SKILLS_ZIP_CONTENTS" | grep -q "${skill_name}/SKILL\.md"; then
    echo "    ERROR: ${skill_name}/SKILL.md no encontrado en $ZIP_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# Sin referencias residuales a skill-guides en el ZIP de skills
SKILLS_REFS=$(unzip -p "$BUNDLE_STAGING/$ZIP_SHARED" "*/SKILL.md" 2>/dev/null | grep -c 'skills-guides/' || true)
if [[ "$SKILLS_REFS" -gt 0 ]]; then
  echo "    ERROR: referencias residuales a skills-guides/ en $ZIP_SHARED" >&2
  ERRORS=$((ERRORS + 1))
fi

# Si el agente declara mcps, debe estar en el bundle
if [[ -f "$AGENT_ABS/mcps" ]]; then
  if ! echo "$BUNDLE_CONTENTS" | grep -q "^mcps$"; then
    echo "    ERROR: fichero mcps no encontrado en el bundle" >&2
    ERRORS=$((ERRORS + 1))
  fi
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FALLO: $ERRORS error(es) de verificación" >&2
  exit 1
fi

echo "==> OK — dist/${AGENT_NAME}-stratio-cowork.zip"
echo "    Contiene:"
echo "      - $ZIP_NO_SHARED  (agente sin shared skills)"
echo "      - $ZIP_SHARED  (${#SHARED_SKILLS[@]} shared skill(s))"
[[ -f "$AGENT_ABS/mcps" ]] && echo "      - mcps  (listado de MCPs)"
