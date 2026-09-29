# Canonical dashboard tool contract v1

## Mandatory delivery

Pass canonical cards directly to the dashboard MCP tool. Do not emit the
payload in assistant text and do not save it to a file. The frontend does not
persist dashboard actions.

## Append-only safety boundary

Cowork can create a new dashboard, append new cards, and list dashboards. It
cannot delete, remove, clear, replace, edit, overwrite, or reorder an existing
dashboard or card.

For a destructive request, do not call a dashboard tool, delegate, or use shell
commands or direct REST/PATCH/DELETE requests. Never use `create_dashboard` or
`add_dashboard_cards` to simulate deletion or a desired final state. Reply that
the operation is unavailable from Cowork and must be performed manually in
Dashboards, then stop. If a request mixes destructive and additive work, perform
no mutation and ask for the additive request separately.

## Contents

1. Tool calls
2. Shared card fields
3. Card content by type
4. Sources and images
5. Layout
6. Chart settings
7. Complete examples
8. Validation checklist

## 1. Tool calls

Use the exact tool schema presented by the runtime. The logical arguments are:

- `create_dashboard(title, cards, description?)`
- `add_dashboard_cards(cards, dashboard_id?, dashboard_title?)`
- `list_dashboards(page?, page_size?)`

`cards` must contain at least one canonical card. For append operations, supply
either a real `dashboard_id` or the exact target `dashboard_title`. Do not add
action-envelope fields such as `version`, `operation`, `targetDashboardId`, or
`dashboard` to a tool call.

`add_dashboard_cards` is strictly append-only: it increments the existing card
set and never represents the desired final state. It cannot remove, replace, or
edit existing cards. Include only cards explicitly requested in the current
additive turn; never replay earlier cards or unfinished requests.

A successful create or append returns only `{"dashboardId":"<id>"}`. Treat the
ID as opaque client metadata: do not echo it or construct a path, URL, origin,
or host from it. The UI builds navigation with its own router and deployment
base.

## 2. Shared card fields

```json
{
  "type": "text | data | chart | image",
  "title": "Optional concise title",
  "layout": { "x": 0, "y": 0, "w": 12, "h": 4 },
  "card_content": {}
}
```

Only `type` and `card_content` are always required. `title` and `layout` are
optional. Operational drafts use `source` only for an image copied from the
workspace; do not attach source metadata to text, data, or chart cards because
their persistence model does not retain it.

## 3. Card content by type

### Text

Provide at least one of `markdown` or `html`. Prefer Markdown. Do not place image
markup here when an image card can represent it.

```json
{
  "type": "text",
  "title": "Executive summary",
  "card_content": {
    "markdown": "## Result\nRevenue increased by 12%.",
    "raw": null
  }
}
```

### Data

`data` and `querySchema` are required arrays. Each data row is an object whose
cells may contain any valid JSON value: string, number, boolean, null, array, or
object. Use the corresponding schema type for every column and set `nullable`
consistently with the materialized values. Every schema entry requires `name`,
`type`, `nullable`, and `metadata`.

```json
{
  "type": "data",
  "title": "Revenue by year",
  "card_content": {
    "data": [
      { "year": 2025, "revenue": 1200000, "audited": true },
      { "year": 2026, "revenue": 1450000, "audited": null }
    ],
    "querySchema": [
      { "name": "year", "type": "integer", "nullable": false, "metadata": {} },
      { "name": "revenue", "type": "double", "nullable": false, "metadata": {} },
      { "name": "audited", "type": "boolean", "nullable": true, "metadata": {} }
    ],
    "raw": null
  }
}
```

Allowed schema types: `string`, `boolean`, `integer`, `double`, `float`, `long`,
`decimal`, `date`, `datetime`, `timestamp`, `object`, `array`, and `json`.

Use `object` for object-valued columns, `array` for array-valued columns, and
`json` when a column intentionally contains heterogeneous JSON structures. Add
`sqlQuery` only when it is a real SQL statement produced successfully in the
current context.

### Chart

Chart content requires `data`, `querySchema`, `chartType`, and `chartConfig`.
The data and schema rules are the same as for a data card.

```json
{
  "type": "chart",
  "title": "Revenue trend",
  "layout": { "w": 12, "h": 6 },
  "card_content": {
    "data": [
      { "year": 2025, "revenue": 1200000 },
      { "year": 2026, "revenue": 1450000 }
    ],
    "querySchema": [
      { "name": "year", "type": "integer", "nullable": false, "metadata": {} },
      { "name": "revenue", "type": "double", "nullable": false, "metadata": {} }
    ],
    "chartType": "bar",
    "chartConfig": {
      "graph.dimensions": ["year"],
      "graph.metrics": ["revenue"]
    },
    "raw": null
  }
}
```

Operationally supported chart types: `bar`, `line`, `area`, `waterfall`, `pie`,
`histogram`, `radar`, `bubble`, `scatter`, `progress`, `gauge`, `map`, `pinmap`,
and `table`. Do not generate `heatmap`: the transport model still recognizes
the legacy value, but the current dashboard UI does not render it.

### Image

Provide one resolvable image reference: `src` or a `workspace_path` source. The
`workspace_path` flow currently requires a custom/direct HTTP MCP configured
with `?projectId={env:PROJECT_ID}`. A native System MCP registration does not
carry that project context. With the project-aware direct transport, the API
reads and validates an authorized workspace file, then encodes and persists a
complete Base64 Data URL directly in `card_content.src`; the model must not move
the binary through the conversation. The persisted card remains renderable if
the project stops or is deleted. Supported image MIME types are PNG, JPEG, GIF,
and WebP, with a maximum decoded size of 5 MB. `raw` must be `null`.

```json
{
  "type": "image",
  "title": "Generated chart",
  "source": {
    "kind": "workspace_path",
    "path": "/root/project/output/chart.png"
  },
  "card_content": {
    "alt": "Revenue chart generated during the analysis",
    "caption": "Revenue by year",
    "fit": "contain",
    "position": "center",
    "raw": null
  }
}
```

`fit` is one of `contain`, `cover`, or `fill`; it defaults to `contain`.
`position` defaults to `center`.

## 4. Sources and images

The only operational source shape is:

- `{"kind":"workspace_path","path":"/root/project/output/chart.png"}` requires
  an exact path. Use it only on an image card and omit `projectId` from the tool
  payload. The custom/direct MCP URL must include
  `?projectId={env:PROJECT_ID}` so the API receives the current project outside
  the model-generated arguments and embeds the validated file as Base64.

Do not emit `source` for text, data, or chart cards. Do not emit
`chat_message`, `tool_result`, or `generated` sources in operational drafts;
their metadata is not part of the persisted contract. The image source may live
on the card or in `card_content.source`, but never in both places.

For `src`, use either a valid HTTP(S) URL or a complete
`data:image/<type>;base64,<payload>` Data URL. For File Browser images, omit
`src`; never pass `@filename` there. Never emit placeholder Base64 or a
truncated payload.

## 5. Layout

The grid has 12 columns:

- `x`: integer from 0 through 11.
- `y`: non-negative integer.
- `w`: integer from 1 through 12.
- `h`: integer from 1 through 12.
- When both are present, `x + w` must not exceed 12.

All layout fields are optional. Recommended defaults when explicit layout
matters:

- text: `{ "w": 12, "h": 4 }`
- data: `{ "w": 12, "h": 7 }`
- chart: `{ "w": 6, "h": 6 }`
- image: `{ "w": 6, "h": 5 }`

Prefer omitting `x` and `y`; the persistence layer places new cards without
collisions.

## 6. Chart settings

Reference only columns present in `data` and `querySchema`.

- `bar`, `line`, `area`, `waterfall`, `scatter`:
  `{"graph.dimensions":["dimension"],"graph.metrics":["metric"]}`
- `bubble`: add `"scatter.bubble":"sizeColumn"`.
- `pie`: `{"pie.dimension":"dimension","pie.measure":"metric"}`
- `progress`: `{"progress.goal":100}`
- `gauge`: `{"gauge.segments":[{"min":0,"max":50,"label":"Low"}]}`
- `radar`: `{"radar.metrics":["metric"],"radar.dimension":["dimension"]}`
- `map`:
  `{"map.metric":"metric","map.dimension":"region","map.region":"world_countries","map.type":"region"}`
- `pinmap`: `{"map.latitude_column":"latitude","map.longitude_column":"longitude"}`
- `histogram`: `{"counts":[2,5,3],"bin_edges":[0,10,20,30]}`

Use `table` only when the runtime already provides a known-compatible chart
configuration; otherwise use a `data` card.

For `map.region`, use exactly one of `Spain-communities`, `Spain-provinces`,
`world_countries`, or `United States`. Values are case-sensitive. Do not
generate `heatmap` until the dashboard UI supports it.

## 7. Complete examples

### `create_dashboard` arguments

```json
{
  "title": "Customer analytics",
  "description": "Generated from the current Cowork analysis",
  "cards": [
    {
      "type": "text",
      "title": "Summary",
      "card_content": {
        "markdown": "Revenue increased from 1.2M to 1.45M.",
        "raw": null
      }
    },
    {
      "type": "chart",
      "title": "Revenue by year",
      "card_content": {
        "data": [
          { "year": 2025, "revenue": 1200000 },
          { "year": 2026, "revenue": 1450000 }
        ],
        "querySchema": [
          { "name": "year", "type": "integer", "nullable": false, "metadata": {} },
          { "name": "revenue", "type": "double", "nullable": false, "metadata": {} }
        ],
        "chartType": "bar",
        "chartConfig": {
          "graph.dimensions": ["year"],
          "graph.metrics": ["revenue"]
        },
        "raw": null
      }
    }
  ]
}
```

### `add_dashboard_cards` arguments using the target name

```json
{
  "dashboard_title": "Architecture",
  "cards": [
    {
      "type": "image",
      "title": "Architecture diagram",
      "card_content": {
        "src": "https://example.com/architecture.png",
        "alt": "Architecture diagram generated in Cowork",
        "fit": "contain",
        "position": "center",
        "raw": null
      }
    }
  ]
}
```

## 8. Validation checklist

- Use only documented fields and exact camelCase spelling.
- Do not include `id`, `created_at`, or `updated_at` in drafts.
- Do not emit an empty `cards` array.
- Do not invent a target ID or SQL.
- Do not call a dashboard tool for a destructive request.
- Do not include cards carried over from an earlier turn.
- Keep `querySchema` as a JSON array, not a serialized JSON string.
- Ensure every row value is valid JSON and agrees with the declared schema.
- Match each chart configuration to its chart type and real columns.
- Use image cards for visual files and exact workspace paths.
- Keep inline images complete, supported, and within 5 MB.
