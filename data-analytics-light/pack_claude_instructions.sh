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

OUTPUT_DIR="dist/claude_instructions/$PROJECT_NAME"
OUTPUT_FILE="$OUTPUT_DIR/CLAUDE.md"

# --- Limpiar si existe ---
if [ -d "$OUTPUT_DIR" ]; then
  echo "Borrando directorio existente en $OUTPUT_DIR..."
  rm -rf "$OUTPUT_DIR"
fi

mkdir -p "$OUTPUT_DIR"

# --- Funcion para append con separador ---
# $1 = fichero fuente, $2 = skip_frontmatter (true/false)
append_section() {
  local src="$1"
  local skip_fm="${2:-false}"

  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"

  if [ "$skip_fm" = "true" ]; then
    # Saltar frontmatter YAML (entre --- y ---)
    awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$src" >> "$OUTPUT_FILE"
  else
    cat "$src" >> "$OUTPUT_FILE"
  fi
}

# --- 1. CLAUDE.md como base ---
echo "Concatenando CLAUDE.md..."
cp CLAUDE.md "$OUTPUT_FILE"

# --- 2. Guias compartidas ---
echo "Concatenando skills-guides..."
append_section "skills-guides/exploration.md"

# --- 3. Skill analyze + sub-guias ---
echo "Concatenando skill analyze..."
append_section ".claude/skills/analyze/SKILL.md" true
append_section ".claude/skills/analyze/advanced-analytics.md"
append_section ".claude/skills/analyze/analytical-patterns.md"
append_section ".claude/skills/analyze/clustering-guide.md"

# --- 4. Skills secundarias ---
echo "Concatenando skills secundarias..."
append_section ".claude/skills/explore-data/SKILL.md" true
append_section ".claude/skills/propose-knowledge/SKILL.md" true

# --- 5. Reemplazos de referencias ---
echo "Actualizando referencias internas..."

# Tipo 1: Links markdown [texto](fichero.md) → [texto](#anchor)
sed -i 's|(advanced-analytics\.md)|(#tecnicas-analiticas-avanzadas)|g' "$OUTPUT_FILE"
sed -i 's|(analytical-patterns\.md)|(#patrones-analiticos-adicionales)|g' "$OUTPUT_FILE"
sed -i 's|(clustering-guide\.md)|(#guia-de-segmentacion-por-reglas-y-rfm)|g' "$OUTPUT_FILE"
# Tipo 2: Referencias en backticks `skills-guides/fichero.md` → texto descriptivo
sed -i 's|`skills-guides/exploration\.md`|la seccion "Guia de Exploracion"|g' "$OUTPUT_FILE"
sed -i 's|`skills-guides/visualization\.md`|la seccion "Guia de Visualizacion"|g' "$OUTPUT_FILE"

# Tipo 3: Texto plano suelto (DESPUES de Tipo 1 para evitar doble reemplazo)
sed -i 's|seccion 4\.2 de SKILL\.md|seccion 4.2 de la Skill de Analisis|g' "$OUTPUT_FILE"

# --- 6. Verificacion ---
echo ""
echo "=== Verificacion ==="

# Contar secciones H1 reales (excluyendo comentarios de codigo en bloques ```)
H1_COUNT=$(awk '
  /^```/{in_code=!in_code}
  /^# / && !in_code{count++}
  END{print count}
' "$OUTPUT_FILE")
echo "  Secciones H1: $H1_COUNT (esperado: 9)"

# Buscar referencias rotas
BROKEN=""
BROKEN+=$(grep -n 'skills-guides/' "$OUTPUT_FILE" 2>/dev/null || true)
BROKEN+=$(grep -n '(advanced-analytics\.md)' "$OUTPUT_FILE" 2>/dev/null || true)
BROKEN+=$(grep -n '(analytical-patterns\.md)' "$OUTPUT_FILE" 2>/dev/null || true)
BROKEN+=$(grep -n '(clustering-guide\.md)' "$OUTPUT_FILE" 2>/dev/null || true)
BROKEN+=$(grep -n 'seccion 4\.2 de SKILL\.md' "$OUTPUT_FILE" 2>/dev/null || true)

if [ -n "$BROKEN" ]; then
  echo "  WARN: Referencias posiblemente sin actualizar:"
  echo "$BROKEN" | head -20
else
  echo "  OK: No se encontraron referencias rotas"
fi

# Verificar anchors corresponden a headers reales
echo ""
echo "  Verificando anchors..."
ALL_OK=true
for anchor in "tecnicas-analiticas-avanzadas" "patrones-analiticos-adicionales" "guia-de-segmentacion-por-reglas-y-rfm"; do
  if grep -qi "^# .*$(echo "$anchor" | sed 's/-/ /g')" "$OUTPUT_FILE" 2>/dev/null; then
    echo "    OK: #$anchor"
  else
    echo "    WARN: #$anchor no tiene header correspondiente"
    ALL_OK=false
  fi
done

# Tamano del fichero
FILE_SIZE=$(du -sh "$OUTPUT_FILE" | cut -f1)
LINE_COUNT=$(wc -l < "$OUTPUT_FILE")
echo ""
echo "  Tamano: $FILE_SIZE ($LINE_COUNT lineas)"

echo ""
echo "=== Fichero generado: $OUTPUT_FILE ==="
