#!/usr/bin/env bash
# pack_sandbox_mandatory_skills.sh — Packages the sandbox mandatory skills into one ZIP
#
# Sandbox mandatory skills are the skills every Stratio sandbox carries, whatever the
# project, agentless ones included. They are never uploaded to GenAI UI nor imported by
# an agent: genai-agents-sandbox downloads this ZIP at build time and unpacks it onto
# OpenCode's skills path. The ZIP holds one folder per skill at its root.
#
# Each skill is packed like a shared skill (pack_skills.sh): the guides its `guides`
# manifest names are copied in from guides/ and `guides/` references are made local.
# On top of that, the files its `bundle-assets` manifest names are copied in from
# anywhere in the monorepo, so the packed skill is self-contained.
#
# Usage: bash pack_sandbox_mandatory_skills.sh [--skill <name>] [--output-dir <dir>]
#   Output: <output-dir>/sandbox-mandatory-skills.zip (default <output-dir>: dist/)
#
# English only: the sandbox image is one build for every user, and the agent answers
# in the user's language whatever the language of the skill.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"
SKILLS_SRC="$MONOREPO_ROOT/sandbox-mandatory-skills"
SKILL_FILTER=""
OUTPUT_DIR="$MONOREPO_ROOT/dist"

SOURCE_DATE_EPOCH=$(git -C "$SCRIPT_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
export SOURCE_DATE_EPOCH

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill) SKILL_FILTER="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2
       echo "Usage: bash pack_sandbox_mandatory_skills.sh [--skill <name>] [--output-dir <dir>]" >&2
       exit 1 ;;
  esac
done

die() { echo "ERROR: $*" >&2; exit 1; }

[[ -d "$SKILLS_SRC" ]] || die "no sandbox-mandatory-skills/ directory in $MONOREPO_ROOT"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
ZIP_PATH="$OUTPUT_DIR/sandbox-mandatory-skills.zip"

STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT

# The frontmatter must name the directory: OpenCode finds a skill by its folder, and a
# name that disagrees is a skill that silently never loads.
check_frontmatter() {
  local skill_md="$1" name="$2" frontmatter
  [[ "$(head -n 1 "$skill_md")" == "---" ]] || die "$skill_md does not start with a --- frontmatter"
  frontmatter="$(awk 'NR==1{next} /^---$/{exit} {print}' "$skill_md")"
  grep -qx "name: $name" <<<"$frontmatter" || die "$skill_md: frontmatter 'name:' is not '$name'"
  grep -q "^description: ." <<<"$frontmatter" || die "$skill_md: frontmatter has no description"
}

copy_guides() {
  local manifest="$1" dest="$2" skill="$3" guide
  while IFS= read -r guide || [[ -n "$guide" ]]; do
    [[ -z "$guide" || "$guide" == \#* ]] && continue
    [[ -e "$MONOREPO_ROOT/guides/$guide" ]] || die "$skill/guides: guides/$guide does not exist"
    cp -r "$MONOREPO_ROOT/guides/$guide" "$dest/$guide"
    echo "    + guides/$guide"
  done < "$manifest"
}

copy_bundle_assets() {
  local manifest="$1" dest_root="$2" skill="$3" src dest extra
  while read -r src dest extra || [[ -n "${src:-}" ]]; do
    [[ -z "${src:-}" || "$src" == \#* ]] && continue
    [[ -n "${dest:-}" && -z "${extra:-}" ]] || die "$skill/bundle-assets: expected '<source> <destination>', got '$src ${dest:-} ${extra:-}'"
    [[ "$src" != /* && "$src" != *..* ]] || die "$skill/bundle-assets: source must be inside the monorepo: $src"
    [[ "$dest" != /* && "$dest" != *..* ]] || die "$skill/bundle-assets: destination must be inside the skill: $dest"
    [[ -e "$MONOREPO_ROOT/$src" ]] || die "$skill/bundle-assets: $src does not exist"
    [[ ! -e "$dest_root/$dest" ]] || die "$skill/bundle-assets: $dest would overwrite a file of the skill itself"
    # Only the skill's own SKILL.md may be named SKILL.md: OpenCode would load any other
    # as a skill of its own.
    [[ "$(basename "$dest")" != "SKILL.md" ]] || die "$skill/bundle-assets: $dest cannot be named SKILL.md"
    mkdir -p "$(dirname "$dest_root/$dest")"
    cp -R "$MONOREPO_ROOT/$src" "$dest_root/$dest"
    echo "    + $src -> $dest"
  done < "$manifest"
}

echo "==> Packaging sandbox mandatory skills..."
PACKED=0
for skill_dir in "$SKILLS_SRC"/*/; do
  [[ -d "$skill_dir" ]] || continue
  name="$(basename "$skill_dir")"
  [[ -n "$SKILL_FILTER" && "$name" != "$SKILL_FILTER" ]] && continue
  [[ -f "$skill_dir/SKILL.md" ]] || die "sandbox-mandatory-skills/$name has no SKILL.md"
  check_frontmatter "$skill_dir/SKILL.md" "$name"

  echo "  [$name]"
  dest="$STAGING/$name"
  mkdir -p "$dest"
  cp -r "$skill_dir"/. "$dest/"
  rm -f "$dest/guides" "$dest/bundle-assets"
  [[ -f "$skill_dir/guides" ]] && copy_guides "$skill_dir/guides" "$dest" "$name"
  [[ -f "$skill_dir/bundle-assets" ]] && copy_bundle_assets "$skill_dir/bundle-assets" "$dest" "$name"
  PACKED=$((PACKED + 1))
done
[[ "$PACKED" -gt 0 ]] || die "no sandbox mandatory skill matched${SKILL_FILTER:+ '$SKILL_FILTER'}"

# Guides now sit at the skill root: make `guides/<file>` references local, as pack_skills.sh does.
find "$STAGING" -type f \( -name '*.md' -o -name '*.txt' \) -exec sed -i 's|guides/||g' {} \;
bash "$SCRIPT_DIR/bin/sweep-nonruntime.sh" "$STAGING"
find "$STAGING" -mindepth 1 -type d -empty -delete

# --- Verification ---
ERRORS=0
if grep -rlq 'guides/' "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null; then
  echo "ERROR: files still reference guides/:" >&2
  grep -rl 'guides/' "$STAGING" --include='*.md' --include='*.txt' >&2
  ERRORS=$((ERRORS + 1))
fi
for skill in "$STAGING"/*/; do
  if [[ "$(find "$skill" -name SKILL.md | wc -l)" -ne 1 ]]; then
    echo "ERROR: $(basename "$skill") must hold exactly one SKILL.md, at its root" >&2
    ERRORS=$((ERRORS + 1))
  fi
done
[[ "$ERRORS" -eq 0 ]] || die "$ERRORS verification error(s)"

rm -f "$ZIP_PATH"
bash "$SCRIPT_DIR/bin/zip-deterministic.sh" "$STAGING" "$ZIP_PATH"
echo "==> OK — $PACKED sandbox mandatory skill(s) -> $ZIP_PATH ($(du -sh "$ZIP_PATH" | cut -f1))"
