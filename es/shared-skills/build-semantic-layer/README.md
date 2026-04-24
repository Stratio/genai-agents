# build-semantic-layer

Orquestador end-to-end que construye la capa semántica completa de un dominio técnico en Stratio Governance. Ejecuta las **cinco fases del pipeline en secuencia** (términos técnicos → ontología → business views → SQL mappings → términos semánticos), con un paso opcional de publicación entre fases 4 y 5.

La skill invoca las herramientas MCP de gobierno inline — **no** delega en las skills individuales `create-*` (las skills no pueden invocar programáticamente otras skills). Las skills `create-*` siguen disponibles para usuarios que quieren ejecutar una sola fase de forma independiente.

## Qué hace

- Resuelve el dominio técnico y ejecuta un **diagnóstico completo en paralelo**: descripción de la colección, cobertura de términos técnicos, ontologías existentes, business views, mappings y términos semánticos — incluyendo su estado de gobierno.
- Presenta un dashboard de estado por fase y propone un plan de ejecución, señalando lo completo, parcial o pendiente, y las dependencias entre fases.
- Recoge **contexto global del usuario** una sola vez: ficheros de referencia (ontologías, specs, glosarios), definiciones de negocio, reglas de naming. Ese contexto se pasa como `user_instructions` a cada fase que lo acepte.
- Ejecuta cada fase en orden estricto, reportando progreso y el resumen de la herramienta tras cada una. La Fase 2 (ontología) ejecuta el mismo bucle de planning interactivo que `create-ontology`.
- Ofrece publicación opcional de las views entre la fase 4 y la fase 5.
- En caso de fallo, ofrece tres caminos de recuperación por fase: reintentar con instrucciones mejoradas, saltar (con aviso de dependencias) o abortar.

## Cuándo usarla

- Construir la capa semántica de una colección recién creada desde cero.
- Completar una capa semántica parcialmente construida (retomar donde se paró una ejecución previa).
- Auditar una capa semántica existente (el dashboard de diagnóstico vale por sí solo aunque no se ejecute ninguna fase).
- Para un cambio de una sola fase, prefiere la skill `create-*` correspondiente.

## Dependencias

### Otras skills
- **Prerrequisito duro:** `create-data-collection` (el dominio técnico debe existir).
- **Referencia (recomendada a cargar antes):** `stratio-semantic-layer` — las reglas de los MCPs de gobierno.
- **Delegadas en espíritu (no en código):** `create-technical-terms`, `create-ontology`, `create-business-views`, `create-sql-mappings`, `create-semantic-terms`.
- **Siguiente paso típico:** `manage-business-terms` para enriquecer el diccionario con business terms transversales.

### Guides
- `stratio-semantic-layer-tools.md` — referencia completa de los MCPs de gobierno: listado de herramientas, inmutabilidad de `domain_name`, contrato de `user_instructions`, protocolo de operaciones destructivas, reglas ADD+DELETE de ontologías, tabla de detección de estado para idempotencia y fallback de disponibilidad de OpenSearch.

### MCPs
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `create_ontology`, `update_ontology`, `delete_ontology_classes`, `create_technical_terms`, `list_technical_domain_concepts`, `create_business_views`, `delete_business_views`, `publish_business_views`, `create_sql_mappings`, `create_semantic_terms`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Las operaciones destructivas** (borrado de clases de ontología, regeneración de views con `regenerate=true`, regeneración de términos semánticos) requieren siempre confirmación explícita del usuario — el pipeline nunca autoregenera artefactos existentes.
- **Propagación de caché:** si el dominio no aparece tras `search_domains`, la skill reintenta con `refresh=true` y espera hasta ~60 segundos antes de rendirse.
- **Saltar una fase avisa de las dependencias:** saltar la fase de ontología implica que no se pueden crear views en la fase 3.
- **La publicación nunca es automática** — al usuario se le pregunta entre fase 4 y fase 5 si publicar las views (pasar de Draft a Pending Publish).
- **La capa semántica se convierte en el dominio `semantic_*`** una vez publicada al virtualizador; antes vive dentro del dominio técnico.
