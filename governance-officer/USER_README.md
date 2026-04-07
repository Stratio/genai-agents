# Governance Officer Agent

Expert governance agent combining semantic layer building and data quality management into a single assistant.

## What this agent does

Governance Officer is a comprehensive assistant that handles both sides of data governance: building semantic layers and managing data quality. It can construct ontologies, business views, SQL mappings, and semantic terms for your data domains, and also assess quality coverage, identify gaps, create quality rules, and generate coverage reports.

The agent works with Stratio Data Governance via MCP tools, orchestrating the full lifecycle of governance artifacts with your approval at every critical step.

## Capabilities

### Semantic layer
- Build and maintain complete semantic layers (ontologies, views, mappings, terms)
- Publish business views for review
- Explore technical domains and published semantic layers
- Interactive ontology planning with local file reading
- Create data collections (technical domains) from data dictionary searches
- Manage business terms in the governance dictionary

### Data quality
- Assess quality coverage by domain, collection, table, or column
- Identify gaps: uncovered quality dimensions, tables or columns without coverage
- Propose reasoned quality rules based on semantic context and real data
- Create quality rules with mandatory human approval (human-in-the-loop)
- Schedule automatic execution of quality rules
- Generate coverage reports in chat, PDF, DOCX, or Markdown

## What you can ask

### Semantic layer
- "Build the semantic layer for domain X"
- "Generate technical descriptions for domain Y"
- "Create an ontology for the customer domain"
- "Create business views and publish them"
- "Generate semantic terms for the views"
- "Create a business term for CLV"
- "Create a new data collection with tables from X"

### Data quality
- "What is the quality coverage of the customers domain?"
- "Create quality rules to cover the gaps in domain X"
- "Create a rule that verifies the email field has a valid format"
- "Generate a PDF coverage report for the sales domain"
- "Schedule the automatic execution of rules for the customers domain"

### Combined workflows
- "Build the semantic layer for domain X and then assess its quality"
- "What governance artifacts exist for domain Y?"

## Available skills

| Command | Description |
|---------|-------------|
| `/build-semantic-layer` | Full semantic layer pipeline: terms, ontology, views, mappings, semantic terms |
| `/generate-technical-terms` | Generate technical descriptions for tables and columns |
| `/create-ontology` | Create, extend, or delete ontology classes with interactive planning |
| `/create-business-views` | Create, regenerate, or delete business views |
| `/create-sql-mappings` | Create or update SQL mappings for existing views |
| `/create-semantic-terms` | Generate business semantic terms for views |
| `/manage-business-terms` | Create business terms in the governance dictionary |
| `/create-data-collection` | Search tables in the dictionary and create new data collections |
| `/assess-quality` | Assess quality coverage by domain or table |
| `/create-quality-rules` | Design and create quality rules with mandatory human approval |
| `/create-quality-planification` | Create automatic execution schedules for quality rules |
| `/quality-report` | Generate a formal coverage report in PDF, DOCX, or Markdown |

## Required connections

- **Governance MCP**: semantic layer management, quality dimensions, rule creation
- **Data MCP**: domain exploration, data profiling, SQL execution

## Getting started

Start the agent and ask: "Build the semantic layer for domain X" or "What is the quality coverage of domain Y?"
