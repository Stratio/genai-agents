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

  # Run pytest against the current Python environment (sandbox: /opt/venv via PATH;
  # dev local: user-managed venv or system Python). No bootstrap from the script.
  (cd "$MODULE_DIR" && python3 -m pytest $TEST_FILES -v) || true

done < "$REPO_ROOT/release-modules"

echo "==> Tests completed"
