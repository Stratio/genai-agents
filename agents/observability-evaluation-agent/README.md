# Observability & Evaluation Agent

Agent that answers end-user questions about the OpenTelemetry traces of the Stratio GenAI platform, querying Grafana Tempo through the Grafana datasource proxy. Read-only: `GET` requests only, traces as the only data source.

## Structure

```
observability-evaluation-agent/
├── AGENTS.md                          # Role, workflow, evidence rules
├── opencode.json                      # Permissions (no MCPs; granular bash allowlist)
├── cowork-metadata.yaml               # Bundle description + tags
├── USER_README.md                     # End-user README (becomes the bundle README.md)
└── skills/tempo-queries/              # Local skill: the query cookbook
    ├── SKILL.md                       # Router + shared query conventions
    ├── references/vocabulary.md       # Services / spans / attributes / knobs map
    └── tasks/
        ├── connect.md                 # Grafana proxy setup (once per session)
        ├── discover-schema.md         # Tags / tag-values primitives
        ├── cowork-usage.md            # Agents used, users, sessions per user
        ├── cowork-session.md          # Session inspection + conversation reconstruction
        └── sql-chain.md               # SQL chain invocations, errors, eval content
```

## Configuration

| Env var | Purpose |
|---|---|
| `GRAFANA_URL` | Grafana base URL (the agent asks the user and offers a default when unset) |
| `TEMPO_DATASOURCE_UID` | Tempo datasource UID (discovered via `/api/datasources` when unset) |

No MCPs and no Python dependencies — the recipes use `curl`, `jq` and `python3` from the sandbox image.

## Packaging

```bash
bash pack_opencode.sh --agent observability-evaluation-agent [--lang es]
bash pack_stratio_cowork.sh --agent observability-evaluation-agent [--lang es]
```

## Notes for maintainers

- The query recipes were validated live against a `grafana/otel-lgtm` deployment (Tempo 2.x, Grafana 13). Tempo API details that tend to drift: the datasource proxy route (`/api/datasources/proxy/uid/...` vs `.../resources/...`), the metrics endpoint range cap, and TraceQL `select()` support.
- `references/vocabulary.md` mirrors the platform's instrumentation conventions. When instrumentation changes (new attributes, the dots-vs-dashes migration completing, MCP semconv adoption), update it — the agent is instructed to trust the live schema over the map, but the map drives its first queries.
