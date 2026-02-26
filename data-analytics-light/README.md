# data-analytics-light

Agente ligero de Business Intelligence y Business Analytics. Mismo motor analitico que `data-analytics`, pero orientado a conversacion: el output principal es el chat, sin generacion de informes formales.

## Capacidades

- Consulta de datos gobernados via MCP (servidor SQL de Stratio)
- Analisis avanzado con Python (pandas, numpy, scipy)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Output directo en chat con insights accionables

## Scripts de empaquetado

Todos los scripts son no-interactivos (CI/CD-friendly). Si no se pasa `--name`, usan `data-analytics-light` por defecto.

### Scripts especificos (desde esta carpeta)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_project.sh` | claude.ai (Projects) | `dist/claude_projects/<nombre>/` | `bash pack_claude_project.sh --name data-analytics-light` |
| `pack_claude_instructions.sh` | claude.ai (Custom Instructions) | `dist/claude_instructions/<nombre>/CLAUDE.md` | `bash pack_claude_instructions.sh --name data-analytics-light` |
| `pack_claude_plugin.sh` | Claude Code (Plugin) | `dist/claude_plugins/<nombre>/` | `bash pack_claude_plugin.sh --name data-analytics-light` |
| `pack_claude_marketplace.sh` | Claude Marketplace | `dist/claude_plugins/<nombre>/` | `bash pack_claude_marketplace.sh --name data-analytics-light` |

Los scripts de plugin y marketplace aceptan tambien `--url <MCP_URL>` y `--key <API_KEY>`. Si se omiten, quedan como variables de entorno template para configurar despues.

### Scripts genericos (desde la raiz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics-light` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics-light` |

### Empaquetado como Claude Plugin

Genera un ZIP listo para instalar como plugin en Claude Code. El paquete incluye las skills del agente y un fichero de agente (`agents/<nombre>.md`) con el contenido de `CLAUDE.md` como instrucciones, ademas de la configuracion MCP (`.mcp.json`). Las guias compartidas de `skills-guides/` se copian junto al `SKILL.md` de cada skill que las usa (patron de los plugins oficiales de Anthropic):

```bash
bash pack_claude_plugin.sh --name data-analytics-light --url https://mcp.ejemplo.com --key mi-api-key
```

El resultado se encuentra en `dist/claude_plugins/data-analytics-light/data-analytics-light.zip`.

### Empaquetado como Claude Marketplace

Genera un ZIP con el paquete completo: skills, agente y configuracion MCP. Las guias compartidas de `skills-guides/` se copian junto al `SKILL.md` de cada skill que las usa (mismo patron que el plugin):

```bash
bash pack_claude_marketplace.sh --name data-analytics-light --url https://mcp.ejemplo.com --key mi-api-key
```

El resultado se encuentra en `dist/claude_plugins/data-analytics-light-marketplace/data-analytics-light-marketplace.zip`.

### Empaquetado como Claude Project (claude.ai)

Genera los ficheros aplanados (skills, guias, requirements, setup) + un ZIP:

```bash
bash pack_claude_project.sh --name data-analytics-light
```

Para configurarlo en claude.ai:

1. Crear un nuevo **Project** en [claude.ai](https://claude.ai)
2. Abrir `dist/claude_projects/data-analytics-light/` y subir **todos los ficheros** (excepto `CLAUDE.md` y el ZIP) a la seccion de archivos del proyecto
3. Abrir `CLAUDE.md` del paquete generado, copiar **todo su contenido** y pegarlo en el campo **Instructions** del proyecto
4. Guardar el proyecto — el agente estara listo para usar

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
