#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

# --- Parsear argumentos CLI ---
ARG_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)  ARG_NAME="$2"; shift 2 ;;
    *) echo "ERROR: Argumento desconocido: $1"; echo "Uso: $0 [--name NOMBRE]"; exit 1 ;;
  esac
done

# --- Nombre: argumento CLI o default ---
PROJECT_NAME="${ARG_NAME:-data-analytics-light}"

PROJECT_DIR="dist/claude_projects/$PROJECT_NAME"

# --- Limpiar si existe ---
if [ -d "$PROJECT_DIR" ]; then
  echo "Borrando proyecto existente en $PROJECT_DIR..."
  rm -rf "$PROJECT_DIR"
fi

mkdir -p "$PROJECT_DIR"

# --- 1. Ficheros raiz (sin cambio de nombre) ---
echo "Copiando ficheros raiz..."
cp AGENTS.md "$PROJECT_DIR/CLAUDE.md"
cp requirements.txt "$PROJECT_DIR/requirements.txt"
cp setup_env.sh "$PROJECT_DIR/setup_env.sh"

# --- 2. skills-guides/ → prefijo skills-guides_ ---
echo "Copiando skills-guides..."
# Leer shared-guides del agente para saber que guides incluir
if [ -f "shared-guides" ]; then
  while IFS= read -r guide || [ -n "$guide" ]; do
    [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
    guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
    guide_flat="skills-guides_$(echo "$guide" | tr '/' '_')"
    if [ -f "$guide_src" ]; then
      cp "$guide_src" "$PROJECT_DIR/$guide_flat"
    else
      echo "WARN: shared guide '$guide' no encontrado en $guide_src" >&2
    fi
  done < "shared-guides"
fi
# Copiar guides locales restantes (si existen)
if [ -d "skills-guides" ]; then
  for f in skills-guides/*.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    # No duplicar los que ya vienen de shared-skill-guides
    dst="$PROJECT_DIR/skills-guides_$base"
    [ -f "$dst" ] && continue
    cp "$f" "$dst"
  done
fi

# --- 3. Skills ---
echo "Copiando skills..."

# Resolver directorio base de skills (fallback en 4 ubicaciones)
SKILLS_SRC=""
if [ -d "skills" ]; then
  SKILLS_SRC="skills"
elif [ -d ".claude/skills" ]; then
  SKILLS_SRC=".claude/skills"
elif [ -d ".opencode/skills" ]; then
  SKILLS_SRC=".opencode/skills"
elif [ -d ".agents/skills" ]; then
  SKILLS_SRC=".agents/skills"
fi

if [ -z "$SKILLS_SRC" ]; then
  echo "ERROR: No se encontro directorio de skills" >&2
  exit 1
fi

# Normalizar: detectar si el origen usa formato plano (analyze.md) o canónico (analyze/SKILL.md)
# y crear un directorio temporal normalizado si es necesario
SKILLS_NORM=""
# Comprobar si hay .md sueltos en la raíz de SKILLS_SRC (formato plano)
HAS_FLAT=$(find "$SKILLS_SRC" -maxdepth 1 -name '*.md' -not -name 'SKILL.md' 2>/dev/null | head -1)
if [ -n "$HAS_FLAT" ]; then
  # Formato plano: normalizar a canónico en directorio temporal
  SKILLS_NORM=$(mktemp -d)
  cp -r "$SKILLS_SRC/." "$SKILLS_NORM/"
  for md_file in "$SKILLS_NORM"/*.md; do
    [ -f "$md_file" ] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$SKILLS_NORM/$skill_name"
    mv "$md_file" "$SKILLS_NORM/$skill_name/SKILL.md"
  done
  SKILLS_SRC="$SKILLS_NORM"
fi

# analyze: SKILL.md → analyze.md, subficheros → analyze_*.md (caso especial: tiene subficheros)
cp "$SKILLS_SRC/analyze/SKILL.md" "$PROJECT_DIR/analyze.md"
for f in "$SKILLS_SRC"/analyze/*.md; do
  base=$(basename "$f")
  [ "$base" = "SKILL.md" ] && continue
  cp "$f" "$PROJECT_DIR/analyze_${base}"
done

# Otras skills locales (formato simple: <nombre>/SKILL.md → <nombre>.md)
for skill_dir in "$SKILLS_SRC"/*/; do
  skill_name=$(basename "$skill_dir")
  [ "$skill_name" = "analyze" ] && continue
  [ -f "$skill_dir/SKILL.md" ] || continue
  cp "$skill_dir/SKILL.md" "$PROJECT_DIR/${skill_name}.md"
done

# Limpiar directorio temporal si se creó
if [ -n "$SKILLS_NORM" ]; then
  rm -rf "$SKILLS_NORM"
fi

# Shared skills (desde manifiesto shared-skills del agente)
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    # Prioridad local: si ya existe en el output, no sobreescribir
    if [ -f "$PROJECT_DIR/${skill_name}.md" ]; then
      echo "  '$skill_name' omitida (version local tiene prioridad)"
      continue
    fi
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name/SKILL.md"
    if [ -f "$skill_src" ]; then
      cp "$skill_src" "$PROJECT_DIR/${skill_name}.md"
    else
      echo "WARN: shared skill '$skill_name' no encontrada en $skill_src" >&2
    fi
  done < "shared-skills"
fi

# --- 4. Reemplazos de referencias en todos los .md copiados ---
echo "Actualizando referencias internas..."

# Patron A: rutas skills-guides/
sed -i 's|skills-guides/exploration\.md|skills-guides_exploration.md|g' "$PROJECT_DIR"/*.md
sed -i 's|skills-guides/visualization\.md|skills-guides_visualization.md|g' "$PROJECT_DIR"/*.md

# Patron B: links markdown a subficheros de analyze — buscar con parentesis
sed -i 's|(advanced-analytics\.md)|(analyze_advanced-analytics.md)|g' "$PROJECT_DIR"/*.md
sed -i 's|(analytical-patterns\.md)|(analyze_analytical-patterns.md)|g' "$PROJECT_DIR"/*.md
sed -i 's|(clustering-guide\.md)|(analyze_clustering-guide.md)|g' "$PROJECT_DIR"/*.md
sed -i 's|(visualization\.md)|(analyze_visualization.md)|g' "$PROJECT_DIR"/*.md

# Patron C: rutas de subficheros de analyze en texto plano (sin parentesis)
sed -i 's|skills/analyze/visualization\.md|analyze_visualization.md|g' "$PROJECT_DIR"/*.md

# Patron D: AGENTS.md → CLAUDE.md (referencias en texto plano dentro de skills)
sed -i 's/AGENTS\.md/CLAUDE.md/g' "$PROJECT_DIR"/*.md

sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PROJECT_DIR"/*.md

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
BROKEN+=$(grep -rn '(visualization\.md)' "$PROJECT_DIR"/*.md 2>/dev/null || true)

if [ -n "$BROKEN" ]; then
  echo "  WARN: Referencias posiblemente sin actualizar:"
  echo "$BROKEN" | head -20
else
  echo "  OK: No se encontraron referencias rotas"
fi

# --- 6. ZIP ---
echo ""
# Generar ZIP siempre (CI/CD-friendly, sin interaccion)
ZIP_NAME="${PROJECT_NAME}.zip"
(cd "$PROJECT_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
mv "dist/claude_projects/_tmp_${ZIP_NAME}" "$PROJECT_DIR/${ZIP_NAME}"
ZIP_SIZE=$(du -sh "$PROJECT_DIR/${ZIP_NAME}" | cut -f1)
echo "  ZIP: $PROJECT_DIR/${ZIP_NAME} ($ZIP_SIZE)"

echo ""
echo "=== Proyecto empaquetado en $PROJECT_DIR ==="
