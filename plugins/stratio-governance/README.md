# Stratio Governance plugin

Functional plugin that bundles the data governance agents of the monorepo into a single deployable unit for Stratio Cowork.

## What's inside

| Agent | Role |
|---|---|
| [data-governance-officer](../../agents/data-governance-officer/) | Full-spectrum governance: builds and maintains semantic layers AND manages data quality, plus PDF/DOCX/PPTX/XLSX/web/poster/markdown reporting. |
| [data-quality](../../agents/data-quality/) | Quality assessment, rule creation with mandatory human approval, scheduling and coverage reports in multiple formats. |
| [semantic-layer](../../agents/semantic-layer/) | Semantic layer construction: data collections, technical terms, ontologies, business views, SQL mappings and term publishing. |

## Supported platforms

| Platform | Supported | Why |
|---|---|---|
| Stratio Cowork | yes | Plugins with agents are deployable as `agents/v1` bundles. |
| Claude (claude-plugin) | no | Claude does not support agents in plugins; only skills-only plugins target Claude. |

## Installation

The plugin produces `dist/stratio-governance-stratio-cowork-{version}.zip`. To deploy it to a Stratio Cowork tenant, use the `upload-plugin` task of the [`cowork-api`](../../skills/cowork-api/) shared skill — it opens the bundle and dispatches each sub-ZIP to the right `genai-api` endpoint.

## Layout of the generated bundle

```
stratio-governance-stratio-cowork-{version}.zip
├── plugin.yaml                                  # aggregated manifest
├── README.md                                    # this file
└── agents/
    ├── data-governance-officer-stratio-cowork.zip    # agents/v1 sub-bundle
    ├── data-quality-stratio-cowork.zip          # agents/v1 sub-bundle
    └── semantic-layer-stratio-cowork.zip        # agents/v1 sub-bundle
```

Each sub-ZIP is a self-contained `agents/v1` container; if you prefer, you can extract the wrapper and upload sub-ZIPs individually with the `upload-agent` task.
