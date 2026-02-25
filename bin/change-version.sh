#!/usr/bin/env bash
# change-version.sh — Actualiza la version del proyecto
set -euo pipefail

NEW_VERSION="${1:?Uso: $0 <nueva-version>}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "$NEW_VERSION" > "$REPO_ROOT/VERSION"
echo "Version actualizada a: $NEW_VERSION"
