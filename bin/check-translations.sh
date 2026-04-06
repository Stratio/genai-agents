#!/usr/bin/env bash
# check-translations.sh — Verifies that all translatable files have
# their variant in each language declared in the 'languages' file.
#
# Translatable files: AGENTS.md, SKILL.md, USER_README.md, README.md (agents),
#   cowork-metadata.yaml, *.md in skills/*/ and skills-guides/, shared-skill-guides/,
#   output-templates/
#
# Usage: bin/check-translations.sh [--lang <code>]
#   Without --lang: verifies all secondary languages from the 'languages' file
#   With --lang: verifies only that language
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK_LANG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lang) CHECK_LANG="$2"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 1 ;;
  esac
done

# Read languages from the languages file (excluding 'en' which is the primary)
LANGUAGES_FILE="$REPO_ROOT/languages"
if [[ ! -f "$LANGUAGES_FILE" ]]; then
  echo "ERROR: 'languages' file not found in $REPO_ROOT" >&2
  exit 1
fi

SECONDARY_LANGS=()
while IFS= read -r lang || [[ -n "$lang" ]]; do
  lang=$(echo "$lang" | tr -d '[:space:]')
  [[ -z "$lang" || "$lang" == "#"* || "$lang" == "en" ]] && continue
  if [[ -n "$CHECK_LANG" && "$lang" != "$CHECK_LANG" ]]; then
    continue
  fi
  SECONDARY_LANGS+=("$lang")
done < "$LANGUAGES_FILE"

if [[ ${#SECONDARY_LANGS[@]} -eq 0 ]]; then
  echo "No secondary languages to verify."
  exit 0
fi

# ---------------------------------------------------------------------------
# Collect translatable files (primary, without language suffix)
# ---------------------------------------------------------------------------
TRANSLATABLE=()

# Root AGENTS.md and README.md are development docs, NOT translatable.
# Only agent-level files are translatable.

# release-modules defines the agents
MODULES_FILE="$REPO_ROOT/release-modules"
if [[ -f "$MODULES_FILE" ]]; then
  while IFS= read -r module || [[ -n "$module" ]]; do
    [[ -z "$module" || "$module" == "#"* ]] && continue
    MODULE_DIR="$REPO_ROOT/$module"
    [[ ! -d "$MODULE_DIR" ]] && continue

    # Agent-level files
    for f in AGENTS.md USER_README.md README.md; do
      [[ -f "$MODULE_DIR/$f" ]] && TRANSLATABLE+=("$MODULE_DIR/$f")
    done

    # cowork-metadata.yaml
    [[ -f "$MODULE_DIR/cowork-metadata.yaml" ]] && TRANSLATABLE+=("$MODULE_DIR/cowork-metadata.yaml")

    # Local skills: SKILL.md and sub-guides *.md
    if [[ -d "$MODULE_DIR/skills" ]]; then
      while IFS= read -r md_file; do
        # Exclude files already with language suffix
        base=$(basename "$md_file")
        [[ "$base" == *.??.md ]] && continue
        TRANSLATABLE+=("$md_file")
      done < <(find "$MODULE_DIR/skills" -type f -name '*.md' 2>/dev/null)
    fi

    # Local skills-guides
    if [[ -d "$MODULE_DIR/skills-guides" ]]; then
      while IFS= read -r md_file; do
        base=$(basename "$md_file")
        [[ "$base" == *.??.md ]] && continue
        TRANSLATABLE+=("$md_file")
      done < <(find "$MODULE_DIR/skills-guides" -type f -name '*.md' 2>/dev/null)
    fi

    # output-templates
    if [[ -d "$MODULE_DIR/output-templates" ]]; then
      while IFS= read -r md_file; do
        base=$(basename "$md_file")
        [[ "$base" == *.??.md ]] && continue
        TRANSLATABLE+=("$md_file")
      done < <(find "$MODULE_DIR/output-templates" -type f -name '*.md' 2>/dev/null)
    fi
  done < "$MODULES_FILE"
fi

# Shared skills
if [[ -d "$REPO_ROOT/shared-skills" ]]; then
  for skill_dir in "$REPO_ROOT/shared-skills"/*/; do
    [[ ! -d "$skill_dir" ]] && continue
    while IFS= read -r md_file; do
      base=$(basename "$md_file")
      [[ "$base" == *.??.md ]] && continue
      TRANSLATABLE+=("$md_file")
    done < <(find "$skill_dir" -type f -name '*.md' 2>/dev/null)
  done
fi

# Shared skill guides
if [[ -d "$REPO_ROOT/shared-skill-guides" ]]; then
  while IFS= read -r md_file; do
    base=$(basename "$md_file")
    [[ "$base" == *.??.md ]] && continue
    TRANSLATABLE+=("$md_file")
  done < <(find "$REPO_ROOT/shared-skill-guides" -type f -name '*.md' 2>/dev/null)
fi

# ---------------------------------------------------------------------------
# Verify translations
# ---------------------------------------------------------------------------
MISSING=0
TOTAL=${#TRANSLATABLE[@]}

for lang in "${SECONDARY_LANGS[@]}"; do
  echo "==> Verifying translations for language: $lang"
  LANG_MISSING=0

  for file in "${TRANSLATABLE[@]}"; do
    dir=$(dirname "$file")
    base=$(basename "$file")
    ext="${base##*.}"
    stem="${base%.*}"
    lang_file="$dir/${stem}.${lang}.${ext}"

    if [[ ! -f "$lang_file" ]]; then
      rel_path="${file#$REPO_ROOT/}"
      echo "  MISSING: ${stem}.${lang}.${ext}  (for $rel_path)"
      LANG_MISSING=$((LANG_MISSING + 1))
    fi
  done

  if [[ $LANG_MISSING -eq 0 ]]; then
    echo "  OK: all translations present ($TOTAL files)"
  else
    echo "  MISSING: $LANG_MISSING of $TOTAL translations"
  fi
  MISSING=$((MISSING + LANG_MISSING))
done

echo ""
if [[ $MISSING -gt 0 ]]; then
  echo "=== RESULT: $MISSING missing translation(s) ==="
  exit 1
else
  echo "=== RESULT: all translations complete ==="
  exit 0
fi
