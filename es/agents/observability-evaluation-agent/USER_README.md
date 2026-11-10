# Agente de Observabilidad y Evaluación

Pregunta qué hizo realmente la plataforma Stratio GenAI — y obtén respuestas respaldadas por sus trazas OpenTelemetry. El agente consulta el backend de trazas de la plataforma (Grafana Tempo), reconstruye lo que ocurrió y cita la evidencia de cada afirmación.

## Qué hace este agente

- **Preguntas de uso**: qué agentes de Cowork se han usado, qué usuarios estuvieron activos, cuántas sesiones tuvo cada usuario, qué proyectos se ejecutaron.
- **Inspección de sesiones**: qué pasó en una sesión de Cowork concreta — turnos, tool calls, llamadas LLM, tiempos.
- **Reconstrucción de conversaciones**: reconstruye una sesión turno a turno (entrada del usuario, salida del agente) — lista para usar como input de evaluaciones black-box.
- **Actividad de la chain SQL**: invocaciones, errores, latencia, llamadas a servicios de plataforma y contenido de los turnos cuando la captura está habilitada.
- **Evaluaciones según tus términos**: tú defines los criterios; el agente los aplica al comportamiento reconstruido y liga cada veredicto a la evidencia de las trazas.

Es **de solo lectura**: únicamente emite peticiones `GET` contra el backend de trazas y no cambia nada.

## Cómo funciona

1. **Conectar** — con la primera pregunta, el agente resuelve la URL de Grafana (variable de entorno o te la pregunta, ofreciendo el default de la plataforma) y verifica que el backend responde.
2. **Investigar** — descubre el esquema de trazas, busca con TraceQL y profundiza en las trazas que la pregunta necesite. Pregunta la ventana temporal cuando no esté clara.
3. **Informar** — los hallazgos vienen con sus `trace_id`; observaciones e inferencias se etiquetan por separado. Para evaluaciones, primero pregunta qué significa "bien" para ti.

## Qué puedes preguntarle

- "¿Qué agentes se han usado esta semana?"
- "¿Cuántas sesiones tuvo el usuario X ayer?"
- "¿Qué pasó en la sesión `ses_...`? Reconstruye la conversación."
- "Dame el input para una evaluación black-box de esa sesión."
- "Muéstrame las invocaciones de la chain SQL de las últimas 24 horas y su latencia."
- "¿Falló alguna invocación de chain esta mañana? ¿Dónde falló?"

## Conviene saber

- Las trazas muestran lo que *se ejecutó*, no lo que está *desplegado* — las preguntas de inventario pertenecen a la UI de administración de la plataforma, y el agente lo dirá.
- El contenido de las conversaciones aparece en las trazas solo cuando la opción de captura de contenido de la plataforma está habilitada; en caso contrario el agente informa de la estructura (turnos, tools, tiempos) y te dice que la captura de contenido está apagada.
- Si una pregunta no puede responderse desde trazas (logs, configuración viva, estado de bases de datos), el agente lo dice en lugar de adivinar.
