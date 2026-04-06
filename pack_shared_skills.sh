#!/usr/bin/env bash
# pack_shared_skills.sh — Packages the monorepo's shared skills into a self-contained ZIP
# Usage: bash pack_shared_skills.sh [--name <name>] [--skill <skill-name>] [--lang <code>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Phase 0 — Parsing and validation
# ---------------------------------------------------------------------------
PACK_NAME=""
SKILL_FILTER=""
LANG_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) PACK_NAME="$2"; shift 2 ;;
    --skill) SKILL_FILTER="$2"; shift 2 ;;
    --lang) LANG_CODE="$2"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; echo "Usage: bash pack_shared_skills.sh [--name <name>] [--skill <skill-name>] [--lang <code>]" >&2; exit 1 ;;
  esac
done

# Language resolution
_LANG_TMPDIR=""
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  _LANG_TMPDIR=$(mktemp -d "/tmp/pack-lang-${LANG_CODE}-XXXXXX")
  bash "$MONOREPO_ROOT/bin/resolve-lang.sh" --lang "$LANG_CODE" --source "$MONOREPO_ROOT" --target "$_LANG_TMPDIR"
  MONOREPO_ROOT="$_LANG_TMPDIR"
fi
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"' EXIT

if [[ -n "$SKILL_FILTER" ]]; then
  PACK_NAME="${PACK_NAME:-$SKILL_FILTER}"
else
  PACK_NAME="${PACK_NAME:-shared-skills}"
fi

if [[ ! -d "$MONOREPO_ROOT/shared-skills" ]]; then
  echo "ERROR: shared-skills/ directory not found in $MONOREPO_ROOT" >&2
  exit 1
fi

if [[ -n "$SKILL_FILTER" && ! -d "$MONOREPO_ROOT/shared-skills/$SKILL_FILTER" ]]; then
  echo "ERROR: skill '$SKILL_FILTER' not found in shared-skills/" >&2
  exit 1
fi

if [[ -n "$SKILL_FILTER" ]]; then
  echo "==> Packaging individual skill '$SKILL_FILTER' as '$PACK_NAME'"
else
  echo "==> Packaging shared skills as '$PACK_NAME'"
fi

# ---------------------------------------------------------------------------
# Phase 1 — Staging
# ---------------------------------------------------------------------------
STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT

# ---------------------------------------------------------------------------
# Phase 2 — Function to process a skill + iterate
# ---------------------------------------------------------------------------
N_SKILLS=0
N_GUIDES=0

_pack_one_skill() {
  local skill_dir="$1"
  local dest_dir="$2"

  # Copy skill content
  mkdir -p "$dest_dir"
  cp -r "$skill_dir"/. "$dest_dir/"

  # Read skill-guides manifest and copy guides to the skill root
  if [[ -f "$skill_dir/skill-guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$dest_dir/$guide"
        N_GUIDES=$((N_GUIDES + 1))
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$dest_dir/$guide"
        N_GUIDES=$((N_GUIDES + 1))
      else
        echo "    WARN: guide '$guide' not found in $guide_src — skipped" >&2
      fi
    done < "$skill_dir/skill-guides"
  fi

  # Remove skill-guides from output
  rm -f "$dest_dir/skill-guides"

  N_SKILLS=$((N_SKILLS + 1))
}

if [[ -n "$SKILL_FILTER" ]]; then
  # Individual mode: files directly at the staging root
  _pack_one_skill "$MONOREPO_ROOT/shared-skills/$SKILL_FILTER" "$STAGING"
else
  # Bulk mode: each skill in its own subfolder
  for skill_dir in "$MONOREPO_ROOT/shared-skills"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    _pack_one_skill "$skill_dir" "$STAGING/$skill_name"
  done
fi

echo "    $N_SKILLS skill(s), $N_GUIDES guide(s) copied"

# ---------------------------------------------------------------------------
# Phase 3 — Path substitutions in .md and .txt
# ---------------------------------------------------------------------------
find "$STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|skills-guides/||g' {} \;
find "$STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|shared-skill-guides/||g' {} \;
echo "    Path substitutions applied"

# ---------------------------------------------------------------------------
# Phase 4 — Generate ZIP
# ---------------------------------------------------------------------------
REAL_DIST="$SCRIPT_DIR/dist"
mkdir -p "$REAL_DIST"
ZIP_PATH="$REAL_DIST/${PACK_NAME}.zip"
rm -f "$ZIP_PATH"
(cd "$STAGING" && zip -r "$ZIP_PATH" . -q)
ZIP_SIZE=$(du -sh "$ZIP_PATH" | cut -f1)
echo "    ZIP generated: dist/${PACK_NAME}.zip ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Phase 5 — Verification
# ---------------------------------------------------------------------------
echo "    Verifying integrity..."
ERRORS=0

# No residual references to skills-guides/ or shared-skill-guides/
REFS=$(grep -rl 'skills-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null | wc -l) || true
if [[ "$REFS" -gt 0 ]]; then
  echo "    ERROR: $REFS file(s) still contain 'skills-guides/':" >&2
  grep -rl 'skills-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null >&2 || true
  ERRORS=$((ERRORS + 1))
fi

REFS2=$(grep -rl 'shared-skill-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null | wc -l) || true
if [[ "$REFS2" -gt 0 ]]; then
  echo "    ERROR: $REFS2 file(s) still contain 'shared-skill-guides/':" >&2
  grep -rl 'shared-skill-guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null >&2 || true
  ERRORS=$((ERRORS + 1))
fi

# Verify SKILL.md — in bulk mode, check subfolders; in individual mode, check root
if [[ -n "$SKILL_FILTER" ]]; then
  if [[ ! -f "$STAGING/SKILL.md" ]]; then
    echo "    ERROR: SKILL.md not found in the output" >&2
    ERRORS=$((ERRORS + 1))
  fi
else
  for skill_dir in "$STAGING"/*/; do
    [[ -d "$skill_dir" ]] || continue
    if [[ ! -f "$skill_dir/SKILL.md" ]]; then
      echo "    ERROR: $(basename "$skill_dir") does not have SKILL.md" >&2
      ERRORS=$((ERRORS + 1))
    fi
  done
fi

# No skill-guides file should remain
LEFTOVER=$(find "$STAGING" -name 'skill-guides' -type f 2>/dev/null | wc -l) || true
if [[ "$LEFTOVER" -gt 0 ]]; then
  echo "    ERROR: residual skill-guides file(s) in the output" >&2
  ERRORS=$((ERRORS + 1))
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FAILED: $ERRORS verification error(s)" >&2
  exit 1
fi

echo "==> OK — $N_SKILLS skill(s) packaged in dist/${PACK_NAME}.zip"
