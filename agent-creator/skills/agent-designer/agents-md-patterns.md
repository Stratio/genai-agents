# AGENTS.md Design Patterns Catalog

Catalog of proven patterns for writing effective agent instructions. Each pattern includes: what it is, when to use it, the exact format, and a generic example.

---

## 1. Triage Pattern

**What**: A routing table that classifies the user's intent before activating any workflow or skill. It is always the first phase (Phase 0) and determines the execution path.

**When to use**: Every agent must have a triage phase. Without it, the agent applies the full workflow to every request — including trivial ones.

**Why it matters**: Not all requests require the full workflow. A simple factual question should not trigger a multi-phase process. Triage prevents this by separating direct-action requests from those that require loading a skill or activating a full workflow.

**Format** — Two-column (simple agents):

```markdown
| User intent | Action |
|-------------|--------|
| "..." | Resolve directly: [describe action] |
| "..." | Load `/skill-name`, then follow its workflow |
| "..." | Full workflow (Phases 1-N) |
```

**Format** — Three-column (agents with distinct skills and direct actions):

```markdown
| User intent | Direct action | Skill to load |
|-------------|---------------|---------------|
| "..." | — | `skill-name` |
| "..." | [describe tool call or chat response] | — |
```

**Triage criteria**: State the decision rule explicitly:

```markdown
**Triage criteria**: Can the request be answered with a direct action (1-2 tool calls)
without a multi-step workflow? → Resolve directly. Otherwise → Load the corresponding skill.
```

**Example**:

```markdown
| User intent | Direct action | Skill to load |
|-------------|---------------|---------------|
| "What is the status of X?" | Query via MCP, respond in chat | — |
| "Build a full X for domain Y" | — | `/build-x` |
| "Review this X" | — | Jump to Phase N (Review) |
```

---

## 2. Sequential Phases Pattern

**What**: Numbered phases that define the agent's workflow as a linear progression with clear entry/exit conditions.

**When to use**: When the agent's work involves distinct stages that must happen in order (e.g., discovery → planning → execution → validation).

**Why it matters**: Clear phases prevent the agent from skipping steps or mixing concerns. Each phase has a defined purpose and completion criteria.

**Format**:

```markdown
### Phase N — {Name}

**Entry**: {what triggers this phase — e.g., "User confirmed the design plan"}

1. {Step 1}
2. {Step 2}
3. ...

**Exit**: {what must be true before moving to the next phase — e.g., "All files generated and reported to user"}
```

**Example**:

```markdown
### Phase 1 — Discovery

**Entry**: Triage classified the request as requiring full workflow.

1. Identify the scope (domain, table, or column)
2. Run discovery queries to understand the current state
3. Present a summary of findings to the user

**Exit**: User has confirmed the scope and understands the current state.
```

---

## 3. Skill Activation Pattern

**What**: A conditional loading rule that tells the agent to load a specific skill before continuing with its workflow.

**When to use**: Whenever the agent delegates operational detail to a skill. The skill is loaded on-demand, not at agent startup.

**Why it matters**: Skills contain detailed operational instructions that would bloat the AGENTS.md if inlined. Conditional loading keeps the agent's instructions lean while ensuring the right detail is available when needed.

**Format**:

```markdown
**Skill activation**: Load the corresponding skill BEFORE continuing with the workflow.
The skill contains the necessary operational detail.
```

For specific triage entries:

```markdown
| "Build X for domain Y" | — | `/build-x` |
```

In the workflow text:

```markdown
Load `/skill-name` as the authoritative reference for [topic].
```

**Anti-pattern**: Never reference a skill without explicitly instructing to load it. Saying "see /skill-name for details" is not enough — the agent must be told to load it.

---

## 4. Human-in-the-Loop Pattern

**What**: A double-confirmation protocol for actions that have side effects, are destructive, or are irreversible.

**When to use**: Before any action that modifies external systems, creates artifacts, deletes data, or cannot be easily undone.

**Why it matters**: LLMs can misinterpret intent. Requiring explicit confirmation before executing ensures the user is aware of what will happen and agrees to it. This prevents costly mistakes.

**Format**:

```markdown
1. Design the action (plan what will be done)
2. Present the complete plan to the user, including:
   - What will be created/modified/deleted
   - Expected outcome
   - Any risks or side effects
3. **Wait for explicit confirmation**: words like "yes", "proceed", "ok", "go ahead",
   "approved", or equivalent in the user's language
4. Execute only after confirmation

- If the user rejects: adjust the plan and present again
- If the user partially approves: execute only the approved parts
- If the user asks for changes: incorporate feedback and re-present
```

**Critical rule format** (for actions that must NEVER skip confirmation):

```markdown
**CRITICAL**: `{tool_name}` is NEVER called without explicit user confirmation.
```

---

## 5. Depth Matrix Pattern

**What**: A capability activation table that adjusts behavior based on the user's chosen depth level.

**When to use**: When the same workflow can be executed at different levels of thoroughness (e.g., quick check vs. deep analysis).

**Why it matters**: Not all requests need the same level of detail. A depth matrix gives the user control over the trade-off between speed and thoroughness, and makes the agent's behavior predictable at each level.

**Format**:

```markdown
| Capability | Quick | Standard | Deep |
|-----------|-------|----------|------|
| Discovery | Basic | Full | Full + extended profiling |
| Hypotheses | Optional | Required | All + systematic testing |
| Validation | Skip | When relevant | Mandatory for all |
| Iterations | 0 | Max 1 | Max 2 |
```

**Usage**: Ask the user to choose a depth level at the start of the workflow:

```markdown
Ask the user with options: "What level of depth?"
1. **Quick** — Fast overview, minimal detail
2. **Standard** — Balanced analysis (recommended)
3. **Deep** — Thorough investigation with full validation
```

---

## 6. Guide Delegation Pattern

**What**: A reference to an external guide file that contains detailed operational rules, delegating the specifics to a separate document.

**When to use**: When a topic (e.g., MCP tool usage, data profiling rules) has detailed operational rules that would exceed 30-50 lines if inlined in AGENTS.md.

**Why it matters**: Keeps AGENTS.md focused on the workflow and decision-making. Operational details like tool parameters, error handling, and edge cases belong in guides that are loaded by the skill.

**Format**:

```markdown
All rules for [topic] (available tools, strict rules, [list key topics])
are in `skills-guides/[guide-name].md`. Follow ALL rules defined there.
```

**Important**: The path format `skills-guides/filename.md` is used in the source AGENTS.md. Pack scripts may rewrite this to a local path when embedding guides inside skills.

---

## 7. Question Convention Pattern

**What**: A standardized way of asking the user questions with structured options, using an interactive tool when available.

**When to use**: Every agent must include this convention in its User Interaction section. It is referenced by all phases and skills that need user input.

**Why it matters**: Consistent question formatting improves the user experience. The interactive tool (when available) provides a better UX than plain text options. The fallback ensures the agent works on all platforms.

**Format** (exact text — copy verbatim into the agent's User Interaction section):

```markdown
**Question convention**: Whenever these instructions say "ask the user with options",
present the options in a clear and structured way. If the environment provides an
interactive question tool{{TOOL_QUESTIONS}}, invoke it mandatorily — never write the
questions in chat when a user question tool is available. Otherwise, present the options
as a numbered list in chat, with readable formatting, and instruct the user to respond
with the number or name of their choice. For multiple selection, indicate they can choose
several separated by comma. Apply this convention to every reference to "user questions
with options" in skills and guides.
```

> `{{TOOL_QUESTIONS}}` is a placeholder automatically substituted by the platform at deployment time. Leave it as-is in the source AGENTS.md.

---

## 8. Critical Rules Pattern

**What**: NEVER/ALWAYS statements for hard constraints that must never be violated.

**When to use**: For rules that, if broken, would cause data loss, security issues, incorrect results, or bad user experience.

**Why it matters**: LLMs follow instructions better when constraints are stated as absolute rules with the reason behind them. The reason enables the model to apply the rule correctly in edge cases.

**Format**:

```markdown
**CRITICAL**: NEVER [action] without [condition] because [consequence if violated].
```

```markdown
**ALWAYS** [action] before [other action] because [reason].
```

**Example**:

```markdown
**CRITICAL**: NEVER execute a query without validating the SQL first,
because a malformed query can silently return partial results leading to incorrect analysis.

**ALWAYS** present the current state before proposing actions,
because the user needs context to make informed decisions.
```

---

## 9. Language Pattern

**What**: An explicit instruction to always respond in the user's language.

**When to use**: Every agent must include this. It is non-negotiable.

**Format** (exact text — place in the Communication style subsection of Overview and Role):

```markdown
**Language**: ALWAYS respond in the same language the user uses to formulate their question
```

Expanded version (for the User Interaction section):

```markdown
- **Language**: Respond in the same language the user uses, including summaries,
  status tables, and all generated content
```

---

## 10. Progress Reporting Pattern

**What**: Rules for keeping the user informed during multi-step operations.

**When to use**: When the agent's workflow involves operations that take multiple steps (e.g., creating multiple files, running several queries, processing a pipeline).

**Why it matters**: Without progress reporting, long operations feel like the agent is stuck. Reporting also helps the user catch problems early.

**Format**:

```markdown
- Report progress during multi-phase operations
- Upon completion: summary of actions taken + suggestions for next steps
```

**Example in a generation phase**:

```markdown
For each file generated:
1. Write the file
2. Report: file path, size, key highlights
3. Continue with the next file
```

---

## Pattern Combinations

Most effective agents combine several patterns. A typical agent uses:

1. **Triage** (always) → routes to the appropriate workflow
2. **Sequential phases** → structures the main workflow
3. **Skill activation** → loads operational detail on demand
4. **Human-in-the-loop** → protects destructive actions
5. **Question convention** → standardizes user interaction
6. **Language** → ensures multilingual support
7. **Progress reporting** → keeps the user informed

Optional additions:
- **Depth matrix** → when the same workflow can run at different thoroughness levels
- **Guide delegation** → when operational rules exceed 30-50 lines
- **Critical rules** → when hard constraints exist
