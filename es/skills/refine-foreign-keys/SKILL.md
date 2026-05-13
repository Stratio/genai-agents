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
| `refine_foreign_keys(domain, user_instructions, table_names?)` | gov | Añade, modifica o elimina FKs virtuales. `user_instructions` es obligatorio. Devuelve `per_table_results` con `fks_added` / `fks_replaced` / `fks_deleted` / `fks_kept` por tabla |

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

Invoca `refine_foreign_keys(domain, user_instructions, table_names?)`. La herramienta devuelve:

- `message`: resumen breve en markdown.
- `per_table_results`: lista con `table_name`, `fks_added`, `fks_kept`, `fks_replaced`, `fks_deleted`, `persist_succeeded`, `bt_updated` y `warning` opcional.

Presenta el resultado por tabla directamente:
- Tablas modificadas — lista de `fks_added` / `fks_replaced` / `fks_deleted`, y confirma `bt_updated`.
- Tablas sin cambios — "ninguna FK coincidía con la petición" o "el estado actual ya está alineado".
- Tablas omitidas — muestra el aviso (aún sin TN, sin data_asset_id, etc.).
- Tablas con fallos de persistencia — muestra la cola del error (probablemente permisos o problema de backend); el TN se dejó intacto a propósito para no mostrar un estado distinto al de la API.

Si una tabla falla por una razón recuperable (p. ej. un nombre de columna inválido en la FK propuesta), sugiere reintentar con una instrucción más específica; el actor reintenta internamente hasta su presupuesto de intentos.

## Notas

- La herramienta **nunca regenera el término técnico** de una tabla; solo se re-renderizan la sección de Claves Foráneas y los párrafos de FK de las columnas origen afectadas.
- La herramienta **no es destructiva por defecto**: una FK se elimina solo cuando la instrucción lo dice explícitamente (o cuando la tabla destino ya no existe en el dominio). Las instrucciones genéricas "revisa" preservan el estado actual.
- Si el `governance_language` del despliegue no es compatible con esta herramienta, la respuesta llevará un error explícito — preséntalo al usuario tal cual. No se espera que el usuario conozca la configuración del despliegue de antemano.
