#!/usr/bin/env bash
# pack_plugins.sh — Creates hard-linked skill trees inside each plugin directory
# so the plugin system can resolve skills via the paths declared in plugin.json.
#
# Usage: bash pack_plugins.sh [--plugin <name>]
#
# For each skill path declared in plugin.json (e.g. "./shared-skills/brand-kit"),
# creates <plugin_dir>/shared-skills/<name>/ as a hard-linked copy of the real
# shared-skills/<name>/ directory (cp -rl). Existing trees are removed first.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Phase 0 — Parsing
# ---------------------------------------------------------------------------
PLUGIN_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plugin) PLUGIN_FILTER="$2"; shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2
       echo "Usage: bash pack_plugins.sh [--plugin <name>]" >&2
       exit 1 ;;
  esac
done

PLUGINS_SRC="$SCRIPT_DIR/plugins"

if [[ ! -d "$PLUGINS_SRC" ]]; then
  echo "ERROR: plugins/ directory not found" >&2; exit 1
fi

if [[ -n "$PLUGIN_FILTER" && ! -d "$PLUGINS_SRC/$PLUGIN_FILTER" ]]; then
  echo "ERROR: plugin '$PLUGIN_FILTER' not found in plugins/" >&2; exit 1
fi

# ---------------------------------------------------------------------------
# Phase 1 — Process each plugin
# ---------------------------------------------------------------------------
N_PLUGINS=0
N_SKILLS_TOTAL=0

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

  echo "==> $plugin_name"

  # Resolve skill paths from plugin.json (array of strings like "./shared-skills/<name>")
  skill_paths=$(python3 - "$plugin_json" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
skills = d.get("skills", [])
if isinstance(skills, list):
    for s in skills:
        print(s)
PYEOF
)

  N_SKILLS=0
  while IFS= read -r skill_path || [[ -n "$skill_path" ]]; do
    [[ -z "$skill_path" ]] && continue

    skill_name="$(basename "$skill_path")"
    # Destination: <plugin_dir>/<skill_path>  (e.g. plugins/genai-generic-skills/shared-skills/brand-kit)
    dest="$plugin_dir/$skill_path"
    # Source: the real skill dir at repo root
    src="$SCRIPT_DIR/shared-skills/$skill_name"

    if [[ ! -d "$src" ]]; then
      echo "  WARN: shared-skills/$skill_name not found — skipped" >&2
      continue
    fi

    # Remove stale tree and recreate via hard links
    rm -rf "$dest"
    mkdir -p "$(dirname "$dest")"
    cp -rl "$src" "$dest"

    echo "  linked $skill_name"
    N_SKILLS=$((N_SKILLS + 1))
  done <<< "$skill_paths"

  echo "    $N_SKILLS skill(s) hard-linked"
  N_SKILLS_TOTAL=$((N_SKILLS_TOTAL + N_SKILLS))
  N_PLUGINS=$((N_PLUGINS + 1))
done

echo ""
echo "==> OK — $N_PLUGINS plugin(s), $N_SKILLS_TOTAL skill(s) hard-linked"
