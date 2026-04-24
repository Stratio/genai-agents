# Patrones y antipatrones de escritura

Catálogo de patrones y antipatrones recomendados para escribir skills efectivas para agentes de IA. Cada entrada incluye un ejemplo concreto que muestra el enfoque correcto y el incorrecto.

## 1. Flujo de control

### ✅ Human-in-the-loop (confirmación humana)

Presenta un plan completo al usuario y espera confirmación explícita antes de ejecutar acciones con efectos secundarios.

**Bien:**
```markdown
## 3. Execution Plan

Before executing, present the complete plan to the user:

| # | Action | Target | Detail |
|---|--------|--------|--------|
| 1 | Create rule | `orders.amount` | NOT NULL check (completeness) |
| 2 | Create rule | `orders.email` | Regex format validation |
| 3 | Create rule | `orders.status` | Allowed values: ACTIVE, CLOSED |

**Wait for explicit confirmation** (words like "yes", "proceed", "ok", "approved",
or language equivalent) before executing any `create_rule` call.

If the user rejects or modifies any row, adjust the plan and present it again.
```

**Mal:**
```markdown
## 3. Execution

Create the quality rules based on the analysis results.
```

La versión incorrecta ejecuta automáticamente sin aprobación del usuario. Esto es peligroso para acciones que crean, modifican o eliminan recursos.

### ✅ Triage-first routing (clasificación inicial)

Comienza con una tabla de clasificación que enruta la intención del usuario a la acción o fase apropiada.

**Bien:**
```markdown
## Phase 0 — Triage

Before activating any skill, classify the user's request:

| User intent | Action |
|-------------|--------|
| "What tables are in domain X?" | Direct action: `list_domain_tables()` — no skill needed |
| "Analyze the quality of domain X" | Full workflow (phases 1-5) |
| "Create a rule that checks nulls in column Y" | Skip to phase 3 (specific rule creation) |
| "Generate a coverage report" | Load /quality-report skill |
```

**Mal:**
```markdown
## Instructions

Follow these steps for every request:
1. First, explore the domain
2. Then, analyze quality
3. Then, create rules
...
```

La versión incorrecta fuerza el mismo flujo pesado para todas las peticiones, incluso las más simples.

## 2. Formato de salida

### ✅ Salida estructurada con esquema

Define el formato de salida esperado de forma explícita, con un ejemplo concreto.

**Bien:**
```markdown
## 4. Report Data Structure

Save the report data to `output/report-input.json` using this exact schema:

```json
{
  "title": "Data Quality Coverage Report",
  "domain": "customers",
  "generated_at": "2025-01-15",
  "summary": {
    "rules_total": 42,
    "rules_ok": 38,
    "rules_ko": 4,
    "coverage_estimate": "78%"
  },
  "tables": [
    {
      "name": "orders",
      "coverage_estimate": "85%",
      "rules": [
        { "name": "orders_amount_not_null", "dimension": "completeness", "status": "OK" }
      ],
      "gaps": [
        { "column": "email", "missing_dimension": "validity", "priority": "high" }
      ]
    }
  ]
}
```

All fields are required. Do not add extra fields not shown in the schema.
```

**Mal:**
```markdown
## 4. Report

Generate a JSON file with the report data including the summary and table details.
```

La versión incorrecta deja el formato completamente a la interpretación del agente, lo que produce salidas inconsistentes.

### ✅ Indica qué HACER, no qué evitar

Formula las instrucciones en positivo.

**Bien:**
```markdown
Compose your response as flowing prose paragraphs with clear section headers.
Use inline code formatting only for technical identifiers like table names or column names.
```

**Mal:**
```markdown
Do not use markdown tables. Do not use bullet points. Do not use bold text.
Do not use numbered lists unless absolutely necessary. Avoid headers.
```

La versión buena establece un objetivo claro; la versión mala es un campo de minas de negaciones que aún deja al agente sin saber qué DEBE hacer.

## 3. Comportamiento condicional

### ✅ Check before using (verificar antes de usar)

Verifica que los recursos existen antes de referenciarlos.

**Bien:**
```markdown
## 2. Gather Context

If `output/MEMORY.md` exists, read the "Known Data Patterns" section for patterns
observed in previous sessions for this domain (3+ occurrences = mature pattern).

If the file does not exist, proceed without prior context — this is the first session.
```

**Mal:**
```markdown
## 2. Gather Context

Read `output/MEMORY.md` section "Known Data Patterns" for prior session context.
```

La versión incorrecta asume que el fichero existe y provocará un error en la primera sesión.

### ✅ Scope-dependent behavior (comportamiento según el alcance)

Ajusta el comportamiento en función del alcance de la petición.

**Bien:**
```markdown
**If full domain** (no specific table mentioned):
  1. List all tables: `list_domain_tables(domain_name)`
  2. For each table, launch profiling in parallel
  3. If > 10 tables, assess user-mentioned tables first, then ask to continue

**If specific table**:
  1. Skip table listing
  2. Profile only the target table
  3. No batching needed
```

## 4. Paralelismo

### ✅ Lanzar operaciones independientes simultáneamente

Instruye explícitamente la ejecución en paralelo para llamadas independientes.

**Bien:**
```markdown
## 2. Data Collection

Once the scope is determined, launch in parallel:

```
Parallel:
  A. list_domain_tables(domain_name)
  B. get_quality_rule_dimensions(collection_name=domain_name)
  C. quality_rules_metadata(domain_name=domain_name)
```

Then, with the table list from A, launch for ALL tables in parallel:

```
For each table (in parallel):
  get_tables_quality_details(domain_name, [table])
  get_table_columns_details(domain_name, table)
```
```

**Mal:**
```markdown
## 2. Data Collection

1. First, list the tables
2. Then, get the quality dimensions
3. Then, get the rules metadata
4. Then, for each table, get quality details
5. Then, for each table, get column details
```

La versión incorrecta serializa operaciones independientes, desperdiciando tiempo. Los pasos 1-3 pueden ejecutarse simultáneamente, y las operaciones por tabla también pueden ejecutarse en paralelo.

## 5. Ejemplos en skills

### ✅ Ejemplos realistas de entrada/salida

Incluye ejemplos concretos que reflejen el uso real.

**Bien:**
```markdown
## Example

**User says**: "What is the quality coverage of the customers domain?"

**Expected behavior**:
1. Validate domain: `search_domains("customers")` → `customers_v2`
2. Launch parallel data collection (section 2)
3. Analyze coverage (section 3)
4. Present coverage table:

| Table | Coverage | Completeness | Validity | Uniqueness | Gaps |
|-------|----------|-------------|----------|------------|------|
| orders | 85% | ✅ 3 rules | ✅ 2 rules | ❌ missing | email validity |
| clients | 40% | ✅ 1 rule | ❌ missing | ❌ missing | name, phone |
```

**Mal:**
```markdown
## Example

When the user asks about quality, assess the domain and report back.
```

La versión incorrecta es demasiado abstracta para guiar el comportamiento del agente.

## 6. Ejecución con subagentes

### ✅ Fork para tareas aisladas

Usa `context: fork` para tareas que no necesitan el historial de la conversación.

**Bien:**
```yaml
---
name: explore-codebase
description: Explore the codebase to find relevant files and patterns. Use when researching before implementation.
context: fork
agent: Explore
allowed-tools: Read Grep Glob Bash(git log *) Bash(git show *)
---

Search the codebase for:
1. Files matching the pattern described by the user
2. Related test files
3. Similar implementations that could be reused

Report: list of relevant files with brief descriptions of their role.
```

**Mal (para una tarea aislada):**
```yaml
---
name: explore-codebase
description: Explore the codebase
---

Search the codebase for files the user describes...
```

La versión incorrecta se ejecuta en línea, consumiendo la ventana de contexto de la conversación principal con resultados de exploración que el agente no necesita retener.

## 7. Claridad de las instrucciones

### ✅ Explicar el POR QUÉ (Theory of Mind)

**Bien:**
```markdown
Use the **exact** `domain_name` returned by `search_domains()` or `list_domains()`.
Never translate, paraphrase, or infer domain names, because the MCP server performs
an exact string match — even a minor difference (e.g., "Customers" vs "customers_v2")
will return an empty result or an error, silently breaking the entire workflow.
```

**Mal:**
```markdown
ALWAYS use the EXACT domain_name from the MCP. NEVER change it. This is CRITICAL.
```

Ambas versiones consiguen el mismo objetivo, pero la versión buena explica el mecanismo (coincidencia exacta de cadena) y la consecuencia (fallo silencioso). El agente puede entonces aplicar este principio a situaciones similares (nombres de tablas, nombres de columnas) incluso si la skill no las menciona.

## 8. Portabilidad

### ✅ Referencias genéricas a ficheros del sistema

**Bien:**
```markdown
Present the options to the user following the user question convention
(adaptive to the environment: interactive tool if available, numbered list in chat otherwise).
```

**Mal:**
```markdown
Use the `AskUserQuestion` tool to present options to the user.
```

La versión incorrecta solo funciona en Claude Code. En OpenCode, la herramienta se llama `question`. En entornos solo de chat, ninguna de las dos existe. La frase genérica permite que el script de empaquetado de cada plataforma sustituya la referencia correcta.

## 9. Dependencias

### ✅ Autocontenida con dependencias declaradas

**Bien:**
```markdown
## 1. Scope Determination

If the domain is unclear, follow the standard discovery workflow described in
`skills-guides/stratio-data-tools.md` section 4.1-4.2.
```

La skill referencia un guide compartido por su ruta estándar. Los scripts de empaquetado lo copian junto a la skill automáticamente.

**Mal:**
```markdown
## 1. Scope Determination

If the domain is unclear, follow the data exploration workflow. You probably
know how to do domain discovery — just use the appropriate MCP calls.
```

La versión incorrecta asume que el agente conoce el flujo. Puede que no sea así: diferentes agentes tienen diferentes capacidades y conocimiento.

## 10. Tamaño de la skill

### ✅ Modular con ficheros de apoyo

**Bien:**
```
my-skill/
  SKILL.md                  # ~200 lines: workflow + quick reference
  field-reference.md        # ~150 lines: detailed field documentation
  examples.md               # ~100 lines: extended examples catalog
```

En SKILL.md:
```markdown
For the complete field reference, see `field-reference.md`.
For additional examples beyond those shown here, see `examples.md`.
```

**Mal:**
```
my-skill/
  SKILL.md                  # ~800 lines: everything in one file
```

La versión incorrecta supera la recomendación de 500 líneas y obliga al agente a cargar todo el contenido aunque solo necesite una parte.

## 11. Activación

### ✅ Descripción proactiva con palabras clave de activación

**Bien:**
```yaml
description: "Assess the current data quality coverage for a domain, table, or column. Returns analysis of covered dimensions, missing gaps, and priority columns. Use when the user wants to understand quality status, identify gaps, check coverage, or find columns without quality rules."
```

**Mal:**
```yaml
description: "Quality assessment tool for data governance"
```

La descripción buena incluye palabras clave que los usuarios usan naturalmente: "quality status", "gaps", "coverage", "columns without rules". La descripción mala usa términos abstractos que no coinciden con el lenguaje del usuario.

### ✅ Evitar activaciones falsas

**Bien:**
```yaml
description: "Generate formal coverage reports in PDF, DOCX, or Markdown. Use when the user explicitly asks for a report file or document. Do NOT use for in-chat quality summaries — those are handled by assess-quality."
```

La exclusión explícita evita que la skill se active cuando el usuario solo quiere un resumen en el chat.

## 12. Código en skills

### ✅ Extraer código largo a scripts

**Bien:**
```markdown
## 4. Generate Report

Run the report generator:
```bash
python3 scripts/generate_report.py \
  --format pdf \
  --output "output/${slug}-${date}.pdf" \
  --input-file output/payload.json
```
```

**Mal (código inline > 20 líneas):**
```markdown
## 4. Generate Report

```python
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
# ... 80 more lines of Python code ...
```
```

Los bloques de código largos en línea hinchan la skill, son difíciles de mantener y no pueden probarse de forma independiente. Extráelos a `scripts/` e invócalos desde la skill.
