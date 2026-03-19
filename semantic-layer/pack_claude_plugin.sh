#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

# --- Parsear argumentos CLI ---
ARG_NAME="" ARG_GOV_URL="" ARG_GOV_KEY="" ARG_SQL_URL="" ARG_SQL_KEY="" WITH_AGENT=false SHARED_GUIDES=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)       ARG_NAME="$2"; shift 2 ;;
    --gov-url)    ARG_GOV_URL="$2"; shift 2 ;;
    --gov-key)    ARG_GOV_KEY="$2"; shift 2 ;;
    --sql-url)    ARG_SQL_URL="$2"; shift 2 ;;
    --sql-key)    ARG_SQL_KEY="$2"; shift 2 ;;
    --with-agent) WITH_AGENT=true; shift ;;
    --shared-guides) SHARED_GUIDES=true; shift ;;
    *) echo "ERROR: Argumento desconocido: $1"; echo "Uso: $0 [--name NOMBRE] [--gov-url URL] [--gov-key KEY] [--sql-url URL] [--sql-key KEY] [--with-agent] [--shared-guides]"; exit 1 ;;
  esac
done

# --- Nombre: argumento CLI o default ---
PLUGIN_NAME="${ARG_NAME:-semantic-layer}"

# Validar kebab-case
if ! echo "$PLUGIN_NAME" | grep -qE '^[a-z][a-z0-9]*(-[a-z0-9]+)*$'; then
  echo "ERROR: El nombre del plugin debe ser kebab-case (ej: mi-plugin, semantic-layer)."
  exit 1
fi

PLUGIN_DIR="dist/claude_plugins/$PLUGIN_NAME"

# --- Limpiar si existe ---
if [ -d "$PLUGIN_DIR" ]; then
  echo "Borrando plugin existente en $PLUGIN_DIR..."
  rm -rf "$PLUGIN_DIR"
fi

# --- Crear estructura ---
echo "Creando estructura del plugin..."
mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/skills"

# --- plugin.json ---
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" <<EOF
{
  "name": "$PLUGIN_NAME",
  "description": "Semantic Layer Builder Agent",
  "version": "1.0.0"
}
EOF

# --- Copiar skills ---
echo "Copiando skills..."
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
  cp -r "$SKILLS_SRC"/* "$PLUGIN_DIR/skills/"
  # Normalizar: archivos .md sueltos → subcarpeta/SKILL.md
  for md_file in "$PLUGIN_DIR/skills/"*.md; do
    [ -f "$md_file" ] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$PLUGIN_DIR/skills/$skill_name"
    mv "$md_file" "$PLUGIN_DIR/skills/$skill_name/SKILL.md"
  done
  echo "  Skills copiadas desde $SKILLS_SRC"
else
  echo "WARN: No se encontro directorio de skills — el plugin no tendra skills."
fi

# --- Copiar shared skills (si las declara el agente) ---
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    skill_dst="$PLUGIN_DIR/skills/$skill_name"
    if [ ! -d "$skill_src" ]; then
      echo "  WARN: shared skill '$skill_name' no encontrada en $skill_src — omitida" >&2
      continue
    fi
    # Prioridad local
    if [ -d "$skill_dst" ]; then
      echo "  '$skill_name' omitida (version local tiene prioridad)"
      continue
    fi
    cp -r "$skill_src" "$skill_dst"
    # Eliminar fichero skill-guides del output (no es parte del SKILL.md)
    rm -f "$skill_dst/skill-guides"
    echo "  Shared skill '$skill_name' incluida"
  done < "shared-skills"
fi

# --- Recopilar lista de guides necesarios (shared-skill-guides + locales) ---
GUIDES_NEEDED=()
# Desde shared-skills/*/skill-guides
if [ -f "shared-skills" ]; then
  while IFS= read -r skill_name || [ -n "$skill_name" ]; do
    [ -z "$skill_name" ] || [[ "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    if [ -f "$skill_src/skill-guides" ]; then
      while IFS= read -r guide || [ -n "$guide" ]; do
        [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
        GUIDES_NEEDED+=("shared:$guide")
      done < "$skill_src/skill-guides"
    fi
  done < "shared-skills"
fi
# Desde shared-guides del agente
if [ -f "shared-guides" ]; then
  while IFS= read -r guide || [ -n "$guide" ]; do
    [ -z "$guide" ] || [[ "$guide" == \#* ]] && continue
    GUIDES_NEEDED+=("shared:$guide")
  done < "shared-guides"
fi
# Guides locales (si existen)
if [ -d "skills-guides" ]; then
  for f in skills-guides/*.md; do
    [ -f "$f" ] || continue
    GUIDES_NEEDED+=("local:$(basename "$f")")
  done
fi

# --- Copiar skills-guides ---
# Construir lista deduplicada de guides a copiar
declare -A _GUIDES_MAP=()
for entry in "${GUIDES_NEEDED[@]}"; do
  src_type="${entry%%:*}"
  guide_name="${entry#*:}"
  _GUIDES_MAP["$guide_name"]="$src_type"
done

if [ ${#_GUIDES_MAP[@]} -gt 0 ]; then
  if [ "$SHARED_GUIDES" = true ]; then
    echo "Copiando skills-guides a raiz del plugin (modo compartido)..."
    mkdir -p "$PLUGIN_DIR/skills-guides"
    for guide_name in "${!_GUIDES_MAP[@]}"; do
      src_type="${_GUIDES_MAP[$guide_name]}"
      if [ "$src_type" = "shared" ]; then
        guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide_name"
      else
        guide_src="skills-guides/$guide_name"
      fi
      if [ -d "$guide_src" ]; then
        cp -r "$guide_src" "$PLUGIN_DIR/skills-guides/$guide_name"
      elif [ -f "$guide_src" ]; then
        cp "$guide_src" "$PLUGIN_DIR/skills-guides/$guide_name"
      fi
    done
    sed -i 's|`skills-guides/stratio-semantic-layer-tools\.md`|`../../skills-guides/stratio-semantic-layer-tools.md`|g' "$PLUGIN_DIR/skills/"*/SKILL.md 2>/dev/null || true
  else
    echo "Copiando skills-guides a skills..."
    # Copiar guide dentro de la skill que lo declara (stratio-semantic-layer)
    for skill_dir in "$PLUGIN_DIR/skills/stratio-semantic-layer"; do
      if [ -d "$skill_dir" ]; then
        for guide_name in "${!_GUIDES_MAP[@]}"; do
          src_type="${_GUIDES_MAP[$guide_name]}"
          if [ "$src_type" = "shared" ]; then
            guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide_name"
          else
            guide_src="skills-guides/$guide_name"
          fi
          if [ -d "$guide_src" ]; then
            cp -r "$guide_src" "$skill_dir/$guide_name"
          elif [ -f "$guide_src" ]; then
            cp "$guide_src" "$skill_dir/$guide_name"
          fi
        done
      fi
    done
    sed -i 's|`skills-guides/stratio-semantic-layer-tools\.md`|`stratio-semantic-layer-tools.md`|g' "$PLUGIN_DIR/skills/"*/SKILL.md 2>/dev/null || true
  fi
fi

# --- Generar agent file (solo con --with-agent) ---
if [ "$WITH_AGENT" = true ]; then
  echo "Generando agente del plugin..."
  mkdir -p "$PLUGIN_DIR/agents"
  cat > "$PLUGIN_DIR/agents/$PLUGIN_NAME.md" <<YAMLEOF
---
name: $PLUGIN_NAME
description: Especialista en construccion de capas semanticas en Stratio Governance. Orquesta terminos tecnicos, ontologias, vistas de negocio, SQL mappings, terminos semanticos y business terms.
model: inherit
---
YAMLEOF
  cat AGENTS.md >> "$PLUGIN_DIR/agents/$PLUGIN_NAME.md"
  cat > "$PLUGIN_DIR/settings.json" <<EOF
{
  "agent": "$PLUGIN_NAME"
}
EOF
  # Actualizar referencias a skills-guides/ en agent
  if [ "$SHARED_GUIDES" = true ]; then
    sed -i 's|`skills-guides/stratio-semantic-layer-tools\.md`|`skills-guides/stratio-semantic-layer-tools.md`|g' "$PLUGIN_DIR/agents/"*.md 2>/dev/null || true
  else
    sed -i 's|`skills-guides/stratio-semantic-layer-tools\.md`|`skills/stratio-semantic-layer/stratio-semantic-layer-tools.md`|g' "$PLUGIN_DIR/agents/"*.md 2>/dev/null || true
  fi
  sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PLUGIN_DIR/agents/"*.md 2>/dev/null || true
fi
sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' "$PLUGIN_DIR/skills/"*/SKILL.md 2>/dev/null || true

# --- .mcp.json del plugin (2 servidores: gov + sql) ---
GOV_URL_VALUE="${ARG_GOV_URL:-\$\{MCP_GOV_URL:-http://127.0.0.1:8080/mcp\}}"
GOV_KEY_VALUE="${ARG_GOV_KEY:-\$\{MCP_GOV_API_KEY:-\}}"
SQL_URL_VALUE="${ARG_SQL_URL:-\$\{MCP_SQL_URL:-http://127.0.0.1:8080/mcp\}}"
SQL_KEY_VALUE="${ARG_SQL_KEY:-\$\{MCP_SQL_API_KEY:-\}}"

if [ -n "$ARG_GOV_URL" ] || [ -n "$ARG_GOV_KEY" ] || [ -n "$ARG_SQL_URL" ] || [ -n "$ARG_SQL_KEY" ]; then
  # Al menos un valor concreto proporcionado — generar con valores mixtos
  cat > "$PLUGIN_DIR/.mcp.json" <<EOF
{
  "mcpServers": {
    "gov": {
      "type": "http",
      "url": "$GOV_URL_VALUE",
      "headers": {
        "X-API-Key": "$GOV_KEY_VALUE",
        "Authorization": "Bearer $GOV_KEY_VALUE"
      },
      "allowedTools": [
        "stratio_list_ontologies",
        "stratio_get_ontology_info",
        "stratio_create_ontology",
        "stratio_update_ontology",
        "stratio_create_technical_terms",
        "stratio_create_business_views",
        "stratio_create_sql_mappings",
        "stratio_create_semantic_terms",
        "stratio_create_business_term",
        "stratio_list_business_asset_types",
        "stratio_list_technical_domain_concepts",
        "stratio_create_collection_description",
        "stratio_delete_ontology_classes",
        "stratio_delete_business_views"
      ]
    },
    "sql": {
      "type": "http",
      "url": "$SQL_URL_VALUE",
      "headers": {
        "X-API-Key": "$SQL_KEY_VALUE",
        "Authorization": "Bearer $SQL_KEY_VALUE"
      },
      "allowedTools": [
        "stratio_list_technical_domains",
        "stratio_list_domain_tables",
        "stratio_get_tables_details",
        "stratio_get_table_columns_details",
        "stratio_list_business_domains",
        "stratio_search_domain_knowledge"
      ]
    }
  }
}
EOF
else
  # Sin args: dejar templates con variables de entorno
  cat > "$PLUGIN_DIR/.mcp.json" <<'EOF'
{
  "mcpServers": {
    "gov": {
      "type": "http",
      "url": "${MCP_GOV_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_GOV_API_KEY:-}",
        "Authorization": "Bearer ${MCP_GOV_API_KEY:-}"
      },
      "allowedTools": [
        "stratio_list_ontologies",
        "stratio_get_ontology_info",
        "stratio_create_ontology",
        "stratio_update_ontology",
        "stratio_create_technical_terms",
        "stratio_create_business_views",
        "stratio_create_sql_mappings",
        "stratio_create_semantic_terms",
        "stratio_create_business_term",
        "stratio_list_business_asset_types",
        "stratio_list_technical_domain_concepts",
        "stratio_create_collection_description",
        "stratio_delete_ontology_classes",
        "stratio_delete_business_views"
      ]
    },
    "sql": {
      "type": "http",
      "url": "${MCP_SQL_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_SQL_API_KEY:-}",
        "Authorization": "Bearer ${MCP_SQL_API_KEY:-}"
      },
      "allowedTools": [
        "stratio_list_technical_domains",
        "stratio_list_domain_tables",
        "stratio_get_tables_details",
        "stratio_get_table_columns_details",
        "stratio_list_business_domains",
        "stratio_search_domain_knowledge"
      ]
    }
  }
}
EOF
fi

# --- Generar ZIP ---
ZIP_NAME="${PLUGIN_NAME}.zip"
echo "Generando $ZIP_NAME..."
(cd "$PLUGIN_DIR" && zip -r "../_tmp_${ZIP_NAME}" . -q)
# Limpiar contenido del directorio y dejar solo el ZIP
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"
mv "dist/claude_plugins/_tmp_${ZIP_NAME}" "$PLUGIN_DIR/${ZIP_NAME}"

# --- Resumen ---
ZIP_SIZE=$(du -sh "$PLUGIN_DIR/${ZIP_NAME}" | cut -f1)
echo ""
echo "=== Plugin empaquetado ==="
echo "  ZIP: $PLUGIN_DIR/${ZIP_NAME} ($ZIP_SIZE)"
echo ""
if [ -n "$ARG_GOV_URL" ]; then
  echo "  GOV MCP URL: $ARG_GOV_URL"
else
  echo "  GOV MCP URL: \${MCP_GOV_URL:-http://127.0.0.1:8080/mcp} (env var)"
fi
if [ -n "$ARG_SQL_URL" ]; then
  echo "  SQL MCP URL: $ARG_SQL_URL"
else
  echo "  SQL MCP URL: \${MCP_SQL_URL:-http://127.0.0.1:8080/mcp} (env var)"
fi
echo ""
