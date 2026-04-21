#!/usr/bin/env bash
# sweep-nonruntime.sh — remove test files, caches and other non-runtime
# artifacts from a packaging staging directory. Called by every pack script
# after the initial copy so the final zip only contains files that matter
# at runtime.
#
# Usage: bash bin/sweep-nonruntime.sh <staging-dir>

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "usage: $0 <staging-dir>" >&2
    exit 2
fi

TARGET="$1"

if [ ! -d "$TARGET" ]; then
    echo "sweep-nonruntime: directory not found: $TARGET" >&2
    exit 1
fi

# Files (by name, anywhere in the tree)
find "$TARGET" \
    \( -type f \
       \( -name 'test_*.py' \
       -o -name '*_test.py' \
       -o -name 'conftest.py' \
       -o -name '*.pyc' \
       -o -name '*.pyo' \
       -o -name '.DS_Store' \
       -o -name 'Thumbs.db' \
       -o -name '*.bak' \
       -o -name '*~' \
       -o -name '*.swp' \
       -o -name '.coverage' \
       -o -name '.coverage.*' \
       \) \
    \) -delete 2>/dev/null || true

# Directories (by name, recursively)
find "$TARGET" \
    \( -type d \
       \( -name '__pycache__' \
       -o -name '.pytest_cache' \
       -o -name '.tox' \
       -o -name '.mypy_cache' \
       -o -name '.ruff_cache' \
       -o -name 'htmlcov' \
       -o -name '.idea' \
       -o -name '.vscode' \
       -o -name 'node_modules' \
       -o -name '_tmp' \
       -o -name '.tmp' \
       -o -name '*.egg-info' \
       \) \
    \) -prune -exec rm -rf {} + 2>/dev/null || true
