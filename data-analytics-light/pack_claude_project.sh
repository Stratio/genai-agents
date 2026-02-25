#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Parsear argumentos CLI ---
ARG_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)  ARG_NAME="$2"; shift 2 ;;
    *) echo "ERROR: Argumento desconocido: $1"; echo "Uso: $0 [--name NOMBRE]"; exit 1 ;;
  esac
done

# --- Input: usar argumento CLI o preguntar interactivamente ---
if [ -n "$ARG_NAME" ]; then
  PROJECT_NAME="$ARG_NAME"
else
  read -p "Nombre del proyecto [data-analytics-light]: " PROJECT_NAME
  PROJECT_NAME="${PROJECT_NAME:-data-analytics-light}"
fi

PROJECT_DIR="dist/claude_projects/$PROJECT_NAME"

# --- Limpiar si existe ---
if [ -d "$PROJECT_DIR" ]; then
  echo "Borrando proyecto existente en $PROJECT_DIR..."
  rm -rf "$PROJECT_DIR"
fi

mkdir -p "$PROJECT_DIR"

# --- 1. Ficheros raiz (sin cambio de nombre) ---
echo "Copiando ficheros raiz..."
cp CLAUDE.md "$PROJECT_DIR/CLAUDE.md"
cp requirements.txt "$PROJECT_DIR/requirements.txt"
cp setup_env.sh "$PROJECT_DIR/setup_env.sh"

# --- 2. skills-guides/ → prefijo skills-guides_ ---
echo "Copiando skills-guides..."
cp skills-guides/exploration.md "$PROJECT_DIR/skills-guides_exploration.md"

# --- 3. Skills ---
echo "Copiando skills..."

# analyze: SKILL.md → analyze.md, subficheros → analyze_*.md
cp .claude/skills/analyze/SKILL.md "$PROJECT_DIR/analyze.md"
for f in .claude/skills/analyze/*.md; do
  base=$(basename "$f")
  [ "$base" = "SKILL.md" ] && continue
  cp "$f" "$PROJECT_DIR/analyze_${base}"
done

# explore-data: SKILL.md → explore-data.md
cp .claude/skills/explore-data/SKILL.md "$PROJECT_DIR/explore-data.md"

# propose-knowledge: SKILL.md → propose-knowledge.md
cp .claude/skills/propose-knowledge/SKILL.md "$PROJECT_DIR/propose-knowledge.md"

# --- 4. Reemplazos de referencias en todos los .md copiados ---
echo "Actualizando referencias internas..."

# Patron A: rutas skills-guides/
sed -i 's|skills-guides/exploration\.md|skills-guides_exploration.md|g' "$PROJECT_DIR"/*.md
sed -i 's|skills-guides/visualization\.md|skills-guides_visualization.md|g' "$PROJECT_DIR"/*.md

# Patron B: links markdown a subficheros de analyze — buscar con parentesis
sed -i 's|(advanced-analytics\.md)|(analyze_advanced-analytics.md)|g' "$PROJECT_DIR"/*.md
sed -i 's|(analytical-patterns\.md)|(analyze_analytical-patterns.md)|g' "$PROJECT_DIR"/*.md
sed -i 's|(clustering-guide\.md)|(analyze_clustering-guide.md)|g' "$PROJECT_DIR"/*.md

# --- 5. Verificacion ---
echo ""
echo "=== Verificacion ==="

# Contar ficheros
FILE_COUNT=$(ls -1 "$PROJECT_DIR"/*.md "$PROJECT_DIR"/*.txt "$PROJECT_DIR"/*.sh 2>/dev/null | wc -l)
echo "  Ficheros generados: $FILE_COUNT"

# Buscar referencias rotas (rutas con / que no sean URLs ni rutas de output/)
BROKEN=$(grep -rn 'skills-guides/' "$PROJECT_DIR"/*.md 2>/dev/null || true)
BROKEN+=$(grep -rn '(advanced-analytics\.md)' "$PROJECT_DIR"/*.md 2>/dev/null || true)
BROKEN+=$(grep -rn '(analytical-patterns\.md)' "$PROJECT_DIR"/*.md 2>/dev/null || true)
BROKEN+=$(grep -rn '(clustering-guide\.md)' "$PROJECT_DIR"/*.md 2>/dev/null || true)

if [ -n "$BROKEN" ]; then
  echo "  WARN: Referencias posiblemente sin actualizar:"
  echo "$BROKEN" | head -20
else
  echo "  OK: No se encontraron referencias rotas"
fi

# --- 6. ZIP ---
echo ""
if [ -n "$ARG_NAME" ]; then
  # Modo no-interactivo: generar ZIP automaticamente
  GEN_ZIP="s"
else
  read -p "Generar ZIP? [s/N]: " GEN_ZIP
fi
if [[ "$GEN_ZIP" =~ ^[sS]$ ]]; then
  ZIP_NAME="${PROJECT_NAME}.zip"
  (cd "$PROJECT_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
  mv "dist/claude_projects/_tmp_${ZIP_NAME}" "$PROJECT_DIR/${ZIP_NAME}"
  ZIP_SIZE=$(du -sh "$PROJECT_DIR/${ZIP_NAME}" | cut -f1)
  echo "  ZIP: $PROJECT_DIR/${ZIP_NAME} ($ZIP_SIZE)"
fi

echo ""
echo "=== Proyecto empaquetado en $PROJECT_DIR ==="
