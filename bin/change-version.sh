#!/usr/bin/env bash
# change-version.sh — Updates the project version
set -euo pipefail

NEW_VERSION="${1:?Usage: $0 <new-version>}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "$NEW_VERSION" > "$REPO_ROOT/VERSION"
echo "Version updated to: $NEW_VERSION"

# Normalize version for artifact naming (strip build qualifiers for Nexus)
# RELEASE: VERSION = 0.1.0-BUILD => VERSION_ARTIFACT = 0.1.0
# All other types (SNAPSHOT, MILESTONE, PR, pre-release) keep the suffix as-is
VERSION_ARTIFACT="$NEW_VERSION"
if [[ "$VERSION_ARTIFACT" == *-BUILD* ]]; then
    VERSION_ARTIFACT="$(echo "$VERSION_ARTIFACT" | cut -d'-' -f1)"
fi

echo "$VERSION_ARTIFACT" > "$REPO_ROOT/VERSION_ARTIFACT"
echo "Artifact version: $VERSION_ARTIFACT"
