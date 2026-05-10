#!/usr/bin/env bash
# package.sh — Full packaging with versioned zips, multi-language
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(cat "$REPO_ROOT/VERSION" | tr -d '[:space:]')
# RELEASE: VERSION = 0.1.0-BUILD => strip -BUILD for artifact naming
if [[ "$VERSION" == *-BUILD* ]]; then
  VERSION="$(echo "$VERSION" | cut -d'-' -f1)"
fi
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

SOURCE_DATE_EPOCH=$(git -C "$REPO_ROOT" log -1 --format=%ct 2>/dev/null || echo 0)
export SOURCE_DATE_EPOCH

echo "==> Packaging genai-agents v$VERSION..."
echo "    Languages: ${LANGUAGES[*]}"
echo "    SOURCE_DATE_EPOCH: $SOURCE_DATE_EPOCH"

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

  # --- Generic pack per agent (opencode + stratio_cowork) ---
  while IFS= read -r module; do
    [[ -z "$module" || "$module" =~ ^# ]] && continue
    MODULE_DIR="$REPO_ROOT/$module"

    if [[ ! -d "$MODULE_DIR" ]]; then
      echo "  WARN: Module '$module' does not exist, skipping"
      continue
    fi

    echo "  [$module] Packaging opencode..."
    bash "$REPO_ROOT/pack_opencode.sh" --agent "$module" --name "$module" "${LANG_ARGS[@]}"
    if [[ -n "$LANG_SUFFIX" ]]; then
      INTERMEDIATE="$MODULE_DIR/dist/$lang/opencode/$module"
    else
      INTERMEDIATE="$MODULE_DIR/dist/opencode/$module"
    fi
    if [[ -d "$INTERMEDIATE" ]]; then
      bash "$REPO_ROOT/bin/zip-deterministic.sh" "$INTERMEDIATE" "$DIST_DIR/${module}-opencode${LANG_SUFFIX}-${VERSION}.zip"
      echo "    -> dist/${module}-opencode${LANG_SUFFIX}-${VERSION}.zip"
    fi

    echo "  [$module] Packaging Stratio cowork (agent + mcps + shared skills separately)..."
    bash "$REPO_ROOT/pack_stratio_cowork.sh" --agent "$module" --name "$module" --version "$VERSION" "${LANG_ARGS[@]}" || {
      echo "  WARN: pack_stratio_cowork.sh failed for $module — continuing"
    }
    if [[ -f "$REPO_ROOT/dist/${module}-stratio-cowork.zip" ]]; then
      mv "$REPO_ROOT/dist/${module}-stratio-cowork.zip" "$DIST_DIR/${module}-stratio-cowork${LANG_SUFFIX}-${VERSION}.zip"
      echo "    -> dist/${module}-stratio-cowork${LANG_SUFFIX}-${VERSION}.zip"
    fi

  done < "$REPO_ROOT/release-modules"

  # --- Pack skills (bulk) ---
  echo "  [skills] Packaging skills bundle..."
  bash "$REPO_ROOT/pack_skills.sh" --name skills "${LANG_ARGS[@]}"
  if [[ -f "$REPO_ROOT/dist/skills.zip" ]]; then
    mv "$REPO_ROOT/dist/skills.zip" "$DIST_DIR/skills${LANG_SUFFIX}-${VERSION}.zip"
    echo "    -> dist/skills${LANG_SUFFIX}-${VERSION}.zip"
  fi

  # --- Pack individual skills ---
  for skill_dir in "$REPO_ROOT/skills"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    echo "  [skills] Packaging individual skill '$skill_name'..."
    bash "$REPO_ROOT/pack_skills.sh" --skill "$skill_name" "${LANG_ARGS[@]}"
    if [[ -f "$REPO_ROOT/dist/${skill_name}.zip" ]]; then
      mv "$REPO_ROOT/dist/${skill_name}.zip" "$DIST_DIR/skill-${skill_name}${LANG_SUFFIX}-${VERSION}.zip"
      echo "    -> dist/skill-${skill_name}${LANG_SUFFIX}-${VERSION}.zip"
    fi
  done

  # --- Pass 2: Functional plugins (plugins/*) ---
  if [[ -d "$REPO_ROOT/plugins" ]]; then
    # Run validator once per language pass (the plugin manifests don't change between languages)
    if [[ -x "$REPO_ROOT/bin/validate-plugins.py" ]]; then
      python3 "$REPO_ROOT/bin/validate-plugins.py" >/dev/null
    fi
    for plugin_dir in "$REPO_ROOT/plugins"/*/; do
      [[ -d "$plugin_dir" ]] || continue
      plugin_name="$(basename "$plugin_dir")"
      [[ "$plugin_name" == .* ]] && continue
      [[ -f "$plugin_dir/plugin.yaml" ]] || continue

      for plugin_platform in stratio-cowork claude; do
        echo "  [plugin:$plugin_name] Packaging for $plugin_platform${LANG_SUFFIX:+ ($lang)}..."
        bash "$REPO_ROOT/pack_plugin.sh" \
          --plugin "$plugin_name" \
          --platform "$plugin_platform" \
          --version "$VERSION" \
          "${LANG_ARGS[@]}" >/dev/null || {
          echo "  WARN: pack_plugin.sh failed for plugin '$plugin_name' / $plugin_platform — continuing"
          continue
        }
        SRC_ZIP="$REPO_ROOT/dist/${plugin_name}-${plugin_platform}.zip"
        if [[ -f "$SRC_ZIP" ]]; then
          mv "$SRC_ZIP" "$DIST_DIR/${plugin_name}-${plugin_platform}${LANG_SUFFIX}-${VERSION}.zip"
          echo "    -> dist/${plugin_name}-${plugin_platform}${LANG_SUFFIX}-${VERSION}.zip"
        fi
      done
    done
  fi
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
