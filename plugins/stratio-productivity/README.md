# Stratio Productivity plugin

Skills-only functional plugin that bundles document I/O, visual crafting and brand-identity capabilities. Pluggable into any agent (Cowork or Claude) that needs to read, author or transform office documents and visual outputs with consistent design.

## What's inside

| Skill | Purpose |
|---|---|
| [pdf-reader](../../skills/pdf-reader/) | PDF reading and content extraction. |
| [pdf-writer](../../skills/pdf-writer/) | PDF authoring and manipulation: merge, split, watermark, encrypt, forms, multi-page typographic documents. |
| [docx-reader](../../skills/docx-reader/) | DOCX reading and content extraction. |
| [docx-writer](../../skills/docx-writer/) | DOCX authoring and manipulation: merge, split, find-replace, `.doc` → `.docx`. |
| [pptx-reader](../../skills/pptx-reader/) | PPTX reading and content extraction. |
| [pptx-writer](../../skills/pptx-writer/) | PPTX authoring: merge, split, reorder, find-replace in slides and notes, `.ppt` → `.pptx`. |
| [xlsx-reader](../../skills/xlsx-reader/) | XLSX reading and content extraction. |
| [xlsx-writer](../../skills/xlsx-writer/) | XLSX authoring: analytical workbooks, pivot matrices, tabular exports, `.xls` → `.xlsx`, formula refresh. |
| [web-craft](../../skills/web-craft/) | Interactive frontend output (HTML/CSS/JS, React, Vue): components, pages, dashboards. |
| [canvas-craft](../../skills/canvas-craft/) | Single-page static visual artifacts (PDF/PNG): posters, covers, certificates, infographics. |
| [brand-kit](../../skills/brand-kit/) | Centralised visual identity tokens (colors, typography, chart palettes, sizes, tone). Ten curated themes; clients can extend or replace. |

## Supported platforms

| Platform | Supported | Notes |
|---|---|---|
| Stratio Cowork | yes | Skills-only plugins are deployable via the `/v1/agents/skills/bundle/import` endpoint of `genai-api`. |
| Claude (claude-plugin) | yes | Generates a `.claude-plugin/plugin.json` consumable as a Claude Code marketplace plugin. |

## Installation

The plugin produces two artifacts:

- `dist/stratio-productivity-stratio-cowork-{version}.zip` — Stratio Cowork bundle.
- `dist/stratio-productivity-claude-{version}.zip` — Claude marketplace plugin.

Use the `upload-plugin` task of the [`cowork-api`](../../skills/cowork-api/) shared skill to deploy the Cowork variant to a tenant. For the Claude variant, follow the standard Claude Code plugin install flow (`/plugin install` from a marketplace).

## MCPs

This plugin does not require any MCP — its skills operate on local files and produce local output.
