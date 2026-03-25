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

# --- Pack shared-skills ---
echo "  [shared-skills] Empaquetando shared skills..."
bash "$REPO_ROOT/pack_shared_skills.sh" --name shared-skills
if [[ -f "$DIST_DIR/shared-skills.zip" ]]; then
  mv "$DIST_DIR/shared-skills.zip" "$DIST_DIR/shared-skills-${VERSION}.zip"
  echo "    -> dist/shared-skills-${VERSION}.zip"
fi

# --- Pack shared-skills individuales ---
for skill_dir in "$REPO_ROOT/shared-skills"/*/; do
  [[ -d "$skill_dir" ]] || continue
  skill_name="$(basename "$skill_dir")"
  echo "  [shared-skills] Empaquetando skill individual '$skill_name'..."
  bash "$REPO_ROOT/pack_shared_skills.sh" --skill "$skill_name"
  if [[ -f "$DIST_DIR/${skill_name}.zip" ]]; then
    mv "$DIST_DIR/${skill_name}.zip" "$DIST_DIR/shared-skill-${skill_name}-${VERSION}.zip"
    echo "    -> dist/shared-skill-${skill_name}-${VERSION}.zip"
  fi
done

# --- Pack adicionales de data-analytics-light ---
DAL_DIR="$REPO_ROOT/data-analytics-light"
if [[ -d "$DAL_DIR" ]]; then
  for pack_script in "$DAL_DIR"/pack_claude_*.sh; do
    [[ ! -f "$pack_script" ]] && continue
    SCRIPT_NAME=$(basename "$pack_script")

    # Extraer tipo del nombre: pack_claude_ai_project.sh -> ai_project
    PACK_TYPE="${SCRIPT_NAME#pack_claude_}"
    PACK_TYPE="${PACK_TYPE%.sh}"

    echo "  [data-analytics-light] Ejecutando $SCRIPT_NAME..."
    (cd "$DAL_DIR" && bash "$SCRIPT_NAME" --name data-analytics-light) || {
      echo "  WARN: $SCRIPT_NAME fallo — continuando"
      continue
    }

    # Buscar el directorio de output generado
    case "$PACK_TYPE" in
      ai_project) OUTPUT_SUBDIR="dist/claude_ai_projects/data-analytics-light" ;;
      cowork)     OUTPUT_SUBDIR="dist/claude_cowork/data-analytics-light" ;;
      *) echo "  WARN: Tipo desconocido: $PACK_TYPE"; continue ;;
    esac

    # Normalizar PACK_TYPE para el nombre del ZIP (ai_project -> ai-project)
    ZIP_TYPE=$(echo "$PACK_TYPE" | tr '_' '-')

    OUTPUT_DIR="$DAL_DIR/$OUTPUT_SUBDIR"
    if [[ -d "$OUTPUT_DIR" ]]; then
      (cd "$OUTPUT_DIR" && zip -r "$DIST_DIR/data-analytics-light-claude-${ZIP_TYPE}-${VERSION}.zip" . -q)
      echo "    -> dist/data-analytics-light-claude-${ZIP_TYPE}-${VERSION}.zip"
    fi
  done
fi

# --- Pack adicionales de semantic-layer ---
SL_DIR="$REPO_ROOT/semantic-layer"
if [[ -d "$SL_DIR" ]]; then
  for pack_script in "$SL_DIR"/pack_claude_*.sh; do
    [[ ! -f "$pack_script" ]] && continue
    SCRIPT_NAME=$(basename "$pack_script")

    # Extraer tipo del nombre: pack_claude_ai_project.sh -> ai_project
    PACK_TYPE="${SCRIPT_NAME#pack_claude_}"
    PACK_TYPE="${PACK_TYPE%.sh}"

    echo "  [semantic-layer] Ejecutando $SCRIPT_NAME..."
    (cd "$SL_DIR" && bash "$SCRIPT_NAME" --name semantic-layer) || {
      echo "  WARN: $SCRIPT_NAME fallo — continuando"
      continue
    }

    # Buscar el directorio de output generado
    case "$PACK_TYPE" in
      ai_project) OUTPUT_SUBDIR="dist/claude_ai_projects/semantic-layer" ;;
      cowork)     OUTPUT_SUBDIR="dist/claude_cowork/semantic-layer" ;;
      *) echo "  WARN: Tipo desconocido: $PACK_TYPE"; continue ;;
    esac

    # Normalizar PACK_TYPE para el nombre del ZIP (ai_project -> ai-project)
    ZIP_TYPE=$(echo "$PACK_TYPE" | tr '_' '-')

    OUTPUT_DIR="$SL_DIR/$OUTPUT_SUBDIR"
    if [[ -d "$OUTPUT_DIR" ]]; then
      (cd "$OUTPUT_DIR" && zip -r "$DIST_DIR/semantic-layer-claude-${ZIP_TYPE}-${VERSION}.zip" . -q)
      echo "    -> dist/semantic-layer-claude-${ZIP_TYPE}-${VERSION}.zip"
    fi
  done
fi


# --- Resumen ---
echo ""
echo "=== Empaquetado completado ==="
echo "  Version: $VERSION"
echo "  Artefactos:"
ls -lh "$DIST_DIR"/*.zip 2>/dev/null | while read -r line; do
  echo "    $line"
done
