---
name: update-quality-rules
description: "Modify existing quality rules: fix SQL queries, change thresholds, update descriptions, add or remove scheduling, or change measurement configuration. Requires the rule's UUID (obtained via get_tables_quality_details if not already in context) and mandatory human confirmation before execution."
argument-hint: "[rule name or domain] [optional: what to change]"
---

# Skill: Quality Rule Update

Workflow for modifying an existing quality rule with human approval. Only the fields that the user wants to change are sent — the rest remain untouched.

## PREREQUISITE

The user wants to modify an existing quality rule. There are two entry paths:

**Direct path**: The user identifies the rule by name, UUID, or description. The agent may or may not already have the rule's UUID in context.

**From assessment context**: The agent has already listed quality rules (via `get_tables_quality_details`) and the user wants to fix one or more rules that are in KO or WARNING status.

This skill does NOT require a prior coverage assessment.

## CRITICAL APPROVAL PAUSE

**NEVER call `update_quality_rule` without the user having explicitly confirmed the proposed changes.**

This pause is mandatory. Do not interpret silence or ambiguous responses as approval.

If the query or query_reference changes, **SQL validation is MANDATORY** before presenting the plan. Do not show the plan without first verifying both queries are valid.

**Each invocation of this skill is independent.** An approval given for a previous change is NOT valid for a new modification.

---

## 1. Identify the Rule

**If the UUID is already known** (in conversation context): use it directly. Skip to step 2.

**If only the rule name or description is known**:
1. Call `get_tables_quality_details(domain_name, [table])` to retrieve the full rule inventory
2. Locate the rule by name or description in the returned list
3. Extract its UUID and current parameters: name, SQL queries, dimension, measurement configuration, scheduling, and current status (OK/KO/WARNING + % pass)

If the user does not provide the domain or table, ask with options before calling the tool.

**Show the user the current state** of the rule before proceeding:

```markdown
### Current state of rule dq-account-completeness-id (UUID: fa989da8-...)
- **Table**: account
- **Dimension**: completeness
- **SQL (passing records)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Measurement**: percentage, ranges — [0%-80%] KO, (80%-95%] WARNING, (95%-100%] OK
- **Schedule**: daily at 9:00 (Europe/Madrid)
- **Current status**: KO (72%)
```

---

## 2. Collect the Changes

**If the user already described the changes in the request**: proceed with those changes directly.

**If the request is vague** (e.g., "fix rule X", "update it"): ask what they want to change with options:

```
What do you want to change in this rule?
1. The SQL query (fix the logic, add/remove conditions)
2. The measurement thresholds (change levels, type, or values)
3. The scheduling (add, modify, or remove automatic execution)
4. The description or name
5. The dimension
6. Several of the above (describe them)
```

### Special cases

**Remove scheduling**: pass `cron_expression=""` (empty string). This removes the schedule without changing any other field.

**Only change thresholds**: pass only the new `measurement_type`, `threshold_mode`, and `exact_threshold` or `threshold_breakpoints`. Do not touch queries or other fields.

**Change SQL**: see section 3 (SQL validation is MANDATORY).

**Change description**: apply the same mandatory rules as in the `create-quality-rules` skill section 3.1 — no scheduling information, no technical column names, no dimension mentions, no measurement information, no active/inactive status.

**Activate/deactivate**: pass `active=true` or `active=false` if the user wants to change the rule's active state.

---

## 3. SQL Validation (MANDATORY if query or query_reference changes)

If the proposed changes include a new `query` or `query_reference`, validate both before presenting the plan.

**Validation procedure:**
1. Prepare the new `query` and `query_reference`.
2. Resolve `${table}` placeholders by substituting them with the actual table name.
3. Execute both queries using `execute_sql(query=[sql], limit=1)`.
4. If any query returns an error:
   - Review the SQL syntax.
   - Correct the query.
   - Re-validate until both are successful.
5. With both queries successful, calculate the result and rule status:
   - Obtain `query_val` (numeric value from `query`) and `query_ref_val` (numeric value from `query_reference`).
   - Apply the measurement configuration (existing one, or new one if also being changed):
     - If `measurement_type = "percentage"`: `result = (query_val / query_ref_val) * 100` rounded to 2 decimal places. If `query_ref_val == 0`, note `NO_DATA`.
     - If `measurement_type = "count"`: `result = query_val`.
   - Evaluate the status according to `threshold_mode` (existing thresholds unless also changing them):
     - `"exact"`: if `result == exact_threshold.value` → `equal_status`; otherwise → `not_equal_status`.
     - `"range"`: traverse `threshold_breakpoints` in ascending order; for the first point whose `value >= result`, use that `status`; if `result` exceeds all points with a value, use the `status` of the last point.
   - The calculated status is included in the **New validation result** field of the plan.

If only the thresholds change (not the SQL), you can calculate the new projected status using the existing SQL values if they were already known (e.g., from `get_tables_quality_details`). If not, note that the rule will be re-evaluated on next execution.

---

## 4. PAUSE: Present Plan and Wait for Approval

Before executing any call to `update_quality_rule`, present the proposed changes in a before/after format.

### Plan format

```markdown
## Quality Rule Update Plan

**Rule**: dq-account-completeness-id (UUID: fa989da8-...)
**Domain**: [domain_name]

### Current state
- **SQL (passing records)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL`
- **SQL (total)**: `SELECT COUNT(*) FROM ${account}`
- **Measurement**: percentage, ranges — [0%-80%] KO, (80%-95%] WARNING, (95%-100%] OK
- **Schedule**: daily at 9:00 (Europe/Madrid)
- **Status**: KO (72%)

### Proposed changes
- **SQL (passing records)**: `SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL AND id != ''`
- **New validation result**: 45,230 of 45,230 records pass → 100.0% → OK

(Fields not listed here remain unchanged.)
```

Only list fields that actually change in the "Proposed changes" section. Fields not mentioned remain exactly as they are.

**If SQL changes and validates successfully**: always show the new validation result.

**If only thresholds change**: show the threshold before/after. If the previous status percentage is known, calculate the projected new status.

**If removing scheduling**: note it explicitly — "Schedule: removed (currently: daily at 9:00)".

**If multiple fields change**: list each one clearly in the "Proposed changes" section.

---

```
Shall I proceed with this update?
```

### Interpreting the user's response

**Valid approval signals**: "yes", "y", "proceed", "go ahead", "ok", "update it", "apply", "confirmed", or equivalents in the user's language.

**Rejection or modification signals**: "no", "cancel", "change X instead", "also change Y", "wait".

If the user modifies the request: update the plan and present again for final approval.

---

## 5. Execute: Update the Rule

Only after explicit approval, call `update_quality_rule` with **only the fields that change**. Do not send fields that remain unchanged.

```
update_quality_rule(
  uuid="fa989da8-ae49-4e50-bcd5-1e1be33dbbe8",
  query="SELECT COUNT(*) FROM ${account} WHERE id IS NOT NULL AND id != ''",
  query_reference="SELECT COUNT(*) FROM ${account}"
)
```

**Examples by change type:**

Fix SQL only:
```
update_quality_rule(uuid=..., query=..., query_reference=...)
```

Change thresholds only:
```
update_quality_rule(uuid=..., measurement_type="percentage", threshold_mode="exact", exact_threshold={"value": "100", "equal_status": "OK", "not_equal_status": "KO"})
```

Add scheduling:
```
update_quality_rule(uuid=..., cron_expression="0 0 9 * * ?", cron_timezone="Europe/Madrid")
```

Remove scheduling:
```
update_quality_rule(uuid=..., cron_expression="")
```

Change description only:
```
update_quality_rule(uuid=..., description="Validates that every account record has a non-null and non-empty primary identifier, ensuring data integrity across the system")
```

Change multiple fields:
```
update_quality_rule(uuid=..., query=..., query_reference=..., cron_expression="0 0 9 * * ?")
```

Report the result immediately after the call:

```
[OK]  dq-account-completeness-id — updated successfully
[ERR] dq-account-completeness-id — error: [MCP message]
```

---

## 6. Summary

After a successful update, present a brief summary:

```markdown
## Update Result

- **Rule**: dq-account-completeness-id
- **Changes applied**: SQL query corrected, no changes to measurement or scheduling
- **Previous status**: KO (72%)
- **Projected status** (based on new SQL validation): OK (100.0%)

### Recommended next steps

- Execute the rule to confirm the new status with current data
- [If the rule was in KO before the fix]: verify it now passes consistently
```

If the update fails, clearly indicate the error and suggest alternatives (retry, verify the UUID, contact the platform administrator).

## 7. Follow-up Question

At the end, ask the user with options how they want to continue, following the user question convention:
- **Update another rule**
- **Create a new rule** (load `create-quality-rules`)
- **Assess coverage** for the domain
- **Finish**
