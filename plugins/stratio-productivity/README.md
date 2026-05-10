# Stratio Productivity plugin

Skills-only functional plugin that bundles document I/O, visual crafting and skill authoring capabilities. Pluggable into any agent (Cowork or Claude) that needs to read, author or transform office documents and visual outputs.

## What's inside

| Skill | Purpose |
|---|---|
| [pdf-reader](../../shared-skills/pdf-reader/) | PDF reading and content extraction. |
| [pdf-writer](../../shared-skills/pdf-writer/) | PDF authoring and manipulation: merge, split, watermark, encrypt, forms, multi-page typographic documents. |
| [docx-reader](../../shared-skills/docx-reader/) | DOCX reading and content extraction. |
| [docx-writer](../../shared-skills/docx-writer/) | DOCX authoring and manipulation: merge, split, find-replace, `.doc` → `.docx`. |
| [pptx-reader](../../shared-skills/pptx-reader/) | PPTX reading and content extraction. |
| [pptx-writer](../../shared-skills/pptx-writer/) | PPTX authoring: merge, split, reorder, find-replace in slides and notes, `.ppt` → `.pptx`. |
| [xlsx-reader](../../shared-skills/xlsx-reader/) | XLSX reading and content extraction. |
| [xlsx-writer](../../shared-skills/xlsx-writer/) | XLSX authoring: analytical workbooks, pivot matrices, tabular exports, `.xls` → `.xlsx`, formula refresh. |
| [skill-creator](../../shared-skills/skill-creator/) | Designs and generates new agent skills (SKILL.md authoring guide, quality checklist). |
| [web-craft](../../shared-skills/web-craft/) | Interactive frontend output (HTML/CSS/JS, React, Vue): components, pages, dashboards. |
| [canvas-craft](../../shared-skills/canvas-craft/) | Single-page static visual artifacts (PDF/PNG): posters, covers, certificates, infographics. |

## Supported platforms

| Platform | Supported | Notes |
|---|---|---|
| Stratio Cowork | yes | Skills-only plugins are deployable via the `/v1/agents/skills/bundle/import` endpoint of `genai-api`. |
| Claude (claude-plugin) | yes | Generates a `.claude-plugin/plugin.json` consumable as a Claude Code marketplace plugin. |

## Installation

The plugin produces two artifacts:

- `dist/stratio-productivity-stratio-cowork-{version}.zip` — Stratio Cowork bundle.
- `dist/stratio-productivity-claude-{version}.zip` — Claude marketplace plugin.

Use the `upload-plugin` task of the [`cowork-api`](../../shared-skills/cowork-api/) shared skill to deploy the Cowork variant to a tenant. For the Claude variant, follow the standard Claude Code plugin install flow (`/plugin install` from a marketplace).

## MCPs

This plugin does not require any MCP — its skills operate on local files and produce local output. Skills like `web-craft` and `canvas-craft` may receive data from any MCP the consuming agent has configured, but the plugin itself imposes no MCP requirement.

## Overlap with other plugins

`web-craft` and `canvas-craft` also appear in `stratio-data-storytelling`. This is intentional: a skill can belong to multiple plugins, since plugins are additive composition units, not exclusive partitions of the skill catalog.
