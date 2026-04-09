---
name: agent-designer
description: "Design the architecture of an AI agent for Stratio Cowork. Use when the user needs to plan an agent's workflow, triage table, skills, and file structure before generating files."
argument-hint: "[agent description or requirements]"
---

# Skill: Agent Architecture Designer

Reference for designing effective AI agents for the Stratio Cowork platform. Use this skill whenever designing a new agent or reviewing/improving an existing one.

## 1. Anatomy of a Stratio Cowork Agent

An agent for Stratio Cowork consists of these files:

| File | Purpose | Required |
|------|---------|----------|
| `AGENTS.md` | Agent instructions: identity, workflow, triage, skills, interaction rules | Yes |
| `README.md` | User-facing documentation: what the agent does, how to interact, examples | Yes |
| `opencode.json` | Platform configuration: instruction file reference, permissions | Yes |
| `.opencode/skills/{name}/SKILL.md` | Internal skills: detailed operational instructions for specific tasks | Optional |

### Skill types

Skills extend the agent's capabilities. There are three categories:

| Type | Where it lives | When to use |
|------|---------------|-------------|
| **Internal skill** | Inside the agent ZIP at `.opencode/skills/{name}/SKILL.md` | Specific to this agent — not reusable by others |
| **Shared skill (new)** | Separate ZIP alongside the agent | The user wants it available for other agents too |
| **Platform skill (existing)** | Already available on the platform | Referenced by name in AGENTS.md — the platform loads it at runtime |

Internal and shared skills are created using the `/skill-creator` skill. Platform skills are only referenced.

## 2. Writing an Effective AGENTS.md

The AGENTS.md is the most important file — it defines how the agent thinks and acts. Follow these principles:

### Structure

Every AGENTS.md must have these sections in order:

1. **Overview and Role** — Identity, capabilities, limitations, communication style
2. **Mandatory Workflow** — Triage table + numbered phases
3. **[Domain-specific sections]** — Rules, reference tables, tool docs (0 or more)
4. **User Interaction** — Question convention, language, progress, iteration

### Triage table design

The triage table is always Phase 0. It routes user intent to the right action.

**Design process:**
1. List all distinct things a user might ask the agent to do
2. For each, decide: can it be resolved with 1-2 direct actions (tool call, chat response), or does it need a multi-step workflow?
3. Direct actions → resolve inline. Multi-step workflows → load a skill or activate the full phase sequence

Use the Triage Pattern format from `agents-md-patterns.md`.

### Workflow phase design

Design phases from the user's workflow requirements (gathered in Phase 1 of the agent-creator):

1. Map each workflow scenario to a sequence of steps
2. Group related steps into phases (3-6 phases is typical)
3. For each phase, define:
   - **Entry condition**: what triggers this phase
   - **Steps**: numbered list of actions
   - **Exit condition**: what must be true before moving on
4. Identify phases that need human-in-the-loop (any phase that modifies external systems or creates artifacts)

### Human-in-the-loop implementation

For phases with side effects, use the Human-in-the-Loop Pattern from `agents-md-patterns.md`. Key rules:

- Present the complete plan BEFORE executing
- Wait for explicit confirmation (never proceed on ambiguous responses)
- Handle rejection, partial approval, and iteration
- Use `**CRITICAL**: NEVER [action] without explicit user confirmation` for the strongest constraints

### Skill activation

When the triage routes to a skill, use this exact pattern in the workflow:

```
Load `/skill-name` as the authoritative reference for [topic].
```

And in the triage section:

```
**Skill activation**: Load the corresponding skill BEFORE continuing with the workflow.
The skill contains the necessary operational detail.
```

### Guide references

If the agent uses external guide files inside skills, reference them with:

```
All rules for [topic] are in `skills-guides/[guide-name].md`. Follow ALL rules defined there.
```

### Instruction quality

Apply these rules to every instruction in the AGENTS.md:

- **Explain WHY**: "Validate the SQL before executing because a malformed query can silently return partial results" is better than just "Validate the SQL"
- **Imperative voice**: "Present the plan to the user" not "The plan should be presented"
- **Tables for decisions**: Use markdown tables for routing, not prose paragraphs
- **Positive framing**: "Do X" is better than "Don't do Y" (tell what TO do, not what to avoid)
- **Specific over vague**: "Query via `search_domains` MCP tool" is better than "Look up the information"

### Length guidelines

| Agent complexity | Target AGENTS.md length | Strategy |
|-----------------|------------------------|----------|
| Simple (1-2 skills, linear workflow) | < 150 lines | Everything inline |
| Medium (3-5 skills, branching workflow) | 150-300 lines | Extract operational detail to skills |
| Complex (6+ skills, multiple domains) | 300-500 lines | Extract aggressively; skills carry the detail |

If AGENTS.md exceeds 500 lines, split operational content into skills or guides.

## 3. Design Patterns

The complete catalog of proven patterns is in `agents-md-patterns.md`. The most important ones:

1. **Triage** — Route user intent before activating workflows (mandatory)
2. **Sequential phases** — Structure work as numbered stages with entry/exit conditions
3. **Skill activation** — Load operational detail on demand
4. **Human-in-the-loop** — Confirm before side effects
5. **Question convention** — Standardize user interaction with `{{TOOL_QUESTIONS}}`
6. **Language** — Always respond in the user's language

## 4. Template

The skeleton template for a new AGENTS.md is in `agents-md-template.md`. Use it as a starting point and customize based on the agent's design.

## 5. Quality Checklist

Run this checklist before finalizing any agent. Present results as ✅/❌ items:

**A. AGENTS.md quality:**

1. ✅ Has identity section with role, capabilities, limitations, and communication style
2. ✅ Has mandatory workflow with numbered phases
3. ✅ Phase 0 is a triage table routing user intent to actions or skills
4. ✅ Each phase has clear entry and exit conditions
5. ✅ Human-in-the-loop gates exist for actions with side effects
6. ✅ Skill activation rules use the pattern: "Load /skill-name BEFORE continuing"
7. ✅ User Interaction section defines: language, question convention (`{{TOOL_QUESTIONS}}`), progress reporting
8. ✅ Skills do not contain direct references to `AGENTS.md` or `CLAUDE.md` — use generic phrases
9. ✅ Uses imperative voice throughout
10. ✅ Uses tables for decision routing (not prose)
11. ✅ Key instructions explain WHY, not just WHAT
12. ✅ Appropriate length (< 300 lines for simple agents, extracted to skills if longer)
13. ✅ Includes language instruction: "ALWAYS respond in the same language the user uses"
14. ✅ Has at least one example of expected interaction or usage reference

**B. File structure quality:**

15. ✅ `opencode.json` is valid JSON with `"instructions": ["AGENTS.md"]`
16. ✅ `opencode.json` permissions match the agent's actual tool usage
17. ✅ `README.md` has all sections: what it does, capabilities, examples, skills table, getting started
18. ✅ All internal skills have valid YAML frontmatter with `name` and `description`
19. ✅ Skill descriptions start with action verb and include "Use when..." for activation
20. ✅ No orphan file references (all referenced files exist)
21. ✅ Skills are self-contained: no dependencies on unverifiable external knowledge

**C. Packaging quality:**

22. ✅ `metadata.yaml` has `format_version: "agents/v1"` and `name`
23. ✅ `metadata.yaml` `agent_zip` references the correct filename
24. ✅ Agent ZIP contains `AGENTS.md` at root
25. ✅ Agent ZIP contains `.opencode/skills/` with internal skills
26. ✅ If shared skills exist, `skills_zip` is declared and ZIP contains `{skill-name}/SKILL.md` for each
