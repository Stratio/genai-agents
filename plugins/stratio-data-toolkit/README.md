# Stratio Data Toolkit plugin

Claude marketplace plugin that exposes the core Stratio data skills as a pluggable bundle, for users who have the Stratio data and governance MCPs configured and prefer to work from Claude Code.

## What's inside

| Skill | Purpose |
|---|---|
| [stratio-data](../../skills/stratio-data/) | Mandatory rules and usage patterns for the Stratio data MCPs (`query_data`, `list_domains`, `search_domains`, `generate_sql`, `profile_data`, etc.). |
| [explore-data](../../skills/explore-data/) | Guided workflow to discover governed domains, tables, columns and terminology before any analysis. |
| [propose-knowledge](../../skills/propose-knowledge/) | Capture data-dictionary improvements suggested during analysis and submit them as governance proposals. |
| [assess-quality](../../skills/assess-quality/) | Evaluate quality coverage of a domain, table or column; identify gaps in the eight quality dimensions. |

## Required MCPs

| MCP | Used by | Purpose |
|---|---|---|
| `Stratio_Data` | `stratio-data`, `explore-data` | Query and profile governed domains. |
| `Stratio_Gov` | `propose-knowledge`, `assess-quality` | Read the data dictionary, propose knowledge updates, and inspect quality rules and coverage. |

Both MCPs must already be configured in your Claude agent before installing this plugin. The plugin manifest declares them so they appear in the install summary, but the marketplace does not auto-configure MCPs.

## Supported platforms

| Platform | Supported | Notes |
|---|---|---|
| Claude (claude-plugin) | yes | Generates a `.claude-plugin/plugin.json` consumable as a Claude Code marketplace plugin. |
| Stratio Cowork | **no** | Cowork users already get these skills via the agent plugins (`stratio-data`, `stratio-governance`), which package them inside the agent bundles. |

## Installation

The plugin produces one artifact:

- `dist/plugin-stratio-data-toolkit-claude-{version}.zip` — Claude marketplace plugin.

Install through the standard Claude Code plugin install flow (`/plugin install` from a marketplace that exposes this plugin).

## Output composition

To generate reports (PDF, DOCX, PPTX, XLSX, web pages, posters) on top of the data and quality data this toolkit gives you, also install the [`stratio-productivity`](../stratio-productivity/) plugin. The two are designed to compose: this toolkit covers **input** (data access + quality assessment), `stratio-productivity` covers **output** (document and visual authoring with brand identity).
