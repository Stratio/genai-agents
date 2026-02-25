# data-analytics-light

Agente ligero de Business Intelligence y Business Analytics. Mismo motor analitico que `data-analytics`, pero orientado a conversacion: el output principal es el chat, sin generacion de informes formales.

## Capacidades

- Consulta de datos gobernados via MCP (servidor SQL de Stratio)
- Analisis avanzado con Python (pandas, numpy, scipy)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Output directo en chat con insights accionables

## Scripts de empaquetado

Scripts especificos de este agente (desde esta carpeta):

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_project.sh` | claude.ai (Projects) | `claude_projects/<nombre>/` | `bash pack_claude_project.sh` |
| `pack_claude_instructions.sh` | claude.ai (Custom Instructions) | `claude_instructions/<nombre>/CLAUDE.md` | `bash pack_claude_instructions.sh` |
| `pack_claude_plugin.sh` | Claude Code (Plugin) | `claude_plugins/<nombre>/` | `bash pack_claude_plugin.sh` |
| `pack_claude_marketplace.sh` | Claude Marketplace | `claude_plugins/<nombre>/` | `bash pack_claude_marketplace.sh` |

Scripts genericos en la raiz del monorepo (desde `../`):

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics-light` |
| `pack_opencode.sh` | OpenCode | `opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics-light` |

## Setup

```bash
bash setup_env.sh
```

## Uso

Abrir Claude Code desde esta carpeta, o empaquetar para la plataforma deseada con el script correspondiente.
