# Task: Cowork usage questions

Answer "who used what" questions about Stratio Cowork from traces: which agents were used, which users were active, how many sessions each user had, which projects/sandboxes ran.

All recipes need `{PROXY}` (see `tasks/connect.md`) and a time window:

```bash
NOW=$(date +%s); START=$((NOW - 86400))   # agree the window with the user first
```

## Recipes

### 1. Which Cowork agents have been used

Every agent turn is one `invoke_agent` span; `gen_ai.agent.name` carries the agent name:

```bash
curl -sS -G "${PROXY}/api/v2/search/tag/span.gen_ai.agent.name/values" \
  --data-urlencode 'q={ span.gen_ai.operation.name = "invoke_agent" }' \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

> **Honesty note — used vs deployed.** Traces show agents that *ran* in the window. The inventory of *deployed* agents lives in the platform's administration backend, not in Tempo. If the user asks "how many agents are deployed", answer the usage question and state this limitation explicitly.

### 2. Which users were active in Cowork

`stratio.genai.user.id` is stamped by the **web frontend** (RUM spans with `stratio.genai.app = "cowork"`), not by the agent runtime:

```bash
curl -sS -G "${PROXY}/api/v2/search/tag/span.stratio.genai.user.id/values" \
  --data-urlencode 'q={ span.stratio.genai.app = "cowork" }' \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

> Users reach the platform through their browser; a headless client that bypasses the web UI leaves no RUM spans and is invisible to this recipe. Say so if totals look suspiciously low.

### 3. Sessions of one user

The user↔session bridge is also the frontend: browser spans carry both `stratio.genai.user.id` and `stratio.genai.opencode.session.id` (agent-runtime spans do **not** carry the user id — see the caveat below):

```bash
USER_ID="<user>"
curl -sS -G "${PROXY}/api/v2/search/tag/span.stratio.genai.opencode.session.id/values" \
  --data-urlencode "q={ span.stratio.genai.user.id = \"${USER_ID}\" }" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

Count the values for "how many sessions"; feed each `ses_*` id to `tasks/cowork-session.md` for "what happened in them".

For **sessions per user across all users**, iterate recipe 3 over the users from recipe 2 (they are few) — one filtered tag-values call per user is cheaper and more reliable than downloading traces and aggregating client-side.

### 4. Which projects / sandboxes ran

Cowork runs one sandbox per project; its spans carry the project id:

```bash
curl -sS -G "${PROXY}/api/v2/search/tag/span.stratio.genai.project.id/values" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

The sandbox deployment identity is also visible as `resource.service.instance.id` values with prefix `genai-project-`.

### 5. Turn counts / activity rates

- Small windows (≤ 3 h): the TraceQL metrics endpoint can aggregate server-side:

  ```bash
  curl -sS -G "${PROXY}/api/metrics/query_range" \
    --data-urlencode 'q={ span.gen_ai.operation.name = "invoke_agent" } | rate() by (span.gen_ai.agent.name)' \
    --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
  ```

  The backend rejects ranges above its configured maximum (typically 3 h) — fall back to the next option when it does.

- Any window: search with projection and count client-side:

  ```bash
  curl -sS -G "${PROXY}/api/search" \
    --data-urlencode 'q={ span.gen_ai.operation.name = "invoke_agent" } | select(span.gen_ai.agent.name, span.gen_ai.conversation.id, span.stratio.genai.opencode.turn.origin)' \
    --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
    --data-urlencode "limit=200" --data-urlencode "spss=10" | jq '[.traces[]] | length'
  ```

  State the `limit` used; if the result hits it, the count is a lower bound — say so.

## Caveats

- **User↔turn cannot be joined inside one TraceQL query.** The browser trace (which knows the user) and the agent turn trace are *different traces*, stitched by span links — not by parent/child. The reliable bridge is the shared attributes (`stratio.genai.opencode.session.id`, `stratio.genai.message.id`) present on both sides, as in recipe 3.
- **Filter lazy turns when counting real user activity**: turns with `stratio.genai.opencode.turn.origin = "lazy"` are internal LLM housekeeping (title/summary/compaction), not user messages. Recipe 5's projection includes the attribute so you can split the counts.
- Tag-values responses are deduplicated sets — good for "which/how many distinct", useless for frequencies. Use recipe 5 for frequencies.
