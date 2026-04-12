# Data Quality Agent

Expert agent in data governance and data quality that assesses quality coverage, identifies gaps, creates quality rules and delivers coverage reports in eight different formats.

## What this agent does

Data Quality is an assistant specialized in data quality that works on your governed data. It can assess the quality coverage of a domain, collection or table, identify which quality dimensions are missing, propose reasoned rules based on semantic context and real data profiling, and create them with your approval. It also generates coverage reports in multiple formats — from a quick chat summary to a multi-sheet Excel workbook, an interactive web dashboard or a printable infographic.

The agent evaluates quality across 11 dimensions (completeness, uniqueness, validity, consistency, timeliness, accuracy, referential integrity, availability, precision, reasonableness, and traceability) and always requires your approval before creating or modifying rules. It can also ingest local context (rule-spec workbooks in Excel, policy briefs in Word, reference decks in PowerPoint, regulation PDFs) and apply consistent visual branding to every deliverable.

## Capabilities

- Assess quality coverage by domain, collection, table or column
- Identify gaps: uncovered quality dimensions, tables or columns without coverage
- Propose reasoned quality rules based on semantic context and real data profiling
- Create quality rules with mandatory human approval (human-in-the-loop)
- Schedule automatic execution of quality rules
- Generate coverage reports in 8 formats (see [Output formats](#output-formats))
- Read and extract content from PDF, Word, PowerPoint and Excel files (policies, rule specs, reference catalogs)
- Author compliance briefs, executive decks, rule-spec workbooks and standalone visuals (posters, dashboards)
- Apply consistent visual identity across every report via the centralized theming catalog (10 curated themes, extensible per client)
- Consult and define Critical Data Elements (CDEs): identify, recommend, and tag the most critical assets in a domain with mandatory human approval
- Diagnose quality issues with real data profiling

## Output formats

For `/quality-report` you can pick any of:

| Format | Best for |
|---|---|
| **Chat** | Quick review inside the conversation, no file generated |
| **PDF** | Formal report with prose-driven narrative, compliance sign-off |
| **DOCX** | Editable Word document for audit teams and policy briefs |
| **PPTX** | Executive summary deck, steering-committee briefing |
| **Dashboard web** | Interactive HTML with KPI cards, filters, sortable tables |
| **Web article / Narrative report** | Self-contained editorial HTML page with narrative sections, inline KPI callouts and embedded charts |
| **Poster / Infographic** | Single-page visual summary of coverage by domain |
| **XLSX** | Multi-sheet coverage workbook with conditional formatting for audit and compliance teams |
| **Markdown** | Lightweight text format for documentation systems and wikis |

Every visual format applies the theme you choose at the start (or the default corporate theme).

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

### Reports (file generation)
- "Generate a PDF coverage report for the sales domain"
- "Create a PowerPoint executive summary of quality findings"
- "Build an interactive quality dashboard web"
- "Generate a one-page infographic of coverage by domain"
- "Export the rule catalog as an Excel workbook with conditional formatting"
- "Use the forensic-audit theme for this compliance report"
- "Write a Markdown summary of the quality status"

### Reading local context
- "Read this rule-spec Excel workbook and create the rules it defines"
- "Extract the compliance requirements from this policy DOCX"
- "Read the term catalog in this PDF to seed the rule review"

### Scheduling
- "Schedule the automatic execution of rules for the customers domain"
- "Create a daily schedule for the quality rules"

### Critical Data Elements
- "What are the CDEs of the customers domain?"
- "Define the critical data elements for domain X"
- "Recommend which columns should be CDEs in domain Y"
- "Tag table Z as a critical data element"

### Direct queries
- "What quality dimensions exist?"
- "What quality rules does table X have?"
- "What data domains are available?"

## Available skills

### Quality assessment, design and reporting
| Command | Description |
|---------|-------------|
| `/assess-quality` | Assess quality coverage by domain or table: covered dimensions, gaps and priorities |
| `/create-quality-rules` | Design and create quality rules to cover gaps, with mandatory human approval |
| `/create-quality-schedule` | Create automatic execution schedules for quality rules |
| `/quality-report` | Generate a formal coverage report in Chat, PDF, DOCX, PPTX, Dashboard web, Web article / Narrative report, Poster/Infographic, XLSX or Markdown |
| `/manage-critical-data-elements` | Consult or define Critical Data Elements (CDEs) for a governed domain, with mandatory human approval before tagging |

### Content readers
| Command | Description |
|---------|-------------|
| `/pdf-reader` | Extract text, tables, images, forms and attachments from PDF files |
| `/docx-reader` | Extract content from Word documents (`.docx` and legacy `.doc`) |
| `/pptx-reader` | Extract slides, notes and embedded assets from PowerPoint decks |
| `/xlsx-reader` | Read cell values, tables, formulas and metadata from Excel workbooks (rule specs, term catalogs) |

### Content writers
| Command | Description |
|---------|-------------|
| `/pdf-writer` | Create custom PDFs, merge/split, watermark, encrypt, fill forms |
| `/docx-writer` | Author and manipulate Word documents (merge, split, find-replace, `.doc` conversion) |
| `/pptx-writer` | Author and manipulate PowerPoint decks for executive summaries and rule training |
| `/xlsx-writer` | Author multi-sheet Excel workbooks (coverage, rule-spec templates, term catalogs), convert `.xls` to `.xlsx` |

### Visual artifacts and branding
| Command | Description |
|---------|-------------|
| `/web-craft` | Standalone interactive HTML: dashboards, landing pages, UI components |
| `/canvas-craft` | Single-page composition-dominated visuals: posters, infographics, covers |
| `/brand-kit` | Centralized theming catalog: 10 curated themes (corporate-formal, forensic-audit, luxury-refined, editorial-serious and more), extensible with client-specific themes |

## Required connections

- **Governance MCP**: quality dimensions, rule creation and management, schedules
- **Data MCP**: domain exploration, data profiling, SQL execution

## Getting started

Start the agent and ask: "What is the quality coverage of domain X?"
