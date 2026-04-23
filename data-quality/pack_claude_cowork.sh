#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(dirname "$SCRIPT_DIR")"
REAL_SCRIPT_DIR="$SCRIPT_DIR"

# --- Parse CLI arguments ---
ARG_NAME="" ARG_GOV_URL="" ARG_GOV_KEY="" ARG_SQL_URL="" ARG_SQL_KEY="" LANG_CODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)    ARG_NAME="$2"; shift 2 ;;
    --gov-url) ARG_GOV_URL="$2"; shift 2 ;;
    --gov-key) ARG_GOV_KEY="$2"; shift 2 ;;
    --sql-url) ARG_SQL_URL="$2"; shift 2 ;;
    --sql-key) ARG_SQL_KEY="$2"; shift 2 ;;
    --lang)    LANG_CODE="$2"; shift 2 ;;
    *) echo "ERROR: Unknown argument: $1"; echo "Usage: $0 [--name NAME] [--gov-url URL] [--gov-key KEY] [--sql-url URL] [--sql-key KEY] [--lang CODE]"; exit 1 ;;
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
COWORK_NAME="${ARG_NAME:-data-quality}"

# Validate kebab-case
if ! echo "$COWORK_NAME" | grep -qE '^[a-z][a-z0-9]*(-[a-z0-9]+)*$'; then
  echo "ERROR: Name must be kebab-case (e.g.: my-agent, data-quality)."
  exit 1
fi

if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  COWORK_DIR="$REAL_SCRIPT_DIR/dist/$LANG_CODE/claude_cowork/$COWORK_NAME"
else
  COWORK_DIR="dist/claude_cowork/$COWORK_NAME"
fi

# --- Clean if exists ---
if [ -d "$COWORK_DIR" ]; then
  echo "Deleting existing cowork in $COWORK_DIR..."
  rm -rf "$COWORK_DIR"
fi

# ============================================================
# Step 1: Build inline plugin (skills + MCP, without agent)
# ============================================================
echo "Building inline plugin..."
PLUGIN_BUILD="$COWORK_DIR/_plugin_build"
mkdir -p "$PLUGIN_BUILD/.claude-plugin"
mkdir -p "$PLUGIN_BUILD/skills"

# --- plugin.json ---
cat > "$PLUGIN_BUILD/.claude-plugin/plugin.json" <<EOF
{
  "name": "$COWORK_NAME",
  "description": "Data Quality Agent",
  "version": "1.0.0"
}
EOF

# --- Copy local skills ---
echo "Copying skills..."
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

if [ -n "$SKILLS_SRC" ]; then
  cp -r "$SKILLS_SRC"/* "$PLUGIN_BUILD/skills/"
  # Normalize: loose .md files → subfolder/SKILL.md
  for md_file in "$PLUGIN_BUILD/skills/"*.md; do
    [ -f "$md_file" ] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$PLUGIN_BUILD/skills/$skill_name"
    mv "$md_file" "$PLUGIN_BUILD/skills/$skill_name/SKILL.md"
  done
  echo "  Skills copied from $SKILLS_SRC"
else
  echo "WARN: Skills directory not found — the plugin will have no skills."
fi

# --- Copy shared skills (if declared by the agent) ---
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    skill_dst="$PLUGIN_BUILD/skills/$skill_name"
    if [ ! -d "$skill_src" ]; then
      echo "  WARN: shared skill '$skill_name' not found in $skill_src — skipped" >&2
      continue
    fi
    # Local priority
    if [ -d "$skill_dst" ]; then
      echo "  '$skill_name' skipped (local version takes priority)"
      continue
    fi
    cp -r "$skill_src" "$skill_dst"
    echo "  Shared skill '$skill_name' included"
  done < "shared-skills"
fi

# --- Copy skills-guides inside each skill that declares them ---
# Self-contained: iterates over ALL skills in the plugin (both local and
# shared) and uses each skill's own `skill-guides` manifest to copy the
# declared guides alongside SKILL.md. Then rewrites `skills-guides/X.md`
# references to `X.md` so they resolve locally to the skill folder, and
# removes the manifest from the output.
for skill_dir in "$PLUGIN_BUILD/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  [ -f "$skill_dir/skill-guides" ] || continue
  while IFS= read -r guide || [ -n "$guide" ]; do
    [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
    guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
    if [ -d "$guide_src" ]; then
      cp -r "$guide_src" "$skill_dir/$guide"
    elif [ -f "$guide_src" ]; then
      cp "$guide_src" "$skill_dir/$guide"
    fi
  done < "$skill_dir/skill-guides"
  find "$skill_dir" -type f -name '*.md' -exec sed -i 's|skills-guides/||g' {} \;
  rm -f "$skill_dir/skill-guides"
done

# --- Placeholder substitution ---
sed -i 's/{{TOOL_QUESTIONS}}/ (`AskUserQuestion`)/g' "$PLUGIN_BUILD/skills/"*/SKILL.md 2>/dev/null || true

# --- Plugin .mcp.json (2 servers: gov + sql) ---
GOV_URL_VALUE="${ARG_GOV_URL:-\$\{MCP_GOV_URL:-http://127.0.0.1:8080/mcp\}}"
GOV_KEY_VALUE="${ARG_GOV_KEY:-\$\{MCP_GOV_API_KEY:-\}}"
SQL_URL_VALUE="${ARG_SQL_URL:-\$\{MCP_SQL_URL:-http://127.0.0.1:8080/mcp\}}"
SQL_KEY_VALUE="${ARG_SQL_KEY:-\$\{MCP_SQL_API_KEY:-\}}"

if [ -n "$ARG_GOV_URL" ] || [ -n "$ARG_GOV_KEY" ] || [ -n "$ARG_SQL_URL" ] || [ -n "$ARG_SQL_KEY" ]; then
  cat > "$PLUGIN_BUILD/.mcp.json" <<EOF
{
  "mcpServers": {
    "stratio_gov": {
      "type": "http",
      "url": "$GOV_URL_VALUE",
      "headers": {
        "X-API-Key": "$GOV_KEY_VALUE",
        "Authorization": "Bearer $GOV_KEY_VALUE"
      },
      "allowedTools": ["*"]
    },
    "stratio_data": {
      "type": "http",
      "url": "$SQL_URL_VALUE",
      "headers": {
        "X-API-Key": "$SQL_KEY_VALUE",
        "Authorization": "Bearer $SQL_KEY_VALUE"
      },
      "allowedTools": ["*"]
    }
  }
}
EOF
else
  cat > "$PLUGIN_BUILD/.mcp.json" <<'EOF'
{
  "mcpServers": {
    "stratio_gov": {
      "type": "http",
      "url": "${MCP_GOV_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_GOV_API_KEY:-}",
        "Authorization": "Bearer ${MCP_GOV_API_KEY:-}"
      },
      "allowedTools": ["*"]
    },
    "stratio_data": {
      "type": "http",
      "url": "${MCP_SQL_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_SQL_API_KEY:-}",
        "Authorization": "Bearer ${MCP_SQL_API_KEY:-}"
      },
      "allowedTools": ["*"]
    }
  }
}
EOF
fi

# --- Non-runtime sweep before zipping ---
bash "$MONOREPO_ROOT/bin/sweep-nonruntime.sh" "$PLUGIN_BUILD"

# --- Generate plugin ZIP ---
PLUGIN_ZIP_NAME="${COWORK_NAME}.zip"
echo "Generating plugin ZIP..."
(cd "$PLUGIN_BUILD" && zip -r "../${PLUGIN_ZIP_NAME}" . -q)

# ============================================================
# Step 2: Generate CLAUDE.md from AGENTS.md
# ============================================================
echo "Generating CLAUDE.md from AGENTS.md..."
sed 's|`skills-guides/stratio-data-tools\.md`|`skills/assess-quality/stratio-data-tools.md`|g' AGENTS.md > "$COWORK_DIR/CLAUDE.md"
sed -i 's|`skills-guides/quality-exploration\.md`|`skills/assess-quality/quality-exploration.md`|g' "$COWORK_DIR/CLAUDE.md"
sed -i 's/{{TOOL_QUESTIONS}}/ (`AskUserQuestion`)/g' "$COWORK_DIR/CLAUDE.md"

# --- User README ---
if [ -f "USER_README.md" ]; then
  cp USER_README.md "$COWORK_DIR/README.md"
  echo "  README.md copied from USER_README.md"
fi

# Write .agent_lang marker next to CLAUDE.md so Python tools (if the user
# runs them from the folder) pick the packaging language as default.
echo "${LANG_CODE:-en}" > "$COWORK_DIR/.agent_lang"

# ============================================================
# Step 3: Clean up temporary build
# ============================================================
rm -rf "$PLUGIN_BUILD"

# --- Summary ---
PLUGIN_SIZE=$(du -sh "$COWORK_DIR/${COWORK_NAME}.zip" | cut -f1)
echo ""
echo "=== Cowork packaged ==="
echo "  CLAUDE.md:   $COWORK_DIR/CLAUDE.md (folder instructions, generated from AGENTS.md)"
echo "  Plugin ZIP:  $COWORK_DIR/${COWORK_NAME}.zip ($PLUGIN_SIZE) (skills + MCP, without agent)"
echo ""
