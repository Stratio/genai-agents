# refine-semantic-foreign-keys

Edición quirúrgica (añadir / modificar / eliminar) de relaciones de clave foránea entre vistas de negocio de un dominio de Stratio Governance. Hermana de `create-semantic-terms`, pero solo para mantenimiento de FKs — NO regenera los términos semánticos en sí.

## Qué hace

- Resuelve el dominio vía `search_domains(domain_type='technical')`, con fallback a `list_domains`. La herramienta acepta tanto el nombre técnico (canónico, preferido en los ejemplos) como la contraparte `semantic_*`; si el usuario escribe la forma semántica, la skill quita el prefijo en cliente y trabaja sobre el equivalente técnico, indicándole que ambas formas se aceptan.
- Inspecciona las candidatas con `list_technical_domain_concepts`: las vistas de negocio con `has_semantic_terms: true` son refinables independientemente del estado de gobernanza (Draft / Pending Publish / Published); las que tienen `has_semantic_terms: false` se presentan aparte y se redirige al usuario a `/create-semantic-terms` para esas.
- Ofrece dos opciones de scope: todas las vistas refinables (por defecto) o un subconjunto específico.
- Pide al usuario `user_instructions` (obligatorio) y le guía entre los dos intents productivos — **TARGETED** (nombrar una relación concreta) o **DISCOVERY** (pedir detectar FKs que falten en vistas concretas); las frases genéricas sin specifics desperdician un round-trip y se desaconsejan.
- Construye el `user_instructions` final mediante el **Glossary Instruction Enrichment Workflow** (`stratio-semantic-layer-tools.md` §11), con scope a la fase `semantic_terms`.
- Invoca `refine_semantic_foreign_keys` y reenvía el campo `message` de la herramienta (un resumen en markdown que cubre los totales del dominio y una lista por vista con `fk_count`, el resultado de la persistencia, el estado de actualización del TN, las columnas enriquecidas y cualquier aviso de omisión) tal cual al usuario — sin parsear campos. Los errores de la herramienta también se presentan tal cual.

## Cuándo usarla

- Una FK detectada por `create-semantic-terms` apunta a una vista destino errónea.
- La fase de creación se perdió una FK entre vistas que debería existir (modo DISCOVERY).
- Una FK ya no aplica y debe eliminarse.
- Una ejecución de mantenimiento dirigida que no debe regenerar todo el término semántico (más barato que `create_semantic_terms(regenerate=true)`).

## Dependencias

### Otras skills
- **Prerrequisito duro:** `create-semantic-terms` — cada vista que el usuario quiera refinar debe llevar ya un Término de Negocio semántico. La herramienta omite las vistas sin él con un aviso explícito.
- **Referencia (recomendada cargar antes):** `stratio-semantic-layer` — las reglas de las MCP de governance.

### Guías
- `stratio-semantic-layer-tools.md` — referencia completa de las MCP de governance, incluido el §11 Glossary Instruction Enrichment Workflow.

### MCPs
- **Governance (`gov`):** `refine_semantic_foreign_keys`, `list_technical_domain_concepts`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
Ninguna — skill solo de prompt.

### Sistema
Ninguno.

## Assets incluidos
Ninguno.

## Notas

- **`user_instructions` es obligatorio.** La herramienta rechaza entrada vacía o solo con espacios — sin una instrucción concreta no hay refinado.
- **No es destructiva por defecto.** Una FK se elimina solo cuando la instrucción la nombra explícitamente o su vista destino desapareció del dominio; las instrucciones genéricas preservan el estado actual.
- **Columnas multi-FK soportadas.** Una misma columna origen puede participar en varias relaciones FK y la chain renderiza un sufijo por cada relación; la skill no necesita gestión especial.
- **El contenido añadido por el usuario se preserva entre refinados.** Cualquier contenido añadido al Término de Negocio de una vista fuera de la sección autogenerada de `### Relaciones de Clave Foránea` — encabezados adicionales, prosa, listas, tablas — se mantiene intacto cuando el flujo de refinado reescribe la sección.
- **Las vistas sin Término de Negocio semántico se omiten.** Se le indica al usuario que ejecute `create_semantic_terms` antes; no se hacen llamadas a LLM para esas vistas.
- **No se requiere publicación.** Cualquier vista con término de negocio semántico es refinable, esté en Draft, Pending Publish o Published.
- **Idempotente.** Reejecutar la misma instrucción produce un diff vacío y `BT=unchanged` (ningún PUT).
- **Soporte de idiomas.** La herramienta subyacente solo soporta EN y ES. Otros idiomas devuelven un error explícito de la chain y se presentan al usuario sin presuponer la causa.
- **Tolerancia del formato del dominio.** La herramienta acepta tanto el nombre técnico (canónico) como la contraparte `semantic_*`; la skill normaliza en cliente a la forma técnica para mantener consistencia en el descubrimiento.
- **Los nombres de entrada se normalizan.** Los espacios al inicio o al final y los backticks envolventes en `view_names` se eliminan automáticamente.
- **Las FKs entre tablas técnicas son una skill distinta.** Para FKs entre tablas físicas de un dominio técnico usa `refine-foreign-keys`. Esta skill nunca enruta automáticamente entre las dos.
