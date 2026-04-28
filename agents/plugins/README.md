# agents/plugins — genai-agents Plugin Marketplace

Local Claude Code plugin marketplace for the `genai-agents` monorepo.

## Plugins

| Plugin | Description |
|--------|-------------|
| [`genai-generic-skills`](./genai-generic-skills/README.md) | Generic document processing and creative output skills (PDF, DOCX, PPTX, XLSX, web, canvas) |
| [`genai-stratio-skills`](./genai-stratio-skills/README.md) | Stratio platform skills (data exploration, semantic layer, governance, data quality) |

## Installation

Run from the `genai-agents` repository root:

```bash
# Register the marketplace once (CLI)
claude plugin marketplace add ./agents/plugins
```
```
# Install each plugin (slash commands in a Claude Code session)
/plugin install genai-generic-skills@genai-agents-plugins
/plugin install genai-stratio-skills@genai-agents-plugins
/reload-plugins
```

## Structure

```
agents/plugins/
  .claude-plugin/
    marketplace.json              # Marketplace manifest
  genai-generic-skills/
    .claude-plugin/
      plugin.json                 # Plugin manifest (skills array points into shared-skills/)
    README.md
  genai-stratio-skills/
    .claude-plugin/
      plugin.json                 # Plugin manifest (skills array points into shared-skills/)
    README.md
```

Each `plugin.json` lists individual skill paths pointing directly into `shared-skills/` at the repo root — no duplication, single source of truth.
