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

# --- Nombre: argumento CLI o default ---
COWORK_NAME="${ARG_NAME:-data-analytics-light}"

# Validar kebab-case
if ! echo "$COWORK_NAME" | grep -qE '^[a-z][a-z0-9]*(-[a-z0-9]+)*$'; then
  echo "ERROR: El nombre debe ser kebab-case (ej: mi-agente, data-analytics-light)."
  exit 1
fi

COWORK_DIR="dist/claude_cowork/$COWORK_NAME"

# --- Limpiar si existe ---
if [ -d "$COWORK_DIR" ]; then
  echo "Borrando cowork existente en $COWORK_DIR..."
  rm -rf "$COWORK_DIR"
fi

# --- Paso 1: Generar plugin sin agente ---
echo "Generando plugin sin agente..."
PLUGIN_ARGS=(--name "$COWORK_NAME")
[ -n "$ARG_URL" ] && PLUGIN_ARGS+=(--url "$ARG_URL")
[ -n "$ARG_KEY" ] && PLUGIN_ARGS+=(--key "$ARG_KEY")
bash pack_claude_plugin.sh "${PLUGIN_ARGS[@]}"

PLUGIN_DIR="dist/claude_plugins/$COWORK_NAME"
PLUGIN_ZIP="$PLUGIN_DIR/${COWORK_NAME}.zip"

if [ ! -f "$PLUGIN_ZIP" ]; then
  echo "ERROR: No se encontro el ZIP del plugin en $PLUGIN_ZIP"
  exit 1
fi

# --- Paso 2: Crear directorio cowork ---
echo "Creando estructura cowork..."
mkdir -p "$COWORK_DIR"

# --- Paso 3: Copiar CLAUDE.md con referencias actualizadas ---
echo "Copiando AGENTS.md con referencias actualizadas..."
sed 's|`skills-guides/exploration\.md`|`skills/analyze/exploration.md`|g' AGENTS.md > "$COWORK_DIR/CLAUDE.md"
sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$COWORK_DIR/CLAUDE.md"

# --- Paso 4: Copiar plugin ZIP ---
cp "$PLUGIN_ZIP" "$COWORK_DIR/${COWORK_NAME}.zip"

# --- Paso 5: Generar ZIP final ---
ZIP_NAME="${COWORK_NAME}-cowork.zip"
echo "Generando $ZIP_NAME..."
(cd "$COWORK_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
mv "dist/claude_cowork/_tmp_${ZIP_NAME}" "$COWORK_DIR/${ZIP_NAME}"

# --- Resumen ---
ZIP_SIZE=$(du -sh "$COWORK_DIR/${ZIP_NAME}" | cut -f1)
PLUGIN_SIZE=$(du -sh "$COWORK_DIR/${COWORK_NAME}.zip" | cut -f1)
echo ""
echo "=== Cowork empaquetado ==="
echo "  CLAUDE.md:   $COWORK_DIR/CLAUDE.md (folder instructions, generado desde AGENTS.md)"
echo "  Plugin ZIP:  $COWORK_DIR/${COWORK_NAME}.zip ($PLUGIN_SIZE) (skills + MCP, sin agente)"
echo "  Cowork ZIP:  $COWORK_DIR/${ZIP_NAME} ($ZIP_SIZE) (CLAUDE.md + plugin ZIP)"
echo ""
