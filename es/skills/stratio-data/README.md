# stratio-data

Skill de referencia que carga las **reglas obligatorias, patrones de uso y mejores prácticas** para las herramientas MCP de datos de Stratio (`query_data`, `search_domains`, `list_domains`, `generate_sql`, `profile_data`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`, `get_tables_quality_details`, `propose_knowledge`, …).

Esta skill **no** invoca MCPs — carga el contrato que toda skill o agente relacionado con datos debe seguir antes de tocar datos gobernados.

## Qué hace

- Carga la referencia completa de MCPs de datos (`stratio-data-tools.md`) en la conversación.
- Cubre:
  - El catálogo completo de herramientas del servidor `sql`, con parámetros y propósito.
  - La regla fundamental: **nunca escribir SQL a mano** — delegar siempre la generación en `query_data` o `generate_sql`.
  - Reglas estrictas: inmutabilidad de `domain_name`, estrategia MCP-first, cuándo usar `query_data` vs. Python/pandas, valores válidos de `output_format`, semántica de ejecución paralela.
  - Workflow de descubrimiento de dominio (search → list → tablas → detalles → columnas → terminología).
  - Reglas de profiling: umbrales de `profile_data` (<100k / 100k–1M / >1M filas), generación de SQL vía `generate_sql`, uso del parámetro `limit` en lugar de `LIMIT` en el SQL.
  - Cobertura de calidad de gobierno vía `get_tables_quality_details` — check ligero durante exploración (no reemplaza a `assess-quality`).
  - Cascada de clarificación cuando `query_data` / `generate_sql` responden con una pregunta en lugar de datos (buscar en conocimiento → inferir del plan → preguntar al usuario → reformular → reportar).
  - Siete validaciones post-query que aplicar a cada resultado de `query_data`.
  - Polling de tareas largas (`task_id` → `get_mcp_task_result` con `pending` / `done` / `error` / `not_found`).
  - Fallback de disponibilidad de OpenSearch para `search_domains` cuando el índice no está disponible.

## Cuándo usarla

- Antes de la primera llamada a cualquier MCP de datos en una conversación.
- Al refrescar las reglas para generación de queries, profiling, ejecución paralela o manejo de clarificaciones.
- Cuando el agente va a trabajar con un dominio no tocado en esta sesión.
- Para exploración amplia adaptada a la pregunta del usuario, prefiere `explore-data` — ya incluye el subconjunto relevante de estas reglas.

## Dependencias

### Otras skills
Ninguna. Es una skill de solo referencia; todas las demás skills consumidoras de datos se construyen encima.

### Guides
- `stratio-data-tools.md` — la referencia completa de MCPs de datos. Se carga íntegra cuando esta skill se activa.

### MCPs
Ninguno invocado directamente. El guide referencia el catálogo completo de MCPs de datos, listado en detalle en el guide compañero.

### Python
Ninguna — skill de referencia de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Cárgala pronto.** La skill está diseñada para ejecutarse antes de cualquier otra llamada a herramienta de datos en una conversación; cargarla a mitad sigue funcionando pero las reglas pueden haberse roto ya.
- **Pareja con `stratio-semantic-layer`** — entre las dos cubren las dos familias MCP (datos + gobierno). Los agentes que tocan ambas típicamente cargan las dos.
- **El guide se mantiene en `shared-skill-guides/`** para que varias skills referencien la misma fuente de verdad sin duplicar.
