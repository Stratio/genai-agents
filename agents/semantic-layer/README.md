# semantic-layer

Agent specialized in building and maintaining semantic layers in Stratio Data Governance.

## Capabilities

- Building semantic layers via governance MCPs (`stratio_gov` server)
- Exploring technical domains and published semantic layers (`stratio_data` server)
- Complete 5-phase pipeline: technical terms → ontology → business views → SQL mappings → semantic terms
- Interactive ontology planning (with reading of local files .owl/.ttl, CSVs, business documents)
- Diagnosing the status of a domain's semantic layer
- Managing business terms in the governance dictionary
- Creating data collections (technical domains) from data dictionary searches
- Read-only data validation: sample-query validation of mapping SQL before publishing, and sanity checks of the published `semantic_<domain>` with `query_data` / `generate_sql` / `execute_sql`

This agent runs read-only data queries (`query_data`, `generate_sql`, `execute_sql`) for validation and sanity checks. It does not run `profile_data`, does not generate files on disk, and does not analyze data — its main output is interaction with governance MCP tools + summaries in chat.

## Requirements

- Access to two Stratio MCP servers:
  - `stratio_gov` (governance): creation and management of semantic artifacts
  - `stratio_data` (exploration): domain and data dictionary queries
- Environment variables: `MCP_GOV_URL`, `MCP_GOV_API_KEY`, `MCP_SQL_URL`, `MCP_SQL_API_KEY`
- Preconfigured setup in `opencode.json` (OpenCode), preconfigured to read the URL and credentials from environment variables. The `mcps` file at the agent root lists the MCP names registered when deploying the `agents/v1` bundle to Stratio Cowork

### System and Python dependencies

This agent does not ship a `requirements.txt` of its own because its primary output is MCP interaction, not file generation. However, it declares the shared skills `docx-reader` and `pptx-reader` (in `imported-skills`) so that planning can ingest DOCX specifications and PPTX decks. Those skills require:

- Python: `python-docx`, `python-pptx`, `lxml`
- System: `pandoc` (DOCX extraction, including tracked changes), `libreoffice-*-nogui` (legacy `.doc`/`.ppt` conversion and preview rasterization), `poppler-utils` (rasterization)

In the Stratio Cowork sandbox (`genai-agents-sandbox`) these dependencies are provided by the image. For local/out-of-sandbox installs, see the sandbox `development/DOCKER_DEPENDENCIES.md` or each skill's README.

## Packaging scripts

All scripts are non-interactive (CI/CD-friendly). If `--name` is not provided, they default to `semantic-layer`. All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish). When `--lang` is used, output goes to `dist/<lang>/...` instead of `dist/...`.

| Script | Target | Output | Example |
|--------|--------|--------|---------|
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent semantic-layer` |
| `pack_stratio_cowork.sh` | Stratio Cowork (`agents/v1`) | `dist/<name>-stratio-cowork.zip` | `bash ../pack_stratio_cowork.sh --agent semantic-layer` |

## Compatibility

- **OpenCode**: Package with `pack_opencode.sh` for use with OpenCode.
- **Stratio Cowork**: Package with `pack_stratio_cowork.sh` and deploy via the `cowork-api` shared skill (or as part of the `stratio-governance` plugin).

## Available skills

| Skill | Command | Description |
|-------|---------|-------------|
| Full pipeline | `/build-semantic-layer` | 5-phase pipeline to build the semantic layer of a domain |
| Semantic MCP reference | `/stratio-semantic-layer` | Governance MCP tools reference: rules, patterns, and best practices |
| Technical terms | `/create-technical-terms` | Create technical descriptions of tables and columns |
| Ontology | `/create-ontology` | Create, extend, or delete ontology classes with interactive planning |
| Business views | `/create-business-views` | Create, regenerate, or delete business views from an ontology |
| SQL Mappings | `/create-sql-mappings` | Create or update SQL mappings for existing views |
| Semantic terms | `/create-semantic-terms` | Generate business semantic terms for the views of a domain |
| Business Terms | `/manage-business-terms` | Create Business Terms with relationships to data assets |
| Data collection | `/create-data-collection` | Search tables in the dictionary and create a new data collection |

All skills live in `skills/` at the monorepo root and are shared with the data-governance-officer agent.

**Note**: This agent does not generate files on disk — the main output is interaction with MCP tools + summaries in chat.
