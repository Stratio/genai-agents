#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

# --- Parsear argumentos CLI ---
ARG_NAME="" ARG_GOV_URL="" ARG_GOV_KEY="" ARG_SQL_URL="" ARG_SQL_KEY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)    ARG_NAME="$2"; shift 2 ;;
    --gov-url) ARG_GOV_URL="$2"; shift 2 ;;
    --gov-key) ARG_GOV_KEY="$2"; shift 2 ;;
    --sql-url) ARG_SQL_URL="$2"; shift 2 ;;
    --sql-key) ARG_SQL_KEY="$2"; shift 2 ;;
    *) echo "ERROR: Argumento desconocido: $1"; echo "Uso: $0 [--name NOMBRE] [--gov-url URL] [--gov-key KEY] [--sql-url URL] [--sql-key KEY]"; exit 1 ;;
  esac
done

# --- Nombre: argumento CLI o default ---
COWORK_NAME="${ARG_NAME:-data-quality}"

# Validar kebab-case
if ! echo "$COWORK_NAME" | grep -qE '^[a-z][a-z0-9]*(-[a-z0-9]+)*$'; then
  echo "ERROR: El nombre debe ser kebab-case (ej: mi-agente, data-quality)."
  exit 1
fi

COWORK_DIR="dist/claude_cowork/$COWORK_NAME"

# --- Limpiar si existe ---
if [ -d "$COWORK_DIR" ]; then
  echo "Borrando cowork existente en $COWORK_DIR..."
  rm -rf "$COWORK_DIR"
fi

# ============================================================
# Paso 1: Construir plugin inline (skills + MCP, sin agente)
# ============================================================
echo "Construyendo plugin inline..."
PLUGIN_BUILD="$COWORK_DIR/_plugin_build"
mkdir -p "$PLUGIN_BUILD/.claude-plugin"
mkdir -p "$PLUGIN_BUILD/skills"

# --- plugin.json ---
cat > "$PLUGIN_BUILD/.claude-plugin/plugin.json" <<EOF
{
  "name": "$COWORK_NAME",
  "description": "Data Quality Agent",
  "version": "1.0.0"
}
EOF

# --- Copiar skills locales ---
echo "Copiando skills..."
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

if [ -n "$SKILLS_SRC" ]; then
  cp -r "$SKILLS_SRC"/* "$PLUGIN_BUILD/skills/"
  # Normalizar: archivos .md sueltos → subcarpeta/SKILL.md
  for md_file in "$PLUGIN_BUILD/skills/"*.md; do
    [ -f "$md_file" ] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$PLUGIN_BUILD/skills/$skill_name"
    mv "$md_file" "$PLUGIN_BUILD/skills/$skill_name/SKILL.md"
  done
  echo "  Skills copiadas desde $SKILLS_SRC"
else
  echo "WARN: No se encontro directorio de skills — el plugin no tendra skills."
fi

# --- Copiar shared skills (si las declara el agente) ---
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    skill_dst="$PLUGIN_BUILD/skills/$skill_name"
    if [ ! -d "$skill_src" ]; then
      echo "  WARN: shared skill '$skill_name' no encontrada en $skill_src — omitida" >&2
      continue
    fi
    # Prioridad local
    if [ -d "$skill_dst" ]; then
      echo "  '$skill_name' omitida (version local tiene prioridad)"
      continue
    fi
    cp -r "$skill_src" "$skill_dst"
    # Eliminar fichero skill-guides del output
    rm -f "$skill_dst/skill-guides"
    echo "  Shared skill '$skill_name' incluida"
  done < "shared-skills"
fi

# --- Recopilar y copiar skills-guides (inline: dentro de cada skill) ---
GUIDES_NEEDED=()
# Desde shared-skills/*/skill-guides
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    if [ -f "$skill_src/skill-guides" ]; then
      while IFS= read -r guide || [ -n "$guide" ]; do
        [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
        GUIDES_NEEDED+=("shared:$guide")
      done < "$skill_src/skill-guides"
    fi
  done < "shared-skills"
fi
# Desde shared-guides del agente
if [ -f "shared-guides" ]; then
  while IFS= read -r guide || [ -n "$guide" ]; do
    [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
    GUIDES_NEEDED+=("shared:$guide")
  done < "shared-guides"
fi
# Guides locales
if [ -d "skills-guides" ]; then
  for f in skills-guides/*.md; do
    [ -f "$f" ] || continue
    GUIDES_NEEDED+=("local:$(basename "$f")")
  done
fi

# Construir lista deduplicada
declare -A _GUIDES_MAP=()
for entry in "${GUIDES_NEEDED[@]}"; do
  src_type="${entry%%:*}"
  guide_name="${entry#*:}"
  _GUIDES_MAP["$guide_name"]="$src_type"
done

if [ ${#_GUIDES_MAP[@]} -gt 0 ]; then
  echo "Copiando skills-guides a skills..."
  # Copiar guide dentro de cada skill del plugin
  for skill_dir in "$PLUGIN_BUILD/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    for guide_name in "${!_GUIDES_MAP[@]}"; do
      src_type="${_GUIDES_MAP[$guide_name]}"
      if [ "$src_type" = "shared" ]; then
        guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide_name"
      else
        guide_src="skills-guides/$guide_name"
      fi
      if [ -d "$guide_src" ]; then
        cp -r "$guide_src" "$skill_dir/$guide_name"
      elif [ -f "$guide_src" ]; then
        cp "$guide_src" "$skill_dir/$guide_name"
      fi
    done
  done
  sed -i 's|`skills-guides/stratio-data-tools\.md`|`stratio-data-tools.md`|g' "$PLUGIN_BUILD/skills/"*/SKILL.md 2>/dev/null || true
  sed -i 's|`skills-guides/exploration\.md`|`exploration.md`|g' "$PLUGIN_BUILD/skills/"*/SKILL.md 2>/dev/null || true
fi

# --- Sustitucion de placeholders ---
sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PLUGIN_BUILD/skills/"*/SKILL.md 2>/dev/null || true

# --- .mcp.json del plugin (2 servidores: gov + sql) ---
GOV_URL_VALUE="${ARG_GOV_URL:-\$\{MCP_GOV_URL:-http://127.0.0.1:8080/mcp\}}"
GOV_KEY_VALUE="${ARG_GOV_KEY:-\$\{MCP_GOV_API_KEY:-\}}"
SQL_URL_VALUE="${ARG_SQL_URL:-\$\{MCP_SQL_URL:-http://127.0.0.1:8080/mcp\}}"
SQL_KEY_VALUE="${ARG_SQL_KEY:-\$\{MCP_SQL_API_KEY:-\}}"

if [ -n "$ARG_GOV_URL" ] || [ -n "$ARG_GOV_KEY" ] || [ -n "$ARG_SQL_URL" ] || [ -n "$ARG_SQL_KEY" ]; then
  cat > "$PLUGIN_BUILD/.mcp.json" <<EOF
{
  "mcpServers": {
    "stratio_gov": {
      "type": "http",
      "url": "$GOV_URL_VALUE",
      "headers": {
        "X-API-Key": "$GOV_KEY_VALUE",
        "Authorization": "Bearer $GOV_KEY_VALUE"
      },
      "allowedTools": ["*"]
    },
    "stratio_data": {
      "type": "http",
      "url": "$SQL_URL_VALUE",
      "headers": {
        "X-API-Key": "$SQL_KEY_VALUE",
        "Authorization": "Bearer $SQL_KEY_VALUE"
      },
      "allowedTools": ["*"]
    }
  }
}
EOF
else
  cat > "$PLUGIN_BUILD/.mcp.json" <<'EOF'
{
  "mcpServers": {
    "stratio_gov": {
      "type": "http",
      "url": "${MCP_GOV_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_GOV_API_KEY:-}",
        "Authorization": "Bearer ${MCP_GOV_API_KEY:-}"
      },
      "allowedTools": ["*"]
    },
    "stratio_data": {
      "type": "http",
      "url": "${MCP_SQL_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_SQL_API_KEY:-}",
        "Authorization": "Bearer ${MCP_SQL_API_KEY:-}"
      },
      "allowedTools": ["*"]
    }
  }
}
EOF
fi

# --- Generar plugin ZIP ---
PLUGIN_ZIP_NAME="${COWORK_NAME}.zip"
echo "Generando plugin ZIP..."
(cd "$PLUGIN_BUILD" && zip -r "../${PLUGIN_ZIP_NAME}" . -q)

# ============================================================
# Paso 2: Generar CLAUDE.md desde AGENTS.md
# ============================================================
echo "Generando CLAUDE.md desde AGENTS.md..."
sed 's|`skills-guides/stratio-data-tools\.md`|`skills/assess-quality/stratio-data-tools.md`|g' AGENTS.md > "$COWORK_DIR/CLAUDE.md"
sed -i 's|`skills-guides/exploration\.md`|`skills/assess-quality/exploration.md`|g' "$COWORK_DIR/CLAUDE.md"
sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$COWORK_DIR/CLAUDE.md"

# --- README de usuario ---
if [ -f "USER_README.md" ]; then
  cp USER_README.md "$COWORK_DIR/README.md"
  echo "  README.md copiado desde USER_README.md"
fi

# ============================================================
# Paso 3: Limpiar build temporal
# ============================================================
rm -rf "$PLUGIN_BUILD"

# --- Resumen ---
PLUGIN_SIZE=$(du -sh "$COWORK_DIR/${COWORK_NAME}.zip" | cut -f1)
echo ""
echo "=== Cowork empaquetado ==="
echo "  CLAUDE.md:   $COWORK_DIR/CLAUDE.md (folder instructions, generado desde AGENTS.md)"
echo "  Plugin ZIP:  $COWORK_DIR/${COWORK_NAME}.zip ($PLUGIN_SIZE) (skills + MCP, sin agente)"
echo ""
