#!/usr/bin/env bash
# compile.sh — Validacion ligera del monorepo
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0

echo "==> Validando estructura del monorepo..."

# --- Comprobar ficheros raiz obligatorios ---
for f in VERSION LICENSE.txt CHANGELOG.md; do
  if [[ ! -f "$REPO_ROOT/$f" ]]; then
    echo "ERROR: Falta fichero raiz: $f" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# --- Comprobar que cada modulo en release-modules existe ---
if [[ ! -f "$REPO_ROOT/release-modules" ]]; then
  echo "ERROR: Falta fichero release-modules" >&2
  ERRORS=$((ERRORS + 1))
else
  while IFS= read -r module; do
    [[ -z "$module" || "$module" =~ ^# ]] && continue
    if [[ ! -d "$REPO_ROOT/$module" ]]; then
      echo "ERROR: Modulo '$module' listado en release-modules pero no existe como directorio" >&2
      ERRORS=$((ERRORS + 1))
    else
      echo "  [OK] Modulo: $module"
      # Validar JSON si existen ficheros .json o .mcp.json
      for json_file in $(find "$REPO_ROOT/$module" -maxdepth 2 \( -name '*.json' -o -name '.mcp.json' \) -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/claude_code/*' -not -path '*/opencode/*' -not -path '*/claude_plugins/*' -not -path '*/claude_projects/*' -not -path '*/claude_instructions/*' 2>/dev/null); do
        if command -v python3 &>/dev/null; then
          if ! python3 -c "import json; json.load(open('$json_file'))" 2>/dev/null; then
            echo "  WARN: JSON invalido (o contiene templates): $(basename "$json_file") en $module"
          fi
        fi
      done
    fi
  done < "$REPO_ROOT/release-modules"
fi

# --- Validar sintaxis bash de scripts pack_*.sh y bin/*.sh ---
echo "==> Validando sintaxis de scripts bash..."
for script in "$REPO_ROOT"/pack_*.sh "$REPO_ROOT"/data-analytics-light/pack_*.sh "$REPO_ROOT"/bin/*.sh; do
  [[ ! -f "$script" ]] && continue
  if bash -n "$script" 2>/dev/null; then
    echo "  [OK] $(basename "$script")"
  else
    echo "  ERROR: Sintaxis invalida: $script" >&2
    ERRORS=$((ERRORS + 1))
  fi
done

# --- Resultado ---
if [[ "$ERRORS" -gt 0 ]]; then
  echo "==> FALLO: $ERRORS error(es) de validacion" >&2
  exit 1
fi

echo "==> Compilacion OK — estructura valida"
