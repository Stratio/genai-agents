---
name: propose-knowledge
description: Analyze the conversation to propose business terms and preferences discovered to the `Stratio Governance` layer of the domain. Use when the user wants to enrich the semantic layer with definitions, rules or preferences discovered during an analysis.
argument-hint: [domain (optional)]
---

# Skill: Knowledge Proposal to Governance

Guide for analyzing an analysis conversation and proposing discovered business knowledge to the `Stratio Governance` semantic layer.

## 1. Determine Domain

- If `$ARGUMENTS` contains a domain name, validate it with `search_domains($ARGUMENTS)` before using it. Use the exact name from the result, not the user's interpretation
- If not, infer the domain from the current conversation (look for previous MCP calls with `domain_name`)
- If it cannot be inferred, list available domains via `list_domains()` and ask the user following the user question convention (adaptive to the environment: interactive if available, numbered list in chat otherwise)

## 2. Gather Conversation Context

Review `output/MEMORY.md` sec "Known Data Patterns" if it exists — if there are mature patterns for the domain (observed 3+ times), consider including them as candidates for governed knowledge proposal.

Analyze EVERYTHING that occurred in the conversation — original question, analysis plan, data obtained, calculations performed, insights discovered, conclusions and recommendations.

Classify findings into two categories:

### 2.1 Business definitions
- Business terms used or discovered (e.g.: "VIP Customers", "Retention Rate")
- Segmentations applied (e.g.: "Top 10% by revenue")
- Thresholds or criteria (e.g.: "Churn: no purchases in 90 days")
- Metrics with formula (e.g.: "ARPU = total revenue / active users")

### 2.2 Preferences

**CRITICAL RULE**: Only propose preferences **specific to the data domain**. NEVER propose workflow, session or analysis format preferences — these are transient options the user chooses in each analysis (Phase 2 of the workflow) and do not constitute reusable domain knowledge.

#### 2.2.1 Explicit exclusions

The following categories are NEVER proposed as domain knowledge:

| Category | Examples | Origin (not domain knowledge) |
|----------|----------|-------------------------------|
| Output formats | PDF, Web, PowerPoint | Block 2, Phase 2 of the workflow |
| Visual style | Corporate, Academic, Modern | Block 2, Phase 2 of the workflow |
| Report structure | Scaffold, On the fly | Block 2, Phase 2 of the workflow |
| Audience | C-level, Manager, Technical | Block 1, Phase 2 of the workflow |
| Analysis depth | Quick, Standard, Deep | Block 1, Phase 2 of the workflow |

#### 2.2.2 What SHOULD be proposed as a preference

**Validation criterion**: The preference must mention specific tables, columns or metrics from the domain. If it applies to any domain generically → discard.

- Domain-specific SQL patterns (e.g.: "LEFT JOIN between customers and orders in the retail domain because orders has customers without a record")
- Visualization preferences tied to domain metrics (e.g.: "Heatmap for retention matrix by cohort in the subscriptions table")
- Domain filtering conventions (e.g.: "Exclude records with status='TEST' in the transactions table")

## 3. Query Existing Metadata

Before proposing, verify that already governed knowledge is not duplicated:

1. Use `get_tables_details(domain_name, table_names)` to review business terms already defined on the relevant tables
2. Use `search_domain_knowledge(question, domain_name)` to search for each candidate term/concept

For each finding:
- **Already exists with same definition** (even if different wording): Discard (do not propose duplicate)
- **Already exists with different definition**: Propose update ONLY if the new definition adds substantially new information (formula, threshold, additional context). Do not propose if it is simply a rewording
- **Does not exist**: Propose as new

## 4. Prioritize and Limit Proposals

**Total limit: maximum 5 proposals per execution** (exceptionally 6 if there is a sixth `business_concept` of high relevance).

Classify each candidate proposal according to this priority table:

| Priority | Type | Inclusion criterion | Limit |
|----------|------|---------------------|-------|
| **P1 — Critical** | `business_concept` (new) | Term discovered or defined in the analysis that does NOT exist in the governed domain | Max 3 |
| **P2 — High** | `business_concept` (update) | Term that already exists but with a different/improved definition | Max 2 |
| **P3 — Medium** | `sql_preference` | SQL pattern discovered that improves domain queries | Max 1 |
| **P3 — Medium** | `chart_preference` | Domain-specific visualization preference | Max 1 |

If there are more candidates than the limit, apply priority (P1 first) and within each priority, sort by relevance to the user's original question.

### Quality criteria for business_concept

A `business_concept` is only proposed if it meets **AT LEAST 2** of these criteria:
- Has a **precise definition** with formula or numeric threshold
- Was **actively used** in the analysis (not just mentioned)
- Is **relevant to the domain** (applies to existing tables/columns)
- Was **explicitly defined** by the user in the conversation

If a candidate does not meet at least 2 criteria, discard it and document the reason in the report.

## 5. Prepare Proposals

Classify each proposal into one of the 3 supported types:

| Type | Description | Example |
|------|-------------|---------|
| `business_concept` | Term definitions, segmentations, metrics, thresholds | "VIP Customers: annual revenue > 10,000 EUR" |
| `sql_preference` | Preferred SQL patterns | "LEFT JOIN for customers-orders" |
| `chart_preference` | Visualization preferences | "Area charts for time series, bars for categories" |

For each proposal, document:
- **Type**: One of the 3 above
- **Priority**: P1, P2 or P3
- **Name**: Short name of the term or preference
- **Definition**: Complete and precise description
- **Context**: Quote or reference of where it arose in the analysis
- **Related tables**: Domain tables where it applies (if applicable)

## 6. Present to User for Approval

Show proposals organized by priority and type to the user. For each one, indicate:
- Priority (P1/P2/P3)
- Type
- Name
- Definition
- Context (where it arose)
- Related tables

Ask the user following the user question convention (adaptive to the environment: interactive if available, numbered list in chat otherwise):
- **Send all**: Propose everything as is
- **Select**: The user indicates which to send (ask allowing multiple selection)
- **Modify**: The user wants to adjust a definition before sending
- **Cancel**: Do not propose anything

If the user chooses "Modify", ask what changes they want to make, apply them and present again for approval.

## 7. Send via MCP

For approved proposals, call `propose_knowledge(business_context=..., domain_name=...)`.

The `business_context` parameter should be a structured markdown text with the following format:

```markdown
## Knowledge Proposals

### business_concept
- **[Term name]**: [Complete definition]
  - Context: [Where it arose in the analysis]
  - Related tables: [table1, table2]

### sql_preference
- **[Preference name]**: [SQL pattern description]
  - Context: [Where it arose]

### chart_preference
- **[Preference name]**: [Visual preference description]
  - Context: [Where it arose]
```

Only include sections that have proposals. Do not include empty sections.

## 8. Report

Present a final summary to the user:

- Proposals sent broken down by priority (P1/P2/P3) and type
- Summary of each sent proposal
- Discarded proposals and reason (duplicate, low priority, does not meet quality criteria)
- Errors encountered (if any)
- Note: "The proposals will be reviewed by an administrator in the Governance console before being integrated into the domain's semantic layer"
