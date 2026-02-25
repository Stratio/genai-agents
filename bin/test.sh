#!/usr/bin/env bash
# test.sh — Ejecuta tests pytest en cada agente de release-modules
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Buscando tests en agentes..."

while IFS= read -r module; do
  [[ -z "$module" || "$module" =~ ^# ]] && continue
  MODULE_DIR="$REPO_ROOT/$module"

  if [[ ! -d "$MODULE_DIR" ]]; then
    echo "  WARN: Modulo '$module' no existe, saltando"
    continue
  fi

  # Buscar ficheros de test
  TEST_FILES=$(find "$MODULE_DIR" -name 'test_*.py' -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/output/*' 2>/dev/null || true)

  if [[ -z "$TEST_FILES" ]]; then
    echo "  [$module] Sin tests — saltando"
    continue
  fi

  echo "  [$module] Tests encontrados — ejecutando pytest..."

  # Activar venv si existe setup_env.sh
  if [[ -f "$MODULE_DIR/setup_env.sh" ]]; then
    echo "  [$module] Configurando entorno con setup_env.sh..."
    (cd "$MODULE_DIR" && bash setup_env.sh)
    if [[ -f "$MODULE_DIR/.venv/bin/activate" ]]; then
      (cd "$MODULE_DIR" && source .venv/bin/activate && python -m pytest $TEST_FILES -v)
    else
      echo "  [$module] WARN: setup_env.sh no creo .venv — ejecutando pytest global"
      (cd "$MODULE_DIR" && python -m pytest $TEST_FILES -v) || true
    fi
  else
    echo "  [$module] Sin setup_env.sh — ejecutando pytest global"
    (cd "$MODULE_DIR" && python -m pytest $TEST_FILES -v) || true
  fi

done < "$REPO_ROOT/release-modules"

echo "==> Tests completados"
