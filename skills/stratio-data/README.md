# stratio-data

Reference skill that loads the **mandatory rules, usage patterns and best practices** for the Stratio data MCP tools (`query_data`, `search_domains`, `list_domains`, `generate_sql`, `profile_data`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`, `get_tables_quality_details`, `propose_knowledge`, …).

This skill does **not** call MCP tools — it loads the contract that every data-related skill and agent must follow before touching governed data.

## What it does

- Loads the full data-MCP reference (`stratio-data-tools.md`) into the conversation.
- Covers:
  - The complete tool catalogue on the `sql` server, with parameters and purpose.
  - The fundamental rule: **never write SQL manually** — always delegate generation to `query_data` or `generate_sql`.
  - Strict rules: immutability of `domain_name`, MCP-first strategy, when to use `query_data` vs. Python/pandas, valid `output_format` values, parallel execution semantics.
  - Domain discovery workflow (search → list → tables → details → columns → terminology).
  - Profiling rules: `profile_data` thresholds (<100k / 100k–1M / >1M rows), SQL generation via `generate_sql`, use of the `limit` parameter instead of in-SQL `LIMIT`.
  - Governance quality coverage via `get_tables_quality_details` — lightweight check during exploration (not a replacement for `assess-quality`).
  - Clarification cascade when `query_data` / `generate_sql` respond with a question instead of data (search knowledge → infer from plan → ask user → reformulate → report).
  - Seven post-query validations to apply to every `query_data` result.
  - Long-running task polling (`task_id` → `get_mcp_task_result` with `pending` / `done` / `error` / `not_found`).
  - OpenSearch-availability fallback for `search_domains` when the index is unavailable.

## When to use it

- Before the first call to any data MCP tool in a conversation.
- When refreshing the rules for query generation, profiling, parallel execution or clarification handling.
- When the agent is about to work with a domain that has not been touched in this session.
- For broad exploration tailored to the user's question, prefer `explore-data` — it already embeds the relevant subset of these rules.

## Dependencies

### Other skills
None. This is a reference-only skill; every other data-consuming skill builds on top of it.

### Guides
- `stratio-data-tools.md` — the full data-MCP reference. Loaded wholesale when this skill activates.

### MCPs
None invoked directly. The guide references the full data-MCP catalogue, listed in detail in the companion guide.

### Python
None — prompt-only reference skill.

### System
None.

## Bundled assets
None.

## Notes

- **Load early.** The skill is designed to run before any other data tool call in a conversation; loading it mid-conversation still works but rules may already have been broken.
- **Pairs with `stratio-semantic-layer`** — together they cover the two MCP families (data + governance). Agents that touch both typically load both.
- **The guide is kept in `shared-skill-guides/`** so multiple skills reference the same source of truth without duplication.
