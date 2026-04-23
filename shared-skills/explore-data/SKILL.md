---
name: explore-data
description: "Quick exploration of data domains, tables, columns, statistical profiling, governance quality coverage and business terminology using the governed data MCPs. Use when the user wants to discover what data is available, understand a domain's structure, or explore tables and columns before an analysis."
argument-hint: "[domain (optional)]"
---

# Skill: Domain and Data Exploration

Guide for quickly exploring available data in governed domains.

## 1. Domain Discovery

Read and follow `skills-guides/stratio-data-tools.md` sec 4 for domain discovery steps (search or list domains, select, explore tables, columns and terminology).

If the user provides an argument ($ARGUMENTS), search with `search_domains($ARGUMENTS)`. If it matches a domain, skip directly to exploring tables. If it does not match, ask the user which domain to explore following the user question convention (adaptive to the environment: interactive if available, numbered list in chat otherwise). Ask if they want to drill into a specific table or see all of them.

## 2. Prior Domain Context

If `output/MEMORY.md` exists, read the "Known Data Patterns" section for the domain being explored. If there are registered patterns, inform the user before profiling (e.g.: "In previous analyses it was detected that column X has ~35% nulls").

## 3. Deepening (when scope is focused)

When the user is focused on a specific domain or a small subset of tables, add a lightweight enrichment step after exploring columns. Skip this for broad multi-domain exploration — profiling is costly.

For each key table identified, launch **in parallel**:
- `profile_data` per table — follow `skills-guides/stratio-data-tools.md` sec 5.1 (SQL generated with `generate_sql`, adaptive thresholds by size, `limit` parameter).
- `get_tables_quality_details(domain_name, [tables])` — see `skills-guides/stratio-data-tools.md` sec 5.2.

Summarize lightly (descriptive, do not turn this into an analysis):
- From `profile_data`: notable null percentages, temporal range if date columns exist, anomalous cardinalities or outliers worth flagging.
- From `get_tables_quality_details`: number of rules per table, status breakdown (OK / KO / WARNING / not-executed), dimensions with failing rules.

Feed both findings into the summary of section 4. If `profile_data` flags an anomaly that no governance rule tracks (uncovered dimension), call it out as a candidate for the `assess-quality` skill.

## 4. Summary and Proactive Suggestions

Present a structured summary:
- Domain explored and its purpose
- Number of available tables
- Main tables with their description
- Key columns identified
- Relevant business terms
- Statistical highlights (if profiling was performed in section 3)
- Governance quality coverage (if quality details were retrieved in section 3)

### Suggested analyses based on the domain structure and findings

After exploring, automatically detect analytical opportunities and present them to the user:

| If you find... | Suggest |
|----------------|---------|
| Date columns (date, timestamp, period) | "**Time trend** — How have the [metrics] evolved over time?" |
| Categories (region, product, segment, type) | "**Comparison/Pareto** — Where is 80% of [metric] concentrated? Which [dimension] stands out?" |
| Multiple related tables (FK, shared entities) | "**Cross-analysis** — What is the relationship between [table A] and [table B]? E.g.: customers x products" |
| Numeric + categorical variables together | "**Segmentation** — Are there natural groups? What [entity] profiles exist?" |
| Status or stage column (pipeline, phase, status) | "**Funnel** — What is the conversion rate between stages? Where is the most drop-off?" |
| Monetary columns (amount, price, cost, revenue) | "**Concentration** — Does 20% of [entities] generate 80% of [metric]?" |
| Registration date column + subsequent activity | "**Cohorts** — How are [entities] retained based on their start date?" |

Present as a prioritized list of 3-5 concrete suggestions, tailored to the actual tables and columns of the explored domain. Each suggestion should mention specific tables and columns.
