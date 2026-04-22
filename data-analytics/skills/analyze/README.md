# analyze

Local skill of the `data-analytics` agent. Drives the full analytical workflow: intake, clarifying questions, plan, querying governed data via MCP, Python analysis, visualizations, optional testing, iteration, reasoning and validation documentation, and deliverable generation (PDF, DOCX, notebook, PPTX).

This is the single analytical engine of the agent; every other agent skill (`update-memory`, sub-guides `report/`, `reasoning-guide.md`, `validation-guide.md`) is orchestrated from here.

## What it does

- Reads governed data via MCP (`query_data` with natural-language questions) — no manual SQL
- Pandas/numpy/scipy analysis in scripts under `output/[ANALYSIS_DIR]/scripts/`
- Statistical tests, clustering, feature importance via `scikit-learn` + `statsmodels`
- Trend / seasonality with `pymannkendall`
- Visualizations with `matplotlib`, `seaborn`, `plotly`
- Static PNG export of Plotly charts via `kaleido`
- Multi-format reports (HTML → PDF via `weasyprint`, DOCX via `python-docx`, PPTX via `python-pptx`, Markdown, notebook via `nbconvert`)
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
- `jinja2>=3.1`
- `markdown>=3.7`
- `weasyprint>=65`
- `beautifulsoup4>=4.12`
- `nbformat>=5.10`
- `nbclient>=0.10`
- `nbconvert>=7.16`
- `python-pptx>=1.0`
- `python-docx>=1.1`
- `openpyxl>=3.1`
- `tabulate>=0.9`

## System dependencies (apt)

- `libcairo2` + `libpango-1.0-0` + `libpangoft2-1.0-0` + `libgdk-pixbuf2.0-0` — backing `weasyprint`
- `shared-mime-info` + `fonts-liberation` — MIME and TrueType for rendering

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Sub-guides

- `report/report.md` — multi-format deliverable generation
- `reasoning-guide.md` — how and when to document reasoning
- `validation-guide.md` — validation blocks and formats
- `skills-guides/stratio-data-tools.md` — MCP-first data retrieval (inherited from the agent)
