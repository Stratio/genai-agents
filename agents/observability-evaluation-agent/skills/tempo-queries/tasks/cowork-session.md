# Task: inspect / reconstruct a Cowork session

Given a session id (`ses_*`), answer "what happened in this session" and rebuild the conversation turn by turn — the input for black-box evaluations.

Needs `{PROXY}` (see `tasks/connect.md`), the session id, and a window that covers the session:

```bash
SES="ses_..."
NOW=$(date +%s); START=$((NOW - 86400))
```

## Recipes

### 1. Everything the session left behind (overview)

`stratio.genai.opencode.session.id` is stamped on **both** sides — browser RUM spans and agent-runtime spans — so one query lists the full activity:

```bash
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode "q={ span.stratio.genai.opencode.session.id = \"${SES}\" }" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
  --data-urlencode "limit=100"
```

Read the result as three families (by `rootServiceName` / `rootTraceName`):
- **Agent turns**: root `invoke_agent <agent>` on the sandbox service — the substance.
- **Send actions**: root `cowork.send-message` on the frontend service — one per prompt sent from the browser.
- **UI polling**: `GET .../session/:id/message`, `.../todo` on the frontend — noise for most questions; ignore unless asked about UI behavior.

### 2. Reconstruct the conversation (black-box eval input)

One query returns every turn **with its content**, no full-trace download needed:

```bash
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode "q={ span.gen_ai.operation.name = \"invoke_agent\" && span.gen_ai.conversation.id = \"${SES}\" } | select(span.gen_ai.input.messages, span.gen_ai.output.messages, span.stratio.genai.message.id, span.stratio.genai.opencode.turn.origin, span.stratio.genai.opencode.span.end_reason, span.stratio.genai.opencode.turn.tool_calls)" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
  --data-urlencode "limit=100" --data-urlencode "spss=10"
```

Assembly:
1. Collect the matched spans from every returned trace (one trace per turn) and **sort by `startTimeUnixNano`**.
2. `gen_ai.input.messages` / `gen_ai.output.messages` are JSON strings — arrays of `{role, parts[]}` (output adds `finish_reason`). Parse and render as User/Assistant turns.
3. Keep `stratio.genai.message.id` per turn: it is the correlation key with the browser's `cowork.send-message` span and with the platform's conversation store.

### 3. Drill into one turn (tools, LLM calls, cost)

Fetch the turn's full trace only when the question needs the execution tree:

```bash
curl -sS "${PROXY}/api/traces/<traceID>"
```

Inside, per span family:
- `chat <model>` — one per LLM call; `gen_ai.usage.input_tokens` / `output_tokens`, `stratio.genai.opencode.cost_usd`.
- `execute_tool <tool>` — one per tool call; `gen_ai.tool.name`, `stratio.genai.opencode.tool.title`, `stratio.genai.opencode.tool.output_bytes`.
- Gateway-side spans (`POST /chat/completions`, `chat <model>` on the LLM gateway service) mirror each LLM call with provider detail.

## Caveats (apply to every reconstruction)

- **Content only exists when capture is enabled** in the observed deployment. The `invoke_agent` spans always exist, but `gen_ai.input.messages` / `gen_ai.output.messages` appear only with the evaluation-content capture knob on (see the knobs table in `references/vocabulary.md`). If they are missing, report the skeleton (turn count, timing, tools) and say content capture is off — do not present that as "the conversation was empty".
- **Filter lazy turns**: `stratio.genai.opencode.turn.origin = "lazy"` marks internal title/summary/compaction turns. Only `user_message` turns belong in a conversation reconstruction.
- **Discard truncated turns for evaluation**: keep only `stratio.genai.opencode.span.end_reason = "completed"`; other values (`superseded`, `session_idle`, `session_error`, TTL/LRU sweeps) mean the span closed abnormally and its content may be partial.
- **Sub-agents leave no conversation of their own**: a `task` tool call shows title and output size, not the sub-agent's prompt or answer. Tool arguments/results in general appear only with the trajectory-capture knob on.
- **Browser↔turn are separate traces** stitched by span links (only user-message turns carry the link). Correlate by the shared attributes (`session.id` family, `stratio.genai.message.id`); link-following (`link:traceID`) exists in recent Tempo versions but is rarely needed.
- **Very long turns can hit the backend's per-attribute size limit** — a truncated `gen_ai.*.messages` value will fail to parse as JSON. Report the turn as truncated-at-ingest; the platform conversation store is then the only complete source.
- **Minimize exposure**: reconstructions contain user prompts and model output. Show them only as far as the question requires; redact when the user's question is about structure, not content.
