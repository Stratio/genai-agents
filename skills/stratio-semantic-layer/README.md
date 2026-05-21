# stratio-semantic-layer

Reference skill that loads the **mandatory rules, usage patterns and best practices** for the Stratio Governance MCP tools (`create_ontology`, `update_ontology`, `delete_ontology`, `delete_ontology_classes`, `create_business_views`, `create_technical_terms`, `refine_foreign_keys`, `create_sql_mappings`, `create_semantic_terms`, `create_business_term`, `publish_business_views`, `create_data_collection`, and the full `sql`-server exploration toolkit), including the optional `best_effort` delivery mode on ontology creation/update and the six-option recovery flow on post-plan ontology failures.

This skill does **not** call MCP tools — it loads the contract that every governance-related skill and agent must follow.

## What it does

- Loads the full governance-MCP reference (`stratio-semantic-layer-tools.md`) into the conversation.
- Covers:
  - The complete tool catalogue split by server (`gov` + `sql`), with parameters and purpose.
  - Strict rules: immutability of `domain_name`, technical-vs-semantic domain usage, `user_instructions` built through the §11 Glossary Instruction Enrichment Workflow (no silent injection), mandatory confirmation for destructive operations (`regenerate=true`, `delete_*` — including the new whole-ontology `delete_ontology`), view-publishing approval, ADD+DELETE ontology semantics, naming conventions for collections and ontologies, optional `best_effort` argument on `create_ontology` / `update_ontology` (opt-in; only affects how quality rejections during generation are handled, does not override pre-generation feasibility failures).
  - Technical domain discovery workflow (search → list → explore tables → details → columns → knowledge).
  - Exploration of **published** semantic domains (`semantic_*` prefix).
  - State-detection table for idempotency: how to detect existing collections, technical terms, ontologies, views, mappings, semantic terms and publishing status before acting.
  - Error handling and recovery: generic retry-with-improved-`user_instructions` (max 2 per entity), plus the **ontology-specific six-option recovery flow** (§7.2) for failures that occur after the plan was already validated — clean and retry with best-effort, complete missing classes via update (with or without best-effort), clean and retry with corrected plan, just clean, or leave as-is for manual fix in the UI.
  - Parallel execution rules (read tools in parallel, creations sequential within a phase, strict phase sequence between phases).
  - Long-running task polling protocol (`task_id` → `get_mcp_task_result` with `pending` / `done` / `error` / `not_found`).
  - OpenSearch-availability fallback (deterministic `list_*` + local substring filter when search endpoints fail).

## When to use it

- Before the first interaction with any governance MCP tool in a conversation.
- When refreshing the rules for destructive operations, publishing, or ontology semantics.
- When a specialised `create-*` skill is not the right fit but the agent still needs to call governance tools directly.
- For a specific flow (creating terms, ontology, views, mappings…), prefer the matching `create-*` skill — it already embeds the relevant subset of these rules.

## Dependencies

### Other skills
None. This is a reference-only skill; every other governance skill builds on top of it.

### Guides
- `stratio-semantic-layer-tools.md` — the full governance MCP reference. Loaded wholesale when this skill activates.

### MCPs
None invoked directly. The guide references the full governance MCP catalogue, which is listed in detail in the companion guide.

### Python
None — prompt-only reference skill.

### System
None.

## Bundled assets
None.

## Notes

- **Load early.** The skill is designed to run before any other governance tool call; loading it mid-conversation still works, but it is less efficient because the rules may already have been broken.
- **Pairs with `stratio-data`** — together they cover the two MCP families (governance + data). Agents that touch both usually load both.
- **The guide itself lives in the central monorepo guides folder** so multiple skills can reference the same source of truth without duplication.
