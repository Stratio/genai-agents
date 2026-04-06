#!/usr/bin/env bash
# package.sh — Full packaging with versioned zips, multi-language
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
DIST_DIR="$REPO_ROOT/dist"

# Read languages from the languages file (default: 'en' only)
LANGUAGES_FILE="$REPO_ROOT/languages"
LANGUAGES=()
if [[ -f "$LANGUAGES_FILE" ]]; then
  while IFS= read -r lang || [[ -n "$lang" ]]; do
    lang=$(echo "$lang" | tr -d '[:space:]')
    [[ -z "$lang" || "$lang" == "#"* ]] && continue
    LANGUAGES+=("$lang")
  done < "$LANGUAGES_FILE"
else
  LANGUAGES=(en)
fi

echo "==> Packaging genai-agents v$VERSION..."
echo "    Languages: ${LANGUAGES[*]}"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

for lang in "${LANGUAGES[@]}"; do
  echo ""
  echo "=========================================="
  echo "==> Language: $lang"
  echo "=========================================="

  # Build --lang argument for pack scripts (empty for English)
  LANG_ARGS=()
  LANG_SUFFIX=""
  if [[ "$lang" != "en" ]]; then
    LANG_ARGS=(--lang "$lang")
    LANG_SUFFIX="-${lang}"
  fi

  # --- Generic pack per agent (claude_code + opencode + stratio_cowork) ---
  while IFS= read -r module; do
    [[ -z "$module" || "$module" =~ ^# ]] && continue
    MODULE_DIR="$REPO_ROOT/$module"

    if [[ ! -d "$MODULE_DIR" ]]; then
      echo "  WARN: Module '$module' does not exist, skipping"
      continue
    fi

    echo "  [$module] Packaging claude_code..."
    bash "$REPO_ROOT/pack_claude_code.sh" --agent "$module" --name "$module" "${LANG_ARGS[@]}"
    # Intermediate output: {agent}/dist/[{lang}/]claude_code/{name}/
    if [[ -n "$LANG_SUFFIX" ]]; then
      INTERMEDIATE="$MODULE_DIR/dist/$lang/claude_code/$module"
    else
      INTERMEDIATE="$MODULE_DIR/dist/claude_code/$module"
    fi
    if [[ -d "$INTERMEDIATE" ]]; then
      (cd "$INTERMEDIATE" && zip -r "$DIST_DIR/${module}-claude-code${LANG_SUFFIX}-${VERSION}.zip" . -q)
      echo "    -> dist/${module}-claude-code${LANG_SUFFIX}-${VERSION}.zip"
    fi

    echo "  [$module] Packaging opencode..."
    bash "$REPO_ROOT/pack_opencode.sh" --agent "$module" --name "$module" "${LANG_ARGS[@]}"
    if [[ -n "$LANG_SUFFIX" ]]; then
      INTERMEDIATE="$MODULE_DIR/dist/$lang/opencode/$module"
    else
      INTERMEDIATE="$MODULE_DIR/dist/opencode/$module"
    fi
    if [[ -d "$INTERMEDIATE" ]]; then
      (cd "$INTERMEDIATE" && zip -r "$DIST_DIR/${module}-opencode${LANG_SUFFIX}-${VERSION}.zip" . -q)
      echo "    -> dist/${module}-opencode${LANG_SUFFIX}-${VERSION}.zip"
    fi

    if [[ "$module" != "data-analytics-light" ]]; then
      echo "  [$module] Packaging Stratio cowork (agent + mcps + shared skills separately)..."
      bash "$REPO_ROOT/pack_stratio_cowork.sh" --agent "$module" --name "$module" --version "$VERSION" "${LANG_ARGS[@]}" || {
        echo "  WARN: pack_stratio_cowork.sh failed for $module — continuing"
      }
      if [[ -f "$REPO_ROOT/dist/${module}-stratio-cowork.zip" ]]; then
        mv "$REPO_ROOT/dist/${module}-stratio-cowork.zip" "$DIST_DIR/${module}-stratio-cowork${LANG_SUFFIX}-${VERSION}.zip"
        echo "    -> dist/${module}-stratio-cowork${LANG_SUFFIX}-${VERSION}.zip"
      fi
    fi

  done < "$REPO_ROOT/release-modules"

  # --- Pack shared-skills ---
  echo "  [shared-skills] Packaging shared skills..."
  bash "$REPO_ROOT/pack_shared_skills.sh" --name shared-skills "${LANG_ARGS[@]}"
  if [[ -f "$REPO_ROOT/dist/shared-skills.zip" ]]; then
    mv "$REPO_ROOT/dist/shared-skills.zip" "$DIST_DIR/shared-skills${LANG_SUFFIX}-${VERSION}.zip"
    echo "    -> dist/shared-skills${LANG_SUFFIX}-${VERSION}.zip"
  fi

  # --- Pack individual shared-skills ---
  for skill_dir in "$REPO_ROOT/shared-skills"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    echo "  [shared-skills] Packaging individual skill '$skill_name'..."
    bash "$REPO_ROOT/pack_shared_skills.sh" --skill "$skill_name" "${LANG_ARGS[@]}"
    if [[ -f "$REPO_ROOT/dist/${skill_name}.zip" ]]; then
      mv "$REPO_ROOT/dist/${skill_name}.zip" "$DIST_DIR/shared-skill-${skill_name}${LANG_SUFFIX}-${VERSION}.zip"
      echo "    -> dist/shared-skill-${skill_name}${LANG_SUFFIX}-${VERSION}.zip"
    fi
  done

  # --- Additional packs for agents with their own scripts ---
  _pack_agent_extras() {
    local agent_name="$1"
    local agent_dir="$REPO_ROOT/$agent_name"
    [[ -d "$agent_dir" ]] || return 0

    for pack_script in "$agent_dir"/pack_claude_*.sh; do
      [[ ! -f "$pack_script" ]] && continue
      local script_name
      script_name=$(basename "$pack_script")

      # Extract type from name: pack_claude_ai_project.sh -> ai_project
      local pack_type="${script_name#pack_claude_}"
      pack_type="${pack_type%.sh}"

      echo "  [$agent_name] Running $script_name..."
      (cd "$agent_dir" && bash "$script_name" --name "$agent_name" "${LANG_ARGS[@]}") || {
        echo "  WARN: $script_name failed — continuing"
        continue
      }

      # Find the generated output directory
      local output_subdir=""
      case "$pack_type" in
        ai_project) output_subdir="dist${LANG_SUFFIX:+/$lang}/claude_ai_projects/$agent_name" ;;
        cowork)     output_subdir="dist${LANG_SUFFIX:+/$lang}/claude_cowork/$agent_name" ;;
        *) echo "  WARN: Unknown type: $pack_type"; continue ;;
      esac

      # Normalize PACK_TYPE for the ZIP name (ai_project -> ai-project)
      local zip_type
      zip_type=$(echo "$pack_type" | tr '_' '-')

      local output_dir="$agent_dir/$output_subdir"
      if [[ -d "$output_dir" ]]; then
        (cd "$output_dir" && zip -r "$DIST_DIR/${agent_name}-claude-${zip_type}${LANG_SUFFIX}-${VERSION}.zip" . -q)
        echo "    -> dist/${agent_name}-claude-${zip_type}${LANG_SUFFIX}-${VERSION}.zip"
      fi
    done
  }

  _pack_agent_extras "data-analytics-light"
  _pack_agent_extras "semantic-layer"
  _pack_agent_extras "data-quality"
done

# --- Summary ---
echo ""
echo "=== Packaging completed ==="
echo "  Version: $VERSION"
echo "  Languages: ${LANGUAGES[*]}"
echo "  Artifacts:"
ls -lh "$DIST_DIR"/*.zip 2>/dev/null | while read -r line; do
  echo "    $line"
done
