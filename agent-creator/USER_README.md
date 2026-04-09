# Agent Creator

Expert agent for designing and generating complete AI agents for the Stratio Cowork platform — from requirements gathering to a deployable ZIP package.

## What this agent does

Agent Creator guides you through the full lifecycle of creating an agent: understanding what your agent should do, designing its workflow and skills, generating all instruction and configuration files, reviewing quality, and packaging everything as a Stratio Cowork-compatible ZIP bundle. It follows proven agent design patterns to ensure your agent is effective, well-structured, and ready for deployment.

## Capabilities

- Design agents from scratch through guided interviews
- Generate AGENTS.md with workflow phases, triage tables, and interaction rules
- Create internal skills for your agent using the skill-creator engine
- Create shared skills that can be reused by other agents
- Reference existing platform skills by name
- Generate README.md, opencode.json, and metadata.yaml
- Review agents against a 26-point quality checklist
- Package as Stratio Cowork agents/v1 ZIP bundle

## What you can ask

**Create agents:**
- "Create an agent for managing data quality assessments"
- "I need an agent that helps with code review workflows"
- "Design a customer support assistant agent"

**Work with existing content:**
- "Review this AGENTS.md and suggest improvements" (paste your content)
- "I have a partial agent, help me complete it"
- "Add a skill to my existing agent"

**Learn about agent design:**
- "What makes a good agent?"
- "How should I structure an agent's workflow?"
- "Package my agent files as a Stratio Cowork ZIP"

## Available skills

| Command | Description |
|---------|-------------|
| `/agent-designer` | Agent architecture design: workflow patterns, triage templates, AGENTS.md generation, quality checklist |
| `/agent-packager` | Stratio Cowork agents/v1 packaging: ZIP structure, metadata, validation |
| `/skill-creator` | Skill creation engine for building SKILL.md files (used for internal and shared skill generation) |

## Getting started

Start the agent and describe what agent you need: "Create an agent for [your use case]". The agent will guide you through the process step by step.
