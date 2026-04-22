# Writing Patterns and Anti-patterns

Catalog of recommended patterns and anti-patterns for writing effective AI agent skills. Each entry includes a concrete example showing the right and wrong approach.

## 1. Control Flow

### ✅ Human-in-the-loop

Present a complete plan to the user and wait for explicit confirmation before executing actions with side effects.

**Good:**
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

**Bad:**
```markdown
## 3. Execution

Create the quality rules based on the analysis results.
```

The bad version auto-executes without user approval. This is dangerous for actions that create, modify, or delete resources.

### ✅ Triage-first routing

Start with a classification table that routes the user's intent to the appropriate action or phase.

**Good:**
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

**Bad:**
```markdown
## Instructions

Follow these steps for every request:
1. First, explore the domain
2. Then, analyze quality
3. Then, create rules
...
```

The bad version forces the same heavyweight workflow for every request, even simple ones.

## 2. Output Format

### ✅ Structured output with schema

Define the expected output format explicitly, with a concrete example.

**Good:**
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

**Bad:**
```markdown
## 4. Report

Generate a JSON file with the report data including the summary and table details.
```

The bad version leaves the format entirely to the agent's interpretation, leading to inconsistent outputs.

### ✅ Tell what TO DO, not what to avoid

Frame instructions positively.

**Good:**
```markdown
Compose your response as flowing prose paragraphs with clear section headers.
Use inline code formatting only for technical identifiers like table names or column names.
```

**Bad:**
```markdown
Do not use markdown tables. Do not use bullet points. Do not use bold text.
Do not use numbered lists unless absolutely necessary. Avoid headers.
```

The good version gives a clear target; the bad version is a minefield of negations that still leaves the agent unsure what TO do.

## 3. Conditional Behavior

### ✅ Check before using

Verify that resources exist before referencing them.

**Good:**
```markdown
## 2. Gather Context

If `output/MEMORY.md` exists, read the "Known Data Patterns" section for patterns
observed in previous sessions for this domain (3+ occurrences = mature pattern).

If the file does not exist, proceed without prior context — this is the first session.
```

**Bad:**
```markdown
## 2. Gather Context

Read `output/MEMORY.md` section "Known Data Patterns" for prior session context.
```

The bad version assumes the file exists and will cause an error on the first session.

### ✅ Scope-dependent behavior

Adjust behavior based on the scope of the request.

**Good:**
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

## 4. Parallelism

### ✅ Launch independent operations simultaneously

Explicitly instruct parallel execution for independent calls.

**Good:**
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

**Bad:**
```markdown
## 2. Data Collection

1. First, list the tables
2. Then, get the quality dimensions
3. Then, get the rules metadata
4. Then, for each table, get quality details
5. Then, for each table, get column details
```

The bad version serializes independent operations, wasting time. Steps 1-3 can run simultaneously, and the per-table operations can run in parallel too.

## 5. Examples in Skills

### ✅ Realistic input/output examples

Include concrete examples that mirror real usage.

**Good:**
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

**Bad:**
```markdown
## Example

When the user asks about quality, assess the domain and report back.
```

The bad version is too abstract to guide the agent's behavior.

## 6. Subagent Execution

### ✅ Fork for isolated tasks

Use `context: fork` for tasks that don't need conversation history.

**Good:**
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

**Bad (for an isolated task):**
```yaml
---
name: explore-codebase
description: Explore the codebase
---

Search the codebase for files the user describes...
```

The bad version runs inline, consuming the main conversation's context window with exploration results the agent doesn't need to retain.

## 7. Instruction Clarity

### ✅ Explain WHY (theory of mind)

**Good:**
```markdown
Use the **exact** `domain_name` returned by `search_domains()` or `list_domains()`.
Never translate, paraphrase, or infer domain names, because the MCP server performs
an exact string match — even a minor difference (e.g., "Customers" vs "customers_v2")
will return an empty result or an error, silently breaking the entire workflow.
```

**Bad:**
```markdown
ALWAYS use the EXACT domain_name from the MCP. NEVER change it. This is CRITICAL.
```

Both achieve the same goal, but the good version explains the mechanism (exact string match) and the consequence (silent failure). The agent can then apply this principle to similar situations (table names, column names) even if the skill doesn't mention them.

## 8. Portability

### ✅ Generic references to system files

**Good:**
```markdown
Present the options to the user following the user question convention
(adaptive to the environment: interactive tool if available, numbered list in chat otherwise).
```

**Bad:**
```markdown
Use the `AskUserQuestion` tool to present options to the user.
```

The bad version only works in Claude Code. In OpenCode, the tool is called `question`. In chat-only environments, neither exists. The generic phrase lets each platform's packaging script substitute the correct reference.

## 9. Dependencies

### ✅ Self-contained with declared dependencies

**Good:**
```markdown
## 1. Scope Determination

If the domain is unclear, follow the standard discovery workflow described in
`skills-guides/stratio-data-tools.md` section 4.1-4.2.
```

The skill references a shared guide by its standard path. Pack scripts copy it alongside the skill automatically.

**Bad:**
```markdown
## 1. Scope Determination

If the domain is unclear, follow the data exploration workflow. You probably
know how to do domain discovery — just use the appropriate MCP calls.
```

The bad version assumes the agent knows the workflow. It might not — different agents have different capabilities and knowledge.

## 10. Skill Size

### ✅ Modular with supporting files

**Good:**
```
my-skill/
  SKILL.md                  # ~200 lines: workflow + quick reference
  field-reference.md        # ~150 lines: detailed field documentation
  examples.md               # ~100 lines: extended examples catalog
```

In SKILL.md:
```markdown
For the complete field reference, see `field-reference.md`.
For additional examples beyond those shown here, see `examples.md`.
```

**Bad:**
```
my-skill/
  SKILL.md                  # ~800 lines: everything in one file
```

The bad version exceeds the 500-line guideline and forces the agent to load all content even when only part is needed.

## 11. Triggering

### ✅ Proactive description with activation keywords

**Good:**
```yaml
description: "Assess the current data quality coverage for a domain, table, or column. Returns analysis of covered dimensions, missing gaps, and priority columns. Use when the user wants to understand quality status, identify gaps, check coverage, or find columns without quality rules."
```

**Bad:**
```yaml
description: "Quality assessment tool for data governance"
```

The good description includes keywords users naturally say: "quality status", "gaps", "coverage", "columns without rules". The bad description uses abstract terms that don't match user language.

### ✅ Avoiding false triggers

**Good:**
```yaml
description: "Generate formal coverage reports in PDF, DOCX, or Markdown. Use when the user explicitly asks for a report file or document. Do NOT use for in-chat quality summaries — those are handled by assess-quality."
```

The explicit exclusion prevents the skill from triggering when the user just wants a chat-based summary.

## 12. Code in Skills

### ✅ Extract long code to scripts

**Good:**
```markdown
## 4. Generate Report

Run the report generator:
```bash
python3 scripts/quality_report_generator.py \
  --format pdf \
  --output "output/quality-report-${domain}-${date}.pdf" \
  --input-file output/report-input.json
```
```

**Bad (inline code > 20 lines):**
```markdown
## 4. Generate Report

```python
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
# ... 80 more lines of Python code ...
```
```

Long inline code blocks bloat the skill, are hard to maintain, and cannot be tested independently. Extract them to `scripts/` and invoke from the skill.
