# Task: discover the trace schema

List which services, span names, and attributes actually exist in the backend for a time window. Run this before assuming any attribute convention, and whenever a query unexpectedly returns nothing.

## Queries

All of them require `start`/`end` (Unix seconds). **Without a time range Tempo answers from recent blocks only and the result looks complete when it is not** — never trust an unranged tag query.

```bash
NOW=$(date +%s); START=$((NOW - 86400))   # adjust the window to the question
```

1. **Which services are emitting**:

   ```bash
   curl -sS -G "${PROXY}/api/v2/search/tag/resource.service.name/values" \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
   ```

2. **Which attributes exist** (per scope):

   ```bash
   curl -sS -G "${PROXY}/api/v2/search/tags" \
     --data-urlencode "scope=span" \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
   # scope=resource for resource attributes
   ```

3. **Values of one attribute**, optionally filtered by a TraceQL condition (`q`) — this is the cheapest aggregation primitive available, use it before writing search loops:

   ```bash
   curl -sS -G "${PROXY}/api/v2/search/tag/span.gen_ai.operation.name/values" \
     --data-urlencode 'q={ resource.service.name = "genai-litellm" }' \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
   ```

   The tag in the path is scoped (`resource.x` or `span.x`). The `q` filter restricts values to spans matching the condition.

4. **Sample spans with projected attributes** (to see real values side by side):

   ```bash
   curl -sS -G "${PROXY}/api/search" \
     --data-urlencode 'q={ resource.service.name = "<svc>" } | select(span.gen_ai.operation.name, name)' \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
     --data-urlencode "limit=20" --data-urlencode "spss=5"
   ```

## Interpretation

- **State the convention you found.** The platform mixes several: OTel GenAI semconv (`gen_ai.*`), platform attributes (`stratio.genai.*`), vendor attributes (`litellm.*`), plus HTTP semconv. `references/vocabulary.md` maps who emits what — trust the live schema over the map when they disagree.
- **Expect tag noise from the LLM gateway**: `genai-litellm` contributes hundreds of span tags of the form `llm.request.functions.<N>.*` and `gen_ai.tool.<N>.*` (one per tool slot per request). Ignore them for schema purposes.
- **An empty result has four candidate explanations** — check in this order before concluding "it did not run": (1) wrong window, (2) wrong attribute grafia (see the dots-vs-dashes note in the vocabulary), (3) a capture/signal knob is off in the observed deployment (knobs table in the vocabulary), (4) the code really never ran.
- Tag listings are data, not guarantees: a tag appears if at least one span in the window carries it — it says nothing about which service emitted it. Confirm ownership with a filtered values query (primitive 3) or a sampled search (primitive 4).
