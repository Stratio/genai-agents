---
name: explore-data
description: "Quick exploration of data domains, tables, columns, statistical profiling and business terminology using the governed data MCPs. Use when the user wants to discover what data is available, understand a domain's structure, or explore tables and columns before an analysis."
argument-hint: "[domain (optional)]"
---

# Skill: Domain and Data Exploration

Guide for quickly exploring available data in governed domains.

## 1. Domain Discovery

Read and follow `skills-guides/stratio-data-tools.md` sec 4-5 for domain discovery steps (search or list domains, select, explore tables, columns, terminology and profiling).

If the user provides an argument ($ARGUMENTS), search with `search_domains($ARGUMENTS)`. If it matches a domain, skip directly to exploring tables. If it does not match, ask the user which domain to explore following the user question convention (adaptive to the environment: interactive if available, numbered list in chat otherwise). Ask if they want to drill into a specific table or see all of them.

## 2. Prior Domain Context

If `output/MEMORY.md` exists, read the "Known Data Patterns" section for the domain being explored. If there are registered patterns, inform the user before profiling (e.g.: "In previous analyses it was detected that column X has ~35% nulls").

## 3. Summary and Proactive Suggestions

Present a structured summary:
- Domain explored and its purpose
- Number of available tables
- Main tables with their description
- Key columns identified
- Relevant business terms
- Data quality observations (if profiling was performed)

### Suggested analyses based on the domain structure

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
