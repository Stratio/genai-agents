#!/usr/bin/env bash
# pack_plugin.sh — Packages a functional plugin (plugins/<name>/) for a target platform.
#
# Usage:
#   bash pack_plugin.sh --plugin <name> --platform stratio-cowork [--version <semver>] [--lang <code>]
#   bash pack_plugin.sh --plugin <name> --platform claude         [--version <semver>] [--lang <code>]
#
# Output:
#   dist/<plugin>-stratio-cowork.zip   (wrapper bundle: agents/v1 sub-zips + skills sub-zip + plugin.yaml + README)
#   dist/<plugin>-claude.zip           (.claude-plugin/plugin.json + README + skills/)
#
# bin/package.sh handles language suffix and version renaming after this script writes the unsuffixed zip.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"
SOURCE_DATE_EPOCH=$(git -C "$SCRIPT_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
export SOURCE_DATE_EPOCH

# ---------------------------------------------------------------------------
# Phase 0 — Parsing
# ---------------------------------------------------------------------------
PLUGIN_NAME=""
PLATFORM=""
PLUGIN_VERSION=""
LANG_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plugin)   PLUGIN_NAME="$2";    shift 2 ;;
    --platform) PLATFORM="$2";       shift 2 ;;
    --version)  PLUGIN_VERSION="$2"; shift 2 ;;
    --lang)     LANG_CODE="$2";      shift 2 ;;
    *) echo "ERROR: unknown argument: $1" >&2
       echo "Usage: bash pack_plugin.sh --plugin <name> --platform {stratio-cowork|claude} [--version <semver>] [--lang <code>]" >&2
       exit 1 ;;
  esac
done

if [[ -z "$PLUGIN_NAME" || -z "$PLATFORM" ]]; then
  echo "ERROR: --plugin and --platform are required" >&2
  exit 1
fi

case "$PLATFORM" in
  stratio-cowork|claude) ;;
  *) echo "ERROR: --platform must be 'stratio-cowork' or 'claude' (got '$PLATFORM')" >&2; exit 1 ;;
esac

PLUGIN_DIR="$MONOREPO_ROOT/plugins/$PLUGIN_NAME"
if [[ ! -d "$PLUGIN_DIR" ]]; then
  echo "ERROR: plugin '$PLUGIN_NAME' not found at $PLUGIN_DIR" >&2
  exit 1
fi

PLUGIN_YAML="$PLUGIN_DIR/plugin.yaml"
if [[ ! -f "$PLUGIN_YAML" ]]; then
  echo "ERROR: $PLUGIN_YAML not found" >&2
  exit 1
fi

# Run the validator before doing anything destructive
if [[ -x "$MONOREPO_ROOT/bin/validate-plugins.py" ]]; then
  python3 "$MONOREPO_ROOT/bin/validate-plugins.py" --plugin "$PLUGIN_NAME" >/dev/null
fi

# ---------------------------------------------------------------------------
# Phase 1 — Read plugin.yaml fields (delegated to Python for proper YAML parsing)
# ---------------------------------------------------------------------------
_PLUGIN_FIELDS=$(python3 - "$PLUGIN_YAML" <<'PY'
import sys, yaml, json
d = yaml.safe_load(open(sys.argv[1])) or {}
contents = d.get("contents") or {}
agents = contents.get("agents") or []
skills = contents.get("skills") or []
mcps = d.get("mcps") or []
platforms = d.get("platforms")  # may be None
print(json.dumps({
  "name": d.get("name", ""),
  "version": d.get("version") or "",
  "description": d.get("description", ""),
  "tags": d.get("tags") or [],
  "agents": agents,
  "skills": skills,
  "mcps": mcps,
  "platforms": platforms,
}))
PY
)

PLUGIN_DESC=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read())['description'])" <<<"$_PLUGIN_FIELDS")
PLUGIN_AGENTS=()
while IFS= read -r line; do [[ -n "$line" ]] && PLUGIN_AGENTS+=("$line"); done < <(python3 -c "import json,sys; [print(a) for a in json.loads(sys.stdin.read())['agents']]" <<<"$_PLUGIN_FIELDS")
PLUGIN_SKILLS=()
while IFS= read -r line; do [[ -n "$line" ]] && PLUGIN_SKILLS+=("$line"); done < <(python3 -c "import json,sys; [print(s) for s in json.loads(sys.stdin.read())['skills']]" <<<"$_PLUGIN_FIELDS")
PLUGIN_MCPS=()
while IFS= read -r line; do [[ -n "$line" ]] && PLUGIN_MCPS+=("$line"); done < <(python3 -c "import json,sys; [print(m) for m in json.loads(sys.stdin.read())['mcps']]" <<<"$_PLUGIN_FIELDS")

# Resolve effective platforms (defaults derived from contents)
EFFECTIVE_PLATFORMS=$(python3 - <<PY
import json
d = json.loads('''$_PLUGIN_FIELDS''')
agents = d.get("agents") or []
declared = d.get("platforms")
if declared is None:
    print("stratio-cowork" if agents else "stratio-cowork claude")
else:
    print(" ".join(declared))
PY
)

# Compatibility check: requested platform must be in effective platforms
if ! echo " $EFFECTIVE_PLATFORMS " | grep -q " $PLATFORM "; then
  echo "==> Plugin '$PLUGIN_NAME' is not compatible with platform '$PLATFORM' (effective: $EFFECTIVE_PLATFORMS); skipping"
  exit 0
fi

# Strict rule: claude + agents is invalid (validator already catches it, defense in depth)
if [[ "$PLATFORM" == "claude" && ${#PLUGIN_AGENTS[@]} -gt 0 ]]; then
  echo "ERROR: plugin '$PLUGIN_NAME' has agents — Claude does not support agents in plugins" >&2
  exit 1
fi

EFFECTIVE_VERSION="${PLUGIN_VERSION:-${EFFECTIVE_VERSION_FROM_FIELDS:-}}"
# Read version from the manifest if --version was not passed
if [[ -z "$EFFECTIVE_VERSION" ]]; then
  EFFECTIVE_VERSION=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read())['version'])" <<<"$_PLUGIN_FIELDS")
fi

# ---------------------------------------------------------------------------
# Phase 2 — Language resolution (overlay if lang != en)
# ---------------------------------------------------------------------------
REAL_PLUGIN_DIR="$PLUGIN_DIR"
_LANG_TMPDIR=""
LANG_PASSTHROUGH=()
if [[ -n "$LANG_CODE" && "$LANG_CODE" != "en" ]]; then
  _LANG_TMPDIR=$(mktemp -d "/tmp/pack-plugin-${LANG_CODE}-XXXXXX")
  bash "$MONOREPO_ROOT/bin/resolve-lang.sh" --lang "$LANG_CODE" --source "$MONOREPO_ROOT" --target "$_LANG_TMPDIR"
  MONOREPO_ROOT="$_LANG_TMPDIR"
  PLUGIN_DIR="$_LANG_TMPDIR/plugins/$PLUGIN_NAME"
  LANG_PASSTHROUGH=(--lang "$LANG_CODE")
fi
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"' EXIT

echo "==> Packaging plugin '$PLUGIN_NAME' for $PLATFORM${LANG_CODE:+ ($LANG_CODE)}"
echo "    Agents : ${PLUGIN_AGENTS[*]:-none}"
echo "    Skills : ${PLUGIN_SKILLS[*]:-none}"

# ---------------------------------------------------------------------------
# Phase 3 — Build staging area
# ---------------------------------------------------------------------------
STAGING=$(mktemp -d "/tmp/pack-plugin-staging-XXXXXX")
trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"; rm -rf "$STAGING"' EXIT

# Copy README from the plugin (taken from the language-resolved tree)
if [[ -f "$PLUGIN_DIR/README.md" ]]; then
  cp "$PLUGIN_DIR/README.md" "$STAGING/README.md"
else
  echo "ERROR: plugin README.md missing at $PLUGIN_DIR/README.md" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Helper — pack a single skill into a destination directory (replicates
# pack_shared_skills.sh::_pack_one_skill: copy + resolve guides + flatten paths)
# ---------------------------------------------------------------------------
_pack_one_skill_into() {
  local skill_name="$1"
  local dest_dir="$2"

  local src="$MONOREPO_ROOT/shared-skills/$skill_name"
  if [[ ! -d "$src" ]]; then
    echo "ERROR: skill '$skill_name' not found in shared-skills/" >&2
    return 1
  fi

  mkdir -p "$dest_dir"
  cp -r "$src/." "$dest_dir/"

  if [[ -f "$src/skill-guides" ]]; then
    while IFS= read -r guide || [[ -n "$guide" ]]; do
      [[ -z "$guide" || "$guide" == \#* ]] && continue
      local guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
      if [[ -d "$guide_src" ]]; then
        cp -r "$guide_src" "$dest_dir/$guide"
      elif [[ -f "$guide_src" ]]; then
        cp "$guide_src" "$dest_dir/$guide"
      else
        echo "    WARN: guide '$guide' not found for skill '$skill_name' — skipped" >&2
      fi
    done < "$src/skill-guides"
  fi

  rm -f "$dest_dir/skill-guides"
  find "$dest_dir" -type f \( -name '*.md' -o -name '*.txt' \) \
    -exec sed -i 's|skills-guides/||g' {} \;
  find "$dest_dir" -type f \( -name '*.md' -o -name '*.txt' \) \
    -exec sed -i 's|shared-skill-guides/||g' {} \;
}

# ---------------------------------------------------------------------------
# Phase 4 — Branch by platform
# ---------------------------------------------------------------------------
REAL_DIST="$SCRIPT_DIR/dist"
mkdir -p "$REAL_DIST"

if [[ "$PLATFORM" == "stratio-cowork" ]]; then
  # ----- Stratio Cowork wrapper bundle -----

  # 4a. Sub-zip per agent (regenerate via pack_stratio_cowork.sh — idempotent)
  if [[ ${#PLUGIN_AGENTS[@]} -gt 0 ]]; then
    mkdir -p "$STAGING/agents"
    for agent in "${PLUGIN_AGENTS[@]}"; do
      echo "    [4a] Packaging agent '$agent' (stratio-cowork)..."
      VERSION_ARG=()
      [[ -n "$EFFECTIVE_VERSION" ]] && VERSION_ARG=(--version "$EFFECTIVE_VERSION")
      bash "$SCRIPT_DIR/pack_stratio_cowork.sh" \
        --agent "$agent" --name "$agent" \
        "${VERSION_ARG[@]}" "${LANG_PASSTHROUGH[@]}" >/dev/null
      AGENT_ZIP="$REAL_DIST/${agent}-stratio-cowork.zip"
      if [[ ! -f "$AGENT_ZIP" ]]; then
        echo "ERROR: pack_stratio_cowork.sh did not produce $AGENT_ZIP" >&2
        exit 1
      fi
      # Move (not copy) so the unsuffixed intermediate doesn't pollute dist/.
      # bin/package.sh's pass 1 already renamed the legitimate per-agent zip to
      # <agent>-stratio-cowork-<lang>-<version>.zip; the file we're moving here
      # is the one our own pack_stratio_cowork.sh call just regenerated.
      mv "$AGENT_ZIP" "$STAGING/agents/${agent}-stratio-cowork.zip"
    done
  fi

  # 4b. Sub-zip with the explicitly-listed skills (only those NOT already arrastradas
  # by an agent of the plugin). For now — and consistently with the plan — we
  # include exactly what `skills:` declares; if an agent already pulls a skill
  # via its own `shared-skills` manifest, listing it again here is allowed
  # (idempotent) but the validator could later warn on it.
  if [[ ${#PLUGIN_SKILLS[@]} -gt 0 ]]; then
    mkdir -p "$STAGING/shared-skills"
    SKILLS_STAGING=$(mktemp -d "/tmp/pack-plugin-skills-XXXXXX")
    trap '[[ -n "$_LANG_TMPDIR" ]] && rm -rf "$_LANG_TMPDIR"; rm -rf "$STAGING" "$SKILLS_STAGING"' EXIT
    for skill in "${PLUGIN_SKILLS[@]}"; do
      _pack_one_skill_into "$skill" "$SKILLS_STAGING/$skill"
    done
    bash "$SCRIPT_DIR/bin/sweep-nonruntime.sh" "$SKILLS_STAGING"
    bash "$SCRIPT_DIR/bin/zip-deterministic.sh" \
      "$SKILLS_STAGING" "$STAGING/shared-skills/${PLUGIN_NAME}-skills.zip"
    echo "    [4b] ${#PLUGIN_SKILLS[@]} skill(s) packaged into ${PLUGIN_NAME}-skills.zip"
  fi

  # 4c. Aggregated plugin.yaml in the wrapper (with bundles[] for the deployer)
  AGGREGATED_YAML="$STAGING/plugin.yaml"
  python3 - "$PLUGIN_YAML" "$AGGREGATED_YAML" "$EFFECTIVE_VERSION" "$STAGING" <<'PY'
import sys, hashlib, yaml
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
version = sys.argv[3] or None
staging = Path(sys.argv[4])

manifest = yaml.safe_load(src.read_text()) or {}
if version:
    manifest["version"] = version

bundles = []
agents_dir = staging / "agents"
if agents_dir.is_dir():
    for sub in sorted(agents_dir.glob("*.zip")):
        bundles.append({
            "path": f"agents/{sub.name}",
            "type": "agent",
            "endpoint": "/v1/agents/bundle/import",
            "sha256": hashlib.sha256(sub.read_bytes()).hexdigest(),
        })
skills_dir = staging / "shared-skills"
if skills_dir.is_dir():
    for sub in sorted(skills_dir.glob("*.zip")):
        bundles.append({
            "path": f"shared-skills/{sub.name}",
            "type": "skills",
            "endpoint": "/v1/agents/skills/bundle/import",
            "sha256": hashlib.sha256(sub.read_bytes()).hexdigest(),
        })
manifest["bundles"] = bundles

dst.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True))
PY

  # 4d. Wrapper zip
  WRAPPER_ZIP="$REAL_DIST/${PLUGIN_NAME}-stratio-cowork.zip"
  rm -f "$WRAPPER_ZIP"
  bash "$SCRIPT_DIR/bin/zip-deterministic.sh" "$STAGING" "$WRAPPER_ZIP"
  ZIP_SIZE=$(du -sh "$WRAPPER_ZIP" | cut -f1)
  echo "==> OK — dist/${PLUGIN_NAME}-stratio-cowork.zip ($ZIP_SIZE)"

elif [[ "$PLATFORM" == "claude" ]]; then
  # ----- Claude marketplace plugin -----

  # Defense in depth: claude requires skills only (already enforced by validator)
  if [[ ${#PLUGIN_SKILLS[@]} -eq 0 ]]; then
    echo "ERROR: plugin '$PLUGIN_NAME' has no skills — cannot build a Claude variant" >&2
    exit 1
  fi

  # 4e. Copy each skill (with guides resolved) into staging/skills/<skill>/
  mkdir -p "$STAGING/skills"
  for skill in "${PLUGIN_SKILLS[@]}"; do
    _pack_one_skill_into "$skill" "$STAGING/skills/$skill"
  done

  # 4f. Generate .claude-plugin/plugin.json
  mkdir -p "$STAGING/.claude-plugin"
  python3 - "$PLUGIN_YAML" "$STAGING/.claude-plugin/plugin.json" "$EFFECTIVE_VERSION" <<'PY'
import sys, json, yaml
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
version = sys.argv[3] or None

manifest = yaml.safe_load(src.read_text()) or {}
contents = manifest.get("contents") or {}
skills = contents.get("skills") or []

obj = {
    "name": manifest["name"],
    "version": version or manifest.get("version") or "0.0.0",
    "description": manifest["description"],
    "skills": [f"./skills/{s}" for s in skills],
}
dst.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
PY

  # 4g. Marketplace ZIP
  bash "$SCRIPT_DIR/bin/sweep-nonruntime.sh" "$STAGING"
  CLAUDE_ZIP="$REAL_DIST/${PLUGIN_NAME}-claude.zip"
  rm -f "$CLAUDE_ZIP"
  bash "$SCRIPT_DIR/bin/zip-deterministic.sh" "$STAGING" "$CLAUDE_ZIP"
  ZIP_SIZE=$(du -sh "$CLAUDE_ZIP" | cut -f1)
  echo "==> OK — dist/${PLUGIN_NAME}-claude.zip ($ZIP_SIZE)"
fi
