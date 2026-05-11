# create-quality-rules

Designs and creates data-quality rules in Stratio Governance with **mandatory human confirmation before execution**. Supports two entry flows: **Flow A** (cover gaps identified by a prior `assess-quality` run) and **Flow B** (create a specific rule described by the user, without a prior assessment).

Scheduling (Quartz cron) and measurement configuration (percentage/count × exact/range thresholds) are negotiated together with the approval step — never as a separate afterthought.

## What it does

- **Flow A — gaps:** reads the inventory of existing rules (`get_tables_quality_details`) and the prior EDA from `assess-quality`, then designs rules only for dimensions/columns not already covered.
- **Flow B — specific rule:** fetches columns, table details and dimension definitions, then designs a single rule from the user's description.
- Designs each rule with: kebab-case name (`dq-[table]-[dimension]-[column]`), business-language description (no scheduling, no technical column names, no dimension mention), SQL `query` (numerator — records that pass) and `query_reference` (denominator — total), dimension, measurement type + threshold configuration, and optional cron schedule.
- Covers seven dimensions with canonical SQL patterns: `completeness`, `uniqueness`, `validity` (numeric range, enumeration, date), `consistency` (intra-row and across tables), `timeliness`, `accuracy`.
- **SQL validation is mandatory** before the approval step: runs `execute_sql(query, limit=1)` on both SQLs, computes the current result and status (OK / KO / WARNING / NO_DATA) and shows it in the plan.
- Presents the full plan and waits for explicit approval. Asks scheduling and measurement together with the approval — no silent defaults.
- Creates rules sequentially (not parallel) and reports per-rule `[OK]` / `[ERR]` status in chat.
- Refreshes AI metadata (`quality_rules_metadata`) after creation and shows a before-vs-after coverage table.

## When to use it

- Follow-up of `assess-quality` to cover the identified gaps (Flow A).
- Ad-hoc creation of a specific rule (FK check, non-negative amount, custom accuracy reconciliation) without running a full assessment first (Flow B).
- For scheduling **already-existing** rules, prefer `create-quality-schedule` — that is a folder-level scheduler for batches of rules.

## Dependencies

### Other skills
- **Typical predecessor for Flow A:** `assess-quality`.
- **Typical next step:** `create-quality-schedule` (folder-level automation) or `quality-report` (formalise the outcome).
- **Reference to load beforehand:** `stratio-data` (MCP rules).

### Guides
- `quality-exploration.md` — mandatory `get_quality_rule_dimensions` step and EDA signals per column type; drives Flow A reasoning and Flow B dimension choice.

### MCPs
- **Data (`sql`):** `get_table_columns_details`, `get_tables_details`, `generate_sql`, `execute_sql`.
- **Governance (`gov`):** `get_quality_rule_dimensions`, `quality_rules_metadata`, `get_tables_quality_details`, `create_quality_rule`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Critical approval pause:** `create_quality_rule` is **never** called without explicit user confirmation. Silence or ambiguity is not approval. Approval from a previous batch in the same conversation is not valid for a new batch.
- **SQL validation is mandatory, not optional.** Only rules whose queries have been successfully executed can be part of the plan presented to the user.
- **Never use current min/max from EDA as validity thresholds.** Thresholds come from business logic; EDA only parameterises and prioritises.
- **Measurement default** is `percentage` + `exact` (=100% OK, !=100% KO). Four other combinations (count/exact, percentage/range, count/range) are offered when the user asks.
- **Scheduling timezone** defaults to `Europe/Madrid` unless the user explicitly requests another. Very-low-frequency cron expressions (every second/minute) are blocked.
- **Sequential execution is intentional** so the user can interrupt if something goes wrong.
