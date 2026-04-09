# Frontmatter Reference

Complete reference for all YAML frontmatter fields available in SKILL.md files. Every field is optional except where noted, but `name` and `description` are strongly recommended.

## Field Catalog

### name

- **Type**: string
- **Default**: derived from filename/folder
- **Description**: Unique identifier for the skill. Becomes the `/slash-command` users type to invoke it.
- **Rules**: lowercase letters, numbers, and hyphens only. Maximum 64 characters.
- **Good**: `name: create-quality-rules`
- **Bad**: `name: CreateQualityRules` (no camelCase), `name: my awesome skill!` (no spaces or special chars)

### description

- **Type**: string
- **Default**: none
- **Description**: Explains what the skill does and when to use it. This is the **primary triggering mechanism** — the agent reads all skill descriptions to decide which to activate.
- **Rules**: Front-load the key use case. Include "Use when..." clause. Include keywords the user is likely to say. Maximum ~250 characters recommended.

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

### argument-hint

- **Type**: string
- **Default**: none
- **Description**: Placeholder text shown in autocomplete UI when the user starts typing the slash command.
- **Good**: `argument-hint: "[domain] [table (optional)]"`
- **Good**: `argument-hint: "[issue-number]"`
- **Bad**: `argument-hint: "enter your arguments here"` (too vague)

### user-invocable

- **Type**: boolean
- **Default**: `true`
- **Description**: When `false`, only the agent can invoke this skill. The skill does NOT appear in the slash command list. Its description IS loaded into context so the agent can decide when to use it.
- **When to use**: For background knowledge skills the agent should apply automatically: `legacy-system-context`, `coding-standards`.
- **Example**:
  ```yaml
  name: legacy-system-context
  description: Context about the legacy auth system. Use when working with auth-related code.
  user-invocable: false
  ```

### Invocation control summary

| Frontmatter | User invokes | Agent invokes | Description in context |
|-------------|:------------:|:-------------:|:---------------------:|
| Default (both true) | ✅ | ✅ | ✅ |
| `user-invocable: false` | ❌ | ✅ | ✅ |

### allowed-tools

- **Type**: string (space-separated tool names)
- **Default**: all tools available
- **Description**: Restricts which tools the agent can use while executing this skill. Tools listed here are granted without per-use approval.
- **When to use**: When a skill should only have access to specific tools for security or focus.
- **Example**:
  ```yaml
  allowed-tools: Read Grep Glob Bash(git *) Bash(npm *)
  ```
  This allows Read, Grep, Glob, and Bash only for `git` and `npm` commands.

### model

- **Type**: string (model ID)
- **Default**: inherits from session
- **Description**: Specifies which model to use when the skill is active. Overrides the session's model.
- **When to use**: When a skill requires a specific model's capabilities (e.g., a complex reasoning skill that needs the most capable model).
- **Example**: `model: claude-sonnet-4-6`

### effort

- **Type**: string (`low`, `medium`, `high`, `max`)
- **Default**: inherits from session
- **Description**: Sets the thinking effort level when the skill is active. Overrides the session level.
- **When to use**: Set `max` for complex reasoning skills; `low` for simple lookup/formatting skills.
- **Example**: `effort: max`

### context

- **Type**: string
- **Default**: runs inline
- **Description**: Set to `fork` to run the skill in an isolated subagent context. The skill content becomes the prompt driving the subagent. The subagent has its own context window and cannot see the parent conversation.
- **When to use**: For isolated, self-contained tasks that don't need conversation history: code exploration, file analysis, report generation.
- **Example**: `context: fork`

### agent

- **Type**: string
- **Default**: `general-purpose`
- **Description**: Specifies which subagent type to use when `context: fork` is set. Options: `Explore`, `Plan`, `general-purpose`, or a custom subagent defined in `.claude/agents/`.
- **When to use**: Combined with `context: fork` to specialize the subagent's behavior.
- **Example**:
  ```yaml
  context: fork
  agent: Explore
  ```

### paths

- **Type**: string (comma-separated glob patterns) or YAML list
- **Default**: activates everywhere
- **Description**: Limits when the skill activates based on the files being worked on. The skill only loads when the current task involves files matching these patterns.
- **When to use**: For skills specific to certain file types or directories.
- **Example**:
  ```yaml
  paths: src/**/*.ts, src/**/*.tsx
  ```
  or
  ```yaml
  paths:
    - src/**/*.ts
    - src/**/*.tsx
  ```

### shell

- **Type**: string (`bash` or `powershell`)
- **Default**: `bash`
- **Description**: Sets the shell used for inline commands (`` !`command` `` syntax) in the skill body.
- **When to use**: Only set to `powershell` if the skill targets Windows environments.

### hooks

- **Type**: object
- **Default**: none
- **Description**: Lifecycle hooks for automation. Allows running shell commands at specific points in the skill's execution.
- **When to use**: For skills that need setup/teardown or notification side effects.

## String Substitutions

These placeholders are replaced at runtime when the skill is invoked:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `$ARGUMENTS` | All arguments passed after the slash command | `/my-skill arg1 arg2` → `$ARGUMENTS` = `arg1 arg2` |
| `$ARGUMENTS[0]` or `$0` | First argument | `/my-skill domain_name` → `$0` = `domain_name` |
| `$ARGUMENTS[1]` or `$1` | Second argument | `/my-skill domain table` → `$1` = `table` |
| `${CLAUDE_SESSION_ID}` | Current session ID (useful for logging) | `session-abc123` |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the directory containing this SKILL.md | `/home/user/.claude/skills/my-skill` |

**Usage example:**

```markdown
---
name: assess-quality
argument-hint: "[domain] [table (optional)]"
---

## 1. Determine scope

Assess the quality of domain `$ARGUMENTS[0]`.
If a second argument was provided, focus on table `$ARGUMENTS[1]`.
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
