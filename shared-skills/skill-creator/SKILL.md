---
name: skill-creator
description: >-
  Comprehensive guide for creating high-quality AI agent skills (SKILL.md files).
  Use when designing, drafting, reviewing, or improving skills.
  Covers anatomy, frontmatter, progressive disclosure, writing patterns,
  description optimization, supporting files, and quality checklist.
argument-hint: "[skill topic or name (optional)]"
---

# Skill: Skill Creator

Complete reference for designing and writing high-quality AI agent skills. This guide contains all the knowledge needed to create effective skills — it does not depend on external documentation or web access.

## 1. Skill Anatomy

A **skill** is a set of instructions packaged as Markdown files that extend an AI agent's capabilities. The entry point is always a file called `SKILL.md`.

### 1.1 Directory structure

```
<skill-name>/
  SKILL.md              # Required — main instructions
  guide.md              # Optional — supporting guide
  scripts/              # Optional — executable helpers (Python, bash)
    helper.py
  references/           # Optional — static reference docs (schemas, examples)
    schema.md
  assets/               # Optional — files used in output (templates, icons)
    template.html
```

### 1.2 Naming conventions

- Use **lowercase with hyphens**: `create-quality-rules`, `explore-data`
- Never use camelCase or PascalCase: ~~`CreateQualityRules`~~, ~~`exploreData`~~
- The name becomes the `/slash-command` to invoke the skill
- Maximum 64 characters; use only lowercase letters, numbers, and hyphens

### 1.3 Two types of skills

**Reference Content** — Adds knowledge the agent applies to its current work. Runs inline with the conversation context. Examples: coding conventions, API patterns, style guides, domain knowledge.

```yaml
---
name: api-conventions
description: REST API design patterns for this codebase. Use when writing or reviewing API endpoints.
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats using the ErrorResponse schema
- Include request validation with Zod schemas
```

**Task Content** — Step-by-step instructions for specific actions. Often invoked manually by the user. Examples: deployments, commits, code generation workflows.

```yaml
---
name: deploy
description: Deploy the application to production. Use when the user wants to deploy or release.
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite: `npm test`
2. Build: `npm run build`
3. Push to deployment target: `npm run deploy`
```

### 1.4 Progressive disclosure

Skills load in three layers to optimize context usage:

| Layer | Content | When loaded | Token cost |
|-------|---------|-------------|------------|
| **Metadata** | `name` + `description` from frontmatter | Always in memory | ~100-200 tokens per skill |
| **Body** | Full SKILL.md content | Only when skill activates | Varies (aim for < 500 lines) |
| **Resources** | Supporting files (scripts, references, guides) | On demand, when referenced | Varies |

This system prevents overloading the context with unused skills. Write your skill knowing that its body is only loaded when relevant — keep the description good enough to trigger activation, and keep the body focused on execution.

## 2. YAML Frontmatter

Every SKILL.md starts with YAML frontmatter between `---` markers. The frontmatter tells the agent when and how to use the skill.

### 2.1 Essential fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier. Becomes the `/slash-command`. Lowercase, hyphens, max 64 chars |
| `description` | Yes (strongly recommended) | What the skill does and when to use it. This is the **primary triggering mechanism** |
| `argument-hint` | No | Placeholder shown in autocomplete: `[domain] [table (optional)]` |

### 2.2 Description — the most important field

The `description` determines when the agent loads your skill. Agents tend to **under-activate** skills, so descriptions should be proactive.

**Pattern**: action verb + what it does + "Use when..." + activation keywords

**Good description:**
```yaml
description: >-
  Assess the current data quality coverage for a domain, table, or column.
  Use when the user wants to understand quality status, identify gaps,
  find uncovered dimensions, or check which columns need quality rules.
```

**Bad description:**
```yaml
description: Quality assessment tool
```

The bad description is too vague — it will rarely trigger. The good description includes specific keywords ("gaps", "uncovered dimensions", "quality rules") that match what users actually say.

**Optimization rules:**
- Front-load the primary use case (first sentence)
- Include 3-5 keywords the user is likely to say
- Maximum ~250 characters recommended
- Always include a "Use when..." clause
- If the skill should NOT trigger in some cases, mention that: "Do NOT use for X"

For the complete field reference with all optional fields, examples, and invocation control, see `frontmatter-reference.md`.

## 3. Writing the Skill Body

### 3.1 Explain WHY, not just WHAT

Modern LLMs generalize well when they understand the reason behind an instruction. Instead of rigid directives, explain the motivation:

| Less effective | More effective |
|---------------|---------------|
| `ALWAYS validate the SQL` | `Validate the SQL before executing because a malformed query can silently return partial results, leading to incorrect analysis` |
| `NEVER use markdown tables` | `Format output as flowing prose paragraphs because the response will be read aloud by text-to-speech software, which cannot pronounce table structures` |
| `DO NOT skip profiling` | `Run profiling before analysis because without real data distribution knowledge, you may miss null patterns or outliers that invalidate statistical conclusions` |

This approach (sometimes called "theory of mind") is more effective than ALL-CAPS directives because the agent can apply the underlying principle to edge cases it hasn't seen.

### 3.2 Structure and formatting

- Use **numbered sections** for sequential workflows: `## 1. Discovery`, `## 2. Analysis`
- Use **tables** for decision routing:
  ```markdown
  | User intent | Action |
  |-------------|--------|
  | "Analyze domain X" | Full workflow (phases 1-5) |
  | "Just show me the tables" | Skip to phase 1 only |
  ```
- Use **imperative voice**: "Validate the input" (not "The input should be validated")
- Use **conditional blocks** for optional behavior: "If `output/MEMORY.md` exists, read it for context"

### 3.3 Instruction budget

Aim for **150-200 discrete instructions** in a skill. Beyond this threshold, LLM compliance tends to decrease. For each line, ask: "Would the agent make a mistake without this instruction?" If not, remove it.

### 3.4 Clarity and specificity

- Tell the agent what **to do**, not what to avoid. Instead of "Don't use markdown" → "Compose your response as flowing prose paragraphs"
- Define ambiguous terms explicitly. Never use "good", "professional", "reasonable" without specifying what that means in context
- Specify the desired output format explicitly (table, list, JSON, paragraph, code block)
- When showing expected output, provide a concrete example

### 3.5 Examples (few-shot)

Include 2-5 realistic examples when the expected behavior is not obvious:

- Examples should be **relevant** (reflect real use cases), **diverse** (cover edge cases), and **structured** (consistent format)
- Show input → expected output pairs
- Wrap examples in fenced blocks or use clear delimiters

### 3.6 Portability rule

Do not reference platform-specific file names like `AGENTS.md`, `CLAUDE.md`, or `opencode.json` directly. Packaging scripts rename these files depending on the target platform. Use generic phrases instead:

| Don't write | Write instead |
|------------|--------------|
| "As defined in AGENTS.md" | "As defined in the agent's instructions" |
| "Following the rules in CLAUDE.md" | "Following the agent's rules" |
| "Use the AskUserQuestion tool" | "Follow the user question convention" |

### 3.7 Target length

Keep SKILL.md **under 500 lines**. If approaching this limit, extract detailed sections to supporting files within the skill folder (see section 4).

## 4. Supporting Files

### 4.1 When to extract

Extract content to a separate file when:
- SKILL.md exceeds ~300 lines
- A section can be consulted independently (e.g., a field reference, a pattern catalog)
- Content is detailed reference material that isn't needed on every execution

### 4.2 File types

| Directory | Purpose | Example |
|-----------|---------|---------|
| Root of skill folder | Supporting guides loaded on demand | `advanced-guide.md`, `field-reference.md` |
| `scripts/` | Executable helpers the skill invokes | `scripts/validate.py`, `scripts/generate.sh` |
| `references/` | Static reference docs (schemas, specs) | `references/api-schema.json` |
| `assets/` | Files used in output generation | `assets/template.html`, `assets/logo.png` |

### 4.3 Referencing supporting files

Reference files from SKILL.md using relative paths:

```markdown
For the complete field reference, see `frontmatter-reference.md`.
For writing patterns and anti-patterns, see `writing-patterns.md`.
```

If a guide is shared across multiple skills, place it in `shared-skill-guides/` and declare it in a `skill-guides` manifest file inside the skill directory (one filename per line).

### 4.4 Dynamic context injection

Use `` !`command` `` syntax to run shell commands and inject the output before the agent sees the content:

```markdown
## Current environment
- Node version: !`node --version`
- Git branch: !`git branch --show-current`
```

For multi-line commands:
````markdown
```!
git log --oneline -5
npm test -- --reporter=json 2>/dev/null | jq '.numPassedTests'
```
````

### 4.5 Large reference files

For reference files over 300 lines, include a table of contents at the top so the agent can navigate directly to the relevant section.

## 5. Patterns and Anti-patterns

For the complete catalog of writing patterns with concrete code examples for each, see `writing-patterns.md`.

Key patterns summary:

- **Human-in-the-loop**: Present a complete plan → wait for explicit confirmation → execute. Never auto-execute destructive or irreversible actions
- **Structured output**: Define output format with a JSON schema example or template, not vague descriptions
- **Conditional behavior**: Check if resources exist before using them ("if MEMORY.md exists, read it")
- **Parallel operations**: Launch independent operations simultaneously ("launch all independent queries in parallel")
- **Proactive description**: Include activation keywords that match real user language
- **Self-contained skills**: All necessary knowledge embedded — never depend on unverifiable external knowledge

## 6. Quality Checklist

Run this checklist before finalizing any skill:

1. ✅ Frontmatter has `name` and `description`; description starts with action verb and includes "Use when..."
2. ✅ Body is under 500 lines; supporting files used for overflow
3. ✅ No direct references to `AGENTS.md` or `CLAUDE.md` — uses generic phrases
4. ✅ No dependencies on agent-specific tools, styles, or templates
5. ✅ Guide references use relative paths (`skills-guides/<file>` or direct filename)
6. ✅ Numbered sections for sequential workflows
7. ✅ Tables for decision routing
8. ✅ Each major step explains WHY, not just WHAT
9. ✅ Human-in-the-loop for destructive or irreversible actions
10. ✅ Instructions in imperative voice
11. ✅ At least one input/output example included
12. ✅ Name in kebab-case (lowercase, hyphens)
13. ✅ All necessary knowledge is embedded — skill does not depend on unverifiable external knowledge
14. ✅ Description is proactive enough to activate when relevant
