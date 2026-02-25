# genai-agents

Coleccion de agentes de IA generativa para analisis de datos de negocio. Compatibles con **Claude Code**, **Claude Cowork**, **claude.ai**, **OpenCode**, **OpenWork** y herramientas compatibles con MCP.

## Agentes

| Agente | Descripcion | Plataformas | Carpeta |
|--------|-------------|-------------|---------|
| **data-analytics** | Agente completo de BI/BA con analisis avanzado, clustering, informes multi-formato (PDF, DOCX, web, PowerPoint) y documentacion del razonamiento | Claude Code, OpenCode, OpenWork | `data-analytics/` |
| **data-analytics-light** | Agente ligero de BI/BA orientado a analisis en chat, sin generacion de informes formales. Incluye scripts de empaquetado para multiples plataformas | Claude Code, Claude Cowork, claude.ai, OpenCode | `data-analytics-light/` |

## Empaquetado

Scripts en la raiz del monorepo para empaquetar cualquier agente en el formato de la plataforma destino:

| Script | Plataforma destino | Output |
|--------|-------------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agente}/dist/claude_code/{nombre}/` |
| `pack_opencode.sh` | OpenCode | `{agente}/dist/opencode/{nombre}/` |

```bash
# Empaquetar data-analytics para Claude Code
bash pack_claude_code.sh --agent data-analytics

# Empaquetar data-analytics para OpenCode con nombre personalizado
bash pack_opencode.sh --agent data-analytics --name mi-agente
```

El nombre debe ser kebab-case. Si se omite, se usa el basename del directorio del agente. Los directorios generados estan excluidos del repositorio (`.gitignore`).

`data-analytics-light` incluye ademas scripts especificos para otras plataformas (Claude Projects, claude.ai, Claude Plugin, Claude Marketplace) — ver su propio `README.md`.

### Estructura de outputs (`make package`)

Todos los artefactos se generan bajo `dist/`, tanto a nivel de agente (intermedios) como en la raiz (zips finales versionados):

```
genai-agents/
  dist/                                         # ZIPs finales versionados
    data-analytics-claude-code-{v}.zip
    data-analytics-opencode-{v}.zip
    data-analytics-light-claude-code-{v}.zip
    data-analytics-light-opencode-{v}.zip
    data-analytics-light-claude-plugin-{v}.zip
    data-analytics-light-claude-marketplace-{v}.zip
    data-analytics-light-claude-project-{v}.zip
    data-analytics-light-claude-instructions-{v}.zip
    genai-agents-{v}.zip                        # ZIP global con todos los anteriores

  data-analytics/
    dist/                                       # Artefactos intermedios
      claude_code/data-analytics/
      opencode/data-analytics/

  data-analytics-light/
    dist/                                       # Artefactos intermedios
      claude_code/data-analytics-light/
      opencode/data-analytics-light/
      claude_plugins/data-analytics-light/
      claude_plugins/data-analytics-light-marketplace/
      claude_projects/data-analytics-light/
      claude_instructions/data-analytics-light/
```

`make clean` elimina todos los `dist/` (raiz + agentes).

## Requisitos comunes

- Python 3.10+
- Acceso a un servidor MCP de Stratio (configurado en `.mcp.json` de cada agente)

## Setup

Cada agente tiene su propio entorno virtual y dependencias. Desde la carpeta de cada agente:

```bash
cd data-analytics/    # o data-analytics-light/
bash setup_env.sh
```

Esto crea un `.venv/` local con las dependencias definidas en `requirements.txt`.
