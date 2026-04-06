#!/usr/bin/env bash
# pack_stratio_cowork.sh — Generates a composite ZIP in agents/v1 format for Stratio Cowork:
#   metadata.yaml                   → bundle manifest (agents/v1)
#   {name}-opencode-agent.zip       → agent without the declared shared skills
#   {name}-shared-skills.zip        → agent's shared skills (self-contained, optional)
#   Result: dist/{name}-stratio-cowork.zip
#
# Usage: bash pack_stratio_cowork.sh --agent <path> [--name <kebab-name>] [--version <semver>] [--lang <code>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

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
# Phase 1 — Read shared skills manifest
# ---------------------------------------------------------------------------
SHARED_SKILLS=()

if [[ -f "$AGENT_ABS/shared-skills" ]]; then
  while IFS= read -r skill_name || [[ -n "$skill_name" ]]; do
    [[ -z "$skill_name" || "$skill_name" == \#* ]] && continue
    # Only include skills that actually exist in shared-skills/
    if [[ -d "$MONOREPO_ROOT/shared-skills/$skill_name" ]]; then
      SHARED_SKILLS+=("$skill_name")
    else
      echo "    WARN: shared skill '$skill_name' not found in shared-skills/ — skipped"
    fi
  done < "$AGENT_ABS/shared-skills"
fi

if [[ ${#SHARED_SKILLS[@]} -eq 0 ]]; then
  echo "    WARN: no shared skills declared for this agent"
fi

echo "    [1] ${#SHARED_SKILLS[@]} shared skill(s) detected: ${SHARED_SKILLS[*]:-none}"

# ---------------------------------------------------------------------------
# Phase 2 — Package full agent with pack_opencode.sh
# ---------------------------------------------------------------------------
echo "    [2] Running pack_opencode.sh..."
bash "$MONOREPO_ROOT/pack_opencode.sh" --agent "$AGENT_ABS" --name "$AGENT_NAME"

STAGING_FULL="$AGENT_ABS/dist/opencode/$AGENT_NAME"

if [[ ! -d "$STAGING_FULL" ]]; then
  echo "ERROR: pack_opencode.sh staging not found at $STAGING_FULL" >&2
  exit 1
fi
echo "    [2] Full staging ready at $STAGING_FULL"

# ---------------------------------------------------------------------------
# Phase 3 — Clone staging and remove shared skills from the clone
# ---------------------------------------------------------------------------
echo "    [3] Cloning staging for version without shared skills..."
STAGING_NO_SHARED=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED"' EXIT

cp -r "$STAGING_FULL/." "$STAGING_NO_SHARED/"

N_REMOVED=0
for skill_name in "${SHARED_SKILLS[@]}"; do
  skill_dst="$STAGING_NO_SHARED/.opencode/skills/$skill_name"
  if [[ -d "$skill_dst" ]]; then
    rm -rf "$skill_dst"
    N_REMOVED=$((N_REMOVED + 1))
    echo "    [3] Skill '$skill_name' removed from staging"
  else
    echo "    [3] WARN: '$skill_name' not found in staging (possibly overridden by local)"
  fi
done

# If skills-guides/ became empty after removing shared skills, clean it up
SKILLS_GUIDES_DIR="$STAGING_NO_SHARED/skills-guides"
if [[ -d "$SKILLS_GUIDES_DIR" ]]; then
  # Check if local skills use any guide from skills-guides/
  # Shared-skills guides are embedded within each skill folder,
  # not in skills-guides/ — but agent's shared-guides are copied there.
  # Therefore we leave skills-guides/ alone: it may contain agent-specific guides.
  echo "    [3] skills-guides/ preserved (may contain agent-specific guides)"
fi

echo "    [3] $N_REMOVED skill(s) removed from clone"

# ---------------------------------------------------------------------------
# Phase 4 — Sub-ZIP of agent without shared skills
# ---------------------------------------------------------------------------
BUNDLE_STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED" "$BUNDLE_STAGING"' EXIT

mkdir -p "$BUNDLE_STAGING"

ZIP_NO_SHARED="${AGENT_NAME}-opencode-agent.zip"
echo "    [4] Generating $ZIP_NO_SHARED..."
(cd "$STAGING_NO_SHARED" && zip -r "$BUNDLE_STAGING/$ZIP_NO_SHARED" . -q)
ZIP_SIZE=$(du -sh "$BUNDLE_STAGING/$ZIP_NO_SHARED" | cut -f1)
echo "    [4] $ZIP_NO_SHARED generated ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Phase 5 — Sub-ZIP of agent's shared skills
# ---------------------------------------------------------------------------
ZIP_SHARED="${AGENT_NAME}-shared-skills.zip"
echo "    [5] Generating $ZIP_SHARED..."

SKILLS_STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING_NO_SHARED" "$BUNDLE_STAGING" "$SKILLS_STAGING"' EXIT

N_SKILLS_PACKED=0
N_GUIDES_PACKED=0

for skill_name in "${SHARED_SKILLS[@]}"; do
  skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
  skill_dst="$SKILLS_STAGING/$skill_name"

  mkdir -p "$skill_dst"
  cp -r "$skill_src/." "$skill_dst/"

  # Embed guides declared in skill-guides
  if [[ -f "$skill_src/skill-guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$skill_dst/$guide"
        N_GUIDES_PACKED=$((N_GUIDES_PACKED + 1))
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$skill_dst/$guide"
        N_GUIDES_PACKED=$((N_GUIDES_PACKED + 1))
      else
        echo "    WARN: guide '$guide' not found — skipped"
      fi
    done < "$skill_src/skill-guides"
  fi

  # Remove the skill-guides manifest from output
  rm -f "$skill_dst/skill-guides"

  N_SKILLS_PACKED=$((N_SKILLS_PACKED + 1))
done

# Path substitutions
find "$SKILLS_STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|skills-guides/||g' {} \;
find "$SKILLS_STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|shared-skill-guides/||g' {} \;

if [[ $N_SKILLS_PACKED -gt 0 ]]; then
  (cd "$SKILLS_STAGING" && zip -r "$BUNDLE_STAGING/$ZIP_SHARED" . -q)
  ZIP_SIZE=$(du -sh "$BUNDLE_STAGING/$ZIP_SHARED" | cut -f1)
  echo "    [5] $ZIP_SHARED generated ($N_SKILLS_PACKED skill(s), $N_GUIDES_PACKED guide(s)) ($ZIP_SIZE)"
else
  echo "    [5] No shared skills — $ZIP_SHARED skipped"
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
  if [[ ${#SHARED_SKILLS[@]} -gt 0 ]]; then
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
(cd "$BUNDLE_STAGING" && zip -r "$BUNDLE_ZIP" . -q)
BUNDLE_SIZE=$(du -sh "$BUNDLE_ZIP" | cut -f1)
echo "    [6] Bundle generated: dist/${AGENT_NAME}-stratio-cowork.zip ($BUNDLE_SIZE)"

# ---------------------------------------------------------------------------
# Phase 7 — Integrity verification
# ---------------------------------------------------------------------------
echo "    [7] Verifying integrity..."
ERRORS=0

# The three required files must be in the bundle
BUNDLE_CONTENTS=$(unzip -Z1 "$BUNDLE_ZIP" 2>/dev/null) || true
if ! echo "$BUNDLE_CONTENTS" | grep -q "^metadata\.yaml$"; then
  echo "    ERROR: metadata.yaml not found in the bundle" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$BUNDLE_CONTENTS" | grep -q "$ZIP_NO_SHARED"; then
  echo "    ERROR: $ZIP_NO_SHARED not found in the bundle" >&2
  ERRORS=$((ERRORS + 1))
fi
if [[ ${#SHARED_SKILLS[@]} -gt 0 ]]; then
  if ! echo "$BUNDLE_CONTENTS" | grep -q "$ZIP_SHARED"; then
    echo "    ERROR: $ZIP_SHARED not found in the bundle" >&2
    ERRORS=$((ERRORS + 1))
  fi
fi

# metadata.yaml must declare format_version agents/v1
METADATA_CONTENT=$(unzip -p "$BUNDLE_ZIP" metadata.yaml 2>/dev/null) || true
if ! echo "$METADATA_CONTENT" | grep -q 'format_version:.*agents/v1'; then
  echo "    ERROR: metadata.yaml does not contain format_version: \"agents/v1\"" >&2
  ERRORS=$((ERRORS + 1))
fi
if ! echo "$METADATA_CONTENT" | grep -q "agent_zip:.*${ZIP_NO_SHARED}"; then
  echo "    ERROR: metadata.yaml does not correctly reference agent_zip ($ZIP_NO_SHARED)" >&2
  ERRORS=$((ERRORS + 1))
fi

# Agent sub-ZIP must contain AGENTS.md
AGENT_ZIP_CONTENTS=$(unzip -Z1 "$BUNDLE_STAGING/$ZIP_NO_SHARED" 2>/dev/null) || true
if ! echo "$AGENT_ZIP_CONTENTS" | grep -q 'AGENTS\.md'; then
  echo "    ERROR: AGENTS.md not found in $ZIP_NO_SHARED" >&2
  ERRORS=$((ERRORS + 1))
fi

# Agent sub-ZIP must NOT contain the removed shared skills
for skill_name in "${SHARED_SKILLS[@]}"; do
  if echo "$AGENT_ZIP_CONTENTS" | grep -q "\.opencode/skills/$skill_name/"; then
    echo "    ERROR: skill '$skill_name' still present in $ZIP_NO_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# Skills sub-ZIP must contain SKILL.md for each skill
for skill_name in "${SHARED_SKILLS[@]}"; do
  SKILLS_ZIP_CONTENTS=$(unzip -Z1 "$BUNDLE_STAGING/$ZIP_SHARED" 2>/dev/null) || true
  if ! echo "$SKILLS_ZIP_CONTENTS" | grep -q "${skill_name}/SKILL\.md"; then
    echo "    ERROR: ${skill_name}/SKILL.md not found in $ZIP_SHARED" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# No residual references to skill-guides in the skills ZIP
if [[ ${#SHARED_SKILLS[@]} -gt 0 ]]; then
  SKILLS_REFS=$(unzip -p "$BUNDLE_STAGING/$ZIP_SHARED" "*/SKILL.md" 2>/dev/null | grep -c 'skills-guides/' || true)
  if [[ "$SKILLS_REFS" -gt 0 ]]; then
    echo "    ERROR: residual references to skills-guides/ in $ZIP_SHARED" >&2
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
echo "      - $ZIP_NO_SHARED  (agent without shared skills)"
if [[ ${#SHARED_SKILLS[@]} -gt 0 ]]; then
  echo "      - $ZIP_SHARED  (${#SHARED_SKILLS[@]} shared skill(s))"
fi
