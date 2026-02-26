# genai-agents — Monorepo

Monorepo con agentes de IA generativa para analisis de datos de negocio.

## Estructura

```
genai-agents/
  data-analytics/          # Agente completo (analisis + informes multi-formato)
  data-analytics-light/    # Agente ligero (analisis en chat)
```

## Instrucciones de desarrollo

- Cada agente tiene su propio `CLAUDE.md` con instrucciones especificas. Trabajar siempre desde la carpeta del agente correspondiente
- Skills de cada agente en `.claude/skills/`
- Scripts de empaquetado genericos en la raiz del monorepo: `pack_claude_code.sh` y `pack_opencode.sh` (cualquier agente)
- Scripts de empaquetado especificos de plataforma en `data-analytics-light/` (`pack_claude_project.sh`, `pack_claude_instructions.sh`, `pack_claude_plugin.sh`, `pack_claude_cowork.sh`)
- El `.gitignore` raiz cubre ambos agentes

## Resumen de agentes

### data-analytics
Agente completo de BI/BA: consulta de datos gobernados via MCP, analisis con Python (pandas, scipy, scikit-learn), visualizaciones (matplotlib, seaborn, plotly), generacion de informes (PDF, DOCX, web, PowerPoint), documentacion del razonamiento, validacion, gestion de la memoria entre sesiones.

### data-analytics-light
Agente ligero de BI/BA: mismo motor analitico pero orientado a conversacion. Sin generacion de informes formales — el output principal es el chat. Incluye scripts de empaquetado para Claude Projects, Claude Instructions, Claude Plugin y Claude Cowork.

## Scripts de empaquetado (raiz)

Scripts genericos que funcionan con cualquier agente del monorepo:

| Script | Plataforma destino | Output |
|--------|-------------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agente}/claude_code/{nombre}/` |
| `pack_opencode.sh` | OpenCode | `{agente}/opencode/{nombre}/` |

Uso: `bash pack_claude_code.sh --agent <ruta-agente> [--name <nombre-kebab>]`
