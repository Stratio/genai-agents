# Stratio Data Storytelling plugin

Skills-only functional plugin focused on telling stories with Stratio governed data. Bundles data-access rules, brand identity tokens and visual output skills so any consuming agent can go from query to polished, on-brand artifact.

## What's inside

| Skill | Purpose |
|---|---|
| [stratio-data](../../shared-skills/stratio-data/) | Mandatory rules and usage patterns for Stratio data MCPs (`query_data`, `list_domains`, `search_domains`, `generate_sql`, `profile_data`, etc.). |
| [brand-kit](../../shared-skills/brand-kit/) | Centralised visual identity tokens (colors, typography, chart palettes, sizes, tone). Ten curated themes; clients can extend or replace. |
| [web-craft](../../shared-skills/web-craft/) | Interactive frontend output (HTML/CSS/JS, React, Vue): dashboards, narrative web reports, components. |
| [canvas-craft](../../shared-skills/canvas-craft/) | Single-page static artifacts (PDF/PNG): posters, infographics, covers, certificates. |

## Required MCPs

This plugin needs the following MCPs to be configured on the consuming agent:

| MCP | Used by | Purpose |
|---|---|---|
| `Stratio_Data` | `stratio-data` | Provides `query_data`, `list_domains`, `search_domains`, `generate_sql`, `execute_sql`, `profile_data` and the rest of the data MCPs surface. |

The endpoint `/v1/agents/skills/bundle/import` of `genai-api` does not configure MCPs — they must already exist on the agent that consumes these skills, or be added to its `metadata.yaml` afterwards. The future `plugins/v1` API (phase 2) will let the plugin manifest configure them server-side.

## Supported platforms

| Platform | Supported | Notes |
|---|---|---|
| Stratio Cowork | yes | Skills-only plugins are deployable via the `/v1/agents/skills/bundle/import` endpoint of `genai-api`. |
| Claude (claude-plugin) | yes | Generates a `.claude-plugin/plugin.json` consumable as a Claude Code marketplace plugin. |

## Installation

The plugin produces two artifacts:

- `dist/stratio-data-storytelling-stratio-cowork-{version}.zip` — Stratio Cowork bundle.
- `dist/stratio-data-storytelling-claude-{version}.zip` — Claude marketplace plugin.

Use the `upload-plugin` task of the [`cowork-api`](../../shared-skills/cowork-api/) shared skill to deploy the Cowork variant. For the Claude variant, follow the standard Claude Code plugin install flow.

## Overlap with other plugins

`web-craft` and `canvas-craft` also appear in `stratio-productivity`. This is intentional: a skill can belong to multiple plugins, since plugins are additive composition units, not exclusive partitions of the skill catalog.
