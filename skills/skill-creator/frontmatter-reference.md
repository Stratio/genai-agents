# Frontmatter Reference

Reference for the YAML frontmatter fields recognized by **OpenCode** skills.

> **Scope note.** OpenCode's skill loader (verified in `packages/opencode/src/skill/index.ts:36-58` of the OpenCode source) only reads `name` and `description` from the frontmatter; any other top-level field is silently ignored at load time. Other runtimes (e.g. Claude Code) accept additional fields like `model`, `effort`, `context: fork`, `agent`, `paths`, `allowed-tools`, `shell`, `hooks`, `argument-hint`, `user-invocable` — those fields have **no effect** when the skill is packaged for OpenCode and are not documented here.

## Field Catalog

### name

- **Type**: string
- **Default**: derived from filename/folder
- **Description**: Unique identifier for the skill. Becomes the `/slash-command` users type to invoke it.
- **Rules**: lowercase letters, numbers, and hyphens only. Maximum 64 characters. Must match the parent directory name. Must not contain reserved words `anthropic` or `claude`.
- **Good**: `name: create-quality-rules`
- **Bad**: `name: CreateQualityRules` (no camelCase), `name: my awesome skill!` (no spaces or special chars)

### description

- **Type**: string
- **Default**: none
- **Description**: Explains what the skill does and when to use it. This is the **primary triggering mechanism** — the agent reads all skill descriptions to decide which to activate.
- **Rules**: Front-load the key use case. Include "Use when..." clause. Include keywords the user is likely to say. Maximum 1024 characters (only the first ~250 are shown in the slash-command UI listings).

**Good examples:**

```yaml
# Example 1: Quality assessment skill
description: "Assess the current data quality coverage for a domain, table, or column. Returns analysis of covered dimensions, missing gaps, and priority columns. Use when the user wants to understand quality status or identify gaps."

# Example 2: Data exploration skill
description: "Quick exploration of a governed data domain: list tables, show columns, preview sample data, and display basic statistics. Use when the user wants to browse or understand available data before analysis."

# Example 3: Code review skill
description: "Review code changes for bugs, security issues, and style violations. Use when the user submits a PR, asks for a code review, or wants feedback on their changes. Also triggers on \"check my code\" or \"review this\"."

# Example 4: Deployment skill
description: "Deploy the application to staging or production environments. Use when the user says deploy, release, push to prod, or ship it."

# Example 5: Semantic term generator
description: "Generate business semantic terms for published views in a governed domain. Use when the user wants to create or update semantic terms, or asks about the meaning of columns in business views."
```

**Bad examples:**

```yaml
# Too vague — will rarely trigger
description: "Quality tool"

# Too long and unfocused — buries the key use case
description: "This is a comprehensive tool that can be used for many purposes related to data quality including but not limited to assessment of coverage, identification of potential gaps in quality rules, analysis of dimensions, and more."

# Missing "Use when" — agent doesn't know when to activate
description: "Generates reports in PDF format"

# Overlaps with everything — will trigger too often
description: "Use this skill whenever the user asks anything about data."
```

## Description Optimization Exercises

### Exercise: Refining a weak description

**Step 1 — Start with the intent:**
```yaml
description: "Creates reports"
```

**Step 2 — Add specificity:**
```yaml
description: "Generate data quality coverage reports in PDF, DOCX, or Markdown format"
```

**Step 3 — Add "Use when..." trigger:**
```yaml
description: "Generate data quality coverage reports in PDF, DOCX, or Markdown. Use when the user wants a formal report of quality status."
```

**Step 4 — Add activation keywords:**
```yaml
description: "Generate data quality coverage reports in PDF, DOCX, or Markdown. Use when the user wants a formal report, coverage summary, quality document, or asks to export/download quality results."
```

This final version will trigger on: "generate a report", "I need a PDF of the quality status", "export the coverage results", "create a quality document".
