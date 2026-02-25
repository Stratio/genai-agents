#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Parsear argumentos CLI ---
ARG_NAME="" ARG_URL="" ARG_KEY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)  ARG_NAME="$2"; shift 2 ;;
    --url)   ARG_URL="$2"; shift 2 ;;
    --key)   ARG_KEY="$2"; shift 2 ;;
    *) echo "ERROR: Argumento desconocido: $1"; echo "Uso: $0 [--name NOMBRE] [--url MCP_URL] [--key API_KEY]"; exit 1 ;;
  esac
done

# --- Inputs: usar argumento CLI o preguntar interactivamente ---
if [ -n "$ARG_NAME" ]; then
  PLUGIN_NAME="$ARG_NAME"
else
  read -p "Nombre del plugin [data-analytics-light]: " PLUGIN_NAME
  PLUGIN_NAME="${PLUGIN_NAME:-data-analytics-light}"
fi

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

PLUGIN_DIR="dist/claude_plugins/${PLUGIN_NAME}-marketplace"

# --- Limpiar si existe ---
if [ -d "$PLUGIN_DIR" ]; then
  echo "Borrando marketplace existente en $PLUGIN_DIR..."
  rm -rf "$PLUGIN_DIR"
fi

# --- Crear estructura ---
echo "Creando estructura del marketplace (paquete completo)..."
mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/skills"
mkdir -p "$PLUGIN_DIR/output"

# --- plugin.json ---
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<EOF
{
  "name": "$PLUGIN_NAME",
  "description": "BI/BA Analytics Agent (Light) — Analisis de datos gobernados sin generacion de informes.",
  "version": "1.0.0"
}
EOF

# --- Copiar skills ---
echo "Copiando skills..."
SKILLS_SRC=""
if [ -d ".claude/skills" ]; then
  SKILLS_SRC=".claude/skills"
elif [ -d ".opencode/skills" ]; then
  SKILLS_SRC=".opencode/skills"
elif [ -d ".agents/skills" ]; then
  SKILLS_SRC=".agents/skills"
elif [ -d "skills" ]; then
  SKILLS_SRC="skills"
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

# --- Generar agent file ---
COWORK_DIR="claude-cowork-agent"
mkdir -p "$PLUGIN_DIR/agents"
if [ -d "$COWORK_DIR" ]; then
  echo "Usando overrides de $COWORK_DIR..."
  AGENT_HEADER=$(ls "$COWORK_DIR"/*.md 2>/dev/null | head -1)
  if [ -n "$AGENT_HEADER" ]; then
    # Sustituir name: en el YAML header por el nombre elegido
    sed "s/^name: .*/name: $PLUGIN_NAME/" "$AGENT_HEADER" > "$PLUGIN_DIR/agents/$PLUGIN_NAME.md"
    cat CLAUDE.md >> "$PLUGIN_DIR/agents/$PLUGIN_NAME.md"
  else
    echo "WARN: No se encontro .md en $COWORK_DIR — generando agent por defecto"
    cat > "$PLUGIN_DIR/agents/$PLUGIN_NAME.md" <<YAMLEOF
---
name: $PLUGIN_NAME
description: BI/BA Analytics Agent
model: inherit
---
YAMLEOF
    cat CLAUDE.md >> "$PLUGIN_DIR/agents/$PLUGIN_NAME.md"
  fi
  if [ -f "$COWORK_DIR/settings.json" ]; then
    sed "s/\"agent\": \"[^\"]*\"/\"agent\": \"$PLUGIN_NAME\"/" "$COWORK_DIR/settings.json" > "$PLUGIN_DIR/settings.json"
  fi
else
  echo "No se encontro $COWORK_DIR — generando agent y settings por defecto..."
  cat > "$PLUGIN_DIR/agents/$PLUGIN_NAME.md" <<YAMLEOF
---
name: $PLUGIN_NAME
description: BI/BA Analytics Agent
model: inherit
---
YAMLEOF
  cat CLAUDE.md >> "$PLUGIN_DIR/agents/$PLUGIN_NAME.md"
  cat > "$PLUGIN_DIR/settings.json" <<EOF
{
  "agent": "$PLUGIN_NAME"
}
EOF
fi

# --- Copiar skills-guides/ ---
echo "Copiando skills-guides/..."
cp -r skills-guides/ "$PLUGIN_DIR/skills-guides/"

# --- Copiar setup_env.sh y requirements.txt ---
echo "Copiando setup_env.sh y requirements.txt..."
cp setup_env.sh "$PLUGIN_DIR/setup_env.sh"
cp requirements.txt "$PLUGIN_DIR/requirements.txt"

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
        "X-API-Key": "$MCP_KEY_VALUE"
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
        "X-API-Key": "${MCP_SQL_API_KEY:-}"
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
ZIP_NAME="${PLUGIN_NAME}-marketplace.zip"
echo "Generando $ZIP_NAME..."
(cd "$PLUGIN_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
# Limpiar contenido del directorio y dejar solo el ZIP
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"
mv "dist/claude_plugins/_tmp_${ZIP_NAME}" "$PLUGIN_DIR/${ZIP_NAME}"

# --- Resumen ---
ZIP_SIZE=$(du -sh "$PLUGIN_DIR/${ZIP_NAME}" | cut -f1)
echo ""
echo "=== Marketplace empaquetado (paquete completo) ==="
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
