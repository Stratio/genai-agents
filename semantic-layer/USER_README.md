# Semantic Layer Builder Agent

An agent specialized in building and maintaining semantic layers in Stratio Data Governance — the full pipeline from technical table descriptions to business semantic terms, with interactive planning and the ability to ingest your own specification documents.

## What is this agent

Semantic Layer Builder guides you in the creation, maintenance and publication of the governance artifacts that compose the semantic layer of a data domain. It works with a 5-phase pipeline — from technical table descriptions to the generation of business semantic terms — and can execute each phase independently or as a complete pipeline.

The agent can also ingest local context to enrich planning: Word specifications with glossaries and business rules, PowerPoint decks with architecture walkthroughs, plain CSV catalogs and ontology files (`.owl`, `.ttl`).

It does not execute data queries or generate files on disk — its output is direct interaction with the governance tools and summaries in chat.

## Capabilities

- Build complete semantic layers with a guided 5-phase pipeline
- Generate automatic technical descriptions of tables and columns
- Create and manage ontologies with interactive planning
- Create business views from existing ontologies
- Generate and update SQL mappings for business views
- Create business semantic terms
- Manage business terms with relationships to data assets
- Create data collections (technical domains) from dictionary searches
- Diagnose the status of a domain's semantic layer
- Ingest local specification documents to enrich planning: Word files (`.docx`/`.doc`), PowerPoint decks (`.pptx`/`.ppt`), CSV catalogs and ontology files (`.owl`, `.ttl`)

## What you can ask

### Full pipeline
- "Build the semantic layer for the customers domain"
- "I want to create the semantic layer for the billing domain from scratch"

### Individual phases
- "Generate the technical descriptions of the tables in the sales domain"
- "Create an ontology for the customers domain"
- "Create the business views from the existing ontology"
- "Update the SQL mappings for the domain's views"
- "Generate the semantic terms for the published views"

### Artifact management
- "Create a business term for Customer Lifetime Value"
- "Create a data collection with the billing tables"
- "Publish the business views for domain Y"

### Ingesting local specifications
- "Ingest this policy DOCX and propose business terms from the glossary"
- "Read this architecture deck and bootstrap the ontology from it"
- "Use this CSV as a seed for the technical terms"

### Exploration and diagnostics
- "What is the status of the semantic layer for domain X?"
- "What tables are there about customers in the data dictionary?"
- "What data domains are available?"

## Available skills

### Semantic layer pipeline
| Command | Description |
|---------|-------------|
| `/build-semantic-layer` | Complete 5-phase pipeline to build the semantic layer of a domain |
| `/create-technical-terms` | Create automatic technical descriptions of tables and columns |
| `/create-ontology` | Create, extend or delete ontology classes with interactive planning |
| `/create-business-views` | Create, regenerate or delete business views from an ontology |
| `/create-sql-mappings` | Create or update SQL mappings for existing business views |
| `/create-semantic-terms` | Generate business semantic terms for the views of a domain |
| `/manage-business-terms` | Create business terms with relationships to data assets |
| `/create-data-collection` | Search tables in the dictionary and create a new data collection |

### Local file ingestion
| Command | Description |
|---------|-------------|
| `/docx-reader` | Read Word documents (`.docx` and legacy `.doc`) — specifications, glossaries, business rules |
| `/pptx-reader` | Read PowerPoint decks (`.pptx` and legacy `.ppt`) — architecture walkthroughs, specification decks |

### MCP tools reference
| Command | Description |
|---------|-------------|
| `/stratio-semantic-layer` | Reference for the semantic-layer governance MCP tools: patterns, best practices, tool-by-tool guidance |

## Required connections

- **Governance MCP**: creation and management of semantic artifacts (ontologies, views, terms, business terms)
- **Data MCP**: exploration of domains and data dictionary

## Getting started

Start the agent and ask: "What is the status of the semantic layer for domain X?"
