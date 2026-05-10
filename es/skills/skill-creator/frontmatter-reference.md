# Referencia de Frontmatter

Referencia completa de todos los campos YAML de frontmatter disponibles en los ficheros SKILL.md. Todos los campos son opcionales salvo que se indique lo contrario, pero `name` y `description` son muy recomendables.

## Catálogo de campos

### name

- **Tipo**: string
- **Valor por defecto**: derivado del nombre de fichero/carpeta
- **Descripción**: Identificador único de la skill. Se convierte en el `/slash-command` que los usuarios escriben para invocarla.
- **Reglas**: solo letras minúsculas, números y guiones. Máximo 64 caracteres.
- **Correcto**: `name: create-quality-rules`
- **Incorrecto**: `name: CreateQualityRules` (sin camelCase), `name: my awesome skill!` (sin espacios ni caracteres especiales)

### description

- **Tipo**: string
- **Valor por defecto**: ninguno
- **Descripción**: Explica qué hace la skill y cuándo usarla. Este es el **mecanismo principal de activación** — el agente lee todas las descripciones de las skills para decidir cuál activar.
- **Reglas**: Sitúa al inicio el caso de uso principal. Incluye una cláusula "Use when...". Incluye palabras clave que el usuario probablemente diga. Se recomiendan ~250 caracteres como máximo.

**Buenos ejemplos:**

```yaml
# Example 1: Quality assessment skill
description: "Assess the current data quality coverage for a domain, table, or column. Returns analysis of covered dimensions, missing gaps, and priority columns. Use when the user wants to understand quality status or identify gaps."

# Example 2: Data exploration skill
description: "Quick exploration of a governed data domain: list tables, show columns, preview sample data, and display basic statistics. Use when the user wants to browse or understand available data before analysis."

# Example 3: Code review skill
description: "Review code changes for bugs, security issues, and style violations. Use when the user submits a PR, asks for a code review, or wants feedback on their changes. Also triggers on \"check my code\" or \"review this\"."

# Example 4: Deployment skill
description: "Deploy the application to staging or production environments. Use when the user says deploy, release, push to prod, or ship it."

# Example 5: Semantic term generator
description: "Generate business semantic terms for published views in a governed domain. Use when the user wants to create or update semantic terms, or asks about the meaning of columns in business views."
```

**Malos ejemplos:**

```yaml
# Demasiado vago — raramente se activará
description: "Quality tool"

# Demasiado largo y disperso — entierra el caso de uso principal
description: "This is a comprehensive tool that can be used for many purposes related to data quality including but not limited to assessment of coverage, identification of potential gaps in quality rules, analysis of dimensions, and more."

# Falta "Use when" — el agente no sabe cuándo activarla
description: "Generates reports in PDF format"

# Solapa con todo — se activará demasiado a menudo
description: "Use this skill whenever the user asks anything about data."
```

### argument-hint

- **Tipo**: string
- **Valor por defecto**: ninguno
- **Descripción**: Texto de ejemplo mostrado en el autocompletado de la interfaz cuando el usuario empieza a escribir el slash command.
- **Correcto**: `argument-hint: "[domain] [table (optional)]"`
- **Correcto**: `argument-hint: "[issue-number]"`
- **Incorrecto**: `argument-hint: "enter your arguments here"` (demasiado vago)

### user-invocable

- **Tipo**: boolean
- **Valor por defecto**: `true`
- **Descripción**: Cuando es `false`, solo el agente puede invocar esta skill. La skill NO aparece en la lista de slash commands. Su descripción SÍ se carga en el contexto para que el agente pueda decidir cuándo usarla.
- **Cuándo usarlo**: Para skills de conocimiento de fondo que el agente debería aplicar automáticamente: `legacy-system-context`, `coding-standards`.
- **Ejemplo**:
  ```yaml
  name: legacy-system-context
  description: Context about the legacy auth system. Use when working with auth-related code.
  user-invocable: false
  ```

### Resumen de control de invocación

| Frontmatter | Usuario invoca | Agente invoca | Descripción en contexto |
|-------------|:--------------:|:-------------:|:-----------------------:|
| Por defecto (ambos true) | ✅ | ✅ | ✅ |
| `user-invocable: false` | ❌ | ✅ | ✅ |

### allowed-tools

- **Tipo**: string (nombres de herramientas separados por espacios)
- **Valor por defecto**: todas las herramientas disponibles
- **Descripción**: Restringe qué herramientas puede usar el agente mientras ejecuta esta skill. Las herramientas listadas aquí se conceden sin aprobación individual.
- **Cuándo usarlo**: Cuando una skill solo debe tener acceso a herramientas específicas por seguridad o enfoque.
- **Ejemplo**:
  ```yaml
  allowed-tools: Read Grep Glob Bash(git *) Bash(npm *)
  ```
  Esto permite Read, Grep, Glob y Bash solo para comandos `git` y `npm`.

### model

- **Tipo**: string (ID de modelo)
- **Valor por defecto**: hereda de la sesión
- **Descripción**: Especifica qué modelo utilizar cuando la skill está activa. Sobreescribe el modelo de la sesión.
- **Cuándo usarlo**: Cuando una skill requiere las capacidades de un modelo específico (por ejemplo, una skill de razonamiento complejo que necesita el modelo más capaz).
- **Ejemplo**: `model: claude-sonnet-4-6`

### effort

- **Tipo**: string (`low`, `medium`, `high`, `max`)
- **Valor por defecto**: hereda de la sesión
- **Descripción**: Establece el nivel de esfuerzo de razonamiento cuando la skill está activa. Sobreescribe el nivel de la sesión.
- **Cuándo usarlo**: Usa `max` para skills de razonamiento complejo; `low` para skills simples de consulta o formateo.
- **Ejemplo**: `effort: max`

### context

- **Tipo**: string
- **Valor por defecto**: se ejecuta en línea
- **Descripción**: Establécelo a `fork` para ejecutar la skill en un contexto aislado de subagente. El contenido de la skill se convierte en el prompt que dirige al subagente. El subagente tiene su propia ventana de contexto y no puede ver la conversación padre.
- **Cuándo usarlo**: Para tareas aisladas y autocontenidas que no necesitan historial de conversación: exploración de código, análisis de ficheros, generación de informes.
- **Ejemplo**: `context: fork`

### agent

- **Tipo**: string
- **Valor por defecto**: `general-purpose`
- **Descripción**: Especifica qué tipo de subagente usar cuando se establece `context: fork`. Opciones: `Explore`, `Plan`, `general-purpose`, o un subagente personalizado definido en `.claude/agents/`.
- **Cuándo usarlo**: Combinado con `context: fork` para especializar el comportamiento del subagente.
- **Ejemplo**:
  ```yaml
  context: fork
  agent: Explore
  ```

### paths

- **Tipo**: string (patrones glob separados por comas) o lista YAML
- **Valor por defecto**: se activa en cualquier lugar
- **Descripción**: Limita cuándo se activa la skill en función de los ficheros con los que se está trabajando. La skill solo se carga cuando la tarea actual involucra ficheros que coinciden con estos patrones.
- **Cuándo usarlo**: Para skills específicas de ciertos tipos de fichero o directorios.
- **Ejemplo**:
  ```yaml
  paths: src/**/*.ts, src/**/*.tsx
  ```
  o
  ```yaml
  paths:
    - src/**/*.ts
    - src/**/*.tsx
  ```

### shell

- **Tipo**: string (`bash` o `powershell`)
- **Valor por defecto**: `bash`
- **Descripción**: Establece el shell utilizado para comandos en línea (sintaxis `` !`command` ``) en el cuerpo de la skill.
- **Cuándo usarlo**: Solo establécelo a `powershell` si la skill está dirigida a entornos Windows.

### hooks

- **Tipo**: object
- **Valor por defecto**: ninguno
- **Descripción**: Hooks del ciclo de vida para automatización. Permite ejecutar comandos shell en puntos específicos de la ejecución de la skill.
- **Cuándo usarlo**: Para skills que necesitan preparación/limpieza o efectos secundarios de notificación.

## Sustituciones de cadenas

Estos marcadores se reemplazan en tiempo de ejecución cuando se invoca la skill:

| Marcador | Descripción | Ejemplo |
|----------|-------------|---------|
| `$ARGUMENTS` | Todos los argumentos pasados tras el slash command | `/my-skill arg1 arg2` → `$ARGUMENTS` = `arg1 arg2` |
| `$ARGUMENTS[0]` o `$0` | Primer argumento | `/my-skill domain_name` → `$0` = `domain_name` |
| `$ARGUMENTS[1]` o `$1` | Segundo argumento | `/my-skill domain table` → `$1` = `table` |
| `${CLAUDE_SESSION_ID}` | ID de sesión actual (útil para logging) | `session-abc123` |
| `${CLAUDE_SKILL_DIR}` | Ruta absoluta al directorio que contiene este SKILL.md | `/home/user/.claude/skills/my-skill` |

**Ejemplo de uso:**

```markdown
---
name: assess-quality
argument-hint: "[domain] [table (optional)]"
---

## 1. Determine scope

Assess the quality of domain `$ARGUMENTS[0]`.
If a second argument was provided, focus on table `$ARGUMENTS[1]`.
```

## Ejercicios de optimización de descripciones

### Ejercicio: Refinar una descripción débil

**Paso 1 — Empieza con la intención:**
```yaml
description: "Creates reports"
```

**Paso 2 — Añade especificidad:**
```yaml
description: "Generate data quality coverage reports in PDF, DOCX, or Markdown format"
```

**Paso 3 — Añade el disparador "Use when...":**
```yaml
description: "Generate data quality coverage reports in PDF, DOCX, or Markdown. Use when the user wants a formal report of quality status."
```

**Paso 4 — Añade palabras clave de activación:**
```yaml
description: "Generate data quality coverage reports in PDF, DOCX, or Markdown. Use when the user wants a formal report, coverage summary, quality document, or asks to export/download quality results."
```

Esta versión final se activará con: "generate a report", "I need a PDF of the quality status", "export the coverage results", "create a quality document".
