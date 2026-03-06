#!/usr/bin/env bash
# pack_shared_skills.sh — Empaqueta las shared skills del monorepo en un ZIP autocontenido
# Uso: bash pack_shared_skills.sh [--name <nombre>] [--skill <skill-name>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Fase 0 — Parseo y validación
# ---------------------------------------------------------------------------
PACK_NAME=""
SKILL_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) PACK_NAME="$2"; shift 2 ;;
    --skill) SKILL_FILTER="$2"; shift 2 ;;
    *) echo "ERROR: argumento desconocido: $1" >&2; echo "Uso: bash pack_shared_skills.sh [--name <nombre>] [--skill <skill-name>]" >&2; exit 1 ;;
  esac
done

if [[ -n "$SKILL_FILTER" ]]; then
  PACK_NAME="${PACK_NAME:-$SKILL_FILTER}"
else
  PACK_NAME="${PACK_NAME:-shared-skills}"
fi

if [[ ! -d "$MONOREPO_ROOT/shared-skills" ]]; then
  echo "ERROR: directorio shared-skills/ no encontrado en $MONOREPO_ROOT" >&2
  exit 1
fi

if [[ -n "$SKILL_FILTER" && ! -d "$MONOREPO_ROOT/shared-skills/$SKILL_FILTER" ]]; then
  echo "ERROR: skill '$SKILL_FILTER' no encontrada en shared-skills/" >&2
  exit 1
fi

if [[ -n "$SKILL_FILTER" ]]; then
  echo "==> Empaquetando skill individual '$SKILL_FILTER' como '$PACK_NAME'"
else
  echo "==> Empaquetando shared skills como '$PACK_NAME'"
fi

# ---------------------------------------------------------------------------
# Fase 1 — Staging
# ---------------------------------------------------------------------------
STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT

# ---------------------------------------------------------------------------
# Fase 2 — Función para procesar una skill + iterar
# ---------------------------------------------------------------------------
N_SKILLS=0
N_GUIDES=0

_pack_one_skill() {
  local skill_dir="$1"
  local dest_dir="$2"

  # Copiar contenido de la skill
  mkdir -p "$dest_dir"
  cp -r "$skill_dir"/. "$dest_dir/"

  # Leer skill-guides manifest y copiar guides a la raíz de la skill
  if [[ -f "$skill_dir/skill-guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$dest_dir/$guide"
        N_GUIDES=$((N_GUIDES + 1))
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$dest_dir/$guide"
        N_GUIDES=$((N_GUIDES + 1))
      else
        echo "    WARN: guide '$guide' no encontrado en $guide_src — omitido" >&2
      fi
    done < "$skill_dir/skill-guides"
  fi

  # Eliminar skill-guides del output
  rm -f "$dest_dir/skill-guides"

  N_SKILLS=$((N_SKILLS + 1))
}

if [[ -n "$SKILL_FILTER" ]]; then
  # Modo individual: ficheros directamente en la raíz del staging
  _pack_one_skill "$MONOREPO_ROOT/shared-skills/$SKILL_FILTER" "$STAGING"
else
  # Modo bulk: cada skill en su subcarpeta
  for skill_dir in "$MONOREPO_ROOT/shared-skills"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    _pack_one_skill "$skill_dir" "$STAGING/$skill_name"
  done
fi

echo "    $N_SKILLS skill(s), $N_GUIDES guide(s) copiados"

# ---------------------------------------------------------------------------
# Fase 3 — Sustituciones de rutas en .md y .txt
# ---------------------------------------------------------------------------
find "$STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|skills-guides/||g' {} \;
find "$STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|shared-skill-guides/||g' {} \;
echo "    Sustituciones de rutas aplicadas"

# ---------------------------------------------------------------------------
# Fase 4 — Generar ZIP
# ---------------------------------------------------------------------------
mkdir -p "$MONOREPO_ROOT/dist"
ZIP_PATH="$MONOREPO_ROOT/dist/${PACK_NAME}.zip"
rm -f "$ZIP_PATH"
(cd "$STAGING" && zip -r "$ZIP_PATH" . -q)
ZIP_SIZE=$(du -sh "$ZIP_PATH" | cut -f1)
echo "    ZIP generado: dist/${PACK_NAME}.zip ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Fase 5 — Verificación
# ---------------------------------------------------------------------------
echo "    Verificando integridad..."
ERRORS=0

# Sin referencias residuales a skills-guides/ ni shared-skill-guides/
REFS=$(grep -rl 'skills-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null | wc -l) || true
if [[ "$REFS" -gt 0 ]]; then
  echo "    ERROR: $REFS fichero(s) aún contienen 'skills-guides/':" >&2
  grep -rl 'skills-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null >&2 || true
  ERRORS=$((ERRORS + 1))
fi

REFS2=$(grep -rl 'shared-skill-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null | wc -l) || true
if [[ "$REFS2" -gt 0 ]]; then
  echo "    ERROR: $REFS2 fichero(s) aún contienen 'shared-skill-guides/':" >&2
  grep -rl 'shared-skill-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null >&2 || true
  ERRORS=$((ERRORS + 1))
fi

# Verificar SKILL.md — en modo bulk, comprobar subcarpetas; en modo individual, comprobar raíz
if [[ -n "$SKILL_FILTER" ]]; then
  if [[ ! -f "$STAGING/SKILL.md" ]]; then
    echo "    ERROR: SKILL.md no encontrado en el output" >&2
    ERRORS=$((ERRORS + 1))
  fi
else
  for skill_dir in "$STAGING"/*/; do
    [[ -d "$skill_dir" ]] || continue
    if [[ ! -f "$skill_dir/SKILL.md" ]]; then
      echo "    ERROR: $(basename "$skill_dir") no tiene SKILL.md" >&2
      ERRORS=$((ERRORS + 1))
    fi
  done
fi

# No debe quedar ningún fichero skill-guides
LEFTOVER=$(find "$STAGING" -name 'skill-guides' -type f 2>/dev/null | wc -l) || true
if [[ "$LEFTOVER" -gt 0 ]]; then
  echo "    ERROR: fichero(s) skill-guides residuales en el output" >&2
  ERRORS=$((ERRORS + 1))
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FALLO: $ERRORS error(es) de verificación" >&2
  exit 1
fi

echo "==> OK — $N_SKILLS skill(s) empaquetadas en dist/${PACK_NAME}.zip"
