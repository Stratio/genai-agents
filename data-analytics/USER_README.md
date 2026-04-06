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

## Available skills

| Command | Description |
|---------|-------------|
| `/analyze` | Full analysis: domain discovery, planning, queries, statistical analysis, visualizations, and reports |
| `/report` | Professional report generation in PDF, DOCX, interactive web, or PowerPoint |
| `/explore-data` | Quick exploration of domains, tables, columns, and business terminology |
| `/update-memory` | Update persistent memory with preferences and learned patterns |
| `/propose-knowledge` | Propose discovered business terms to the governance dictionary |

## Required connections

- **Data MCP**: SQL queries, domain exploration, table and column profiling

## Getting started

Start the agent and ask: "What data domains are available?"
