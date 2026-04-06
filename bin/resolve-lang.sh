#!/usr/bin/env bash
# resolve-lang.sh — Creates a temporary repo tree in the specified language
#
# For --lang en: copies the repo without language overlay directories
# For --lang es: copies the repo, then overlays es/ on top (replacing English with Spanish)
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
# Phase 1 — Copy repo (excluding language overlay directories and artifacts)
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
  --exclude='es/' \
  "$SOURCE/" "$TARGET/"

# ---------------------------------------------------------------------------
# Phase 2 — Overlay language directory (for non-English languages)
# ---------------------------------------------------------------------------
if [[ "$LANG_CODE" != "en" ]]; then
  LANG_DIR="$SOURCE/$LANG_CODE"
  if [[ -d "$LANG_DIR" ]]; then
    rsync -a "$LANG_DIR/" "$TARGET/"
  else
    echo "WARN: language directory '$LANG_DIR' not found — using English content" >&2
  fi
fi

echo "==> Tree resolved for language '$LANG_CODE' in $TARGET"
