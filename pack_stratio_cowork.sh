#!/usr/bin/env bash
# pack_stratio_cowork.sh — Generates a composite ZIP in agents/v1 format for Stratio Cowork:
#   metadata.yaml                   → bundle manifest (agents/v1)
#   {name}-opencode-agent.zip       → agent without the declared imported skills
#   {name}-skills.zip               → agent's imported skills (self-contained, optional)
#   Result: dist/{name}-stratio-cowork.zip
#
# Usage: bash pack_stratio_cowork.sh --agent <path> [--name <kebab-name>] [--version <semver>] [--lang <code>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"
SOURCE_DATE_EPOCH=$(git -C "$SCRIPT_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
export SOURCE_DATE_EPOCH

# ---------------------------------------------------------------------------
# Phase 0 — Parsing and validation
# ---------------------------------------------------------------------------
AGENT_PATH=""
AGENT_NAME=""
AGENT_VERSION=""
LANG_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)   AGENT_PATH="$2";   shift 2 ;;
    --name)    AGENT_NAME="$2";   shift 2 ;;
    --version) AGENT_VERSION="$2"; shift 2 ;;
    --lang)    LANG_CODE="$2";    shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2
       echo "Usage: bash pack_stratio_cowork.sh --agent <path> [--name <kebab-name>] [--version <semver>] [--lang <code>]" >&2
       exit 1 ;;
  esac
done

if [[ -z "$AGENT_PATH" ]]; then
  echo "ERROR: --agent is required" >&2
  echo "Usage: bash pack_stratio_cowork.sh --agent <path> [--name <kebab-name>] [--version <semver>] [--lang <code>]" >&2
  exit 1
fi

# Resolve absolute path
if [[ -d "$SCRIPT_DIR/$AGENT_PATH" ]]; then
  AGENT_ABS="$(cd "$SCRIPT_DIR/$AGENT_PATH" && pwd)"
elif [[ -d "$AGENT_PATH" ]]; then
  AGENT_ABS="$(cd "$AGENT_PATH" && pwd)"
else
  echo "ERROR: agent directory not found: $AGENT_PATH" >&2
  exit 1
fi

# Default name: basename of the directory
if [[ -z "$AGENT_NAME" ]]; then
  AGENT_NAME="$(basename "$AGENT_ABS")"
fi

# Validate kebab-case format
KEBAB_RE='^[a-z][a-z0-9]*(-[a-z0-9]+)*$'
if [[ ! "$AGENT_NAME" =~ $KEBAB_RE ]]; then
  echo "ERROR: name '$AGENT_NAME' is not valid kebab-case (e.g.: my-agent, data-analytics)" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Language resolution
# ---------------------------------------------------------------------------
REAL_AGENT_ABS="$AGENT_ABS"
_LANG_TMPDIR=""
LANG_ARGS=()
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  _LANG_TMPDIR=$(mktemp -d "/tmp/pack-lang-${LANG_CODE}-XXXXXX")
  bash "$MONOREPO_ROOT/bin/resolve-lang.sh" --lang "$LANG_CODE" --source "$MONOREPO_ROOT" --target "$_LANG_TMPDIR"
  MONOREPO_ROOT="$_LANG_TMPDIR"
  AGENT_ABS="$_LANG_TMPDIR/$(basename "$REAL_AGENT_ABS")"
  LANG_ARGS=(--lang "$LANG_CODE")
fi
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"' EXIT

echo "==> Generating Stratio Cowork bundle (agents/v1) for '$AGENT_NAME'${LANG_CODE:+ ($LANG_CODE)}"
echo "    Source : $AGENT_ABS"

# ---------------------------------------------------------------------------
# Phase 1 — Read imported skills manifest
# ---------------------------------------------------------------------------
IMPORTED_SKILLS=()

if [[ -f "$AGENT_ABS/imported-skills" ]]; then
  while IFS= read -r skill_name || [[ -n "$skill_name" ]]; do
    [[ -z "$skill_name" || "$skill_name" == \#* ]] && continue
    # Only include skills that actually exist in skills/
    if [[ -d "$MONOREPO_ROOT/skills/$skill_name" ]]; then
      IMPORTED_SKILLS+=("$skill_name")
    else
      echo "    WARN: imported skill '$skill_name' not found in skills/ — skipped"
    fi
  done < "$AGENT_ABS/imported-skills"
fi

if [[ ${#IMPORTED_SKILLS[@]} -eq 0 ]]; then
  echo "    WARN: no imported skills declared for this agent"
fi

echo "    [1] ${#IMPORTED_SKILLS[@]} imported skill(s) detected: ${IMPORTED_SKILLS[*]:-none}"

# ---------------------------------------------------------------------------
# Phase 2 — Package full agent with pack_opencode.sh
# ---------------------------------------------------------------------------
echo "    [2] Running pack_opencode.sh..."
# Note: we invoke pack_opencode.sh WITHOUT --lang because this script has
# already resolved the overlay into a tmpdir (lines 68-74). pack_opencode.sh
# operates on that already-translated tree, so passing --lang would trigger
# a redundant second resolve. However, pack_opencode.sh will then write
# `.agent_lang=en` to the staging output; we overwrite it below with the
# real LANG_CODE so the packaged tools pick up the correct default language.
bash "$MONOREPO_ROOT/pack_opencode.sh" --agent "$AGENT_ABS" --name "$AGENT_NAME"

STAGING_FULL="$AGENT_ABS/dist/opencode/$AGENT_NAME"

if [[ ! -d "$STAGING_FULL" ]]; then
  echo "ERROR: pack_opencode.sh staging not found at $STAGING_FULL" >&2
  exit 1
fi

# Overwrite .agent_lang so the packaged tools see the real language this
# stratio-cowork bundle was built for (pack_opencode.sh wrote "en" because
# it didn't receive --lang — see note above).
echo "${LANG_CODE:-en}" > "$STAGING_FULL/.agent_lang"

echo "    [2] Full staging ready at $STAGING_FULL"

# ---------------------------------------------------------------------------
# Phase 3 — Clone staging and remove imported skills from the clone
# ---------------------------------------------------------------------------
echo "    [3] Cloning staging for version without imported skills..."
STAGING_NO_SHARED=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED"' EXIT

cp -r "$STAGING_FULL/." "$STAGING_NO_SHARED/"

N_REMOVED=0
for skill_name in "${IMPORTED_SKILLS[@]}"; do
  skill_dst="$STAGING_NO_SHARED/.opencode/skills/$skill_name"
  if [[ -d "$skill_dst" ]]; then
    rm -rf "$skill_dst"
    N_REMOVED=$((N_REMOVED + 1))
    echo "    [3] Skill '$skill_name' removed from staging"
  else
    echo "    [3] WARN: '$skill_name' not found in staging (possibly overridden by local)"
  fi
done

# If guides/ became empty after removing imported skills, clean it up
GUIDES_DIR="$STAGING_NO_SHARED/guides"
if [[ -d "$GUIDES_DIR" ]]; then
  # Check if local skills use any guide from guides/
  # Imported-skill guides are embedded within each skill folder,
  # not in guides/ — but agent's shared-guides are copied there.
  # Therefore we leave guides/ alone: it may contain agent-specific guides.
  echo "    [3] guides/ preserved (may contain agent-specific guides)"
fi

echo "    [3] $N_REMOVED skill(s) removed from clone"

# Remove root-level files that should not travel in the Cowork bundle:
# - requirements.txt: the sandbox image provides the Python stack
# - setup_env.sh: the sandbox does not invoke it; defensive in case it ever reappears
find "$STAGING_NO_SHARED" -maxdepth 1 \( -name 'requirements.txt' -o -name 'setup_env.sh' \) -delete

# ---------------------------------------------------------------------------
# Phase 4 — Sub-ZIP of agent without imported skills
# ---------------------------------------------------------------------------
BUNDLE_STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED" "$BUNDLE_STAGING"' EXIT

mkdir -p "$BUNDLE_STAGING"

ZIP_NO_SHARED="${AGENT_NAME}-opencode-agent.zip"
echo "    [4] Generating $ZIP_NO_SHARED..."
bash "$SCRIPT_DIR/bin/sweep-nonruntime.sh" "$STAGING_NO_SHARED"
bash "$SCRIPT_DIR/bin/zip-deterministic.sh" "$STAGING_NO_SHARED" "$BUNDLE_STAGING/$ZIP_NO_SHARED"
ZIP_SIZE=$(du -sh "$BUNDLE_STAGING/$ZIP_NO_SHARED" | cut -f1)
echo "    [4] $ZIP_NO_SHARED generated ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Phase 5 — Sub-ZIP of agent's imported skills
# ---------------------------------------------------------------------------
ZIP_SHARED="${AGENT_NAME}-skills.zip"
echo "    [5] Generating $ZIP_SHARED..."

SKILLS_STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED" "$BUNDLE_STAGING" "$SKILLS_STAGING"' EXIT

N_SKILLS_PACKED=0
N_GUIDES_PACKED=0

for skill_name in "${IMPORTED_SKILLS[@]}"; do
  skill_src="$MONOREPO_ROOT/skills/$skill_name"
  skill_dst="$SKILLS_STAGING/$skill_name"

  mkdir -p "$skill_dst"
  cp -r "$skill_src/." "$skill_dst/"

  # Embed guides declared in the skill's `guides` manifest
  if [[ -f "$skill_src/guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      guide_src="$MONOREPO_ROOT/guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$skill_dst/$guide"
        N_GUIDES_PACKED=$((N_GUIDES_PACKED + 1))
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$skill_dst/$guide"
        N_GUIDES_PACKED=$((N_GUIDES_PACKED + 1))
      else
        echo "    WARN: guide '$guide' not found — skipped"
      fi
    done < "$skill_src/guides"
  fi

  # Remove the `guides` manifest from output
  rm -f "$skill_dst/guides"

  N_SKILLS_PACKED=$((N_SKILLS_PACKED + 1))
done

# Path substitutions
find "$SKILLS_STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|guides/||g' {} \;

if [[ $N_SKILLS_PACKED -gt 0 ]]; then
  bash "$SCRIPT_DIR/bin/sweep-nonruntime.sh" "$SKILLS_STAGING"
  bash "$SCRIPT_DIR/bin/zip-deterministic.sh" "$SKILLS_STAGING" "$BUNDLE_STAGING/$ZIP_SHARED"
  ZIP_SIZE=$(du -sh "$BUNDLE_STAGING/$ZIP_SHARED" | cut -f1)
  echo "    [5] $ZIP_SHARED generated ($N_SKILLS_PACKED skill(s), $N_GUIDES_PACKED guide(s)) ($ZIP_SIZE)"
else
  echo "    [5] No imported skills — $ZIP_SHARED skipped"
fi

# ---------------------------------------------------------------------------
# Phase 5.5 — Generate metadata.yaml (agents/v1 manifest)
# ---------------------------------------------------------------------------
echo "    [5.5] Generating metadata.yaml..."

METADATA_FILE="$BUNDLE_STAGING/metadata.yaml"

{
  echo 'format_version: "agents/v1"'
  echo "name: \"${AGENT_NAME}\""
  echo "agent_zip: \"${ZIP_NO_SHARED}\""
  if [[ ${#IMPORTED_SKILLS[@]} -gt 0 ]]; then
    echo "skills_zip: \"${ZIP_SHARED}\""
  fi
  if [[ -n "$AGENT_VERSION" ]]; then
    echo "external_version: \"${AGENT_VERSION}\""
  fi
  if [[ -f "$AGENT_ABS/mcps" ]]; then
    echo "mcps:"
    while IFS= read -r mcp_name || [[ -n "$mcp_name" ]]; do
      [[ -z "$mcp_name" || "$mcp_name" == \#* ]] && continue
      echo "  - name: \"${mcp_name}\""
    done < "$AGENT_ABS/mcps"
  fi
} > "$METADATA_FILE"

# Inject additional agent metadata (if exists)
COWORK_META_FILE="$AGENT_ABS/cowork-metadata.yaml"
if [[ -f "$COWORK_META_FILE" ]]; then
  cat "$COWORK_META_FILE" >> "$METADATA_FILE"
  echo "    [5.5] Metadata from cowork-metadata.yaml injected"
else
  echo "    [5.5] WARN: cowork-metadata.yaml not found — no additional metadata"
fi

echo "    [5.5] metadata.yaml generated"

# ---------------------------------------------------------------------------
# Phase 6 — Container ZIP
# ---------------------------------------------------------------------------
REAL_DIST="$SCRIPT_DIR/dist"
mkdir -p "$REAL_DIST"
BUNDLE_ZIP="$REAL_DIST/${AGENT_NAME}-stratio-cowork.zip"
rm -f "$BUNDLE_ZIP"
bash "$SCRIPT_DIR/bin/zip-deterministic.sh" "$BUNDLE_STAGING" "$BUNDLE_ZIP"
BUNDLE_SIZE=$(du -sh "$BUNDLE_ZIP" | cut -f1)
echo "    [6] Bundle generated: dist/${AGENT_NAME}-stratio-cowork.zip ($BUNDLE_SIZE)"

# ---------------------------------------------------------------------------
# Phase 7 — Integrity verification
# ---------------------------------------------------------------------------
echo "    [7] Verifying integrity..."
ERRORS=0

# The three required files must be in the bundle
BUNDLE_CONTENTS=""
if ! BUNDLE_CONTENTS=$(unzip -Z1 "$BUNDLE_ZIP" 2>/dev/null); then
  echo "    ERROR: cannot list bundle ZIP '$BUNDLE_ZIP'" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$BUNDLE_CONTENTS" | grep -q "^metadata\.yaml$"; then
  echo "    ERROR: metadata.yaml not found in the bundle" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$BUNDLE_CONTENTS" | grep -q "$ZIP_NO_SHARED"; then
  echo "    ERROR: $ZIP_NO_SHARED not found in the bundle" >&2
  ERRORS=$((ERRORS + 1))
fi
if [[ ${#IMPORTED_SKILLS[@]} -gt 0 ]]; then
  if ! echo "$BUNDLE_CONTENTS" | grep -q "$ZIP_SHARED"; then
    echo "    ERROR: $ZIP_SHARED not found in the bundle" >&2
    ERRORS=$((ERRORS + 1))
  fi
fi

# metadata.yaml must declare format_version agents/v1
METADATA_CONTENT=""
if ! METADATA_CONTENT=$(unzip -p "$BUNDLE_ZIP" metadata.yaml 2>/dev/null); then
  echo "    ERROR: cannot extract metadata.yaml from bundle ZIP" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$METADATA_CONTENT" | grep -q 'format_version:.*agents/v1'; then
  echo "    ERROR: metadata.yaml does not contain format_version: \"agents/v1\"" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$METADATA_CONTENT" | grep -q "agent_zip:.*${ZIP_NO_SHARED}"; then
  echo "    ERROR: metadata.yaml does not correctly reference agent_zip ($ZIP_NO_SHARED)" >&2
  ERRORS=$((ERRORS + 1))
fi

# Agent sub-ZIP must contain AGENTS.md
AGENT_ZIP_CONTENTS=""
if ! AGENT_ZIP_CONTENTS=$(unzip -Z1 "$BUNDLE_STAGING/$ZIP_NO_SHARED" 2>/dev/null); then
  echo "    ERROR: cannot list agent sub-ZIP '$ZIP_NO_SHARED'" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$AGENT_ZIP_CONTENTS" | grep -q 'AGENTS\.md'; then
  echo "    ERROR: AGENTS.md not found in $ZIP_NO_SHARED" >&2
  ERRORS=$((ERRORS + 1))
fi

# Agent sub-ZIP must NOT contain the removed imported skills
for skill_name in "${IMPORTED_SKILLS[@]}"; do
  if echo "$AGENT_ZIP_CONTENTS" | grep -q "\.opencode/skills/$skill_name/"; then
    echo "    ERROR: skill '$skill_name' still present in $ZIP_NO_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# Skills sub-ZIP must contain SKILL.md for each skill
SKILLS_ZIP_CONTENTS=""
if [[ ${#IMPORTED_SKILLS[@]} -gt 0 ]]; then
  if ! SKILLS_ZIP_CONTENTS=$(unzip -Z1 "$BUNDLE_STAGING/$ZIP_SHARED" 2>/dev/null); then
    echo "    ERROR: cannot list skills sub-ZIP '$ZIP_SHARED'" >&2
    ERRORS=$((ERRORS + 1))
  fi
fi
for skill_name in "${IMPORTED_SKILLS[@]}"; do
  if ! echo "$SKILLS_ZIP_CONTENTS" | grep -q "${skill_name}/SKILL\.md"; then
    echo "    ERROR: ${skill_name}/SKILL.md not found in $ZIP_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# No residual references to guides/ in the skills ZIP
if [[ ${#IMPORTED_SKILLS[@]} -gt 0 ]]; then
  _skills_md_content=""
  if ! _skills_md_content=$(unzip -p "$BUNDLE_STAGING/$ZIP_SHARED" "*/SKILL.md" 2>/dev/null); then
    echo "    ERROR: cannot extract SKILL.md files from skills sub-ZIP '$ZIP_SHARED'" >&2
    ERRORS=$((ERRORS + 1))
  fi
  SKILLS_REFS=$(echo "$_skills_md_content" | grep -c 'guides/' || true)
  if [[ "$SKILLS_REFS" -gt 0 ]]; then
    echo "    ERROR: residual references to guides/ in $ZIP_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FAILED: $ERRORS verification error(s)" >&2
  exit 1
fi

echo "==> OK — dist/${AGENT_NAME}-stratio-cowork.zip"
echo "    Contains:"
echo "      - metadata.yaml  (agents/v1 manifest)"
echo "      - $ZIP_NO_SHARED  (agent without imported skills)"
if [[ ${#IMPORTED_SKILLS[@]} -gt 0 ]]; then
  echo "      - $ZIP_SHARED  (${#IMPORTED_SKILLS[@]} imported skill(s))"
fi
