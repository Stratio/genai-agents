---
name: tempo-queries
description: "Query Grafana Tempo for OpenTelemetry traces of the Stratio GenAI platform: connect through the Grafana datasource proxy, discover the trace schema, answer Cowork usage questions (agents used, active users, sessions per user), reconstruct a Cowork conversation turn by turn, and inspect SQL chain invocations. Use when the user asks anything that must be answered from platform traces — usage, session activity, conversation reconstruction, chain behavior, errors or latency."
---

# Skill: Grafana Tempo trace queries

Router skill. Each capability lives in its own file under `tasks/`. **This file is intentionally minimal** — when the agent needs to perform a specific task, it must load and follow the corresponding sub-file in full. Do not improvise queries from this index.

## Prerequisites — read first

- Connection: `tasks/connect.md` builds the `{PROXY}` base URL (once per session). Every other task assumes `{PROXY}` exists.
- Vocabulary: `references/vocabulary.md` is the map of services, span names, attributes, and the capture knobs that condition which signal exists. Consult it before interpreting results or writing new queries; verify against the live schema (`tasks/discover-schema.md`) when something does not match.

## Shared query conventions (apply to every task)

1. **Always pass a time range**: `start` and `end` in Unix seconds on every search, tag, and tag-values call. Without them Tempo silently answers from recent blocks only and results look complete when they are not. Compute with `date +%s` (e.g. `START=$(( $(date +%s) - 86400 ))` for the last 24 h).
2. **Always URL-encode the TraceQL query**: use `curl -sG ... --data-urlencode 'q={ ... }'` — braces, quotes, and spaces do not survive the proxy hop otherwise.
3. **Bound the volume**: set `limit` explicitly on searches (default is low); add `spss` (spans per span-set) when selecting spans. Say when an answer rests on a truncated result.
4. **Project, don't download**: prefer `| select(span.attr, ...)` in the search query to get attributes directly in the result; fetch full traces (`{PROXY}/api/traces/{traceID}`) only when the execution tree itself is needed.
5. **Read-only**: `GET` requests only, no credentials attached.

## Capability index

| Capability | When to use | Sub-file to load |
|---|---|---|
| Connect to the trace backend | First trace question of the session; `{PROXY}` not built yet. | `tasks/connect.md` |
| Discover the schema | Unknown attribute names or conventions; verify what signal exists in a window; something returns empty unexpectedly. | `tasks/discover-schema.md` |
| Cowork usage questions | Which agents were used, which users were active, sessions per user, projects/sandboxes that ran. | `tasks/cowork-usage.md` |
| Inspect / reconstruct a Cowork session | What happened in session X; rebuild the conversation turn by turn; extract black-box evaluation input. | `tasks/cowork-session.md` |
| SQL chain activity | Chain invocations, errors, latency, platform service calls, chain turn content for evaluation. | `tasks/sql-chain.md` |

## Routing rules

1. Identify the capability from the user's intent. If none matches, compose the primitives of `tasks/discover-schema.md` (tags → tag values → search → trace fetch) and say which convention you found.
2. Make sure `tasks/connect.md` has been completed once before any other task.
3. Load the matching sub-file and follow it end-to-end. Do not blend instructions across sub-files.
4. Interpret results with `references/vocabulary.md` at hand — especially the knobs table before concluding that something "did not happen".

## Adding a new capability

1. Create `tasks/<capability>.md` with: when to use, the exact queries (ready-to-run curl), how to interpret the result, and the caveats that apply.
2. Add an entry to the **Capability index** above.
3. Mirror both files under the `es/` overlay.
