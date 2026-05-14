# Semantic Layer Builder Agent

An agent specialized in building and maintaining semantic layers in Stratio Data Governance — the full pipeline from technical table descriptions to business semantic terms, with interactive planning and the ability to ingest your own specification documents.

## What is this agent

Semantic Layer Builder guides you in the creation, maintenance and publication of the governance artifacts that compose the semantic layer of a data domain. It works with a 5-phase pipeline — from technical table descriptions to the generation of business semantic terms — and can execute each phase independently or as a complete pipeline.

The agent can also ingest local context to enrich planning: Word specifications with glossaries and business rules, PowerPoint decks with architecture walkthroughs, plain CSV catalogs and ontology files (`.owl`, `.ttl`).

It can run read-only data queries to validate the SQL of mappings before publishing and to sanity-check the published semantic layer end-to-end. It does not generate files on disk — its main output is direct interaction with the governance tools and summaries in chat.

## Capabilities

- Build complete semantic layers with a guided 5-phase pipeline
- Generate automatic technical descriptions of tables and columns
- Refine the virtual foreign keys of existing tables: add missing ones, fix wrong targets, remove obsolete ones — without regenerating the technical terms
- Create and manage ontologies with interactive planning
- Create business views from existing ontologies
- Generate and update SQL mappings for business views
- Create business semantic terms
- Manage business terms with relationships to data assets
- Create data collections (technical domains) from dictionary searches
- Diagnose the status of a domain's semantic layer
- Validate the SQL of mappings with a sample query (LIMIT 5) before publishing
- Sanity-check the published `semantic_<domain>` with 1–3 business questions
- Ingest local specification documents to enrich planning: Word files (`.docx`/`.doc`), PowerPoint decks (`.pptx`/`.ppt`), CSV catalogs and ontology files (`.owl`, `.ttl`)

## What you can ask

### Full pipeline
- "Build the semantic layer for the customers domain"
- "I want to create the semantic layer for the billing domain from scratch"

### Individual phases
- "Generate the technical descriptions of the tables in the sales domain"
- "Detect the missing foreign keys in card_csv and disp_csv" / "Delete fk_obsolete from order_csv" / "Add a foreign key from orders.customer_id to customers.id"
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

### Validation
- "Run a top 5 of each mapping before I OK the publication"
- "Validate the queries before publishing"
- "Run a sanity check on the published semantic layer of X"

## Available skills

### Semantic layer pipeline
| Command | Description |
|---------|-------------|
| `/build-semantic-layer` | Complete 5-phase pipeline to build the semantic layer of a domain |
| `/create-technical-terms` | Create automatic technical descriptions of tables and columns |
| `/refine-foreign-keys` | Add, modify or remove virtual foreign keys on tables that already have technical terms |
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
