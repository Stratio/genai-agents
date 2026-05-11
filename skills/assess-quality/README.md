# assess-quality

Read-only assessment of data-quality coverage over a governed domain, table, or single column. Answers "which dimensions are monitored, which are missing, and which columns are priority candidates for new rules". The output is a structured summary in chat — the skill does **not** create rules or generate files by itself.

## What it does

- Determines the scope: full domain, specific table(s), or a single column.
- Loads the domain-specific dimension catalogue (`get_quality_rule_dimensions` — **mandatory**, because definitions of `completeness`, `validity`, etc. can differ by domain).
- Launches everything else in parallel: table list, existing-rule status (`get_tables_quality_details`), table and column semantics, and statistical profiling (`profile_data` via SQL generated with `generate_sql`).
- Builds a gap analysis that is **semantics-first** (what dimensions should exist given the business meaning of each column) and **EDA-validated** (confirms, prioritises and parameterises the gaps).
- Adjusts reasoning for technical domains (where business descriptions may be absent, EDA becomes the primary source).
- Presents results in five canonical sections: executive summary, dimension coverage table, existing-rules status, prioritised gaps, and recommended next steps.
- Ends with a follow-up question: create rules, generate a formal report, dig deeper, or stop.

## When to use it

- The user wants to know the current quality status of a domain or table.
- Before creating new quality rules — `assess-quality` determines the expected rules and the gaps that justify them.
- Before writing a formal quality report (the assessment feeds `quality-report`).
- For a full end-to-end pipeline "assess → create → report", the agent chains this skill with `create-quality-rules` and then `quality-report`.

## Dependencies

### Other skills
- **Companion reference:** `stratio-data` (MCP rules and patterns).
- **Typical next steps:** `create-quality-rules` (to act on the gaps), `quality-report` (to formalise the assessment).

### Guides
- `stratio-data-tools.md` — flow for the data MCPs: domain discovery, SQL generation, parallel execution, `profile_data` thresholds.
- `quality-exploration.md` — mandatory `get_quality_rule_dimensions` step, EDA signals per column type (nulls → completeness, distinct_count → uniqueness, min/max → validity, etc.), and the technical-domain adjustment.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `generate_sql`, `profile_data`.
- **Governance (`gov`):** `get_quality_rule_dimensions`, `quality_rules_metadata`, `get_tables_quality_details`.

### Python
None — this is a prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Read-only:** the skill never calls `create_quality_rule` or any destructive MCP. If the user wants to act on the gaps, the agent delegates to `create-quality-rules` after explicit approval.
- **EDA is never used to *avoid* a rule:** zero nulls today do not cancel a `completeness` rule on an ID column — the rule still protects against future nulls.
- **Scale:** for domains with more than 10 tables, the skill assesses the tables the user mentions first and asks before continuing; full-domain profiling is expensive.
- **Coverage figure is an estimate** (expected rules vs. existing rules), not an exact metric. Use ranges when uncertain ("between 40% and 60% coverage").
