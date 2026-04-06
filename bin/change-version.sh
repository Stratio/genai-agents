#!/usr/bin/env bash
# change-version.sh — Updates the project version
set -euo pipefail

NEW_VERSION="${1:?Usage: $0 <new-version>}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "$NEW_VERSION" > "$REPO_ROOT/VERSION"
echo "Version updated to: $NEW_VERSION"
