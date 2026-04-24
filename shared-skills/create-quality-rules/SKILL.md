---
name: create-quality-rules
description: "Design and create data quality rules in Stratio Governance with mandatory human confirmation before execution. Use when the user wants to create a quality rule, cover uncovered dimensions, fix quality gaps from a prior assessment (Flow A), or add a specific validation on a column or table without prior assessment (Flow B). For scheduling the execution of existing rules, prefer create-quality-schedule."
argument-hint: "[domain] [table (optional)]"
---

# Skill: Quality Rule Creation

Workflow for designing, proposing, and creating quality rules with human approval. This skill has a mandatory prerequisite and a critical approval pause.

## PREREQUISITE

This skill has two entry flows with different prerequisites:

**Flow A — Gaps (requires prior coverage assessment):**
The user wants to cover coverage gaps (e.g., "create rules for domain X", "complete the coverage of table Y"). This flow requires that quality coverage has already been assessed for the indicated scope: inventory of existing rules (from `get_tables_quality_details`), identified gaps, and EDA results from `profile_data`. If this data is not available in the conversation context:
1. Inform the user that coverage must be assessed first
2. Stop so that the assessment is performed before continuing

**Flow B — Specific rule (does NOT require prior assessment):**
The user describes a specific rule they want to create (e.g., "create a rule that verifies every customer in table A exists in table B", "I want a validity rule that checks the amount is positive in transactions"). In this case, a prior coverage assessment is NOT required — go directly to the "Flow B: Specific Rule" section below.

## CRITICAL APPROVAL PAUSE

**NEVER call `create_quality_rule` without the user having explicitly confirmed the plan.**

This pause is the most important step in the entire skill. If there are doubts about whether the user has approved, ask again. Do not interpret silence or ambiguous responses as approval.

**The scheduling question is integrated into section 4 (approval).** It is not a separate step — it is presented together with the confirmation request so it is impossible to omit.

**Each invocation of this skill is independent.** An approval given earlier in the same conversation is NOT valid for a new batch of rules. Even if the user already approved a previous plan, section 4 must always be followed again from scratch.

---

## 1. Determine Tables with Gaps

From the coverage assessment results, retrieve the existing rules inventory obtained via `get_tables_quality_details`. This inventory is the source of truth: **only design rules for dimensions/columns NOT already covered by an existing rule**.

Identify:
- Which tables have coverage gaps (expected dimensions not covered by any existing rule)
- Which dimensions are missing in each table (considering both standard and domain-specific ones)
- Which are the priority gaps based on the prior EDA from `profile_data`

**About dimensions**: the domain definitions (obtained during the coverage assessment via `get_quality_rule_dimensions`) always prevail over standard ones. See section 2 of `skills-guides/quality-exploration.md`.

If the user has specified a subset ("only the account table"), respect that restriction.

If there are existing rules in KO or WARNING status: mention them as a priority action before creating new ones. Ask whether they want to resolve those first or continue with the gaps.

## 2. Rule Design (from the complete coverage assessment analysis)

The coverage assessment has already produced two sources of information that are used here directly — do not repeat any MCP calls unless the scope has changed:

**Source 1 — Semantic analysis** (from `get_tables_details` + `get_table_columns_details`):
The semantic analysis from the coverage assessment determined *why* each column needs each dimension: column role (key, metric, status, FK...), business mandatoriness, constraints documented in governance. That reasoning is the justification for each rule. Retrieve it and use it as the basis for the description and SQL design.

**Note for technical domains**: If the domain is technical, business descriptions may be limited or nonexistent. In that case, give greater weight to the EDA and reason by column names/types (conventions like `*_id`, `*_date`, `*_amount`). Validate assumptions with the user about semantics before designing `validity` rules (ranges, enumerations).

**Source 2 — EDA** (from `profile_data`):
Statistical profiling serves to parameterize and prioritize, not to decide whether a rule should exist:

| Gap type | EDA signals | Implication for SQL |
|----------|------------|---------------------|
| Completeness | `nulls > 0` | Confirms the problem; the current % guides urgency |
| Uniqueness | `distinct_count < count` | There are real duplicates; inform the user before creating the rule |
| Validity (range) | `min`, `max` | Guide the range — final thresholds should be based on business logic, not current values |
| Validity (enumeration) | `top_values` | Use as basis for the `IN (...)`, confirming with the user whether the list is exhaustive |
| Consistency | Related columns | May require cross-referencing data; design the SQL carefully |

**Attention**: If the EDA shows 100% nulls or completely invalid values, inform the user before creating the rule — but do not discard it if semantics justify it.

## 3. Rule Design

For each identified gap, design the corresponding quality rule.

### 3.1 Rule structure

Each rule has the following fields:
- `rule_name`: descriptive name in kebab-case. Convention: `dq-[table]-[dimension]-[column-or-description]`
- `primary_table`: main table the rule belongs to
- `table_names`: list of tables referenced in the SQLs (always include primary_table)
- `description`: concise natural language description in clear business terms (no technical jargon) of what this rule checks, describing the expected outcome. **Mandatory rules**: (1) Do NOT include scheduling or planning information (frequency, schedules, cron). (2) Do NOT use technical column names (like `card_id`, `district_id`); instead, use the semantic/business definition of the field obtained from `get_table_columns_details`. (3) Do NOT mention the rule dimension (completeness, uniqueness, validity, etc.) — the dimension is already a separate field. Correct example: "Validates that every account record has a non-null district identifier, ensuring all accounts are assigned to a district". Incorrect example: "Completeness check: Checks that district_id is never null. Scheduled daily at 09:00"
- `query`: SQL that counts the records that PASS the check (numerator)
- `query_reference`: SQL that counts the total number of records (denominator)
- `dimension`: completeness / uniqueness / validity / consistency
- `collection_name`: the domain's domain_name
- `measurement_type`: (optional) how the quality result is measured. Possible values:
  - `percentage` (default): compares query vs query_reference as a percentage
  - `count`: uses the absolute record count from the query
- `threshold_mode`: (optional) how evaluation thresholds are defined. Possible values:
  - `exact` (default): exact value with `=` and `!=` operators
  - `range`: ranges with operators like `>`, `<=`
- `exact_threshold`: (optional, only for `threshold_mode=exact`) object with:
  - `value`: comparison value (e.g., `"100"`, `"0"`)
  - `equal_status`: status when result = value (`OK`, `KO`, or `WARNING`)
  - `not_equal_status`: status when result != value (`OK`, `KO`, or `WARNING`)
  - Default: `{value: "100", equal_status: "OK", not_equal_status: "KO"}`
- `threshold_breakpoints`: (optional, only for `threshold_mode=range`) ascending ordered list of breakpoints. Each entry has:
  - `value`: upper limit of the interval (e.g., `"50"`, `"80"`)
  - `status`: status for that interval (`OK`, `KO`, or `WARNING`)
  - The **last entry** does NOT have a `value` (open-ended upper range); only `status`
  - Minimum 2 entries, at least one `OK` and one `KO`. See section 3.4
- `cron_expression`: (optional) Quartz cron expression for automatic execution. If not specified, the rule is not scheduled
- `cron_timezone`: (optional) cron timezone; if there is a cron and none is specified, use `Europe/Madrid`
- `cron_start_datetime`: (optional) ISO 8601 with the first scheduled execution; if not specified, scheduling starts immediately after creation

### 3.2 SQL patterns by dimension

**Completeness** — non-null column:
```sql
query:     SELECT COUNT(*) FROM ${table} WHERE column IS NOT NULL
reference: SELECT COUNT(*) FROM ${table}
```

**Uniqueness** — no duplicates in a column:
```sql
query:     SELECT COUNT(*) FROM (SELECT DISTINCT column FROM ${table})
reference: SELECT COUNT(*) FROM ${table}
```

**Uniqueness** — composite key:
```sql
query:     SELECT COUNT(*) FROM (SELECT DISTINCT col1, col2 FROM ${table})
reference: SELECT COUNT(*) FROM ${table}
```

**Validity (numeric range)**:
```sql
-- non-negative amount
query:     SELECT COUNT(*) FROM ${table} WHERE amount >= 0
reference: SELECT COUNT(*) FROM ${table}

-- age in logical range
query:     SELECT COUNT(*) FROM ${table} WHERE age BETWEEN 0 AND 150
reference: SELECT COUNT(*) FROM ${table}
```

**Validity (enumeration)**:
```sql
query:     SELECT COUNT(*) FROM ${table} WHERE status IN ('ACTIVE', 'INACTIVE', 'PENDING')
reference: SELECT COUNT(*) FROM ${table}
```

**Validity (date)**:
```sql
-- non-future date
query:     SELECT COUNT(*) FROM ${table} WHERE creation_date <= CURRENT_DATE
reference: SELECT COUNT(*) FROM ${table}

-- date in logical range
query:     SELECT COUNT(*) FROM ${table} WHERE creation_date BETWEEN '1900-01-01' AND CURRENT_DATE
reference: SELECT COUNT(*) FROM ${table}
```

**Consistency (between columns)**:
```sql
-- start date before or equal to end date
query:     SELECT COUNT(*) FROM ${table} WHERE start_date <= end_date OR end_date IS NULL
reference: SELECT COUNT(*) FROM ${table}
```

**Consistency (between tables)**:
```sql
-- valid FK: every record in table_a has its FK in table_b
query:     SELECT COUNT(*) FROM ${table_a} a WHERE EXISTS (SELECT 1 FROM ${table_b} b WHERE b.id = a.fk_id)
reference: SELECT COUNT(*) FROM ${table_a}
table_names: [table_a, table_b]
```

**Timeliness (data freshness)**:
```sql
-- record loaded in the last 24h
query:     SELECT COUNT(*) FROM ${table} WHERE load_date >= CURRENT_DATE - INTERVAL '1 day'
reference: SELECT COUNT(*) FROM ${table}
```

**Accuracy (truthfulness and precision)**:
```sql
-- amount matches the sum of its breakdown (reconciliation check example)
query:     SELECT COUNT(*) FROM ${header_table} c WHERE total_amount = (SELECT SUM(sub_amount) FROM ${detail_table} d WHERE d.parent_id = c.id)
reference: SELECT COUNT(*) FROM ${header_table}
table_names: [header_table, detail_table]
```

### 3.3 Design guidelines

- **NEVER use the current min/max of the data as validity thresholds**. Thresholds must be based on business logic (an amount might be -1 today but should not be valid). If you don't know the valid range, ask the user or use a conservative threshold
- **For enumerations**: use EDA values from the prior profiling only if the model is confident they are exhaustive. If in doubt, ask the user for the valid values
- **Completeness + always-null column**: if the prior EDA shows 100% nulls, inform the user and ask whether they still want the rule (it could be a field not yet in use)
- **Uniqueness + existing duplicates**: if there are duplicates, the rule will create an immediate KO. Inform the user of the current level before creating the rule

### 3.4 Measurement and Threshold Configuration

The parameters `measurement_type`, `threshold_mode`, and (`exact_threshold` or `threshold_breakpoints`) are **optional**. If the user chooses not to configure measurement, the defaults apply: `measurement_type=percentage`, `threshold_mode=exact`, `exact_threshold={value: "100", equal_status: "OK", not_equal_status: "KO"}`. The plan must always report the measurement configuration that will be applied to each rule (see section 4), and the measurement question is mandatory in the approval step — do not assume the default without asking.

#### Flow when the user asks to configure measurement

If the user references measuring quality, configuring thresholds, or requests a specific measurement type:

1. **Present the 4 available options** (see measurement types table below) with clear descriptions
2. **Collect the user's choice**: measurement type (`percentage`/`count`) + threshold mode (`exact`/`range`)
3. **If they choose `exact`**: ask for the exact value and statuses (e.g., "Is =100% OK and !=100% KO?")
4. **If they choose `range`**: ask how many levels (2 or 3) and the breakpoint values with their statuses
5. **Confirm the complete configuration** before applying it to the rule

Do not assume the measurement configuration — always iterate with the user until it is clear.

#### Available measurement types

| Type | `measurement_type` | `threshold_mode` | Description |
|------|-------------------|-----------------|-------------|
| Exact value (%) | `percentage` | `exact` | Compares query/reference as percentage, evaluates with exact value |
| Exact value (count) | `count` | `exact` | Uses absolute count from query, evaluates with exact value |
| Ranges (%) | `percentage` | `range` | Compares query/reference as percentage, evaluates with ranges |
| Ranges (count) | `count` | `range` | Uses absolute count from query, evaluates with ranges |

**Default behavior** (without parameters): `measurement_type=percentage`, `threshold_mode=exact`, `exact_threshold={value: "100", equal_status: "OK", not_equal_status: "KO"}`.

#### Guidelines for suggesting measurement type

If the user asks for a recommendation or is unsure which measurement type to use, these guidelines can help guide the conversation:

| Dimension / Case | Recommended type | Reason |
|------------------|-----------------|--------|
| Completeness, Uniqueness, Validity, Consistency | `percentage` + `exact` (=100% OK) | Total pass is expected; any failure is KO (**this is the default**) |
| Timeliness (freshness) | `count` + `exact` | The result is measured in absolute number of recent records |
| Rules with explicit user tolerance | `percentage` + `range` (2-3 levels) | Only if the user explicitly asks for an intermediate WARNING range |
| Rules with absolute count threshold | `count` + `range` | When limits are expressed in record count, not percentage |

These are guidelines for suggesting to the user — the final decision is always the user's. If the user explicitly indicates a measurement type, use that. **By default, always use exact measurement (=100% OK / !=100% KO) unless the user requests otherwise.**

#### Complete measurement parameter examples

Each example shows the parameters as they should be passed to `create_quality_rule`:

**Example 1 — Exact percentage (=100% OK / !=100% KO) [DEFAULT]:**
```json
measurement_type: "percentage"
threshold_mode: "exact"
exact_threshold: {"value": "100", "equal_status": "OK", "not_equal_status": "KO"}
```

**Example 2 — Exact count (=0 failing records OK):**
```json
measurement_type: "count"
threshold_mode: "exact"
exact_threshold: {"value": "0", "equal_status": "OK", "not_equal_status": "KO"}
```

**Example 3 — Range percentage 3 levels (<=50% KO, >50-80% WARNING, >80% OK):**
```json
measurement_type: "percentage"
threshold_mode: "range"
threshold_breakpoints: [
  {"value": "50", "status": "KO"},
  {"value": "80", "status": "WARNING"},
  {"status": "OK"}
]
```

**Example 4 — Range percentage 2 levels (<=90% KO, >90% OK):**
```json
measurement_type: "percentage"
threshold_mode: "range"
threshold_breakpoints: [
  {"value": "90", "status": "KO"},
  {"status": "OK"}
]
```

**Example 5 — Range count (<=50 KO, >50-100 WARNING, >100 OK):**
```json
measurement_type: "count"
threshold_mode: "range"
threshold_breakpoints: [
  {"value": "50", "status": "KO"},
  {"value": "100", "status": "WARNING"},
  {"status": "OK"}
]
```

**Requirements**: at least one entry with `status: "OK"` and one with `status: "KO"`. `WARNING` is optional. In `threshold_breakpoints`, entries must be ordered from lowest to highest value, and the last entry has no `value` (open-ended range).

## 3.5 SQL Validation (MANDATORY)

Before presenting the plan to the user, the technical validity of the designed queries must be verified.

**Validation procedure:**
1. For each designed rule, prepare the `query` and the `query_reference`.
2. Resolve the `${table}` placeholders by substituting them with the actual table name.
3. Execute both queries using `execute_sql(query=[sql], limit=1)`.
4. If any query returns an error:
   - Review the SQL syntax.
   - Adjust the rule design.
   - Re-validate until both queries are successful.
5. With both queries successful, calculate the result and the rule status:
   - Obtain `query_val` (numeric value from `query`) and `query_ref_val` (numeric value from `query_reference`).
   - If `measurement_type = "percentage"`: `result = (query_val / query_ref_val) * 100` rounded to 2 decimal places. If `query_ref_val == 0`, note `NO_DATA` (do not divide).
   - If `measurement_type = "count"`: `result = query_val`.
   - Evaluate the status according to `threshold_mode`:
     - `"exact"`: if `result == exact_threshold.value` → `equal_status`; otherwise → `not_equal_status`.
     - `"range"`: traverse `threshold_breakpoints` in ascending order; for the first point whose `value >= result`, use that `status`; if `result` exceeds all points with a value, use the `status` of the last point (open-ended range, no `value`).
   - The calculated status (`OK`, `KO`, `WARNING`, or `NO_DATA`) is included in the **Validation result** field of the plan (see section 4).

Only rules whose queries have been successfully validated can be part of the plan presented to the user.

---

## Flow B: Specific Rule

This flow applies when the user directly describes a rule they want to create, without needing a prior coverage assessment. The goal is to design, validate, and create that specific rule with human approval.

### B.1 Scope and Metadata

1. **Identify domain and tables**: from the user's description, determine the `domain_name` and the tables involved. If unclear, ask.
2. **Obtain metadata in parallel**:
   ```
   Parallel:
     A. get_table_columns_details(domain_name, table)  [for each table involved]
     B. get_tables_details(domain_name, [tables])
     C. get_quality_rule_dimensions(collection_name=domain_name)
     D. quality_rules_metadata(domain_name=domain_name)  <-- only if not executed before
   ```
   **Note about `quality_rules_metadata`**: updates the AI metadata of existing rules (description, dimension). Executed without `force_update` — only processes rules without metadata or modified, which covers rules created outside this agent. If it fails, continue without blocking.
3. **Verify existence**: confirm that the tables and columns mentioned by the user exist in the domain. If any do not exist, inform and ask.

### B.2 Design the Rule

With the obtained metadata and the user's description, design the rule:

- **`dimension`**: choose the most appropriate dimension based on the rule's nature (completeness, validity, consistency, etc.). Use the domain definitions obtained in B.1.
- **`query`**: SQL that counts the records that PASS the check. For parts involving governed tables, use `generate_sql` to obtain the correct table/column names. For specific business logic (joins, complex conditions), build the SQL manually respecting the resolved names.
- **`query_reference`**: SQL that counts the total number of records (denominator).
- **`rule_name`**: follow the convention `dq-[table]-[dimension]-[description]` in kebab-case.
- **`description`**: concise natural language description in clear business terms (no technical jargon) of what this rule checks, describing the expected outcome. Apply the same mandatory rules as in section 3.1: do not include scheduling, do not use technical column names, do not mention the dimension — use the semantic definition of the field.

Follow the design guidelines in section 3.3 and the SQL patterns in section 3.2.

### B.3 SQL Validation (MANDATORY)

Same as section 3.5:
1. Resolve the `${table}` placeholders with the actual table name.
2. Execute `query` and `query_reference` with `execute_sql(query=[sql], limit=1)`.
3. If any query fails, review and correct until both are successful.
4. Calculate the result and rule status applying the logic from step 5 of section 3.5 (measurement_type, threshold_mode, and configured thresholds).
5. **Inform the user of the result** including the calculated status. Examples:
   - Percentage exact: "the query returns 45,000 of 45,230 total → 99.5% → KO (threshold: =100% OK)"
   - Count exact: "the query returns 0 records → OK (threshold: =0 OK)"
   - Range: "the query returns 72% → WARNING (range: <=50% KO, >50-80% WARNING, >80% OK)"
   - No data: "query_reference returns 0 records → NO_DATA"

After informing of the result, continue directly with section 4 (Present Plan and Wait for Approval). In Flow B, the plan will typically contain a single rule. Include the SQL validation result with the calculated status in the presentation.

**Note**: After rule creation (section 5), AI metadata will be automatically generated via `quality_rules_metadata`.

---

## 4. PAUSE: Present Plan and Wait for Approval

Before executing any call to `create_quality_rule`, present the complete plan to the user.

**Note for Flow B (specific rule)**: The plan will typically contain a single rule. Also include the SQL validation result with the calculated status (OK/KO/WARNING/NO_DATA).

### Plan format

```markdown
## Quality Rule Creation Plan

**Domain**: [domain_name]
**Affected tables**: [list]
**Rules to create**: N

---

### Rule 1: dq-account-completeness-id
- **Table**: account
- **Dimension**: completeness
- **Column**: id
- **Description**: Validates that every account record has a non-null primary identifier, ensuring data integrity across the system
- **SQL (passing records)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Measurement**: Percentage, exact value — =100% OK, !=100% KO
- **Justification**: The id column is the table's primary key. A null in this field indicates a corrupt record that breaks referential integrity.
- **Validation result**: 45,230 of 45,230 records pass → 100.0% → OK

### Rule 2: dq-account-uniqueness-id
[...]
```

**Note about the result field**:
- **Flow B** (specific rule): always use `**Validation result**` with the actual value obtained from the queries. Format: `[query_val] of [query_ref_val] records pass → [result]% → [STATUS]` (percentage) or `[query_val] records → [STATUS]` (count).
- **Flow A** (with prior EDA): if the EDA already provided current situation data, combine both in a single field. Format: `**Current situation** (prior EDA): 0 nulls of 45,230 records; **SQL validation**: 45,230 of 45,230 pass → 100.0% → OK`.
- If `query_reference` returns 0: `**Validation result**: NO_DATA — query_reference returns 0 records`.

---

```
Shall I proceed with the creation of these N rules?

The measurement for each rule is indicated in the **Measurement** field of the plan. If you want to change how any rule is measured, indicate so before approving.

Additionally, do you want to schedule automatic execution of the rules?
1. Yes, with the same schedule for all rules
2. Yes, with different schedules per rule (or only for some)
3. No, create the rules without scheduling (manual execution)

Do you want to configure rule measurement?
1. Yes, I want to configure how they are measured (I will ask you the details)
2. No, use the default measurement (percentage, exact value: =100% OK / !=100% KO)
```

### Interpreting the user's response

**Approval without choosing a scheduling or measurement option** → If the user simply says "yes", "go ahead", "proceed" or another approval signal without choosing a scheduling option or answering the measurement question, do NOT create the rules yet. Explicitly ask both things before continuing:

```
Before proceeding, I need to know:

1. **Scheduling**: do you want to schedule automatic execution?
   1. Yes, with the same schedule for all rules
   2. Yes, with different schedules per rule (or only for some)
   3. No, manual execution

2. **Measurement**: do you want to configure how the rules are measured?
   1. Yes, I want to configure how they are measured (I will ask you the details)
   2. No, use the default measurement (percentage, exact value: =100% OK / !=100% KO)
```

**Approval + scheduling option 3 + measurement option 2 (both explicitly indicated)** → Create the rules without scheduling parameters or custom measurement.

**Approval + option 1** → Before creating the rules, collect the scheduling parameters once for all:

- `cron_expression` (mandatory): ask in natural language if the user doesn't know Quartz format ("How often do you want them to execute?") and generate the equivalent expression. Guide with examples:
  - Daily at 9:00 → `0 0 9 * * ?`
  - Every Monday at 9:00 → `0 0 9 ? * MON`
  - First day of each month at 9:00 → `0 0 9 1 * ?`
- `cron_start_datetime` (optional): ask "When do you want execution to start? (leave blank to start immediately)". If the user indicates a date/time in natural language, convert it to ISO 8601. Example: `2026-04-01T09:00:00`
- `cron_timezone`: **Do NOT ask** unless the user mentions a different timezone. Use `Europe/Madrid` by default.

If the user provides the cron details in the same approval response (e.g., "yes, option 1, daily at 9"), do not ask again — use that data directly.

**Approval + option 2** → For each rule (or block of rules the user wants to treat the same), ask for the same fields as above. Allow some rules to have scheduling and others not.

**Measurement configuration (option 1)** → If the user chooses to configure measurement, follow the interaction flow in section 3.4: present the 4 options, collect the choice, ask for details based on the chosen mode (exact or range), and confirm. Apply the resulting configuration to the affected rules. If the user chooses option 2 or does not mention measurement, do not pass measurement parameters (use tool defaults).

**Measurement change** → If the user asks to change how one or more rules are measured (e.g., "I want rule 1 to use count instead of percentage", "set 3-level ranges for all"), adjust the `measurement_type`, `threshold_mode`, and/or `exact_threshold`/`threshold_breakpoints` parameters of the affected rules. If the user describes thresholds in natural language (e.g., "KO below 80%, WARNING between 80-95%, OK above 95%"), translate them to the corresponding `threshold_breakpoints` format (see complete examples in section 3.4). Update the **Measurement** field in the plan and present again for approval.

**Rejection** → Do not create. If the user modifies any rule, update the plan and present again for final approval.

### Plan format with custom measurement (if applicable)

If after the user's response any rule has custom measurement (different from default), include in its block:
```markdown
- **Measurement**: Count, ranges — <=50 KO, >50-100 WARNING, >100 OK
```

The **Measurement** field must always appear in all rules in the plan, both with defaults and custom values. Format: `[Percentage|Count], [exact value|ranges] — [threshold details]`.

### Plan format with scheduling (if applicable)

If after the user's response any rule has scheduling configured, include in its block:
```markdown
- **Scheduling**: `0 0 9 * * ?` — daily at 9:00 (Europe/Madrid)
  - First execution: 2026-04-01T09:00:00
```

Rules without scheduling: do not add any scheduling field (nor "No scheduling"). If no rule has scheduling, completely omit any reference to scheduling.

### Valid approval signals

Any of these responses (or equivalents in the user's language) are considered approval:
- "yes", "y", "sure"
- "proceed", "go ahead", "ok", "OK", "fine"
- "create the rules", "do it", "execute"
- "approved", "confirmed", "I confirm"

### Rejection or modification signals

- "no", "cancel", "stop"
- "modify rule X"
- "remove the rule for Y"
- "change the threshold of Z"

If the user modifies: update the plan and present again for final approval.

## 5. Execution: Create Rules

Only after explicit approval, create the rules one by one:

```
For each approved rule (sequential, NOT in parallel):
  1. Call create_quality_rule with the designed parameters, including the optional
     scheduling ones if configured (cron_expression, cron_timezone, cron_start_datetime)
     and the measurement ones if the user configured them (measurement_type, threshold_mode, and exact_threshold
     or threshold_breakpoints depending on the mode — pass them together as shown in the examples in section 3.4)
  2. Report the result immediately in chat
  3. If it fails: indicate the error and continue with the next one
```

**Why sequential and not in parallel**: to report progress in real time and allow the user to interrupt if something goes wrong.

**Per-rule report format** (add scheduling in parentheses when it exists):
```
[OK]  dq-account-completeness-id — created successfully (scheduled: daily at 9:00)
[OK]  dq-account-uniqueness-id — created successfully
[ERR] dq-account-validity-amount — error: [MCP message]
[OK]  dq-card-completeness-card-id — created successfully (scheduled: every Monday at 9:00, from 2026-04-01)
```

### 5.1 Generate Metadata for Created Rules

After creating all rules (successful or not), execute a single call to enrich the newly created rules with AI metadata:

```
quality_rules_metadata(domain_name=domain_name)
```

Without `force_update` — newly created rules will not have metadata yet, so they will be automatically processed. If it fails, inform the user but do not block the final summary.

## 6. Final Summary

After completing creation, present a summary:

```markdown
## Rule Creation Result

- Rules created successfully: N/M
- Failed rules: X/M
- AI metadata generated: Yes/No (indicate whether the `quality_rules_metadata` call was successful)

### Coverage before and after

| Table | Previous coverage | New coverage |
|-------|-------------------|--------------|
| account | ~30% | ~75% |
| card | ~50% | ~90% |

### Recommended next steps

- Execute the newly created rules to obtain a quality baseline
- [If any rule had calculated status KO in SQL validation]: **PRIORITY — these rules already show KO with current data**: [list of names]. KO status indicates current data does not meet the configured threshold; review whether the threshold is correct or there is a real quality issue before putting them into production.
- [If any rule had calculated status WARNING in SQL validation]: review these rules, current data is in the warning zone: [list of names].
- [If gaps remain]: consider also covering [list of remaining gaps]
```

If there were creation errors, clearly indicate which rules failed and suggest actions (retry, review the SQL, contact the platform administrator).

## 7. Follow-up Question

At the end, ask the user with options how they want to continue, following the user question convention:
- **Generate a formal report with the results**
- **Create another specific rule**
- **Assess the coverage of other tables in the domain**
- **Finish**
