#!/usr/bin/env bash
# package.sh — Empaquetado completo con zips versionados
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
DIST_DIR="$REPO_ROOT/dist"

echo "==> Empaquetando genai-agents v$VERSION..."

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# --- Pack generico por agente (claude_code + opencode) ---
while IFS= read -r module; do
  [[ -z "$module" || "$module" =~ ^# ]] && continue
  MODULE_DIR="$REPO_ROOT/$module"

  if [[ ! -d "$MODULE_DIR" ]]; then
    echo "  WARN: Modulo '$module' no existe, saltando"
    continue
  fi

  echo "  [$module] Empaquetando claude_code..."
  bash "$REPO_ROOT/pack_claude_code.sh" --agent "$module" --name "$module"
  if [[ -d "$MODULE_DIR/dist/claude_code/$module" ]]; then
    (cd "$MODULE_DIR/dist/claude_code/$module" && zip -r "$DIST_DIR/${module}-claude-code-${VERSION}.zip" . -q)
    echo "    -> dist/${module}-claude-code-${VERSION}.zip"
  fi

  echo "  [$module] Empaquetando opencode..."
  bash "$REPO_ROOT/pack_opencode.sh" --agent "$module" --name "$module"
  if [[ -d "$MODULE_DIR/dist/opencode/$module" ]]; then
    (cd "$MODULE_DIR/dist/opencode/$module" && zip -r "$DIST_DIR/${module}-opencode-${VERSION}.zip" . -q)
    echo "    -> dist/${module}-opencode-${VERSION}.zip"
  fi

done < "$REPO_ROOT/release-modules"

# --- Pack adicionales de data-analytics-light ---
DAL_DIR="$REPO_ROOT/data-analytics-light"
if [[ -d "$DAL_DIR" ]]; then
  for pack_script in "$DAL_DIR"/pack_claude_*.sh; do
    [[ ! -f "$pack_script" ]] && continue
    SCRIPT_NAME=$(basename "$pack_script")

    # Extraer tipo del nombre: pack_claude_project.sh -> project
    PACK_TYPE="${SCRIPT_NAME#pack_claude_}"
    PACK_TYPE="${PACK_TYPE%.sh}"

    echo "  [data-analytics-light] Ejecutando $SCRIPT_NAME..."
    (cd "$DAL_DIR" && bash "$SCRIPT_NAME" --name data-analytics-light) || {
      echo "  WARN: $SCRIPT_NAME fallo — continuando"
      continue
    }

    # Buscar el directorio de output generado
    case "$PACK_TYPE" in
      project)   OUTPUT_SUBDIR="dist/claude_projects/data-analytics-light" ;;
      instructions) OUTPUT_SUBDIR="dist/claude_instructions/data-analytics-light" ;;
      plugin)    OUTPUT_SUBDIR="dist/claude_plugins/data-analytics-light" ;;
      marketplace) OUTPUT_SUBDIR="dist/claude_plugins/data-analytics-light-marketplace" ;;
      *) echo "  WARN: Tipo desconocido: $PACK_TYPE"; continue ;;
    esac

    # Los pack scripts generan un ZIP dentro del directorio
    ZIP_FILE=$(find "$DAL_DIR/$OUTPUT_SUBDIR" -name '*.zip' -maxdepth 1 2>/dev/null | head -1)
    if [[ -n "$ZIP_FILE" ]]; then
      cp "$ZIP_FILE" "$DIST_DIR/data-analytics-light-claude-${PACK_TYPE}-${VERSION}.zip"
      echo "    -> dist/data-analytics-light-claude-${PACK_TYPE}-${VERSION}.zip"
    fi
  done
fi

# --- Zip de fuentes ---
echo "  Generando zip de fuentes..."
SOURCES_ZIP="genai-agents-sources-${VERSION}.zip"
(cd "$REPO_ROOT" && zip -r "$DIST_DIR/$SOURCES_ZIP" . \
  -x "dist/*" \
  -x ".git/*" \
  -x "*/.venv/*" \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x "*/node_modules/*" \
  -x "*/.idea/*" \
  -x "*/output/*" \
  -q)
echo "    -> dist/$SOURCES_ZIP"

# --- Zip global ---
echo "  Generando zip global..."
(cd "$DIST_DIR" && zip -r "genai-agents-${VERSION}.zip" *.zip -q 2>/dev/null) || true
echo "    -> dist/genai-agents-${VERSION}.zip"

# --- Resumen ---
echo ""
echo "=== Empaquetado completado ==="
echo "  Version: $VERSION"
echo "  Artefactos:"
ls -lh "$DIST_DIR"/*.zip 2>/dev/null | while read -r line; do
  echo "    $line"
done
