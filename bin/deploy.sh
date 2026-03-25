#!/usr/bin/env bash
# deploy.sh — Stub: lista artefactos generados. Destino de deploy pendiente de definir.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
DIST_DIR="$REPO_ROOT/dist"
USERNAME="stratio"

echo "==> Deploy genai-agents v$VERSION"
echo ""

if [[ ! -d "$DIST_DIR" ]] || [[ -z "$(ls "$DIST_DIR"/*.zip 2>/dev/null)" ]]; then
  echo "ERROR: No hay artefactos en dist/. Ejecutar 'make package' primero." >&2
  exit 1
fi

echo "Artefactos disponibles para deploy:"
for zip in "$DIST_DIR"/*.zip; do
  SIZE=$(du -sh "$zip" | cut -f1)
  echo "  $(basename "$zip") ($SIZE)"
done

echo "Iniciando subida de artefactos a Nexus..."

NEXUS_BASE_URL="http://qa.int.stratio.com/repository"
# Repositorios raw según tipo de build
NEXUS_RAW_RELEASES="raw"
NEXUS_RAW_SNAPSHOTS="raw-snapshots"
NEXUS_RAW_STAGING="raw-staging"

# Por defecto: snapshot
NEXUS_REPO="$NEXUS_RAW_SNAPSHOTS"
# RELEASE / PRE_RELEASE / MILESTONE: JOB_NAME=Release/...
if [[ "${JOB_NAME:-}" == Release* ]]; then
  NEXUS_REPO="$NEXUS_RAW_RELEASES"
fi
# PR: JOB_NAME=.../PR-XX
if [[ "${JOB_NAME:-}" == *PR-* ]]; then
  NEXUS_REPO="$NEXUS_RAW_STAGING"
fi

echo "JOB_NAME = ${JOB_NAME:-<no definido>}"
echo "Repositorio Nexus seleccionado: $NEXUS_REPO"

NEXUS_URL="${NEXUS_BASE_URL}/${NEXUS_REPO}/genai-agents/${VERSION}"

for zip in "$DIST_DIR"/*.zip; do
  ZIP_NAME=$(basename "$zip")
  echo "Subiendo $ZIP_NAME a $NEXUS_URL..."

  curl --fail-with-body -u "${USERNAME}:${NEXUSPASS}" \
       --upload-file "$zip" \
       "${NEXUS_URL}/${ZIP_NAME}"
done

echo "Deploy finalizado correctamente."
