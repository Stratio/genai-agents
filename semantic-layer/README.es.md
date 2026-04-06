# semantic-layer

Agente especializado en construccion y mantenimiento de capas semanticas en Stratio Data Governance.

## Capacidades

- Construccion de capas semanticas via MCPs de gobernanza (servidor `stratio_gov`)
- Exploracion de dominios tecnicos y capas semanticas publicadas (servidor `stratio_data`)
- Pipeline completo de 5 fases: terminos tecnicos → ontologia → vistas de negocio → SQL mappings → terminos semanticos
- Planificacion interactiva de ontologias (con lectura de ficheros locales .owl/.ttl, CSVs, documentos de negocio)
- Diagnostico de estado de la capa semantica de un dominio
- Gestion de business terms en el diccionario de gobernanza
- Creacion de colecciones de datos (dominios tecnicos) a partir de busquedas en el diccionario de datos

Este agente no ejecuta queries de datos, no genera ficheros en disco y no analiza datos — su output es interaccion con tools MCP de gobernanza + resumenes en chat.

## Requisitos

- Acceso a dos servidores MCP de Stratio:
  - `stratio_gov` (gobernanza): creacion y gestion de artefactos semanticos
  - `stratio_data` (exploración): consulta de dominios y diccionario de datos
- Variables de entorno: `MCP_GOV_URL`, `MCP_GOV_API_KEY`, `MCP_SQL_URL`, `MCP_SQL_API_KEY`
- Configuracion preconfigurada en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer la URL y credenciales desde variables de entorno

## Scripts de empaquetado

Todos los scripts son no-interactivos (CI/CD-friendly). Si no se pasa `--name`, usan `semantic-layer` por defecto.

### Scripts especificos (desde esta carpeta)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<nombre>/` | `bash pack_claude_ai_project.sh --name semantic-layer` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<nombre>/` | `bash pack_claude_cowork.sh --name semantic-layer` |

El script de cowork acepta tambien `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>` y `--sql-key <KEY>` para configurar los dos servidores MCP. Si se omiten, quedan como variables de entorno template para configurar despues.

### Scripts genericos (desde la raiz del monorepo)

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

¹ Generado (no copia directa): referencias `skills-guides/` → `skills/stratio-semantic-layer/`, placeholder `{{TOOL_PREGUNTAS}}` resuelto.
² Aplanadas en raiz: `build-semantic-layer.md`, `stratio-semantic-layer.md`, `generate-technical-terms.md`, etc.; guias prefijadas: `skills-guides_stratio-semantic-layer-tools.md`.
³ Guias renombradas con prefijo: `skills-guides_stratio-semantic-layer-tools.md`.
⁴ Guides dentro de cada skill (autocontenida) + en `skills-guides/` para referencias desde `CLAUDE.md`/`AGENTS.md`.

### Empaquetado como Claude Cowork

Genera un paquete para configurar el agente en Claude Cowork sin reemplazar al orquestador. El script construye el plugin internamente (skills + MCP, sin agente) y lo combina con las instrucciones del agente. Produce dos ficheros:

| Fichero | Que es | Para que sirve |
|---------|--------|----------------|
| `CLAUDE.md` | Folder instructions (generado desde AGENTS.md) | Instrucciones del agente — Cowork las lee automaticamente del directorio de trabajo |
| `<nombre>.zip` | Plugin ZIP (solo skills + MCP, sin agente) | Se instala como plugin en Cowork; aporta las skills y la conexion MCP |

> **Nota:** Los plugins de Claude no incluyen instrucciones de agente (CLAUDE.md) — solo skills, MCP y hooks. Por eso el `CLAUDE.md` va aparte, como fichero del directorio de trabajo.

```bash
bash pack_claude_cowork.sh --name semantic-layer --gov-url https://gov.ejemplo.com --sql-url https://sql.ejemplo.com
```

El resultado se encuentra en `dist/claude_cowork/semantic-layer/`.

**Como usarlo en Cowork:**

1. Copiar `CLAUDE.md` al directorio de trabajo del proyecto en Cowork — Cowork lo lee automaticamente como folder instructions
3. Instalar `<nombre>.zip` como plugin en Cowork (aporta las skills `/build-semantic-layer`, `/stratio-semantic-layer`, `/generate-technical-terms`, `/create-ontology`, `/create-business-views`, `/create-sql-mappings`, `/create-semantic-terms`, `/manage-business-terms`, `/create-data-collection` y la conexion MCP)
4. El orquestador de Cowork lee las instrucciones del `CLAUDE.md` y delega a las skills del plugin cuando corresponda

### Empaquetado como Claude AI Project (claude.ai)

Genera los ficheros aplanados (skills, guias):

```bash
bash pack_claude_ai_project.sh --name semantic-layer
```

Para configurarlo en claude.ai:

1. Crear un nuevo **Project** en [claude.ai](https://claude.ai)
2. Abrir `dist/claude_ai_projects/semantic-layer/` y subir **todos los ficheros** (excepto `CLAUDE.md`) a la seccion de archivos del proyecto
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
| Pipeline completo | `/build-semantic-layer` | local | Pipeline de 5 fases para construir la capa semantica de un dominio |
| Referencia MCP semantica | `/stratio-semantic-layer` | **shared** | Referencia de herramientas MCP de gobernanza: reglas, patrones y buenas practicas |
| Terminos tecnicos | `/generate-technical-terms` | **shared** | Generar descripciones tecnicas de tablas y columnas |
| Ontologia | `/create-ontology` | **shared** | Crear, ampliar o borrar clases de ontologia con planificacion interactiva |
| Vistas de negocio | `/create-business-views` | **shared** | Crear, regenerar o borrar vistas de negocio desde una ontologia |
| SQL Mappings | `/create-sql-mappings` | **shared** | Crear o actualizar SQL mappings para vistas existentes |
| Terminos semanticos | `/create-semantic-terms` | **shared** | Generar terminos semanticos de negocio para las vistas de un dominio |
| Business Terms | `/manage-business-terms` | **shared** | Crear Business Terms con relaciones a activos de datos |
| Coleccion de datos | `/create-data-collection` | **shared** | Buscar tablas en el diccionario y crear una nueva coleccion de datos |

Las skills marcadas como **shared** viven en `shared-skills/` en la raiz del monorepo y se comparten con otros agentes. La skill local vive en `skills/` de este agente.

**Nota**: Este agente no usa memoria persistente en ficheros ni genera ficheros en disco — el output principal es interaccion con tools MCP + resumenes en chat.
