#!/usr/bin/env bash
# zip-reproducible.sh — Reproducible zip: fixed timestamps, sorted entries, no extra Unix attrs.
# Usage: bash bin/zip-reproducible.sh <src-dir> <out.zip>
# Env:   SOURCE_DATE_EPOCH — Unix timestamp to stamp all entries (default: last git commit)
set -euo pipefail

SRC_DIR="$1"
OUT_ZIP="$2"

if [[ -z "${SOURCE_DATE_EPOCH:-}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  SOURCE_DATE_EPOCH=$(git -C "$SCRIPT_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
fi

# Normalize all mtimes to SOURCE_DATE_EPOCH so repeated runs produce identical bytes
find "$SRC_DIR" -exec touch -d "@${SOURCE_DATE_EPOCH}" {} +

# Zip with deterministic entry order (-@ reads from stdin) and no extra Unix attrs (-X)
(cd "$SRC_DIR" && find . | LC_ALL=C sort | zip -X -@ -q "$OUT_ZIP")
