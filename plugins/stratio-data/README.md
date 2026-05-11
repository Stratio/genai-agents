# Stratio Data plugin

Data analytics vertical for Stratio Cowork. Bundles the `data-analytics` agent: a senior BI/BA analyst that turns business questions into actionable analyses with real data from governed domains.

## What's inside

| Agent | Purpose |
|---|---|
| [data-analytics](../../agents/data-analytics/) | Full BI/BA workflow: data discovery on governed domains, EDA and profiling, hypothesis-driven analysis with Python (pandas, scipy, scikit-learn), visualisations (matplotlib, seaborn, plotly), and multi-format deliverable generation (PDF, DOCX, PPTX, Dashboard web, Web article, Poster/Infographic, XLSX). |

The agent imports the skills it needs (`stratio-data`, `quality-report`, `pdf-writer`, `docx-writer`, `pptx-writer`, `xlsx-writer`, `web-craft`, `canvas-craft`, `brand-kit`, …) via its `imported-skills` manifest. They travel inside the agent bundle and are linked to the agent at install time in Cowork.

## Supported platforms

| Platform | Supported | Notes |
|---|---|---|
| Stratio Cowork | yes | Deployable as an `agents/v1` wrapper bundle. |
| Claude (claude-plugin) | **no** | Claude marketplace plugins do not support agents. |

## Installation

The plugin produces one artifact:

- `dist/stratio-data-stratio-cowork-{version}.zip` — Stratio Cowork wrapper bundle.

Use the `upload-plugin` task of the [`cowork-api`](../../skills/cowork-api/) shared skill to deploy it.
