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

Este agente no ejecuta queries de datos, no genera ficheros en disco y no analiza datos — su output es interacción con tools MCP de gobernanza + resúmenes en chat.

## Requisitos

- Acceso a dos servidores MCP de Stratio:
  - `stratio_gov` (gobernanza): creación y gestión de artefactos semánticos
  - `stratio_data` (exploración): consulta de dominios y diccionario de datos
- Variables de entorno: `MCP_GOV_URL`, `MCP_GOV_API_KEY`, `MCP_SQL_URL`, `MCP_SQL_API_KEY`
- Configuración preconfigurada en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer la URL y credenciales desde variables de entorno

## Scripts de empaquetado

Todos los scripts son no-interactivos (CI/CD-friendly). Si no se pasa `--name`, usan `semantic-layer` por defecto. Todos los scripts aceptan `--lang <código>` para generar output en un idioma específico (ej: `--lang es` para español). Cuando se usa `--lang`, el output va a `dist/<lang>/...` en lugar de `dist/...`.

### Scripts específicos (desde esta carpeta)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<nombre>/` | `bash pack_claude_ai_project.sh --name semantic-layer` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<nombre>/` | `bash pack_claude_cowork.sh --name semantic-layer` |

El script de cowork acepta también `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>` y `--sql-key <KEY>` para configurar los dos servidores MCP. Si se omiten, quedan como variables de entorno template para configurar después.

### Scripts genéricos (desde la raíz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent semantic-layer` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent semantic-layer` |

### Ficheros incluidos por paquete

| Fichero fuente | `claude_ai_project` | `claude_cowork` | `claude_code` | `opencode` |
|---|---|---|---|---|
| `AGENTS.md` | ✅ → `CLAUDE.md` | ✅ → `CLAUDE.md`¹ | ✅ → `CLAUDE.md` | ✅ → `AGENTS.md` |
| `skills/` | ✅² | ✅ (en ZIP) | ✅ (en `.claude/skills/`) | ✅ (en `.opencode/skills/`) |
| `skills-guides/` | ✅³ | ✅ (en ZIP) | ✅⁴ | ✅⁴ |
| `.mcp.json` | ❌ | ✅ (en ZIP) | ✅ | ❌ |
| `opencode.json` | ❌ | ❌ | ❌ | ✅ |
| `plugin.json` | ❌ | ✅ (en ZIP) | ❌ | ❌ |
| `.claude/settings.local.json` | ❌ | ❌ | ✅ | ❌ |

¹ Generado (no copia directa): referencias `skills-guides/` → `skills/stratio-semantic-layer/`, placeholder `{{TOOL_QUESTIONS}}` resuelto.
² Aplanadas en raíz: `build-semantic-layer.md`, `stratio-semantic-layer.md`, `generate-technical-terms.md`, etc.; guías prefijadas: `skills-guides_stratio-semantic-layer-tools.md`.
³ Guías renombradas con prefijo: `skills-guides_stratio-semantic-layer-tools.md`.
⁴ Guides dentro de cada skill (autocontenida) + en `skills-guides/` para referencias desde `CLAUDE.md`/`AGENTS.md`.

### Empaquetado como Claude Cowork

Genera un paquete para configurar el agente en Claude Cowork sin reemplazar al orquestador. El script construye el plugin internamente (skills + MCP, sin agente) y lo combina con las instrucciones del agente. Produce dos ficheros:

| Fichero | Qué es | Para que sirve |
|---------|--------|----------------|
| `CLAUDE.md` | Folder instructions (generado desde AGENTS.md) | Instrucciones del agente — Cowork las lee automáticamente del directorio de trabajo |
| `<nombre>.zip` | Plugin ZIP (solo skills + MCP, sin agente) | Se instala como plugin en Cowork; aporta las skills y la conexión MCP |

> **Nota:** Los plugins de Claude no incluyen instrucciones de agente (CLAUDE.md) — solo skills, MCP y hooks. Por eso el `CLAUDE.md` va aparte, como fichero del directorio de trabajo.

```bash
bash pack_claude_cowork.sh --name semantic-layer --gov-url https://gov.ejemplo.com --sql-url https://sql.ejemplo.com
```

El resultado se encuentra en `dist/claude_cowork/semantic-layer/`.

**Cómo usarlo en Cowork:**

1. Copiar `CLAUDE.md` al directorio de trabajo del proyecto en Cowork — Cowork lo lee automáticamente como folder instructions
3. Instalar `<nombre>.zip` como plugin en Cowork (aporta las skills `/build-semantic-layer`, `/stratio-semantic-layer`, `/generate-technical-terms`, `/create-ontology`, `/create-business-views`, `/create-sql-mappings`, `/create-semantic-terms`, `/manage-business-terms`, `/create-data-collection` y la conexión MCP)
4. El orquestador de Cowork lee las instrucciones del `CLAUDE.md` y delega a las skills del plugin cuando corresponda

### Empaquetado como Claude AI Project (claude.ai)

Genera los ficheros aplanados (skills, guías):

```bash
bash pack_claude_ai_project.sh --name semantic-layer
```

Para configurarlo en claude.ai:

1. Crear un nuevo **Project** en [claude.ai](https://claude.ai)
2. Abrir `dist/claude_ai_projects/semantic-layer/` y subir **todos los ficheros** (excepto `CLAUDE.md`) a la sección de archivos del proyecto
3. Abrir `CLAUDE.md` del paquete generado, copiar **todo su contenido** y pegarlo en el campo **Instructions** del proyecto
4. Guardar el proyecto — el agente estará listo para usar

## Compatibilidad

Para usar con cualquier plataforma, empaquetar con el script correspondiente:

- **Claude Code**: Empaquetar con `pack_claude_code.sh` para usar con Claude Code.
- **OpenCode**: Empaquetar con `pack_opencode.sh` para usar con OpenCode.

Los pack scripts generan el formato correcto para cada plataforma (renombrando ficheros, reubicando skills, etc.).

## Skills disponibles

| Skill | Comando | Descripción |
|-------|---------|-------------|
| Pipeline completo | `/build-semantic-layer` | Pipeline de 5 fases para construir la capa semántica de un dominio |
| Referencia MCP semántica | `/stratio-semantic-layer` | Referencia de herramientas MCP de gobernanza: reglas, patrones y buenas prácticas |
| Términos técnicos | `/generate-technical-terms` | Generar descripciones técnicas de tablas y columnas |
| Ontología | `/create-ontology` | Crear, ampliar o borrar clases de ontología con planificación interactiva |
| Vistas de negocio | `/create-business-views` | Crear, regenerar o borrar vistas de negocio desde una ontología |
| SQL Mappings | `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas existentes |
| Términos semánticos | `/create-semantic-terms` | Generar términos semánticos de negocio para las vistas de un dominio |
| Business Terms | `/manage-business-terms` | Crear Business Terms con relaciones a activos de datos |
| Colección de datos | `/create-data-collection` | Buscar tablas en el diccionario y crear una nueva colección de datos |

Todas las skills viven en `shared-skills/` en la raíz del monorepo y se comparten con el agente governance-officer.

**Nota**: Este agente no usa memoria persistente en ficheros ni genera ficheros en disco — el output principal es interacción con tools MCP + resúmenes en chat.
