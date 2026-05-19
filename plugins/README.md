# Plugins

Functional plugins are top-down composition units. Each one bundles a curated set of agents and/or shared skills into a single deployable artifact that solves a vertical of business — data governance, document productivity, analytics, agent authoring, and so on.

Plugins are **additive**. The per-agent and per-skill ZIPs the monorepo already produces keep being built; a plugin simply references those artifacts by name and ships them together inside a wrapper ZIP.

## Available plugins

| Plugin | What it ships | Bundles | Platforms |
|---|---|---|---|
| [stratio-cowork-development](stratio-cowork-development/) | Guided workflow to build AI agents and skills interactively: requirements → architecture → code → review → packaging. | `agent-creator` + `skill-creator` (agents) | Stratio Cowork |
| [stratio-data](stratio-data/) | Senior BI/BA analyst that turns business questions into actionable analyses on governed data. | `data-analytics-officer` (agent) | Stratio Cowork |
| [stratio-data-toolkit](stratio-data-toolkit/) | Pluggable Stratio data skills (MCP query patterns, domain exploration, knowledge contributions, quality coverage assessment). Requires Stratio data and governance MCPs configured in the host agent. | `stratio-data`, `explore-data`, `propose-knowledge`, `assess-quality` (skills) | Claude |
| [stratio-governance](stratio-governance/) | Data governance vertical: semantic layers (ontologies, views, mappings, terms) and data quality (assessment, rule creation, scheduling, coverage reports). | `data-governance-officer` + `data-quality` + `semantic-layer` (agents) | Stratio Cowork |
| [stratio-productivity](stratio-productivity/) | Office-document and visual-output skills (read/write PDF, DOCX, PPTX, XLSX, web, canvas, brand kit). | `pdf-reader`, `pdf-writer`, `docx-reader`, `docx-writer`, `pptx-reader`, `pptx-writer`, `xlsx-reader`, `xlsx-writer`, `web-craft`, `canvas-craft`, `brand-kit` (skills) | Stratio Cowork, Claude |

Each plugin has its own `README.md` with the full description, deploy instructions and bundle layout.

## Anatomy of a plugin

```
plugins/<name>/
├── plugin.yaml    # Declarative manifest (required)
└── README.md      # User-facing documentation (required, English)
es/plugins/<name>/
└── README.md      # Spanish overlay of the README (plugin.yaml is not translated)
```

The manifest is a small YAML file:

```yaml
name: <plugin-name>            # kebab-case, must match the folder name
description: "..."             # ≤1024 chars
tags:                          # optional
  - <tag>
contents:
  agents:                      # optional list of agent folder names (under agents/)
    - <agent-name>
  skills:                      # optional list of shared skill names (under skills/)
    - <skill-name>
mcps:                          # optional, only allowed in skills-only plugins
  - <MCP_NAME>
platforms:                     # optional; defaults derived from contents
  - stratio-cowork
  - claude
```

At least one of `agents:` or `skills:` must be non-empty. Declaring `mcps:` together with `agents:` is rejected by the validator (MCPs are inferred from each agent's own `mcps` file).

## Platform rules

| Plugin contents | Stratio Cowork | Claude |
|---|---|---|
| Has agents | yes — wrapper bundle with one `agents/v1` sub-ZIP per agent | **no** — Claude does not support agents inside plugins |
| Skills-only | yes — wrapper bundle with one skills sub-ZIP compatible with `/v1/agents/skills/bundle/import` | yes — `.claude-plugin/plugin.json` marketplace bundle |

The validator (`bin/validate-plugins.py`) refuses to package a plugin that explicitly lists `claude` in `platforms:` while declaring `agents:`. If the effective set of platforms excludes the requested target, the build skips that platform silently.

## Output artifacts

`make package` produces one wrapper ZIP per `(plugin, platform, language)` combination in `dist/`:

```
dist/
├── plugin-stratio-governance-stratio-cowork-{version}.zip
├── plugin-stratio-governance-stratio-cowork-es-{version}.zip
├── plugin-stratio-data-stratio-cowork-{version}.zip
├── plugin-stratio-data-stratio-cowork-es-{version}.zip
├── plugin-stratio-cowork-development-stratio-cowork-{version}.zip
├── plugin-stratio-cowork-development-stratio-cowork-es-{version}.zip
├── plugin-stratio-productivity-stratio-cowork-{version}.zip
├── plugin-stratio-productivity-stratio-cowork-es-{version}.zip
├── plugin-stratio-productivity-claude-{version}.zip
├── plugin-stratio-productivity-claude-es-{version}.zip
├── plugin-stratio-data-toolkit-claude-{version}.zip
└── plugin-stratio-data-toolkit-claude-es-{version}.zip
```

A Stratio Cowork wrapper contains an **aggregated `plugin.yaml`** with a `bundles[]` catalogue — one entry per sub-bundle with its filename, kind (`agent` or `skill`) and SHA-256 — plus this plugin's `README.md` and the `agents/` and/or `skills/` sub-directories with the per-bundle ZIPs. The SHA-256s are validated by `cowork-api` at deploy time, so a tampered or out-of-sync wrapper is detected before any sub-bundle is dispatched. A Claude wrapper contains `.claude-plugin/plugin.json` (derived from `plugin.yaml`) and the resolved skill folders ready to be loaded by Claude Code.

## Packaging and validation

```bash
# Validate every plugin manifest (run on every save)
python3 bin/validate-plugins.py
python3 bin/validate-plugins.py --plugin <name>
python3 bin/validate-plugins.py --strict   # warnings count as errors

# Package one plugin for one platform
bash pack_plugin.sh --plugin <name> --platform stratio-cowork
bash pack_plugin.sh --plugin <name> --platform claude
bash pack_plugin.sh --plugin <name> --platform stratio-cowork --lang es
```

The validator emits two kinds of feedback:

- **Errors** — fatal. Examples: `name` does not match the folder, `description` longer than 1024 chars, both `agents:` and `skills:` empty, `mcps:` declared together with `agents:`, `claude` listed in `platforms:` with non-empty `agents:`, an `agents:` entry that does not exist as a top-level directory with an `AGENTS.md`, a `skills:` entry that does not exist as `skills/<name>/SKILL.md`.
- **Warnings** — non-fatal by default, escalated to errors with `--strict`. Example: an `mcps:` entry that does not appear in any `<agent>/mcps` file in the monorepo (likely a typo). Use `--strict` in CI so warnings cannot accumulate silently.

The full release pipeline (`make package`) runs the validator once per language and then iterates over every `(plugin, platform)` combination.

## Adding a new plugin

1. **Create the folder.** `mkdir plugins/<name>`. Pick a kebab-case name that matches the value of `name:` in the manifest.
2. **Write `plugin.yaml`.** Start from one of the existing plugins as a template:
   - Multi-agent vertical: `stratio-governance/plugin.yaml` (three agents) or `stratio-cowork-development/plugin.yaml` (two agents).
   - Single-agent vertical: `stratio-data/plugin.yaml`.
   - Skills-only for both platforms: `stratio-productivity/plugin.yaml`.
   - Skills-only for Claude only: `stratio-data-toolkit/plugin.yaml`.
3. **Write `README.md`.** Include: *What's inside* (table linking the agents/skills with one-line roles), *Supported platforms*, *Installation*, *Layout of the generated bundle*.
4. **Translate.** Create `es/plugins/<name>/README.md` (Spanish overlay of the user-facing README). `plugin.yaml` is **not** translated — it is a manifest, not a content file — and the top-level `plugins/README.md` of this folder is repo-only metadocumentation that stays English-only.
5. **Validate.** Run `python3 bin/validate-plugins.py --plugin <name>` until it returns OK.
6. **Package and verify.** Run `bash pack_plugin.sh --plugin <name> --platform stratio-cowork` (and `--platform claude` if applicable). Inspect the output ZIP — its layout should match the *Output artifacts* section above.
7. **Register.** Nothing extra to register. `make package` picks up every plugin folder automatically. Add the new entry to the catalogue above.

## Installing a plugin

- **Stratio Cowork.** Use the `upload-plugin` task of the [`cowork-api`](../skills/cowork-api/) shared skill from inside the Cowork sandbox. The task opens the wrapper, reads the aggregated manifest, recomputes the SHA-256 of every sub-bundle and compares it with the hash recorded in `plugin.yaml` before any deploy starts, then dispatches each sub-bundle to the matching `genai-api` endpoint (`/v1/agents/bundle/import` for agent bundles, `/v1/agents/skills/bundle/import` for skill bundles). It returns an aggregated report of imported, conflicted and failed artifacts. Atomicity is best-effort in this phase (no server-side rollback); the future `plugins/v1` API will improve this.
- **Claude.** Use the standard Claude Code plugin install flow (`/plugin install` from a marketplace).

## See also

- [`agents/README.md`](../agents/README.md) — agents that a plugin can bundle.
- [`skills/README.md`](../skills/README.md) — shared skills that a plugin can bundle.
- Repository root [`README.md`](../README.md) — packaging output structure and `make package` orchestration.
