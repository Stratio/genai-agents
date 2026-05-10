#!/usr/bin/env bash
# clean.sh — Cleans build-generated artifacts
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Cleaning artifacts..."

# --- Global dist/ ---
if [[ -d "$REPO_ROOT/dist" ]]; then
  rm -rf "$REPO_ROOT/dist"
  echo "  [OK] dist/"
fi

# --- Per-agent artifacts ---
if [[ -f "$REPO_ROOT/release-modules" ]]; then
  while IFS= read -r module; do
    [[ -z "$module" || "$module" =~ ^# ]] && continue
    MODULE_DIR="$REPO_ROOT/$module"
    [[ ! -d "$MODULE_DIR" ]] && continue

    if [[ -d "$MODULE_DIR/dist" ]]; then
      rm -rf "$MODULE_DIR/dist"
      echo "  [OK] $module/dist"
    fi

    for artifact_dir in __pycache__ .pytest_cache .venv; do
      if [[ -d "$MODULE_DIR/$artifact_dir" ]]; then
        rm -rf "$MODULE_DIR/$artifact_dir"
        echo "  [OK] $module/$artifact_dir"
      fi
    done
  done < "$REPO_ROOT/release-modules"
fi

echo "==> Cleaning completed"
