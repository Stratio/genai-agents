---
name: refine-foreign-keys
description: "Add, modify or remove virtual foreign keys of tables in a technical Stratio Governance domain. Use after create-technical-terms when the user wants to fix incorrect FK targets, detect FKs the create phase missed, or remove FKs no longer applicable. Only operates on tables with previously generated technical terms."
argument-hint: "[technical domain (optional)]"
---

# Skill: Refine Foreign Keys

Surgical edits to the virtual foreign keys of tables in a technical domain. Sibling of `create-technical-terms`, but for FK maintenance only — does NOT regenerate the technical terms themselves.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains. `refresh=true` for cache bypass |
| `list_domain_tables(domain)` | sql | List tables with their descriptions (tables with descriptions already have technical terms — only these are candidates for refine) |
| `refine_foreign_keys(domain, user_instructions, table_names?)` | gov | Add, modify or remove virtual FKs. `user_instructions` is required. Returns a single `message` field with a markdown summary in explicit `key=value` notation, e.g. `added=N, replaced=N, deleted=N, kept=N; persist=<ok\|failed\|not_needed>, BT=<updated\|unchanged>` per table, plus per-domain totals and any skip warning |

**Key rules**: `domain_name` immutable (exact value from `list_domains` or `search_domains`). `user_instructions` is required — the tool rejects empty input. Build `user_instructions` through the Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11, `phase=technical_terms`). Tables without a previous technical term are skipped automatically — run `/create-technical-terms` first if needed.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS, domain_type='technical')`. If it matches a result, continue. If it does not match, retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` in case it is a recently created collection. If it now matches, continue. If it still does not match or there is no argument, list domains with `list_domains(domain_type='technical')` and ask the user following the user question convention.

### 2. Evaluate state

Execute `list_domain_tables(domain)` to evaluate the candidates:
- Tables with description → have technical terms; candidates for refine.
- Tables without description → no BT yet; the tool will skip them with a warning. Inform the user and exclude them from the scope.

Present summary:
```
## State — [domain_name]
- Total tables: N
- With technical terms (refine candidates): X
- Without technical terms (will be skipped): Y
```

If `Y > 0`, suggest running `/create-technical-terms` first for the pending ones.

### 3. Scope selection

Ask the user with options:
1. **All eligible tables** — omit `table_names`. The tool processes every table with a previous technical term.
2. **Specific tables** — multiple selection from the candidates.

### 4. Instruction intent

The tool requires `user_instructions` (non-empty). If the user hasn't provided concrete guidance, ask now. Two productive intents:

- **TARGETED** — the user names the relations to change. Examples:
  - *"Add a foreign key from orders.customer_id to customers.id"*
  - *"Delete fk_obsolete from order_csv"*
  - *"Change the target of fk_district in client_csv to district_csv"*

- **DISCOVERY** — the user asks to detect FKs the create phase missed. Triggered by detection-language verbs (detect / find / discover / encontrar / detectar / descubrir / buscar). Examples:
  - *"Detect the missing foreign keys in card_csv and disp_csv"*
  - *"Find any relationships that were not detected for the loan and trans tables"*

These two intents can coexist in one instruction (e.g. *"Detect missing FKs and delete fk_old"*).

Generic phrases like *"review"* or *"update"* without specifics or detection language produce no changes. Warn the user before invoking the tool with such input — it wastes a round trip without producing any modification.

### 5. Glossary instruction enrichment

Before invoking the MCP tool, apply the Glossary Instruction Enrichment Workflow described in `guides/stratio-semantic-layer-tools.md` §11, scoped to **technical terms** (i.e., when calling `get_glossary_instructions`, request only the `technical_terms` phase).

If the orchestrator already pre-loaded enriched instructions for the technical-terms phase during a prior skill run, reuse them; optionally ask the user whether they want to add anything specific on top.

The enriched text concatenates with the user's intent text from step 4 and becomes the `user_instructions` argument in step 6.

### 6. Execution

Invoke `refine_foreign_keys(domain, user_instructions, table_names?)`. The tool returns a single `message` field whose value is a markdown summary already structured with:

- per-domain totals: `Tables processed`, `Persisted with changes`, `No changes needed`, `Failures or skips`
- a `### Per-table outcome` bullet list using explicit `key=value` notation (no diff glyphs to interpret):
  - `- **<table>**: added=N, replaced=N, deleted=N, kept=N; persist=<ok|failed|not_needed>, BT=<updated|unchanged>`
  - `persist=not_needed` means the diff was empty so no PUT was sent (this is a success path, not a failure).
  - Skipped tables (unknown table, missing data_asset_id, no BT yet) render as `- **<table>**: skipped — warning: ...`.

Forward the `message` markdown to the user **verbatim** — do not paraphrase, summarize or restructure it. The chain authored the wording on purpose so that user-facing output stays consistent across runs and languages.

If the markdown reports `persist=failed` or skip warnings for some tables, you may add a brief, neutral suggestion below the message (e.g. "Re-run with a more specific instruction for those tables, or check governance permissions for the failed ones"), but never edit the markdown itself. `persist=not_needed` does NOT warrant any extra suggestion — it is the normal outcome when no relationships needed adjustment.

## Notes

- The tool **never regenerates the technical term** of a table; only the Foreign Key section and the FK paragraphs of affected source columns are re-rendered.
- The tool is **not destructive by default**: an FK is removed only when the instruction explicitly says so (or when the target table no longer exists in the domain). Generic "review" instructions preserve the current state.
- **User-added content is preserved across refines**: any content the user has added to the Business Term outside the auto-generated Foreign Key Relations section — additional headings, prose, lists, tables — is kept intact when the refine flow rewrites the section.
- If the deployment's `governance_language` is not supported by this tool, the response will carry an explicit error — surface it to the user as-is. The user is not expected to know the deployment configuration up front.
