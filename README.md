# genai-agents

Coleccion de agentes de IA generativa para analisis de datos de negocio. Compatibles con **Claude Code**, **Claude Cowork**, **claude.ai**, **OpenCode**, **OpenWork** y herramientas compatibles con MCP.

## Agentes

| Agente | Descripcion | Plataformas | Carpeta |
|--------|-------------|-------------|---------|
| **data-analytics** | Agente completo de BI/BA con analisis avanzado, clustering, informes multi-formato (PDF, DOCX, web, PowerPoint) y documentacion del razonamiento | Claude Code, OpenCode, OpenWork | `data-analytics/` |
| **data-analytics-light** | Agente ligero de BI/BA orientado a analisis en chat, sin generacion de informes formales. Incluye scripts de empaquetado para multiples plataformas | Claude Code, Claude Cowork, claude.ai, OpenCode | `data-analytics-light/` |

## Empaquetado

Scripts en la raiz del monorepo para empaquetar cualquier agente en el formato de la plataforma destino:

| Script | Plataforma destino | Output |
|--------|-------------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agente}/dist/claude_code/{nombre}/` |
| `pack_opencode.sh` | OpenCode | `{agente}/dist/opencode/{nombre}/` |

```bash
# Empaquetar data-analytics para Claude Code
bash pack_claude_code.sh --agent data-analytics

# Empaquetar data-analytics para OpenCode con nombre personalizado
bash pack_opencode.sh --agent data-analytics --name mi-agente
```

El nombre debe ser kebab-case. Si se omite, se usa el basename del directorio del agente. Los directorios generados estan excluidos del repositorio (`.gitignore`).

`data-analytics-light` incluye ademas scripts de empaquetado para los diferentes formatos de Claude (Projects, Plugin y Cowork), con instrucciones detalladas de como configurar cada formato en la plataforma destino — ver [`data-analytics-light/README.md`](data-analytics-light/README.md).

### Estructura de outputs (`make package`)

Todos los artefactos se generan bajo `dist/`, tanto a nivel de agente (intermedios) como en la raiz (zips finales versionados):

```
genai-agents/
  dist/                                         # ZIPs finales versionados
    data-analytics-claude-code-{v}.zip
    data-analytics-opencode-{v}.zip
    data-analytics-light-claude-code-{v}.zip
    data-analytics-light-opencode-{v}.zip
    data-analytics-light-claude-plugin-{v}.zip
    data-analytics-light-claude-plugin-agent-{v}.zip
    data-analytics-light-claude-cowork-{v}.zip
    data-analytics-light-claude-project-{v}.zip
    genai-agents-sources-{v}.zip                 # Fuentes del repositorio
    genai-agents-{v}.zip                        # ZIP global con todos los anteriores

  data-analytics/
    dist/                                       # Artefactos intermedios
      claude_code/data-analytics/
      opencode/data-analytics/

  data-analytics-light/
    dist/                                       # Artefactos intermedios
      claude_code/data-analytics-light/
      opencode/data-analytics-light/
      claude_plugins/data-analytics-light/
      claude_cowork/data-analytics-light/
      claude_projects/data-analytics-light/
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

## Uso directo (sin empaquetar)

El formato canonico de instrucciones es `AGENTS.md` + `skills/`. Para usar con cualquier plataforma, empaquetar con el script correspondiente. La raiz del monorepo tiene un symlink `CLAUDE.md → AGENTS.md` para compatibilidad con Claude Code.

- **Claude Code**: Empaquetar con `pack_claude_code.sh` para uso fuera del repositorio. Lee instrucciones de `AGENTS.md` (via symlink `CLAUDE.md`). Para uso directo con Claude Code, empaquetar primero con `pack_claude_code.sh`.
- **OpenCode**: `opencode.json` apunta a `AGENTS.md`. Para uso directo con OpenCode, empaquetar primero con `pack_opencode.sh`.

Los pack scripts generan el formato correcto para cada plataforma (renombrando ficheros, reubicando skills, etc.).

## Requisitos comunes

- Python 3.10+
- Acceso a un servidor MCP de Stratio (configurado en `.mcp.json` de cada agente)

## Setup

Cada agente tiene su propio entorno virtual y dependencias. Desde la carpeta de cada agente:

```bash
cd data-analytics/    # o data-analytics-light/
bash setup_env.sh
```

Esto crea un `.venv/` local con las dependencias definidas en `requirements.txt`.

## Crear un agente nuevo

Esta guía explica cómo añadir un agente al monorepo para usarlo en **OpenCode** o en el **framework de agentes de Stratio GenAI**. Un agente se compone de tres piezas: **instrucciones** (`AGENTS.md`), **skills** (`skills/`) y **configuración de herramientas** (`opencode.json`). El script `pack_opencode.sh` se encarga de empaquetarlo.

### 1. Estructura de carpetas

```
mi-agente/
├── AGENTS.md              # Instrucciones principales — rol, workflow, reglas
├── opencode.json          # Configuracion OpenCode (MCPs, permisos)
├── skills/                # Capacidades invocables por el usuario
│   └── mi-skill/
│       └── SKILL.md       # Definicion de la skill (frontmatter YAML + cuerpo)
├── skills-guides/         # (Opcional) Guias tecnicas compartidas entre skills
└── output-templates/      # (Opcional) Semillas de memoria persistente
```

Los directorios `skills-guides/` y `output-templates/` son opcionales: usar `skills-guides/` cuando varias skills comparten documentación técnica extensa; usar `output-templates/` solo si el agente necesita persistir memoria entre sesiones.

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

### 4. opencode.json — Configurar herramientas externas

La configuración de OpenCode declara las instrucciones, los MCPs disponibles y los permisos del agente:

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

### 5. Empaquetar

```bash
# Empaquetar para OpenCode
bash pack_opencode.sh --agent mi-agente

# Con nombre personalizado (kebab-case)
bash pack_opencode.sh --agent mi-agente --name nombre-personalizado
```

El output se genera en `mi-agente/dist/opencode/mi-agente/` (excluido de git por `.gitignore`). Para empaquetar todos los agentes del monorepo de una vez: `make package`.

### 6. Probar en OpenCode

La carpeta `dist/` se sobreescribe en cada ejecución de `pack_opencode.sh`, así que antes de abrir OpenCode conviene copiar el paquete generado a una ruta de trabajo:

```bash
cp -r mi-agente/dist/opencode/mi-agente ~/agentes/mi-agente
```

Si el `opencode.json` referencia variables de entorno para servidores MCP, exportarlas en el terminal antes de abrir OpenCode:

```bash
export MI_SERVIDOR_URL="https://mi-servidor.ejemplo.com/mcp"
export MI_API_KEY="mi-token-secreto"
```

A continuación, abrir OpenCode desde la carpeta del agente:

```bash
cd ~/agentes/mi-agente
opencode
```

Al arrancar, OpenCode carga automáticamente `AGENTS.md` como instrucciones del agente, las skills disponibles en `skills/` y conecta con los servidores MCP definidos en `opencode.json`. Las skills se invocan con `/nombre-skill` en el chat.

El archivo `opencode.json` se puede editar a mano en cualquier momento para añadir, quitar o reconfigurar servidores MCP — solo hace falta reiniciar OpenCode para que los cambios surtan efecto.
