#!/usr/bin/env bash
# deploy.sh — Stub: lista artefactos generados. Destino de deploy pendiente de definir.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
DIST_DIR="$REPO_ROOT/dist"

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

echo ""
echo "NOTA: Destino de deploy pendiente de definir. Este script es un stub."
