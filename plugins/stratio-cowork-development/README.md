# Stratio Cowork Development plugin

AI agent development vertical for Stratio Cowork. Bundles the two builder agents that let users design and generate new agents and skills directly from inside the platform.

## What's inside

| Agent | Purpose |
|---|---|
| [agent-creator](../../agents/agent-creator/) | Designs and generates complete AI agents for Stratio Cowork. Interactive workflow: requirements gathering → architecture design (workflow phases, triage tables, skill decomposition) → AGENTS.md generation → skill creation → quality review (26-point checklist) → `agents/v1` ZIP packaging. |
| [skill-creator](../../agents/skill-creator/) | Designs and generates high-quality AI agent skills (SKILL.md files). Interactive workflow: requirements gathering → skill design following proven principles → SKILL.md generation with supporting files → quality review → ZIP packaging. |

Both agents import the `skill-creator` shared skill via their `imported-skills` manifest. The `cowork-api` shared skill (used by the agents to upload generated bundles to Cowork) is **not** packaged here — Cowork already provides it natively at runtime.

## Supported platforms

| Platform | Supported | Notes |
|---|---|---|
| Stratio Cowork | yes | Deployable as an `agents/v1` wrapper bundle. |
| Claude (claude-plugin) | **no** | Claude marketplace plugins do not support agents. |

## Installation

The plugin produces one artifact:

- `dist/stratio-cowork-development-stratio-cowork-{version}.zip` — Stratio Cowork wrapper bundle.

Use the `upload-plugin` task of the [`cowork-api`](../../skills/cowork-api/) shared skill to deploy it.
