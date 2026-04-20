# Data Quality Agent

Expert agent in data governance and data quality that assesses quality coverage, identifies gaps, and creates quality rules.

## What this agent does

Data Quality is an assistant specialized in data quality that works on your governed data. It can assess quality coverage of a domain, collection, or table, identify which quality dimensions are missing, propose reasoned quality rules based on semantic context and real data, and create those rules with your approval. It also generates coverage reports in multiple formats.

The agent evaluates quality across 11 dimensions (completeness, uniqueness, validity, consistency, timeliness, accuracy, referential integrity, availability, precision, reasonableness, and traceability) and always requires your approval before creating or modifying rules.

## Capabilities

- Assess quality coverage by domain, collection, table, or column
- Identify gaps: uncovered quality dimensions, tables or columns without coverage
- Propose reasoned quality rules based on semantic context and real data
- Create quality rules with mandatory human approval (human-in-the-loop)
- Schedule automatic execution of quality rules (scheduling)
- Generate coverage reports in chat, PDF, DOCX, or Markdown
- Diagnose quality issues with real data profiling

## What you can ask

### Coverage assessment
- "What is the quality coverage of the customers domain?"
- "Which tables in the sales domain have no quality rules?"
- "Assess the quality of the email column in the customers table"
- "What quality dimensions are missing in the billing table?"

### Rule creation
- "Create quality rules to cover the gaps in domain X"
- "Complete the quality coverage of the billing table"
- "Create a rule that verifies the email field has a valid format"
- "I need uniqueness rules for the primary keys in domain Y"

### Reports
- "Generate a PDF coverage report for the sales domain"
- "Write a Markdown report with the quality status"
- "Give me a coverage summary of the entire domain"

### Scheduling
- "Schedule the automatic execution of rules for the customers domain"
- "Create a daily schedule for the quality rules"

### Direct queries
- "What quality dimensions exist?"
- "What quality rules does table X have?"
- "What data domains are available?"

## Available skills

| Command | Description |
|---------|-------------|
| `/assess-quality` | Assess quality coverage by domain or table: covered dimensions, gaps, and priorities |
| `/create-quality-rules` | Design and create quality rules to cover gaps, with mandatory human approval |
| `/create-quality-planification` | Create automatic execution schedules for quality rules |
| `/quality-report` | Generate a formal coverage report in PDF, DOCX, or Markdown |
| `/pdf-reader` | Read and extract content from PDF files (text, tables, images, forms) |
| `/pdf-writer` | Create custom PDF documents, merge/split PDFs, add watermarks, encrypt, fill forms |

## Required connections

- **Governance MCP**: quality dimensions, rule creation and management, schedules
- **Data MCP**: domain exploration, data profiling, SQL execution

## Getting started

Start the agent and ask: "What is the quality coverage of domain X?"
