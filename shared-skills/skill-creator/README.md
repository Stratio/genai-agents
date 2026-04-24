# skill-creator

Complete reference for designing and writing high-quality agent skills (SKILL.md files). Covers anatomy, YAML frontmatter, progressive disclosure, writing patterns, supporting files and a 15-point quality checklist. Self-contained — no external docs or web access needed.

## What it does

- Teaches the anatomy of a skill: directory layout (`SKILL.md` + optional `scripts/`, `references/`, `assets/`), naming conventions (kebab-case), and the two skill types (Reference content vs. Task content).
- Specifies the **YAML frontmatter contract**: required `name` and `description` fields, optional `argument-hint`, formatting rules (always double-quoted on a single line) and description-optimisation patterns ("action verb + what + Use when... + keywords").
- Explains **progressive disclosure**: metadata always in memory, body loaded on activation, supporting files loaded on demand. Drives the "keep SKILL.md under 500 lines" rule.
- Provides writing guidance: explain *why* not just *what*, imperative voice, numbered sections for sequential workflows, decision-routing tables, input/output examples, instruction budget (aim 150–200 discrete instructions).
- Documents supporting-file strategy: when to extract to `scripts/` / `references/` / `assets/`, how to reference them, how to use dynamic context injection (`` !`command` ``).
- Catalogs patterns (human-in-the-loop, structured output, conditional behaviour, parallel operations, proactive description) and anti-patterns.
- Runs a **15-point quality checklist** before declaring a skill done (frontmatter well-formed, body under 500 lines, no platform-specific references, WHY-explained steps, destructive actions gated, kebab-case, proactive description…).

## When to use it

- The user wants to create a new skill, refactor an existing one, or review a skill written elsewhere.
- Before adding a skill to `shared-skills/` or an agent's `skills/` folder — the checklist catches most portability bugs (direct `AGENTS.md` references, platform-specific paths, vague descriptions).
- When improving a skill that is failing to activate (usually a description problem) or loading too much context (usually a body-length problem).

## Dependencies

### Other skills
None. This is a standalone reference skill.

### Guides
None (shared). The skill ships two supporting files inside its own folder:
- `writing-patterns.md` — catalog of reusable writing patterns with concrete code examples.
- `frontmatter-reference.md` — complete reference of YAML frontmatter fields with examples and invocation-control details.

### MCPs
None.

### Python
None — this is a prompt-only reference skill.

### System
None.

## Bundled assets

- `writing-patterns.md` (pattern catalog with code examples)
- `frontmatter-reference.md` (full YAML reference)

Both are consulted on demand from within `SKILL.md`.

## Notes

- **Portability rule:** never reference platform-specific file names (`AGENTS.md`, `CLAUDE.md`, `opencode.json`) directly in a SKILL.md. Use generic phrases like "the agent's instructions" or "follow the user question convention" — packaging scripts rename these files per platform.
- **Description quality determines activation.** Agents tend to *under*-activate skills; a vague description ("quality assessment tool") will rarely trigger. Follow the "action verb + Use when... + keywords" pattern and include 3–5 words the user actually says.
- **Instruction budget:** beyond ~200 discrete instructions, LLM compliance tends to drop. For each line ask "would the agent make a mistake without this?" and delete if not.
