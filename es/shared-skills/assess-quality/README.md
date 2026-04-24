# assess-quality

Evaluación read-only de cobertura de calidad de datos sobre un dominio, tabla o columna única en gobierno. Responde "qué dimensiones están monitorizadas, cuáles faltan y qué columnas son candidatas prioritarias para nuevas reglas". La salida es un resumen estructurado en chat — la skill **no** crea reglas ni genera ficheros por sí misma.

## Qué hace

- Determina el alcance: dominio completo, tabla(s) específica(s), o columna única.
- Carga el catálogo de dimensiones específico del dominio (`get_quality_rule_dimensions` — **obligatorio**, porque las definiciones de `completeness`, `validity`, etc. pueden variar por dominio).
- Lanza el resto en paralelo: lista de tablas, estado de reglas existentes (`get_tables_quality_details`), semántica de tablas y columnas, y profiling estadístico (`profile_data` vía SQL generado con `generate_sql`).
- Construye un análisis de gaps **semantics-first** (qué dimensiones deberían existir dada la semántica de negocio de cada columna) y **EDA-validated** (confirma, prioriza y parametriza los gaps).
- Ajusta el razonamiento para dominios técnicos (donde las descripciones de negocio pueden faltar, la EDA pasa a ser la fuente primaria).
- Presenta resultados en cinco secciones canónicas: resumen ejecutivo, tabla de cobertura por dimensión, estado de reglas existentes, gaps priorizados y siguientes pasos recomendados.
- Termina con una pregunta de seguimiento: crear reglas, generar un reporte formal, profundizar o parar.

## Cuándo usarla

- El usuario quiere conocer el estado actual de calidad de un dominio o tabla.
- Antes de crear nuevas reglas de calidad — `assess-quality` determina las reglas esperadas y los gaps que las justifican.
- Antes de escribir un reporte formal de calidad (la evaluación alimenta `quality-report`).
- Para un pipeline end-to-end "assess → create → report", el agente encadena esta skill con `create-quality-rules` y luego `quality-report`.

## Dependencias

### Otras skills
- **Referencia compañera:** `stratio-data` (reglas y patrones de los MCPs).
- **Siguientes pasos típicos:** `create-quality-rules` (para actuar sobre los gaps), `quality-report` (para formalizar la evaluación).

### Guides
- `stratio-data-tools.md` — flujo de los MCPs de datos: descubrimiento de dominio, generación de SQL, ejecución paralela, umbrales de `profile_data`.
- `quality-exploration.md` — paso obligatorio de `get_quality_rule_dimensions`, señales de EDA por tipo de columna (nulls → completeness, distinct_count → uniqueness, min/max → validity, etc.) y el ajuste para dominios técnicos.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `generate_sql`, `profile_data`.
- **Governance (`gov`):** `get_quality_rule_dimensions`, `quality_rules_metadata`, `get_tables_quality_details`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Read-only:** la skill nunca llama a `create_quality_rule` ni a MCPs destructivos. Si el usuario quiere actuar sobre los gaps, el agente delega en `create-quality-rules` tras aprobación explícita.
- **La EDA nunca se usa para *evitar* una regla:** cero nulls hoy no cancela una regla de `completeness` en una columna ID — la regla sigue protegiendo frente a nulls futuros.
- **Escala:** para dominios con más de 10 tablas, la skill evalúa primero las que el usuario menciona y pregunta antes de continuar; profiling full-domain es caro.
- **La cifra de cobertura es una estimación** (reglas esperadas vs. existentes), no una métrica exacta. Usa rangos cuando hay incertidumbre ("entre 40% y 60% de cobertura").
