# analyze

Local skill of the `data-analytics` agent. Drives the full analytical workflow: intake, clarifying questions, plan, querying governed data via MCP, Python analysis, visualizations, optional testing, iteration, reasoning and validation documentation, and orchestration of deliverable generation via the writer skills declared in `AGENTS.md §8`.

This is the single analytical engine of the agent; every other local skill (`update-memory`) is orchestrated from here. Deliverable generation is delegated to `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` + `brand-kit`.

## What it does

- Reads governed data via MCP (`query_data` with natural-language questions) — no manual SQL
- Pandas/numpy/scipy analysis in scripts under `output/[ANALYSIS_DIR]/scripts/`
- Statistical tests, clustering, feature importance via `scikit-learn` + `statsmodels`
- Trend / seasonality with `pymannkendall`
- Visualizations with `matplotlib`, `seaborn`, `plotly`
- Static PNG export of Plotly charts via `kaleido`
- Writes the internal analytical markdown (`report.md`) and hands off to the writer skills for each selected format
- Optional per-script `pytest`+`pytest-mock` testing

## Python dependencies

- `pandas>=3.0`
- `numpy>=2.1`
- `scipy>=1.14`
- `pymannkendall>=1.4`
- `scikit-learn>=1.5`
- `statsmodels>=0.14.4`
- `matplotlib>=3.9`
- `seaborn>=0.13`
- `plotly>=6.0,<6.2` (upper-bound aligned with `kaleido 0.2.x`)
- `kaleido>=0.2,<1`
- `openpyxl>=3.1`
- `tabulate>=0.9`

Writer skills (`pdf-writer`, `docx-writer`, `pptx-writer`) bring their own Python stack when invoked.

## System dependencies (apt)

None specific to `/analyze` itself. The writer skills declare their own system dependencies.

## Sub-guides

- `visualization.md` — chart type selection, storytelling, anti-overlap principles
- `analytical-dashboard.md` — composition patterns for analytical dashboards (loaded by `web-craft` when the format is Dashboard web)
- `reasoning-guide.md` — how and when to document reasoning
- `validation-guide.md` — validation blocks and formats
- `analytical-patterns.md` — operationalised patterns (Pareto, cohorts, funnel, RFM, etc.)
- `advanced-analytics.md` — statistical rigor, prospective analysis, anomaly detection, root cause
- `clustering-guide.md` — segmentation, clustering, feature importance
- `chart_layout.py` — Python utility for anti-overlap layout on matplotlib/Plotly charts
- `skills-guides/stratio-data-tools.md` — MCP-first data retrieval (inherited from the agent)
