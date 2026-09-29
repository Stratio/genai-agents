# Observability & Evaluation Agent

Ask questions about what the Stratio GenAI platform actually did — and get answers backed by its OpenTelemetry traces. The agent queries the platform's trace backend (Grafana Tempo), reconstructs what happened, and cites the evidence for every claim.

## What this agent does

- **Usage questions**: which Cowork agents have been used, which users were active, how many sessions each user had, which projects ran.
- **Session inspection**: what happened in a given Cowork session — turns, tool calls, LLM calls, timing.
- **Conversation reconstruction**: rebuild a session turn by turn (user input, agent output) — ready to use as input for black-box evaluations.
- **SQL chain activity**: invocations, errors, latency, platform-service calls, and turn content when capture is enabled.
- **Evaluations on your terms**: you define the criteria; the agent applies them to the reconstructed behavior and ties every verdict to trace evidence.

It is **read-only**: it only issues `GET` requests against the trace backend and changes nothing.

## How it works

1. **Connect** — on the first question, the agent resolves the Grafana URL (environment variable or asks you, offering the platform default) and verifies the backend responds.
2. **Investigate** — it discovers the trace schema, searches with TraceQL, and drills into the traces the question needs. It asks for the time window when unclear.
3. **Report** — findings come with their `trace_id`s; observations and inferences are labeled apart. For evaluations, it first asks what "good" looks like to you.

## What you can ask

- "¿Qué agentes se han usado esta semana?"
- "How many sessions did user X have yesterday?"
- "What happened in session `ses_...`? Reconstruct the conversation."
- "Get me the input for a black-box evaluation of that session."
- "Show the SQL chain invocations of the last 24 hours and their latency."
- "Did any chain invocation fail this morning? Where did it fail?"

## Good to know

- Traces show what *ran*, not what is *deployed* — inventory questions belong to the platform administration UI, and the agent will say so.
- Conversation content appears in traces only when the platform's content-capture setting is enabled; otherwise the agent reports the structure (turns, tools, timing) and tells you content capture is off.
- If a question cannot be answered from traces (logs, live configuration, database state), the agent says so instead of guessing.
