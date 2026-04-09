# Changelog

## 0.1.0 (upcoming)

* [ROCK-NA] bin/package.sh: replace hard-coded _pack_agent_extras calls with a dynamic loop over release-modules so new agents are picked up automatically
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
* Remove redundant directory conventions section from data-analytics agent (section 10 duplicated sections 2/5/8/9/12); relocate unique entries to section 8; renumber sections; saves ~650 tokens of context window
* Fix section numbering in data-analytics-light analyze skill: replace misleading alphabetic suffixes (4.5b/c/d, 5.4b/c) with sequential ordinal numbers (4.6–4.10, 5.5–5.8); update all cross-references in AGENTS.md
* Add new agent creation guide to README (structure, AGENTS.md, skills, opencode.json, packaging); add packaging files matrix table to data-analytics-light README; gitignore OpenCode workspace local files
* Add step 6 "Probar en OpenCode" to new agent guide: copy dist package to working dir, export MCP env vars, open OpenCode and edit opencode.json
* Add MCP clarification response protocol (cascade: domain search → infer from plan → ask user → reformulate → inform and continue; max 2 iterations per query) to both agents and exploration guide; add new agent integration checklist to monorepo AGENTS.md
* Expand new agent guide to cover Claude Code: add .mcp.json config section (4b), Claude Code pack command (step 5), and Claude Code test instructions (step 6b); update root and per-agent READMEs with platform compatibility and Requisitos sections
* Make shared skills self-contained: pack_claude_code.sh and pack_opencode.sh now embed skill guides inside each skill folder and rewrite local references; add pack_shared_skills.sh for standalone skill packaging; complete packaging docs with missing shared-skill zips and script tables
* Add TLS note to new agent guide: document NODE_TLS_REJECT_UNAUTHORIZED=0 workaround for MCP servers using self-signed certificates in development and pre-production environments
* Improve README intro: rewrite opening description to mention Stratio Semantic Data Layer, Stratio Governance (domains, semantic layers, data quality, business terms) and Stratio Virtualizer
* Clarify Cowork packaging docs: replace bullet list with table for the three generated artefacts, add note that plugins do not support CLAUDE.md (goes as folder instruction separately), fix incorrect AGENTS.md reference in usage steps
* Document stratio-data as standalone shared skill in README and CLAUDE.md; remove it from agent shared-skills manifests (agents consume stratio-data-tools.md guide directly)
* Add semantic-layer agent: specialized in building and maintaining semantic layers in Stratio Governance; includes 7 shared skills (stratio-semantic-layer, generate-technical-terms, create-ontology, create-business-views, create-sql-mappings, create-semantic-terms, manage-business-terms), the stratio-semantic-layer-tools guide, and full packaging support (Claude Code, OpenCode, Plugin, Cowork, Project)
* Add README for semantic-layer agent: capabilities, MCP requirements, packaging scripts (project/plugin/cowork + generic), files matrix per package type, and skills table
* Simplify Claude packaging: delete pack_claude_plugin.sh (logic absorbed into pack_claude_cowork.sh), rename pack_claude_project.sh → pack_claude_ai_project.sh with output dir claude_ai_projects/; remove plugin and plugin-agent artifacts from make package; update bin/package.sh, bin/clean.sh, bin/compile.sh and all documentation
* Remove redundant sources and global zip artifacts from make package: sources zip duplicated the repo, global zip was a zip-of-zips of the other artifacts
* [ROCK-NNNNN] Rename MCP servers to stratio_data/stratio_gov prefix across all agents; simplify tool allowlists to wildcards; add stratio_gov server to root .mcp.json; minor improvements to data-analytics tools
* [ROCK-NNNNN] semantic-layer: decouple create-data-collection from build-semantic-layer pipeline; add routing guidance to AGENTS.md; improve keyword search guidance and name/description flow in create-data-collection skill
* [ROCK-NNNNN] Add pack_stratio_cowork.sh script: document bundle format (agent + shared skills + mcps), update agent platform tables and README examples; exclude mcps file from pack_claude_code.sh and pack_opencode.sh with validation checks
* [ROCK-NNNNN] semantic-layer: add publish business views support — publish_business_views triage action, optional publication step in build-semantic-layer pipeline, refresh=true on domain discovery, increased MCP gov timeout to 600s, updated skill guides and create-business-views skill
* [ROCK-NNNNN] semantic-layer: fix opencode.json permission denials (replace *query_data with *profile_data and *propose_knowledge); clarify Pending Publish state description in build-semantic-layer, create-business-views and create-sql-mappings skills
* [ROCK-NNNNN] pack scripts: consolidate skills-guides/ to root level; fix broken references from CLAUDE.md/AGENTS.md and local skills; add Fase 8 integrity check for skills-guides references
* [ROCK-NNNNN] Migrate domain discovery tools: replace list_business_domains/list_technical_domains with unified list_domains (domain_type: both/business/technical) and search_domains; introduce search_ontologies alongside list_ontologies in semantic-layer; adopt search-first pattern across all agents and skills; open data-analytics to all domain types; remove list_technical_domains permission denials from opencode.json and pack_opencode.sh
* [ROCK-NA] Add USER_README.md support to all pack scripts (copied as README.md in output); add cowork-metadata.yaml injection in pack_stratio_cowork.sh; add USER_README.md and cowork-metadata.yaml for all agents
* [ROCK-NA] Internationalize monorepo: translate all primary files to English, add Spanish variants (.es.md/.es.yaml) for all agents and shared skills, add bin/check-translations.sh and bin/resolve-lang.sh, add languages file, update bin/package.sh to build multi-language artifacts
* [ROCK-14601] Add governance-officer agent combining semantic layer and data quality; promote data-quality and semantic-layer local skills to shared-skills; rename exploration.md to quality-exploration.md in shared-skill-guides
* [ROCK-NA] Document NODE_TLS_REJECT_UNAUTHORIZED setup for Claude Desktop and Claude Cowork on macOS and Windows (local and remote MCP servers)
* [ROCK-NA] Add skill-creator agent: interactive workflow for designing and generating AI agent skills (SKILL.md) with requirements gathering, design, generation, quality review and ZIP packaging; includes shared skill and full Spanish translation
* [ROCK-NA] Rename placeholder {{TOOL_PREGUNTAS}} to {{TOOL_QUESTIONS}} across all AGENTS.md files, pack scripts and READMEs for consistency with the English-primary i18n convention
* [ROCK-NA] Exclude cowork-metadata.yaml from pack_claude_code.sh and pack_opencode.sh output
* [ROCK-NA] Document MCP configuration for Claude Desktop and Cowork: clarify that claude_desktop_config.json requires mcp-remote proxy for remote HTTP servers and does not support ${VAR:-default} syntax; add packaging notes to agent READMEs
* [ROCK-NA] Add agent-creator agent: interactive workflow for designing and generating complete AI agents for Stratio Cowork with requirements gathering, architecture design (workflow phases, triage tables, skill decomposition), AGENTS.md generation following proven patterns, skill creation via shared skill-creator, 26-point quality review and agents/v1 ZIP packaging; includes two internal skills (agent-designer with pattern catalog and skeleton template, agent-packager) and full Spanish translation
* [ROCK-NNNNN] CI/CD: Update Jenkins builder Docker image to python-builder-3.12:1.3.0
