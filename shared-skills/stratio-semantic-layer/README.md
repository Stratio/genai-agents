# stratio-semantic-layer

Reference skill that loads the **mandatory rules, usage patterns and best practices** for the Stratio Governance MCP tools (`create_ontology`, `create_business_views`, `create_technical_terms`, `create_sql_mappings`, `create_semantic_terms`, `create_business_term`, `publish_business_views`, `create_data_collection`, and the full `sql`-server exploration toolkit).

This skill does **not** call MCP tools — it loads the contract that every governance-related skill and agent must follow.

## What it does

- Loads the full governance-MCP reference (`stratio-semantic-layer-tools.md`) into the conversation.
- Covers:
  - The complete tool catalogue split by server (`gov` + `sql`), with parameters and purpose.
  - Strict rules: immutability of `domain_name`, technical-vs-semantic domain usage, always-offered `user_instructions`, mandatory confirmation for destructive operations (`regenerate=true`, `delete_*`), view-publishing approval, ADD+DELETE ontology semantics, naming conventions for collections and ontologies.
  - Technical domain discovery workflow (search → list → explore tables → details → columns → knowledge).
  - Exploration of **published** semantic domains (`semantic_*` prefix).
  - State-detection table for idempotency: how to detect existing collections, technical terms, ontologies, views, mappings, semantic terms and publishing status before acting.
  - Error handling and recovery (retry with improved `user_instructions`, max 2 retries per entity).
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
- **The guide itself is kept in `shared-skill-guides/`** so multiple skills can reference the same source of truth without duplication.
