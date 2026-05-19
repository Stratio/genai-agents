---
name: refine-foreign-keys
description: "Añade, modifica o elimina claves foráneas virtuales de tablas en un dominio técnico de Stratio Governance. Úsala después de create-technical-terms cuando el usuario quiera corregir destinos erróneos de FK, detectar FKs que la fase de creación no descubrió, o eliminar FKs que ya no aplican. Solo opera sobre tablas con términos técnicos previamente generados."
argument-hint: "[dominio técnico (opcional)]"
---

# Skill: Refinar Claves Foráneas

Ediciones quirúrgicas sobre las claves foráneas virtuales de las tablas de un dominio técnico. Hermana de `create-technical-terms`, pero solo para mantenimiento de FKs — NO regenera los términos técnicos en sí.

## Herramientas MCP utilizadas

| Herramienta | Servidor | Propósito |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Preferida**. Busca dominios técnicos por texto libre. Resultados por relevancia |
| `list_domains(domain_type='technical', refresh?)` | sql | Lista todos los dominios técnicos. `refresh=true` para saltar la caché |
| `list_domain_tables(domain)` | sql | Lista las tablas con sus descripciones (las tablas con descripción ya tienen términos técnicos — solo estas son candidatas para refinar) |
| `refine_foreign_keys(domain, user_instructions, table_names?)` | gov | Añade, modifica o elimina FKs virtuales. `user_instructions` es obligatorio. Devuelve un único campo `message` con un resumen en markdown en notación explícita `key=value`, p. ej. `added=N, replaced=N, deleted=N, kept=N; persist=<ok\|failed\|not_needed>, BT=<updated\|unchanged>` por tabla, más los totales por dominio y cualquier aviso de omisión |

**Reglas clave**: `domain_name` inmutable (valor exacto de `list_domains` o `search_domains`). `user_instructions` es obligatorio — la herramienta rechaza entrada vacía. Construye `user_instructions` mediante el Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11, `phase=technical_terms`). Las tablas sin un término técnico previo se omiten automáticamente — ejecuta `/create-technical-terms` antes si es necesario.

## Flujo

### 1. Determinar el dominio

Si `$ARGUMENTS` contiene un nombre de dominio, busca con `search_domains($ARGUMENTS, domain_type='technical')`. Si coincide con un resultado, continúa. Si no coincide, reintenta con `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` por si es una colección recién creada. Si ahora coincide, continúa. Si sigue sin coincidir o no hay argumento, lista dominios con `list_domains(domain_type='technical')` y pregunta al usuario siguiendo la convención de preguntas.

### 2. Evaluar el estado

Ejecuta `list_domain_tables(domain)` para evaluar las candidatas:
- Tablas con descripción → tienen términos técnicos; candidatas para refinar.
- Tablas sin descripción → aún no tienen TN; la herramienta las omitirá con un aviso. Informa al usuario y excluyelas del scope.

Presenta el resumen:
```
## Estado — [nombre_dominio]
- Total de tablas: N
- Con términos técnicos (candidatas a refinar): X
- Sin términos técnicos (se omitirán): Y
```

Si `Y > 0`, sugiere ejecutar `/create-technical-terms` para las pendientes antes.

### 3. Selección de scope

Pregunta al usuario con opciones:
1. **Todas las tablas elegibles** — omite `table_names`. La herramienta procesa todas las tablas con un término técnico previo.
2. **Tablas específicas** — selección múltiple entre las candidatas.

### 4. Intent de la instrucción

La herramienta requiere `user_instructions` (no vacío). Si el usuario no ha proporcionado una indicación concreta, pídela ahora. Dos intents productivos:

- **TARGETED** — el usuario nombra las relaciones a cambiar. Ejemplos:
  - *"Añade una clave foránea de orders.customer_id a customers.id"*
  - *"Borra fk_obsolete de order_csv"*
  - *"Cambia el destino de fk_district en client_csv a district_csv"*

- **DISCOVERY** — el usuario pide detectar FKs que la fase de creación no descubrió. Activado por verbos de detección (detectar / encontrar / descubrir / buscar / detect / find / discover). Ejemplos:
  - *"Detecta las claves foráneas que faltan en card_csv y disp_csv"*
  - *"Encuentra cualquier relación que no se haya detectado para las tablas loan y trans"*

Los dos intents pueden coexistir en una sola instrucción (p. ej. *"Detecta las FKs que falten y borra fk_old"*).

Las frases genéricas tipo *"revisa"* o *"actualiza"* sin specifics ni lenguaje de detección no producen cambios. Advierte al usuario antes de invocar la herramienta con una entrada así — gasta un round-trip sin producir ninguna modificación.

### 5. Glossary instruction enrichment

Antes de invocar la herramienta MCP, aplica el Glossary Instruction Enrichment Workflow descrito en `guides/stratio-semantic-layer-tools.md` §11, con scope **technical terms** (al llamar a `get_glossary_instructions`, solicita solo la fase `technical_terms`).

Si el orquestador ya pre-cargó instrucciones enriquecidas para la fase de technical-terms en una skill previa, reutilízalas; opcionalmente pregunta al usuario si quiere añadir algo específico por encima.

El texto enriquecido se concatena con el texto de intent del usuario del paso 4 y se convierte en el argumento `user_instructions` del paso 6.

### 6. Ejecución

Invoca `refine_foreign_keys(domain, user_instructions, table_names?)`. La herramienta devuelve un único campo `message` cuyo valor es un resumen en markdown ya estructurado con:

- totales por dominio: `Tables processed`, `Persisted with changes`, `No changes needed`, `Failures or skips`
- una lista `### Per-table outcome` en notación explícita `key=value` (sin glifos de diff que interpretar):
  - `- **<tabla>**: added=N, replaced=N, deleted=N, kept=N; persist=<ok|failed|not_needed>, BT=<updated|unchanged>`
  - `persist=not_needed` significa que el diff estaba vacío y no se envió PUT (es un camino de éxito, no un fallo).
  - Las tablas omitidas (tabla desconocida, sin data_asset_id, sin TN aún) se renderizan como `- **<tabla>**: skipped — warning: ...`.

Reenvía el markdown del `message` al usuario **tal cual** — no parafrasees, resumas ni reestructures. La chain redactó el texto a propósito para que la salida al usuario sea consistente entre ejecuciones e idiomas.

Si el markdown reporta `persist=failed` o avisos de omisión para algunas tablas, puedes añadir una sugerencia breve y neutra debajo del mensaje (p. ej. "Reintenta con una instrucción más específica para esas tablas, o revisa los permisos de governance para las que fallaron"), pero nunca edites el markdown en sí. `persist=not_needed` NO justifica ninguna sugerencia extra — es el resultado normal cuando ninguna relación necesitaba ajuste.

## Notas

- La herramienta **nunca regenera el término técnico** de una tabla; solo se re-renderizan la sección de Claves Foráneas y los párrafos de FK de las columnas origen afectadas.
- La herramienta **no es destructiva por defecto**: una FK se elimina solo cuando la instrucción lo dice explícitamente (o cuando la tabla destino ya no existe en el dominio). Las instrucciones genéricas "revisa" preservan el estado actual.
- **El contenido añadido por el usuario se preserva entre refinados**: cualquier contenido que el usuario haya añadido al Término de Negocio fuera de la sección autogenerada de Relaciones de Clave Foránea — encabezados adicionales, prosa, listas, tablas — se mantiene intacto cuando el flujo de refinado reescribe la sección.
- Si el `governance_language` del despliegue no es compatible con esta herramienta, la respuesta llevará un error explícito — preséntalo al usuario tal cual. No se espera que el usuario conozca la configuración del despliegue de antemano.
