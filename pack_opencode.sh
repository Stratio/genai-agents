#!/usr/bin/env bash
# pack_opencode.sh — Empaqueta un agente del monorepo para OpenCode
# Uso: bash pack_opencode.sh --agent <path> [--name <nombre-kebab>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
  echo "Uso: bash pack_opencode.sh --agent <path> [--name <nombre-kebab>]" >&2
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

OUTPUT_DIR="$AGENT_ABS/dist/opencode/$AGENT_NAME"
echo "==> Empaquetando '$AGENT_NAME' para OpenCode"
echo "    Fuente : $AGENT_ABS"
echo "    Destino: $OUTPUT_DIR"

# ---------------------------------------------------------------------------
# Fase 1 — Preparación del output
# ---------------------------------------------------------------------------
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/.opencode/skills"

# ---------------------------------------------------------------------------
# Fase 2 — AGENTS.md
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/AGENTS.md" ]]; then
  cp "$AGENT_ABS/AGENTS.md" "$OUTPUT_DIR/AGENTS.md"
  echo "    [2] AGENTS.md copiado desde AGENTS.md"
elif [[ -f "$AGENT_ABS/CLAUDE.md" ]]; then
  cp "$AGENT_ABS/CLAUDE.md" "$OUTPUT_DIR/AGENTS.md"
  echo "    [2] AGENTS.md copiado desde CLAUDE.md"
else
  echo "ERROR: no se encontró AGENTS.md ni CLAUDE.md en $AGENT_ABS" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Fase 3 — opencode.json
# ---------------------------------------------------------------------------
if [[ -f "$AGENT_ABS/opencode.json" ]]; then
  cp "$AGENT_ABS/opencode.json" "$OUTPUT_DIR/opencode.json"
  # Actualizar referencia a instrucciones: CLAUDE.md → AGENTS.md
  sed -i 's/"CLAUDE\.md"/"AGENTS.md"/g' "$OUTPUT_DIR/opencode.json"
  echo "    [3] opencode.json copiado (real) y actualizado"
else
  cat > "$OUTPUT_DIR/opencode.json" << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"],
  "mcp": {
    "sql": {
      "type": "remote",
      "url": "{env:MCP_SQL_URL}",
      "timeout": 90000,
      "headers": { "X-API-Key": "{env:MCP_SQL_API_KEY}" }
    }
  },
  "permission": {
    "read": "allow", "glob": "allow", "grep": "allow", "list": "allow",
    "lsp": "allow", "edit": "allow", "write": "allow",
    "todoread": "allow", "todowrite": "allow", "task": "allow",
    "skill": "allow", "webfetch": "allow",
    "sql_*": "deny",
    "sql_stratio_list_business_domains": "allow",
    "sql_stratio_list_technical_domains": "deny",
    "sql_stratio_list_domain_tables": "allow",
    "sql_stratio_get_tables_details": "allow",
    "sql_stratio_get_table_columns_details": "allow",
    "sql_stratio_generate_sql": "allow",
    "sql_stratio_query_data": "allow",
    "sql_stratio_search_domain_knowledge": "allow",
    "sql_stratio_execute_sql": "allow",
    "sql_stratio_profile_data": "allow",
    "sql_stratio_propose_knowledge": "allow",
    "bash": { "*": "allow" }
  }
}
EOF
  echo "    [3] opencode.json generado (template)"
fi

# ---------------------------------------------------------------------------
# Fase 4 — .opencode/ (NO se copia openwork.json — contiene rutas absolutas)
# ---------------------------------------------------------------------------
# El directorio .opencode/skills ya fue creado en Fase 1.
# openwork.json se excluye intencionalmente.
echo "    [4] .opencode/ preparado (openwork.json excluido)"

# ---------------------------------------------------------------------------
# Fase 5 — Skills (opcional)
# ---------------------------------------------------------------------------
SKILLS_SRC=""
if [[ -d "$AGENT_ABS/.opencode/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.opencode/skills"
elif [[ -d "$AGENT_ABS/.claude/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.claude/skills"
elif [[ -d "$AGENT_ABS/.agents/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/.agents/skills"
elif [[ -d "$AGENT_ABS/skills" ]]; then
  SKILLS_SRC="$AGENT_ABS/skills"
fi

if [[ -n "$SKILLS_SRC" ]]; then
  cp -r "$SKILLS_SRC/." "$OUTPUT_DIR/.opencode/skills/"
  # Normalizar: archivos .md sueltos → subcarpeta/SKILL.md
  for md_file in "$OUTPUT_DIR/.opencode/skills/"*.md; do
    [[ -f "$md_file" ]] || continue
    skill_name="$(basename "$md_file" .md)"
    mkdir -p "$OUTPUT_DIR/.opencode/skills/$skill_name"
    mv "$md_file" "$OUTPUT_DIR/.opencode/skills/$skill_name/SKILL.md"
  done
  N_SKILLS=$(find "$OUTPUT_DIR/.opencode/skills" -type f | wc -l)
  echo "    [5] $N_SKILLS skill(s) copiadas desde $SKILLS_SRC"
else
  echo "    [5] Sin skills (continuando sin error)"
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
  --exclude='pack_*.sh' \
  --exclude=output/ \
  --exclude=output-templates/ \
  --exclude=dist/ \
  --exclude=.venv/ \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude=.idea/ \
  --exclude=node_modules/ \
  "$AGENT_ABS/" "$OUTPUT_DIR/"
echo "    [6] rsync completado"

# ---------------------------------------------------------------------------
# Fase 7 — Reemplazos de texto (CLAUDE.md → AGENTS.md)
# Solo .md, .sh, .py, .txt — NO .json (opencode.json ya fue tratado)
# ---------------------------------------------------------------------------
find "$OUTPUT_DIR" \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' \
  -type f \( -name '*.md' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' \) \
  -exec sed -i 's/CLAUDE\.md/AGENTS.md/g' {} \;
echo "    [7] Reemplazos CLAUDE.md → AGENTS.md aplicados"

# ---------------------------------------------------------------------------
# Fase 8 — Verificación de integridad
# ---------------------------------------------------------------------------
echo "    [8] Verificando integridad..."
ERRORS=0

# AGENTS.md existe y no está vacío
if [[ ! -s "$OUTPUT_DIR/AGENTS.md" ]]; then
  echo "    ERROR: AGENTS.md no existe o está vacío" >&2
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
_validate_json "$OUTPUT_DIR/opencode.json"

# opencode.json contiene "AGENTS.md"
if ! grep -q '"AGENTS\.md"' "$OUTPUT_DIR/opencode.json" 2>/dev/null; then
  echo "    ERROR: opencode.json no contiene referencia a AGENTS.md" >&2
  ERRORS=$((ERRORS + 1))
fi

# 0 ficheros .json con referencia a "CLAUDE.md" en clave instructions
if grep -rl '"CLAUDE\.md"' "$OUTPUT_DIR" --include='*.json' 2>/dev/null | grep -q .; then
  echo "    ERROR: ficheros .json aún contienen referencia a \"CLAUDE.md\":" >&2
  grep -rl '"CLAUDE\.md"' "$OUTPUT_DIR" --include='*.json' 2>/dev/null >&2
  ERRORS=$((ERRORS + 1))
fi

# Ningún directorio prohibido
for FORBIDDEN in .claude; do
  if [[ -d "$OUTPUT_DIR/$FORBIDDEN" ]]; then
    echo "    ERROR: directorio prohibido encontrado: $FORBIDDEN" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# No debe haber .mcp.json
if [[ -f "$OUTPUT_DIR/.mcp.json" ]]; then
  echo "    ERROR: .mcp.json no debe estar presente en el output OpenCode" >&2
  ERRORS=$((ERRORS + 1))
fi

# Total de ficheros
TOTAL=$(find "$OUTPUT_DIR" -type f | wc -l)

if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FALLO: $ERRORS error(es) de verificación" >&2
  exit 1
fi

echo "==> OK — $TOTAL fichero(s) generados en $OUTPUT_DIR"
