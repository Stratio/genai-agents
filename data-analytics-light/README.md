# data-analytics-light

Agente ligero de Business Intelligence y Business Analytics. Mismo motor analitico que `data-analytics`, pero orientado a conversacion: el output principal es el chat, sin generacion de informes formales.

## Capacidades

- Consulta de datos gobernados via MCP (servidor SQL de Stratio)
- Analisis avanzado con Python (pandas, numpy, scipy)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Output directo en chat con insights accionables

## Requisitos

- Python 3.10+ (dependencias en `requirements.txt`; instalar con `bash setup_env.sh`)
- Acceso a un servidor MCP de Stratio. La configuracion esta en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer la URL y credenciales desde variables de entorno

## Scripts de empaquetado

Todos los scripts son no-interactivos (CI/CD-friendly). Si no se pasa `--name`, usan `data-analytics-light` por defecto.

### Scripts especificos (desde esta carpeta)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<nombre>/` | `bash pack_claude_ai_project.sh --name data-analytics-light` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<nombre>/` | `bash pack_claude_cowork.sh --name data-analytics-light` |

El script de cowork acepta tambien `--url <MCP_URL>` y `--key <API_KEY>`. Si se omiten, quedan como variables de entorno template para configurar despues.

### Scripts genericos (desde la raiz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics-light` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics-light` |

### Ficheros incluidos por paquete

| Fichero fuente | `claude_ai_project` | `claude_cowork` | `claude_code` | `opencode` |
|---|---|---|---|---|
| `AGENTS.md` | ✅ → `CLAUDE.md` | ✅ → `CLAUDE.md`¹ | ✅ → `CLAUDE.md` | ✅ → `AGENTS.md` |
| `requirements.txt` | ✅ | ❌ | ✅ | ✅ |
| `setup_env.sh` | ✅ | ❌ | ✅ | ✅ |
| `skills/` | ✅² | ✅ (en ZIP) | ✅ (en `.claude/skills/`) | ✅ (en `.opencode/skills/`) |
| `skills-guides/` | ✅³ | ✅ (en ZIP) | ✅⁴ | ✅⁴ |
| `.mcp.json` | ❌ | ✅ (en ZIP) | ✅ | ❌ |
| `opencode.json` | ❌ | ❌ | ❌ | ✅ |
| `plugin.json` | ❌ | ✅ (en ZIP) | ❌ | ❌ |
| `.claude/settings.local.json` | ❌ | ❌ | ✅ | ❌ |

¹ Generado (no copia directa): referencias `skills-guides/` → `skills/analyze/`, placeholder `{{TOOL_PREGUNTAS}}` resuelto.
² Aplanadas en raíz: `analyze.md`, `analyze_*.md`, `explore-data.md`, `propose-knowledge.md`; guías prefijadas: `skills-guides_stratio-data-tools.md`.
³ Guías renombradas con prefijo: `skills-guides_stratio-data-tools.md`.
⁴ Guides dentro de cada skill (autocontenida) + en `skills-guides/` para referencias desde `CLAUDE.md`/`AGENTS.md`.

### Empaquetado como Claude Cowork

Genera un paquete para configurar el agente en Claude Cowork sin reemplazar al orquestador. El script construye el plugin internamente (skills + MCP, sin agente) y lo combina con las instrucciones del agente. Produce dos ficheros:

| Fichero | Que es | Para que sirve |
|---------|--------|----------------|
| `CLAUDE.md` | Folder instructions (generado desde AGENTS.md) | Instrucciones del agente — Cowork las lee automaticamente del directorio de trabajo |
| `<nombre>.zip` | Plugin ZIP (solo skills + MCP, sin agente) | Se instala como plugin en Cowork; aporta las skills y la conexion MCP |

> **Nota:** Los plugins de Claude no incluyen instrucciones de agente (CLAUDE.md) — solo skills, MCP y hooks. Por eso el `CLAUDE.md` va aparte, como fichero del directorio de trabajo.

```bash
bash pack_claude_cowork.sh --name data-analytics-light --url https://mcp.ejemplo.com --key mi-api-key
```

El resultado se encuentra en `dist/claude_cowork/data-analytics-light/`.

**Como usarlo en Cowork:**

1. Copiar `CLAUDE.md` al directorio de trabajo del proyecto en Cowork — Cowork lo lee automaticamente como folder instructions
3. Instalar `<nombre>.zip` como plugin en Cowork (aporta las skills `/analyze`, `/explore-data`, `/propose-knowledge` y la conexion MCP)
4. El orquestador de Cowork lee las instrucciones del `CLAUDE.md` y delega a las skills del plugin cuando corresponda

### Empaquetado como Claude AI Project (claude.ai)

Genera los ficheros aplanados (skills, guias, requirements, setup):

```bash
bash pack_claude_ai_project.sh --name data-analytics-light
```

Para configurarlo en claude.ai:

1. Crear un nuevo **Project** en [claude.ai](https://claude.ai)
2. Abrir `dist/claude_ai_projects/data-analytics-light/` y subir **todos los ficheros** (excepto `CLAUDE.md`) a la seccion de archivos del proyecto
3. Abrir `CLAUDE.md` del paquete generado, copiar **todo su contenido** y pegarlo en el campo **Instructions** del proyecto
4. Guardar el proyecto — el agente estara listo para usar

## Compatibilidad

Para usar con cualquier plataforma, empaquetar con el script correspondiente:

- **Claude Code**: Empaquetar con `pack_claude_code.sh` para usar con Claude Code.
- **OpenCode**: Empaquetar con `pack_opencode.sh` para usar con OpenCode.

Los pack scripts generan el formato correcto para cada plataforma (renombrando ficheros, reubicando skills, etc.).

## Skills disponibles

| Skill | Comando | Origen | Descripcion |
|-------|---------|--------|-------------|
| Analisis | `/analyze` | local | Analisis de datos BI/BA: descubrimiento de dominio, EDA, planificacion de KPIs, queries MCP, analisis Python y visualizaciones |
| Exploracion | `/explore-data` | **shared** | Exploracion rapida de dominios, tablas, columnas y terminologia de negocio |
| Conocimiento | `/propose-knowledge` | **shared** | Proponer terminos de negocio descubiertos a Stratio Governance |

Las skills marcadas como **shared** viven en `shared-skills/` en la raiz del monorepo y se comparten con `data-analytics`. Las locales viven en `skills/` de este agente.

**Nota**: Este agente no usa memoria persistente en ficheros — el output principal es el chat.
