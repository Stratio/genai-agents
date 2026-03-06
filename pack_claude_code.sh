#!/usr/bin/env bash
# pack_claude_code.sh — Empaqueta un agente del monorepo para Claude Code CLI
# Uso: bash pack_claude_code.sh --agent <path> [--name <nombre-kebab>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Fase 0 — Parseo y validación
# ---------------------------------------------------------------------------
AGENT_PATH=""
AGENT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_PATH="$2"; shift 2 ;;
    --name)  AGENT_NAME="$2"; shift 2 ;;
    *) echo "ERROR: argumento desconocido: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$AGENT_PATH" ]]; then
  echo "ERROR: --agent es obligatorio" >&2
  echo "Uso: bash pack_claude_code.sh --agent <path> [--name <nombre-kebab>]" >&2
  exit 1
fi

# Resolver ruta absoluta: primero relativo a SCRIPT_DIR, luego como absoluta
if [[ -d "$SCRIPT_DIR/$AGENT_PATH" ]]; then
  AGENT_ABS="$(cd "$SCRIPT_DIR/$AGENT_PATH" && pwd)"
elif [[ -d "$AGENT_PATH" ]]; then
  AGENT_ABS="$(cd "$AGENT_PATH" && pwd)"
else
  echo "ERROR: directorio del agente no encontrado: $AGENT_PATH" >&2
  exit 1
fi

# Nombre por defecto: basename del directorio
if [[ -z "$AGENT_NAME" ]]; then
  AGENT_NAME="$(basename "$AGENT_ABS")"
fi

# Validar formato kebab-case
KEBAB_RE='^[a-z][a-z0-9]*(-[a-z0-9]+)*$'
if [[ ! "$AGENT_NAME" =~ $KEBAB_RE ]]; then
  echo "ERROR: el nombre '$AGENT_NAME' no es kebab-case válido (ej: mi-agente, data-analytics)" >&2
  exit 1
fi

OUTPUT_DIR="$AGENT_ABS/dist/claude_code/$AGENT_NAME"
echo "==> Empaquetando '$AGENT_NAME' para Claude Code"
echo "    Fuente : $AGENT_ABS"
echo "    Destino: $OUTPUT_DIR"

# ---------------------------------------------------------------------------
# Fase 1 — Preparación del output
# ---------------------------------------------------------------------------
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/.claude/skills"

# ---------------------------------------------------------------------------
# Fase 2 — CLAUDE.md
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/AGENTS.md" ]]; then
  cp "$AGENT_ABS/AGENTS.md" "$OUTPUT_DIR/CLAUDE.md"
  echo "    [2] CLAUDE.md copiado desde AGENTS.md"
elif [[ -f "$AGENT_ABS/CLAUDE.md" ]]; then
  cp "$AGENT_ABS/CLAUDE.md" "$OUTPUT_DIR/CLAUDE.md"
  echo "    [2] CLAUDE.md copiado desde CLAUDE.md"
else
  echo "ERROR: no se encontró CLAUDE.md ni AGENTS.md en $AGENT_ABS" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Fase 3 — .claude/settings.local.json
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/.claude/settings.local.json" ]]; then
  cp "$AGENT_ABS/.claude/settings.local.json" "$OUTPUT_DIR/.claude/settings.local.json"
  echo "    [3] .claude/settings.local.json copiado (real)"
else
  cat > "$OUTPUT_DIR/.claude/settings.local.json" << 'EOF'
{
  "env": { "NODE_TLS_REJECT_UNAUTHORIZED": "0" },
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
      "mcp__sql__stratio_list_business_domains",
      "mcp__sql__stratio_list_domain_tables",
      "mcp__sql__stratio_get_tables_details",
      "mcp__sql__stratio_get_table_columns_details",
      "mcp__sql__stratio_generate_sql",
      "mcp__sql__stratio_query_data",
      "mcp__sql__stratio_execute_sql",
      "mcp__sql__stratio_profile_data",
      "mcp__sql__stratio_search_domain_knowledge",
      "mcp__sql__stratio_propose_knowledge"
    ]
  },
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["sql"]
}
EOF
  echo "    [3] .claude/settings.local.json generado (template)"
fi

# ---------------------------------------------------------------------------
# Fase 4 — .mcp.json
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/.mcp.json" ]]; then
  cp "$AGENT_ABS/.mcp.json" "$OUTPUT_DIR/.mcp.json"
  echo "    [4] .mcp.json copiado (real)"
else
  cat > "$OUTPUT_DIR/.mcp.json" << 'EOF'
{
  "mcpServers": {
    "sql": {
      "type": "http",
      "url": "${MCP_SQL_URL:-http://127.0.0.1:8080/mcp}",
      "headers": {
        "X-API-Key": "${MCP_SQL_API_KEY:-}",
        "Authorization": "Bearer ${MCP_SQL_API_KEY:-}"
      },
      "allowedTools": [
        "stratio_list_business_domains", "stratio_list_domain_tables",
        "stratio_get_tables_details", "stratio_get_table_columns_details",
        "stratio_generate_sql", "stratio_query_data",
        "stratio_search_domain_knowledge", "stratio_execute_sql",
        "stratio_profile_data", "stratio_propose_knowledge"
      ]
    }
  }
}
EOF
  echo "    [4] .mcp.json generado (template)"
fi

# ---------------------------------------------------------------------------
# Fase 5 — Skills (opcional)
# ---------------------------------------------------------------------------
SKILLS_SRC=""
if [[ -d "$AGENT_ABS/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/skills"
elif [[ -d "$AGENT_ABS/.claude/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.claude/skills"
elif [[ -d "$AGENT_ABS/.opencode/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.opencode/skills"
elif [[ -d "$AGENT_ABS/.agents/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.agents/skills"
fi

if [[ -n "$SKILLS_SRC" ]]; then
  cp -r "$SKILLS_SRC/." "$OUTPUT_DIR/.claude/skills/"
  # Normalizar: archivos .md sueltos → subcarpeta/SKILL.md
  for md_file in "$OUTPUT_DIR/.claude/skills/"*.md; do
    [[ -f "$md_file" ]] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$OUTPUT_DIR/.claude/skills/$skill_name"
    mv "$md_file" "$OUTPUT_DIR/.claude/skills/$skill_name/SKILL.md"
  done
  N_SKILLS=$(find "$OUTPUT_DIR/.claude/skills" -type f | wc -l)
  echo "    [5] $N_SKILLS skill(s) copiadas desde $SKILLS_SRC"
else
  echo "    [5] Sin skills (continuando sin error)"
fi

# ---------------------------------------------------------------------------
# Fase 5.1 — Shared skills (opcional)
# ---------------------------------------------------------------------------
SHARED_GUIDES_NEEDED=()

if [[ -f "$AGENT_ABS/shared-skills" ]]; then
  N_SHARED=0
  while IFS= read -r skill_name || [[ -n "$skill_name" ]]; do
    # Ignorar lineas vacias y comentarios
    [[ -z "$skill_name" || "$skill_name" == \#* ]] && continue
    skill_src="$MONOREPO_ROOT/shared-skills/$skill_name"
    skill_dst="$OUTPUT_DIR/.claude/skills/$skill_name"
    if [[ ! -d "$skill_src" ]]; then
      echo "    WARN: shared skill '$skill_name' no encontrada en $skill_src — omitida" >&2
      continue
    fi
    # Prioridad local: si ya existe en el output, no sobreescribir
    if [[ -d "$skill_dst" ]]; then
      echo "    [5.1] '$skill_name' omitida (version local tiene prioridad)"
      continue
    fi
    cp -r "$skill_src" "$skill_dst"
    rm -f "$skill_dst/skill-guides"
    # Copiar guides declarados DENTRO de la skill (autocontenida)
    if [[ -f "$skill_src/skill-guides" ]]; then
      while IFS= read -r guide || [[ -n "$guide" ]]; do
        [[ -z "$guide" || "$guide" == \#* ]] && continue
        guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
        if [[ -d "$guide_src" ]]; then
          cp -r "$guide_src" "$skill_dst/$guide"
        elif [[ -f "$guide_src" ]]; then
          cp "$guide_src" "$skill_dst/$guide"
        else
          echo "    WARN: shared guide '$guide' no encontrado — omitido" >&2
        fi
      done < "$skill_src/skill-guides"
      # Actualizar referencias en la skill para que sean locales
      find "$skill_dst" -type f -name '*.md' -exec sed -i 's|skills-guides/||g' {} \;
    fi
    N_SHARED=$((N_SHARED + 1))
    # Acumular guides declarados en la skill
    if [[ -f "$skill_src/skill-guides" ]]; then
      while IFS= read -r guide || [[ -n "$guide" ]]; do
        [[ -z "$guide" || "$guide" == \#* ]] && continue
        SHARED_GUIDES_NEEDED+=("$guide")
      done < "$skill_src/skill-guides"
    fi
  done < "$AGENT_ABS/shared-skills"
  echo "    [5.1] $N_SHARED shared skill(s) incluidas"
else
  echo "    [5.1] Sin shared-skills declaradas (continuando sin error)"
fi

# Acumular guides declarados directamente por el agente
if [[ -f "$AGENT_ABS/shared-guides" ]]; then
  while IFS= read -r guide || [[ -n "$guide" ]]; do
    [[ -z "$guide" || "$guide" == \#* ]] && continue
    SHARED_GUIDES_NEEDED+=("$guide")
  done < "$AGENT_ABS/shared-guides"
fi

# Copiar shared-skill-guides al output (deduplicando)
if [[ ${#SHARED_GUIDES_NEEDED[@]} -gt 0 ]]; then
  mkdir -p "$OUTPUT_DIR/.claude/skills-guides"
  declare -A _GUIDES_SEEN=()
  N_GUIDES=0
  for guide in "${SHARED_GUIDES_NEEDED[@]}"; do
    [[ -n "${_GUIDES_SEEN[$guide]:-}" ]] && continue
    _GUIDES_SEEN[$guide]=1
    guide_src="$MONOREPO_ROOT/shared-skill-guides/$guide"
    if [[ -d "$guide_src" ]]; then
      cp -r "$guide_src" "$OUTPUT_DIR/.claude/skills-guides/$guide"
    elif [[ -f "$guide_src" ]]; then
      cp "$guide_src" "$OUTPUT_DIR/.claude/skills-guides/$guide"
    else
      echo "    WARN: shared guide '$guide' no encontrado en $guide_src — omitido" >&2
      continue
    fi
    N_GUIDES=$((N_GUIDES + 1))
  done
  echo "    [5.1] $N_GUIDES shared guide(s) copiados a .claude/skills-guides/"
fi

# ---------------------------------------------------------------------------
# Fase 5.5 — Output templates (opcional)
# ---------------------------------------------------------------------------
if [[ -d "$AGENT_ABS/output-templates" ]]; then
  mkdir -p "$OUTPUT_DIR/output"
  cp -r "$AGENT_ABS/output-templates/." "$OUTPUT_DIR/output/"
  N_TEMPLATES=$(find "$OUTPUT_DIR/output" -type f | wc -l)
  echo "    [5.5] $N_TEMPLATES plantilla(s) copiadas desde output-templates/"
fi

# ---------------------------------------------------------------------------
# Fase 6 — rsync del resto de ficheros
# ---------------------------------------------------------------------------
rsync -a \
  --exclude=README.md \
  --exclude=CLAUDE.md \
  --exclude=AGENTS.md \
  --exclude=.mcp.json \
  --exclude=.claude/ \
  --exclude=.opencode/ \
  --exclude=.agents/ \
  --exclude=opencode.json \
  --exclude=skills/ \
  --exclude=shared-skills \
  --exclude=shared-guides \
  --exclude='pack_*.sh' \
  --exclude=output/ \
  --exclude=output-templates/ \
  --exclude=dist/ \
  --exclude=.venv/ \
  --exclude='__pycache__/' \
  --exclude='.pytest_cache/' \
  --exclude='*.pyc' \
  --exclude=.idea/ \
  --exclude=node_modules/ \
  "$AGENT_ABS/" "$OUTPUT_DIR/"
echo "    [6] rsync completado"

# ---------------------------------------------------------------------------
# Fase 7 — Reemplazos de texto (AGENTS.md → CLAUDE.md)
# ---------------------------------------------------------------------------
find "$OUTPUT_DIR" \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' \
  -type f \( -name '*.md' -o -name '*.json' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' \) \
  -exec sed -i 's/AGENTS\.md/CLAUDE.md/g' {} \;
echo "    [7] Reemplazos AGENTS.md → CLAUDE.md aplicados"

# Sustituir placeholder de tool de preguntas por la tool de Claude Code
find "$OUTPUT_DIR" \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' \
  -type f \( -name '*.md' -o -name '*.json' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' \) \
  -exec sed -i 's/{{TOOL_PREGUNTAS}}/ (`AskUserQuestion`)/g' {} \;
echo "    [7b] Placeholder TOOL_PREGUNTAS → AskUserQuestion"

# ---------------------------------------------------------------------------
# Fase 8 — Verificación de integridad
# ---------------------------------------------------------------------------
echo "    [8] Verificando integridad..."
ERRORS=0

# CLAUDE.md existe y no está vacío
if [[ ! -s "$OUTPUT_DIR/CLAUDE.md" ]]; then
  echo "    ERROR: CLAUDE.md no existe o está vacío" >&2
  ERRORS=$((ERRORS + 1))
fi

# Validar JSON con python3 si disponible
_validate_json() {
  local file="$1"
  if command -v python3 &>/dev/null; then
    if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
      echo "    ERROR: JSON inválido: $file" >&2
      ERRORS=$((ERRORS + 1))
    fi
  fi
}
_validate_json "$OUTPUT_DIR/.claude/settings.local.json"
_validate_json "$OUTPUT_DIR/.mcp.json"

# 0 ficheros con referencia a AGENTS.md
REFS=$(grep -rl 'AGENTS\.md' "$OUTPUT_DIR" --include='*.md' --include='*.json' \
       --include='*.sh' --include='*.py' --include='*.txt' 2>/dev/null | wc -l) || true
if [[ "$REFS" -gt 0 ]]; then
  echo "    ERROR: $REFS fichero(s) aún contienen referencia a AGENTS.md:" >&2
  grep -rl 'AGENTS\.md' "$OUTPUT_DIR" --include='*.md' --include='*.json' \
       --include='*.sh' --include='*.py' --include='*.txt' 2>/dev/null >&2 || true
  ERRORS=$((ERRORS + 1))
fi

# Ningún directorio prohibido
for FORBIDDEN in .opencode .agents opencode dist; do
  if [[ -d "$OUTPUT_DIR/$FORBIDDEN" ]]; then
    echo "    ERROR: directorio prohibido encontrado: $FORBIDDEN" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# Total de ficheros
TOTAL=$(find "$OUTPUT_DIR" -type f | wc -l)

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FALLO: $ERRORS error(es) de verificación" >&2
  exit 1
fi

echo "==> OK — $TOTAL fichero(s) generados en $OUTPUT_DIR"
