# genai-stratio-skills

Claude Code plugin with agent skills for Stratio platform operations — data exploration, semantic layer construction, governance, data quality, and Cowork API integration.

## Installation

From the `genai-agents` workspace root:

```bash
# Register the marketplace once (CLI)
claude plugin marketplace add ./agents/plugins
```
```
# Install the plugin (slash command in a Claude Code session)
/plugin install genai-stratio-skills@genai-agents-plugins
/reload-plugins
```

## Skills

| Skill | Description |
|-------|-------------|
| `assess-quality` | Assess data quality coverage for a domain, table, or column |
| `build-semantic-layer` | Build the full semantic layer of a technical domain end-to-end in Stratio Governance |
| `cowork-api` | Capabilities of the Stratio Cowork management REST API (skill/agent registration) |
| `create-business-views` | Create, regenerate, delete or publish business views and SQL mappings in Stratio Governance |
| `create-data-collection` | Create a new data collection (technical domain) in Stratio Governance |
| `create-ontology` | Create, extend or delete ontology classes in Stratio Governance |
| `create-quality-rules` | Design and create data quality rules in Stratio Governance |
| `create-quality-schedule` | Create schedules for automated quality rule execution in Stratio Governance |
| `create-semantic-terms` | Generate or regenerate semantic terms for business views in Stratio Governance |
| `create-sql-mappings` | Create or update SQL mappings of existing business views in Stratio Governance |
| `create-technical-terms` | Create or regenerate technical terms (table/column descriptions) in Stratio Governance |
| `explore-data` | Quick exploration of data domains, tables, columns using governed data MCPs |
| `manage-business-terms` | Create and manage business terms in the Stratio Governance dictionary |
| `propose-knowledge` | Propose business terms and definitions discovered during analysis for Stratio Governance |
| `quality-report` | Generate formal data quality coverage reports in multiple formats |
| `stratio-data` | Reference for Stratio data MCPs — rules, usage patterns, best practices |
| `stratio-semantic-layer` | Reference for Stratio semantic layer MCPs — rules, usage patterns, best practices |

## Usage

Skills are invoked automatically when the agent recognises a matching task. You can also invoke them explicitly:

```
/genai-stratio-skills:explore-data
/genai-stratio-skills:build-semantic-layer
```

Skill content lives in `shared-skills/` at the repo root; `plugin.json` references them directly — no duplication.
