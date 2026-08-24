# dashboard-builder

Creates new native GenAI dashboards and appends cards to existing dashboards
from a Cowork conversation. It converts grounded conversation content, tool
results, materialized tabular data, and workspace images into canonical
`text`, `data`, `chart`, and `image` cards.

## What it does

- Calls the dashboard MCP directly; it does not use assistant output or proposal
  files as a persistence channel.
- Creates dashboards and appends new cards while treating existing content as
  append-only.
- Validates card payloads against the canonical contract in
  `references/contract.md`.
- Resolves File Browser images through an exact workspace path. The API embeds
  an authorized copy as a Base64 Data URL so the dashboard remains independent
  of the project workspace lifecycle.
- Treats the returned dashboard identifier as opaque UI metadata and never
  manufactures deployment URLs.

## When to use it

- Create a dashboard from a Cowork analysis or conversation.
- Append one or more cards to an existing dashboard.
- Represent grounded information as native text, data, chart, or image cards.
- Add a workspace image referenced through File Browser or an `@filename`.
- Refuse dashboard/card deletion or editing requests safely; those operations
  must be performed manually in Dashboards.

## Dependencies

### MCP

The host agent must expose tools with these unprefixed names:

- `create_dashboard`
- `add_dashboard_cards`
- `list_dashboards`

The runtime may prefix them with its MCP server alias.

Workspace images additionally require the dashboard server to be configured as
a custom/direct HTTP MCP whose URL includes
`?projectId={env:PROJECT_ID}`. A native System MCP registration does not
currently carry the project context needed to resolve `/root/project` paths.
Without this project-aware transport, the skill can still create text, data,
chart, and URL/Data-URL image cards, but it cannot import File Browser images.

### Other skills

None.

### Python and system packages

None. This is an instruction-only skill. Workspace image validation and Base64
embedding are responsibilities of the dashboard MCP implementation.

## Bundled references

- `references/contract.md` — canonical tool arguments, card schemas, source and
  image rules, grid layout, chart configuration, examples, and validation
  checklist.

## Safety model

Cowork dashboard mutations are intentionally append-only. The skill can create
a dashboard or append cards, but cannot delete, replace, edit, overwrite, clear,
or reorder persisted dashboards or cards. It does not emulate destructive
requests by recreating content.
