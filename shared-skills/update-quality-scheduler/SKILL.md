---
name: update-quality-scheduler
description: "Modify an existing quality rule scheduler: change the schedule (cron), update collections or table filters, rename, update description, activate/deactivate, or change execution size. Requires the scheduler UUID (discovered via list_quality_rule_schedulers if not in context) and mandatory human confirmation before execution."
argument-hint: "[scheduler name or UUID] [optional: what to change]"
---

# Skill: Quality Rule Scheduler Update

Workflow for modifying an existing quality rule scheduler with human approval. Only the fields that the user wants to change are sent — the rest remain untouched.

## CRITICAL APPROVAL PAUSE

**NEVER call `update_quality_rule_scheduler` without the user having explicitly confirmed the proposed changes.**

This pause is mandatory. Do not interpret silence or ambiguous responses as approval.

**Each invocation of this skill is independent.** An approval given for a previous change is NOT valid for a new modification.

---

## 1. Identify the Scheduler

**If the UUID is already known** (in conversation context, e.g. from a recent `create_quality_rule_scheduler` call): use it directly. Skip to step 2.

**If the UUID is not known**:
1. Call `list_quality_rule_schedulers()` — no parameters needed.
2. Present the results to the user in a readable format:

```markdown
### Existing Quality Schedulers

| Name | Active | Collections | Schedule | UUID |
|------|--------|-------------|----------|------|
| plan-financial | ✓ | financial_domain | `0 0 9 * * ?` (daily at 9:00) | fa989da8-... |
| plan-payments | ✗ | payments_domain | `0 30 8 ? * MON` (Mon at 8:30) | bc123ef4-... |
```

3. Ask the user which scheduler they want to modify.
4. Extract the UUID and current state of the selected scheduler.

**Show the user the current state** of the selected scheduler before proceeding:

```markdown
### Current state of scheduler plan-financial (UUID: fa989da8-...)
- **Name**: plan-financial
- **Description**: Periodic execution of quality validations for the financial domain
- **Collections**: financial_domain
- **Table filter**: all tables
- **Schedule**: `0 0 9 * * ?` — daily at 9:00 (Europe/Madrid)
- **First execution**: immediately
- **Execution size**: XS
- **Active**: yes
```

---

## 2. Collect the Changes

**If the user already described the changes in the request**: proceed with those changes directly.

**If the request is vague** (e.g., "update scheduler X", "modify it"): ask what they want to change with options:

```
What do you want to change in this scheduler?
1. The schedule (cron expression, frequency, timezone)
2. The collections or table filter (which folders to execute)
3. The name or description
4. Activate or deactivate the scheduler
5. The execution size (XS/S/M/L/XL)
6. Several of the above (describe them)
```

### Special cases

**Activate/deactivate**: pass `active=true` or `active=false`. No other fields need to change.

**Change cron only**: pass `cron_expression` (and optionally `cron_timezone`, `cron_start_datetime`). Do not touch collections or other fields.

**Replace collections**: `collection_names` **replaces** all existing planned resources — it is not additive. If provided, validate the new collections (see section 3).

**Table filter**: `table_names` is only used when `collection_names` is also provided. If only the table filter changes within existing collections, the entire `collection_names` must also be passed.

**`cron_timezone` and `cron_start_datetime`**: only used when `cron_expression` is provided.

**Change description**: apply the same mandatory rules as in the `create-quality-scheduler` skill section 3.2 — no scheduling information, no technical table or column names, no measurement information, no active/inactive status.

**Cron expression**: accept frequency in **natural language** and translate to a Quartz cron expression (6 or 7 fields). Examples:
- "daily at 9:00" → `0 0 9 * * ?`
- "every Monday at 8:30" → `0 30 8 ? * MON`
- "first day of each month at 6:00" → `0 0 6 1 * ?`

Do NOT allow very low frequency expressions (like `* * * * * *`). If the user provides a valid Quartz expression directly, use it as-is.

---

## 3. Validate New Collections (MANDATORY if `collection_names` changes)

If the proposed changes include a new or different `collection_names` list:

1. Validate each collection name against `search_domains` or `list_domains` to confirm it exists.
2. For each new collection, call `list_domain_tables(domain_name)` and `get_tables_quality_details(domain_name, [tables])` to verify it contains quality rules.
3. If a collection has no rules: warn the user — scheduling an empty folder is pointless. Ask with options (following the user question convention) whether to continue anyway or create rules first.
4. Summarize the rules found in the new collections:

```markdown
### Rules in the new collections

| Collection | Tables with rules | Total rules | OK | KO | Warning | Not executed |
|------------|-------------------|-------------|----|----|---------|-------------|
| payments_domain | 3 | 12 | 10 | 0 | 2 | 0 |
```

---

## 4. PAUSE: Present Plan and Wait for Approval

Before executing any call to `update_quality_rule_scheduler`, present the proposed changes in a before/after format.

### Plan format

```markdown
## Quality Scheduler Update Plan

**Scheduler**: plan-financial (UUID: fa989da8-...)

### Current state
- **Collections**: financial_domain
- **Schedule**: `0 0 9 * * ?` — daily at 9:00 (Europe/Madrid)
- **Active**: yes
- **Execution size**: XS

### Proposed changes
- **Schedule**: `0 30 8 ? * MON` — every Monday at 8:30 (Europe/Madrid)

(Fields not listed here remain unchanged.)
```

Only list fields that actually change in the "Proposed changes" section. Fields not mentioned remain exactly as they are.

---

```
Shall I proceed with this update?
```

### Interpreting the user's response

**Valid approval signals**: "yes", "y", "proceed", "go ahead", "ok", "update it", "apply", "confirmed", or equivalents in the user's language.

**Rejection or modification signals**: "no", "cancel", "change X instead", "also change Y", "wait".

If the user modifies the request: update the plan and present again for final approval.

---

## 5. Execute: Update the Scheduler

Only after explicit approval, call `update_quality_rule_scheduler` with **only the fields that change**. Do not send fields that remain unchanged.

**Examples by change type:**

Change cron only:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  cron_expression="0 30 8 ? * MON",
  cron_timezone="Europe/Madrid"
)
```

Activate/deactivate:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  active=false
)
```

Replace collections:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  collection_names=["payments_domain", "financial_domain"]
)
```

Change name and description:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  name="plan-financial-payments",
  description="Periodic execution of quality validations for financial and payments domains"
)
```

Change execution size:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  execution_size="M"
)
```

Multiple fields:
```
update_quality_rule_scheduler(
  planification_uuid="fa989da8-...",
  cron_expression="0 0 6 1 * ?",
  collection_names=["financial_domain", "payments_domain"],
  execution_size="S"
)
```

Report the result immediately after the call:

```
[OK]  plan-financial — updated successfully
[ERR] plan-financial — error: [MCP message]
```

---

## 6. Summary

After a successful update, present a brief summary:

```markdown
## Update Result

- **Scheduler**: plan-financial
- **Changes applied**: cron updated — previously daily at 9:00, now every Monday at 8:30
- **Next execution**: next Monday at 8:30 (Europe/Madrid)
```

If the update fails, clearly indicate the error and suggest alternatives (retry, verify the UUID, contact the platform administrator).

## 7. Follow-up Question

At the end, ask the user with options how they want to continue, following the user question convention:
- **Update another scheduler**
- **Create a new scheduler** (load `create-quality-scheduler`)
- **List current schedulers**
- **Finish**
