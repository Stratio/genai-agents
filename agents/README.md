# Agents

This folder contains the generative AI agents of the monorepo. Each agent is a self-contained unit (`AGENTS.md` + `skills/` + tool configuration) that can be packaged and deployed to **OpenCode**, **Stratio Cowork** (`agents/v1` bundles), or any other host compatible with the `AGENTS.md` + `skills/` standard.

## Available agents

| Agent | What it does | Main outputs |
|---|---|---|
| [agent-creator](agent-creator/) | Designs and generates complete AI agents for Stratio Cowork through a guided workflow: requirements → architecture → AGENTS.md → skills → review → packaging. | New agent folders and `agents/v1` ZIPs. |
| [data-analytics-officer](data-analytics-officer/) | Full BI/BA agent. Queries governed data, runs Python analysis (pandas, scipy, scikit-learn), generates visualisations and multi-format reports (PDF, DOCX, PPTX, web, XLSX), documents reasoning. Read-only on data quality. | Analytical reports, dashboards, decks, workbooks. |
| [data-governance-officer](data-governance-officer/) | Combined governance agent: builds and maintains semantic layers AND manages data quality end-to-end. Unrestricted access to every governance and data MCP. | Semantic layers, quality rules, compliance reports, ontology documentation. |
| [data-quality](data-quality/) | Data quality specialist. Assesses coverage by domain / collection / table / column, proposes and creates rules (with mandatory human approval), schedules executions, and produces coverage reports in many formats. | Quality rules, schedules, coverage reports. |
| [semantic-layer](semantic-layer/) | Builds and maintains semantic layers in Stratio Governance: data collections, technical terms, ontologies, business views, SQL mappings, view publishing, semantic terms and business terms. | MCP interactions; no local files. |
| [skill-creator](skill-creator/) | Designs and generates skills (SKILL.md) for any AGENTS.md-based agent. Interactive: requirements → design → SKILL.md → review → ZIP. | New skill folders and packaged ZIPs. |

Each agent has its own `README.md` (developer-facing) and `USER_README.md` (end-user-facing) with the full description, MCP requirements, system dependencies and runtime notes.

## Anatomy of an agent

An agent is a self-contained folder with the agent's instructions, an optional set of local skills, and configuration for the runtime tools it talks to. An **MCP** (Model Context Protocol) server is the standard way these agents call external tools — Stratio Governance, Stratio Data, custom integrations — without baking the protocol details into the agent itself.

```
agents/<name>/
├── AGENTS.md              # Role, workflow, cross-cutting rules — required
├── README.md              # Developer-facing documentation
├── USER_README.md         # End-user-facing documentation
├── opencode.json          # OpenCode runtime config: MCP servers + permissions
├── mcps                   # Optional. Plain-text list of MCPs the Stratio Cowork bundle requires (one per line)
├── requirements.txt       # Optional. Python dependencies when the agent runs code
├── cowork-metadata.yaml   # Stratio Cowork metadata (display name, tags, …)
├── skills/                # Optional. Local skills specific to this agent
│   └── <skill-name>/SKILL.md
├── imported-skills        # Optional. Names of shared skills loaded from the monorepo (one per line)
├── guides                 # Optional. Names of root-level guides AGENTS.md references directly
└── templates/             # Optional. Static templates the agent ships
```

Required for any agent: `AGENTS.md` and either `opencode.json` or an equivalent host config. Everything else is optional and depends on what the agent does — a chat-only agent has no `requirements.txt`, a Cowork-only agent may skip OpenCode config.

Local skills live in `<agent>/skills/`. Shared skills come from the top-level [`skills/`](../skills/) folder via the `imported-skills` manifest — see [`skills/README.md`](../skills/README.md) for the catalogue and import workflow. When an agent has a local skill with the same name as a shared one, the local version wins.

For a concrete reference of scale, look at `data-analytics-officer/`: it ships several local skills, imports ~15 shared skills and declares two MCP servers. `semantic-layer/` is the lean opposite — no Python, no writer skills, output is just MCP interactions and chat replies.

## Packaging an agent

From the monorepo root:

```bash
# OpenCode bundle (developer testing, default English)
bash pack_opencode.sh --agent <name>

# OpenCode bundle in Spanish (resolves content from es/ overlay)
bash pack_opencode.sh --agent <name> --lang es

# Stratio Cowork agents/v1 bundle (agent + separate shared skills + mcps file)
bash pack_stratio_cowork.sh --agent <name>

# Everything for every language at once
make package
```

Outputs land in `agents/<name>/dist/` (intermediate) and `dist/` (final versioned ZIPs). The intermediate folders are gitignored.

## Adding a new agent

The detailed step-by-step tutorial — folder layout, `AGENTS.md` template, skill declaration, `opencode.json`/`mcps` configuration, packaging, OpenCode testing and Stratio Cowork deployment — lives in the repository root [`README.md`](../README.md#creating-a-new-agent), section *Creating a new agent*.

Roadmap of the work, in order:

1. **Folder.** `mkdir agents/<name>` with a kebab-case name (it becomes the bundle identifier).
2. **`AGENTS.md`.** Write the role, the mandatory workflow (numbered phases) and the cross-cutting rules. The more explicit, the more predictable runtime behaviour will be.
3. **Skills.** Local ones in `agents/<name>/skills/<skill>/SKILL.md`; shared ones in the plain-text `imported-skills` manifest (one per line). Root-level guides referenced from `AGENTS.md` go in a `guides` manifest.
4. **Runtime config.** `opencode.json` for the OpenCode runtime (instructions file, MCP servers, permissions — use `{env:VAR_NAME}` for secrets); `mcps` for the Stratio Cowork bundle (plain-text MCP names, one per line). `cowork-metadata.yaml` for the Cowork display name/tags. `USER_README.md` if the agent has end-user-facing instructions. `requirements.txt` if the agent runs Python code.
5. **Register for release.** Add `<name>` as a new line in the `release-modules` file at the monorepo root so `make package` includes it.
6. **Translate.** Create Spanish counterparts under `es/agents/<name>/` for `AGENTS.md`, `README.md`, `USER_README.md`, `cowork-metadata.yaml`, every sub-guide and every local skill. Run `bash bin/check-translations.sh` to verify completeness.
7. **Package and test.** `bash pack_opencode.sh --agent <name>` produces a runnable OpenCode bundle in `agents/<name>/dist/opencode/<name>/`; copy it to a working directory, export the MCP env vars (`opencode.json` resolves `{env:…}` placeholders at startup), and open it with `opencode`.
8. **Update the catalogue.** Add a row to the *Available agents* table above. If the agent will ship in a functional plugin, see [`plugins/README.md`](../plugins/README.md) to wire it in.

The repository root tutorial expands every step with templates, example snippets and the Cowork deploy flow.

## See also

- [`skills/README.md`](../skills/README.md) — shared skills catalogue and import workflow.
- [`guides/README.md`](../guides/README.md) — technical guides referenced from agents and skills.
- [`plugins/README.md`](../plugins/README.md) — functional plugins (verticals that bundle agents and/or skills).
- Repository root [`README.md`](../README.md) — system dependencies, packaging output structure, OpenCode runtime instructions.
