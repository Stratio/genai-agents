# refine-foreign-keys

Edición quirúrgica (añadir / modificar / eliminar) de claves foráneas virtuales en las tablas de un dominio técnico de Stratio Governance. Hermana de `create-technical-terms`, pero solo para mantenimiento de FKs — NO regenera los términos técnicos en sí.

## Qué hace

- Resuelve el dominio técnico (`search_domains` con `domain_type='technical'`, con fallback a `list_domains`).
- Informa de las candidatas: las tablas con términos técnicos previamente generados son elegibles; las que no tienen TN se muestran y se invita al usuario a ejecutar `/create-technical-terms` primero.
- Ofrece dos opciones de scope: todas las tablas elegibles (por defecto) o un subconjunto específico.
- Pide al usuario `user_instructions` (obligatorio) y le guía entre los dos intents productivos — **TARGETED** (nombrar una relación concreta) o **DISCOVERY** (pedir detectar FKs que falten en tablas concretas); las frases genéricas sin specifics desperdician un round-trip y se desaconsejan.
- Construye el `user_instructions` final mediante el **Glossary Instruction Enrichment Workflow** (`stratio-semantic-layer-tools.md` §11), con scope a la fase `technical_terms`.
- Invoca `refine_foreign_keys` y reenvía el campo `message` de la herramienta (un resumen en markdown que cubre los totales del dominio y una lista por tabla con los nombres de FK añadidas / mantenidas / reemplazadas / borradas, el resultado de la persistencia, el estado de actualización del TN y cualquier aviso de omisión) tal cual al usuario — sin parsear campos.

## Cuándo usarla

- Una FK detectada por `create-technical-terms` apunta a un destino erróneo.
- La fase de creación se perdió una FK que debería existir (modo DISCOVERY).
- Una FK ya no aplica y debe eliminarse.
- Una ejecución de mantenimiento dirigida que no debe regenerar todo el término técnico (más barato que `create_technical_terms(regenerate=true)`).

## Dependencias

### Otras skills
- **Prerrequisito duro:** `create-technical-terms` — cada tabla que el usuario quiera refinar debe llevar ya un Business Term de tipo technical-data-model. La herramienta omite las tablas sin él con un aviso explícito.
- **Referencia (recomendada cargar antes):** `stratio-semantic-layer` — las reglas de las MCP de governance.

### Guías
- `stratio-semantic-layer-tools.md` — referencia completa de las MCP de governance, incluido el §11 Glossary Instruction Enrichment Workflow.

### MCPs
- **Governance (`gov`):** `refine_foreign_keys`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.

### Python
Ninguna — skill solo de prompt.

### Sistema
Ninguno.

## Assets incluidos
Ninguno.

## Notas

- **`user_instructions` es obligatorio.** La herramienta rechaza entrada vacía o solo con espacios — sin una instrucción concreta no hay refinado.
- **No es destructiva por defecto.** Una FK se elimina solo cuando la instrucción la nombra explícitamente o su tabla destino desapareció del dominio; las instrucciones genéricas preservan el estado actual.
- **El contenido añadido por el usuario se preserva entre refinados.** Cualquier contenido añadido al Término de Negocio fuera de la sección autogenerada de Relaciones de Clave Foránea — encabezados adicionales, prosa, listas, tablas — se mantiene intacto cuando el flujo de refinado reescribe la sección.
- **Las tablas sin Business Term se omiten.** Se le indica al usuario que ejecute `create_technical_terms` antes; no se hacen llamadas a LLM para esas tablas.
- **Idempotente.** Reejecutar la misma instrucción produce un diff vacío y ningún PUT.
- **Errores específicos del despliegue** (idioma de governance no soportado, permisos faltantes) los devuelve la herramienta tal cual y se presentan al usuario sin presuponer la causa.
