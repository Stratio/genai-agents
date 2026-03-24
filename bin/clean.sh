#!/usr/bin/env bash
# clean.sh — Limpia artefactos generados por el build
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Limpiando artefactos..."

# --- dist/ global ---
if [[ -d "$REPO_ROOT/dist" ]]; then
  rm -rf "$REPO_ROOT/dist"
  echo "  [OK] dist/"
fi

# --- Artefactos por agente ---
if [[ -f "$REPO_ROOT/release-modules" ]]; then
  while IFS= read -r module; do
    [[ -z "$module" || "$module" =~ ^# ]] && continue
    MODULE_DIR="$REPO_ROOT/$module"
    [[ ! -d "$MODULE_DIR" ]] && continue

    if [[ -d "$MODULE_DIR/dist" ]]; then
      rm -rf "$MODULE_DIR/dist"
      echo "  [OK] $module/dist"
    fi

    # Legacy: limpiar directorios de artefactos pre-migracion a dist/
    for legacy_dir in claude_code opencode claude_projects claude_ai_projects claude_plugins; do
      if [[ -d "$MODULE_DIR/$legacy_dir" ]]; then
        rm -rf "$MODULE_DIR/$legacy_dir"
        echo "  [OK] $module/$legacy_dir (legacy)"
      fi
    done

    for artifact_dir in __pycache__ .pytest_cache .venv; do
      if [[ -d "$MODULE_DIR/$artifact_dir" ]]; then
        rm -rf "$MODULE_DIR/$artifact_dir"
        echo "  [OK] $module/$artifact_dir"
      fi
    done
  done < "$REPO_ROOT/release-modules"
fi

echo "==> Limpieza completada"
