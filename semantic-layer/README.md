# semantic-layer

Agente especializado en construccion y mantenimiento de capas semanticas en Stratio Data Governance.

## Capacidades

- Construccion de capas semanticas via MCPs de gobernanza (servidor `gov`)
- Exploracion de dominios tecnicos y capas semanticas publicadas (servidor `sql`)
- Pipeline completo de 5 fases: terminos tecnicos → ontologia → vistas de negocio → SQL mappings → terminos semanticos
- Planificacion interactiva de ontologias (con lectura de ficheros locales .owl/.ttl, CSVs, documentos de negocio)
- Diagnostico de estado de la capa semantica de un dominio
- Gestion de business terms en el diccionario de gobernanza
- Creacion de colecciones de datos (dominios tecnicos) a partir de busquedas en el diccionario de datos

Este agente no ejecuta queries de datos, no genera ficheros en disco y no analiza datos — su output es interaccion con tools MCP de gobernanza + resumenes en chat.

## Requisitos

- Acceso a dos servidores MCP de Stratio:
  - `gov` (gobernanza): creacion y gestion de artefactos semanticos
  - `sql` (exploracion): consulta de dominios y diccionario de datos
- Variables de entorno: `MCP_GOV_URL`, `MCP_GOV_API_KEY`, `MCP_SQL_URL`, `MCP_SQL_API_KEY`
- Configuracion preconfigurada en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer la URL y credenciales desde variables de entorno

## Scripts de empaquetado

Todos los scripts son no-interactivos (CI/CD-friendly). Si no se pasa `--name`, usan `semantic-layer` por defecto.

### Scripts especificos (desde esta carpeta)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_project.sh` | claude.ai (Projects) | `dist/claude_projects/<nombre>/` | `bash pack_claude_project.sh --name semantic-layer` |
| `pack_claude_plugin.sh` | Claude Code (Plugin) | `dist/claude_plugins/<nombre>/` | `bash pack_claude_plugin.sh --name semantic-layer --with-agent` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<nombre>/` | `bash pack_claude_cowork.sh --name semantic-layer` |

Los scripts de plugin y cowork aceptan tambien `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>` y `--sql-key <KEY>` para configurar los dos servidores MCP. Si se omiten, quedan como variables de entorno template para configurar despues. El script de plugin acepta `--with-agent` para incluir el agente en el paquete y `--shared-guides` para colocar las guias en un directorio compartido en la raiz del plugin en vez de duplicarlas junto a cada skill (ver detalles abajo).

### Scripts genericos (desde la raiz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent semantic-layer` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<nombre>/` | `bash ../pack_opencode.sh --agent semantic-layer` |

### Ficheros incluidos por paquete

| Fichero fuente | `claude_project` | `claude_plugin` | `claude_plugin --with-agent` | `claude_cowork` | `claude_code` | `opencode` |
|---|---|---|---|---|---|---|
| `AGENTS.md` | ✅ → `CLAUDE.md` | ❌ | ✅ → `agents/<n>.md` | ✅ → `CLAUDE.md`¹ | ✅ → `CLAUDE.md` | ✅ → `AGENTS.md` |
| `skills/` | ✅² | ✅³ | ✅³ | ✅ (en ZIP) | ✅ (en `.claude/skills/`) | ✅ (en `.opencode/skills/`) |
| `skills-guides/` | ✅⁴ | ✅⁵ | ✅⁵ | ✅ (en ZIP) | ✅⁶ | ✅⁶ |
| `.mcp.json` | ❌ | ✅ | ✅ | ✅ (en ZIP) | ✅ | ❌ |
| `opencode.json` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `plugin.json` | ❌ | ✅ | ✅ | ✅ (en ZIP) | ❌ | ❌ |
| `settings.json` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `.claude/settings.local.json` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

¹ Generado (no copia directa): referencias `skills-guides/` → `skills/stratio-semantic-layer/`, placeholder `{{TOOL_PREGUNTAS}}` resuelto.
² Aplanadas en raiz: `build-semantic-layer.md`, `stratio-semantic-layer.md`, `generate-technical-terms.md`, etc.; guias prefijadas: `skills-guides_stratio-semantic-layer-tools.md`.
³ Estructura canonica: `skills/<skill>/SKILL.md` + subficheros.
⁴ Guias renombradas con prefijo: `skills-guides_stratio-semantic-layer-tools.md`.
⁵ Default: duplicadas junto a cada skill; con `--shared-guides`: en directorio `skills-guides/` raiz.
⁶ Guides dentro de cada skill (autocontenida) + en `skills-guides/` para referencias desde `CLAUDE.md`/`AGENTS.md`.

### Empaquetado como Claude Plugin

Genera un ZIP listo para instalar como plugin en Claude Code. Las guias compartidas de `skills-guides/` se copian junto al `SKILL.md` de cada skill que las usa (patron de los plugins oficiales de Anthropic). El script soporta dos variantes:

- **Con agente** (`--with-agent`): Para Claude Code CLI. El paquete incluye `agents/<nombre>.md` (con `AGENTS.md` como instrucciones) y `settings.json` — el agente del plugin toma el control como hilo principal. Funciona tambien en Cowork, pero reemplaza al orquestador (pierde la capacidad de coordinacion con otros plugins/agentes).
- **Sin agente** (default): Solo skills + MCP. Uso interno por `pack_claude_cowork.sh`, no se distribuye como entregable independiente porque las skills referencian secciones de AGENTS.md.

```bash
# Plugin con agente (para Claude Code CLI)
bash pack_claude_plugin.sh --name semantic-layer --with-agent --gov-url https://gov.ejemplo.com --sql-url https://sql.ejemplo.com

# Plugin sin agente (uso interno por pack_claude_cowork.sh)
bash pack_claude_plugin.sh --name semantic-layer
```

El resultado se encuentra en `dist/claude_plugins/semantic-layer/semantic-layer.zip`.

**Guias compartidas** (`--shared-guides`): Por defecto las guias de `skills-guides/` se duplican junto al `SKILL.md` de cada skill que las usa. Con `--shared-guides` se colocan en un directorio `skills-guides/` en la raiz del plugin y las skills las referencian con ruta relativa. Esto evita duplicacion pero depende de que Claude resuelva rutas relativas entre directorios del plugin.

### Empaquetado como Claude Cowork

Genera un paquete para configurar el agente en Claude Cowork sin reemplazar al orquestador. El script produce tres ficheros:

| Fichero | Que es | Para que sirve |
|---------|--------|----------------|
| `CLAUDE.md` | Folder instructions (generado desde AGENTS.md) | Instrucciones del agente — Cowork las lee automaticamente del directorio de trabajo |
| `<nombre>.zip` | Plugin ZIP (solo skills + MCP, sin agente) | Se instala como plugin en Cowork; aporta las skills y la conexion MCP |
| `<nombre>-cowork.zip` | ZIP de distribucion con los dos ficheros anteriores | Para enviar/compartir el paquete completo; el usuario lo descomprime y usa cada pieza por separado |

> **Nota:** Los plugins de Claude no incluyen instrucciones de agente (CLAUDE.md) — solo skills, MCP y hooks. Por eso el `CLAUDE.md` va aparte, como fichero del directorio de trabajo.

```bash
bash pack_claude_cowork.sh --name semantic-layer --gov-url https://gov.ejemplo.com --sql-url https://sql.ejemplo.com
```

El resultado se encuentra en `dist/claude_cowork/semantic-layer/`.

**Como usarlo en Cowork:**

1. Descomprimir `<nombre>-cowork.zip` (o usar los ficheros sueltos del directorio `dist/`)
2. Copiar `CLAUDE.md` al directorio de trabajo del proyecto en Cowork — Cowork lo lee automaticamente como folder instructions
3. Instalar `<nombre>.zip` como plugin en Cowork (aporta las skills `/build-semantic-layer`, `/stratio-semantic-layer`, `/generate-technical-terms`, `/create-ontology`, `/create-business-views`, `/create-sql-mappings`, `/create-semantic-terms`, `/manage-business-terms`, `/create-data-collection` y la conexion MCP)
4. El orquestador de Cowork lee las instrucciones del `CLAUDE.md` y delega a las skills del plugin cuando corresponda

**Diferencia con el plugin con agente:** En Cowork con agente (`pack_claude_plugin.sh --with-agent`), el plugin sustituye al orquestador — funciona como Claude Code CLI dentro de Cowork. Con el paquete Cowork, el orquestador mantiene el control y puede coordinar con otros plugins/agentes.

### Empaquetado como Claude Project (claude.ai)

Genera los ficheros aplanados (skills, guias) + un ZIP:

```bash
bash pack_claude_project.sh --name semantic-layer
```

Para configurarlo en claude.ai:

1. Crear un nuevo **Project** en [claude.ai](https://claude.ai)
2. Abrir `dist/claude_projects/semantic-layer/` y subir **todos los ficheros** (excepto `CLAUDE.md` y el ZIP) a la seccion de archivos del proyecto
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
