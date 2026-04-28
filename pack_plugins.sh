#!/usr/bin/env bash
# pack_plugins.sh — Packages the plugin marketplace into a self-contained ZIP
# Usage: bash pack_plugins.sh [--name <name>] [--plugin <plugin-name>] [--lang <code>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Phase 0 — Parsing and validation
# ---------------------------------------------------------------------------
PACK_NAME=""
PLUGIN_FILTER=""
LANG_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)   PACK_NAME="$2";     shift 2 ;;
    --plugin) PLUGIN_FILTER="$2"; shift 2 ;;
    --lang)   LANG_CODE="$2";     shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2
       echo "Usage: bash pack_plugins.sh [--name <name>] [--plugin <plugin-name>] [--lang <code>]" >&2
       exit 1 ;;
  esac
done

if [[ -n "$PLUGIN_FILTER" ]]; then
  PACK_NAME="${PACK_NAME:-$PLUGIN_FILTER}"
else
  PACK_NAME="${PACK_NAME:-plugins}"
fi

# ---------------------------------------------------------------------------
# Language resolution
# ---------------------------------------------------------------------------
_LANG_TMPDIR=""
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  _LANG_TMPDIR=$(mktemp -d "/tmp/pack-lang-${LANG_CODE}-XXXXXX")
  bash "$SCRIPT_DIR/bin/resolve-lang.sh" --lang "$LANG_CODE" --source "$MONOREPO_ROOT" --target "$_LANG_TMPDIR"
  MONOREPO_ROOT="$_LANG_TMPDIR"
fi
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"' EXIT

PLUGINS_SRC="$SCRIPT_DIR/plugins"   # always the real (non-translated) source

if [[ ! -d "$PLUGINS_SRC" ]]; then
  echo "ERROR: plugins/ directory not found in $SCRIPT_DIR" >&2
  exit 1
fi

if [[ -n "$PLUGIN_FILTER" && ! -d "$PLUGINS_SRC/$PLUGIN_FILTER" ]]; then
  echo "ERROR: plugin '$PLUGIN_FILTER' not found in plugins/" >&2
  exit 1
fi

if [[ -n "$PLUGIN_FILTER" ]]; then
  echo "==> Packaging individual plugin '$PLUGIN_FILTER' as '$PACK_NAME'"
else
  echo "==> Packaging plugin marketplace as '$PACK_NAME'"
fi

# ---------------------------------------------------------------------------
# Phase 1 — Staging
# ---------------------------------------------------------------------------
STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT

# ---------------------------------------------------------------------------
# Phase 2 — Helper: pack one skill into a destination directory
# ---------------------------------------------------------------------------
N_GUIDES=0

_pack_one_skill() {
  local skill_src="$1"
  local skill_dst="$2"
  local skill_name
  skill_name="$(basename "$skill_src")"

  if [[ ! -d "$skill_src" ]]; then
    echo "    WARN: skill '$skill_name' not found at $skill_src — skipped" >&2
    return 0
  fi

  mkdir -p "$skill_dst"
  cp -r "$skill_src"/. "$skill_dst/"

  # Resolve skill-guides declared inside the skill
  if [[ -f "$skill_src/skill-guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      local guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$skill_dst/$guide"
        N_GUIDES=$((N_GUIDES + 1))
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$skill_dst/$guide"
        N_GUIDES=$((N_GUIDES + 1))
      else
        echo "    WARN: guide '$guide' referenced by '$skill_name' not found — skipped" >&2
      fi
    done < "$skill_src/skill-guides"
  fi

  # Remove the manifest — it must not ship to runtime
  rm -f "$skill_dst/skill-guides"

  # Fix path references so guides resolve locally
  find "$skill_dst" -type f \( -name '*.md' -o -name '*.txt' \) \
    -exec sed -i 's|skills-guides/||g; s|shared-skill-guides/||g' {} \;
}

# ---------------------------------------------------------------------------
# Phase 3 — Process plugins
# ---------------------------------------------------------------------------
N_PLUGINS=0
N_SKILLS_TOTAL=0

# Marketplace manifest (only needed when packing all plugins)
if [[ -z "$PLUGIN_FILTER" ]]; then
  cp -r "$PLUGINS_SRC/.claude-plugin" "$STAGING/.claude-plugin"
fi

for plugin_dir in "$PLUGINS_SRC"/*/; do
  [[ -d "$plugin_dir" ]] || continue
  plugin_name="$(basename "$plugin_dir")"

  if [[ -n "$PLUGIN_FILTER" && "$plugin_name" != "$PLUGIN_FILTER" ]]; then
    continue
  fi

  plugin_json="$plugin_dir/.claude-plugin/plugin.json"
  if [[ ! -f "$plugin_json" ]]; then
    echo "WARN: $plugin_name has no .claude-plugin/plugin.json — skipped" >&2
    continue
  fi

  echo "    plugin '$plugin_name'"

  # In single-plugin mode files go directly to staging root; in bulk mode into a subdir
  if [[ -n "$PLUGIN_FILTER" ]]; then
    out_plugin="$STAGING"
  else
    out_plugin="$STAGING/$plugin_name"
  fi
  mkdir -p "$out_plugin/.claude-plugin" "$out_plugin/skills"

  # Emit a clean plugin.json with skills pointing to ./skills/
  python3 - "$plugin_json" "$out_plugin/.claude-plugin/plugin.json" <<'PYEOF'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))
out = {"name": d["name"], "version": d.get("version", "1.0.0"),
       "description": d.get("description", ""), "skills": "./skills/"}
json.dump(out, open(dst, "w"), indent=2)
PYEOF

  # Resolve skill names from the skills array in plugin.json
  skill_names=$(python3 - "$plugin_json" <<'PYEOF'
import json, os, sys
d = json.load(open(sys.argv[1]))
skills = d.get("skills", [])
if isinstance(skills, list):
    for s in skills:
        print(os.path.basename(s.rstrip("/")))
PYEOF
)

  N_SKILLS=0
  while IFS= read -r skill_name || [[ -n "$skill_name" ]]; do
    [[ -z "$skill_name" ]] && continue
    _pack_one_skill "$MONOREPO_ROOT/shared-skills/$skill_name" "$out_plugin/skills/$skill_name"
    N_SKILLS=$((N_SKILLS + 1))
  done <<< "$skill_names"

  echo "      $N_SKILLS skill(s), $N_GUIDES guide(s) copied"
  N_SKILLS_TOTAL=$((N_SKILLS_TOTAL + N_SKILLS))
  N_GUIDES=0
  N_PLUGINS=$((N_PLUGINS + 1))
done

echo "    $N_PLUGINS plugin(s), $N_SKILLS_TOTAL skill(s) total"

# ---------------------------------------------------------------------------
# Phase 4 — Path substitutions
# ---------------------------------------------------------------------------
find "$STAGING" \
  -type f \( -name '*.md' -o -name '*.txt' \) \
  -exec sed -i 's|skills-guides/||g; s|shared-skill-guides/||g' {} \;
echo "    Path substitutions applied"

# ---------------------------------------------------------------------------
# Phase 5 — Non-runtime sweep
# ---------------------------------------------------------------------------
bash "$SCRIPT_DIR/bin/sweep-nonruntime.sh" "$STAGING"

# ---------------------------------------------------------------------------
# Phase 6 — Generate ZIP
# ---------------------------------------------------------------------------
REAL_DIST="$SCRIPT_DIR/dist"
mkdir -p "$REAL_DIST"
ZIP_PATH="$REAL_DIST/${PACK_NAME}.zip"
rm -f "$ZIP_PATH"
(cd "$STAGING" && zip -r "$ZIP_PATH" . -q)
ZIP_SIZE=$(du -sh "$ZIP_PATH" | cut -f1)
echo "    ZIP generated: dist/${PACK_NAME}.zip ($ZIP_SIZE)"

# ---------------------------------------------------------------------------
# Phase 7 — Verification
# ---------------------------------------------------------------------------
echo "    Verifying integrity..."
ERRORS=0

# Every skill must have a SKILL.md
for skill_dir in "$STAGING"/*/skills/*/; do
  [[ -d "$skill_dir" ]] || continue
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "    ERROR: $(basename "$skill_dir") has no SKILL.md" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# No residual skill-guides manifests
LEFTOVER=$(find "$STAGING" -name 'skill-guides' -type f 2>/dev/null | wc -l) || true
if [[ "$LEFTOVER" -gt 0 ]]; then
  echo "    ERROR: residual skill-guides file(s) in the output" >&2
  ERRORS=$((ERRORS + 1))
fi

# No residual path references
for pattern in 'skills-guides/' 'shared-skill-guides/'; do
  REFS=$(grep -rl "$pattern" "$STAGING" --include='*.md' --include='*.txt' 2>/dev/null | wc -l) || true
  if [[ "$REFS" -gt 0 ]]; then
    echo "    ERROR: $REFS file(s) still contain '$pattern'" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FAILED: $ERRORS verification error(s)" >&2
  exit 1
fi

echo "==> OK — $N_PLUGINS plugin(s) packaged in dist/${PACK_NAME}.zip"
