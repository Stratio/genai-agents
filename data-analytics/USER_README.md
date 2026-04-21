# Data Analytics Agent

A senior BI/BA analyst agent that turns business questions into actionable analyses with real data from governed domains.

## What is this agent

Data Analytics is a complete BI/BA assistant that connects to your organization's governed data to perform advanced analyses. It can discover data domains, execute queries, perform statistical analyses, generate professional visualizations, and deliver results in multiple formats: PDF reports, Word documents, PowerPoint presentations, or interactive web dashboards.

The agent maintains memory between sessions, remembering your analysis preferences, known data patterns, and learned heuristics.

## Capabilities

- Explore governed data domains and discover tables, columns, and business rules
- Answer business questions with real data (KPIs, metrics, trends)
- Perform advanced statistical analyses (correlations, distributions, hypothesis tests)
- Automatic data segmentation and clustering (RFM, KMeans, DBSCAN)
- Generate professional visualizations (charts, graphs, dashboards)
- **Analytical reports** in multiple formats (PDF, DOCX, PowerPoint, interactive web) — generated when you ask for an analysis with a deliverable
- **Lightweight visual deliverables** without running an analysis — quick posters and infographics, standalone interactive dashboards, simple PDFs with a few KPIs
- **Read existing PDFs** to extract text, tables, and form data
- **Assess data quality coverage** and generate quality reports (Chat / PDF / DOCX / Markdown) — read-only, does not create or schedule rules
- Remember preferences and previous analyses between sessions (persistent memory)
- Propose business terms to the governance dictionary

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

### Lightweight visuals (no analysis, just an artifact)
- "Make a poster with last quarter's top 3 KPIs" *(canvas-craft)*
- "Build a marketing infographic for the launch numbers" *(canvas-craft)*
- "Give me a one-page PDF with these 3 sales numbers" *(pdf-writer)*
- "Standalone interactive dashboard for the operations team — no narrative" *(web-craft)*
- "Repackage yesterday's analysis output as a PDF in another style" *(pdf-writer)*

### Repackaging an exploration or quick lookup
After exploring a domain, a quality assessment, or a quick MCP lookup, you can ask to package what you saw — without re-analyzing:
- After `/explore-data` of the sales domain → "Now give me this in a PDF" *(pdf-writer)*
- After listing the tables of a domain → "Make me a one-page poster with this list" *(canvas-craft)*
- After `/assess-quality` → "Pass this to a standalone dashboard" *(web-craft)*

(If you add an analytical verb — "now analyze this and give me a PDF" — the agent runs the full analysis instead of just packaging.)

### Reading PDFs
- "Read this PDF and extract the tables"
- "What does this contract PDF say about renewal terms?"

### Exploration
- "What data domains are available?"
- "Describe the tables in the customer domain"
- "What does the 'churn_score' field mean in the customer table?"

### Quality coverage
- "Assess the quality coverage of the sales domain"
- "What quality rules does the customers table have?"
- "Generate a quality PDF report for the logistics domain"
- "Which dimensions are not covered in the billing table?"

> Note: this agent evaluates and reports. To create rules or schedule executions, use the Data Quality or Governance Officer agents.

## Available skills

| Command | Description |
|---------|-------------|
| `/analyze` | Full analysis: domain discovery, planning, queries, statistical analysis, visualizations, and multi-format deliverables (PDF, DOCX, interactive web, PowerPoint — generated internally) |
| `/explore-data` | Quick exploration of domains, tables, columns, and business terminology |
| `/assess-quality` | Quality coverage assessment (dimensions, existing rules, gaps) |
| `/quality-report` | Generate a formal quality coverage report (Chat / PDF / DOCX / Markdown) |
| `/update-memory` | Update persistent memory with preferences and learned patterns |
| `/propose-knowledge` | Propose discovered business terms to the governance dictionary |
| `/pdf-reader` | Read and extract content from PDF files (text, tables, images, forms, attachments) |
| `/pdf-writer` | Designed multi-page or prose-dominated PDFs (data-light reports with ≤3 KPIs, invoices, letters, newsletters, certificates). Also merge/split/rotate, watermark, encrypt, fill forms |
| `/canvas-craft` | Single-page composition-dominated visuals: posters, infographics, covers, marketing one-pagers (PDF or PNG) |
| `/web-craft` | Standalone interactive HTML: dashboards without analytical narrative, UI components, landing pages |

## Required connections

- **Data MCP** (`stratio_data`): SQL queries, domain exploration, table and column profiling — configured via `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **Governance MCP** (`stratio_gov`, read-only): quality dimensions and rule metadata for coverage assessment — configured via `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Getting started

Start the agent and ask: "What data domains are available?"
