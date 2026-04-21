---
name: create-quality-schedule
description: "Create a schedule to automatically execute all quality rules in one or more folders/collections. Operates at the folder level (domain/collection), not individual rules. Requires mandatory human confirmation before execution."
argument-hint: "[domain/collection] [frequency (optional)]"
---

# Skill: Quality Rule Schedule Creation

Workflow for creating a schedule that automatically executes all quality rules contained in one or more folders (collections/domains) according to a calendar defined by the user.

## CRITICAL APPROVAL PAUSE

**NEVER call `create_quality_rule_planification` without the user having explicitly confirmed the plan.**

If there are doubts about whether the user has approved, ask again. Do not interpret silence or ambiguous responses as approval.

---

## 1. Scope Determination

### 1.1 Identify collections/domains

From the user's request, determine which collections (domains) to include in the schedule.

- If the user specifies domain names: validate them using `search_domains` or `list_domains` with the corresponding `domain_type` (semantic or technical). If they do not specify the type, ask the user with options following the user question convention.
- **CRITICAL rule**: the collection names used in the call to `create_quality_rule_planification` must be **exactly** the values returned by the listing tools. NEVER translate, interpret, or paraphrase them.
- If the user does not specify specific domains: list the available ones and ask which to include.
- The schedule supports **multiple collections** in a single call (`collection_names` is a list).

### 1.2 Optional table filter

If the user wants to include only specific tables within the collections:

1. Validate the tables with `list_domain_tables(domain_name)` for each collection.
2. Confirm that the mentioned tables exist in the domain.
3. If any table does not exist, inform and ask.

If the user does not mention specific tables, the schedule will include all tables in each collection (default behavior).

---

## 2. Existing Rules Verification

Before creating the schedule, verify that the selected folders contain quality rules. Scheduling the execution of a folder without rules is pointless.

**Procedure** — for each included collection:

1. Get the domain tables with `list_domain_tables(domain_name)`.
2. Call `get_tables_quality_details(domain_name, [tables])` to get the rules inventory.
   - If filtered by tables (section 1.2), use only those tables.
   - If not, use all domain tables.
3. Count existing rules and their status (OK / KO / Warning / Not executed).

**Result evaluation:**

- **Collection without rules**: explicitly warn the user. Suggest assessing coverage and creating rules before scheduling. Ask the user with options, following the user question convention, whether they want to continue anyway or create rules first.
- **Collection with rules in KO status**: mention it as relevant information — the schedule will also execute KO rules, which may generate recurring alerts.
- **Collection with rules**: summarize how many rules there are, in how many tables, and their general status.

If all selected collections are empty, do not continue with the schedule. Redirect the user to create rules first.

**Present summary to the user** before continuing:

```markdown
### Rules in selected collections

| Collection | Tables with rules | Total rules | OK | KO | Warning | Not executed |
|------------|-------------------|-------------|----|----|---------|-------------|
| financial | 5 | 23 | 18 | 2 | 1 | 2 |
| payments  | 3 | 12 | 10 | 0 | 2 | 0 |
```

---

## 3. Collect Schedule Parameters

Collect the parameters needed to create the schedule. Some are asked to the user, others have reasonable defaults.

### 3.1 Name (`name`) — mandatory

Suggest a name following the convention `plan-[domain]-[frequency]`:
- `plan-financial-daily`
- `plan-payments-weekly`
- `plan-financial-payments-monthly`

The user can accept the suggestion or propose another name. If there are multiple collections, combine the relevant names or use a descriptive generic name.

### 3.2 Description (`description`) — mandatory

Generate a business-language description that explains the purpose of the schedule. **Mandatory rules** (same as for quality rule descriptions):
1. Do NOT include technical scheduling details (frequency, cron, times) — that information is already in the schedule fields
2. Do NOT use technical table or column names
3. Describe the business purpose of the schedule

Correct example: "Periodic execution of quality validations for the financial domain to ensure data integrity of accounts and transactions"
Incorrect example: "Daily cron at 9:00 that executes the rules in the financial_domain collection on the account and transaction tables"

Present the proposed description to the user for validation.

### 3.3 Cron expression (`cron_expression`) — mandatory

Accept the frequency in **natural language** and translate to a Quartz cron expression (6 or 7 fields: second minute hour day-of-month month day-of-week [year]).

**Translation examples:**
- "daily at 9:00" → `0 0 9 * * ?`
- "every Monday at 8:30" → `0 30 8 ? * MON`
- "first day of each month at 6:00" → `0 0 6 1 * ?`
- "every 6 hours" → `0 0 */6 * * ?`
- "Monday to Friday at 7:00" → `0 0 7 ? * MON-FRI`

**Restriction**: Do NOT allow very low frequency expressions (like `* * * * * *` or similar that execute every second/minute). If the user asks for something like that, explain the risk and suggest a reasonable minimum frequency.

If the user directly provides a valid Quartz expression, use it as-is.

### 3.4 Timezone (`cron_timezone`) — optional

Default: `Europe/Madrid`. **Do NOT ask** unless the user explicitly mentions another timezone. If they do, use the indicated timezone (e.g., `UTC`, `America/New_York`).

### 3.5 Start date (`cron_start_datetime`) — optional

Ask: "When do you want execution to start? (leave blank to start immediately)".

If the user indicates a date/time in natural language, convert to ISO 8601 format (e.g., "next Monday at 9" → `<YYYY-MM-DD>T09:00:00`, where `<YYYY-MM-DD>` is the date of next Monday calculated from today). If they indicate nothing, the schedule starts immediately after creation.

### 3.6 Execution size (`execution_size`) — optional

Default: `XS`. **Do NOT ask** unless the user mentions performance concerns, data volume, or execution size. Available options: `XS`, `S`, `M`, `L`, `XL`.

If the user asks or the schedule covers a large volume of rules/tables, guide:
- `XS` / `S`: small domains, few rules
- `M`: medium domains, dozens of rules
- `L` / `XL`: large domains, hundreds of rules or complex queries

---

## 4. PAUSE: Present Plan and Wait for Approval

Before executing the call to `create_quality_rule_planification`, present the complete plan to the user.

### Plan format

```markdown
## Quality Schedule Plan

**Name**: plan-financial-daily
**Description**: Periodic execution of quality validations for the financial domain to ensure data integrity of accounts and transactions
**Collections**: financial_domain
**Filtered tables**: all (or list of tables if filtered)
**Rules to be executed**: 23 rules across 5 tables
**Schedule**: `0 0 9 * * ?` — daily at 9:00 (Europe/Madrid)
**First execution**: immediately (or ISO 8601 date if indicated)
**Execution size**: XS

---

Shall I proceed with creating this schedule?
```

### Valid approval signals

Any of these responses (or equivalents in the user's language):
- "yes", "y", "sure"
- "proceed", "go ahead", "ok", "OK", "fine"
- "create it", "do it", "execute"
- "approved", "confirmed", "I confirm"

### Rejection or modification signals

- "no", "cancel", "stop"
- "change the frequency to..."
- "change the name to..."
- "add/remove collection X"
- "filter only tables Y"

If the user modifies any parameter: update the plan and present again for approval.

---

## 5. Execution

Only after explicit user approval:

1. Call `create_quality_rule_planification` with all configured parameters:
   - `name`: schedule name
   - `description`: business description
   - `collection_names`: list of collections/domains
   - `cron_expression`: Quartz cron expression
   - `table_names`: list of tables (only if filtered; if not, omit)
   - `cron_timezone`: timezone (only if different from default)
   - `cron_start_datetime`: start date (only if indicated)
   - `execution_size`: size (only if different from default)

2. Report the result immediately in chat.

3. If the call fails:
   - Inform the user of the error with the MCP message.
   - If the error is correctable (e.g., invalid cron expression, duplicate name), suggest an adjustment and ask if they want to retry.
   - Maximum 2 retries with adjusted parameters. If it still fails, inform and suggest alternative actions.

---

## 6. Final Summary

After successful creation, present confirmation:

```markdown
## Schedule Created

- **Name**: plan-financial-daily
- **Status**: Created successfully
- **Collections**: financial_domain
- **Scheduled rules**: 23 rules across 5 tables
- **Schedule**: daily at 9:00 (Europe/Madrid)
- **First execution**: immediately
- **Size**: XS
```

---

## 7. Follow-up Question

At the end, ask the user with options how they want to continue, following the user question convention:
- **Create another schedule for other collections**
- **Create quality rules for collections that were empty**
- **Assess the current quality coverage**
- **Finish**
