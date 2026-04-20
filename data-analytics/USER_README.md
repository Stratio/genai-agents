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
- Create reports in multiple formats: PDF, DOCX, PowerPoint, interactive web
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

### Reports
- "Generate a PDF report with the profitability analysis"
- "Create an interactive web dashboard with sales KPIs"
- "Prepare a PowerPoint presentation with the quarterly results"
- "Generate a Word report with the cohort analysis"

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
| `/analyze` | Full analysis: domain discovery, planning, queries, statistical analysis, visualizations, and reports |
| `/report` | Professional report generation in PDF, DOCX, interactive web, or PowerPoint |
| `/explore-data` | Quick exploration of domains, tables, columns, and business terminology |
| `/assess-quality` | Quality coverage assessment (dimensions, existing rules, gaps) |
| `/quality-report` | Generate a formal quality coverage report (Chat / PDF / DOCX / Markdown) |
| `/update-memory` | Update persistent memory with preferences and learned patterns |
| `/propose-knowledge` | Propose discovered business terms to the governance dictionary |
| `/pdf-reader` | Read and extract content from PDF files (text, tables, images, forms, attachments) |
| `/pdf-writer` | Create custom PDF documents, merge/split/rotate PDFs, add watermarks, encrypt, fill forms |

## Required connections

- **Data MCP** (`stratio_data`): SQL queries, domain exploration, table and column profiling — configured via `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **Governance MCP** (`stratio_gov`, read-only): quality dimensions and rule metadata for coverage assessment — configured via `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Getting started

Start the agent and ask: "What data domains are available?"
