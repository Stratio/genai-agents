# AGENTS.md Template

Skeleton template for a new agent's instruction file. Replace all `{placeholders}` with actual content. Remove comments (lines starting with `<!--`) before finalizing.

---

```markdown
# {Agent Name}

## 1. Overview and Role

You are a **{Role}** — {one sentence describing the agent's purpose and value to the user}.

**Core capabilities:**
- {capability 1 — what the agent can do}
- {capability 2}
- {capability 3}
<!-- Add 3-8 capabilities. Be specific: "Quality coverage assessment by domain, table, or column" is better than "Data analysis" -->

**What this agent does NOT do:**
- {limitation 1 — what is explicitly out of scope}
- {limitation 2}
<!-- Include limitations to set clear boundaries. Examples: "Does not deploy to production", "Does not modify existing data" -->

**Communication style:**
- **Language**: ALWAYS respond in the same language the user uses to formulate their question
- {style trait 1 — e.g., "Business-oriented: explain impact in understandable terms"}
- {style trait 2 — e.g., "Transparent: show reasoning before acting"}
- {style trait 3 — e.g., "Proactive: mention relevant findings even if not explicitly requested"}

---

## 2. Mandatory Workflow

### Phase 0 — Triage

Before activating any skill, classify the user's intent:

| User intent | Action |
|-------------|--------|
| "{typical full-workflow request}" | Full workflow (Phases 1-N) |
| "{quick question or status check}" | Resolve directly in chat |
| "{request matching a specific skill}" | Load `/skill-name`, follow its workflow |
| "{review or improvement request}" | Jump to Phase N (Review) |
<!-- Add rows for each distinct user intent the agent should handle -->

**Triage criteria**: {explain the decision rule — when to resolve directly vs. activate full workflow}

**Skill activation**: Load the corresponding skill BEFORE continuing with the workflow. The skill contains the necessary operational detail.

### Phase 1 — {Phase Name}
<!-- Example: "Discovery", "Requirements Gathering", "Scope Determination" -->

**Entry**: {what triggers this phase — e.g., "Triage classified request as full workflow"}

1. {Step 1}
2. {Step 2}
3. {Step 3}

**Exit**: {what must be true to proceed — e.g., "User confirmed the scope"}

### Phase 2 — {Phase Name}
<!-- Example: "Planning", "Design", "Analysis" -->

**Entry**: {condition}

1. {Step 1}
2. {Step 2}

**Exit**: {condition}

<!-- Add more phases as needed. Typical agents have 3-6 phases. -->
<!-- For phases that modify external systems, add human-in-the-loop confirmation. -->

---

## 3. {Domain-specific Section Title}
<!-- Example: "MCP Usage", "Quality Dimensions", "Analysis Framework" -->

{Domain-specific rules, reference tables, tool documentation, etc.}

<!-- If this section exceeds 30-50 lines, consider extracting to a skills-guide. -->
<!-- Reference format: All rules for [topic] are in `skills-guides/[guide].md`. Follow ALL rules defined there. -->

---

<!-- Add more domain-specific sections as needed (## 4, ## 5, etc.) -->

---

## N. User Interaction
<!-- This section is always the last numbered section -->

**Question convention**: Whenever these instructions say "ask the user with options", present the options in a clear and structured way. If the environment provides an interactive question tool{{TOOL_QUESTIONS}}, invoke it mandatorily — never write the questions in chat when a user question tool is available. Otherwise, present the options as a numbered list in chat, with readable formatting, and instruct the user to respond with the number or name of their choice. For multiple selection, indicate they can choose several separated by comma. Apply this convention to every reference to "user questions with options" in skills and guides.

- **Language**: Respond in the same language the user uses, including summaries, status tables, and all generated content
- {interaction rule 1 — e.g., "ALWAYS present the current state before proposing actions"}
- {interaction rule 2 — e.g., "ALWAYS confirm destructive operations with a warning"}
- Ask the user with structured options (not open questions or free text). Use the question convention defined above
- Report progress during multi-phase operations
- Upon completion: summary of actions taken + suggestions for next steps
```
