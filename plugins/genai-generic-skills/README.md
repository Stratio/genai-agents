# genai-generic-skills

Claude Code plugin with generic agent skills for document processing and creative output.

## Installation

From the `genai-agents` workspace root:

```bash
# Register the marketplace once (CLI)
claude plugin marketplace add ./plugins
```
```
# Install the plugin (slash command in a Claude Code session)
/plugin install genai-generic-skills@genai-agents-plugins
/reload-plugins
```

## Skills

| Skill | Description |
|-------|-------------|
| `brand-kit` | Select and apply a visual identity theme consumed by all writer skills |
| `canvas-craft` | Create single-page visual artifacts — posters, covers, certificates, infographics |
| `docx-reader` | Inspect and extract content from Word documents (.docx / .doc) |
| `docx-writer` | Create and manipulate Word documents with intentional design |
| `pdf-reader` | Inspect and extract content from PDF files |
| `pdf-writer` | Create and manipulate PDF files with intentional design |
| `pptx-reader` | Inspect and extract content from PowerPoint (.pptx) files |
| `pptx-writer` | Create and manipulate PowerPoint decks with intentional design |
| `skill-creator` | Comprehensive guide for creating high-quality SKILL.md files |
| `web-craft` | Build production-grade interactive frontends (HTML/CSS/JS, React, Vue) |
| `xlsx-reader` | Inspect and extract content from Excel workbooks |
| `xlsx-writer` | Create and manipulate Excel workbooks with intentional structure |

## Usage

Skills are invoked automatically when the agent recognises a matching task. You can also invoke them explicitly:

```
/genai-generic-skills:pdf-writer
/genai-generic-skills:docx-writer
```

Skill content lives in `shared-skills/` at the repo root; `plugin.json` references them directly — no duplication.
