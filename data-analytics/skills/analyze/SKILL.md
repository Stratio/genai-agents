---
name: analyze
description: "Full BI/BA data analysis — domain discovery, EDA and data quality, metric and KPI planning with analytical framework, data queries via MCP, Python analysis with pandas, visualizations, multi-format report generation, and reasoning documentation. Use when the user needs to analyze business data, calculate KPIs, produce visualizations, generate graphic summaries, obtain insights, or answer analytical questions about governed domains. Also activates for multi-metric comparisons, KPI overviews, deliverable requests (reports, dashboards), or any request requiring data crossing across dimensions."
argument-hint: "[analysis question or topic]"
---

# Skill: Full BI/BA Analysis

This guide defines the complete workflow for performing a Business Intelligence / Business Analytics analysis.

## 1. Parse the Request

- Extract the main business question from the argument: $ARGUMENTS
- Identify implicit sub-questions
- Detect if a domain, tables, or specific metrics are mentioned
- Detect if a preferred output format is mentioned

### 1.1 Quick triage

If the request can be resolved with a single MCP call (see Phase 0 of the workflow (AGENTS.md)), respond directly:
- Definitions/concepts → `search_domain_knowledge` → chat
- Structure/columns → `list_domain_tables` / `get_table_columns_details` → chat
- Point data → `query_data` → chat
- In these cases, do NOT continue with the rest of the workflow

If the request requires analysis (data crossing, hypotheses, visualizations, multiple metrics), continue with section 2.

## 2. Domain Discovery

If the domain is already known from the conversation (identified and explored in prior turns), skip this section and proceed to section 3. Use the domain and table context already established.

Read and follow `skills-guides/stratio-data-tools.md` sec 4 for the domain discovery steps (search or list domains, select, explore tables, columns, and terminology).

## 3. EDA and Data Profiling

Before asking the user about formats and planning metrics, understand the reality of the data on two complementary dimensions: the **statistical profile** (EDA) and the **governance quality coverage** already defined for those tables. Both run in parallel.

1. **Parallel launch** — For the key tables identified in step 2, launch together:
   - `profile_data` per table (statistical profiling — follow mechanics and adaptive thresholds from `skills-guides/stratio-data-tools.md` sec 5)
   - `get_tables_quality_details(domain_name, [tables])` (existing governance rules and their OK/KO/WARNING status)

2. **Evaluate statistical profile (from `profile_data`)**:
   - **Completeness**: % of nulls per column. Flag columns with >50% nulls as a limitation
   - **Time range**: Verify that the data covers the period the user needs
   - **Outliers**: Identify extreme values (IQR) that could bias averages or totals
   - **Distributions**: Skew in numerics, imbalance in categoricals
   - **Correlations**: Strong relationships between variables (|r| > 0.7) — may indicate multicollinearity or redundancy
   - **Cardinality**: Categoricals with >100 unique values are difficult to visualize or group

3. **Evaluate governance quality coverage (from `get_tables_quality_details`)**:
   - Count rules per table and overall
   - Classify by status: OK, KO, WARNING, not-executed
   - For each KO/WARNING rule, note the dimension and affected column
   - Identify whether any KO/WARNING rule affects a column the user plans to use for metrics, dimensions, or filters in their request
   - This is a **lightweight check**: a full coverage evaluation (dimension catalog, gap identification, prioritisation) is outside the scope of this skill. If the user explicitly asks for a full coverage assessment instead of an analysis, stop here and inform them that a dedicated coverage workflow is required — the agent will route accordingly per its instructions

4. **Sufficiency checklist** — Apply BEFORE asking about formats:

   | Criterion | Minimum threshold | If it fails |
   |-----------|-------------------|-------------|
   | Records | >0 | STOP — reformulate query |
   | Temporal completeness | >=80% of requested period | Offer analysis of available period |
   | Nulls in key vars | <30% | Alert severe limitation, consider imputation |
   | Size for inference | n >= 30 | Report as exploratory, no statistical tests |
   | Size for clustering | n >= 10 x features | Recommend descriptive analysis without segmentation |
   | Variability | std > 0 in key numerics | Exclude constant variable |
   | Granularity | Requested level available | Offer aggregation to available level |

5. **Data Profiling Score**: HIGH (80-100%), MEDIUM (60-79%), LOW (<60%) — derived from the statistical profile. If LOW, recommend improving data or reformulating.

6. **Governance Quality Status**: Summary derived from `get_tables_quality_details`. Format: `<N rules defined, X OK, Y KO, Z WARNING>` or `no governance rules defined for these tables`. If any KO/WARNING rule affects a relevant column, flag it with a ⚠️ marker.

7. **Inform the user**: Generate a combined mini-summary with both signals before asking about format and style. Examples:
   - "**Profiling: HIGH (85%)** · Data covers January 2023 to December 2025. The `descuento` column has 35% nulls. 12 outliers in `importe_total` (>3 IQR). The `categoria_producto` distribution is concentrated: 3 of 15 categories represent 80% of records.
     **Governance: 8 rules defined (6 OK, 1 KO, 1 WARNING)**. ⚠️ KO rule `validity-fecha_factura` affects a column you'll use for temporal aggregation — results for that dimension should be taken with care."
   - "**Profiling: MEDIUM (72%)** · 30% nulls in `importe`, 3-month data gap in Q2 2024. **Governance: no quality rules defined for these tables** — statistical profile is your only quality signal."
   - "**Profiling: HIGH (90%)** · no significant issues. **Governance: 5 rules defined, all OK**."

8. **Adjust expectations**: If there are serious limitations (LOW Profiling Score, KO rules on key columns, missing temporal coverage), warn the user that certain metrics or visualizations may not be reliable. When a KO rule affects a column central to the request, ask the user whether to:
   - Continue the analysis acknowledging the caveat in the deliverable
   - Exclude that column/dimension
   - Stop analysing and request a full coverage evaluation instead (a dedicated workflow outside the scope of this skill)

## 4. Classification and User Questions

> **Note**: All questions with options in this section follow the question convention.

### 4.0 Triage vs Analysis

Simple questions (point data, no slicing dimensions) are resolved in Triage (Phase 0 of the workflow) without invoking this skill. Everything else is an analysis and follows the question block flow described below.

### 4.1 Question Block — Depth, Audience, Format, Tests

A single interaction:

| # | Question | Options (literal) | Selection | Condition |
|---|----------|-------------------|-----------|-----------|
| 1 | What analysis depth do you prefer? | **Quick** · **Standard** (Recommended) · **Deep** | Single | Always |
| 2 | What audience is the analysis for? | **C-level/Executive** · **Manager/Lead** · **Technical/Data team** · **Mixed/General** | Single | Always |
| 3 | In what formats do you want the deliverables? | **Document** (PDF + DOCX) · **Web** (Interactive HTML with Plotly) · **PowerPoint** (.pptx) | Multiple | Always |
| 4 | Do you want unit tests to be generated and run on the Python code? | **Yes** (Recommended): improves precision and quality, but consumes more time, cost, and context · **No**: direct execution without tests | Single | Standard/Deep only |

**Adaptive rule**: If the user's request already specifies information that answers any of these questions, pre-fill that answer and do not ask it again. For example: if the user said "give me a PDF report", pre-fill format as Document; if the user said "quick analysis", pre-fill depth as Quick; if the user said "executive dashboard", pre-fill audience as C-level/Executive and format as Web. Only ask questions whose answers cannot be inferred from the request.

- Tests validate transformations and calculations before running with real data. They improve precision but consume more tokens, time, and cost. **In Quick depth, testing is automatically disabled without asking the user.**
- The format question ALWAYS allows multiple selection
- The format options are EXACTLY 3: Document (PDF + DOCX), Web, PowerPoint. Do not invent, omit, or substitute
- If no format is selected → no deliverables, the analysis is delivered only in chat + automatic report.md
- **If one or more formats are selected → deliverables ARE ALWAYS GENERATED, regardless of the chosen depth. Quick/Standard/Deep affects the analysis, not the deliverables.**
- Additional requirements via "Other" option (time filters, segments, mandatory metrics)

Structure and visual style are not asked here — they are asked later when loading `report/report.md`.

## 5. Planning

Develop a detailed plan following the analytical framework (sec "Analytical Framework" of AGENTS.md):

### 5.0 Historical context
Read in parallel (if they exist):
- `output/ANALYSIS_MEMORY.md` — quick triage: search for entries from the same domain. If there is a relevant entry, read its `analysis_memory.md` file referenced in the **Detail** field to obtain KPIs, insights, and reference baselines
- `output/MEMORY.md` — sec "Known Data Patterns" for the domain to anticipate known data problems

### 5.1 Additional libraries
Evaluate whether `requirements.txt` needs to be extended

### 5.2 Analytical approach: descriptive, segmentation, or feature importance

Determine whether the question requires only descriptive analysis or also segmentation/clustering or feature importance:

| Scenario | Recommendation |
|----------|----------------|
| Describe what happened and why | Descriptive analysis (pandas, groupings, comparisons) |
| Discover non-predefined groups/segments | Clustering (RFM, KMeans, DBSCAN). See [clustering-guide.md](clustering-guide.md) |
| Identify influential factors (>5 variables) | Exploratory feature importance. See [clustering-guide.md](clustering-guide.md) sec 7 |
| Temporal projection | Linear projection + CI95%. See [advanced-analytics.md](advanced-analytics.md) |

**Automatic detection**: If the question mentions "segment", "group", "profiles" → clustering. If it mentions "what factors influence", "what explains" → feature importance. If it asks for temporal projection → linear projection (not ML). Infer the type from the question and data, do not ask the user.

### 5.3 Hypotheses
Formulate hypotheses BEFORE querying data. Use the template from sec "Analytical thinking" of AGENTS.md. For each sub-question identified in step 1:
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
→ Result: CONFIRMED (ratio = 1.45)
→ Evidence: Q4 = EUR2.1M vs Q1-Q3 average = EUR1.45M
→ So What: Q4 = 36% of annual sales. Adjust inventory from Oct, reinforce logistics Nov
→ Confidence: High (3 years of data, consistent pattern)
```

### 5.4 Metrics and KPIs

For each KPI, document:

| Field | Description |
|-------|-------------|
| Name | Clear identifier |
| Formula | Exact calculation |
| Granularity | Temporal: daily/weekly/monthly/quarterly |
| Dimensions | Slicing axes (region, product, segment) |
| Benchmark | Target, industry average, or previous period |
| Source | Domain table(s) and column(s) |
| Statistical test | If it requires CI or group comparison (see [advanced-analytics.md](advanced-analytics.md)) |

**Benchmark Discovery** — Scale according to depth (see activation matrix in AGENTS.md sec 2):
- **Quick**: Do not actively search. Use natural temporal comparison if the query already includes a time dimension
- **Standard**: Silent best-effort:
  1. `search_domain_knowledge("target/objetivo de [KPI_name]", domain)`
  2. Additional MCP query for the same KPI in period T-1
  3. If no external reference: mean/median as internal reference
  Without benchmark → report the data normally, document in reasoning
- **Deep**: Steps 1-3 + trend if >6 temporal points + ask the user

Document the benchmark in the KPI's "Benchmark" field. Data without benchmarks are reported normally — the absence is only marked as a limitation in Deep depth.

### 5.5 Data questions
List of natural language questions for `query_data`. NEVER write SQL.

For formulation best practices and query strategy (planning order, parallel execution), see `skills-guides/stratio-data-tools.md` sec 9.

### 5.6 Visualizations

Read and follow [visualization.md](visualization.md) for chart selection and visualization principles.

For each visualization in the plan, define:
- **Analytical question** it answers
- **Chart type**: Select according to the table in [visualization.md](visualization.md) sec 1
- **Variables**: What goes on each axis, groupings, filters
- **Title**: Formulated as an insight, not a description
- **Source data**: MCP query that feeds the visualization

### 5.7 Advanced analytical techniques

Activate according to the selected depth (see activation matrix in AGENTS.md sec 2):
- **Standard**: Consult [advanced-analytics.md](advanced-analytics.md) when relevant
- **Deep**: Consult [advanced-analytics.md](advanced-analytics.md) systematically

Covers: statistical rigor (tests, CI, effect sizes), prospective analysis (scenarios, Monte Carlo), root cause analysis, anomaly detection.

### 5.8 Additional analytical patterns

Detailed implementation of patterns whose trigger is in sec "Operationalized analytical patterns" of AGENTS.md (Lorenz/Gini, mix, indexation, deviation vs reference, gap).

When a pattern is activated: consult [analytical-patterns.md](analytical-patterns.md) for MCP query, Python, and interpretation.

### 5.9 Segmentation and clustering

For the complete segmentation guide (RFM, clustering, validation, profiling), see [clustering-guide.md](clustering-guide.md).

Use when the user requests segmentation, customer/product grouping, or profile discovery. The guide covers:
- Decision table (when to use rule-based, RFM, KMeans, or DBSCAN)
- RFM with quintiles and business labels
- Basic clustering with elbow + silhouette
- Cluster validation and mandatory profiling

For feature importance as a complement to segmentation or descriptive analysis, see [clustering-guide.md](clustering-guide.md) sec 7.

### 5.10 Deliverable structure
Sections, content of each, format. Apply data storytelling principles (section 7.1)

### 5.11 Present plan
Present the complete plan to the user and request approval before executing.

At the end of the plan presentation, include a brief note:
> If you have additional documentation, reference benchmarks, previous reports, or complementary data that could enrich the analysis, you can share them now.

Do not make this note a blocking question. It is an invitation, not a mandatory step. If the user does not contribute anything, continue without waiting for additional response beyond plan approval.

## 6. Execution

### 6.0 Determine analysis folder
Generate name `YYYY-MM-DD_HHMM_descriptive_name` (lowercase, no accents, underscores, max 30 chars in the name). Announce in chat. Create subdirectories: `output/[ANALYSIS_DIR]/scripts/`, `output/[ANALYSIS_DIR]/data/`, `output/[ANALYSIS_DIR]/assets/`. If depth >= Standard, also create `output/[ANALYSIS_DIR]/reasoning/` and `output/[ANALYSIS_DIR]/validation/`.

Persist the approved plan in `output/[ANALYSIS_DIR]/plan.md`.
Write the plan as formulated in Phase 3 (section 5) and approved by the user:
hypotheses, metrics/KPIs, data queries, visualizations, deliverable structure,
complexity, depth, formats, and style.

### 6.1 Environment
The Python stack is provided by the environment (Cowork sandbox image or local venv); `python3` resolves automatically. If the analysis needs a library not in `requirements.txt`, `pip install <pkg>` in the current environment. For recurring deps, also add them to `requirements.txt` so the sandbox image picks them up on next rebuild.

### 6.2 Data retrieval
- Use `query_data(data_question=..., domain_name=..., output_format="dict")` for each data question. **Launch in parallel** all independent queries defined in the plan (step 5.5). Only serialize if one query needs another's result to be formulated
- Follow all rules from `skills-guides/stratio-data-tools.md` (MCP-first, output_format, no manual SQL, parallel execution)
- Save intermediate data in `output/[ANALYSIS_DIR]/data/` as CSV if needed for subsequent scripts

### 6.3 Post-query validation (mandatory)
Apply the 7 validations from `skills-guides/stratio-data-tools.md` sec 7 to each received result. When queries are launched in parallel, validate each result as it arrives. If any fails: reformulate the question to the MCP, inform the user, adjust the plan.

### 6.4 Script development
- Write scripts in `output/[ANALYSIS_DIR]/scripts/` with descriptive names that include analysis context
- Each script must:
  - Read data from `output/[ANALYSIS_DIR]/data/` (previously saved CSVs) or receive data as a parameter
  - Perform transformations and calculations
  - Generate visualizations in `output/[ANALYSIS_DIR]/assets/`
  - Produce outputs in `output/[ANALYSIS_DIR]/`
- **Large datasets (>100k rows)**: Use stratified sampling for rapid development, full data for the final version

### 6.5 Testing

> **Only if the depth is Standard/Deep AND the user chose "Yes" in the testing question of §4.1.** In Quick depth or if the user chose "No", skip this section and execute the script directly with real data.

- Generate `output/[ANALYSIS_DIR]/scripts/test_*.py` with unit tests BEFORE running with real data
- Use mock DataFrames with structure similar to real data
- Validate transformations, calculations, and output formats
- Run: `python3 -m pytest output/[ANALYSIS_DIR]/scripts/test_*.py -v`
- Only proceed if tests pass

### 6.6 Execution with real data
```bash
python3 output/[ANALYSIS_DIR]/scripts/my_script.py
```

### 6.7 Iteration loop

After reviewing initial results, evaluate whether iteration is needed:

1. **Trigger**: Finding contradicts hypothesis, unexpected pattern, or unforeseen critical question
2. **Action**: Document finding → formulate new question(s) → additional MCP queries (6.2-6.3) → update scripts
3. **Limit**: Max 2 iterations. More → document as follow-up analysis
4. **Record**: Each iteration in reasoning: hypothesis → finding → new hypothesis → result

### 6.8 Complexity Upgrade

If during execution a finding is detected that exceeds the scope of the current complexity level:

**Triggers:**
- Anomaly: result differs >30% from benchmark or from what is reasonable for the domain
- Inconsistency: two queries give totals that don't match (difference >5%)
- Critical pattern: Gini concentration >0.8, drop/growth >50% between periods, outlier in main KPI

**Action:**
1. Pause normal execution
2. Inform the user following the question convention: "I detected [description of finding]. This requires additional investigation. Would you like me to dig deeper?" with options:
   - "Yes, dig deeper" → Escalate complexity, activate additional phases (full EDA, hypotheses about the finding, drill-down visualizations)
   - "No, just document it" → Record finding in chat and in reasoning as "area for future investigation"
3. The upgrade does NOT restart the analysis — it extends the current analysis with additional phases

**Difference from the iteration loop (6.7):** The loop refines hypotheses within the same complexity level. The upgrade changes the level (e.g.: Triage → Analysis) and activates additional capabilities (EDA, formal hypotheses, visualizations).

### 6.9 Deliverable generation

> **MANDATORY if the user selected formats in §4.1.** The analysis depth (Quick/Standard/Deep) does NOT affect this step — if the user chose formats, all are generated.

1. Load `report/report.md` for deliverable packaging instructions
2. Generate ALL selected formats (do not omit any)
3. Verify existence of each file with `ls -lh` before reporting to the user (see Phase 4, step 10 of AGENTS.md)

### 6.10 Reasoning

Generate reasoning according to depth (see defaults in sec "Reasoning" of AGENTS.md):

- **Quick**: Do not generate file. Key notes are included in the chat report (sec 7.1).
- **Standard/Deep**: Follow the complete guide in [reasoning-guide.md](reasoning-guide.md). Generate `.md` only.

If the user requested a format override, apply their preference.

### 6.11 Final output validation

Run validation according to depth (see defaults in sec "Reasoning" of AGENTS.md):

- **Quick**: Block A only (file integrity). Report result in chat. Do not generate file.
- **Standard**: Blocks A + B + C. Generate `validation/validation.md`. Report summary in chat.
- **Deep**: Blocks A + B + C + D. Generate `validation/validation.md`. Report summary in chat.

For detail on each block, thresholds, and PASS/WARNING/FAIL criteria, see [validation-guide.md](validation-guide.md).

If the user requested a format override, apply their preference.

## 7. Final Report

### 7.1 Chat report structure

When presenting findings in conversation, follow this structure:

1. **Hook**: The most impactful finding first
2. Executive summary (3-5 bullets with "so what")
3. Insights with concrete data and comparative context (vs previous, vs target)
4. Prioritized actionable recommendations (high impact + high confidence first)
5. Limitations and caveats
6. Generated file paths
7. Follow-up analysis suggestions

**Mandatory "So What?" checklist** — For EACH finding before including it:

| Question | Bad (data) | Good (actionable insight) |
|----------|-----------|--------------------------|
| **Magnitude?** | "Sales dropped" | "Dropped 12%, ~EUR45K/month" |
| **Vs. what?** | "North is doing well" | "North +23% vs national average, +8% vs target" |
| **What to do?** | "Improve retention" | "Loyalty program for Premium (45% vs 72% benchmark) → ROI EUR120K/year" |
| **Confidence?** | "Customers prefer A" | Adapt to depth: Quick="67% (n=450, High)"; Standard="67% (n=450, CI95%: 62-72%)"; Deep="67% (n=450, CI95%: 62-72%, p<0.001)" |

If a finding does not pass the 4 questions → it is information, not insight. It does not go in the executive summary.

**Insight classification** — Determines placement in the report:
- **CRITICAL**: High impact + high confidence → Executive summary, firm recommendation
- **IMPORTANT**: High impact + low confidence → Main section, investigate further
- **INFORMATIONAL**: Low impact → Appendix, no recommendation

For data storytelling principles and mapping findings → narrative, read [visualization.md](visualization.md) sections 3 and 4.

## 8. Analysis Memory (Confirmation required)

After presenting the final report, ask the user (following the question convention):

"Would you like to save this analysis to persistent memory? The analysis registry (`ANALYSIS_MEMORY.md`) and the knowledge memory (`MEMORY.md`) will be updated."
- **Yes** → Continue with steps 8.1, 8.2, and 8.3
- **No** → Skip all memory writing steps. Finish without updating any memory files

The following steps are executed **only if the user responds "Yes"**:

**Language**: Write all memory content (detail file, index entries) in the user's language.

### 8.1 Create analysis detail file

Create `output/[ANALYSIS_DIR]/analysis_memory.md` with the full content:

```markdown
# Analysis Memory: Descriptive Title

- **Domain**: exact_domain_name
- **Question**: "User's original question"
- **Folder**: `output/YYYY-MM-DD_HHMM_name/`
- **Report**: `output/YYYY-MM-DD_HHMM_name/report.md`
- **KPIs**: KPI1: value (period), KPI2: value (period)
- **Insights**: Finding 1 (confidence), Finding 2 (confidence)
- **Data Profiling Score**: HIGH/MEDIUM/LOW (N%)
```

### 8.2 Add compact entry to the index

Add an entry at the end of `output/ANALYSIS_MEMORY.md` with only the triage fields:

```markdown
---

## YYYY-MM-DD HH:MM — Descriptive Title

- **Domain**: exact_domain_name
- **Summary**: Question + main finding in 1 sentence (max ~120 chars)
- **Detail**: `output/YYYY-MM-DD_HHMM_name/analysis_memory.md`

---
```

If `output/ANALYSIS_MEMORY.md` does not exist, initialize it from the template before adding the entry:

```bash
mkdir -p output
cp templates/memory/ANALYSIS_MEMORY.md output/ANALYSIS_MEMORY.md
```

Then append the entry at the end (chronological).

### 8.3 Knowledge Memory

After writing to ANALYSIS_MEMORY.md, invoke the skill `/update-memory` to update `output/MEMORY.md` with preferences, data patterns, and heuristics discovered in this analysis.

## 9. Knowledge Proposal (Optional)

After presenting the final report, ask the user following the question convention:
- **Yes**: Analyze conversation and propose knowledge to the domain
- **No**: Finish without proposing

If they accept, load the skill `propose-knowledge` with the domain used in this analysis.
If they decline, finish normally.

This step is ALWAYS optional. Never propose automatically.
