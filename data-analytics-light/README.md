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

## Compatibilidad

Este agente funciona directamente sin empaquetar en:

- **Claude Code**: `claude .` desde esta carpeta. Lee `CLAUDE.md` y carga skills de `.claude/skills/` automaticamente.
- **OpenCode**: Abrir desde esta carpeta. `opencode.json` apunta a `CLAUDE.md` y reconoce `.claude/skills/`.

Los pack scripts solo son necesarios para distribuir el agente fuera del repositorio.

## Skills disponibles

| Skill | Comando | Descripcion |
|-------|---------|-------------|
| Analisis | `/analyze` | Analisis de datos BI/BA: descubrimiento de dominio, EDA, planificacion de KPIs, queries MCP, analisis Python y visualizaciones |
| Exploracion | `/explore-data` | Exploracion rapida de dominios, tablas, columnas y terminologia de negocio |
| Conocimiento | `/propose-knowledge` | Proponer terminos de negocio descubiertos a Stratio Governance |

**Nota**: Este agente no usa memoria persistente en ficheros — el output principal es el chat.

## Setup

```bash
bash setup_env.sh
```

## Uso

```bash
claude .
```
