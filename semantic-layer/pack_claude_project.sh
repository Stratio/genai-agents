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
PROJECT_NAME="${ARG_NAME:-semantic-layer}"

PROJECT_DIR="dist/claude_projects/$PROJECT_NAME"

# --- Limpiar si existe ---
if [ -d "$PROJECT_DIR" ]; then
  echo "Borrando proyecto existente en $PROJECT_DIR..."
  rm -rf "$PROJECT_DIR"
fi

mkdir -p "$PROJECT_DIR"

# --- 1. Fichero raiz ---
echo "Copiando ficheros raiz..."
cp AGENTS.md "$PROJECT_DIR/CLAUDE.md"

# --- 2. skills-guides/ → prefijo skills-guides_ ---
echo "Copiando skills-guides..."
# Leer shared-guides del agente para saber que guides incluir
if [ -f "shared-guides" ]; then
  while IFS= read -r guide || [ -n "$guide" ]; do
    [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
    guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
    if [ -d "$guide_src" ]; then
      # Aplanar directorio: cada fichero interno se convierte en skills-guides_dir_file.md
      while IFS= read -r sub_file; do
        [ -f "$sub_file" ] || continue
        rel="${sub_file#$guide_src/}"
        flat_name="skills-guides_${guide}_$(echo "$rel" | tr '/' '_')"
        cp "$sub_file" "$PROJECT_DIR/$flat_name"
      done < <(find "$guide_src" -type f)
    elif [ -f "$guide_src" ]; then
      guide_flat="skills-guides_$(echo "$guide" | tr '/' '_')"
      cp "$guide_src" "$PROJECT_DIR/$guide_flat"
    else
      echo "WARN: shared guide '$guide' no encontrado en $guide_src" >&2
    fi
  done < "shared-guides"
fi
# Copiar guides locales restantes (si existen)
if [ -d "skills-guides" ]; then
  for entry in skills-guides/*; do
    [ -e "$entry" ] || continue
    base=$(basename "$entry")
    if [ -d "$entry" ]; then
      # Aplanar directorio local
      while IFS= read -r sub_file; do
        [ -f "$sub_file" ] || continue
        rel="${sub_file#$entry/}"
        flat_name="skills-guides_${base}_$(echo "$rel" | tr '/' '_')"
        [ -f "$PROJECT_DIR/$flat_name" ] && continue
        cp "$sub_file" "$PROJECT_DIR/$flat_name"
      done < <(find "$entry" -type f)
    elif [ -f "$entry" ]; then
      dst="$PROJECT_DIR/skills-guides_$base"
      [ -f "$dst" ] && continue
      cp "$entry" "$dst"
    fi
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

# Copiar skills locales (formato: <nombre>/SKILL.md → <nombre>.md)
if [ -n "$SKILLS_SRC" ]; then
  # Normalizar: detectar si hay .md sueltos (formato plano)
  SKILLS_NORM=""
  HAS_FLAT=$(find "$SKILLS_SRC" -maxdepth 1 -name '*.md' -not -name 'SKILL.md' 2>/dev/null | head -1)
  if [ -n "$HAS_FLAT" ]; then
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

  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    [ -f "$skill_dir/SKILL.md" ] || continue
    cp "$skill_dir/SKILL.md" "$PROJECT_DIR/${skill_name}.md"
  done

  # Limpiar directorio temporal si se creo
  if [ -n "$SKILLS_NORM" ]; then
    rm -rf "$SKILLS_NORM"
  fi
else
  echo "WARN: No se encontro directorio de skills"
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
sed -i 's|skills-guides/stratio-semantic-layer-tools\.md|skills-guides_stratio-semantic-layer-tools.md|g' "$PROJECT_DIR"/*.md

# Patron B: AGENTS.md → CLAUDE.md (referencias en texto plano dentro de skills)
sed -i 's/AGENTS\.md/CLAUDE.md/g' "$PROJECT_DIR"/*.md

sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PROJECT_DIR"/*.md

# --- 5. Verificacion ---
echo ""
echo "=== Verificacion ==="

# Contar ficheros
FILE_COUNT=$(ls -1 "$PROJECT_DIR"/*.md 2>/dev/null | wc -l)
echo "  Ficheros generados: $FILE_COUNT"

# Buscar referencias rotas (rutas skills-guides/ que no fueron sustituidas)
BROKEN=$(grep -rn 'skills-guides/' "$PROJECT_DIR"/*.md 2>/dev/null || true)

if [ -n "$BROKEN" ]; then
  echo "  WARN: Referencias posiblemente sin actualizar:"
  echo "$BROKEN" | head -20
else
  echo "  OK: No se encontraron referencias rotas"
fi

# --- 6. ZIP ---
echo ""
ZIP_NAME="${PROJECT_NAME}.zip"
(cd "$PROJECT_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
mv "dist/claude_projects/_tmp_${ZIP_NAME}" "$PROJECT_DIR/${ZIP_NAME}"
ZIP_SIZE=$(du -sh "$PROJECT_DIR/${ZIP_NAME}" | cut -f1)
echo "  ZIP: $PROJECT_DIR/${ZIP_NAME} ($ZIP_SIZE)"

echo ""
echo "=== Proyecto empaquetado en $PROJECT_DIR ==="
