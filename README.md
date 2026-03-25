# genai-agents

Coleccion de agentes y skills de IA generativa que explotan la **Stratio Semantic Data Layer**, la capa de datos semantizados que **Stratio Governance** genera a partir de sus dominios de datos, capas semanticas, reglas de calidad del dato y business terms, produciendo colecciones listas para consumo analitico. Gracias a **Stratio Virtualizer**, un motor basado en Apache Spark, el acceso a los datos es independiente del datastore subyacente y compatible con big data. Los agentes de este repositorio se conectan a Governance para consultar, analizar y generar informes sobre esos datos gobernados.

El repositorio esta orientado principalmente a **OpenCode**, la herramienta opensource sobre la que Stratio basa su Agent Builder en la plataforma GenAI. Algunos agentes incluyen ademas empaquetados para otras plataformas como **claude.ai Projects** o **Claude Desktop** (Claude Cowork).

## Agentes

| Agente | Descripcion | Plataformas | Carpeta |
|--------|-------------|-------------|---------|
| **data-analytics** | Agente completo de BI/BA con analisis avanzado, clustering, informes multi-formato (PDF, DOCX, web, PowerPoint) y documentacion del razonamiento | Claude Code, OpenCode, Stratio Cowork | `data-analytics/` |
| **data-analytics-light** | Agente ligero de BI/BA orientado a analisis en chat, sin generacion de informes formales. Incluye scripts de empaquetado para multiples plataformas | Claude Code, Claude Cowork, claude.ai, OpenCode | `data-analytics-light/` |
| **semantic-layer** | Agente especializado en construccion y mantenimiento de capas semanticas en Stratio Governance: creacion de colecciones de datos (dominios tecnicos), terminos tecnicos, ontologias, vistas de negocio, SQL mappings, publicacion de vistas, terminos semanticos y business terms | Claude Code, Claude Cowork, claude.ai, OpenCode, Stratio Cowork | `semantic-layer/` |

## Empaquetado

Scripts en la raiz del monorepo para empaquetar cualquier agente en el formato de la plataforma destino:

| Script | Plataforma destino | Output |
|--------|-------------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agente}/dist/claude_code/{nombre}/` |
| `pack_opencode.sh` | OpenCode | `{agente}/dist/opencode/{nombre}/` |
| `pack_stratio_cowork.sh` | Stratio Cowork (OpenCode) | `dist/{nombre}-stratio-cowork.zip` |
| `pack_shared_skills.sh` | Todas (skills sueltas) | `dist/shared-skills.zip` o `dist/{skill}.zip` |

```bash
# Empaquetar data-analytics para Claude Code
bash pack_claude_code.sh --agent data-analytics

# Empaquetar data-analytics para OpenCode con nombre personalizado
bash pack_opencode.sh --agent data-analytics --name mi-agente

# Empaquetar semantic-layer para Stratio Cowork
bash pack_stratio_cowork.sh --agent semantic-layer
```

El nombre debe ser kebab-case. Si se omite, se usa el basename del directorio del agente. Los directorios generados estan excluidos del repositorio (`.gitignore`).

`pack_stratio_cowork.sh` genera un ZIP compuesto con dos sub-ZIPs pensado para el despliegue en Stratio Cowork: uno con el agente sin sus shared skills, y otro con las shared skills por separado (para distribuirlas de forma independiente al agente). Además incluye en la raíz del bundle el fichero `mcps` del agente si existe (ver [Configurar herramientas externas](#4-configurar-herramientas-externas-mcps)).

`data-analytics-light` y `semantic-layer` incluyen ademas scripts de empaquetado para los diferentes formatos de Claude (AI Projects y Cowork). Ver [`data-analytics-light/README.md`](data-analytics-light/README.md) para instrucciones detalladas de como configurar cada formato en la plataforma destino.

### Estructura de outputs (`make package`)

Todos los artefactos se generan bajo `dist/`, tanto a nivel de agente (intermedios) como en la raiz (zips finales versionados):

```
genai-agents/
  dist/                                         # ZIPs finales versionados
    data-analytics-claude-code-{v}.zip
    data-analytics-opencode-{v}.zip
    data-analytics-stratio-cowork.zip            # Bundle Stratio Cowork (agente + shared skills)
    data-analytics-light-claude-code-{v}.zip
    data-analytics-light-opencode-{v}.zip
    data-analytics-light-claude-cowork-{v}.zip
    data-analytics-light-claude-ai-project-{v}.zip
    semantic-layer-claude-code-{v}.zip
    semantic-layer-opencode-{v}.zip
    semantic-layer-claude-cowork-{v}.zip
    semantic-layer-claude-ai-project-{v}.zip
    semantic-layer-stratio-cowork.zip            # Bundle Stratio Cowork (agente + shared skills)
    shared-skills-{v}.zip                        # Todas las shared skills juntas
    shared-skill-propose-knowledge-{v}.zip       # Skill individual
    shared-skill-explore-data-{v}.zip            # Skill individual
    shared-skill-stratio-data-{v}.zip            # Skill individual
    shared-skill-stratio-semantic-layer-{v}.zip  # Skill individual
    shared-skill-generate-technical-terms-{v}.zip
    shared-skill-create-ontology-{v}.zip
    shared-skill-create-business-views-{v}.zip
    shared-skill-create-sql-mappings-{v}.zip
    shared-skill-create-semantic-terms-{v}.zip
    shared-skill-manage-business-terms-{v}.zip
    shared-skill-create-data-collection-{v}.zip

  data-analytics/
    dist/                                       # Artefactos intermedios
      claude_code/data-analytics/
      opencode/data-analytics/

  data-analytics-light/
    dist/                                       # Artefactos intermedios
      claude_code/data-analytics-light/
      opencode/data-analytics-light/
      claude_cowork/data-analytics-light/
      claude_ai_projects/data-analytics-light/

  semantic-layer/
    dist/                                       # Artefactos intermedios
      claude_code/semantic-layer/
      opencode/semantic-layer/
      claude_cowork/semantic-layer/
      claude_ai_projects/semantic-layer/
```

`make clean` elimina todos los `dist/` (raiz + agentes).

### Formatos de skills soportados

Los pack scripts reconocen dos formatos de definicion de skills:

| Formato | Estructura | Ejemplo |
|---------|-----------|---------|
| **Canonico** (recomendado) | `skills/<nombre>/SKILL.md` | `skills/analyze/SKILL.md` |
| **Plano** | `skills/<nombre>.md` | `skills/analyze.md` |

El formato plano se normaliza automaticamente a canonico al empaquetar (`<nombre>.md` → `<nombre>/SKILL.md`).

Ubicaciones de busqueda (por orden de prioridad): `skills/` → `.claude/skills/` → `.opencode/skills/` → `.agents/skills/`.

### Plantillas de output

Si un agente tiene un directorio `output-templates/`, los pack scripts crean `output/` en el paquete con ese contenido. Esto permite versionar en git las plantillas semilla (ficheros de memoria inicial, etc.) sin versionar el runtime — `**/output/` sigue en `.gitignore`.

## Skills compartidas

`shared-skills/` agrupa skills reutilizables entre varios agentes del monorepo. Los pack scripts las incluyen automáticamente en el output de cada agente que las declare, sin necesidad de duplicar código.

### Skills disponibles

| Skill | Descripcion | Agentes que la usan |
|-------|-------------|---------------------|
| `propose-knowledge` | Proponer terminos de negocio y preferencias a Stratio Governance tras un analisis | data-analytics, data-analytics-light |
| `explore-data` | Exploracion rapida de dominios, tablas, columnas y terminologia gobernada | data-analytics, data-analytics-light |
| `stratio-data` | Referencia de MCPs de datos Stratio: reglas, patrones de uso y buenas practicas | (independiente) |
| `stratio-semantic-layer` | Referencia de MCPs de capa semantica Stratio: reglas, patrones de uso y buenas practicas para tools de gobernanza | semantic-layer |
| `generate-technical-terms` | Generar o regenerar terminos tecnicos (descripciones de tablas y columnas) para un dominio | semantic-layer |
| `create-ontology` | Crear o ampliar ontologias con planificacion interactiva | semantic-layer |
| `create-business-views` | Crear, regenerar o publicar vistas de negocio y SQL mappings a partir de una ontologia | semantic-layer |
| `create-sql-mappings` | Crear o actualizar SQL mappings de vistas existentes | semantic-layer |
| `create-semantic-terms` | Generar o regenerar terminos semanticos de negocio para vistas | semantic-layer |
| `manage-business-terms` | Crear Business Terms en el diccionario con relaciones a activos de datos | semantic-layer |
| `create-data-collection` | Buscar tablas y paths en el diccionario de datos tecnico y crear una nueva coleccion (dominio tecnico) | semantic-layer |

Los guides compartidos (documentacion tecnica que las skills referencian) viven en `shared-skill-guides/`:

| Guide | Usado por |
|-------|-----------|
| `stratio-data-tools.md` | `explore-data`, `analyze`, `AGENTS.md` (data-analytics, data-analytics-light) |
| `stratio-semantic-layer-tools.md` | `stratio-semantic-layer`, `AGENTS.md` (semantic-layer) |

### Usar una shared skill en un agente

1. Crear (si no existe) el fichero `shared-skills` en la carpeta del agente con el nombre de la skill, una por línea:

   ```
   propose-knowledge
   explore-data
   ```

2. Si el `AGENTS.md` del agente referencia directamente algún guide de `shared-skill-guides/`, declararlo también en `shared-guides`:

   ```
   stratio-data-tools.md
   ```

3. Empaquetar con normalidad — los pack scripts genéricos (`pack_claude_code.sh`, `pack_opencode.sh`) copian cada guide declarado en `skill-guides` **dentro** de la carpeta de la skill en el output y reescriben las referencias en `SKILL.md` para que sean locales (skill autocontenida). Los guides declarados en `shared-guides` del agente se copian además a `skills-guides/` para que `AGENTS.md`/`CLAUDE.md` los referencie:

   ```bash
   bash pack_claude_code.sh --agent mi-agente
   ```

   Output resultante (ejemplo con `explore-data` que declara `stratio-data-tools.md`):
   ```
   .claude/
     skills/
       explore-data/
         SKILL.md                  # referencia "stratio-data-tools.md" (local)
         stratio-data-tools.md     # guide dentro de la skill
     skills-guides/
       stratio-data-tools.md       # para AGENTS.md (posible duplicado, ok)
   ```

Si el agente tiene en `skills/` una skill con el mismo nombre, la versión local tiene prioridad sobre la shared.

### Crear una shared skill nueva

1. Crear la carpeta y el `SKILL.md` en `shared-skills/`:

   ```
   shared-skills/
   └── mi-skill/
       ├── SKILL.md       # Definicion de la skill (autocontenida o casi)
       └── skill-guides   # (Opcional) Lista de shared-skill-guides que necesita
   ```

2. Si la skill necesita guides externos, añadir los ficheros en `shared-skill-guides/` y listarlos en `skill-guides`:

   ```
   # shared-skills/mi-skill/skill-guides
   mi-guide.md
   ```

3. Declarar la skill en los agentes que deban incluirla (fichero `shared-skills` en cada agente).

Una shared skill debe ser lo más autocontenida posible: sin dependencias de herramientas Python, estilos ni templates específicos de un agente. Si una skill depende fuertemente de artefactos de un agente concreto, mantenerla como skill local en ese agente.

**Contenido del SKILL.md:** No referenciar `AGENTS.md` ni `CLAUDE.md` directamente — los pack scripts sustituyen estos nombres según la plataforma, pero una referencia directa puede quedar mal en algún destino. Usar formulaciones genéricas como "siguiendo la convención de preguntas al usuario" o "según las instrucciones del agente". Las referencias a guides deben usar la ruta `skills-guides/<fichero>` en el fuente — los pack scripts genéricos copian el guide dentro de la skill y reescriben la referencia para que sea local (autocontenida).

## Formato y compatibilidad con herramientas de desarrollo

Los agentes siguen el formato `AGENTS.md` + `skills/`, reconocido por **OpenCode**, **Cursor**, plugins de **GitHub Copilot** y otras herramientas compatibles con el estandar de instrucciones de agente.

Un agente se compone de:

- `AGENTS.md` (o `CLAUDE.md`) — instrucciones del agente: rol, workflow, reglas (**obligatorio**)
- `skills/` — skills invocables por el usuario (opcional)
- `opencode.json` — configuracion de MCPs y permisos para OpenCode (opcional)
- `.mcp.json` — configuracion de MCPs para Claude Code / claude.ai (opcional)

Con estos ficheros, basta ejecutar el script de empaquetado correspondiente para generar el paquete listo para usar en la plataforma destino.

La raiz del monorepo incluye un symlink `CLAUDE.md → AGENTS.md` para poder abrir el proyecto directamente con **Claude Code** y programar nuevos agentes con su asistente de codigo.

## Crear un agente nuevo

Esta guía explica cómo añadir un agente al monorepo para usarlo en **OpenCode**, **Claude Code** o el **framework de agentes de Stratio GenAI**. Un agente se compone de tres piezas: **instrucciones** (`AGENTS.md`), **skills** (`skills/`) y **configuración de herramientas**. Añadiendo `opencode.json` y/o `.mcp.json` el agente puede funcionar en ambas plataformas a la vez. Los scripts `pack_opencode.sh` y `pack_claude_code.sh` se encargan de empaquetarlo para cada destino.

### 1. Estructura de carpetas

```
mi-agente/
├── AGENTS.md              # Instrucciones principales — rol, workflow, reglas
├── opencode.json          # Configuracion OpenCode (MCPs, permisos)
├── .mcp.json              # Configuracion de MCPs para Claude Code / claude.ai
├── mcps                   # (Opcional) Lista de MCPs requeridos para Stratio Cowork
├── skills/                # Skills propias del agente (invocables por el usuario)
│   └── mi-skill/
│       └── SKILL.md       # Definicion de la skill (frontmatter YAML + cuerpo)
├── skills-guides/         # (Opcional) Guias tecnicas locales compartidas entre skills
├── shared-skills          # (Opcional) Lista de shared skills del monorepo a incluir
├── shared-guides          # (Opcional) Lista de shared-skill-guides que AGENTS.md usa directamente
└── output-templates/      # (Opcional) Semillas de memoria persistente
```

Los directorios `skills-guides/` y `output-templates/` son opcionales: usar `skills-guides/` cuando varias skills del agente comparten documentación técnica extensa; usar `output-templates/` solo si el agente necesita persistir memoria entre sesiones.

Los ficheros `shared-skills` y `shared-guides` (texto plano, una entrada por línea) permiten incluir skills y guides del monorepo sin duplicarlos. Ver [Skills compartidas](#skills-compartidas) para el detalle.

### 2. AGENTS.md — Instrucciones del agente

Define el **rol**, el **workflow** y las **reglas transversales** del agente. Estructura orientativa:

```markdown
# [Nombre del Agente]

## Rol y Contexto
Descripcion del agente: qué hace, para quién, y con qué herramientas opera.

## Workflow Obligatorio
Fases de ejecucion numeradas. Ejemplo: triage → exploracion → preguntas → plan → ejecucion.
Cuanto mas detallado, mas predecible el comportamiento del agente.

## Reglas Transversales
Normas que aplican a toda sesion (idioma de respuesta, validaciones obligatorias,
herramientas que tiene prohibido usar, etc.).

## Skills Disponibles
Lista de skills y cuando activar cada una.
```

### 3. Skills — Definir capacidades

Cada skill encapsula un workflow específico que el usuario puede invocar (ej: `/analizar`, `/generar-informe`). Formato de `SKILL.md`:

```markdown
---
name: mi-skill
description: Descripcion de cuando usar esta skill y que hace
argument-hint: [argumento esperado, ej: pregunta o tema]
---

# Skill: Mi Skill

## 1. Primer Paso
Instrucciones operativas detalladas...

## 2. Segundo Paso
...
```

El frontmatter YAML es obligatorio: `name` es el identificador, `description` lo usa el agente para decidir cuándo activarla, `argument-hint` aparece como placeholder en la UI. Las secciones del cuerpo son instrucciones paso a paso que sigue el agente al ejecutar la skill. Si varias skills comparten documentación, extraerla a `skills-guides/` y referenciarla desde el cuerpo de la skill.

Para reutilizar skills ya existentes en el monorepo sin duplicarlas, ver la sección [Skills compartidas](#skills-compartidas) — el sistema de shared skills evita mantener copies de skills idénticas en cada agente.

### 4. Configurar herramientas externas (MCPs)

Cada plataforma tiene su propio fichero de configuración. Se pueden crear ambos para que el agente funcione en OpenCode y en Claude Code a la vez.

#### 4a. `opencode.json` — OpenCode

Declara las instrucciones, los MCPs disponibles y los permisos del agente:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"],
  "mcp": {
    "mi-servidor": {
      "type": "remote",
      "url": "{env:MI_SERVIDOR_URL}",
      "timeout": 90000,
      "headers": { "Authorization": "Bearer {env:MI_API_KEY}" }
    }
  },
  "permission": {
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "bash": { "*": "allow" }
  }
}
```

Las variables de entorno se referencian con la sintaxis `{env:NOMBRE_VAR}`. Si el agente no usa MCPs externos, omitir el bloque `mcp`.

El bloque `permission` controla tanto los comandos bash/ficheros como las herramientas MCP expuestas. Para las herramientas MCP el patrón es `{nombre-servidor}_*` (todas las tools de ese servidor) o `*{nombre-tool}` (una tool concreta en cualquier servidor).

#### 4b. `.mcp.json` — Claude Code / claude.ai

Declara los servidores MCP disponibles para Claude Code:

```json
{
  "mcpServers": {
    "mi-servidor": {
      "type": "http",
      "url": "${MI_SERVIDOR_URL:-http://127.0.0.1:8080/mcp}",
      "headers": { "Authorization": "Bearer ${MI_API_KEY:-}" },
      "allowedTools": ["nombre_tool_1", "nombre_tool_2"]
    }
  }
}
```

Las variables de entorno usan sintaxis bash `${VAR:-valor_por_defecto}`. `allowedTools` restringe qué herramientas del servidor MCP se exponen al agente. Los permisos de bash y sistema de ficheros los gestiona Claude Code por su cuenta (fuera de este fichero).

#### 4c. `mcps` — Stratio Cowork

Fichero de texto plano (una línea por MCP) que declara los servidores MCP que necesita el agente. Solo es relevante para el bundle de **Stratio Cowork** — `pack_stratio_cowork.sh` lo incluye en la raíz del ZIP compuesto como referencia para el administrador que configure la instalación.

```
Stratio_Data
Stratio_Gov
```

No tiene efecto en los empaquetados para Claude Code ni para OpenCode (ambos scripts lo excluyen de su rsync). Si el agente no se va a distribuir via Stratio Cowork, no es necesario crearlo.

### 5. Empaquetar

```bash
# Empaquetar para OpenCode
bash pack_opencode.sh --agent mi-agente

# Empaquetar para Claude Code
bash pack_claude_code.sh --agent mi-agente

# Empaquetar bundle Stratio Cowork (agente + shared skills separadas + mcps)
bash pack_stratio_cowork.sh --agent mi-agente

# Con nombre personalizado (kebab-case)
bash pack_opencode.sh --agent mi-agente --name nombre-personalizado

# Empaquetar para ambas plataformas a la vez
make package
```

El output se genera en `mi-agente/dist/opencode/mi-agente/` y `mi-agente/dist/claude_code/mi-agente/` respectivamente (excluidos de git por `.gitignore`).

### 6. Probar

La carpeta `dist/` se sobreescribe en cada ejecución de los scripts de empaquetado, así que antes de abrir el agente conviene copiar el paquete generado a una ruta de trabajo.

#### 6a. Probar en OpenCode

```bash
cp -r mi-agente/dist/opencode/mi-agente ~/agentes/mi-agente
```

Si el `opencode.json` referencia variables de entorno para servidores MCP, exportarlas en el terminal antes de abrir OpenCode:

```bash
export MI_SERVIDOR_URL="https://mi-servidor.ejemplo.com/mcp"
export MI_API_KEY="mi-token-secreto"
```

> **Nota sobre TLS:** Si los servidores MCP utilizan certificados TLS autofirmados (habitual en entornos de desarrollo o pre-producción), Node.js rechazará la conexión por defecto. Para permitirla, exportar también:
>
> ```bash
> export NODE_TLS_REJECT_UNAUTHORIZED=0
> ```
>
> Esta variable desactiva la validación de certificados TLS en todas las conexiones de Node.js del proceso. Usarla **solo en entornos de confianza** — nunca en producción.

A continuación, abrir OpenCode desde la carpeta del agente:

```bash
cd ~/agentes/mi-agente
opencode
```

Al arrancar, OpenCode carga automáticamente `AGENTS.md` como instrucciones del agente, las skills disponibles en `skills/` y conecta con los servidores MCP definidos en `opencode.json`. Las skills se invocan con `/nombre-skill` en el chat.

El archivo `opencode.json` se puede editar a mano en cualquier momento para añadir, quitar o reconfigurar servidores MCP — solo hace falta reiniciar OpenCode para que los cambios surtan efecto.

#### 6b. Probar en Claude Code

```bash
cp -r mi-agente/dist/claude_code/mi-agente ~/agentes/mi-agente-cc
export MI_SERVIDOR_URL="https://mi-servidor.ejemplo.com/mcp"
export MI_API_KEY="mi-token-secreto"
cd ~/agentes/mi-agente-cc
claude .
```

> **Nota sobre TLS:** Si los servidores MCP utilizan certificados TLS autofirmados (habitual en entornos de desarrollo o pre-producción), Node.js rechazará la conexión por defecto. Para permitirla, exportar también:
>
> ```bash
> export NODE_TLS_REJECT_UNAUTHORIZED=0
> ```
>
> Esta variable desactiva la validación de certificados TLS en todas las conexiones de Node.js del proceso. Usarla **solo en entornos de confianza** — nunca en producción.

Al arrancar, Claude Code carga `CLAUDE.md` como instrucciones del agente y las skills disponibles en `.claude/skills/`. Los servidores MCP se leen de `.mcp.json`. Las skills se invocan con `/nombre-skill` en el chat.
