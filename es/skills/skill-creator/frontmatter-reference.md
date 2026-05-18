# Referencia de Frontmatter

Referencia de los campos YAML de frontmatter reconocidos por las skills de **OpenCode**.

> **Nota de alcance.** El cargador de skills de OpenCode (verificado en `packages/opencode/src/skill/index.ts:36-58` del código fuente de OpenCode) solo lee `name` y `description` del frontmatter; cualquier otro campo top-level se ignora silenciosamente en tiempo de carga. Otros runtimes (p. ej. Claude Code) aceptan campos adicionales como `model`, `effort`, `context: fork`, `agent`, `paths`, `allowed-tools`, `shell`, `hooks`, `argument-hint`, `user-invocable` — esos campos **no surten efecto** cuando la skill se empaqueta para OpenCode y no se documentan aquí.

## Catálogo de campos

### name

- **Tipo**: string
- **Valor por defecto**: derivado del nombre de fichero/carpeta
- **Descripción**: Identificador único de la skill. Se convierte en el `/slash-command` que los usuarios escriben para invocarla.
- **Reglas**: solo letras minúsculas, números y guiones. Máximo 64 caracteres. Debe coincidir con el nombre del directorio padre. No debe contener las palabras reservadas `anthropic` ni `claude`.
- **Correcto**: `name: create-quality-rules`
- **Incorrecto**: `name: CreateQualityRules` (sin camelCase), `name: my awesome skill!` (sin espacios ni caracteres especiales)

### description

- **Tipo**: string
- **Valor por defecto**: ninguno
- **Descripción**: Explica qué hace la skill y cuándo usarla. Este es el **mecanismo principal de activación** — el agente lee todas las descripciones de las skills para decidir cuál activar.
- **Reglas**: Sitúa al inicio el caso de uso principal. Incluye una cláusula "Use when...". Incluye palabras clave que el usuario probablemente diga. Máximo 1024 caracteres (solo los primeros ~250 se muestran en los listados de la UI de slash-commands).

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
