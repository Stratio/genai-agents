#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Parsear argumentos CLI ---
ARG_NAME="" ARG_URL="" ARG_KEY="" WITH_AGENT=false SHARED_GUIDES=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)  ARG_NAME="$2"; shift 2 ;;
    --url)   ARG_URL="$2"; shift 2 ;;
    --key)   ARG_KEY="$2"; shift 2 ;;
    --with-agent) WITH_AGENT=true; shift ;;
    --shared-guides) SHARED_GUIDES=true; shift ;;
    *) echo "ERROR: Argumento desconocido: $1"; echo "Uso: $0 [--name NOMBRE] [--url MCP_URL] [--key API_KEY] [--with-agent] [--shared-guides]"; exit 1 ;;
  esac
done

# --- Nombre: argumento CLI o default ---
PLUGIN_NAME="${ARG_NAME:-data-analytics-light}"

# Validar kebab-case
if ! echo "$PLUGIN_NAME" | grep -qE '^[a-z][a-z0-9]*(-[a-z0-9]+)*$'; then
  echo "ERROR: El nombre del plugin debe ser kebab-case (ej: mi-plugin, data-analytics-light)."
  exit 1
fi

# MCP: si se pasan args, usar valores concretos; si no, dejar env vars como template
MCP_URL_RESOLVED=""
MCP_KEY_RESOLVED=""
if [ -n "$ARG_URL" ]; then
  MCP_URL_RESOLVED="$ARG_URL"
fi
if [ -n "$ARG_KEY" ]; then
  MCP_KEY_RESOLVED="$ARG_KEY"
fi

PLUGIN_DIR="dist/claude_plugins/$PLUGIN_NAME"

# --- Limpiar si existe ---
if [ -d "$PLUGIN_DIR" ]; then
  echo "Borrando plugin existente en $PLUGIN_DIR..."
  rm -rf "$PLUGIN_DIR"
fi

# --- Crear estructura ---
echo "Creando estructura del plugin..."
mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/skills"

# --- plugin.json ---
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<EOF
{
  "name": "$PLUGIN_NAME",
  "description": "BI/BA Analytics Agent (Light)",
  "version": "1.0.0"
}
EOF

# --- Copiar skills ---
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
  cp -r "$SKILLS_SRC"/* "$PLUGIN_DIR/skills/"
  # Normalizar: archivos .md sueltos → subcarpeta/SKILL.md
  for md_file in "$PLUGIN_DIR/skills/"*.md; do
    [ -f "$md_file" ] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$PLUGIN_DIR/skills/$skill_name"
    mv "$md_file" "$PLUGIN_DIR/skills/$skill_name/SKILL.md"
  done
  echo "  Skills copiadas desde $SKILLS_SRC"
else
  echo "WARN: No se encontro directorio de skills — el plugin no tendra skills."
fi

# --- Copiar skills-guides ---
if [ -d "skills-guides" ]; then
  if [ "$SHARED_GUIDES" = true ]; then
    # Modo compartido: skills-guides/ en la raiz del plugin, referenciado con ruta relativa
    echo "Copiando skills-guides a raiz del plugin (modo compartido)..."
    mkdir -p "$PLUGIN_DIR/skills-guides"
    cp skills-guides/*.md "$PLUGIN_DIR/skills-guides/"
    sed -i 's|`skills-guides/exploration\.md`|`../../skills-guides/exploration.md`|g' "$PLUGIN_DIR/skills/"*/SKILL.md 2>/dev/null || true
  else
    # Modo por defecto: duplicar junto al SKILL.md de cada skill que los usa
    echo "Copiando skills-guides a skills..."
    for skill_dir in "$PLUGIN_DIR/skills/analyze" "$PLUGIN_DIR/skills/explore-data"; do
      if [ -d "$skill_dir" ]; then
        cp skills-guides/*.md "$skill_dir/"
      fi
    done
    sed -i 's|`skills-guides/exploration\.md`|`exploration.md`|g' "$PLUGIN_DIR/skills/"*/SKILL.md 2>/dev/null || true
  fi
fi

# --- Generar agent file (solo con --with-agent) ---
if [ "$WITH_AGENT" = true ]; then
  echo "Generando agente del plugin..."
  mkdir -p "$PLUGIN_DIR/agents"
  cat > "$PLUGIN_DIR/agents/$PLUGIN_NAME.md" <<YAMLEOF
---
name: $PLUGIN_NAME
description: Analista senior de BI/BA que convierte preguntas de negocio en analisis accionables con datos gobernados via MCP. Usar proactivamente para cualquier tarea de analisis de datos.
model: inherit
---
YAMLEOF
  cat AGENTS.md >> "$PLUGIN_DIR/agents/$PLUGIN_NAME.md"
  cat > "$PLUGIN_DIR/settings.json" <<EOF
{
  "agent": "$PLUGIN_NAME"
}
EOF
  # Actualizar referencias a skills-guides/ en agent
  if [ "$SHARED_GUIDES" = true ]; then
    sed -i 's|`skills-guides/exploration\.md`|`skills-guides/exploration.md`|g' "$PLUGIN_DIR/agents/"*.md 2>/dev/null || true
  else
    sed -i 's|`skills-guides/exploration\.md`|`skills/analyze/exploration.md`|g' "$PLUGIN_DIR/agents/"*.md 2>/dev/null || true
  fi
  sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PLUGIN_DIR/agents/"*.md 2>/dev/null || true
fi
sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PLUGIN_DIR/skills/"*/SKILL.md 2>/dev/null || true

# --- .mcp.json del plugin ---
if [ -n "$MCP_URL_RESOLVED" ] || [ -n "$MCP_KEY_RESOLVED" ]; then
  # Valores concretos proporcionados via args
  MCP_URL_VALUE="${MCP_URL_RESOLVED:-\$\{MCP_SQL_URL:-http://127.0.0.1:8080/mcp\}}"
  MCP_KEY_VALUE="${MCP_KEY_RESOLVED:-\$\{MCP_SQL_API_KEY:-\}}"
  cat > "$PLUGIN_DIR/.mcp.json" <<EOF
{
  "mcpServers": {
    "sql": {
      "type": "http",
      "url": "$MCP_URL_VALUE",
      "headers": {
        "X-API-Key": "$MCP_KEY_VALUE",
        "Authorization": "Bearer $MCP_KEY_VALUE"
      },
      "allowedTools": [
        "stratio_list_business_domains",
        "stratio_list_domain_tables",
        "stratio_get_tables_details",
        "stratio_get_table_columns_details",
        "stratio_generate_sql",
        "stratio_query_data",
        "stratio_search_domain_knowledge",
        "stratio_execute_sql",
        "stratio_profile_data",
        "stratio_propose_knowledge"
      ]
    }
  }
}
EOF
else
  # Sin args: dejar templates con variables de entorno
  cat > "$PLUGIN_DIR/.mcp.json" <<'EOF'
{
  "mcpServers": {
    "sql": {
      "type": "http",
      "url": "${MCP_SQL_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_SQL_API_KEY:-}",
        "Authorization": "Bearer ${MCP_SQL_API_KEY:-}"
      },
      "allowedTools": [
        "stratio_list_business_domains",
        "stratio_list_domain_tables",
        "stratio_get_tables_details",
        "stratio_get_table_columns_details",
        "stratio_generate_sql",
        "stratio_query_data",
        "stratio_search_domain_knowledge",
        "stratio_execute_sql",
        "stratio_profile_data",
        "stratio_propose_knowledge"
      ]
    }
  }
}
EOF
fi

# --- Generar ZIP ---
ZIP_NAME="${PLUGIN_NAME}.zip"
echo "Generando $ZIP_NAME..."
(cd "$PLUGIN_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
# Limpiar contenido del directorio y dejar solo el ZIP
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"
mv "dist/claude_plugins/_tmp_${ZIP_NAME}" "$PLUGIN_DIR/${ZIP_NAME}"

# --- Resumen ---
ZIP_SIZE=$(du -sh "$PLUGIN_DIR/${ZIP_NAME}" | cut -f1)
echo ""
echo "=== Plugin empaquetado ==="
echo "  ZIP: $PLUGIN_DIR/${ZIP_NAME} ($ZIP_SIZE)"
echo ""
if [ -n "$MCP_URL_RESOLVED" ]; then
  echo "  MCP URL: $MCP_URL_RESOLVED"
else
  echo "  MCP URL: \${MCP_SQL_URL:-http://127.0.0.1:8080/mcp} (env var)"
fi
if [ -n "$MCP_KEY_RESOLVED" ]; then
  echo "  MCP API Key: (configurada)"
else
  echo "  MCP API Key: \${MCP_SQL_API_KEY:-} (env var)"
fi
echo ""
