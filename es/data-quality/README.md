# data-quality

Agente experto en Gobernanza y Calidad del Dato. Evalua la cobertura de calidad de datos gobernados, identifica gaps, propone y crea reglas de calidad con aprobación humana, y genera informes de cobertura.

## Capacidades

- Evaluación de cobertura de calidad por dominio, colección o tabla
- Identificación de gaps: dimensiones de calidad no cubiertas o tablas sin cobertura
- Propuesta razonada de reglas de calidad basada en contexto semántico y datos reales
- Creación de reglas de calidad con aprobación humana obligatoria
- Planificación de ejecución automática de reglas de calidad
- Generación de informes de cobertura (chat, PDF, DOCX, Markdown)

## Requisitos

- Python 3.10+ (dependencias en `requirements.txt`; instalar con `bash setup_env.sh`)
- Acceso a dos servidores MCP de Stratio:
  - `gov` (gobernanza): dimensiones de calidad, creación de reglas
  - `sql` (exploración): discovery, generación SQL, profiling, ejecución

La configuración de MCPs está en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer URL y credenciales desde variables de entorno.

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `MCP_SQL_URL` | URL del servidor MCP SQL de Stratio |
| `MCP_SQL_API_KEY` | API key del servidor MCP SQL |
| `MCP_GOV_URL` | URL del servidor MCP Governance de Stratio |
| `MCP_GOV_API_KEY` | API key del servidor MCP Governance |

## Skills

| Skill | Comando | Descripción |
|-------|---------|-------------|
| Evaluación de calidad | `/assess-quality` | Evaluar cobertura de calidad por dominio o tabla: dimensiones cubiertas, gaps y prioridades |
| Creación de reglas | `/create-quality-rules` | Diseñar y crear reglas de calidad para cubrir gaps, con aprobación humana obligatoria |
| Planificación de calidad | `/create-quality-schedule` | Crear planificaciones de ejecución automática de reglas de calidad por dominio/colección |
| Informe de calidad | `/quality-report` | Generar informe formal de cobertura en chat, PDF, DOCX o Markdown |
| Lectura de PDF | `/pdf-reader` | Extraer texto, tablas y datos de archivos PDF proporcionados por el usuario |
| Escritura de PDF | `/pdf-writer` | Crear PDFs personalizados, combinar/dividir, marca de agua, cifrar, rellenar formularios |

## Scripts de empaquetado

Todos los scripts aceptan `--lang <código>` para generar output en un idioma específico (ej: `--lang es` para español). Cuando se usa `--lang`, el output va a `dist/<lang>/...` en lugar de `dist/...`.

### Scripts específicos (desde esta carpeta)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<nombre>/` | `bash pack_claude_ai_project.sh --name data-quality` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<nombre>/` | `bash pack_claude_cowork.sh --name data-quality` |

El script de cowork acepta también `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>` y `--sql-key <KEY>` para configurar los dos servidores MCP. Si se omiten, quedan como variables de entorno template para configurar después.

### Scripts genéricos (desde la raíz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-quality` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-quality` |

## Quick start

```bash
# 1. Configurar variables de entorno
export MCP_SQL_URL="https://mi-servidor-sql.ejemplo.com/mcp"
export MCP_SQL_API_KEY="mi-api-key-sql"
export MCP_GOV_URL="https://mi-servidor-governance.ejemplo.com/mcp"
export MCP_GOV_API_KEY="mi-api-key-governance"

# 2. Instalar dependencias (para generación de informes PDF/DOCX)
bash setup_env.sh

# 3. Empaquetar para la plataforma deseada
bash ../pack_opencode.sh --agent data-quality
# o
bash ../pack_claude_code.sh --agent data-quality
```
