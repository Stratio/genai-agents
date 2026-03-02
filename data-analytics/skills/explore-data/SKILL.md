---
name: explore-data
description: Exploracion rapida de dominios de datos, tablas, columnas, perfilado estadistico y terminologia de negocio usando los MCPs de datos gobernados. Usar cuando el usuario quiera descubrir que datos hay disponibles, entender la estructura de un dominio o explorar tablas y columnas antes de un analisis.
argument-hint: [dominio (opcional)]
---

# Skill: Exploracion de Dominios y Datos

Guia para explorar rapidamente los datos disponibles en los dominios gobernados.

## 1-7. Descubrimiento del Dominio

Leer y seguir `skills-guides/exploration.md` para los pasos de descubrimiento del dominio (listar dominios, seleccionar, explorar tablas, columnas, terminologia y profiling).

Si el usuario proporciona un argumento ($ARGUMENTS) que coincide con un dominio conocido, saltar directamente a explorar tablas. Si no, preguntar al usuario cual dominio explorar siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md) (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no). Preguntar si quiere profundizar en alguna tabla especifica o ver todas.

## 7.5 Contexto Previo del Dominio

Si `output/MEMORY.md` existe, leer la seccion "Patrones de Datos Conocidos" del dominio que se va a explorar. Si hay patrones registrados, informar al usuario antes de perfilar (ej: "En analisis anteriores se detecto que la columna X tiene ~35% nulos").

## 8. Resumen y Sugerencias Proactivas

Presentar un resumen estructurado:
- Dominio explorado y su proposito
- Numero de tablas disponibles
- Tablas principales con su descripcion
- Columnas clave identificadas
- Terminos de negocio relevantes
- Observaciones de calidad de datos (si se hizo perfilado)

### Analisis sugeridos basados en la estructura del dominio

Tras explorar, detectar automaticamente oportunidades analiticas y presentarlas al usuario:

| Si encuentras... | Sugerir |
|-----------------|---------|
| Columnas de fecha (date, timestamp, periodo) | "**Tendencia temporal** — Como han evolucionado las [metricas] a lo largo del tiempo?" |
| Categorias (region, producto, segmento, tipo) | "**Comparacion/Pareto** — Donde se concentra el 80% de [metrica]? Que [dimension] destaca?" |
| Multiples tablas relacionadas (FK, entidades compartidas) | "**Cruce** — Que relacion hay entre [tabla A] y [tabla B]? Ej: clientes × productos" |
| Variables numericas + categoricas juntas | "**Segmentacion** — Hay grupos naturales? Que perfiles de [entidad] existen?" |
| Columna de estado o etapa (pipeline, fase, status) | "**Funnel** — Cual es la tasa de conversion entre etapas? Donde se pierde mas?" |
| Columnas monetarias (importe, precio, coste, ingreso) | "**Concentracion** — El 20% de [entidades] genera el 80% de [metrica]?" |
| Columna de fecha alta + actividad posterior | "**Cohortes** — Como se retienen los [entidades] segun su fecha de inicio?" |

Presentar como lista priorizada de 3-5 sugerencias concretas, adaptadas a las tablas y columnas reales del dominio explorado. Cada sugerencia debe mencionar tablas y columnas especificas.
