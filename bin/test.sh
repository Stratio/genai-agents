#!/usr/bin/env bash
# test.sh — Runs pytest tests in each agent from release-modules
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Searching for tests in agents..."

while IFS= read -r module; do
  [[ -z "$module" || "$module" =~ ^# ]] && continue
  MODULE_DIR="$REPO_ROOT/$module"

  if [[ ! -d "$MODULE_DIR" ]]; then
    echo "  WARN: Module '$module' does not exist, skipping"
    continue
  fi

  # Search for test files
  TEST_FILES=$(find "$MODULE_DIR" -name 'test_*.py' -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/output/*' 2>/dev/null || true)

  if [[ -z "$TEST_FILES" ]]; then
    echo "  [$module] No tests — skipping"
    continue
  fi

  echo "  [$module] Tests found — running pytest..."

  # Activate venv if setup_env.sh exists
  if [[ -f "$MODULE_DIR/setup_env.sh" ]]; then
    echo "  [$module] Setting up environment with setup_env.sh..."
    (cd "$MODULE_DIR" && bash setup_env.sh)
    if [[ -f "$MODULE_DIR/.venv/bin/activate" ]]; then
      (cd "$MODULE_DIR" && source .venv/bin/activate && python -m pytest $TEST_FILES -v)
    else
      echo "  [$module] WARN: setup_env.sh did not create .venv — running global pytest"
      (cd "$MODULE_DIR" && python -m pytest $TEST_FILES -v) || true
    fi
  else
    echo "  [$module] No setup_env.sh — running global pytest"
    (cd "$MODULE_DIR" && python -m pytest $TEST_FILES -v) || true
  fi

done < "$REPO_ROOT/release-modules"

echo "==> Tests completed"
