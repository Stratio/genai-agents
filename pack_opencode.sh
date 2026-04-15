#!/usr/bin/env bash
# pack_opencode.sh — Packages a monorepo agent for OpenCode
# Usage: bash pack_opencode.sh --agent <path> [--name <kebab-name>] [--lang <code>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Phase 0 — Parsing and validation
# ---------------------------------------------------------------------------
AGENT_PATH=""
AGENT_NAME=""
LANG_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_PATH="$2"; shift 2 ;;
    --name)  AGENT_NAME="$2"; shift 2 ;;
    --lang)  LANG_CODE="$2";  shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$AGENT_PATH" ]]; then
  echo "ERROR: --agent is required" >&2
  echo "Usage: bash pack_opencode.sh --agent <path> [--name <kebab-name>] [--lang <code>]" >&2
  exit 1
fi

# Resolve absolute path: first relative to SCRIPT_DIR, then as absolute
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
# Language resolution: if --lang is set and != en, resolve content via overlay
# ---------------------------------------------------------------------------
REAL_AGENT_ABS="$AGENT_ABS"
_LANG_TMPDIR=""
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  _LANG_TMPDIR=$(mktemp -d "/tmp/pack-lang-${LANG_CODE}-XXXXXX")
  bash "$MONOREPO_ROOT/bin/resolve-lang.sh" --lang "$LANG_CODE" --source "$MONOREPO_ROOT" --target "$_LANG_TMPDIR"
  MONOREPO_ROOT="$_LANG_TMPDIR"
  AGENT_ABS="$_LANG_TMPDIR/$(basename "$REAL_AGENT_ABS")"
fi
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"' EXIT

# Output goes to the REAL agent dist, with language subdirectory if applicable
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  OUTPUT_DIR="$REAL_AGENT_ABS/dist/$LANG_CODE/opencode/$AGENT_NAME"
else
  OUTPUT_DIR="$REAL_AGENT_ABS/dist/opencode/$AGENT_NAME"
fi

echo "==> Packaging '$AGENT_NAME' for OpenCode${LANG_CODE:+ ($LANG_CODE)}"
echo "    Source : $AGENT_ABS"
echo "    Target : $OUTPUT_DIR"

# ---------------------------------------------------------------------------
# Phase 1 — Output preparation
# ---------------------------------------------------------------------------
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/.opencode/skills"

# ---------------------------------------------------------------------------
# Phase 2 — AGENTS.md
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/AGENTS.md" ]]; then
  cp "$AGENT_ABS/AGENTS.md" "$OUTPUT_DIR/AGENTS.md"
  echo "    [2] AGENTS.md copied from AGENTS.md"
elif [[ -f "$AGENT_ABS/CLAUDE.md" ]]; then
  cp "$AGENT_ABS/CLAUDE.md" "$OUTPUT_DIR/AGENTS.md"
  echo "    [2] AGENTS.md copied from CLAUDE.md"
else
  echo "ERROR: neither AGENTS.md nor CLAUDE.md found in $AGENT_ABS" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Phase 3 — opencode.json
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/opencode.json" ]]; then
  cp "$AGENT_ABS/opencode.json" "$OUTPUT_DIR/opencode.json"
  # Update instructions reference: CLAUDE.md -> AGENTS.md
  sed -i 's/"CLAUDE\.md"/"AGENTS.md"/g' "$OUTPUT_DIR/opencode.json"
  echo "    [3] opencode.json copied (real) and updated"
else
  cat > "$OUTPUT_DIR/opencode.json" << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"],
  "mcp": {
    "stratio_data": {
      "type": "remote",
      "url": "{env:MCP_SQL_URL}",
      "timeout": 90000,
      "headers": {
        "Authorization": "Bearer {env:MCP_SQL_API_KEY}",
        "X-API-Key": "{env:MCP_SQL_API_KEY}"
      }
    }
  },
  "permission": {
    "read": "allow", "glob": "allow", "grep": "allow", "list": "allow",
    "lsp": "allow", "edit": "allow", "write": "allow",
    "todoread": "allow", "todowrite": "allow", "task": "allow",
    "skill": "allow", "webfetch": "allow",
    "stratio_data_*": "allow",
    "bash": { "*": "allow" }
  }
}
EOF
  echo "    [3] opencode.json generated (template)"
fi

# ---------------------------------------------------------------------------
# Phase 4 — .opencode/ (openwork.json is NOT copied — contains absolute paths)
# ---------------------------------------------------------------------------
# The .opencode/skills directory was already created in Phase 1.
# openwork.json is intentionally excluded.
echo "    [4] .opencode/ prepared (openwork.json excluded)"

# ---------------------------------------------------------------------------
# Phase 5 — Skills (optional)
# ---------------------------------------------------------------------------
SKILLS_SRC=""
if [[ -d "$AGENT_ABS/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/skills"
elif [[ -d "$AGENT_ABS/.opencode/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.opencode/skills"
elif [[ -d "$AGENT_ABS/.claude/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.claude/skills"
elif [[ -d "$AGENT_ABS/.agents/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.agents/skills"
fi

if [[ -n "$SKILLS_SRC" ]]; then
  cp -r "$SKILLS_SRC/." "$OUTPUT_DIR/.opencode/skills/"
  # Normalize: loose .md files -> subfolder/SKILL.md
  for md_file in "$OUTPUT_DIR/.opencode/skills/"*.md; do
    [[ -f "$md_file" ]] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$OUTPUT_DIR/.opencode/skills/$skill_name"
    mv "$md_file" "$OUTPUT_DIR/.opencode/skills/$skill_name/SKILL.md"
  done
  N_SKILLS=$(find "$OUTPUT_DIR/.opencode/skills" -type f | wc -l)
  echo "    [5] $N_SKILLS skill(s) copied from $SKILLS_SRC"
else
  echo "    [5] No skills (continuing without error)"
fi

# ---------------------------------------------------------------------------
# Phase 5.1 — Shared skills (optional)
# ---------------------------------------------------------------------------
SHARED_GUIDES_NEEDED=()

if [[ -f "$AGENT_ABS/shared-skills" ]]; then
  N_SHARED=0
  while IFS= read -r skill_name || [[ -n "$skill_name" ]]; do
    [[ -z "$skill_name" || "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    skill_dst="$OUTPUT_DIR/.opencode/skills/$skill_name"
    if [[ ! -d "$skill_src" ]]; then
      echo "    WARN: shared skill '$skill_name' not found in $skill_src — skipped" >&2
      continue
    fi
    if [[ -d "$skill_dst" ]]; then
      echo "    [5.1] '$skill_name' skipped (local version takes priority)"
      continue
    fi
    cp -r "$skill_src" "$skill_dst"
    rm -f "$skill_dst/skill-guides"
    # Copy guides declared WITHIN the skill (self-contained)
    if [[ -f "$skill_src/skill-guides" ]]; then
      while IFS= read -r guide || [[ -n "$guide" ]]; do
        [[ -z "$guide" || "$guide" == \#* ]] && continue
        guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
        if [[ -d "$guide_src" ]]; then
          cp -r "$guide_src" "$skill_dst/$guide"
        elif [[ -f "$guide_src" ]]; then
          cp "$guide_src" "$skill_dst/$guide"
        else
          echo "    WARN: shared guide '$guide' not found — skipped" >&2
        fi
      done < "$skill_src/skill-guides"
      # Update references in the skill to make them local
      find "$skill_dst" -type f -name '*.md' -exec sed -i 's|skills-guides/||g' {} \;
    fi
    N_SHARED=$((N_SHARED + 1))
    if [[ -f "$skill_src/skill-guides" ]]; then
      while IFS= read -r guide || [[ -n "$guide" ]]; do
        [[ -z "$guide" || "$guide" == \#* ]] && continue
        SHARED_GUIDES_NEEDED+=("$guide")
      done < "$skill_src/skill-guides"
    fi
  done < "$AGENT_ABS/shared-skills"
  echo "    [5.1] $N_SHARED shared skill(s) included"
else
  echo "    [5.1] No shared-skills declared (continuing without error)"
fi

if [[ -f "$AGENT_ABS/shared-guides" ]]; then
  while IFS= read -r guide || [[ -n "$guide" ]]; do
    [[ -z "$guide" || "$guide" == \#* ]] && continue
    SHARED_GUIDES_NEEDED+=("$guide")
  done < "$AGENT_ABS/shared-guides"
fi

if [[ ${#SHARED_GUIDES_NEEDED[@]} -gt 0 ]]; then
  mkdir -p "$OUTPUT_DIR/skills-guides"
  declare -A _GUIDES_SEEN=()
  N_GUIDES=0
  for guide in "${SHARED_GUIDES_NEEDED[@]}"; do
    [[ -n "${_GUIDES_SEEN[$guide]:-}" ]] && continue
    _GUIDES_SEEN[$guide]=1
    guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
    if [[ -d "$guide_src" ]]; then
      cp -r "$guide_src" "$OUTPUT_DIR/skills-guides/$guide"
    elif [[ -f "$guide_src" ]]; then
      cp "$guide_src" "$OUTPUT_DIR/skills-guides/$guide"
    else
      echo "    WARN: shared guide '$guide' not found in $guide_src — skipped" >&2
      continue
    fi
    N_GUIDES=$((N_GUIDES + 1))
  done
  echo "    [5.1] $N_GUIDES shared guide(s) copied to skills-guides/"
fi

# ---------------------------------------------------------------------------
# Phase 6 — rsync remaining files
# ---------------------------------------------------------------------------
# Memory templates live under templates/memory/ and are copied as-is via rsync
# (alongside templates/pdf/ and others). The agent skills initialize output/
# from these templates on first write.
rsync -a \
  --exclude=README.md \
  --exclude=USER_README.md \
  --exclude=mcps \
  --exclude=CLAUDE.md \
  --exclude=AGENTS.md \
  --exclude=.mcp.json \
  --exclude=.claude/ \
  --exclude=.opencode/ \
  --exclude=.agents/ \
  --exclude=opencode.json \
  --exclude=cowork-metadata.yaml \
  --exclude=skills/ \
  --exclude=shared-skills \
  --exclude=shared-guides \
  --exclude='pack_*.sh' \
  --exclude=output/ \
  --exclude=dist/ \
  --exclude=.venv/ \
  --exclude='__pycache__/' \
  --exclude='.pytest_cache/' \
  --exclude='*.pyc' \
  --exclude=.idea/ \
  --exclude=node_modules/ \
  --exclude='es/' \
  "$AGENT_ABS/" "$OUTPUT_DIR/"
echo "    [6] rsync completed"

# ---------------------------------------------------------------------------
# Phase 6.1 — User README
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/USER_README.md" ]]; then
  cp "$AGENT_ABS/USER_README.md" "$OUTPUT_DIR/README.md"
  echo "    [6.1] README.md copied from USER_README.md"
fi

# ---------------------------------------------------------------------------
# Phase 7 — Text replacements (CLAUDE.md -> AGENTS.md)
# Only .md, .sh, .py, .txt — NOT .json (opencode.json was already handled)
# ---------------------------------------------------------------------------
find "$OUTPUT_DIR" \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' \
  -type f \( -name '*.md' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' \) \
  -exec sed -i 's/CLAUDE\.md/AGENTS.md/g' {} \;
echo "    [7] Replacements CLAUDE.md -> AGENTS.md applied"

# Replace question tool placeholder with the OpenCode tool
find "$OUTPUT_DIR" \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' \
  -type f \( -name '*.md' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' \) \
  -exec sed -i 's/{{TOOL_QUESTIONS}}/ (`question`)/g' {} \;
echo "    [7b] Placeholder TOOL_QUESTIONS -> question"

# ---------------------------------------------------------------------------
# Phase 8 — Integrity verification
# ---------------------------------------------------------------------------
echo "    [8] Verifying integrity..."
ERRORS=0

# AGENTS.md exists and is not empty
if [[ ! -s "$OUTPUT_DIR/AGENTS.md" ]]; then
  echo "    ERROR: AGENTS.md does not exist or is empty" >&2
  ERRORS=$((ERRORS + 1))
fi

# Validate JSON with python3 if available
_validate_json() {
  local file="$1"
  if command -v python3 &>/dev/null; then
    if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
      echo "    ERROR: invalid JSON: $file" >&2
      ERRORS=$((ERRORS + 1))
    fi
  fi
}
_validate_json "$OUTPUT_DIR/opencode.json"

# opencode.json contains "AGENTS.md"
if ! grep -q '"AGENTS\.md"' "$OUTPUT_DIR/opencode.json" 2>/dev/null; then
  echo "    ERROR: opencode.json does not contain reference to AGENTS.md" >&2
  ERRORS=$((ERRORS + 1))
fi

# 0 .json files with reference to "CLAUDE.md" in instructions key
if grep -rl '"CLAUDE\.md"' "$OUTPUT_DIR" --include='*.json' 2>/dev/null | grep -q .; then
  echo "    ERROR: .json files still contain reference to \"CLAUDE.md\":" >&2
  grep -rl '"CLAUDE\.md"' "$OUTPUT_DIR" --include='*.json' 2>/dev/null >&2
  ERRORS=$((ERRORS + 1))
fi

# No forbidden directories
for FORBIDDEN in .claude; do
  if [[ -d "$OUTPUT_DIR/$FORBIDDEN" ]]; then
    echo "    ERROR: forbidden directory found: $FORBIDDEN" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# Verify that skills-guides referenced from AGENTS.md exist
if [[ -f "$OUTPUT_DIR/AGENTS.md" ]]; then
  while IFS= read -r ref; do
    if [[ ! -f "$OUTPUT_DIR/$ref" ]]; then
      echo "    ERROR: broken reference in AGENTS.md: $ref" >&2
      ERRORS=$((ERRORS + 1))
    fi
  done < <(grep -oP 'skills-guides/[a-zA-Z0-9_.-]+\.md' "$OUTPUT_DIR/AGENTS.md" | sort -u)
fi

# mcps file must not be present
if [[ -f "$OUTPUT_DIR/mcps" ]]; then
  echo "    ERROR: mcps file must not be present in the OpenCode output" >&2
  ERRORS=$((ERRORS + 1))
fi

# .mcp.json must not be present
if [[ -f "$OUTPUT_DIR/.mcp.json" ]]; then
  echo "    ERROR: .mcp.json must not be present in the OpenCode output" >&2
  ERRORS=$((ERRORS + 1))
fi

# [Final step] Write .agent_lang marker so Python tools can pick up the
# default language when the agent invokes them without passing --lang.
# Falls back to "en" when no --lang was supplied at packaging time.
echo "${LANG_CODE:-en}" > "$OUTPUT_DIR/.agent_lang"

# Total files
TOTAL=$(find "$OUTPUT_DIR" -type f | wc -l)

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FAILED: $ERRORS verification error(s)" >&2
  exit 1
fi

echo "==> OK — $TOTAL file(s) generated in $OUTPUT_DIR"
