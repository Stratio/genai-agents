# Data Analytics Light Agent

A lightweight Business Intelligence and Business Analytics agent oriented to conversation: it analyzes governed data and responds directly in chat with inline visualizations.

## What is this agent

Data Analytics Light is a conversational version of the BI/BA agent. It connects to your organization's governed data to perform analyses and responds with insights directly in chat. Unlike the full Data Analytics agent, it **does not generate file deliverables** — no PDF, DOCX, PowerPoint or Excel files — and it does not read existing documents. Its strength is fast interactive analysis with professional visualizations embedded right in the conversation.

The agent can still apply consistent visual identity to its inline charts through the centralized theming catalog, so the graphics rendered in chat match your corporate look and feel.

## Capabilities

- Explore governed data domains and discover tables, columns and business rules
- Answer business questions with real data (KPIs, metrics, trends)
- Perform statistical analyses (correlations, distributions, hypothesis tests)
- Generate professional visualizations directly in chat
- Apply corporate visual identity (colors, chart palettes, typography) to inline charts via the centralized theming catalog (10 curated themes, extensible per client)
- **Assess data quality coverage** and produce quality summaries in chat (read-only, no file output). For file reports in any format use the full Data Analytics agent.
- Propose business terms to the governance dictionary

> **Scope.** This agent does not generate formal reports (no PDF, DOCX, PowerPoint or Excel files) and does not read existing documents. For file deliverables, document reading, or quality rule creation, use the sibling agents below.

## What you can ask

### Quick queries
- "How many customers do we have?"
- "What was the total sales for last quarter?"
- "What tables are in the billing domain?"

### Conversational analysis
- "Analyze the sales trend by month over the last year"
- "Is there a correlation between marketing spend and sales?"
- "Which products have the highest turnover?"
- "Compare revenue by sales channel"
- "Segment customers by purchasing behavior"

### Exploration
- "What data domains are available?"
- "Describe the tables in the customers domain"
- "What does the 'lifetime_value' field mean?"

### Quality coverage (chat only)
- "Assess the quality coverage of the sales domain"
- "What quality rules does the customers table have?"
- "Which dimensions are not covered in the billing table?"

### Visual identity
- "Use the luxury-refined theme for the charts in this analysis"
- "Apply our corporate palette to the inline visualizations"

> **Note on scope.** This agent delivers analysis and charts **only in chat**. For files (PDF / DOCX / PowerPoint / Excel / Markdown / web dashboard / poster), use the full **Data Analytics** agent. For creating or scheduling quality rules, use the **Data Quality** or **Governance Officer** agents.

## Available skills

| Command | Description |
|---------|-------------|
| `/analyze` | Data analysis: domain discovery, planning, queries, statistical analysis and inline visualizations |
| `/explore-data` | Quick exploration of domains, tables, columns and business terminology |
| `/assess-quality` | Quality coverage assessment (dimensions, existing rules, gaps) |
| `/quality-report` | Quality coverage summary **in chat only** (no file output in this agent) |
| `/propose-knowledge` | Propose discovered business terms to the governance dictionary |
| `/brand-kit` | Centralized theming catalog applied to inline charts (10 curated themes, extensible per client) |

## Required connections

- **Data MCP** (`stratio_data`): SQL queries, domain exploration, table and column profiling — configured via `MCP_SQL_URL` / `MCP_SQL_API_KEY`
- **Governance MCP** (`stratio_gov`, read-only): quality dimensions and rule metadata for coverage assessment — configured via `MCP_GOV_URL` / `MCP_GOV_API_KEY`

## Getting started

Start the agent and ask: "What data domains are available?"
