# data-analytics

Agente completo de Business Intelligence y Business Analytics para Claude Code y OpenCode.

## Capacidades

- Consulta de datos gobernados via MCP (servidor SQL de Stratio)
- Analisis avanzado con Python (pandas, numpy, scipy)
- Segmentacion y clustering (scikit-learn)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Generacion de informes multi-formato: PDF, DOCX, web interactiva, PowerPoint
- Documentacion del razonamiento y validacion de output
- Memoria persistente de analisis y preferencias

## Scripts de empaquetado

Scripts genericos en la raiz del monorepo (desde `../`):

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics` |
| `pack_opencode.sh` | OpenCode | `opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics` |

## Setup

```bash
bash setup_env.sh
```

## Uso

Abrir Claude Code o OpenCode desde esta carpeta. El agente leera `CLAUDE.md` y las skills en `.claude/skills/` automaticamente.

```bash
claude .
```
