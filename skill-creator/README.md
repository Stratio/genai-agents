# skill-creator

Agent for designing and generating high-quality AI agent skills (SKILL.md files). Guides the user through an interactive workflow: requirements gathering, skill design, generation, quality review, and ZIP packaging.

## Capabilities

- Interactive requirements gathering through structured interviews
- SKILL.md generation following proven skill design principles
- Supporting file generation (guides, scripts, references)
- Skill quality review with a 14-point checklist
- Iterative improvement based on user feedback
- ZIP packaging of complete skill bundles

## Requirements

- No external dependencies (no Python, no MCPs)
- `zip` command for packaging (fallback to `tar` if unavailable)

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Skill Creator | `/skill-creator` | Complete guide for creating high-quality skills: anatomy, frontmatter, writing patterns, and quality checklist |

## Packaging scripts

### Generic scripts (from the monorepo root)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent skill-creator` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent skill-creator` |

All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish).

## Quick start

```bash
# Package for Claude Code
bash ../pack_claude_code.sh --agent skill-creator

# Package for OpenCode
bash ../pack_opencode.sh --agent skill-creator

# Package in Spanish
bash ../pack_claude_code.sh --agent skill-creator --lang es
```
