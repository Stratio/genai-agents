# Task: SQL chain activity

Answer questions about the "talk to your data" SQL chain from traces: invocations, errors, latency, calls to platform services, and turn content for evaluation.

Needs `{PROXY}` (see `tasks/connect.md`) and a window:

```bash
NOW=$(date +%s); START=$((NOW - 86400))
```

Chains run as their own traced services. The SQL chain aggregates under `resource.service.name = "genai-chain-sql"` regardless of how many deployments exist; each deployment is distinguished by `resource.service.instance.id` (the chain deployment id). Before anything else, confirm the signal exists in the window (`tasks/discover-schema.md`, primitive 1) — a missing service means the chain was idle or its tracing is off, not that the recipes are wrong.

## Recipes

### 1. Chain invocations (the chain's evaluation turns)

One `invoke_workflow` span per chain invocation — the chain-side equivalent of Cowork's `invoke_agent`:

```bash
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode 'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" } | select(span.gen_ai.workflow.name, span.gen_ai.conversation.id, span.stratio.genai.chat.id)' \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
  --data-urlencode "limit=100" --data-urlencode "spss=5"
```

- `gen_ai.conversation.id` = the chat id — **present only when the invocation belongs to a conversation**; the platform never fabricates a fallback id, so standalone invocations legitimately lack it.
- Restrict to one deployment with `&& resource.service.instance.id = "<chain deployment id>"`.

### 2. One conversation end to end

The chat id lives in two attribute families: `stratio.genai.chat.id` (frontend and chain spans) and `gen_ai.conversation.id` (GenAI operation spans). Query both to get the whole path:

```bash
CHAT="<chat_id>"
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode "q={ span.stratio.genai.chat.id = \"${CHAT}\" || span.gen_ai.conversation.id = \"${CHAT}\" }" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" --data-urlencode "limit=100"
```

The GenAI-side subset alone: `{ span.gen_ai.conversation.id = "<chat_id>" }`. The backend hub's spans in these traces carry no chat id — only dashed user/tenant/request attributes (see the dots-vs-dashes note in `references/vocabulary.md`) — so per-user filters on hub spans need the dashed grafia.

### 3. Errors and latency

```bash
# failed invocations
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" && status = error }'
# slow invocations
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" && duration > 10s }'
```

Drill into a matching trace (`{PROXY}/api/traces/<traceID>`) to locate *where* the time went or the error rose: the platform-service child spans are named `<service>.<operation>` (`governance.get_glossary_items`, `virtualizer.run_sql_command`, `opensearch.search_filter_values`, ...) with `peer.service` set, plus httpx client spans toward the LLM gateway.

### 4. Chain invocations via MCP re-entry

When the chain is used as an MCP tool (by an agent) instead of via chat, the tool execution is the parent of the workflow:

```bash
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "execute_tool" } | select(span.gen_ai.tool.name)'
```

### 5. Turn content for evaluation

Same mechanism as Cowork turns — content lives on the `invoke_workflow` span when evaluation-content capture is on in the chain deployment:

```bash
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" && span.gen_ai.conversation.id = "<chat_id>" } | select(span.gen_ai.input.messages, span.gen_ai.output.messages)'
```

Missing content attributes ⇒ capture is off in that deployment (knobs table in `references/vocabulary.md`); report the skeleton and say so.

## Caveats

- **Deployment-dependent signal.** Chain tracing has its own gate in each chain deployment; node-level LangChain/LangGraph spans and background-refresh traces are additionally knob-gated and **off by default**. Their absence is expected, not a finding — check the knobs table before reporting a gap.
- **User identity lives on the server span** of the chain invocation (`stratio.genai.user.id` on `POST /invoke`-style spans), not on `invoke_workflow` itself; the backend hub's server spans in the same trace carry the dashed variants.
- **`query_result` rows are never captured** on spans, by design. SQL text can appear in captured content; data values should not — flag it if you see them.
- Traces with LangChain instrumentation enabled can exceed 300 spans; use `select()` projections instead of fetching such traces whole when you only need attributes.
