---
name: refine-semantic-foreign-keys
description: "Add, modify or remove the foreign key relations between business views of a Stratio Governance domain. Use after create-semantic-terms when the user wants to fix incorrect FK targets, detect FKs the create phase missed, or remove FKs no longer applicable. Operates on every view with a semantic business term regardless of whether the view is published. Accepts the technical domain name (canonical) or the semantic counterpart on input. For technical-table FKs use refine-foreign-keys."
argument-hint: "[domain (optional)]"
---

# Skill: Refine Semantic Foreign Keys

Surgical edits to the foreign key relations between business views of a domain. Sibling of `create-semantic-terms`, but for FK maintenance only — does NOT regenerate the semantic terms themselves.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List technical domains. `refresh=true` for cache bypass |
| `list_technical_domain_concepts(domain)` | gov | List business views with governance status, `has_sql_mapping` and **`has_semantic_terms`** — the predictor of refinable views |
| `refine_semantic_foreign_keys(domain, user_instructions, view_names?)` | gov | Add, modify or remove FK relations between views. `domain` accepts the technical name (canonical, recommended) or the semantic counterpart — both work. `user_instructions` is required. Returns a single `message` field with a markdown summary in explicit `key=value` notation, e.g. `fk_count=N, persist=<ok\|failed>, BT=<updated\|unchanged>, columns_enriched=N` per view, plus per-domain totals and any skip warning |

**Key rules**: `domain_name` immutable (exact value from `list_domains` or `search_domains`, preferring the technical name). `user_instructions` is required — the tool rejects empty input. Build `user_instructions` through the Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11, `phase=semantic_terms`). The tool refines any view with a semantic business term, **regardless of whether the view is published** — views without one are skipped with a clear warning (run `/create-semantic-terms` first). Only EN and ES are supported by the underlying tool; other languages return an error verbatim.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, normalize and discover the canonical technical name:

- If it starts with the `semantic_` prefix → strip the prefix client-side. The tool accepts both forms but the canonical discovery target is the technical domain. Mention to the user that you are using the technical equivalent — both forms are accepted.
- Search with `search_domains($ARGUMENTS, domain_type='technical')`. If it does not match, retry with `refresh=true` in case it is a recently created collection. If it still does not match, ask the user.

If there is no argument, list technical domains with `list_domains(domain_type='technical')` and ask the user following the user question convention.

The user may also intend a different operation:

- If they explicitly want to refine FKs on **technical tables** (not semantic views), suggest `/refine-foreign-keys`. This skill does NOT route automatically — it only informs; the agent's LLM decides whether to load the other skill.

### 2. Evaluate state

Execute `list_technical_domain_concepts(domain)` to obtain the list of business views with their governance status, `has_sql_mapping` and **`has_semantic_terms`**. The last flag is the authoritative predictor of which views can be refined.

Present summary:
```
## State — [domain_name]
| View | State | Mapping | Semantic terms | Refinable |
|------|-------|---------|----------------|-----------|
| view_a | Draft | ✓ | ✓ | yes |
| view_b | Published | ✓ | ✓ | yes |
| view_c | Draft | ✓ | ✗ | no — run `/create-semantic-terms` first |
```

Views with `has_semantic_terms: true` are refinable **regardless of governance state** (Draft, Pending Publish, or Published). Views with `has_semantic_terms: false` are surfaced separately and excluded from the scope question — point the user to `/create-semantic-terms` for those.

### 3. Scope selection

Ask the user with options (only views with `has_semantic_terms: true`):
1. **All refinable views** — omit `view_names`. The tool processes every view with a semantic business term.
2. **Specific views** — multiple selection from the refinable candidates.

### 4. Instruction intent

The tool requires `user_instructions` (non-empty). If the user hasn't provided concrete guidance, ask now. Two productive intents:

- **TARGETED** — the user names the relations to change. Examples:
  - *"Add a foreign key from orders.customer_id to customers.id"*
  - *"Delete the FK on shipments.carrier_id"*
  - *"Change the target of the FK in orders.address_id to addresses.id"*

- **DISCOVERY** — the user asks to detect FKs the create phase missed. Triggered by detection-language verbs (detect / find / discover / encontrar / detectar / descubrir / buscar). Examples:
  - *"Detect the missing foreign keys in orders and shipments"*
  - *"Find any relationships that were not detected for the customers and addresses views"*

These two intents can coexist in one instruction (e.g. *"Detect missing FKs and delete the FK on carrier_id"*).

Generic phrases like *"review"* or *"update"* without specifics or detection language produce no changes. Warn the user before invoking the tool with such input — it wastes a round trip without producing any modification.

### 5. Glossary instruction enrichment

Before invoking the MCP tool, apply the Glossary Instruction Enrichment Workflow described in `guides/stratio-semantic-layer-tools.md` §11, scoped to **semantic terms** (i.e., when calling `get_glossary_instructions`, request only the `semantic_terms` phase).

If the orchestrator already pre-loaded enriched instructions for the semantic-terms phase during a prior skill run, reuse them; optionally ask the user whether they want to add anything specific on top.

The enriched text concatenates with the user's intent text from step 4 and becomes the `user_instructions` argument in step 6.

### 6. Execution

Invoke `refine_semantic_foreign_keys(domain, user_instructions, view_names?)`. The tool returns a single `message` field whose value is a markdown summary already structured with:

- per-domain totals: views processed, persisted, best-effort fallbacks, skipped or failed
- a per-view bullet list in explicit `key=value` notation (no diff glyphs to interpret):
  - `- **<view>**: fk_count=N, persist=<ok|failed>, BT=<updated|unchanged>, columns_enriched=N`
  - `BT=unchanged` is a normal success path — it means the rendered FK section was identical to the previous one and no PUT was needed.
  - Skipped views (view not found, semantic Business Term not found, etc.) render as `- **<view>**: skipped — <reason>`.

Forward the `message` markdown to the user **verbatim** — do not paraphrase, summarize or restructure it. The chain authored the wording on purpose so that user-facing output stays consistent across runs and languages.

If the markdown reports `persist=failed` or skip warnings for some views, you may add a brief, neutral suggestion below the message (e.g. "Re-run with a more specific instruction for those views, or check governance permissions for the failed ones"), but never edit the markdown itself. `BT=unchanged` does NOT warrant any extra suggestion — it is the normal outcome when no relations needed adjustment.

**Surface errors verbatim too**: the same verbatim rule that applies to the success markdown applies to any error message the tool returns — never paraphrase, summarize or substitute it with your own wording. Error text is authored deliberately so users see consistent, actionable language across all governance tools. If the tool halts because none of the requested views are refinable, the message already explains why and points the user to `/create-semantic-terms` — forward it as-is.

## Notes

- The tool **never regenerates the semantic term** of a view; only the `### Foreign Key Relations` section of the view's Business Term and the FK suffixes of the affected source columns are re-rendered.
- The tool is **not destructive by default**: an FK is removed only when the instruction explicitly says so (or when the target view no longer exists in the domain). Generic "review" instructions preserve the current state.
- A single source column can participate in multiple FK relations (e.g. junction-like views). When that happens the column-level Business Term receives one FK suffix per relation; the skill needs no special handling for this — the chain manages it.
- **User-added content is preserved across refines**: any content the user has added to the Business Term of a view outside the auto-generated `### Foreign Key Relations` section — additional headings, prose, lists, tables — is kept intact when the refine flow rewrites the section.
- **Publication is not a prerequisite**: any view with a semantic business term can be refined, whether it is still Draft, in Pending Publish, or already Published. The skill no longer asks the user to publish first.
- **Domain form is tolerant**: the tool accepts both the technical name and the `semantic_*` counterpart. Examples in this skill use the technical form for discoverability and consistency with the rest of the construction pipeline.
- **Input names are normalized**: leading and trailing whitespace and wrapping backticks in `view_names` are trimmed automatically. The user does not need to clean up copy-pasted names.
- If the deployment's `governance_language` is not supported (i.e. not EN or ES), the response will carry an explicit error — surface it to the user as-is. The user is not expected to know the deployment configuration up front.
- **Technical-table FKs are a different operation**: this skill handles FK relations between **semantic views**. For FKs between physical tables of a technical domain use `/refine-foreign-keys` instead.
