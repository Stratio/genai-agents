#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(dirname "$SCRIPT_DIR")"
REAL_SCRIPT_DIR="$SCRIPT_DIR"

# --- Parse CLI arguments ---
ARG_NAME=""
LANG_CODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)  ARG_NAME="$2"; shift 2 ;;
    --lang)  LANG_CODE="$2"; shift 2 ;;
    *) echo "ERROR: Unknown argument: $1"; echo "Usage: $0 [--name NAME] [--lang CODE]"; exit 1 ;;
  esac
done

# --- Language resolution ---
_LANG_TMPDIR=""
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  _LANG_TMPDIR=$(mktemp -d "/tmp/pack-lang-${LANG_CODE}-XXXXXX")
  bash "$MONOREPO_ROOT/bin/resolve-lang.sh" --lang "$LANG_CODE" --source "$MONOREPO_ROOT" --target "$_LANG_TMPDIR"
  MONOREPO_ROOT="$_LANG_TMPDIR"
  SCRIPT_DIR="$_LANG_TMPDIR/$(basename "$SCRIPT_DIR")"
  cd "$SCRIPT_DIR"
else
  cd "$SCRIPT_DIR"
fi
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"' EXIT

# --- Name: CLI argument or default ---
PROJECT_NAME="${ARG_NAME:-semantic-layer}"

if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  PROJECT_DIR="$REAL_SCRIPT_DIR/dist/$LANG_CODE/claude_ai_projects/$PROJECT_NAME"
else
  PROJECT_DIR="dist/claude_ai_projects/$PROJECT_NAME"
fi

# --- Clean if exists ---
if [ -d "$PROJECT_DIR" ]; then
  echo "Deleting existing project in $PROJECT_DIR..."
  rm -rf "$PROJECT_DIR"
fi

mkdir -p "$PROJECT_DIR"

# --- 1. Root file ---
echo "Copying root files..."
cp AGENTS.md "$PROJECT_DIR/CLAUDE.md"

# --- 1b. User README ---
if [ -f "USER_README.md" ]; then
  cp USER_README.md "$PROJECT_DIR/README.md"
  echo "  README.md copied from USER_README.md"
fi

# --- 2. skills-guides/ → skills-guides_ prefix ---
echo "Copying skills-guides..."
# Read shared-guides from the agent to know which guides to include
if [ -f "shared-guides" ]; then
  while IFS= read -r guide || [ -n "$guide" ]; do
    [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
    guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
    if [ -d "$guide_src" ]; then
      # Flatten directory: each internal file becomes skills-guides_dir_file.md
      while IFS= read -r sub_file; do
        [ -f "$sub_file" ] || continue
        rel="${sub_file#$guide_src/}"
        flat_name="skills-guides_${guide}_$(echo "$rel" | tr '/' '_')"
        cp "$sub_file" "$PROJECT_DIR/$flat_name"
      done < <(find "$guide_src" -type f)
    elif [ -f "$guide_src" ]; then
      guide_flat="skills-guides_$(echo "$guide" | tr '/' '_')"
      cp "$guide_src" "$PROJECT_DIR/$guide_flat"
    else
      echo "WARN: shared guide '$guide' not found in $guide_src" >&2
    fi
  done < "shared-guides"
fi
# Copy remaining local guides (if any)
if [ -d "skills-guides" ]; then
  for entry in skills-guides/*; do
    [ -e "$entry" ] || continue
    base=$(basename "$entry")
    if [ -d "$entry" ]; then
      # Flatten local directory
      while IFS= read -r sub_file; do
        [ -f "$sub_file" ] || continue
        rel="${sub_file#$entry/}"
        flat_name="skills-guides_${base}_$(echo "$rel" | tr '/' '_')"
        [ -f "$PROJECT_DIR/$flat_name" ] && continue
        cp "$sub_file" "$PROJECT_DIR/$flat_name"
      done < <(find "$entry" -type f)
    elif [ -f "$entry" ]; then
      dst="$PROJECT_DIR/skills-guides_$base"
      [ -f "$dst" ] && continue
      cp "$entry" "$dst"
    fi
  done
fi

# --- 3. Skills ---
echo "Copying skills..."

# Resolve skills base directory (fallback across 4 locations)
SKILLS_SRC=""
if [ -d "skills" ]; then
  SKILLS_SRC="skills"
elif [ -d ".claude/skills" ]; then
  SKILLS_SRC=".claude/skills"
elif [ -d ".opencode/skills" ]; then
  SKILLS_SRC=".opencode/skills"
elif [ -d ".agents/skills" ]; then
  SKILLS_SRC=".agents/skills"
fi

# Copy local skills (format: <name>/SKILL.md → <name>.md)
if [ -n "$SKILLS_SRC" ]; then
  # Normalize: detect if there are loose .md files (flat format)
  SKILLS_NORM=""
  HAS_FLAT=$(find "$SKILLS_SRC" -maxdepth 1 -name '*.md' -not -name 'SKILL.md' 2>/dev/null | head -1)
  if [ -n "$HAS_FLAT" ]; then
    SKILLS_NORM=$(mktemp -d)
    cp -r "$SKILLS_SRC/." "$SKILLS_NORM/"
    for md_file in "$SKILLS_NORM"/*.md; do
      [ -f "$md_file" ] || continue
      skill_name="$(basename "$md_file" .md)"
      mkdir -p "$SKILLS_NORM/$skill_name"
      mv "$md_file" "$SKILLS_NORM/$skill_name/SKILL.md"
    done
    SKILLS_SRC="$SKILLS_NORM"
  fi

  for skill_dir in "$SKILLS_SRC"/*/; do
    skill_name=$(basename "$skill_dir")
    [ -f "$skill_dir/SKILL.md" ] || continue
    cp "$skill_dir/SKILL.md" "$PROJECT_DIR/${skill_name}.md"
  done

  # Clean up temporary directory if created
  if [ -n "$SKILLS_NORM" ]; then
    rm -rf "$SKILLS_NORM"
  fi
else
  echo "WARN: Skills directory not found"
fi

# Shared skills (from agent's shared-skills manifest)
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    # Local priority: if already exists in output, do not overwrite
    if [ -f "$PROJECT_DIR/${skill_name}.md" ]; then
      echo "  '$skill_name' skipped (local version takes priority)"
      continue
    fi
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name/SKILL.md"
    if [ -f "$skill_src" ]; then
      cp "$skill_src" "$PROJECT_DIR/${skill_name}.md"
    else
      echo "WARN: shared skill '$skill_name' not found in $skill_src" >&2
    fi
  done < "shared-skills"
fi

# --- 4. Reference replacements in all copied .md files ---
echo "Updating internal references..."

# Pattern A: skills-guides/ paths
sed -i 's|skills-guides/stratio-semantic-layer-tools\.md|skills-guides_stratio-semantic-layer-tools.md|g' "$PROJECT_DIR"/*.md

# Pattern B: AGENTS.md → CLAUDE.md (plain text references inside skills)
sed -i 's/AGENTS\.md/CLAUDE.md/g' "$PROJECT_DIR"/*.md

sed -i 's/{{TOOL_QUESTIONS}}/ (`AskUserQuestion`)/g' "$PROJECT_DIR"/*.md

# --- 5. Verification ---
echo ""
echo "=== Verification ==="

# Count files
FILE_COUNT=$(ls -1 "$PROJECT_DIR"/*.md 2>/dev/null | wc -l)
echo "  Files generated: $FILE_COUNT"

# Search for broken references (skills-guides/ paths that were not replaced)
BROKEN=$(grep -rn 'skills-guides/' "$PROJECT_DIR"/*.md 2>/dev/null || true)

if [ -n "$BROKEN" ]; then
  echo "  WARN: Possibly outdated references:"
  echo "$BROKEN" | head -20
else
  echo "  OK: No broken references found"
fi

echo ""
echo "=== Project packaged in $PROJECT_DIR ==="
