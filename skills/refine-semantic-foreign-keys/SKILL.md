---
name: refine-semantic-foreign-keys
description: "Add, modify or remove the foreign key relations between business views in a semantic Stratio Governance domain. Use after create-semantic-terms when the user wants to fix incorrect FK targets, detect FKs the create phase missed, or remove FKs no longer applicable. Only operates on views with previously generated semantic terms; rejects technical domains and directs the user to refine-foreign-keys instead."
argument-hint: "[semantic domain (optional)]"
---

# Skill: Refine Semantic Foreign Keys

Surgical edits to the foreign key relations between business views in a semantic domain. Sibling of `create-semantic-terms`, but for FK maintenance only — does NOT regenerate the semantic terms themselves.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='business')` | sql | **Prefer**. Search published semantic domains by free text. Results by relevance |
| `list_domains(domain_type='business', refresh?)` | sql | List all published semantic domains. `refresh=true` for cache bypass |
| `list_domain_tables(domain)` | sql | List views of the published semantic domain (works for both technical and semantic domain names) |
| `refine_semantic_foreign_keys(domain, user_instructions, view_names?)` | gov | Add, modify or remove FK relations between views. `domain` MUST start with `semantic_` (technical domains rejected — use `refine_foreign_keys`). `user_instructions` is required. Returns a single `message` field with a markdown summary in explicit `key=value` notation, e.g. `fk_count=N, persist=<ok\|failed>, BT=<updated\|unchanged>, columns_enriched=N` per view, plus per-domain totals and any skip warning |

**Key rules**: `domain_name` immutable (exact value from `list_domains` or `search_domains`). `user_instructions` is required — the tool rejects empty input. Build `user_instructions` through the Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11, `phase=semantic_terms`). Views without a previous semantic Business Term are skipped automatically — run `/create-semantic-terms` first if needed. Only EN and ES are supported by the underlying tool; other languages return an error verbatim.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name:

- If it explicitly starts with `semantic_` → search with `search_domains($ARGUMENTS, domain_type='business')`. If it matches a result, continue. If it does not match, retry with `refresh=true` in case it is a recently published domain. If it still does not match, ask the user.
- If it is **ambiguous** (a bare name like `sakila` that could be either a technical domain or the technical-name prefix of `semantic_sakila`) → ask the user explicitly whether they mean the technical tables (use `/refine-foreign-keys`) or the published semantic views (continue here with the `semantic_` prefix prepended). Do NOT assume; do NOT auto-route.
- If it is **inequivocally technical** (no `semantic_` prefix and the user confirms they mean tables) → advise the user that this skill only handles semantic views and suggest `/refine-foreign-keys`. The skill does NOT route automatically — it only informs; the agent's LLM decides whether to load the other skill.

If there is no argument, list semantic domains with `list_domains(domain_type='business')` and ask the user following the user question convention.

If the underlying MCP tool rejects the call because the domain is not semantic, surface the tool's error verbatim — the message already points the user to `refine_foreign_keys`.

### 2. Evaluate state

Execute `list_domain_tables(domain)` to obtain the list of views in the published semantic domain.

Present summary:
```
## State — [domain_name]
- Total views: N
```

In a published semantic domain, all listed views carry a semantic Business Term by construction. If the MCP tool later reports a skip warning for any view (`**<view>**: skipped — semantic business term not found` or similar), surface that warning verbatim and suggest running `/create-semantic-terms` for the missing views.

### 3. Scope selection

Ask the user with options:
1. **All eligible views** — omit `view_names`. The tool processes every view with a previous semantic term.
2. **Specific views** — multiple selection from the candidates.

### 4. Instruction intent

The tool requires `user_instructions` (non-empty). If the user hasn't provided concrete guidance, ask now. Two productive intents:

- **TARGETED** — the user names the relations to change. Examples:
  - *"Add a foreign key from film_actor.film_id to film.film_id"*
  - *"Delete the FK on rental.staff_id"*
  - *"Change the target of the FK in inventory.film_id to film.film_id"*

- **DISCOVERY** — the user asks to detect FKs the create phase missed. Triggered by detection-language verbs (detect / find / discover / encontrar / detectar / descubrir / buscar). Examples:
  - *"Detect the missing foreign keys in film_actor and inventory"*
  - *"Find any relationships that were not detected for the rental and payment views"*

These two intents can coexist in one instruction (e.g. *"Detect missing FKs and delete the FK on staff_id"*).

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

## Notes

- The tool **never regenerates the semantic term** of a view; only the `### Foreign Key Relations` section of the view's Business Term and the FK suffixes of the affected source columns are re-rendered.
- The tool is **not destructive by default**: an FK is removed only when the instruction explicitly says so (or when the target view no longer exists in the domain). Generic "review" instructions preserve the current state.
- A single source column can participate in multiple FK relations (e.g. junction-like views). When that happens the column-level Business Term receives one FK suffix per relation; the skill needs no special handling for this — the chain manages it.
- **User-added content is preserved across refines**: any content the user has added to the Business Term of a view outside the auto-generated `### Foreign Key Relations` section — additional headings, prose, lists, tables — is kept intact when the refine flow rewrites the section.
- If the deployment's `governance_language` is not supported (i.e. not EN or ES), the response will carry an explicit error — surface it to the user as-is. The user is not expected to know the deployment configuration up front.
