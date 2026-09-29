# Reference: trace vocabulary of the Stratio GenAI platform

Map of the services, span names, and attributes the platform emits. It reflects the instrumentation as of mid-2026 — **the live schema wins** when they disagree (`tasks/discover-schema.md`); treat every entry here as "expected", not "guaranteed".

## 1. Service identity (resource attributes)

All platform modules share `service.namespace = "stratio-genai"`. `service.name` is a stable logical role (not the deployment); `service.instance.id` identifies the logical deployment (not the pod).

| `service.name` | Component | `service.instance.id` shape |
|---|---|---|
| `genai-ui` | Web frontend (browser RUM) | `<service>.<namespace>` of the UI deployment |
| `genai-api` | Backend hub (control plane) | `<service>.<namespace>` |
| `genai-chain-sql`, `genai-chain-governance`, ... | Chain subprocesses, one name per chain *type* | the chain deployment id |
| `genai-litellm` | LLM/MCP gateway | `<service>.<namespace>` |
| `genai-agents-sandbox-opencode` | Cowork agent runtime (per-project sandbox) | `genai-project-<PROJECT_ID>:opencode` |
| `genai-agents-sandbox-nginx` / `-file-browser` / `-jwt-validator` | Sandbox side services | `genai-project-<PROJECT_ID>:<component>` |

Extra resource attributes:
- `stratio.genai.eval = "true"` — marks the **GenAI executors** (chains, gateway, sandbox agent runtime). Interface and control-plane services (`genai-ui`, `genai-api`, sandbox side services) do not carry it.
- Chain processes add `stratio.genai.chain.{id, service_id, class, module, package_id}` on every span they emit.
- Sandbox services add `stratio.genai.{user.id, project.id, project.name, agent.name, agent.version}` at resource level.

## 2. Span map (who emits what)

**Turn spans** — the evaluation-grade units; always emitted when tracing is on, their *content* is knob-gated:

| Span | Emitter | One per |
|---|---|---|
| `invoke_agent <agent>` (`gen_ai.operation.name = invoke_agent`) | sandbox agent runtime | Cowork agent turn (root of its own trace) |
| `invoke_workflow <chain>` (`gen_ai.operation.name = invoke_workflow`) | chain process | chain invocation |

**Trajectory spans** (children of a turn):

| Span | Emitter | Meaning |
|---|---|---|
| `chat <model>` | sandbox runtime and LLM gateway | one LLM call (each side emits its own) |
| `execute_tool <tool>` | sandbox runtime / chain MCP wrapper | one tool call |
| `<service>.<operation>` (e.g. `governance.get_glossary_items`, `virtualizer.run_sql_command`, `opensearch.search_filter_values`) | chain process | one platform-service call, `peer.service` set |
| LangChain/LangGraph node spans (OpenInference convention, `openinference.span.kind`) | chain process | **only when the LangChain knob is on** (off by default) |
| `POST /chat/completions`, `auth ...`, `postgres ...` | LLM gateway | request handling around each LLM call |
| HTTP client/server spans (`POST /invoke`, `POST /v1/chains/{chain_id}/stream`, ...) | all backend services | the skeleton that stitches services together |

**Frontend (browser) spans** — service `genai-ui`:

| Span | Meaning |
|---|---|
| `cowork.send-message` | one per prompt sent from the Cowork UI (root of the browser-side trace) |
| `METHOD /route/:id` | every XHR/fetch the UI makes (includes heavy session polling: `GET .../session/:id/message`, `.../todo`) |
| `documentLoad` | initial page load |

**Session grouping**: a Cowork conversation is *not* one trace. Each turn is its own trace; the browser send is another; they are stitched by span links and, more practically, by shared attributes: `gen_ai.conversation.id` (= root session id, on GenAI spans), `stratio.genai.opencode.session.id` (on browser *and* sandbox spans), `stratio.genai.message.id` (send↔turn).

## 3. Key span attributes

| Attribute | Where | Notes |
|---|---|---|
| `gen_ai.operation.name` | GenAI spans | `invoke_agent` \| `invoke_workflow` \| `chat` \| `execute_tool` |
| `gen_ai.conversation.id` | turn + trajectory spans | session id (Cowork) or chat id (chains). Never fabricated: absent when there is no conversation |
| `gen_ai.agent.name` | sandbox spans | Cowork agent name |
| `gen_ai.workflow.name` | `invoke_workflow` | chain logical name |
| `gen_ai.input.messages` / `gen_ai.output.messages` | turn spans | **capture-gated**. JSON strings: `[{role, parts[]}]`, output adds `finish_reason` |
| `gen_ai.usage.input_tokens` / `output_tokens` | `chat` spans | token usage |
| `gen_ai.tool.name` / `gen_ai.tool.call.id` | `execute_tool` | tool identity; arguments/results only with trajectory capture |
| `stratio.genai.user.id` | browser spans (span-level); sandbox (resource-level) | **not** on `invoke_agent` spans — bridge users↔sessions through browser spans |
| `stratio.genai.app` | browser spans | `cowork` \| `talk-to-your-data` \| `dashboards` \| `settings` |
| `stratio.genai.chat.id` | browser + chain spans | chat id (dots grafia) |
| `stratio.genai.opencode.session.id` / `.root_session.id` | browser + sandbox spans | the cross-side session key |
| `stratio.genai.message.id` | `cowork.send-message`, `invoke_agent`, `chat` | send↔turn correlation key |
| `stratio.genai.opencode.turn.origin` | `invoke_agent` | `user_message` \| `lazy` (internal title/summary/compaction turns) |
| `stratio.genai.opencode.turn.llm_calls` / `.turn.tool_calls` | `invoke_agent` | per-turn counters |
| `stratio.genai.opencode.span.end_reason` | sandbox spans | `completed` is the only trustworthy value for evaluation; others mean abnormal closure |
| `stratio.genai.opencode.cost_usd` | sandbox `chat` | per-call cost |
| `stratio.genai.opencode.tool.title` / `.tool.output_bytes` | `execute_tool` | tool metadata (never content) |
| `litellm.*` (`litellm.cost.total`, `litellm.call_id`, ...) | gateway `chat` spans | vendor attributes; verify names live before relying on them |

**Dots vs dashes (transitional):** the platform convention is dotted `stratio.genai.*`, but the backend hub (`genai-api`) still stamps dashed span attributes (`stratio-genai-user-id`, `stratio-genai-tenant`, `stratio-genai-request-id`, `stratio-genai-auth-type`). Cross-service queries on those dimensions need an OR over both grafias until the migration completes.

## 4. Knobs that condition which signal exists

Deployment-side environment switches. **Check this table before concluding "X did not happen"** — the two most common false negatives are content capture off and LangChain spans off.

| Knob (env of the observed deployment) | Default | Effect on what you can query |
|---|---|---|
| `OPENTELEMETRY_ENABLED` (per module) | off | master gate: no spans at all from that module |
| `STRATIO_GENAI_CAPTURE_EVAL_CONTENT` (or the global `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`) | off | `gen_ai.input/output.messages` on turn spans |
| `STRATIO_GENAI_CAPTURE_TRAJECTORY_CONTENT` | off | tool arguments/results, LangChain node content, gateway content capture |
| `STRATIO_GENAI_TRACE_LANGCHAIN` (chains) | off | LangChain/LangGraph node spans exist at all |
| `STRATIO_GENAI_TRACE_BACKGROUND_TASKS` (chains) | off | background refresh cycle traces (`governance metadata refresh`, ...) exist at all |
| `GENAI_OTEL_PLUGIN_ENABLED` (sandbox) | — | the per-turn `invoke_agent` model described here; without it (native mode) the sandbox vocabulary is entirely different (`service.name = "opencode"`, one unbounded trace per process) |
| Sampling (`OTEL_TRACES_SAMPLER`) | 100% | platform currently exports everything; if a deployment samples, counts become lower bounds |

## 5. Backend limits worth remembering

- Tag/tag-values endpoints answer from recent blocks when called **without `start`/`end`** — always range them.
- Per-attribute ingest size limit (typically 128 KiB when tuned; 2 KiB stock): very long `gen_ai.*.messages` arrive truncated and fail to parse.
- TraceQL metrics endpoint (`/api/metrics/query_range`) caps the range (typically 3 h).
- Very large traces can exceed the query-path message limit (`response larger than the max`) — project with `select()` instead of fetching whole.
