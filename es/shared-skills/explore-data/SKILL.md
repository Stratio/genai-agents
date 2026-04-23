---
name: explore-data
description: "Exploración rápida de dominios de datos, tablas, columnas, perfilado estadístico, cobertura de calidad de gobierno y terminología de negocio usando los MCPs de datos gobernados. Usar cuando el usuario quiera descubrir que datos hay disponibles, entender la estructura de un dominio o explorar tablas y columnas antes de un análisis."
argument-hint: "[dominio (opcional)]"
---

# Skill: Exploración de Dominios y Datos

Guía para explorar rapidamente los datos disponibles en los dominios gobernados.

## 1. Descubrimiento del Dominio

Leer y seguir `skills-guides/stratio-data-tools.md` sec 4 para los pasos de descubrimiento del dominio (buscar o listar dominios, seleccionar, explorar tablas, columnas y terminología).

Si el usuario proporciona un argumento ($ARGUMENTS), buscar con `search_domains($ARGUMENTS, prefer_semantic=true)` (defecto: colapsar entradas técnicas cuando existe una contraparte semántica con prefijo `semantic_` — el nombre desnudo del usuario se resuelve a la versión semántica). Cambiar a `prefer_semantic=false` solo si la redacción del usuario apunta explícitamente a la capa técnica (ver las instrucciones de Descubrimiento del agente para la lista cerrada de disparadores). Si el argumento coincide con un dominio, saltar directamente a explorar tablas. Si no coincide, preguntar al usuario cual dominio explorar siguiendo la convención de preguntas al usuario (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no). Preguntar si quiere profundizar en alguna tabla específica o ver todas.

## 2. Contexto Previo del Dominio

Si `output/MEMORY.md` existe, leer la sección "Patrones de Datos Conocidos" del dominio que se va a explorar. Si hay patrones registrados, informar al usuario antes de perfilar (ej: "En análisis anteriores se detecto que la columna X tiene ~35% nulos").

## 3. Profundización (cuando el alcance está acotado)

Cuando el usuario está centrado en un dominio concreto o un subconjunto reducido de tablas, añadir un paso de enriquecimiento ligero tras explorar columnas. Omitir este paso en exploraciones amplias de múltiples dominios — el profiling es costoso.

Para cada tabla clave identificada, lanzar **en paralelo**:
- `profile_data` por tabla — seguir `skills-guides/stratio-data-tools.md` sec 5.1 (SQL generada con `generate_sql`, umbrales adaptativos por tamaño, parámetro `limit`).
- `get_tables_quality_details(domain_name, [tablas])` — ver `skills-guides/stratio-data-tools.md` sec 5.2.

Resumir de forma ligera (descriptivo, sin convertir esto en un análisis):
- De `profile_data`: porcentajes de nulos destacables, rango temporal si hay columnas de fecha, cardinalidades anómalas u outliers que merezca flaggear.
- De `get_tables_quality_details`: número de reglas por tabla, desglose por estado (OK / KO / WARNING / not-executed), dimensiones con reglas en estado KO o WARNING.

Alimentar ambos hallazgos en el resumen de la sección 4. Si `profile_data` detecta una anomalía que ninguna regla de gobierno cubre (dimensión no cubierta), señalarla como candidata para la skill `assess-quality`.

## 4. Resumen y Sugerencias Proactivas

Presentar un resumen estructurado:
- Dominio explorado y su propósito
- Número de tablas disponibles
- Tablas principales con su descripción
- Columnas clave identificadas
- Términos de negocio relevantes
- Señales estadísticas destacables (si se ejecutó profiling en la sección 3)
- Cobertura de calidad de gobierno (si se consultaron los detalles de calidad en la sección 3)

### Análisis sugeridos basados en la estructura del dominio y los hallazgos

Tras explorar, detectar automáticamente oportunidades analíticas y presentarlas al usuario:

| Si encuentras... | Sugerir |
|-----------------|---------|
| Columnas de fecha (date, timestamp, periodo) | "**Tendencia temporal** — Como han evolucionado las [métricas] a lo largo del tiempo?" |
| Categorías (región, producto, segmento, tipo) | "**Comparación/Pareto** — Donde se concentra el 80% de [métrica]? Que [dimensión] destaca?" |
| Múltiples tablas relacionadas (FK, entidades compartidas) | "**Cruce** — Que relacion hay entre [tabla A] y [tabla B]? Ej: clientes × productos" |
| Variables numéricas + categóricas juntas | "**Segmentación** — Hay grupos naturales? Que perfiles de [entidad] existen?" |
| Columna de estado o etapa (pipeline, fase, status) | "**Funnel** — Cual es la tasa de conversion entre etapas? Donde se pierde más?" |
| Columnas monetarias (importe, precio, coste, ingreso) | "**Concentración** — El 20% de [entidades] genera el 80% de [métrica]?" |
| Columna de fecha alta + actividad posterior | "**Cohortes** — Como se retienen los [entidades] según su fecha de inicio?" |

Presentar como lista priorizada de 3-5 sugerencias concretas, adaptadas a las tablas y columnas reales del dominio explorado. Cada sugerencia debe mencionar tablas y columnas específicas.
