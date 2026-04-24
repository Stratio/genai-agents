# Skill Creator Agent

Expert agent for designing and generating AI agent skills — the `SKILL.md` files that extend an AI agent's capabilities, with supporting scripts, guides and references when the skill needs them.

## What this agent does

Skill Creator guides you through the full lifecycle of creating a skill: from understanding what you need, to designing the structure, writing the content, reviewing quality against a 14-point checklist, and packaging everything as a downloadable ZIP. It follows proven skill design principles to ensure your skills are effective, well-structured, and portable across platforms.

The workflow is **iterative and human-in-the-loop**: you confirm each milestone (requirements, design, generated content, review) before moving on. You can also enter at any phase — for example, paste an existing `SKILL.md` and ask for a review, or hand over a folder of files and jump straight to packaging.

## How it works

1. **Triage** — Understand whether you're designing a new skill, reviewing an existing one, improving a description, or packaging existing files.
2. **Requirements gathering** — Structured interview to capture what the skill does, when it triggers, inputs/outputs, and any supporting files it needs.
3. **Design** — Shape the frontmatter (name, description, triggers), the body structure, and the supporting-file layout. Presented for your approval.
4. **Generation** — Writes `SKILL.md` plus any supporting scripts, references or guides into `output/<skill-name>/`.
5. **Review** — Runs the 14-point quality checklist and walks you through the findings. Ask for changes and the agent loops back.
6. **Packaging** — Produces a ZIP of the skill folder, ready to drop into an agent or share.

You can enter at any phase. "Review this SKILL.md" jumps to Phase 5. "Package these files" jumps to Phase 6. "Improve the description of my skill" focuses on Phase 3 for that single field.

## Output structure

Skills are generated under `output/<skill-name>/` with a predictable layout — small skills are a single `SKILL.md`, larger ones include supporting folders:

```
output/<skill-name>/
├── SKILL.md                    # The entry point with frontmatter and body
├── scripts/                    # (Optional) helper scripts invoked by the skill
├── references/                 # (Optional) reference documents or data the skill reads
└── assets/                     # (Optional) images, templates, fixtures
```

## Capabilities

- Design skills from scratch through guided interviews
- Generate `SKILL.md` files with proper frontmatter and structured content
- Create supporting files (guides, scripts, references, assets) for complex skills
- Review existing skills against a 14-point quality checklist
- Improve skill descriptions for better triggering accuracy
- Package skills as ZIP files ready for deployment

## What you can ask

### Create skills
- "Create a skill for reviewing pull requests"
- "I need a skill that generates API documentation from code"
- "Design a skill for database migration workflows"

### Work with existing content
- "Review this skill and suggest improvements" (paste your `SKILL.md`)
- "Improve the description of my deploy skill"
- "Package my skill files as a ZIP"

### Learn about skill design
- "How should I write a good skill description?"
- "When should a skill have supporting files vs inline content?"
- "What makes a skill trigger reliably?"

## Available skills

| Command | Description |
|---------|-------------|
| `/skill-creator` | Complete reference for skill creation: anatomy, frontmatter, writing patterns, 14-point quality checklist |

## Getting started

Start the agent and describe what skill you need: "Create a skill for [your use case]". The agent will guide you through the process step by step and wait for your approval at every milestone.
