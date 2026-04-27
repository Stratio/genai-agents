---
name: assess-quality
description: "Assess the current data quality coverage for a full domain, a specific table, or a particular column. Returns an analysis of which dimensions are covered, which are missing, and which columns are priorities for new rules. Use when the user wants to understand the quality status of their data."
argument-hint: "[domain] [table (optional)] [column (optional)]"
---

# Skill: Quality Coverage Assessment

Complete workflow for assessing the state of data quality in a governed domain, table, or column.

## 1. Scope Determination

Before executing any MCP call, determine exactly what will be assessed:

**If the domain is unclear or the `domain_name` needs validation**: follow `skills-guides/stratio-data-tools.md` sec 4.1-4.2 for the standard discovery workflow. If the domain is technical, use `search_domains(search_text, domain_type="technical")` or `list_domains(domain_type="technical")` (see `skills-guides/quality-exploration.md` sec 1 for technical domain details). Note that semantic analysis will be more limited for technical domains: business descriptions, table context, and terminology may be absent or partial.

**Determine scope:**
- **Full domain**: assess all its tables
- **Specific table**: assess only that table
- **Multiple tables**: assess the indicated subset
- **Specific column**: assess a single column within a table (requires domain + table + column)

## 1.5 CDE Check

Before launching data collection, check whether the domain has Critical Data Elements defined. This determines the effective assessment scope.

Call `get_critical_data_elements(collection_name=domain_name)`.

**If CDEs exist** (`critical_tables` or `columns_by_table` are non-empty):
- Inform the user: "This domain has Critical Data Elements defined. The assessment will focus on the marked critical assets."
- Build the effective scope:
  - Tables in `critical_tables` → assess all their columns (entire table is critical)
  - Tables in `columns_by_table` → include in assessment, but in section 3.2 (gap analysis) restrict to the listed columns for that table; mention to the user which columns are CDEs
  - Tables not in either list → exclude from assessment unless explicitly requested by the user
- Store in working context: `cde_mode=true`, `cde_full_tables` (list from `critical_tables`), `cde_partial_tables` (dict from `columns_by_table`)

**If no CDEs** (both `critical_tables` and `columns_by_table` are empty or absent):
- Inform the user: "No Critical Data Elements are defined for this domain. The assessment will cover all domain assets."
- Continue with the standard workflow (`cde_mode=false`).

**Special cases:**
- **Specific table or column explicitly requested by the user**: if the requested asset is not in any CDE list, still evaluate it as requested (user request overrides CDE filter). Always mention whether the asset is a CDE or not.
- **Specific column scope**: the CDE check is informative only — evaluate the requested column normally and mention if it is or is not marked as a Critical Data Element.

## 2. Data Collection (in parallel)

Once the scope is determined, launch in parallel. It is **MANDATORY** to include `get_quality_rule_dimensions` to understand what dimensions the domain supports and their definitions.

**About dimensions**: see section 2 of `skills-guides/quality-exploration.md` to understand why `get_quality_rule_dimensions` is mandatory and how to use its results.

**For full domain:**
```
Parallel:
  A. list_domain_tables(domain_name)
  B. get_quality_rule_dimensions(domain_name=domain_name)  <-- MANDATORY
  C. quality_rules_metadata(domain_name=domain_name)           <-- update AI metadata, only if not executed before
```
Then, with the table list obtained from A, launch in parallel for ALL tables:
```
For each table (in parallel):
  get_tables_quality_details(domain_name, [table])
  get_table_columns_details(domain_name, table)
  get_tables_details(domain_name, [table])
  generate_sql("get all fields from table [table] without filters", domain_name)
```
Finally, use the generated SQLs to launch `profile_data(query=[sql])` in parallel.

**For specific table:**
```
Parallel:
  A. get_tables_quality_details(domain_name, [table])
  B. get_table_columns_details(domain_name, table)
  C. get_quality_rule_dimensions(domain_name=domain_name)  <-- only if not obtained before
  D. get_tables_details(domain_name, [table])                  <-- only if not obtained before
  E. generate_sql("get all fields from table [table] without filters", domain_name)
  F. quality_rules_metadata(domain_name=domain_name)           <-- only if not executed before
```
After obtaining E, launch `profile_data(query=[sql])`.

**For specific column:**
```
Parallel:
  A. get_tables_quality_details(domain_name, [table])
  B. get_table_columns_details(domain_name, table)
  C. get_quality_rule_dimensions(domain_name=domain_name)  <-- only if not obtained before
  D. generate_sql("get only the [column] field from table [table] without filters", domain_name)
  E. quality_rules_metadata(domain_name=domain_name)           <-- only if not executed before
```
After obtaining D, launch `profile_data(query=[sql])`.
In the subsequent analysis (section 3), filter everything to that column's scope: inventory of rules affecting that column, gaps only for that column, EDA only for that column.

**Note about `quality_rules_metadata`**: This call updates the AI metadata of the rules (description, dimension). It is executed without `quality_rules_metadata_force_update` — it only processes rules without metadata or modified ones. If it fails, continue without blocking: the workflow does not depend on it. **Note on permissions**: this tool requires write-level access; users with read-only roles will receive a 403 error. In that case, skip and continue — assessment is not blocked.

**Note**: Profiling (EDA) is fundamental for detecting real gaps (e.g., existing nulls without a completeness rule). If the domain has >10 tables, assess first those the user explicitly mentions and ask if they want to continue with the rest.

## 3. Coverage Analysis

With the collected data (including the EDA from `profile_data`), semantically analyze the coverage:

### 3.1 Existing rules inventory

Using the results from `get_tables_quality_details` (already obtained in phase 2), build for each table the inventory of currently defined rules:

- **Rule name** and dimension it covers (`completeness`, `uniqueness`, `validity`, etc.)
- **Column(s)** it applies to (inferred from the rule name and description)
- **Current status**: OK / KO / Warning and pass percentage

This inventory is the baseline: **only dimensions/columns NOT covered by any existing rule are gaps**. Never propose a rule that duplicates an existing one, even if its status is KO (in that case, report it as a rule to review, not as a gap).

If `get_tables_quality_details` returns an empty list for a table: the table has no rules defined → all semantic checks identified in 3.2 are gaps.

### 3.2 Gap assessment: Semantics first, EDA as validator

The analysis has two complementary sources with distinct roles:

**1. Semantic analysis (primary source — determines WHICH rules should exist)**

Domain semantics are the basis of reasoning. Before looking at the EDA, study in depth:
- **Domain description**: what does this business domain represent? What quality guarantees are inherent to its nature?
- **Business context of each table** (from `get_tables_details`): what process feeds this table? What is it used for? What business constraints apply?
- **Semantics of each column** (from `get_table_columns_details`): name, description, data type, whether it is mandatory, whether it is a key, whether it references another master
- **Documented business rules**: constraints already described in domain governance are immediate gaps if they have no associated rule

With this semantic reading, the model must reason **why** a column needs a specific dimension:

```
ID / primary key column       → completeness + uniqueness are mandatory by definition
Amount / metric column        → validity (range >= 0 or per business logic) is mandatory
Business date column          → validity (logical range) and completeness if it is a key field
Status / classification column → validity (enumeration with allowed business values)
FK / reference column         → completeness if mandatory + consistency if there is a master
Mandatory text column         → completeness (by business definition)
Free text / notes column      → case-by-case assessment; probably needs nothing
```

**2. EDA with `profile_data` (secondary source — confirms and quantifies)**

Once the expected rules are semantically determined, the EDA serves to:
- **Confirm** that the problem actually exists (a field that should be non-null — does it have real nulls?)
- **Prioritize** gaps by real impact: 30% nulls in an ID is more urgent than 0.1%
- **Parameterize** validity rules: EDA values guide ranges and enumerations (without using them as exact limits)
- **Detect gaps that semantics did not anticipate**: statistical anomalies indicating an undocumented quality problem

```
EDA usage by gap type:
Completeness → nulls > 0? Confirms the gap and gives the current failure %
Uniqueness   → distinct_count < count? Confirms real duplicates
Validity     → min/max/top_values guide the expected range or enumeration
Consistency  → cross related columns to detect inconsistencies
```

**The EDA is never the reason to NOT propose a rule** that semantics justify. If the EDA shows 0 nulls in an ID, the `completeness` rule is still necessary: it protects against future nulls. If it shows 100% nulls in a supposedly mandatory field, propose the rule informing the user of the current state.

**CDE gap escalation**: If `cde_mode=true` and a table or column is a Critical Data Element, escalate its gap priority one level: MEDIUM → HIGH, HIGH → CRITICAL. CDE assets represent business-critical data — any unprotected dimension carries a higher business risk by definition.

**Technical domains — gap analysis adjustment:**

When the domain is technical (discovered via `list_domains(domain_type="technical")`), business descriptions, table context, and terminology may be absent or very limited. In this case:
- **EDA becomes the primary reasoning source**: statistical patterns (nulls, duplicates, ranges, distributions) are the basis for identifying gaps.
- **Reason by column names and types**: use common conventions (`*_id` → key/FK, `*_date`/`*_dt` → date, `*_amount`/`*_amt` → amount, `*_code`/`*_status` → enumeration) to infer probable semantics.
- **Recommendations with lower semantic confidence**: without business descriptions, proposed rules should be marked as based on technical inference. Validate assumptions with the user before committing to `validity` rules (ranges, enumerations) that require business knowledge.
- The general flow (inventory → gaps → prioritize) remains identical; only the relative weight of sources changes.

### 3.3 Gap score calculation

For each table, estimate:
- **Expected rules**: sum of rules that should semantically exist
- **Existing rules**: how many of the expected actually exist
- **Estimated coverage**: existing_rules / expected_rules x 100

Present as an estimate with reasoning, not as an exact figure. Use ranges if there is uncertainty ("between 40% and 60% coverage").

## 4. Result Presentation

Structure the output in chat with the following sections:

### Section 1: Executive Summary
```
Domain/Table: [name]
Assessment date: [today]
Assessment mode: CDEs active — N full critical tables, M tables with specific CDE columns | Full domain assessment (no CDEs defined)
Tables analyzed: N
Existing rules: N
Estimated coverage: XX% (summarized reasoning)
Gaps identified: N critical, N moderate
```

### Section 2: Coverage Table by Dimension

For **domain or table** scope:
```markdown
| Table | CDE | Completeness | Uniqueness | Validity | Consistency | Coverage |
|-------|-----|-------------|------------|----------|-------------|----------|
| account | CDE | Partial (2/4) | OK | Gap | N/A | ~50% |
| card | CDE* | OK | OK | Partial | Gap | ~70% |
| order | — | Gap | N/A | N/A | N/A | ~10% |
```

`CDE` = entire table is a Critical Data Element; `CDE*` = only specific columns in the table are CDEs; `—` = not a CDE. Omit the CDE column when `cde_mode=false` (no CDEs defined in the domain).

For **specific column** scope:
```markdown
| Column | Type | CDE | Completeness | Uniqueness | Validity | Consistency | Coverage |
|--------|------|-----|-------------|------------|----------|-------------|----------|
| customer_id | INTEGER | CDE | OK | Gap | N/A | N/A | ~50% |
```

Omit the CDE column when `cde_mode=false`.

Use icons for better readability:
- OK / covered: indicates rule exists and passes
- Partial: some rule exists but does not cover everything expected
- Gap: no rule where one should exist
- N/A: this dimension does not make sense for this table/column
- KO/Warning: rule exists but is failing

### Section 3: Existing Rules Status

For each existing rule, show in a table:
```
| Rule | Table | Dimension | Status | % Pass | Observations |
```

If a rule is in KO or WARNING, highlight it as a priority action regardless of gaps.

### Section 4: Prioritized Gaps

List the most important gaps, ordered by priority:
1. Primary keys / IDs without completeness or uniqueness (CRITICAL)
2. Mandatory business fields without completeness (HIGH)
3. Amounts/metrics without validity (HIGH)
4. Dates without validity (MEDIUM)
5. Statuses/classifications without validity (MEDIUM)
6. Secondary fields without coverage (LOW)

For each gap indicate: table, column, missing dimension, potential impact.

### Section 5: Recommended Next Steps

Summarize recommended actions:
- If there are KO/WARNING rules: resolve those first before creating new ones
- If there are critical gaps: propose creating rules to cover them
- If coverage is good (>80%): acknowledge and mention optional improvements

## 5. Follow-up Question

At the end, ask the user with options how they want to continue, following the user question convention:
- **Create rules to cover the identified gaps**
- **Generate a formal coverage report**
- **Dig deeper into a specific table**
- **Do nothing else**

Do not propose automatic continuation without asking.
