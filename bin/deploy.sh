#!/usr/bin/env bash
# deploy.sh — Stub: lists generated artifacts. Deploy destination pending definition.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
DIST_DIR="$REPO_ROOT/dist"
USERNAME="stratio"

echo "==> Deploy genai-agents v$VERSION"
echo ""

if [[ ! -d "$DIST_DIR" ]] || [[ -z "$(ls "$DIST_DIR"/*.zip 2>/dev/null)" ]]; then
  echo "ERROR: No artifacts in dist/. Run 'make package' first." >&2
  exit 1
fi

echo "Artifacts available for deploy:"
for zip in "$DIST_DIR"/*.zip; do
  SIZE=$(du -sh "$zip" | cut -f1)
  echo "  $(basename "$zip") ($SIZE)"
done

echo "Starting artifact upload to Nexus..."

NEXUS_BASE_URL="http://qa.int.stratio.com/repository"
# Raw repositories by build type
NEXUS_RAW_RELEASES="raw"
NEXUS_RAW_SNAPSHOTS="raw-snapshots"
NEXUS_RAW_STAGING="raw-staging"

# Default: snapshot
NEXUS_REPO="$NEXUS_RAW_SNAPSHOTS"
# RELEASE / PRE_RELEASE / MILESTONE: JOB_NAME=Release/...
if [[ "${JOB_NAME:-}" == Release* ]]; then
  NEXUS_REPO="$NEXUS_RAW_RELEASES"
fi
# PR: JOB_NAME=.../PR-XX
if [[ "${JOB_NAME:-}" == *PR-* ]]; then
  NEXUS_REPO="$NEXUS_RAW_STAGING"
fi

echo "JOB_NAME = ${JOB_NAME:-<not defined>}"
echo "Selected Nexus repository: $NEXUS_REPO"

NEXUS_URL="${NEXUS_BASE_URL}/${NEXUS_REPO}/genai-agents/${VERSION}"

for zip in "$DIST_DIR"/*.zip; do
  ZIP_NAME=$(basename "$zip")
  echo "Uploading $ZIP_NAME to $NEXUS_URL..."

  curl --fail-with-body -u "${USERNAME}:${NEXUSPASS}" \
       --upload-file "$zip" \
       "${NEXUS_URL}/${ZIP_NAME}"
done

echo "Deploy completed successfully."
