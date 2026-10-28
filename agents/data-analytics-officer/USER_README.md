# Data Analytics Agent

A senior BI/BA analyst agent that turns business questions into actionable analyses with real data from governed domains, and ships the result in the format you need — from a PDF report to an Excel workbook, from an interactive dashboard to a single-page infographic.

## What is this agent

Data Analytics is a complete BI/BA assistant that connects to your organization's governed data to perform advanced analyses. It can discover data domains, execute queries, perform statistical analyses, generate professional visualizations, and deliver results in chat or in **six analytical formats**: artifacts in GenAI UI (interactive dashboards or report pages you can share and open again), PDF reports, Word documents, PowerPoint presentations, Excel workbooks and single-page posters/infographics.

It can also ingest local context (PDF contracts, Word briefs, PowerPoint decks, Excel spreadsheets) and apply consistent visual identity through a centralized theming catalog.

## Capabilities

- Explore governed data domains and discover tables, columns and business rules
- Answer business questions with real data (KPIs, metrics, trends)
- Perform advanced statistical analyses (correlations, distributions, hypothesis tests)
- Automatic data segmentation and clustering (RFM, KMeans, DBSCAN)
- Generate professional visualizations (charts, graphs, dashboards)
- **Analytical reports** in chat or in six formats (Artifact — interactive dashboard or report page in GenAI UI —, PDF, DOCX, PowerPoint, Excel, poster/infographic) — generated when you ask for an analysis with a deliverable
- **Lightweight visual deliverables** without running an analysis — quick posters and infographics, standalone interactive dashboards, simple PDFs with a few KPIs, ad-hoc Word and Excel documents
- **Read existing documents** — PDFs, Word (`.docx`/`.doc`), PowerPoint (`.pptx`/`.ppt`) and Excel (`.xlsx`/`.xls`) — to extract text, tables, slides, cell values and metadata
- **Assess data quality coverage** and generate quality reports in 8 formats (Chat, Artifact, PDF, DOCX, PPTX, Poster/Infographic, XLSX, Markdown) — read-only, does not create or schedule rules
- Apply consistent visual identity (colors, typography, chart palettes) to every deliverable using the centralized theming catalog (10 curated themes, extensible per client)
- Propose business terms to the governance dictionary

## Output formats

When you ask for a deliverable, pick the format that matches the audience:

| Format | Best for |
|---|---|
| **Chat** | The analysis or summary in this conversation, with no deliverable |
| **Artifact** (Recommended) | An interactive dashboard or report page in GenAI UI that can be shared and opened again |
| **PDF** | Formal multi-page reports with prose-driven narrative |
| **DOCX** | Editable Word documents for review and iteration |
| **PPTX** | Executive decks, steering-committee briefings |
| **Poster / Infographic** | Single-page visual summary for communication or display |
| **XLSX** | Analytical workbooks (cover/KPI + parameters + detail + appendix), pivot matrices, tabular exports, quantitative models |

Every visual format applies the theme you choose at the start (or the default corporate theme).

## What you can ask

### Quick queries
- "How many customers do we have?"
- "What was the total sales for last quarter?"
- "What tables are in the billing domain?"

### Advanced analysis
- "Analyze sales evolution by region over the last 12 months"
- "What factors most influence customer churn?"
- "Compare north vs south store performance"
- "Segment customers by purchasing behavior"
- "Are there anomalies in last month's billing data?"

### Analytical reports (analysis + deliverable)
- "Generate a PDF report with the profitability analysis"
- "Create an interactive web dashboard with sales KPIs and the deep-dive narrative"
- "Prepare a PowerPoint presentation with the quarterly results and key findings"
- "Generate a Word report with the cohort analysis"
- "Produce an analytical Excel workbook with KPI cover and detailed pivot sheets for last quarter"
- "Use the luxury-refined theme for the executive report"

### Lightweight visuals (no analysis, just an artifact)
- "Make a poster with last quarter's top 3 KPIs" *(canvas-craft)*
- "Build a marketing infographic for the launch numbers" *(canvas-craft)*
- "Give me a one-page PDF with these 3 sales numbers" *(pdf-writer)*
- "Standalone interactive dashboard for the operations team — no narrative" *(artifacts)*
- "Repackage yesterday's analysis output as a PDF in another style" *(pdf-writer)*
- "Export this list of figures as an Excel table with formulas" *(xlsx-writer)*

### Repackaging an exploration or quick lookup
After exploring a domain, a quality assessment, or a quick MCP lookup, you can ask to package what you saw — without re-analyzing:
- After `/explore-data` of the sales domain → "Now give me this in a PDF" *(pdf-writer)*
- After listing the tables of a domain → "Make me a one-page poster with this list" *(canvas-craft)*
- After `/assess-quality` → "Pass this to a standalone dashboard" *(artifacts)*
- After any SQL result → "Drop this as an Excel workbook" *(xlsx-writer)*

(If you add an analytical verb — "now analyze this and give me a PDF" — the agent runs the full analysis instead of just packaging.)

### Reading existing documents
- "Read this PDF and extract the tables"
- "What does this contract PDF say about renewal terms?"
- "Read this Excel and extract the revenue table"
- "Extract the bullet points from this PowerPoint deck"
- "Read this Word report and summarise the KPIs section"

### Exploration
- "What data domains are available?"
- "Describe the tables in the customer domain"
- "What does the 'churn_score' field mean in the customer table?"

### Quality coverage
- "Assess the quality coverage of the sales domain"
- "What quality rules does the customers table have?"
- "Generate a quality PDF report for the logistics domain"
- "Build a quality dashboard for the billing domain"
- "Export the quality coverage of domain X as an Excel workbook"

> Note: this agent evaluates and reports. To create rules or schedule executions, use the Data Quality or Governance Officer agents.

## Available skills

### Analysis and exploration
| Command | Description |
|---------|-------------|
| `/analyze` | Full analysis: domain discovery, planning, queries, statistical analysis, visualizations and multi-format deliverables (Chat, Artifact, PDF, DOCX, PPTX, poster, XLSX) |
| `/explore-data` | Quick exploration of domains, tables, columns and business terminology |
| `/propose-knowledge` | Propose discovered business terms to the governance dictionary |

### Quality coverage (read-only)
| Command | Description |
|---------|-------------|
| `/assess-quality` | Quality coverage assessment (dimensions, existing rules, gaps) |
| `/quality-report` | Generate a formal quality coverage report in Chat, Artifact, PDF, DOCX, PPTX, Poster/Infographic, XLSX or Markdown |

### Content readers
| Command | Description |
|---------|-------------|
| `/pdf-reader` | Extract text, tables, images, forms and attachments from PDF files |
| `/docx-reader` | Extract content from Word documents (`.docx` and legacy `.doc`) |
| `/pptx-reader` | Extract slides, notes and embedded assets from PowerPoint decks |
| `/xlsx-reader` | Read cell values, tables, formulas and metadata from Excel workbooks |

### Content writers
| Command | Description |
|---------|-------------|
| `/pdf-writer` | Multi-page or prose-dominated PDFs (data-light reports with ≤3 KPIs, invoices, letters, newsletters, certificates). Also merge/split/rotate, watermark, encrypt, fill forms |
| `/docx-writer` | Author and manipulate Word documents (merge, split, find-replace, `.doc` conversion) |
| `/pptx-writer` | Author and manipulate PowerPoint decks outside the analytical pipeline (merge, split, reorder, find-replace) |
| `/xlsx-writer` | Author analytical and ad-hoc Excel workbooks (cover/KPI + detail, pivot matrices, tabular exports), convert `.xls` to `.xlsx` |

### Visual artifacts and branding
| Command | Description |
|---------|-------------|
| `/canvas-craft` | Single-page composition-dominated visuals: posters, infographics, covers, marketing one-pagers (PDF or PNG) |
| `/web-craft` | Standalone interactive HTML files: UI components, landing pages, and dashboards or web articles as .html files when you ask for an .html file |
| `/brand-kit` | Centralized theming catalog: 10 curated themes (corporate-formal, luxury-refined, editorial-serious, technical-minimal and more), extensible with client-specific themes |

## Required connections

- **Data MCP** (`stratio_data`): SQL queries, domain exploration, table and column profiling — configured via `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **Governance MCP** (`stratio_gov`, read-only): quality dimensions and rule metadata for coverage assessment — configured via `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Getting started

Start the agent and ask: "What data domains are available?"
