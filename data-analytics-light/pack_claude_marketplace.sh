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

DEFAULT_URL="${MCP_SQL_URL:-http://127.0.0.1:8080/mcp}"
if [ -n "$ARG_URL" ]; then
  MCP_URL="$ARG_URL"
else
  read -p "URL del MCP SQL [$DEFAULT_URL]: " MCP_URL
  MCP_URL="${MCP_URL:-$DEFAULT_URL}"
fi

DEFAULT_KEY="${MCP_SQL_API_KEY:-}"
if [ -n "$ARG_KEY" ]; then
  MCP_KEY="$ARG_KEY"
else
  read -p "API Key del MCP SQL [env var MCP_SQL_API_KEY]: " MCP_KEY
  MCP_KEY="${MCP_KEY:-$DEFAULT_KEY}"
fi

PLUGIN_DIR="claude_plugins/${PLUGIN_NAME}-marketplace"

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
if [ -d ".claude/skills" ]; then
  cp -r .claude/skills/* "$PLUGIN_DIR/skills/"
else
  echo "WARN: No se encontro .claude/skills/ — el plugin no tendra skills."
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

# --- .mcp.json del plugin (valores resueltos, sin env vars) ---
cat > "$PLUGIN_DIR/.mcp.json" <<EOF
{
  "mcpServers": {
    "sql": {
      "type": "http",
      "url": "$MCP_URL",
      "headers": {
        "X-API-Key": "$MCP_KEY"
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

# --- Generar ZIP ---
ZIP_NAME="${PLUGIN_NAME}-marketplace.zip"
echo "Generando $ZIP_NAME..."
(cd "$PLUGIN_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
# Limpiar contenido del directorio y dejar solo el ZIP
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"
mv "claude_plugins/_tmp_${ZIP_NAME}" "$PLUGIN_DIR/${ZIP_NAME}"

# --- Resumen ---
ZIP_SIZE=$(du -sh "$PLUGIN_DIR/${ZIP_NAME}" | cut -f1)
echo ""
echo "=== Marketplace empaquetado (paquete completo) ==="
echo "  ZIP: $PLUGIN_DIR/${ZIP_NAME} ($ZIP_SIZE)"
echo ""
echo "  MCP URL: $MCP_URL"
echo "  MCP API Key: ${MCP_KEY:+(configurada)}${MCP_KEY:-(vacia — usar env var)}"
echo ""
