# Agent Creator

Expert agent for designing and generating complete AI agents for the Stratio Cowork platform — from requirements gathering to a deployable ZIP bundle, with everything in between reviewed and approved by you.

## What this agent does

Agent Creator guides you through the full lifecycle of creating an agent: understanding what your agent should do, designing its workflow and skills, generating all instruction and configuration files, reviewing quality against a 26-point checklist, and packaging everything as a Stratio Cowork-compatible `agents/v1` ZIP bundle. It follows proven agent design patterns to ensure your agent is effective, well-structured, and ready for deployment.

The workflow is **iterative and human-in-the-loop**: you confirm each milestone (requirements, architecture, AGENTS.md, per-skill design, assembled files, review) before moving on. If something needs to change mid-flow, the agent loops back to the relevant phase rather than pushing forward.

## How it works

1. **Triage** — Understand whether you're starting from scratch, completing a partial agent, reviewing existing content, adding a single skill, or going straight to packaging.
2. **Requirements gathering** — Guided interview (identity, workflows, behavior) to capture what the agent must do and how it should behave.
3. **Architecture design** — Workflow phases, triage table, skill map, interaction rules. Presented for your approval.
4. **AGENTS.md generation** — Writes the main instruction file following proven patterns.
5. **Skill creation** — For each skill, decides whether to reference an existing platform skill, create an internal skill (specific to this agent), or create a shared skill (reusable by other agents). Internal and shared skills are built by delegating to the skill-creator engine.
6. **Structure assembly** — Generates `README.md`, `opencode.json`, `metadata.yaml`, and an optional `mcps` manifest listing the MCP servers the agent needs at deploy time.
7. **Review** — Runs the 26-point quality checklist and walks you through the findings. You can ask for changes and the agent loops back.
8. **Packaging** — Creates the `agents/v1` bundle (see below) ready to upload to Stratio Cowork.

You can enter at any phase. "Review this AGENTS.md" jumps to Phase 7. "Package these files" jumps to Phase 8. "Add a skill to my agent" enters Phase 5 for that single skill.

## Skill types in your agent

When designing the architecture, each capability maps to one of three skill types:

| Type | Behavior |
|---|---|
| **Platform skill** | Already exists on the Stratio Cowork platform — the agent references it by name in `AGENTS.md` and does not ship code for it |
| **Internal skill** | Specific to this agent — created alongside the agent, packaged inside the agent ZIP under `.opencode/skills/` |
| **Shared skill** | Reusable across agents — created alongside the agent, packaged in a separate shared-skills ZIP that ships next to the agent bundle |

## Package structure (agents/v1)

The final deliverable is a container ZIP with a predictable layout:

```
{name}-stratio-cowork.zip               # Container bundle
├── metadata.yaml                       # agents/v1 format version and agent metadata
├── {name}-opencode-agent.zip           # Agent files (AGENTS.md, README.md, opencode.json, .opencode/skills/)
├── {name}-shared-skills.zip            # (Optional) new shared skills created for this agent
└── mcps                                # (Optional) MCP servers required at deploy time
```

## Capabilities

- Design agents from scratch through guided interviews
- Complete partial agents (you bring some pieces, the agent fills in the gaps)
- Review existing `AGENTS.md` against a 26-point quality checklist
- Generate `AGENTS.md` with workflow phases, triage tables and interaction rules
- Create internal skills for your agent using the skill-creator engine
- Create shared skills reusable by other agents
- Reference existing platform skills by name
- Generate `README.md`, `opencode.json`, `metadata.yaml` and optional `mcps` manifest
- Package as Stratio Cowork `agents/v1` ZIP bundle

## What you can ask

### Create agents
- "Create an agent for managing data quality assessments"
- "I need an agent that helps with code review workflows"
- "Design a customer support assistant agent"

### Work with existing content
- "Review this AGENTS.md and suggest improvements" (paste your content)
- "I have a partial agent, help me complete it"
- "Add a skill to my existing agent"
- "Improve the triage table of my agent"

### Packaging
- "Package my agent files as a Stratio Cowork ZIP"
- "My agent is ready — generate the agents/v1 bundle"

### Learn about agent design
- "What makes a good agent?"
- "How should I structure an agent's workflow?"
- "When should a capability be a skill vs inline in AGENTS.md?"

## Available skills

| Command | Description |
|---------|-------------|
| `/agent-designer` | Agent architecture design: workflow patterns, triage templates, AGENTS.md generation, 26-point quality checklist |
| `/agent-packager` | Stratio Cowork agents/v1 packaging: ZIP structure, `metadata.yaml`, optional `mcps` manifest, validation |
| `/skill-creator` | Skill creation engine for building `SKILL.md` files (used to generate the agent's internal and shared skills) |

## Getting started

Start the agent and describe what agent you need: "Create an agent for [your use case]". The agent will walk you through the process step by step and wait for your approval at every milestone.
