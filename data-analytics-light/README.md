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
| `pack_claude_plugin.sh` | Claude Code (Plugin) | `dist/claude_plugins/<nombre>/` | `bash pack_claude_plugin.sh --name data-analytics-light --with-agent` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<nombre>/` | `bash pack_claude_cowork.sh --name data-analytics-light` |

Los scripts de plugin y cowork aceptan tambien `--url <MCP_URL>` y `--key <API_KEY>`. Si se omiten, quedan como variables de entorno template para configurar despues. El script de plugin acepta `--with-agent` para incluir el agente en el paquete y `--shared-guides` para colocar las guias en un directorio compartido en la raiz del plugin en vez de duplicarlas junto a cada skill (ver detalles abajo).

### Scripts genericos (desde la raiz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics-light` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics-light` |

### Empaquetado como Claude Plugin

Genera un ZIP listo para instalar como plugin en Claude Code. Las guias compartidas de `skills-guides/` se copian junto al `SKILL.md` de cada skill que las usa (patron de los plugins oficiales de Anthropic). El script soporta dos variantes:

- **Con agente** (`--with-agent`): Para Claude Code CLI. El paquete incluye `agents/<nombre>.md` (con `CLAUDE.md` como instrucciones) y `settings.json` — el agente del plugin toma el control como hilo principal. Funciona tambien en Cowork, pero reemplaza al orquestador (pierde la capacidad de coordinacion con otros plugins/agentes).
- **Sin agente** (default): Solo skills + MCP. Uso interno por `pack_claude_cowork.sh`, no se distribuye como entregable independiente porque las skills referencian secciones de CLAUDE.md.

```bash
# Plugin con agente (para Claude Code CLI)
bash pack_claude_plugin.sh --name data-analytics-light --with-agent --url https://mcp.ejemplo.com --key mi-api-key

# Plugin sin agente (uso interno por pack_claude_cowork.sh)
bash pack_claude_plugin.sh --name data-analytics-light
```

El resultado se encuentra en `dist/claude_plugins/data-analytics-light/data-analytics-light.zip`.

**Guias compartidas** (`--shared-guides`): Por defecto las guias de `skills-guides/` se duplican junto al `SKILL.md` de cada skill que las usa. Con `--shared-guides` se colocan en un directorio `skills-guides/` en la raiz del plugin y las skills las referencian con ruta relativa. Esto evita duplicacion pero depende de que Claude resuelva rutas relativas entre directorios del plugin.

### Empaquetado como Claude Cowork

Genera un paquete para configurar el agente en Claude Cowork sin reemplazar al orquestador. Contiene:

- `CLAUDE.md` — folder instructions con referencias actualizadas para el contexto del plugin
- `<nombre>.zip` — plugin ZIP (solo skills + MCP, sin agente)
- `<nombre>-cowork.zip` — ZIP final con ambos ficheros

```bash
bash pack_claude_cowork.sh --name data-analytics-light --url https://mcp.ejemplo.com --key mi-api-key
```

El resultado se encuentra en `dist/claude_cowork/data-analytics-light/`.

**Como usarlo en Cowork:**

1. Copiar `CLAUDE.md` al directorio de trabajo del proyecto en Cowork (actua como folder instructions)
2. Instalar el ZIP del plugin en Cowork (aporta las skills `/analyze`, `/explore-data`, `/propose-knowledge` y la conexion MCP)
3. El orquestador de Cowork lee las instrucciones de CLAUDE.md y delega a las skills del plugin cuando corresponda

**Diferencia con el plugin con agente:** En Cowork con agente, el plugin sustituye al orquestador — funciona como Claude Code CLI dentro de Cowork. Con el paquete Cowork, el orquestador mantiene el control y puede coordinar con otros plugins/agentes.

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
