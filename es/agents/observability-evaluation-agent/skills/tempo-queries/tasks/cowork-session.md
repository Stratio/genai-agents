# Task: inspeccionar / reconstruir una sesión de Cowork

Dado un id de sesión (`ses_*`), responde "qué pasó en esta sesión" y reconstruye la conversación turno a turno — el input para evaluaciones black-box.

Necesita `{PROXY}` (ver `tasks/connect.md`), el id de sesión y una ventana que cubra la sesión:

```bash
SES="ses_..."
NOW=$(date +%s); START=$((NOW - 86400))
```

## Recetas

### 1. Todo lo que dejó la sesión (visión general)

`stratio.genai.opencode.session.id` se estampa en **ambos** lados — spans RUM del navegador y spans del runtime del agente — así que una sola query lista la actividad completa:

```bash
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode "q={ span.stratio.genai.opencode.session.id = \"${SES}\" }" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
  --data-urlencode "limit=100"
```

Lee el resultado como tres familias (por `rootServiceName` / `rootTraceName`):
- **Turnos de agente**: raíz `invoke_agent <agent>` en el servicio del sandbox — la sustancia.
- **Acciones de envío**: raíz `cowork.send-message` en el servicio del frontend — una por prompt enviado desde el navegador.
- **Polling de la UI**: `GET .../session/:id/message`, `.../todo` en el frontend — ruido para la mayoría de preguntas; ignóralo salvo que pregunten por el comportamiento de la UI.

### 2. Reconstruir la conversación (input de evaluación black-box)

Una sola query devuelve todos los turnos **con su contenido**, sin descargar trazas completas:

```bash
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode "q={ span.gen_ai.operation.name = \"invoke_agent\" && span.gen_ai.conversation.id = \"${SES}\" } | select(span.gen_ai.input.messages, span.gen_ai.output.messages, span.stratio.genai.message.id, span.stratio.genai.opencode.turn.origin, span.stratio.genai.opencode.span.end_reason, span.stratio.genai.opencode.turn.tool_calls)" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
  --data-urlencode "limit=100" --data-urlencode "spss=10"
```

Ensamblado:
1. Reúne los spans coincidentes de cada traza devuelta (una traza por turno) y **ordena por `startTimeUnixNano`**.
2. `gen_ai.input.messages` / `gen_ai.output.messages` son strings JSON — arrays de `{role, parts[]}` (el output añade `finish_reason`). Parséalos y preséntalos como turnos Usuario/Asistente.
3. Conserva `stratio.genai.message.id` por turno: es la clave de correlación con el span `cowork.send-message` del navegador y con el almacén de conversaciones de la plataforma.

### 3. Profundizar en un turno (tools, llamadas LLM, coste)

Descarga la traza completa del turno solo cuando la pregunta necesite el árbol de ejecución:

```bash
curl -sS "${PROXY}/api/traces/<traceID>"
```

Dentro, por familia de spans:
- `chat <model>` — uno por llamada LLM; `gen_ai.usage.input_tokens` / `output_tokens`, `stratio.genai.opencode.cost_usd`.
- `execute_tool <tool>` — uno por tool call; `gen_ai.tool.name`, `stratio.genai.opencode.tool.title`, `stratio.genai.opencode.tool.output_bytes`.
- Los spans del lado del gateway (`POST /chat/completions`, `chat <model>` en el servicio del gateway LLM) reflejan cada llamada LLM con el detalle del proveedor.

## Caveats (aplican a toda reconstrucción)

- **El contenido solo existe cuando la captura está habilitada** en el despliegue observado. Los spans `invoke_agent` existen siempre, pero `gen_ai.input.messages` / `gen_ai.output.messages` aparecen solo con el knob de captura de contenido de evaluación encendido (ver la tabla de knobs de `references/vocabulary.md`). Si faltan, informa del esqueleto (número de turnos, tiempos, tools) y di que la captura de contenido está apagada — no lo presentes como "la conversación estaba vacía".
- **Filtra los turnos lazy**: `stratio.genai.opencode.turn.origin = "lazy"` marca turnos internos de título/resumen/compactación. Solo los turnos `user_message` pertenecen a la reconstrucción de una conversación.
- **Descarta los turnos truncados para evaluación**: quédate solo con `stratio.genai.opencode.span.end_reason = "completed"`; otros valores (`superseded`, `session_idle`, `session_error`, barridos por TTL/LRU) significan que el span cerró de forma anómala y su contenido puede ser parcial.
- **Los subagentes no dejan conversación propia**: un tool call `task` muestra título y tamaño de salida, no el prompt ni la respuesta del subagente. Los argumentos/resultados de tools en general aparecen solo con el knob de captura de trayectoria encendido.
- **Navegador↔turno son trazas separadas** cosidas por span links (solo los turnos de mensaje de usuario llevan el link). Correlaciona por los atributos compartidos (familia `session.id`, `stratio.genai.message.id`); el seguimiento de links (`link:traceID`) existe en versiones recientes de Tempo pero rara vez hace falta.
- **Los turnos muy largos pueden chocar con el límite de tamaño por atributo del backend** — un valor de `gen_ai.*.messages` truncado fallará al parsear como JSON. Informa del turno como truncado-en-ingesta; el almacén de conversaciones de la plataforma es entonces la única fuente completa.
- **Minimiza la exposición**: las reconstrucciones contienen prompts de usuario y salidas del modelo. Muéstralos solo hasta donde la pregunta lo requiera; enmascara cuando la pregunta del usuario sea sobre estructura, no sobre contenido.
