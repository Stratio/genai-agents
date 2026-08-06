---
name: tempo-queries
description: "Consulta Grafana Tempo para las trazas OpenTelemetry de la plataforma Stratio GenAI: conecta a través del proxy de datasources de Grafana, descubre el esquema de trazas, responde preguntas de uso de Cowork (agentes usados, usuarios activos, sesiones por usuario), reconstruye una conversación de Cowork turno a turno e inspecciona invocaciones de la chain SQL. Úsala cuando el usuario pregunte cualquier cosa que deba responderse desde las trazas de la plataforma — uso, actividad de sesiones, reconstrucción de conversaciones, comportamiento de chains, errores o latencia."
---

# Skill: queries de trazas sobre Grafana Tempo

Skill router. Cada capacidad vive en su propio fichero bajo `tasks/`. **Este fichero es deliberadamente mínimo** — cuando el agente necesite realizar una tarea concreta, debe cargar y seguir el sub-fichero correspondiente al completo. No improvises queries desde este índice.

## Prerrequisitos — leer primero

- Conexión: `tasks/connect.md` construye la URL base `{PROXY}` (una vez por sesión). El resto de tasks asume que `{PROXY}` existe.
- Vocabulario: `references/vocabulary.md` es el mapa de servicios, nombres de span, atributos y los knobs de captura que condicionan qué señal existe. Consúltalo antes de interpretar resultados o escribir queries nuevas; verifícalo contra el esquema vivo (`tasks/discover-schema.md`) cuando algo no cuadre.

## Convenciones de query compartidas (aplican a todas las tasks)

1. **Pasa siempre un rango temporal**: `start` y `end` en segundos Unix en cada llamada de search, tags y tag-values. Sin ellos Tempo responde en silencio solo con los bloques recientes y los resultados parecen completos sin serlo. Calcúlalo con `date +%s` (p. ej. `START=$(( $(date +%s) - 86400 ))` para las últimas 24 h).
2. **Codifica siempre la query TraceQL en la URL**: usa `curl -sG ... --data-urlencode 'q={ ... }'` — las llaves, comillas y espacios no sobreviven al salto por el proxy de otra forma.
3. **Acota el volumen**: fija `limit` explícito en las búsquedas (el default es bajo); añade `spss` (spans por span-set) al seleccionar spans. Di cuándo una respuesta se apoya en un resultado truncado.
4. **Proyecta, no descargues**: prefiere `| select(span.attr, ...)` en la query de búsqueda para obtener los atributos directamente en el resultado; descarga trazas completas (`{PROXY}/api/traces/{traceID}`) solo cuando se necesite el árbol de ejecución en sí.
5. **Solo lectura**: únicamente peticiones `GET`, sin credenciales.

## Índice de capacidades

| Capacidad | Cuándo usarla | Sub-fichero a cargar |
|---|---|---|
| Conectar al backend de trazas | Primera pregunta de trazas de la sesión; `{PROXY}` aún no construida. | `tasks/connect.md` |
| Descubrir el esquema | Nombres de atributos o convenciones desconocidos; verificar qué señal existe en una ventana; algo devuelve vacío inesperadamente. | `tasks/discover-schema.md` |
| Preguntas de uso de Cowork | Qué agentes se usaron, qué usuarios estuvieron activos, sesiones por usuario, proyectos/sandboxes ejecutados. | `tasks/cowork-usage.md` |
| Inspeccionar / reconstruir una sesión de Cowork | Qué pasó en la sesión X; reconstruir la conversación turno a turno; extraer input de evaluación black-box. | `tasks/cowork-session.md` |
| Actividad de la chain SQL | Invocaciones de la chain, errores, latencia, llamadas a servicios de plataforma, contenido de turnos de chain para evaluación. | `tasks/sql-chain.md` |

## Reglas de enrutado

1. Identifica la capacidad a partir de la intención del usuario. Si ninguna encaja, compón las primitivas de `tasks/discover-schema.md` (tags → valores de tag → search → descarga de traza) y di qué convención encontraste.
2. Asegúrate de que `tasks/connect.md` se ha completado una vez antes de cualquier otra task.
3. Carga el sub-fichero correspondiente y síguelo de principio a fin. No mezcles instrucciones de distintos sub-ficheros.
4. Interpreta los resultados con `references/vocabulary.md` a mano — especialmente la tabla de knobs antes de concluir que algo "no ocurrió".

## Añadir una capacidad nueva

1. Crea `tasks/<capacidad>.md` con: cuándo usarla, las queries exactas (curl listo para ejecutar), cómo interpretar el resultado y los caveats que apliquen.
2. Añade una entrada al **Índice de capacidades** de arriba.
3. Refleja ambos ficheros bajo el overlay `es/`.
