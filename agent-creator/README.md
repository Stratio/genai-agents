# agent-creator

Agent for designing and generating complete AI agents for the Stratio Cowork platform. Guides the user through an interactive workflow: requirements gathering, architecture design, AGENTS.md generation, skill creation, quality review, and agents/v1 ZIP packaging.

## Capabilities

- Interactive requirements gathering through structured interviews (3 rounds)
- Agent architecture design: workflow phases, triage tables, skill decomposition
- AGENTS.md generation following proven design patterns
- Skill creation for the agent (delegating to `/skill-creator`)
- Supporting file generation: README.md, opencode.json
- Quality review with a 26-point checklist
- Stratio Cowork `agents/v1` ZIP packaging

## Requirements

- No external dependencies (no Python, no MCPs)
- `zip` command for packaging (fallback to `tar` if unavailable)

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Agent Designer | `/agent-designer` | Agent architecture design: workflow patterns, triage templates, AGENTS.md generation, quality checklist |
| Agent Packager | `/agent-packager` | Stratio Cowork agents/v1 packaging: ZIP structure, metadata, validation |
| Skill Creator | `/skill-creator` | Complete guide for creating high-quality skills (shared skill from the monorepo) |

## Packaging scripts

### Generic scripts (from the monorepo root)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent agent-creator` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent agent-creator` |
| `pack_stratio_cowork.sh` | Stratio Cowork | `dist/<name>-stratio-cowork.zip` | `bash ../pack_stratio_cowork.sh --agent agent-creator` |

All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish).

## Quick start

```bash
# Package for Claude Code
bash ../pack_claude_code.sh --agent agent-creator

# Package for OpenCode
bash ../pack_opencode.sh --agent agent-creator

# Package for Stratio Cowork
bash ../pack_stratio_cowork.sh --agent agent-creator

# Package in Spanish
bash ../pack_claude_code.sh --agent agent-creator --lang es
```
