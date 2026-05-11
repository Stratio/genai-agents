#!/usr/bin/env bash
# compile.sh — Lightweight monorepo validation
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0

echo "==> Validating monorepo structure..."

# --- Check required root files ---
for f in VERSION LICENSE.txt CHANGELOG.md; do
  if [[ ! -f "$REPO_ROOT/$f" ]]; then
    echo "ERROR: Missing root file: $f" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# --- Check that each module in release-modules exists ---
if [[ ! -f "$REPO_ROOT/release-modules" ]]; then
  echo "ERROR: Missing release-modules file" >&2
  ERRORS=$((ERRORS + 1))
else
  while IFS= read -r module; do
    [[ -z "$module" || "$module" =~ ^# ]] && continue
    if [[ ! -d "$REPO_ROOT/agents/$module" ]]; then
      echo "ERROR: Module '$module' listed in release-modules but does not exist at agents/$module" >&2
      ERRORS=$((ERRORS + 1))
    else
      echo "  [OK] Module: $module"
      # Validate JSON files (skip venv, node_modules, and any dist/ output)
      for json_file in $(find "$REPO_ROOT/agents/$module" -maxdepth 2 -name '*.json' -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/dist/*' 2>/dev/null); do
        if command -v python3 &>/dev/null; then
          if ! python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
            echo "  WARN: Invalid JSON (or contains templates): $(basename "$json_file") in $module"
          fi
        fi
      done
    fi
  done < "$REPO_ROOT/release-modules"
fi

# --- Validate bash syntax of pack_*.sh and bin/*.sh scripts ---
echo "==> Validating bash script syntax..."
for script in "$REPO_ROOT"/pack_*.sh "$REPO_ROOT"/bin/*.sh; do
  [[ ! -f "$script" ]] && continue
  if bash -n "$script" 2>/dev/null; then
    echo "  [OK] $(basename "$script")"
  else
    echo "  ERROR: Invalid syntax: $script" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# --- Result ---
if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FAILED: $ERRORS validation error(s)" >&2
  exit 1
fi

echo "==> Compilation OK — structure valid"
