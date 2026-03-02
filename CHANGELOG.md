# Changelog

## 0.1.0 (upcoming)

* Initial version: monorepo with data-analytics and data-analytics-light agents
* Unify packaging artifacts under dist/, add CLI args to pack scripts, make MCP config optional in plugin scripts, add CI/CD scaffolding (Jenkinsfile, Makefile, bin/)
* Document build output structure in README, update pack script output paths in table
* Add skills normalization (flat .md → canonical format), output-templates support, sources zip generation and improve agent docs
* Remove interactive prompts from data-analytics-light pack scripts to make them fully CI/CD-friendly
* Add pack_claude_cowork.sh, --with-agent and --shared-guides flags for pack_claude_plugin.sh, instructions ZIP artifact and update packaging docs
* Add interactive dashboard builder for data-analytics: DashboardBuilder tool with filters, KPI cards, Plotly charts, sortable tables, multi-column grid layout, formatValue JS helper, embedded JSON data and 47 unit tests
* Remove pack_claude_instructions.sh from data-analytics-light: marginal use case, near-total overlap with Project pack, fragile maintenance and char limit risk in claude.ai Custom Instructions
* Migrate to AGENTS.md as canonical instructions format and skills/ as canonical skills directory; add symlink CLAUDE.md → AGENTS.md at monorepo root for Claude Code compatibility; update all pack scripts and skill cross-references
* Remove redundant error handling section from data-analytics agent (section 13 duplicated sections 4/5); move matplotlib backend tip to visualization.md
