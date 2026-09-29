---
name: dashboard-builder
description: "Create or extend native GenAI dashboards from Cowork conversations, tool results, materialized tabular data, and workspace images. Use when the user asks to create a dashboard, append cards, turn an analysis into dashboard cards, visualize results as text/data/chart/image cards, include a File Browser image, or requests an unsupported destructive dashboard operation that must be refused safely."
argument-hint: "[dashboard request or content]"
---

# Dashboard Builder

Create or extend dashboards through the dashboard MCP tools. A request such as
"create a dashboard" or "add these cards" authorizes that mutation; do not ask
for a second confirmation.

Before constructing a dashboard payload, read
[`references/contract.md`](references/contract.md) relative to this skill's base
directory. Follow its field names, nesting, required fields, and allowed values
exactly. Do not draft the payload from memory.

## Safety boundary: existing dashboards are append-only

Cowork supports creating a dashboard and appending cards. It does not support
deleting, clearing, replacing, editing, overwriting, or reordering a persisted
dashboard or card.

When the requested effect is destructive or would change existing content:

1. Do not call any dashboard tool, including `list_dashboards`.
2. Do not delegate or use files, shell commands, direct HTTP/REST, PATCH, or
   DELETE as a fallback.
3. Do not use `create_dashboard` or `add_dashboard_cards` to simulate deletion
   or a desired final state.
4. Reply once that deleting or editing existing dashboards and cards is not
   available from Cowork and must be done manually in Dashboards, then stop.

For a mixed request containing destructive and additive changes, perform no
mutation. Explain the boundary and ask the user to make a separate request for
the additive part.

## Mandatory operational channel

Dashboard mutations happen only through the dashboard MCP tools. Use the
available tool whose unprefixed name is `create_dashboard`,
`add_dashboard_cards`, or `list_dashboards`; the runtime may prefix it with the
MCP server alias.

- Never store a dashboard payload with file-writing or shell tools.
- Never create `created-dashboard.json`, a proposal file, or another JSON file
  as a substitute for a dashboard tool call.
- Never emit a `dashboard-skill-output` block. The frontend does not persist
  dashboard actions from assistant text.
- Never invoke dashboard REST endpoints through shell, HTTP, or a non-MCP tool.
- If the dashboard MCP tools are unavailable, state that the project is missing
  its dashboard MCP configuration. Do not pretend to create the dashboard or
  fall back to a file.

## Workflow

1. Classify the current request as create, append, read-only, or unsupported.
   Apply the safety boundary immediately for destructive requests. Do not carry
   an unexecuted mutation from an earlier turn into the current one.
2. Gather only content supported by the conversation, tool results, or workspace
   files. Inspect referenced files when tools permit it.
3. Choose native card types:
   - `text` for summaries, explanations, and Markdown or HTML.
   - `data` for materialized rows that should remain tabular.
   - `chart` for materialized rows with a valid chart configuration.
   - `image` for screenshots, static plots, diagrams, and other visual files.
     Do not embed images in text HTML.
4. Do not add `source` metadata to text, data, or chart cards because it is not
   part of their persisted card content. For an `@filename` or File Browser
   image, resolve the exact path below `/root/project` and use only a
   `workspace_path` source. This flow currently requires the dashboard server to
   be configured as a custom/direct HTTP MCP whose URL includes
   `?projectId={env:PROJECT_ID}`. A native System MCP registration does not
   currently carry this project context.
5. Map each distinct requested item to exactly one card. A singular request for
   one text, table, chart, or image produces one card.
6. Validate the tool arguments against `references/contract.md`.
7. Call the appropriate dashboard MCP tool with the canonical cards.

## Operational persistence

- For a new dashboard, call `create_dashboard` with `title`, optional
  `description`, and a non-empty `cards` array.
- To append cards, use a real `dashboard_id` when known. Otherwise pass the
  exact user-provided name as `dashboard_title`; the API resolves one exact,
  unique case-insensitive match. Never invent an ID.
- Append only cards requested in the current additive turn. Never replay cards
  or unfinished work from an earlier turn.
- If an append request has neither a real ID nor a dashboard name, ask one
  concise clarification before calling the tool.
- On success, answer once with a concise confirmation and no link. Treat the
  returned `dashboardId` as opaque client metadata: do not repeat it or derive
  a path, URL, origin, or host from it. The UI owns dashboard navigation.
- A successful mutation completes the request. Do not propose a follow-up check
  or continue with another verification step.
- On failure, report the actual error. Do not claim success or retry with a file
  or assistant JSON block.
- For hypothetical questions, documentation, or examples that do not authorize
  a mutation, answer normally without calling a dashboard tool.

Ask for clarification only before the tool call when required content cannot be
inferred. Do not ask the user to continue after a completed operation.

## Content rules

- Never invent dashboard IDs, SQL, source IDs, file paths, measurements, or rows.
- Materialize `data` and `chart` rows in the payload. Do not depend on rerunning
  SQL to render a dashboard.
- Include `sqlQuery` only when an actual successful SQL statement exists.
- Set `raw` to `null` for newly composed cards unless a genuine compatible raw
  response is available.
- Prefer Markdown for text drafts; the API sanitizes and converts it to HTML.
- For a File Browser image, do not copy its bytes into the conversation or put
  its mention in `src`. Resolve the exact absolute path below `/root/project`,
  omit `src` and `projectId`, and provide a
  `source: {"kind":"workspace_path","path":"/root/project/..."}`.
  Use this source only when the dashboard MCP is a custom/direct HTTP server
  configured with `?projectId={env:PROJECT_ID}`. If that project-aware transport
  is unavailable, state that workspace images cannot be imported; do not try a
  native System MCP or invent a project ID.
  The API reads and validates the authorized file, then persists a complete
  Base64 Data URL in `card_content.src`, making the card independent of the
  workspace lifecycle.
- Use a complete supported Data URL only when it is already the available
  source; never manufacture or truncate Base64.
- Default image presentation to `fit: "contain"` and `position: "center"`.
- Omit layout when automatic placement is acceptable. When supplied, respect
  the 12-column grid.
- Keep card titles concise and dashboard-ready.

## Final self-check

Before calling the tool, verify:

- The payload contains at least one card and no unknown fields.
- Card count matches the distinct requested items and contains no duplicates.
- Dashboard metadata and append target information are sufficient.
- Every card has valid content for its type.
- Data values and schema fields agree; chart dimensions and metrics exist.
- The chart type is operationally supported; never generate `heatmap` cards.
- Image references are resolvable and do not masquerade as text cards.
- All factual content is grounded in available sources.
