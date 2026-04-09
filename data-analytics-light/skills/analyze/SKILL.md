---
name: analyze
description: "Full BI/BA data analysis — domain discovery, EDA and data quality, metric and KPI planning with analytical framework, data queries via MCP, Python analysis with pandas, visualizations. Use when the user needs to analyze business data, calculate KPIs, produce visualizations, generate graphic summaries, obtain insights, or answer analytical questions about governed domains. Also activates for multi-metric comparisons, KPI overviews, or any request requiring data crossing across dimensions."
argument-hint: "[analysis question or topic]"
---

# Skill: Full BI/BA Analysis

This guide defines the complete workflow for performing a Business Intelligence / Business Analytics analysis.

## 1. Parse the Request

- Extract the main business question from the argument: $ARGUMENTS
- Identify implicit sub-questions
- Detect if it mentions a specific domain, tables, or metrics

### 1.1 Quick triage

If the request can be resolved with a single MCP call (see Phase 0), respond directly:
- Definitions/concepts → `search_domain_knowledge` → chat
- Structure/columns → `list_domain_tables` / `get_table_columns_details` → chat
- Point data → `query_data` → chat
- In these cases, DO NOT continue with the rest of the workflow

If the request requires analysis (data cross-referencing, hypotheses, visualizations, multiple metrics), continue with section 2.

## 2. Domain Discovery

If the domain is already known from the conversation (identified and explored in prior turns), skip this section and proceed to section 3. Use the domain and table context already established.

Read and follow `skills-guides/stratio-data-tools.md` sec 4 for domain discovery steps (search or list domains, select, explore tables, columns, and terminology).

## 3. EDA and Data Quality

Before asking the user and planning metrics, understand the reality of the data:

1. **Profiling**: Run `profile_data` on the key tables identified in step 2. Follow the mechanics and adaptive thresholds of `skills-guides/stratio-data-tools.md` sec 5
2. **Assess quality**:
   - **Completeness**: % of nulls per column. Flag columns with >50% nulls as a limitation
   - **Time range**: Verify that the data covers the period the user needs
   - **Outliers**: Identify extreme values (IQR) that could bias averages or totals
   - **Distributions**: Skewness in numerics, imbalance in categoricals
   - **Correlations**: Strong relationships between variables (|r| > 0.7) — may indicate multicollinearity or redundancy
   - **Cardinality**: Categoricals with >100 unique values are difficult to visualize or group
3. **Sufficiency checklist** — Apply BEFORE asking the user:

   | Criterion | Minimum threshold | If it fails |
   |-----------|-------------------|------------|
   | Records | >0 | STOP — reformulate query |
   | Temporal completeness | >=80% of the requested period | Offer analysis of the available period |
   | Nulls in key vars | <30% | Alert severe limitation, consider imputation |
   | Size for inference | n >= 30 | Report as exploratory, without statistical tests |
   | Variability | std > 0 in key numerics | Exclude constant variable |
   | Granularity | Requested level available | Offer aggregation to the available level |

4. **Data Quality Score**: HIGH (80-100%), MEDIUM (60-79%), LOW (<60%). If LOW, recommend improving data or reformulating
5. **Inform the user**: Generate a quality mini-summary + Data Quality Score before asking about depth. Example:
   - "**Quality: HIGH (85%)**. Data covers from January 2023 to December 2025. The `descuento` column has 35% nulls. 12 outliers were detected in `importe_total` (>3 IQR). The distribution of `categoria_producto` is concentrated: 3 of 15 categories represent 80% of records."
6. **Adjust expectations**: If there are serious limitations, warn the user that certain metrics or visualizations may not be reliable

## 4. Classification and Questions to the User

> **Note**: All questions with options in this section follow the question convention (sec 10).

### 4.0 Triage vs Analysis

Simple questions (point data, no breakdown dimensions) are resolved in Triage (Phase 0 of the workflow) without invoking this skill. Everything else is an analysis and follows the question block flow described below.

### 4.1 Block 1 — Depth, Audience, and Testing

A single interaction:

| # | Question | Options (literal) | Selection | Condition |
|---|---------|-------------------|-----------|-----------|
| 1 | What analysis depth do you prefer? | **Quick** · **Standard** (Recommended) · **Deep** | Single | Always |
| 2 | What audience is the analysis for? | **C-level/Executive** · **Manager/Lead** · **Technical/Data team** · **Mixed/General** | Single | Always |
| 3 | Do you want unit tests to be generated and run on the Python code? | **Yes** (Recommended): improves precision and quality, but consumes more time, cost, and context · **No**: direct execution without tests | Single | Standard/Deep only |

**Adaptive rule**: If the user's request already specifies information that answers any of these questions, pre-fill that answer and do not ask it again. For example: if the user said "quick analysis", pre-fill depth as Quick; if the user said "executive summary", pre-fill audience as C-level/Executive. Only ask questions whose answers cannot be inferred from the request.

- Tests validate transformations and calculations before running with real data. They improve precision but consume more tokens, time, and cost. **In Quick depth, testing is automatically disabled without asking the user.**

## 5. Planning

Develop a detailed plan following the analytical framework (sec "Analytical Framework" in AGENTS.md):

### 5.1 Analytical approach

Determine if the question requires descriptive analysis, rule-based segmentation, or advanced statistical techniques:

| Scenario | Recommendation |
|----------|---------------|
| Describe what happened and why | Descriptive analysis (pandas, groupings, comparisons) |
| Segment customers/products | Rule-based segmentation or RFM → sec 5.8 |
| Project trends | Statistical techniques (statsmodels, seasonal decompose) → sec 5.6 |
| Detect patterns and anomalies | Advanced statistical analysis → sec 5.6 |

### 5.2 Hypotheses
Formulate hypotheses BEFORE querying data. Use the template from sec "Analytical thinking" in AGENTS.md. For each sub-question identified in step 1:
- What we expect to find and why
- What result would be surprising
- Document the hypotheses in the plan to validate them later with data
**Full example:**
```
### H1: Q4 sales >=30% higher than Q1-Q3 average due to retail seasonality
- Statement: The ratio sales_Q4 / average(sales_Q1-Q3) is >= 1.30
- Rationale: Seasonal peak observed in Nov-Dec during EDA
- How to validate: query "total sales by quarter for the last year"
- Criterion: ratio >= 1.30
-> Result: CONFIRMED (ratio = 1.45)
-> Evidence: Q4 = EUR2.1M vs Q1-Q3 average = EUR1.45M
-> So What: Q4 = 36% of annual sales. Adjust inventory from Oct, reinforce logistics in Nov
-> Confidence: High (3 years of data, consistent pattern)
```

### 5.3 Metrics and KPIs

For each KPI, document:

| Field | Description |
|-------|-------------|
| Name | Clear identifier |
| Formula | Exact calculation |
| Granularity | Temporal: daily/weekly/monthly/quarterly |
| Dimensions | Breakdown axes (region, product, segment) |
| Benchmark | Target, industry average, or previous period |
| Source | Domain table(s) and column(s) |
| Statistical test | If it requires CI or comparison between groups (see section 5.6 of this skill) |

**Benchmark Discovery** — Scale based on depth (see activation matrix):
- **Quick**: Do not actively search. Use natural temporal comparison if the query already includes a time dimension
- **Standard**: Silent best-effort:
  1. `search_domain_knowledge("target/objetivo de [KPI_name]", domain)`
  2. Additional MCP query for the same KPI in period T-1
  3. If no external reference: mean/median as internal reference
  No benchmark → report the data normally
- **Deep**: Steps 1-3 + trend if >6 time points + ask the user

### 5.4 Data questions
List of natural language questions for `query_data`. NEVER write SQL.

For formulation best practices and query strategy (planning order, parallel execution), see `skills-guides/stratio-data-tools.md` sec 9.

### 5.5 Visualizations

See [visualization.md](visualization.md) for visualization and data storytelling principles.

For each visualization in the plan, define:
- **Analytical question** it answers
- **Chart type**: Select based on the analytical question (see selection guide in [visualization.md](visualization.md))
- **Variables**: What goes on each axis, groupings, filters
- **Title**: Formulated as an insight, not as a description
- **Source data**: MCP query that feeds the visualization

### 5.6 Advanced analytical techniques

Activate based on the selected depth (see activation matrix):
- **Standard**: Consult [advanced-analytics.md](advanced-analytics.md) when relevant
- **Deep**: Consult [advanced-analytics.md](advanced-analytics.md) systematically

Covers: statistical rigor (tests, CI, effect sizes), prospective analysis (scenarios, Monte Carlo), root cause analysis, anomaly detection.

### 5.7 Additional analytical patterns

Detailed implementation of patterns whose trigger is in sec 3.2 (Lorenz/Gini, mix, indexing, deviation vs reference, gap).

When a pattern is activated: consult [analytical-patterns.md](analytical-patterns.md) for MCP query, Python, and interpretation.

### 5.8 Segmentation and clustering

For a complete segmentation guide (RFM, clustering, validation, profiling), see [clustering-guide.md](clustering-guide.md).

Use when the user asks for segmentation, customer/product grouping, or profile discovery. The guide covers:
- Decision table (when to use rule-based or RFM)
- RFM with quintiles and business labels
- Mandatory segment profiling

### 5.9 Results presentation structure
Analysis sections and narrative order for presenting in chat. Apply data storytelling principles (section 7.1)

### 5.10 Present plan
Present the full plan to the user and request approval before execution

## 6. Execution

### 6.0 Data retrieval
- Use `query_data(data_question=..., domain_name=..., output_format="dict")` for each data question. **Launch in parallel** all independent queries defined in the plan (step 5.4). Only serialize if one query needs the result of another to be formulated
- Follow all rules from `skills-guides/stratio-data-tools.md` (MCP-first, output_format, no manual SQL, parallel execution)
- Save intermediate data as CSV only if a subsequent script needs them as input

### 6.1 Post-query validation (mandatory)
Apply the 7 validations from `skills-guides/stratio-data-tools.md` sec 7 to each received result. When queries are launched in parallel, validate each result as it arrives. If any fails: reformulate the question to the MCP, inform the user, adjust the plan.

### 6.2 Script development
- Write scripts with descriptive names that include the analysis context
- Each script should:
  - Read data from previously saved CSVs or receive data as a parameter
  - Perform transformations and calculations
  - Generate visualizations
- **Large datasets (>100k rows)**: Use stratified sampling for rapid development, full data for the final version

### 6.3 Testing

> **Only if depth is Standard/Deep AND the user chose "Yes" to the testing question in Block 1.** In Quick depth or if the user chose "No", skip this section and directly run the script with real data.

- Generate unit tests BEFORE running with real data
- Use mock DataFrames with structure similar to real data
- Validate transformations, calculations, and output formats
- Only proceed if tests pass

### 6.4 Execution with real data
Run scripts with real data.

### 6.5 Iteration loop

After reviewing initial results, assess whether they require iteration:

1. **Trigger**: Finding contradicts hypothesis, unexpected pattern, or unforeseen critical question
2. **Action**: Document finding → formulate new question(s) → additional MCP queries (6.0-6.1) → update scripts
3. **Limit**: Max 2 iterations. More → document as follow-up analysis
4. **Record**: For each iteration, document in chat: hypothesis → finding → new hypothesis → result

### 6.6 Complexity Upgrade

If during execution a finding is detected that exceeds the scope of the current complexity level:

**Triggers:**
- Anomaly: result differs >30% from the benchmark or from what is reasonable for the domain
- Inconsistency: two queries produce totals that don't add up (difference >5%)
- Critical pattern: Gini concentration >0.8, drop/growth >50% between periods, outlier in main KPI

**Action:**
1. Pause normal execution
2. Inform the user following the question convention (sec 10): "I have detected [finding description]. This requires additional investigation. Would you like me to dig deeper?" with options:
   - "Yes, dig deeper" → Escalate complexity, activate additional phases (full EDA, hypotheses about the finding, drill-down visualizations)
   - "No, just document it" → Record the finding in chat as "area for future investigation"
3. The upgrade does NOT restart the analysis — it extends the current analysis with additional phases

**Difference from the iteration loop (6.5):** The loop refines hypotheses within the same complexity level. The upgrade changes the level (e.g.: Triage → Analysis) and activates additional capabilities (EDA, formal hypotheses, visualizations).

### 6.7 Results presentation
Results are presented in chat, following the structure in section 7.1. Generated visualizations are shown inline as analysis support.

### 6.8 Final output validation
Before presenting to the user, verify:
- Visualizations were generated correctly
- Data used is internally coherent (totals add up, periods aligned)
- Findings pass the "So What?" checklist from section 7.1

If any visualization fails, regenerate it or present the data in table format.

## 7. Final Report

### 7.1 Chat report structure

When presenting findings in the conversation, follow this structure:

1. **Hook**: The most impactful finding first
2. Executive summary (3-5 bullets with "so what")
3. Insights with concrete data and comparative context (vs previous, vs target)
4. Prioritized actionable recommendations (high impact + high confidence first)
5. Limitations and caveats
6. Follow-up analysis suggestions

**Mandatory "So What?" checklist** — For EACH finding before including it:

| Question | Bad (data point) | Good (actionable insight) |
|----------|-----------------|--------------------------|
| **Magnitude?** | "Sales dropped" | "Dropped 12%, ~EUR45K/month" |
| **Vs. what?** | "North is doing well" | "North +23% vs national average, +8% vs target" |
| **What to do?** | "Improve retention" | "Loyalty program for Premium (45% vs 72% benchmark) -> ROI EUR120K/year" |
| **Confidence?** | "Customers prefer A" | Adapt to depth: Quick="67% (n=450, High)"; Standard="67% (n=450, CI95%: 62-72%)"; Deep="67% (n=450, CI95%: 62-72%, p<0.001)" |

If a finding does not pass all 4 questions → it is information, not insight. It does not go in the executive summary.

**Insight classification** — Determines placement in the report:
- **CRITICAL**: High impact + high confidence → Executive summary, firm recommendation
- **IMPORTANT**: High impact + low confidence → Main section, investigate further
- **INFORMATIONAL**: Low impact → Appendix, no recommendation

For data storytelling principles and mapping findings → narrative, read [visualization.md](visualization.md) sections 3 and 4.

## 8. Knowledge Proposal (Optional)

After presenting the final report, ask the user following the question convention (sec 10):
- **Yes**: Analyze the conversation and propose knowledge to the domain
- **No**: Finish without proposing

If accepted, load the skill `propose-knowledge` with the domain used in this analysis.
If declined, finish normally.

This step is ALWAYS optional. Never propose automatically.
