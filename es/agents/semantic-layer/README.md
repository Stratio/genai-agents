# semantic-layer

Agente especializado en construcción y mantenimiento de capas semánticas en Stratio Data Governance.

## Capacidades

- Construcción de capas semánticas vía MCPs de gobernanza (servidor `stratio_gov`)
- Exploración de dominios técnicos y capas semánticas publicadas (servidor `stratio_data`)
- Pipeline completo de 5 fases: términos técnicos → ontología → vistas de negocio → SQL mappings → términos semánticos
- Planificación interactiva de ontologías (con lectura de ficheros locales .owl/.ttl, CSVs, documentos de negocio)
- Diagnóstico de estado de la capa semántica de un dominio
- Gestión de business terms en el diccionario de gobernanza
- Creación de colecciones de datos (dominios técnicos) a partir de busquedas en el diccionario de datos
- Validación de datos de solo lectura: validación con datos de muestra de la SQL del mapping antes de publicar, y sanity-checks del `semantic_<domain>` publicado con `query_data` / `generate_sql` / `execute_sql`

Este agente ejecuta queries de datos de solo lectura (`query_data`, `generate_sql`, `execute_sql`) para validación y sanity checks. No ejecuta `profile_data`, no genera ficheros en disco y no analiza datos — su output principal es interacción con tools MCP de gobernanza + resúmenes en chat.

## Requisitos

- Acceso a dos servidores MCP de Stratio:
  - `stratio_gov` (gobernanza): creación y gestión de artefactos semánticos
  - `stratio_data` (exploración): consulta de dominios y diccionario de datos
- Variables de entorno: `MCP_GOV_URL`, `MCP_GOV_API_KEY`, `MCP_SQL_URL`, `MCP_SQL_API_KEY`
- Configuración preconfigurada en `opencode.json` (OpenCode), preconfigurado para leer la URL y credenciales desde variables de entorno. El fichero `mcps` en la raíz del agente lista los nombres de MCP que se registran al desplegar el bundle `agents/v1` en Stratio Cowork

## Scripts de empaquetado

Todos los scripts son no-interactivos (CI/CD-friendly). Si no se pasa `--name`, usan `semantic-layer` por defecto. Todos los scripts aceptan `--lang <código>` para generar output en un idioma específico (ej: `--lang es` para español). Cuando se usa `--lang`, el output va a `dist/<lang>/...` en lugar de `dist/...`.

| Script | Destino | Output | Ejemplo |
|--------|---------|--------|---------|
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent semantic-layer` |
| `pack_stratio_cowork.sh` | Stratio Cowork (`agents/v1`) | `dist/<nombre>-stratio-cowork.zip` | `bash ../pack_stratio_cowork.sh --agent semantic-layer` |

## Compatibilidad

- **OpenCode**: Empaquetar con `pack_opencode.sh` para usar con OpenCode.
- **Stratio Cowork**: Empaquetar con `pack_stratio_cowork.sh` y desplegar vía la skill compartida `cowork-api` (o como parte del plugin `stratio-governance`).

## Skills disponibles

| Skill | Comando | Descripción |
|-------|---------|-------------|
| Pipeline completo | `/build-semantic-layer` | Pipeline de 5 fases para construir la capa semántica de un dominio |
| Referencia MCP semántica | `/stratio-semantic-layer` | Referencia de herramientas MCP de gobernanza: reglas, patrones y buenas prácticas |
| Términos técnicos | `/create-technical-terms` | Crear descripciones técnicas de tablas y columnas |
| Ontología | `/create-ontology` | Crear, ampliar o borrar clases de ontología con planificación interactiva |
| Vistas de negocio | `/create-business-views` | Crear, regenerar o borrar vistas de negocio desde una ontología |
| SQL Mappings | `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas existentes |
| Términos semánticos | `/create-semantic-terms` | Generar términos semánticos de negocio para las vistas de un dominio |
| Business Terms | `/manage-business-terms` | Crear Business Terms con relaciones a activos de datos |
| Colección de datos | `/create-data-collection` | Buscar tablas en el diccionario y crear una nueva colección de datos |

Todas las skills viven en `skills/` en la raíz del monorepo y se comparten con el agente data-governance-officer.

**Nota**: Este agente no genera ficheros en disco — el output principal es interacción con tools MCP + resúmenes en chat.
