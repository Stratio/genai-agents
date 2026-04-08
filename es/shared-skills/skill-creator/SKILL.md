---
name: skill-creator
description: >-
  Comprehensive guide for creating high-quality AI agent skills (SKILL.md files).
  Use when designing, drafting, reviewing, or improving skills.
  Covers anatomy, frontmatter, progressive disclosure, writing patterns,
  description optimization, supporting files, and quality checklist.
argument-hint: "[skill topic or name (optional)]"
---

# Skill: Skill Creator

Referencia completa para diseñar y escribir skills de alta calidad para agentes de IA. Esta guía contiene todo el conocimiento necesario para crear skills efectivas — no depende de documentación externa ni de acceso a internet.

## 1. Anatomía de una Skill

Una **skill** es un conjunto de instrucciones empaquetadas como archivos Markdown que amplían las capacidades de un agente de IA. El punto de entrada es siempre un archivo llamado `SKILL.md`.

### 1.1 Estructura de directorios

```
<skill-name>/
  SKILL.md              # Obligatorio — instrucciones principales
  guide.md              # Opcional — guía complementaria
  scripts/              # Opcional — scripts auxiliares ejecutables (Python, bash)
    helper.py
  references/           # Opcional — documentos de referencia estáticos (esquemas, ejemplos)
    schema.md
  assets/               # Opcional — archivos usados en la generación de salida (plantillas, iconos)
    template.html
```

### 1.2 Convenciones de nomenclatura

- Usa **minúsculas con guiones**: `create-quality-rules`, `explore-data`
- Nunca uses camelCase ni PascalCase: ~~`CreateQualityRules`~~, ~~`exploreData`~~
- El nombre se convierte en el `/slash-command` para invocar la skill
- Máximo 64 caracteres; usa solo letras minúsculas, números y guiones

### 1.3 Dos tipos de skills

**Contenido de referencia** — Añade conocimiento que el agente aplica a su trabajo actual. Se ejecuta en línea con el contexto de la conversación. Ejemplos: convenciones de código, patrones de API, guías de estilo, conocimiento de dominio.

```yaml
---
name: api-conventions
description: REST API design patterns for this codebase. Use when writing or reviewing API endpoints.
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats using the ErrorResponse schema
- Include request validation with Zod schemas
```

**Contenido de tarea** — Instrucciones paso a paso para acciones específicas. Normalmente las invoca el usuario de forma manual. Ejemplos: despliegues, commits, flujos de generación de código.

```yaml
---
name: deploy
description: Deploy the application to production. Use when the user wants to deploy or release.
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite: `npm test`
2. Build: `npm run build`
3. Push to deployment target: `npm run deploy`
```

### 1.4 Divulgación progresiva (progressive disclosure)

Las skills se cargan en tres capas para optimizar el uso del contexto:

| Capa | Contenido | Cuándo se carga | Coste en tokens |
|------|-----------|-----------------|-----------------|
| **Metadatos** | `name` + `description` del frontmatter | Siempre en memoria | ~100-200 tokens por skill |
| **Cuerpo** | Contenido completo del SKILL.md | Solo cuando la skill se activa | Variable (apunta a < 500 líneas) |
| **Recursos** | Archivos complementarios (scripts, referencias, guías) | Bajo demanda, cuando se referencian | Variable |

Este sistema evita sobrecargar el contexto con skills no utilizadas. Escribe tu skill sabiendo que su cuerpo solo se carga cuando es relevante — haz que la descripción sea lo suficientemente buena para activar la carga, y mantén el cuerpo centrado en la ejecución.

## 2. Frontmatter YAML

Todo SKILL.md comienza con un frontmatter YAML entre marcadores `---`. El frontmatter indica al agente cuándo y cómo utilizar la skill.

### 2.1 Campos esenciales

| Campo | Obligatorio | Descripción |
|-------|-------------|-------------|
| `name` | Sí | Identificador único. Se convierte en el `/slash-command`. Minúsculas, guiones, máximo 64 caracteres |
| `description` | Sí (muy recomendado) | Qué hace la skill y cuándo usarla. Es el **mecanismo principal de activación** |
| `argument-hint` | No | Texto de ejemplo mostrado en el autocompletado: `[domain] [table (optional)]` |

### 2.2 Descripción — el campo más importante

La `description` determina cuándo el agente carga tu skill. Los agentes tienden a **sub-activar** las skills, por lo que las descripciones deben ser proactivas.

**Patrón**: verbo de acción + qué hace + "Use when..." + palabras clave de activación

**Buena descripción:**
```yaml
description: >-
  Assess the current data quality coverage for a domain, table, or column.
  Use when the user wants to understand quality status, identify gaps,
  find uncovered dimensions, or check which columns need quality rules.
```

**Mala descripción:**
```yaml
description: Quality assessment tool
```

La mala descripción es demasiado vaga — rara vez se activará. La buena descripción incluye palabras clave específicas ("gaps", "uncovered dimensions", "quality rules") que coinciden con lo que los usuarios realmente dicen.

**Reglas de optimización:**
- Coloca el caso de uso principal al principio (primera frase)
- Incluye 3-5 palabras clave que el usuario probablemente usará
- Se recomiendan ~250 caracteres como máximo
- Incluye siempre una cláusula "Use when..."
- Si la skill NO debe activarse en algunos casos, menciónalo: "Do NOT use for X"

Para la referencia completa de campos con todos los campos opcionales, ejemplos y control de invocación, consulta `frontmatter-reference.md`.

## 3. Escritura del Cuerpo de la Skill

### 3.1 Explica el POR QUÉ, no solo el QUÉ

Los LLMs modernos generalizan bien cuando comprenden la razón detrás de una instrucción. En lugar de directivas rígidas, explica la motivación:

| Menos efectivo | Más efectivo |
|----------------|--------------|
| `ALWAYS validate the SQL` | `Validate the SQL before executing because a malformed query can silently return partial results, leading to incorrect analysis` |
| `NEVER use markdown tables` | `Format output as flowing prose paragraphs because the response will be read aloud by text-to-speech software, which cannot pronounce table structures` |
| `DO NOT skip profiling` | `Run profiling before analysis because without real data distribution knowledge, you may miss null patterns or outliers that invalidate statistical conclusions` |

Este enfoque (a veces llamado "teoría de la mente") es más efectivo que las directivas en MAYÚSCULAS porque el agente puede aplicar el principio subyacente a casos límite que no ha visto antes.

### 3.2 Estructura y formato

- Usa **secciones numeradas** para flujos de trabajo secuenciales: `## 1. Discovery`, `## 2. Analysis`
- Usa **tablas** para enrutar decisiones:
  ```markdown
  | Intención del usuario | Acción |
  |----------------------|--------|
  | "Analiza el dominio X" | Flujo completo (fases 1-5) |
  | "Solo muéstrame las tablas" | Saltar a la fase 1 únicamente |
  ```
- Usa **voz imperativa**: "Valida la entrada" (no "La entrada debería ser validada")
- Usa **bloques condicionales** para comportamiento opcional: "Si `output/MEMORY.md` existe, léelo para obtener contexto"

### 3.3 Presupuesto de instrucciones

Apunta a **150-200 instrucciones discretas** en una skill. Por encima de este umbral, el cumplimiento del LLM tiende a disminuir. Para cada línea, pregúntate: "¿Cometería el agente un error sin esta instrucción?" Si no, elimínala.

### 3.4 Claridad y especificidad

- Indica al agente qué **debe hacer**, no qué evitar. En lugar de "No uses markdown" → "Compón tu respuesta como párrafos de texto fluido"
- Define los términos ambiguos de forma explícita. Nunca uses "bueno", "profesional", "razonable" sin especificar qué significa en contexto
- Especifica el formato de salida deseado de forma explícita (tabla, lista, JSON, párrafo, bloque de código)
- Cuando muestres la salida esperada, proporciona un ejemplo concreto

### 3.5 Ejemplos (few-shot)

Incluye 2-5 ejemplos realistas cuando el comportamiento esperado no sea obvio:

- Los ejemplos deben ser **relevantes** (reflejar casos de uso reales), **diversos** (cubrir casos límite) y **estructurados** (formato consistente)
- Muestra pares de entrada → salida esperada
- Envuelve los ejemplos en bloques delimitados o usa separadores claros

### 3.6 Regla de portabilidad

No hagas referencia directa a nombres de archivo específicos de plataforma como `AGENTS.md`, `CLAUDE.md` u `opencode.json`. Los scripts de empaquetado renombran estos archivos según la plataforma de destino. Usa frases genéricas en su lugar:

| No escribas | Escribe en su lugar |
|-------------|---------------------|
| "As defined in AGENTS.md" | "As defined in the agent's instructions" |
| "Following the rules in CLAUDE.md" | "Following the agent's rules" |
| "Use the AskUserQuestion tool" | "Follow the user question convention" |

### 3.7 Longitud objetivo

Mantén el SKILL.md **por debajo de 500 líneas**. Si te acercas a este límite, extrae las secciones detalladas a archivos complementarios dentro de la carpeta de la skill (ver sección 4).

## 4. Archivos Complementarios

### 4.1 Cuándo extraer

Extrae contenido a un archivo separado cuando:
- El SKILL.md supere las ~300 líneas
- Una sección pueda consultarse de forma independiente (p. ej., una referencia de campos, un catálogo de patrones)
- El contenido sea material de referencia detallado que no se necesita en cada ejecución

### 4.2 Tipos de archivos

| Directorio | Propósito | Ejemplo |
|------------|-----------|---------|
| Raíz de la carpeta de la skill | Guías complementarias cargadas bajo demanda | `advanced-guide.md`, `field-reference.md` |
| `scripts/` | Scripts auxiliares que la skill invoca | `scripts/validate.py`, `scripts/generate.sh` |
| `references/` | Documentos de referencia estáticos (esquemas, especificaciones) | `references/api-schema.json` |
| `assets/` | Archivos usados en la generación de salida | `assets/template.html`, `assets/logo.png` |

### 4.3 Referenciar archivos complementarios

Haz referencia a los archivos desde el SKILL.md usando rutas relativas:

```markdown
For the complete field reference, see `frontmatter-reference.md`.
For writing patterns and anti-patterns, see `writing-patterns.md`.
```

Si una guía es compartida entre varias skills, colócala en `shared-skill-guides/` y declárala en un archivo de manifiesto `skill-guides` dentro del directorio de la skill (un nombre de archivo por línea).

### 4.4 Inyección dinámica de contexto

Usa la sintaxis `` !`command` `` para ejecutar comandos de shell e inyectar la salida antes de que el agente vea el contenido:

```markdown
## Current environment
- Node version: !`node --version`
- Git branch: !`git branch --show-current`
```

Para comandos multilínea:
````markdown
```!
git log --oneline -5
npm test -- --reporter=json 2>/dev/null | jq '.numPassedTests'
```
````

### 4.5 Archivos de referencia extensos

Para archivos de referencia de más de 300 líneas, incluye una tabla de contenidos al principio para que el agente pueda navegar directamente a la sección relevante.

## 5. Patrones y Anti-patrones

Para el catálogo completo de patrones de escritura con ejemplos de código concretos para cada uno, consulta `writing-patterns.md`.

Resumen de patrones clave:

- **Human-in-the-loop**: Presenta un plan completo → espera confirmación explícita → ejecuta. Nunca auto-ejecutes acciones destructivas o irreversibles
- **Salida estructurada**: Define el formato de salida con un ejemplo de esquema JSON o plantilla, no con descripciones vagas
- **Comportamiento condicional**: Comprueba si los recursos existen antes de usarlos ("si MEMORY.md existe, léelo")
- **Operaciones en paralelo**: Lanza operaciones independientes simultáneamente ("lanza todas las consultas independientes en paralelo")
- **Descripción proactiva**: Incluye palabras clave de activación que coincidan con el lenguaje real de los usuarios
- **Skills autocontenidas**: Todo el conocimiento necesario integrado — nunca dependas de conocimiento externo no verificable

## 6. Lista de Verificación de Calidad

Ejecuta esta lista de verificación antes de finalizar cualquier skill:

1. El frontmatter tiene `name` y `description`; la descripción comienza con verbo de acción e incluye "Use when..."
2. El cuerpo tiene menos de 500 líneas; se usan archivos complementarios para el excedente
3. No hay referencias directas a `AGENTS.md` ni a `CLAUDE.md` — se usan frases genéricas
4. No hay dependencias de herramientas, estilos o plantillas específicas de un agente
5. Las referencias a guías usan rutas relativas (`skills-guides/<file>` o nombre de archivo directo)
6. Secciones numeradas para flujos de trabajo secuenciales
7. Tablas para enrutar decisiones
8. Cada paso importante explica el POR QUÉ, no solo el QUÉ
9. Human-in-the-loop para acciones destructivas o irreversibles
10. Instrucciones en voz imperativa
11. Al menos un ejemplo de entrada/salida incluido
12. Nombre en kebab-case (minúsculas, guiones)
13. Todo el conocimiento necesario está integrado — la skill no depende de conocimiento externo no verificable
14. La descripción es lo suficientemente proactiva para activarse cuando sea relevante
