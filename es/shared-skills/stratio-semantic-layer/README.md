# stratio-semantic-layer

Skill de referencia que carga las **reglas obligatorias, patrones de uso y mejores prácticas** para los MCPs de Stratio Governance (`create_ontology`, `create_business_views`, `create_technical_terms`, `create_sql_mappings`, `create_semantic_terms`, `create_business_term`, `publish_business_views`, `create_data_collection` y el toolkit completo de exploración del servidor `sql`).

Esta skill **no** invoca MCPs — carga el contrato que toda skill o agente relacionado con gobierno debe seguir.

## Qué hace

- Carga la referencia completa de MCPs de gobierno (`stratio-semantic-layer-tools.md`) en la conversación.
- Cubre:
  - El catálogo completo de herramientas dividido por servidor (`gov` + `sql`), con parámetros y propósito.
  - Reglas estrictas: inmutabilidad de `domain_name`, uso técnico-vs-semántico de dominios, `user_instructions` siempre ofrecido, confirmación obligatoria para operaciones destructivas (`regenerate=true`, `delete_*`), aprobación de publicación de views, semántica ADD+DELETE de ontologías, convenciones de naming para colecciones y ontologías.
  - Workflow de descubrimiento de dominio técnico (search → list → explorar tablas → detalles → columnas → conocimiento).
  - Exploración de dominios semánticos **publicados** (prefijo `semantic_*`).
  - Tabla de detección de estado para idempotencia: cómo detectar collections, términos técnicos, ontologías, views, mappings, términos semánticos y estado de publicación existentes antes de actuar.
  - Manejo de errores y recuperación (reintentar con `user_instructions` mejoradas, máx. 2 reintentos por entidad).
  - Reglas de ejecución paralela (lectura en paralelo, creaciones secuenciales dentro de una fase, secuencia estricta entre fases).
  - Protocolo de polling de tareas largas (`task_id` → `get_mcp_task_result` con `pending` / `done` / `error` / `not_found`).
  - Fallback de disponibilidad de OpenSearch (determinista `list_*` + filtro local por substring cuando los endpoints de search fallan).

## Cuándo usarla

- Antes de la primera interacción con cualquier herramienta MCP de gobierno en una conversación.
- Al refrescar las reglas para operaciones destructivas, publicación o semántica de ontologías.
- Cuando una skill `create-*` especializada no es la correcta pero el agente aún necesita invocar herramientas de gobierno directamente.
- Para un flujo específico (crear términos, ontología, views, mappings…), prefiere la skill `create-*` correspondiente — ya incluye el subconjunto relevante de estas reglas.

## Dependencias

### Otras skills
Ninguna. Es una skill de solo referencia; todas las demás skills de gobierno se construyen encima.

### Guides
- `stratio-semantic-layer-tools.md` — la referencia completa de MCPs de gobierno. Se carga íntegra cuando esta skill se activa.

### MCPs
Ninguno invocado directamente. El guide referencia el catálogo completo de MCPs de gobierno, listado en detalle en el guide compañero.

### Python
Ninguna — skill de referencia de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Cárgala pronto.** La skill está diseñada para ejecutarse antes de cualquier otra llamada a herramienta de gobierno; cargarla a mitad de conversación sigue funcionando, pero es menos eficiente porque las reglas pueden haberse roto ya.
- **Pareja con `stratio-data`** — entre las dos cubren las dos familias MCP (gobierno + datos). Los agentes que tocan ambas típicamente cargan las dos.
- **El guide vive en `shared-skill-guides/`** para que varias skills referencien la misma fuente de verdad sin duplicar.
