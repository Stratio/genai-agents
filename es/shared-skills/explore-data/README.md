# explore-data

Exploración rápida de datos gobernados mediante los MCPs de datos de Stratio: busca dominios, entiende tablas y columnas, lee la terminología de negocio existente y, opcionalmente, ejecuta profiling estadístico ligero y checks de cobertura de calidad de gobierno antes de un análisis más profundo.

## Qué hace

- Resuelve el dominio objetivo por nombre o tópico (`search_domains` con `prefer_semantic` por defecto; cae a `list_domains` si no hay matches).
- Lista tablas, trae descripciones de negocio, metadata de columnas y domain knowledge, y aflora terminología de negocio relevante para la pregunta del usuario.
- Con alcance focalizado (un solo dominio o un subconjunto pequeño de tablas), ejecuta `profile_data` y `get_tables_quality_details` en paralelo para añadir una capa estadística + cobertura de gobierno sin convertir la exploración en un análisis completo.
- Lee `output/MEMORY.md` (cuando existe) para patrones de datos conocidos y avisa de problemas recurrentes antes de profiling.
- Produce un resumen estructurado y entre 3–5 sugerencias analíticas concretas ajustadas a las tablas y columnas encontradas (tendencia temporal, Pareto, segmentación, embudo, cohorte, etc.).

## Cuándo usarla

- El usuario pregunta "qué datos tenemos sobre X", "muéstrame las tablas del dominio Y", o quiere entender un dominio antes de elegir un análisis.
- Antes de análisis que requieren conocer relaciones entre tablas y semántica de columnas.
- Como lanzadera para otras skills: `assess-quality`, `propose-knowledge` o el workflow analítico del agente.
- **No** la uses como sustituto de una evaluación completa de calidad (usar `assess-quality`) ni para construir capa semántica (usar `build-semantic-layer`).

## Dependencias

### Otras skills
- **Referencia compañera:** `stratio-data` (reglas y patrones de los MCPs — se carga antes de cualquier interacción con datos).
- **Siguientes pasos típicos:** `assess-quality`, `propose-knowledge` o el workflow de análisis del agente.

### Guides
- `stratio-data-tools.md` — flujo de los MCPs de datos: `search_domains` → `list_domain_tables` → `get_tables_details` → `query_data`. Regla de oro: nunca escribir SQL a mano; siempre delegar en `generate_sql`. Cubre también umbrales de `profile_data` y uso de `get_tables_quality_details`.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`, `generate_sql`, `profile_data`, `get_tables_quality_details`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **El profiling es costoso.** La skill restringe `profile_data` a alcances focalizados (un dominio o una lista corta de tablas) y usa umbrales adaptativos de muestreo (100k / 1M filas) definidos en `stratio-data-tools.md` sección 5.1.
- **Dominios semánticos vs. técnicos:** por defecto la skill prefiere la capa semántica (`prefer_semantic=true`) — el nombre de dominio a secas del usuario se resuelve a la entrada `semantic_*` cuando existe. Cambia a técnico solo ante expresiones explícitas del usuario.
- **Integración con MEMORY.md:** cuando `output/MEMORY.md` existe, los patrones de datos conocidos se presentan al inicio para que el usuario no los redescubra.
