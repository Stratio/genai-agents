# plugins — genai-agents Plugin Marketplace

Source definitions for the Claude Code plugin marketplace. Skills are packed dynamically from `shared-skills/` via `setup-plugins.sh`.

## Plugins

| Plugin | Description |
|--------|-------------|
| `genai-generic-skills` | Generic document processing and creative output (PDF, DOCX, PPTX, XLSX, web, canvas) |
| `genai-stratio-skills` | Stratio platform skills (data exploration, semantic layer, governance, data quality) |

## Usage

```bash
# Build the marketplace ZIP
bash setup-plugins.sh

# Register and install (from repo root)
claude plugin marketplace add ./dist/plugins.zip
/plugin install genai-generic-skills@genai-agents-plugins
/plugin install genai-stratio-skills@genai-agents-plugins
/reload-plugins
```

Single plugin: `bash setup-plugins.sh --plugin genai-generic-skills`  
With language overlay: `bash setup-plugins.sh --lang es`

## Structure

```
plugins/
  README.md                              # this file
  .claude-plugin/
    marketplace.json                     # marketplace manifest
  genai-generic-skills/
    .claude-plugin/
      plugin.json                        # metadata + skills list
  genai-stratio-skills/
    .claude-plugin/
      plugin.json                        # metadata + skills list
```

Skill content is resolved at pack time from `shared-skills/` — no duplication in source.
