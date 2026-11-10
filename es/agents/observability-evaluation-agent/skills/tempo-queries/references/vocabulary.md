# Referencia: vocabulario de trazas de la plataforma Stratio GenAI

Mapa de los servicios, nombres de span y atributos que emite la plataforma. Refleja la instrumentación a mediados de 2026 — **el esquema vivo gana** cuando discrepen (`tasks/discover-schema.md`); trata cada entrada de aquí como "esperada", no "garantizada".

## 1. Identidad de servicio (atributos de resource)

Todos los módulos de la plataforma comparten `service.namespace = "stratio-genai"`. `service.name` es un rol lógico estable (no el despliegue); `service.instance.id` identifica el despliegue lógico (no el pod).

| `service.name` | Componente | Forma de `service.instance.id` |
|---|---|---|
| `genai-ui` | Frontend web (RUM del navegador) | `<servicio>.<namespace>` del despliegue de la UI |
| `genai-api` | Hub backend (plano de control) | `<servicio>.<namespace>` |
| `genai-chain-sql`, `genai-chain-governance`, ... | Subprocesos de chain, un nombre por *tipo* de chain | el id de despliegue de la chain |
| `genai-litellm` | Gateway LLM/MCP | `<servicio>.<namespace>` |
| `genai-agents-sandbox-opencode` | Runtime de agentes de Cowork (sandbox por proyecto) | `genai-project-<PROJECT_ID>:opencode` |
| `genai-agents-sandbox-nginx` / `-file-browser` / `-jwt-validator` | Servicios laterales del sandbox | `genai-project-<PROJECT_ID>:<componente>` |

Atributos de resource adicionales:
- `stratio.genai.eval = "true"` — marca los **ejecutores GenAI** (chains, gateway, runtime de agentes del sandbox). Los servicios de interfaz y plano de control (`genai-ui`, `genai-api`, laterales del sandbox) no lo llevan.
- Los procesos de chain añaden `stratio.genai.chain.{id, service_id, class, module, package_id}` en cada span que emiten.
- Los servicios del sandbox añaden `stratio.genai.{user.id, project.id, project.name, agent.name, agent.version}` a nivel de resource.

## 2. Mapa de spans (quién emite qué)

**Spans de turno** — las unidades con calidad de evaluación; se emiten siempre que el trazado está encendido, su *contenido* está gateado por knob:

| Span | Emisor | Uno por |
|---|---|---|
| `invoke_agent <agent>` (`gen_ai.operation.name = invoke_agent`) | runtime de agentes del sandbox | turno de agente de Cowork (raíz de su propia traza) |
| `invoke_workflow <chain>` (`gen_ai.operation.name = invoke_workflow`) | proceso de chain | invocación de chain |

**Spans de trayectoria** (hijos de un turno):

| Span | Emisor | Significado |
|---|---|---|
| `chat <model>` | runtime del sandbox y gateway LLM | una llamada LLM (cada lado emite el suyo) |
| `execute_tool <tool>` | runtime del sandbox / wrapper MCP de la chain | un tool call |
| `<servicio>.<operación>` (p. ej. `governance.get_glossary_items`, `virtualizer.run_sql_command`, `opensearch.search_filter_values`) | proceso de chain | una llamada a servicio de plataforma, con `peer.service` fijado |
| Spans de nodo LangChain/LangGraph (convención OpenInference, `openinference.span.kind`) | proceso de chain | **solo con el knob de LangChain encendido** (apagado por defecto) |
| `POST /chat/completions`, `auth ...`, `postgres ...` | gateway LLM | gestión de la petición alrededor de cada llamada LLM |
| Spans HTTP cliente/servidor (`POST /invoke`, `POST /v1/chains/{chain_id}/stream`, ...) | todos los servicios backend | el esqueleto que cose los servicios entre sí |

**Spans del frontend (navegador)** — servicio `genai-ui`:

| Span | Significado |
|---|---|
| `cowork.send-message` | uno por prompt enviado desde la UI de Cowork (raíz de la traza del lado navegador) |
| `METHOD /route/:id` | cada XHR/fetch que hace la UI (incluye el polling intenso de sesión: `GET .../session/:id/message`, `.../todo`) |
| `documentLoad` | carga inicial de la página |

**Agrupación de sesión**: una conversación de Cowork *no* es una traza. Cada turno es su propia traza; el envío del navegador es otra; se cosen con span links y, más prácticamente, con atributos compartidos: `gen_ai.conversation.id` (= id de la sesión raíz, en spans GenAI), `stratio.genai.opencode.session.id` (en spans del navegador *y* del sandbox), `stratio.genai.message.id` (envío↔turno).

## 3. Atributos de span clave

| Atributo | Dónde | Notas |
|---|---|---|
| `gen_ai.operation.name` | spans GenAI | `invoke_agent` \| `invoke_workflow` \| `chat` \| `execute_tool` |
| `gen_ai.conversation.id` | spans de turno + trayectoria | id de sesión (Cowork) o id de chat (chains). Nunca fabricado: ausente cuando no hay conversación |
| `gen_ai.agent.name` | spans del sandbox | nombre del agente de Cowork |
| `gen_ai.workflow.name` | `invoke_workflow` | nombre lógico de la chain |
| `gen_ai.input.messages` / `gen_ai.output.messages` | spans de turno | **gateados por captura**. Strings JSON: `[{role, parts[]}]`, el output añade `finish_reason` |
| `gen_ai.usage.input_tokens` / `output_tokens` | spans `chat` | consumo de tokens |
| `gen_ai.tool.name` / `gen_ai.tool.call.id` | `execute_tool` | identidad de la tool; argumentos/resultados solo con captura de trayectoria |
| `stratio.genai.user.id` | spans del navegador (nivel span); sandbox (nivel resource) | **no** está en los spans `invoke_agent` — puentea usuarios↔sesiones por los spans del navegador |
| `stratio.genai.app` | spans del navegador | `cowork` \| `talk-to-your-data` \| `dashboards` \| `settings` |
| `stratio.genai.chat.id` | spans del navegador + chain | id de chat (grafía con puntos) |
| `stratio.genai.opencode.session.id` / `.root_session.id` | spans del navegador + sandbox | la clave de sesión entre ambos lados |
| `stratio.genai.message.id` | `cowork.send-message`, `invoke_agent`, `chat` | clave de correlación envío↔turno |
| `stratio.genai.opencode.turn.origin` | `invoke_agent` | `user_message` \| `lazy` (turnos internos de título/resumen/compactación) |
| `stratio.genai.opencode.turn.llm_calls` / `.turn.tool_calls` | `invoke_agent` | contadores por turno |
| `stratio.genai.opencode.span.end_reason` | spans del sandbox | `completed` es el único valor fiable para evaluación; los demás significan cierre anómalo |
| `stratio.genai.opencode.cost_usd` | `chat` del sandbox | coste por llamada |
| `stratio.genai.opencode.tool.title` / `.tool.output_bytes` | `execute_tool` | metadatos de la tool (nunca contenido) |
| `litellm.*` (`litellm.cost.total`, `litellm.call_id`, ...) | spans `chat` del gateway | atributos vendor; verifica los nombres en vivo antes de apoyarte en ellos |

**Puntos vs guiones (transitorio):** la convención de la plataforma es la grafía con puntos `stratio.genai.*`, pero el hub backend (`genai-api`) todavía estampa atributos de span con guiones (`stratio-genai-user-id`, `stratio-genai-tenant`, `stratio-genai-request-id`, `stratio-genai-auth-type`). Las queries cross-service sobre esas dimensiones necesitan un OR sobre ambas grafías hasta que la migración se complete.

## 4. Knobs que condicionan qué señal existe

Interruptores de entorno del lado del despliegue. **Consulta esta tabla antes de concluir "X no ocurrió"** — los dos falsos negativos más comunes son la captura de contenido apagada y los spans de LangChain apagados.

| Knob (env del despliegue observado) | Default | Efecto sobre lo que puedes consultar |
|---|---|---|
| `OPENTELEMETRY_ENABLED` (por módulo) | off | gate maestro: ningún span en absoluto de ese módulo |
| `STRATIO_GENAI_CAPTURE_EVAL_CONTENT` (o la global `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`) | off | `gen_ai.input/output.messages` en los spans de turno |
| `STRATIO_GENAI_CAPTURE_TRAJECTORY_CONTENT` | off | argumentos/resultados de tools, contenido de nodos LangChain, captura de contenido del gateway |
| `STRATIO_GENAI_TRACE_LANGCHAIN` (chains) | off | que los spans de nodo LangChain/LangGraph existan siquiera |
| `STRATIO_GENAI_TRACE_BACKGROUND_TASKS` (chains) | off | que las trazas de ciclos de refresco en segundo plano (`governance metadata refresh`, ...) existan siquiera |
| `GENAI_OTEL_PLUGIN_ENABLED` (sandbox) | — | el modelo por turno `invoke_agent` descrito aquí; sin él (modo nativo) el vocabulario del sandbox es completamente distinto (`service.name = "opencode"`, una traza sin límite por proceso) |
| Sampling (`OTEL_TRACES_SAMPLER`) | 100% | la plataforma exporta actualmente todo; si un despliegue muestrea, los conteos pasan a ser cotas inferiores |

## 5. Límites del backend que conviene recordar

- Los endpoints de tags/tag-values responden solo con bloques recientes cuando se llaman **sin `start`/`end`** — ponles rango siempre.
- Límite de tamaño por atributo en ingesta (típicamente 128 KiB cuando está tuneado; 2 KiB de fábrica): los `gen_ai.*.messages` muy largos llegan truncados y fallan al parsear.
- El endpoint de métricas TraceQL (`/api/metrics/query_range`) limita el rango (típicamente 3 h).
- Las trazas muy grandes pueden superar el límite de mensaje del camino de consulta (`response larger than the max`) — proyecta con `select()` en lugar de descargarlas enteras.
