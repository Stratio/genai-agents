# refine-foreign-keys

Surgical add / modify / remove of virtual foreign keys in tables of a technical Stratio Governance domain. Sibling of `create-technical-terms`, but for FK maintenance only — does NOT regenerate the technical terms themselves.

## What it does

- Resolves the technical domain (`search_domains` with `domain_type='technical'`, falling back to `list_domains`).
- Reports candidates: tables with previously generated technical terms are eligible; tables without are surfaced and the user is invited to run `/create-technical-terms` first.
- Offers two scope options: all eligible tables (default) or a specific subset.
- Asks the user for `user_instructions` (required) and guides them between the two productive intents — **TARGETED** (name a specific relation) or **DISCOVERY** (ask to detect missing FKs in named tables); generic phrases without specifics waste a round trip and are warned against.
- Builds the final `user_instructions` through the **Glossary Instruction Enrichment Workflow** (`stratio-semantic-layer-tools.md` §11), scoped to the `technical_terms` phase.
- Invokes `refine_foreign_keys` and forwards the tool's `message` field (a markdown summary covering per-domain totals plus a per-table outcome bullet list with added / kept / replaced / deleted FK names, persistence outcome, BT update status and any skip warning) verbatim to the user — no field parsing.

## When to use it

- An FK detected by `create-technical-terms` points to the wrong target.
- The create phase missed an FK that should exist (DISCOVERY mode).
- An FK is no longer applicable and must be removed.
- A targeted maintenance run that should not regenerate the whole technical term (cheaper than `create_technical_terms(regenerate=true)`).

## Dependencies

### Other skills
- **Hard prerequisite:** `create-technical-terms` — every table the user wants to refine must already carry a technical-data-model Business Term. The tool skips tables without one with an explicit warning.
- **Reference (recommended to load first):** `stratio-semantic-layer` — the governance MCP rules.

### Guides
- `stratio-semantic-layer-tools.md` — full reference for the governance MCPs, including §11 Glossary Instruction Enrichment Workflow.

### MCPs
- **Governance (`gov`):** `refine_foreign_keys`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **`user_instructions` is required.** The tool rejects empty or whitespace-only input — no concrete instruction means no refine.
- **Not destructive by default.** An FK is removed only when the instruction names it explicitly or its target table disappeared from the domain; generic instructions preserve the current state.
- **User-added content is preserved across refines.** Any content added to the Business Term outside the auto-generated Foreign Key Relations section — additional headings, prose, lists, tables — is kept intact when the refine flow rewrites the section.
- **Tables without a Business Term are skipped.** The user is told to run `create_technical_terms` first; no LLM calls happen for those tables.
- **Idempotent.** Re-running the same instruction yields an empty diff and no PUT.
- **Deployment-specific errors** (unsupported governance language, missing permissions) come back from the tool as-is and are surfaced to the user without presupposing the cause.
