---
name: manage-critical-data-elements
description: "Consult or define Critical Data Elements (CDEs) for a governed domain. Flow A: view current CDEs. Flow B: tag tables/columns as critical — manually, by agent recommendation, or combined. Mandatory approval pause before any tagging operation."
argument-hint: "[domain]"
---

# Skill: Manage Critical Data Elements

Workflow for consulting and defining Critical Data Elements (CDEs) in a governed domain. CDEs are the data assets — tables or specific columns — considered most important for the business. They receive prioritized quality treatment: assessments focus on them first, and gaps in CDE assets are escalated to a higher priority level.

## CRITICAL APPROVAL PAUSE

**NEVER call `set_critical_data_elements` without explicit user confirmation.**

**HTTP 409 responses during tagging mean the asset was already tagged as a CDE.** This is NOT an error — count these as "already tagged" and do not treat them as failures in results or summaries.

---

## 1. Scope Determination

### 1.1 Validate the domain

If `$ARGUMENTS` provides a domain name, search with `search_domains($ARGUMENTS)`. If not found, retry with `search_domains($ARGUMENTS, refresh=true)`. If still not found, or no argument was provided, list domains with `list_domains()` and ask the user with options following the user question convention.

**CRITICAL rule**: the `collection_name` used in all MCP calls must be **exactly** the value returned by `search_domains` or `list_domains`. NEVER translate, interpret, paraphrase, or infer it.

### 1.2 Determine flow

If the user's request already makes the intent clear, proceed directly:
- "Show me the CDEs" / "What are the critical data elements of [domain]?" → **Flow A**
- "Recommend CDEs" / "Define CDEs" (no specific asset mentioned) → **Flow B** (ask method in B.2)
- "Tag [specific table/column] as critical" (user names exact tables or columns) → **Flow B, skip B.2, go directly to B1** with those assets pre-filled. Do NOT ask the user to choose a method — they already specified what to tag.

Otherwise, ask the user with options following the user question convention:
1. **View current CDEs** — consult what is currently marked as critical in this domain
2. **Define/update CDEs** — tag tables or columns as Critical Data Elements

---

## Flow A: View Current CDEs

### A.1 Retrieve and present current CDEs

Call `get_critical_data_elements(collection_name=domain_name)`.

Present results with clear structure:

```markdown
## Critical Data Elements — [domain_name]

### Fully critical tables (all columns are CDEs)
| Table |
|-------|
| account |
| district |

### Tables with specific CDE columns
| Table | CDE Columns |
|-------|-------------|
| card | card_id, disp_id |
| transaction | account_id, bank, date, trans_id |
```

If both `critical_tables` and `columns_by_table` are empty or absent: "No Critical Data Elements are currently defined for this domain."

### A.2 Optional: quick quality coverage check

After presenting CDEs, offer the user a quick check of quality coverage over the CDE assets. If accepted:

1. Call `get_tables_quality_details(domain_name, [all CDE tables])` — tables from `critical_tables` plus tables with entries in `columns_by_table`
2. Present a summary table:

```markdown
| Table | CDE type | Rules defined | Status |
|-------|----------|---------------|--------|
| account | Full table | 4 | OK |
| card | Specific columns | 1 | Warning |
| transaction | Specific columns | 0 | No rules |
```

3. If any CDE table has no rules defined: highlight as a quality gap to address.

### A.3 Follow-up question

Ask the user with options following the user question convention:
- **Define or update CDEs for this domain** (proceed to Flow B)
- **Assess quality coverage focused on CDEs** (load `assess-quality`)
- **Finish**

---

## Flow B: Define/Update CDEs

### B.1 Gather baseline in parallel

Before recommending or collecting user input, fetch the current state:

```
Parallel:
  A. list_domain_tables(domain_name)
  B. get_critical_data_elements(collection_name=domain_name)   ← baseline: current CDEs
```

### B.2 Determine definition method

Ask the user with options following the user question convention:
1. **Manual specification** — I will indicate directly which tables/columns to tag as CDEs
2. **Agent recommendation** — Analyze the domain semantics and data profile, then recommend CDEs for my confirmation
3. **Combined** — Agent recommends, then I adjust before confirming

---

### Flow B1: Manual Specification

Present the list of available domain tables (from `list_domain_tables`) to help the user choose. If the user wants to inspect columns for a specific table, call `get_table_columns_details(domain_name, table)` on request.

Collect from the user:
- Which **entire tables** to tag as critical (all columns in those tables become CDEs)
- Which **specific columns** in which tables to tag as CDEs

Validate that all mentioned tables and columns exist in the domain before proceeding. Compare the user's specified assets against the baseline from B.1:
- Assets **not** in the baseline → include in the tagging payload (truly new)
- Assets already in the baseline → **exclude** from the payload; note them as "Already tagged" in the plan

**Payload rule**: the tagging payload must contain ONLY the assets that are not in the baseline. If the user requested N assets but all N are already tagged, the payload is empty — skip the API call entirely and present the result as "all requested assets were already tagged as CDEs".

Proceed to **B.4 Approval Pause**.

---

### Flow B2: Agent Recommendation

#### B2.1 Gather information in parallel

```
Parallel:
  A. get_tables_details(domain_name, [all_tables])
  B. get_table_columns_details(domain_name, table)          [for each table — in parallel]
  C. get_tables_quality_details(domain_name, [all_tables])  ← existing rules as recommendation signal
```

Then profile the data for each table:
```
For each table (in parallel):
  generate_sql("get all fields from table [table] without filters", domain_name)
  → profile_data(query=[sql])
```

#### B2.2 Recommendation criteria

**Table-level (tag entire table as CDE):**
- Master or reference entities (accounts, customers, products, locations, categories)
- Tables described in the domain as foundational or central to business processes
- Tables with many foreign key relationships pointing to them from other tables
- Tables explicitly mentioned in documented business rules as authoritative sources of truth

**Column-level (tag specific columns within a table):**
- Primary keys and business identifiers — completeness + uniqueness are critical by definition
- Mandatory foreign keys that drive referential integrity across the domain
- Columns defined in the domain glossary with business terms or formal definitions
- Core financial or operational metric columns (amounts, counts, rates central to reporting)
- Date columns that determine data freshness, SLA compliance, or regulatory reporting windows
- Status or state columns that control business process flows or approvals
- Columns already covered by multiple quality rules — prior investment signals importance

**EDA signals that reinforce a recommendation:**
- Existing nulls in a column that should be non-null → immediate evidence of risk
- Duplicates in a primary key candidate → critical integrity concern
- Columns with several quality rules already defined → someone already considered them critical

#### B2.3 Present recommendation

```markdown
## Recommended Critical Data Elements — [domain_name]

**Basis**: semantic analysis of domain description, table context, column definitions,
domain terminology, EDA results, and existing quality rules.

### Recommended fully critical tables (all columns become CDEs)

| Table | Reason |
|-------|--------|
| account | Master entity — all columns are identifiers, balances, or process-critical fields |
| district | Reference table — provides geographic master data used across 3+ tables |

### Recommended tables with specific CDE columns

| Table | Recommended columns | Reason |
|-------|---------------------|--------|
| card | card_id, disp_id | Primary key + mandatory FK — core integrity identifiers |
| transaction | account_id, trans_id, date, amount | FK, business ID, freshness date, core financial metric |

### Tables not recommended as CDEs

| Table | Reason |
|-------|--------|
| order | Secondary operational table; no master/reference role identified |
```

Inform the user they can accept, modify, or reject individual items before confirming.

---

### Flow B3: Combined

Execute **Flow B2** (agent recommendation) first, then allow the user to:
- Add tables or columns not included in the recommendation
- Remove tables or columns from the recommendation
- Promote a column-level CDE to a full-table CDE (or demote)
- Accept the recommendation as-is

Collect the final agreed list, then proceed to the approval pause.

---

### B.4 PAUSE: Present Plan and Wait for Approval

Before calling `set_critical_data_elements`, present the complete tagging plan:

- **Assets to tag as critical** = only assets NOT present in the baseline (truly new tagging operations).
- **Already tagged** = assets from the user's specification that were already in the baseline — shown for transparency, excluded from the API call.

```markdown
## CDE Tagging Plan — [domain_name]

**Domain**: [collection_name]
**Source**: [Manual specification | Agent recommendation | Combined]

### Assets to tag as critical (new — not yet in the baseline)

**Full critical tables** (all columns will be CDEs):
- account
- district
- loan

**Tables with specific CDE columns**:
| Table | Columns to tag |
|-------|----------------|
| card | card_id, disp_id |
| transaction | account_id, bank, date, trans_id |

**Already tagged** (from current baseline — will be counted as retained, not errors):
- [list or "None"]

---

Shall I proceed with tagging these assets as Critical Data Elements?
```

**Valid approval signals**: "yes", "proceed", "go ahead", "ok", "approved", "confirmed", "do it", or equivalents in the user's language.

**Rejection or modification signals**: "no", "cancel", "remove X", "add Y", "change". If the user modifies: update the plan, present again, and wait for confirmation.

### B.5 Execution

Only after explicit approval, call `set_critical_data_elements` with **only the assets that are new** (not present in the baseline from B.1).

**CRITICAL — payload must contain ONLY new assets:**
- Cross-check the payload against the baseline obtained in B.1 (`get_critical_data_elements` result).
- Remove from the payload ANY asset (table or column) that already appears in the baseline.
- DO NOT include currently-tagged CDEs. The API is additive, not a full replace: re-sending an existing CDE causes a 409 error and is never necessary.
- If the user's specification matches only 1 new asset, the payload contains exactly 1 asset. If it matches 0 new assets, skip the API call entirely.

```json
{
  "collection_name": "domain_name",
  "critical_tables": ["account", "district", "loan"],
  "columns_by_table": {
    "card": ["card_id", "disp_id"],
    "transaction": ["account_id", "bank", "date", "trans_id"]
  }
}
```

### B.6 Present results

Parse the response and present a result table:

```markdown
## CDE Tagging Result — [domain_name]

| Asset | Result |
|-------|--------|
| account (full table) | Tagged successfully |
| district (full table) | Already tagged — no change needed |
| card.card_id | Tagged successfully |
| card.disp_id | Tagged successfully |
| transaction.account_id | Already tagged — no change needed |
| transaction.bank | Tagged successfully |

**Summary**:
- Successfully tagged: N
- Already tagged (retained): M
- Failed: X
```

- HTTP 409 → show as "Already tagged — no change needed" and count as **retained**, not as failure
- Other errors → show as "Failed" with a brief reason note below the table

---

## 7. Follow-up Question

Ask the user with options following the user question convention:
- **Assess quality coverage focused on CDEs** (load `assess-quality`)
- **View the updated list of CDEs for this domain**
- **Define CDEs for another domain**
- **Finish**
