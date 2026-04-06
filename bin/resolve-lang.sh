#!/usr/bin/env bash
# resolve-lang.sh — Creates a temporary repo tree in the specified language
#
# For --lang en: copies the repo and removes *.es.md / *.es.yaml
# For --lang es: copies the repo, replaces .md with .es.md, removes residuals
#
# Usage: bin/resolve-lang.sh --lang <code> --source <repo> --target <directory>
set -euo pipefail

LANG_CODE=""
SOURCE=""
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang)   LANG_CODE="$2"; shift 2 ;;
    --source) SOURCE="$2";    shift 2 ;;
    --target) TARGET="$2";    shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$LANG_CODE" || -z "$SOURCE" || -z "$TARGET" ]]; then
  echo "ERROR: --lang, --source and --target are required" >&2
  echo "Usage: bin/resolve-lang.sh --lang <code> --source <repo> --target <dir>" >&2
  exit 1
fi

if [[ ! -d "$SOURCE" ]]; then
  echo "ERROR: source directory not found: $SOURCE" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Phase 1 — Copy full repo (excluding artifacts and git metadata)
# ---------------------------------------------------------------------------
mkdir -p "$TARGET"

rsync -a \
  --exclude='.git/' \
  --exclude='dist/' \
  --exclude='.venv/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  --exclude='node_modules/' \
  --exclude='.idea/' \
  "$SOURCE/" "$TARGET/"

# ---------------------------------------------------------------------------
# Phase 2 — Resolve language
# ---------------------------------------------------------------------------
if [[ "$LANG_CODE" != "en" ]]; then
  # Replace .md files with their language variant (.{lang}.md -> .md)
  find "$TARGET" -name "*.${LANG_CODE}.md" -type f | while IFS= read -r lang_file; do
    base_file="${lang_file%.${LANG_CODE}.md}.md"
    mv "$lang_file" "$base_file"
  done

  # Replace .yaml files with their language variant (.{lang}.yaml -> .yaml)
  find "$TARGET" -name "*.${LANG_CODE}.yaml" -type f | while IFS= read -r lang_file; do
    base_file="${lang_file%.${LANG_CODE}.yaml}.yaml"
    mv "$lang_file" "$base_file"
  done
fi

# ---------------------------------------------------------------------------
# Phase 3 — Remove residual language files (all *.XX.md / *.XX.yaml)
# ---------------------------------------------------------------------------
find "$TARGET" -type f \( -name '*.??.md' -o -name '*.??.yaml' \) -delete 2>/dev/null || true

echo "==> Tree resolved for language '$LANG_CODE' in $TARGET"
