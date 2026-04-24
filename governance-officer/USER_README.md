# Governance Officer Agent

Expert governance agent that combines semantic layer construction and data quality management into a single assistant — the full governance lifecycle under one roof.

## What this agent does

Governance Officer is a comprehensive assistant for both sides of data governance: building **semantic layers** and managing **data quality**. It can construct ontologies, business views, SQL mappings and semantic terms for your data domains, and also assess quality coverage, identify gaps, create quality rules, schedule their execution, and generate coverage reports in eight different formats — from executive decks to interactive dashboards.

The agent works with Stratio Data Governance via MCP tools, orchestrating the full lifecycle of governance artifacts with your approval at every critical step. It can also ingest local files (Word specifications, PowerPoint walkthroughs, Excel catalogs, PDFs) to enrich planning, and apply consistent visual branding to every deliverable through the centralized theming catalog.

## Capabilities

### Semantic layer
- Build and maintain complete semantic layers (ontologies, business views, SQL mappings, semantic terms)
- Publish business views for review
- Explore technical domains and published semantic layers
- Interactive ontology planning with local file reading (including `.docx` specifications and `.pptx` specification decks)
- Create data collections (technical domains) from data dictionary searches
- Manage business terms in the governance dictionary

### Data quality
- Assess quality coverage by domain, collection, table or column
- Identify gaps: uncovered quality dimensions, tables or columns without coverage
- Propose reasoned quality rules based on semantic context and real data profiling
- Create quality rules with mandatory human approval (human-in-the-loop)
- Schedule automatic execution of quality rules
- Generate coverage reports in 8 formats (see [Output formats](#output-formats))

### Content handling and branding
- Read and extract content from PDF, Word, PowerPoint and Excel files
- Author and manipulate PDF, Word, PowerPoint and Excel documents for compliance briefs, policy decks, ontology walkthroughs, term catalogs and rule-spec workbooks
- Apply consistent visual identity (colors, typography, chart palettes) to every visual deliverable using the centralized theming catalog (10 curated themes, extensible per client)

## Output formats

For quality coverage reports and other multi-format deliverables, you can pick any of:

| Format | Best for |
|---|---|
| **Chat** | Quick review inside the conversation, no file generated |
| **PDF** | Formal documents with prose-driven narrative, executive or compliance reports |
| **DOCX** | Editable Word documents for policy briefs and compliance reports |
| **PPTX** | Executive summary decks, steering-committee briefings, ontology walkthroughs |
| **Dashboard web** | Interactive HTML with KPI cards, filters and sortable tables |
| **Poster / Infographic** | Single-page visual summary for communication or display |
| **XLSX** | Multi-sheet quality-coverage workbook, ontology export, term catalog, compliance matrix with conditional formatting |
| **Markdown** | Lightweight text format for documentation systems and wikis |

Every visual format applies the theme you choose at the start of the deliverable (or the default corporate theme).

## What you can ask

### Semantic layer
- "Build the semantic layer for domain X"
- "Generate technical descriptions for domain Y"
- "Create an ontology for the customers domain"
- "Create business views and publish them"
- "Generate semantic terms for the views"
- "Create a business term for CLV"
- "Create a new data collection with tables from X"
- "Ingest this policy DOCX and propose business terms from the glossary"
- "Read this architecture deck and bootstrap the ontology from it"

### Data quality
- "What is the quality coverage of the customers domain?"
- "Create quality rules to cover the gaps in domain X"
- "Create a rule that verifies the email field has a valid format"
- "Schedule the automatic execution of rules for the customers domain"

### Reports and deliverables
- "Generate a PDF coverage report for the sales domain"
- "Create a PowerPoint executive summary of quality findings"
- "Build an interactive quality dashboard web for the operations team"
- "Generate a one-page infographic of coverage by domain"
- "Export the rule catalog as an Excel workbook with conditional formatting"
- "Use the forensic-audit theme for the compliance report"

### Combined workflows
- "Build the semantic layer for domain X and then assess its quality"
- "What governance artifacts exist for domain Y?"
- "Build the customers ontology and then generate a compliance briefing deck in PowerPoint"
- "Assess quality and produce a branded coverage workbook in Excel for the audit team"

## Available skills

### Semantic layer
| Command | Description |
|---------|-------------|
| `/build-semantic-layer` | Full semantic layer pipeline: terms, ontology, views, mappings, semantic terms |
| `/create-technical-terms` | Create technical descriptions for tables and columns |
| `/create-ontology` | Create, extend or delete ontology classes with interactive planning |
| `/create-business-views` | Create, regenerate or delete business views |
| `/create-sql-mappings` | Create or update SQL mappings for existing views |
| `/create-semantic-terms` | Generate business semantic terms for views |
| `/manage-business-terms` | Create business terms in the governance dictionary |
| `/create-data-collection` | Search tables in the dictionary and create new data collections |
| `/stratio-semantic-layer` | Reference for the semantic-layer governance MCP tools (patterns, best practices) |

### Data quality
| Command | Description |
|---------|-------------|
| `/assess-quality` | Assess quality coverage by domain or table: covered dimensions, gaps and priorities |
| `/create-quality-rules` | Design and create quality rules with mandatory human approval |
| `/create-quality-schedule` | Create automatic execution schedules for quality rules |
| `/quality-report` | Generate a formal coverage report in Chat, PDF, DOCX, PPTX, Dashboard web, Poster/Infographic, XLSX or Markdown |

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
| `/pdf-writer` | Create custom PDFs, merge/split, watermark, encrypt, fill forms |
| `/docx-writer` | Author and manipulate Word documents (merge, split, find-replace, `.doc` conversion) |
| `/pptx-writer` | Author and manipulate PowerPoint decks (merge, split, reorder, find-replace) |
| `/xlsx-writer` | Author multi-sheet Excel workbooks (coverage, term catalogs, rule specs), convert `.xls` to `.xlsx` |

### Visual artifacts and branding
| Command | Description |
|---------|-------------|
| `/web-craft` | Standalone interactive HTML: dashboards, landing pages, UI components |
| `/canvas-craft` | Single-page composition-dominated visuals: posters, infographics, covers |
| `/brand-kit` | Centralized theming catalog: 10 curated themes (corporate-formal, forensic-audit, luxury-refined, editorial-serious and more), extensible with client-specific themes |

## Required connections

- **Governance MCP**: semantic layer management, quality dimensions, rule creation and scheduling
- **Data MCP**: domain exploration, data profiling, SQL execution

## Getting started

Start the agent and ask: "Build the semantic layer for domain X" or "What is the quality coverage of domain Y?"
