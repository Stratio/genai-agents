---
name: refine-semantic-foreign-keys
description: "Añade, modifica o elimina las relaciones de clave foránea entre vistas de negocio de un dominio de Stratio Governance. Úsala después de create-semantic-terms cuando el usuario quiera corregir destinos erróneos de FK, detectar FKs que la fase de creación no descubrió, o eliminar FKs que ya no aplican. Opera sobre cualquier vista con término de negocio semántico, independientemente de si está publicada. Acepta el nombre técnico (canónico) o la contraparte semántica del dominio en la entrada. Para FKs de tablas técnicas usa refine-foreign-keys."
argument-hint: "[dominio (opcional)]"
---

# Skill: Refinar Claves Foráneas Semánticas

Ediciones quirúrgicas sobre las relaciones de clave foránea entre vistas de negocio de un dominio. Hermana de `create-semantic-terms`, pero solo para mantenimiento de FKs — NO regenera los términos semánticos en sí.

## Herramientas MCP utilizadas

| Herramienta | Servidor | Propósito |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferida**. Busca dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Lista los dominios técnicos. `refresh=true` para saltar la caché |
| `list_technical_domain_concepts(domain)` | gov | Lista las vistas de negocio con estado de gobernanza, `has_sql_mapping` y **`has_semantic_terms`** — el predictor de vistas refinables |
| `refine_semantic_foreign_keys(domain, user_instructions, view_names?)` | gov | Añade, modifica o elimina relaciones de FK entre vistas. `domain` acepta el nombre técnico (canónico, recomendado) o la contraparte semántica — ambas funcionan. `user_instructions` es obligatorio. Devuelve un único campo `message` con un resumen en markdown en notación explícita `key=value`, p. ej. `fk_count=N, persist=<ok\|failed>, BT=<updated\|unchanged>, columns_enriched=N` por vista, más los totales por dominio y cualquier aviso de omisión |

**Reglas clave**: `domain_name` inmutable (valor exacto de `list_domains` o `search_domains`, preferiblemente el nombre técnico). `user_instructions` es obligatorio — la herramienta rechaza entrada vacía. Construye `user_instructions` mediante el Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11, `phase=semantic_terms`). La herramienta refina cualquier vista con término de negocio semántico **independientemente de si está publicada** — las vistas sin BT se omiten con un aviso claro (ejecuta `/create-semantic-terms` antes). La herramienta subyacente solo soporta EN y ES; otros idiomas devuelven un error que se reenvía tal cual.

## Flujo

### 1. Determinar el dominio

Si `$ARGUMENTS` contiene un nombre de dominio, normaliza y descubre el nombre técnico canónico:

- Si empieza por el prefijo `semantic_` → elimina el prefijo en cliente. La herramienta acepta ambas formas, pero el objetivo canónico de descubrimiento es el dominio técnico. Indica al usuario que estás usando el equivalente técnico — se aceptan ambas formas.
- Busca con `search_domains($ARGUMENTS, domain_type='technical')`. Si no coincide, reintenta con `refresh=true` por si es una colección recién creada. Si sigue sin coincidir, pregunta al usuario.

Si no hay argumento, lista los dominios técnicos con `list_domains(domain_type='technical')` y pregunta al usuario siguiendo la convención de preguntas.

El usuario puede pretender una operación distinta:

- Si quiere explícitamente refinar FKs entre **tablas técnicas** (no vistas semánticas), sugiérele `/refine-foreign-keys`. Esta skill NO enruta automáticamente — solo informa; el LLM del agente decide si carga la otra skill.

### 2. Evaluar el estado

Ejecuta `list_technical_domain_concepts(domain)` para obtener la lista de vistas de negocio con su estado de gobernanza, `has_sql_mapping` y **`has_semantic_terms`**. Este último flag es el predictor autoritativo de qué vistas se pueden refinar.

Presenta el resumen:
```
## Estado — [nombre_dominio]
| Vista | Estado | Mapping | Términos semánticos | Refinable |
|-------|--------|---------|---------------------|-----------|
| view_a | Draft | ✓ | ✓ | sí |
| view_b | Published | ✓ | ✓ | sí |
| view_c | Draft | ✓ | ✗ | no — ejecuta `/create-semantic-terms` antes |
```

Las vistas con `has_semantic_terms: true` son refinables **independientemente del estado de gobernanza** (Draft, Pending Publish o Published). Las vistas con `has_semantic_terms: false` se presentan aparte y quedan fuera del scope — redirige al usuario a `/create-semantic-terms` para esas.

### 3. Selección de scope

Pregunta al usuario con opciones (solo vistas con `has_semantic_terms: true`):
1. **Todas las vistas refinables** — omite `view_names`. La herramienta procesa todas las vistas con término de negocio semántico.
2. **Vistas específicas** — selección múltiple entre las candidatas refinables.

### 4. Intent de la instrucción

La herramienta requiere `user_instructions` (no vacío). Si el usuario no ha proporcionado una indicación concreta, pídela ahora. Dos intents productivos:

- **TARGETED** — el usuario nombra las relaciones a cambiar. Ejemplos:
  - *"Añade una clave foránea de orders.customer_id a customers.id"*
  - *"Borra la FK en shipments.carrier_id"*
  - *"Cambia el destino de la FK en orders.address_id a addresses.id"*

- **DISCOVERY** — el usuario pide detectar FKs que la fase de creación no descubrió. Activado por verbos de detección (detectar / encontrar / descubrir / buscar / detect / find / discover). Ejemplos:
  - *"Detecta las claves foráneas que faltan en orders y shipments"*
  - *"Encuentra cualquier relación que no se haya detectado para las vistas customers y addresses"*

Los dos intents pueden coexistir en una sola instrucción (p. ej. *"Detecta las FKs que falten y borra la FK en carrier_id"*).

Las frases genéricas tipo *"revisa"* o *"actualiza"* sin specifics ni lenguaje de detección no producen cambios. Advierte al usuario antes de invocar la herramienta con una entrada así — gasta un round-trip sin producir ninguna modificación.

### 5. Glossary instruction enrichment

Antes de invocar la herramienta MCP, aplica el Glossary Instruction Enrichment Workflow descrito en `guides/stratio-semantic-layer-tools.md` §11, con scope **semantic terms** (al llamar a `get_glossary_instructions`, solicita solo la fase `semantic_terms`).

Si el orquestador ya pre-cargó instrucciones enriquecidas para la fase de semantic-terms en una skill previa, reutilízalas; opcionalmente pregunta al usuario si quiere añadir algo específico por encima.

El texto enriquecido se concatena con el texto de intent del usuario del paso 4 y se convierte en el argumento `user_instructions` del paso 6.

### 6. Ejecución

Invoca `refine_semantic_foreign_keys(domain, user_instructions, view_names?)`. La herramienta devuelve un único campo `message` cuyo valor es un resumen en markdown ya estructurado con:

- totales por dominio: vistas procesadas, persistidas, fallbacks best-effort, omitidas o fallidas
- una lista por vista en notación explícita `key=value` (sin glifos de diff que interpretar):
  - `- **<vista>**: fk_count=N, persist=<ok|failed>, BT=<updated|unchanged>, columns_enriched=N`
  - `BT=unchanged` es un camino de éxito normal — significa que la sección FK renderizada era idéntica a la anterior y no se envió PUT.
  - Las vistas omitidas (vista no encontrada, Término de Negocio semántico no encontrado, etc.) se renderizan como `- **<vista>**: skipped — <razón>`.

Reenvía el markdown del `message` al usuario **tal cual** — no parafrasees, resumas ni reestructures. La chain redactó el texto a propósito para que la salida al usuario sea consistente entre ejecuciones e idiomas.

Si el markdown reporta `persist=failed` o avisos de omisión para algunas vistas, puedes añadir una sugerencia breve y neutra debajo del mensaje (p. ej. "Reintenta con una instrucción más específica para esas vistas, o revisa los permisos de governance para las que fallaron"), pero nunca edites el markdown en sí. `BT=unchanged` NO justifica ninguna sugerencia extra — es el resultado normal cuando ninguna relación necesitaba ajuste.

**Presenta también los errores tal cual**: la misma regla verbatim que aplica al markdown de éxito aplica a cualquier mensaje de error que devuelva la herramienta — no parafrasees, resumas ni sustituyas con tu propio texto. Los errores se redactan a propósito para que el usuario vea texto consistente y accionable en todas las tools de governance. Si la herramienta se detiene porque ninguna de las vistas solicitadas es refinable, el mensaje ya explica el motivo y redirige al usuario a `/create-semantic-terms` — reenvíalo tal cual.

## Notas

- La herramienta **nunca regenera el término semántico** de una vista; solo se re-renderizan la sección `### Relaciones de Clave Foránea` del Término de Negocio de la vista y los sufijos FK de las columnas origen afectadas.
- La herramienta **no es destructiva por defecto**: una FK se elimina solo cuando la instrucción lo dice explícitamente (o cuando la vista destino ya no existe en el dominio). Las instrucciones genéricas "revisa" preservan el estado actual.
- Una misma columna origen puede participar en varias relaciones FK (p. ej. en vistas tipo unión). Cuando ocurre, el Término de Negocio a nivel de columna recibe un sufijo FK por cada relación; la skill no necesita gestionar nada especial — lo hace la chain.
- **El contenido añadido por el usuario se preserva entre refinados**: cualquier contenido que el usuario haya añadido al Término de Negocio de una vista fuera de la sección autogenerada de `### Relaciones de Clave Foránea` — encabezados adicionales, prosa, listas, tablas — se mantiene intacto cuando el flujo de refinado reescribe la sección.
- **No se requiere publicación**: cualquier vista con término de negocio semántico se puede refinar, esté en Draft, Pending Publish o Published. La skill ya no pide al usuario que publique antes.
- **El formato del dominio es tolerante**: la herramienta acepta tanto el nombre técnico como la contraparte `semantic_*`. Los ejemplos de esta skill usan la forma técnica por descubrimiento y consistencia con el resto del pipeline de construcción.
- **Los nombres de entrada se normalizan**: los espacios al inicio o al final y los backticks envolventes en `view_names` se eliminan automáticamente. El usuario no necesita limpiar nombres copiados.
- Si el `governance_language` del despliegue no es compatible (es decir, no es EN o ES), la respuesta llevará un error explícito — preséntalo al usuario tal cual. No se espera que el usuario conozca la configuración del despliegue de antemano.
- **Las FKs entre tablas técnicas son una operación distinta**: esta skill gestiona relaciones FK entre **vistas semánticas**. Para FKs entre tablas físicas de un dominio técnico usa `/refine-foreign-keys`.
