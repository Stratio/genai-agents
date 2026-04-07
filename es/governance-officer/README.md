# governance-officer

Agente governance officer que combina la construccion de capas semanticas y la gestion de calidad del dato. Orquesta el ciclo de vida completo de los artefactos de gobierno: ontologias, vistas, mappings, terminos, reglas de calidad e informes de cobertura.

## Capacidades

### Capa semantica
- Construccion y mantenimiento de capas semanticas via MCPs de gobierno
- Publicacion de business views (Draft → Pending Publish)
- Exploracion de dominios tecnicos y capas semanticas publicadas
- Planificacion interactiva de ontologias con lectura de ficheros locales
- Creacion de data collections a partir de busquedas en el diccionario de datos
- Gestion de business terms en el diccionario de gobierno

### Calidad del dato
- Evaluacion de cobertura de calidad por dominio, coleccion, tabla o columna
- Identificacion de gaps: dimensiones de calidad no cubiertas
- Propuesta razonada de reglas de calidad basada en contexto semantico y datos reales
- Creacion de reglas de calidad con aprobacion humana obligatoria
- Planificacion de ejecucion automatica de reglas de calidad
- Generacion de informes de cobertura (chat, PDF, DOCX, Markdown)

## Requisitos

- Python 3.10+ (dependencias en `requirements.txt`; instalar con `bash setup_env.sh`)
- Acceso a dos servidores MCP de Stratio:
  - `gov` (gobierno): herramientas de capa semantica, dimensiones de calidad, creacion de reglas
  - `sql` (exploracion): descubrimiento, generacion SQL, profiling, ejecucion

La configuracion MCP esta en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer URL y credenciales de variables de entorno.

## Variables de entorno

| Variable | Descripcion |
|----------|-------------|
| `MCP_SQL_URL` | URL del servidor MCP SQL de Stratio |
| `MCP_SQL_API_KEY` | API key del servidor MCP SQL |
| `MCP_GOV_URL` | URL del servidor MCP de Gobierno de Stratio |
| `MCP_GOV_API_KEY` | API key del servidor MCP de Gobierno |

## Skills

| Skill | Comando | Descripcion |
|-------|---------|-------------|
| Pipeline completo | `/build-semantic-layer` | Construir capa semantica completa: terminos, ontologia, vistas, mappings, terminos semanticos |
| Terminos tecnicos | `/generate-technical-terms` | Generar descripciones tecnicas para tablas y columnas |
| Ontologia | `/create-ontology` | Crear, extender o eliminar clases de ontologia |
| Business views | `/create-business-views` | Crear, regenerar o eliminar business views |
| SQL mappings | `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas |
| Terminos semanticos | `/create-semantic-terms` | Generar terminos semanticos de negocio |
| Business terms | `/manage-business-terms` | Crear business terms en el diccionario de gobierno |
| Data collection | `/create-data-collection` | Buscar y crear nuevos dominios tecnicos |
| Evaluacion de calidad | `/assess-quality` | Evaluar la cobertura de calidad por dominio o tabla |
| Creacion de reglas | `/create-quality-rules` | Disenar y crear reglas de calidad con aprobacion humana |
| Planificacion de calidad | `/create-quality-planification` | Crear planificaciones de ejecucion automatica |
| Informe de calidad | `/quality-report` | Generar informe formal de cobertura (PDF, DOCX, Markdown) |

## Scripts de empaquetado

Todos los scripts aceptan `--lang <code>` para generar la salida en un idioma especifico (ej. `--lang es` para espanol). Cuando se usa `--lang`, la salida va a `dist/<lang>/...` en lugar de `dist/...`.

### Scripts especificos (desde esta carpeta)

| Script | Plataforma destino | Salida | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<name>/` | `bash pack_claude_ai_project.sh --name governance-officer` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<name>/` | `bash pack_claude_cowork.sh --name governance-officer` |

El script de cowork tambien acepta `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>` y `--sql-key <KEY>` para configurar los dos servidores MCP. Si se omiten, permanecen como plantillas de variables de entorno para configurar posteriormente.

### Scripts genericos (desde la raiz del monorepo)

| Script | Plataforma destino | Salida | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent governance-officer` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent governance-officer` |

## Inicio rapido

```bash
# 1. Configurar variables de entorno
export MCP_SQL_URL="https://my-sql-server.example.com/mcp"
export MCP_SQL_API_KEY="my-sql-api-key"
export MCP_GOV_URL="https://my-governance-server.example.com/mcp"
export MCP_GOV_API_KEY="my-governance-api-key"

# 2. Instalar dependencias (para generacion de informes PDF/DOCX)
bash setup_env.sh

# 3. Empaquetar para la plataforma deseada
bash ../pack_opencode.sh --agent governance-officer
# o
bash ../pack_claude_code.sh --agent governance-officer
```
