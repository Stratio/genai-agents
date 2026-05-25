---
name: refine-semantic-foreign-keys
description: "Añade, modifica o elimina las relaciones de clave foránea entre vistas de negocio en un dominio semántico de Stratio Governance. Úsala después de create-semantic-terms cuando el usuario quiera corregir destinos erróneos de FK, detectar FKs que la fase de creación no descubrió, o eliminar FKs que ya no aplican. Solo opera sobre vistas con términos semánticos previamente generados; rechaza dominios técnicos y dirige al usuario a refine-foreign-keys."
argument-hint: "[dominio semántico (opcional)]"
---

# Skill: Refinar Claves Foráneas Semánticas

Ediciones quirúrgicas sobre las relaciones de clave foránea entre vistas de negocio en un dominio semántico. Hermana de `create-semantic-terms`, pero solo para mantenimiento de FKs — NO regenera los términos semánticos en sí.

## Herramientas MCP utilizadas

| Herramienta | Servidor | Propósito |
|------|--------|---------|
| `search_domains(search_text, domain_type='business')` | sql | **Preferida**. Busca dominios semánticos publicados por texto libre. Resultados por relevancia |
| `list_domains(domain_type='business', refresh?)` | sql | Lista todos los dominios semánticos publicados. `refresh=true` para saltar la caché |
| `list_domain_tables(domain)` | sql | Lista las vistas del dominio semántico publicado (funciona tanto para nombres técnicos como semánticos) |
| `refine_semantic_foreign_keys(domain, user_instructions, view_names?)` | gov | Añade, modifica o elimina relaciones de FK entre vistas. `domain` DEBE empezar por `semantic_` (los dominios técnicos se rechazan — usa `refine_foreign_keys`). `user_instructions` es obligatorio. Devuelve un único campo `message` con un resumen en markdown en notación explícita `key=value`, p. ej. `fk_count=N, persist=<ok\|failed>, BT=<updated\|unchanged>, columns_enriched=N` por vista, más los totales por dominio y cualquier aviso de omisión |

**Reglas clave**: `domain_name` inmutable (valor exacto de `list_domains` o `search_domains`). `user_instructions` es obligatorio — la herramienta rechaza entrada vacía. Construye `user_instructions` mediante el Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11, `phase=semantic_terms`). Las vistas sin un Término de Negocio semántico previo se omiten automáticamente — ejecuta `/create-semantic-terms` antes si es necesario. La herramienta subyacente solo soporta EN y ES; otros idiomas devuelven un error que se reenvía tal cual.

## Flujo

### 1. Determinar el dominio

Si `$ARGUMENTS` contiene un nombre de dominio:

- Si empieza explícitamente por `semantic_` → busca con `search_domains($ARGUMENTS, domain_type='business')`. Si coincide con un resultado, continúa. Si no coincide, reintenta con `refresh=true` por si es un dominio recién publicado. Si sigue sin coincidir, pregunta al usuario.
- Si es **ambiguo** (un nombre desnudo como `sakila` que podría ser tanto el dominio técnico como el prefijo del nombre técnico de `semantic_sakila`) → pregunta al usuario explícitamente si se refiere a las tablas técnicas (usar `/refine-foreign-keys`) o a las vistas semánticas publicadas (continuar aquí anteponiendo el prefijo `semantic_`). NO asumir; NO enrutar automáticamente.
- Si es **inequivocamente técnico** (sin prefijo `semantic_` y el usuario confirma que se refiere a tablas) → advierte al usuario que esta skill solo gestiona vistas semánticas y sugiere `/refine-foreign-keys`. La skill NO enruta automáticamente — solo informa; el LLM del agente decide si carga la otra skill.

Si no hay argumento, lista los dominios semánticos con `list_domains(domain_type='business')` y pregunta al usuario siguiendo la convención de preguntas.

Si la herramienta MCP subyacente rechaza la llamada porque el dominio no es semántico, presenta el error de la herramienta tal cual — el mensaje ya redirige al usuario a `refine_foreign_keys`.

### 2. Evaluar el estado

Ejecuta `list_domain_tables(domain)` para obtener la lista de vistas del dominio semántico publicado.

Presenta el resumen:
```
## Estado — [nombre_dominio]
- Total de vistas: N
```

En un dominio semántico publicado, todas las vistas listadas llevan un Término de Negocio semántico por construcción. Si la herramienta MCP devuelve un aviso de omisión para alguna vista (`**<vista>**: skipped — semantic business term not found` o similar), presenta el aviso tal cual y sugiere ejecutar `/create-semantic-terms` para las vistas que falten.

### 3. Selección de scope

Pregunta al usuario con opciones:
1. **Todas las vistas elegibles** — omite `view_names`. La herramienta procesa todas las vistas con un término semántico previo.
2. **Vistas específicas** — selección múltiple entre las candidatas.

### 4. Intent de la instrucción

La herramienta requiere `user_instructions` (no vacío). Si el usuario no ha proporcionado una indicación concreta, pídela ahora. Dos intents productivos:

- **TARGETED** — el usuario nombra las relaciones a cambiar. Ejemplos:
  - *"Añade una clave foránea de film_actor.film_id a film.film_id"*
  - *"Borra la FK en rental.staff_id"*
  - *"Cambia el destino de la FK en inventory.film_id a film.film_id"*

- **DISCOVERY** — el usuario pide detectar FKs que la fase de creación no descubrió. Activado por verbos de detección (detectar / encontrar / descubrir / buscar / detect / find / discover). Ejemplos:
  - *"Detecta las claves foráneas que faltan en film_actor e inventory"*
  - *"Encuentra cualquier relación que no se haya detectado para las vistas rental y payment"*

Los dos intents pueden coexistir en una sola instrucción (p. ej. *"Detecta las FKs que falten y borra la FK en staff_id"*).

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

## Notas

- La herramienta **nunca regenera el término semántico** de una vista; solo se re-renderizan la sección `### Relaciones de Clave Foránea` del Término de Negocio de la vista y los sufijos FK de las columnas origen afectadas.
- La herramienta **no es destructiva por defecto**: una FK se elimina solo cuando la instrucción lo dice explícitamente (o cuando la vista destino ya no existe en el dominio). Las instrucciones genéricas "revisa" preservan el estado actual.
- Una misma columna origen puede participar en varias relaciones FK (p. ej. en vistas tipo unión). Cuando ocurre, el Término de Negocio a nivel de columna recibe un sufijo FK por cada relación; la skill no necesita gestionar nada especial — lo hace la chain.
- **El contenido añadido por el usuario se preserva entre refinados**: cualquier contenido que el usuario haya añadido al Término de Negocio de una vista fuera de la sección autogenerada de `### Relaciones de Clave Foránea` — encabezados adicionales, prosa, listas, tablas — se mantiene intacto cuando el flujo de refinado reescribe la sección.
- Si el `governance_language` del despliegue no es compatible (es decir, no es EN o ES), la respuesta llevará un error explícito — preséntalo al usuario tal cual. No se espera que el usuario conozca la configuración del despliegue de antemano.
