# Guía de Uso de MCPs de Capa Semántica Stratio

> **Guía compañera.** Para polling de `task_id` y truncación de salidas grandes — ambos pueden ocurrir en cualquier tool MCP de las listadas más abajo, en el servidor `gov` o `sql` — ver `stratio-mcp-response-patterns.md`. Referencia rápida en §9.

## 1. Regla Fundamental

**El agente nunca modifica el modelo de datos directamente.** Opera a través de tools MCP de gobernanza que usan IA interna para generar contenido (descripciones, ontologías, mappings SQL, términos semánticos). El agente orquesta, planifica, valida y proporciona contexto — las tools hacen el trabajo de generación.

## 2. Herramientas MCP Disponibles

### Servidor `gov` (gobernanza)

| Categoría | Herramienta MCP | Propósito |
|-----------|----------------|-----------|
| **Ontología** | `search_ontologies(search_text)` | Buscar ontologías por texto libre (nombre o descripción). Resultados por relevancia. Usar cuando se conoce parte del nombre |
| | `list_ontologies` | Listar todas las ontologías existentes |
| | `get_ontology_info(name)` | Estructura de clases, data properties y relaciones de una ontología |
| | `create_ontology(domain, name, ontology_plan)` | Crear ontología nueva con plan en Markdown |
| | `update_ontology(domain, name, update_plan)` | Añadir clases nuevas a ontología existente |
| | `delete_ontology_classes(ontology_name, class_names)` | DESTRUCTIVO: borrar clases específicas (protegido por Published) |
| **Términos técnicos** | `create_technical_terms(domain, table_names?, user_instructions?, regenerate?)` | Generar descripciones de tablas y columnas. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| | `refine_foreign_keys(domain, user_instructions, table_names?)` | Añadir, modificar o eliminar claves foráneas virtuales de tablas existentes en un dominio técnico. `user_instructions` es OBLIGATORIO — describe qué añadir/modificar/eliminar (TARGETED, p. ej. "borra fk_x", "añade fk de orders.customer_id a customers.id") o pide detectar FKs que falten (DISCOVERY, p. ej. "detecta las FKs que falten en card_csv"); las frases genéricas ("revisa", "actualiza") no producen cambios. Las tablas sin un término técnico previo se omiten con un aviso. Idempotente: re-ejecutar la misma instrucción no produce cambios. Devuelve `per_table_results` con `fks_added` / `fks_replaced` / `fks_deleted` / `fks_kept` por tabla |
| **Vistas de negocio** | `create_business_views(domain, ontology, class_names?, regenerate?)` | Crear vistas + mappings. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| | `delete_business_views(domain, view_names)` | DESTRUCTIVO: borrar vistas específicas sin recrear (protegido por Published) |
| | `publish_business_views(domain, view_names?)` | Publicar vistas (Draft → Pending Publish). Sin `view_names`, publica todas. Devuelve `published`, `failed` (transicion no permitida) y `not_found`. Idempotente |
| **Mappings SQL** | `create_sql_mappings(domain, view_names?, user_instructions?)` | Crear o actualizar mappings SQL de vistas existentes. Devuelve `message` (resumen markdown) **y** `processed_views`: lista de BusinessViewSummary de las vistas realmente procesadas en esta llamada (excluye los nombres no encontrados), cada una con `sql_mapping` — la SQL del mapping recién generada, lista para validación con datos de muestra (`SELECT * FROM (<sql_mapping>) AS m LIMIT 5`) sin necesidad de una llamada adicional a `list_technical_domain_concepts` |
| **Términos semánticos** | `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | Generar términos semánticos. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| **Business terms** | `create_business_term(domain, name, description, type, related_assets)` | Crear business term en el diccionario con relaciones a activos |
| | `list_business_asset_types()` | Listar tipos de activos disponibles para business terms |
| **Colecciones** | `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | Crear colección de datos (dominio técnico) con tablas y paths. `collection_name` sin espacios (usar underscores). Refresca vista técnica automáticamente |
| **Instrucciones del glosario** | `get_glossary_instructions(domain, phases?, include_globals?)` | Leer del diccionario de datos los business terms tipados como instrucciones GenAI para un dominio técnico. Filtrable por `phases` (lista entre `ontology` / `mapping` / `technical_terms` / `semantic_terms`; por defecto las cuatro) y por `include_globals` para el tipo global cross-phase `GenAI Instructions`. Para cada fase, la respuesta incluye siempre el tipo primario de la fase más cualquier tipo adicional por fase que tenga configurado el profile (replica lo que la chain consume internamente). Devuelve una sección por tipo de glosario con el contenido Markdown crudo. Solo lectura. Ver §11 para el workflow al usuario |
| **Utilidad** | `list_technical_domain_concepts(domain)` | Listar vistas de negocio existentes con estado de gobernanza (Draft/Pending Publish/Published), booleano `has_sql_mapping`, la SQL real del mapping en `sql_mapping` (cuando existe — utilizable para validación con datos de muestra: `SELECT * FROM (<sql_mapping>) AS m LIMIT 5`), y `has_semantic_terms` |
| | `create_collection_description(domain, user_instructions?)` | Generar SOLO la descripción del dominio/colección (sin tocar tablas) |
| | `get_mcp_task_result(task_id)` | Obtener el resultado de una tool de larga duración que sigue ejecutándose en segundo plano en el servidor `gov` (ver §9 y `stratio-mcp-response-patterns.md` §1) |

### Servidor `sql` (exploración de dominios)

| Herramienta MCP | Propósito |
|----------------|-----------|
| `search_domains(search_text, domain_type?, refresh?)` | **Preferir sobre `list_domains`**. Buscar dominios por texto libre (nombre o descripción). Para dominios técnicos: `domain_type='technical'`. Para semánticos publicados: `domain_type='business'`. Resultados ordenados por relevancia. Usar cuando se conoce parte del nombre o tema |
| `list_domains(domain_type?, refresh?)` | Listar dominios disponibles. Para dominios técnicos: `domain_type='technical'` (incluye descripción si existe). Para semánticos publicados: `domain_type='business'` (prefijo `semantic_`). `refresh` (boolean, default false): bypass de cache — usar tras crear/eliminar colecciones o cuando un dominio recién publicado no aparezca. Usar solo cuando se necesita ver todos los dominios sin filtro |
| `list_domain_tables(domain)` | Listar tablas de un dominio con sus descripciones (indica si tienen términos técnicos) |
| `get_tables_details(domain, tables)` | Detalle de tablas: reglas de negocio, contexto |
| `get_table_columns_details(domain, table)` | Columnas de una tabla: nombres, tipos, descripciones de negocio |
| `search_domain_knowledge(question, domain)` | Buscar conocimiento en dominios técnicos y semánticos |
| `search_data_dictionary(search_text, search_type?)` | Buscar tablas y paths en el diccionario de datos técnico. `search_type`: `'tables'`, `'paths'` o `'both'` (defecto). Resultados ordenados por relevancia, con `metadata_path`, `name`, `subtype` (Table/Path), `alias`, `data_store`, `description` |
| `get_mcp_task_result(task_id)` | Obtener el resultado de una tool de larga duración que sigue ejecutándose en segundo plano en el servidor `sql` (ver §9 y `stratio-mcp-response-patterns.md` §1) |

## 3. Reglas Estrictas

- **INMUTABILIDAD de `domain_name`**: El parámetro `domain_name` en TODAS las llamadas MCP debe ser **exactamente** el valor devuelto por `list_domains` o `search_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo. Si el dominio se llama `AnaliticaBanca`, usar `"AnaliticaBanca"` — no `"Banca Particulares"`, no `"Analítica Banca"`, no `"banca"`. Si hay duda sobre el nombre exacto, volver a llamar a `search_domains` o `list_domains` para confirmarlo
- **Dominios técnicos para creación, publicación e instrucciones del glosario**: Las tools de creación (`create_technical_terms`, `create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms`), publicación (`publish_business_views`) y la tool de solo lectura `get_glossary_instructions` (que alimenta ese mismo pipeline) operan todas sobre **dominios técnicos**. Descubrirlos con `list_domains(domain_type='technical')` o `search_domains(texto, domain_type='technical')`. Dentro de este **pipeline de construcción**, los dominios semánticos (`semantic_*`) son el RESULTADO, no la entrada. Pasar un dominio `semantic_*` a `get_glossary_instructions` devuelve secciones vacías, porque las instrucciones GenAI están ligadas a la colección técnica. **Fuera del alcance de esta regla**: `create_business_term` es una operación **post-publicación**, no forma parte del pipeline de construcción — se ejecuta tras publicar la capa semántica y **prefiere `semantic_<x>`** por defecto. Ver la regla dedicada más abajo
- **Selección de dominio para business terms (post-publicación)**: `create_business_term` se invoca **después** de construir y publicar la capa semántica, para documentar conceptos de negocio (KPIs, métricas, entradas de glosario). Comportamiento por defecto:
  - **Preferir `semantic_<x>`** como `domain` siempre que exista. Esto archiva el término bajo "Semantic Knowledge" — el dominio padre que ven los consumidores de negocio
  - **Aplicar el mismo prefijo a todos los `related_assets`** — la chain rechaza prefijos mezclados
  - El **dominio técnico está plenamente soportado** para los edge cases legítimos: artefactos del modelo físico, dominios sin capa semántica publicada, o petición explícita del usuario. Es la excepción en el flujo por defecto, no una ruta prohibida
  - Ver la skill `manage-business-terms` para el procedimiento completo de discovery, las reglas de decisión y los ejemplos
  - **Alcance**: esta regla aplica **únicamente** a `create_business_term`. Las demás tools de gobernanza listadas en la regla del pipeline de construcción de arriba siguen requiriendo dominios técnicos
- **Dominios semánticos para exploración**: `list_domains(domain_type='business')`, `search_domains(texto, domain_type='business')` y `search_domain_knowledge` permiten explorar capas semánticas ya publicadas
- **`user_instructions` construido mediante el workflow de enriquecimiento**: Para las cuatro tools de fase que aceptan `user_instructions` (`create_technical_terms`, `create_sql_mappings`, `create_semantic_terms`, y análogamente el paso de planificación de `create_ontology` / `update_ontology` aunque ahí el texto se incorpore al plan Markdown), construir el valor mediante el Workflow de Enriquecimiento con Instrucciones del Glosario descrito en §11. Ese workflow consolida instrucciones del glosario, ficheros externos opcionales (.owl/.ttl, documentos de negocio, CSVs, etc.) y reglas en texto libre en un único texto. **Nunca inyectar contenido del glosario silenciosamente** sin pasar por la pregunta al usuario de §11.2 — el usuario debe ver y poder modificar lo que se va a aplicar. El enriquecimiento no es bloqueante: la opción 4 (saltar) está siempre disponible. **No sugerir opciones que la tool controla internamente** (idioma, formato de salida). Para `create_collection_description`, que no tiene un tipo específico de glossary item por fase, simplemente ofrecer `user_instructions` en texto libre directamente (queda intencionadamente fuera de §11). Para `refine_foreign_keys`, `user_instructions` es OBLIGATORIO (la tool rechaza entrada vacía) — el workflow de enriquecimiento se ejecuta con scope a `phase=technical_terms` y el intent concreto de refinado del usuario (TARGETED o DISCOVERY) se concatena por encima del texto enriquecido antes de invocar la tool
- **Operaciones destructivas (`regenerate=true`, `delete_*`)**: SIEMPRE confirmación explícita del usuario con advertencia clara de que se pierde. Patrón: detectar existencia → informar que se pierde → preguntar (saltar/ejecutar/cancelar) → confirmación adicional para la acción destructiva
- **Publicación de vistas (`publish_business_views`)**: Confirmar con el usuario listando las vistas que se van a publicar. Verificar estado previo con `list_technical_domain_concepts`. No es destructiva ni requiere confirmación de tipo "destructiva", pero es un cambio de estado de gobernanza que el usuario debe aprobar. Presentar resultado: vistas publicadas + fallidas + no encontradas
- **Ontologías son ADD+DELETE**: `update_ontology` añade clases nuevas. `delete_ontology_classes` borra clases específicas (protegido: clases con vistas Published dependientes se saltan automáticamente). No se pueden modificar clases existentes
- **Nomenclatura de ontologías**: Sin espacios (usar guiones bajos), sin caracteres especiales
- **Nomenclatura de colecciones**: Sin espacios (usar guiones bajos), sin caracteres especiales — misma convención que ontologías

## 4. Workflow de Descubrimiento de Dominio Técnico

Pasos para explorar un dominio técnico antes de construir su capa semántica.

### 4.1 Descubrir Dominios Técnicos

**Preferir buscar sobre listar** — `search_domains` devuelve resultados relevantes sin cargar la lista completa (que puede ser muy extensa).

Si el usuario proporciona un dominio o da pistas sobre el tema:
- Ejecutar `search_domains(nombre_o_pista, domain_type='technical')` para buscar coincidencias
- Si coincide con un resultado → usarlo directamente e ir al paso 4.2
- Si no hay coincidencias → ejecutar `list_domains(domain_type='technical')` como fallback y preguntar al usuario

Si no hay dominio claro, preguntar al usuario cuál le interesa. Si el usuario no da pistas, ejecutar `list_domains(domain_type='technical')` para mostrar todos los dominios técnicos disponibles (presentar como opciones seleccionables).

Si el usuario indica que acaba de crear una colección y el dominio no aparece, reintentar con `refresh=true` (bypass de cache) antes de concluir que no existe.

### 4.2 Explorar Tablas

`list_domain_tables(domain)` para listar todas las tablas del dominio. Las tablas con descripción ya tienen términos técnicos generados.

### 4.3 Detalle de Tablas

Para las tablas de interés:
1. `get_tables_details(domain, table_names)` para obtener reglas de negocio y contexto
2. `get_table_columns_details(domain, table)` para columnas, tipos y descripciones

Lanzar 4.3 en paralelo cuando sean sobre tablas independientes.

### 4.4 Conocimiento Existente

- `list_technical_domain_concepts(domain)` → vistas de negocio existentes con estado de mappings y términos semánticos, además de la SQL real del mapping en `sql_mapping` cuando está definida (utilizable para validación con datos de muestra previa a la publicación contra el MCP de datos)
- `search_ontologies(texto)` o `list_ontologies` + `get_ontology_info` → ontologías existentes y su estructura. Preferir `search_ontologies` si se busca una ontología concreta
- `search_domain_knowledge(question, domain)` → buscar terminología y definiciones

## 5. Exploración de Capas Semánticas Publicadas

Cuando una capa semántica generada se aprueba en la UI de Stratio Governance, se publica como un nuevo dominio de negocio con prefijo `semantic_` (ej: `semantic_mi_dominio`).

- `search_domains(texto, domain_type='business')` → **preferir**: buscar dominios semánticos publicados por nombre o descripción
- `list_domains(domain_type='business')` → listar todos los dominios semánticos publicados (fallback si search no da resultados). Si un dominio recién publicado no aparece, reintentar con `refresh=true`
- `list_domain_tables(domain)` → tablas del dominio semántico publicado
- `search_domain_knowledge(question, domain)` → buscar conocimiento en dominio técnico o semántico

Útil para: planificación de ontologías (ver que se ha hecho antes), verificar resultado final, ayudar al usuario a entender el estado actual.

## 6. Detección de Estado (Idempotencia)

Antes de cualquier operación, verificar que no exista ya:

| Artefacto | Cómo detectar | Si ya existe |
|-----------|--------------|-------------|
| Colección de datos | `list_domains(domain_type='technical')` o `search_domains(nombre, domain_type='technical')` → verificar si el dominio ya existe. Si se acaba de crear y no aparece, usar `refresh=true` | Si ya existe, informar. Opciones: usar existente / crear nueva con otro nombre |
| Términos técnicos | `list_domain_tables(domain)` → tablas con descripción | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |
| Descripción de dominio | `list_domains(domain_type='technical')` → si el dominio tiene descripción | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |
| Ontología | `search_ontologies(nombre)` o `list_ontologies` + `get_ontology_info` | Opciones: ampliar (`update_ontology`) / borrar clases (`delete_ontology_classes`) / crear nueva |
| Vistas de negocio | `list_technical_domain_concepts(domain)` | Informar vistas existentes. Opciones: saltar / borrar específicas (`delete_business_views`) / regenerar (`create_business_views(regenerate=true)`) |
| Publicación de vistas | `list_technical_domain_concepts(domain)` → estado de cada vista | Si ya Pending Publish o Published, informar. Solo las vistas en Draft se pueden publicar |
| SQL Mappings | `list_technical_domain_concepts(domain)` → estado de mapping por vista + `sql_mapping` del mapping cuando existe | `create_sql_mappings` sobrescribe mappings existentes. Usar `sql_mapping` para validación de datos pre-publicación (ver §4 de `stratio-data-tools.md`) |
| Términos semánticos | `list_technical_domain_concepts(domain)` → estado de términos por vista | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |

> Cuando cualquiera de las tools `search_*` anteriores no esté disponible (no vacía, sino fallando), sustituir según §10 y continuar.

## 7. Manejo de Errores y Recuperación

- Analizar el error → intentar diagnosticar la causa
- Si el agente puede resolverlo → reintentar con `user_instructions` mejoradas (reformular, añadir contexto específico)
- Si no puede → preguntar al usuario qué contexto adicional aportar → pasarlo como `user_instructions` en el reintento
- Reintentar SOLO la entidad fallida (tabla, clase, vista específica), no todo el lote
- Máximo 2 reintentos por entidad. Si persiste → documentar en resumen y continuar con las demás

## 8. Ejecución en Paralelo

- **Tools de lectura** (`list_*`, `get_*`, `search_*`): Lanzar en paralelo siempre que sean independientes
- **Creación**: Secuencial dentro de una misma fase
- **Entre fases**: Secuencia estricta obligatoria: términos técnicos → ontología → vistas de negocio → mappings SQL → (publicación opcional) → términos semánticos. Cada fase depende de los artefactos de la anterior. La publicación puede hacerse tras completar mappings o en cualquier momento posterior

## 9. Patrones de Respuesta del MCP

Dos patrones de respuesta pueden ocurrir en **cualquier** tool MCP de las listadas en §2, en el servidor `gov` o `sql`. Los protocolos están en `stratio-mcp-response-patterns.md` — aplicarlos siempre que aparezca el disparador. Para el polling, llamar siempre a `get_mcp_task_result` en el **mismo servidor** que la tool original. En `status="error"`, aplicar la estrategia de recuperación de §7.

| Disparador | Sección compañera |
|------------|-------------------|
| La respuesta contiene únicamente un campo `task_id` (sin datos, sin error) | `stratio-mcp-response-patterns.md` §1 — Polling de Tareas de Larga Duración |
| La respuesta sustituida por un aviso de truncación + ruta de fichero guardado, sin `task_id` | `stratio-mcp-response-patterns.md` §2 — Salidas de Tools de Gran Tamaño Truncadas |

## 10. Fallback por Indisponibilidad de OpenSearch

`search_domains`, `search_ontologies` y `search_data_dictionary` consultan OpenSearch internamente. OpenSearch puede no estar disponible en todos los entornos. Esta sección define el fallback cuando cualquiera de estas tools no está disponible — distinto del fallback por *resultado vacío* ya descrito en §4.1 y §5.

### 10.1 Detección del caso

| Situación | Indicador | Ruta de fallback |
|-----------|-----------|------------------|
| Resultado vacío (ya documentado) | La tool devuelve una respuesta bien formada con cero coincidencias | §4.1 / §5 — llamar al `list_*` correspondiente y preguntar al usuario |
| Indisponibilidad (nuevo) | Respuesta de error que menciona OpenSearch / index / connection / timeout, **o** dos reintentos sucesivos según §7 siguen fallando (no un `task_id` pendiente según §9) | §10.2 |

### 10.2 Fallback determinístico

| Tool OpenSearch | Alternativa determinística | Cobertura |
|-----------------|----------------------------|-----------|
| `search_domains(search_text, domain_type?)` | `list_domains(domain_type?)` + filtro local de substring sobre `name` y `description` | Completa |
| `search_ontologies(search_text)` | `list_ontologies()` + filtro local de substring sobre `name` y `description` | Completa |
| `search_data_dictionary(search_text, search_type?)` | Con hint de dominio: `list_domain_tables(domain)` + `get_tables_details(domain, tables)`. Sin hint de dominio: `list_domains(domain_type='technical')` → pedir al usuario que elija uno → continuar | Parcial — sin búsqueda cross-domain free-text sin OpenSearch |

### 10.3 Procedimiento

1. Al detectarse la indisponibilidad por primera vez en la sesión, avisar al usuario una sola vez — por tool, no por llamada.
2. Invocar la alternativa determinística.
3. Continuar el workflow (non-blocking). Las comprobaciones de detección de estado de §6 siguen aplicando: si se usa `search_ontologies(name)` para idempotencia, sustituir por `list_ontologies` + filtro local. El presupuesto de reintentos de §7 se agota antes de declarar indisponibilidad.
4. Parar únicamente si la alternativa no cubre la necesidad del usuario — típicamente `search_data_dictionary` sin hint de dominio cuando el usuario no puede acotar el alcance. En ese caso, informar al usuario y detener la sub-tarea.
5. Registrar la degradación en el resumen al final de la fase.

## 11. Workflow de Enriquecimiento con Instrucciones del Glosario

Algunos dominios técnicos llevan **instrucciones GenAI** que los stewards de datos definen en la UI de Stratio Governance como business terms tipados en el diccionario de datos. Esas instrucciones guían cómo el LLM genera la ontología, los mappings SQL, los términos técnicos y los términos semánticos para ese dominio. Tienen dos alcances:

- **Globales** — aplican a todas las fases (tipo por defecto: `GenAI Instructions`).
- **Específicas por fase** — un tipo por cada fase: `GenAI Ontology Instructions`, `GenAI Mapping Instructions`, `GenAI Technical Term Instructions`, `GenAI Semantic Term Instructions`. Un profile puede además configurar tipos globales adicionales por fase.

Históricamente estas instrucciones se consumían de forma implícita dentro de la chain. La tool `get_glossary_instructions` las expone para que el agente pueda mostrárselas al usuario, discutirlas, mezclarlas con un fichero externo o saltarlas — *antes* de invocar cualquier tool de creación que acepte `user_instructions`.

### 11.1 Cuándo aplicar

- En cualquier skill de fase que vaya a invocar `create_technical_terms`, `create_ontology` / `update_ontology`, `create_sql_mappings` o `create_semantic_terms` — **justo antes** del step actual de `user_instructions`.
- Una sola vez al principio de un pipeline completo dirigido por `build-semantic-layer`, cubriendo todas las fases incluidas en el plan propuesto; las sub-skills reutilizan el texto enriquecido por fase sin volver a preguntar.

`create_collection_description` queda intencionadamente **fuera** de este workflow: no tiene un tipo específico de glossary item asociado, así que el agente simplemente ofrece `user_instructions` en texto libre directamente al invocarlo.

### 11.2 Pregunta al usuario

Siguiendo la convención de preguntas del agente, presentar estas cuatro opciones mutuamente excluyentes:

1. Usar solo las instrucciones del glosario **específicas** de esta fase.
2. Usar **específicas + globales** del glosario.
3. Aportar un **fichero externo** (ruta local) en lugar de (o además de) el glosario.
4. **Saltar** — continuar sin enriquecimiento.

Cuando el workflow se ejecuta desde `build-semantic-layer`, plantear la pregunta para "las fases incluidas en el plan propuesto" y tratar la respuesta del usuario como política para todas; ofrecer override por fase solo si el usuario lo pide explícitamente.

### 11.3 Lectura desde el glosario (opciones 1 y 2)

Invocar `get_glossary_instructions` para el dominio actual y la(s) fase(s) relevante(s):

- `domain` — **siempre el dominio técnico** que alimenta el pipeline. Las cuatro tools de fase (`create_technical_terms`, `create_ontology`, `create_sql_mappings`, `create_semantic_terms`) operan sobre la colección técnica, y `get_glossary_instructions` igual. Pasar un dominio `semantic_*` devuelve secciones vacías porque las instrucciones GenAI no se guardan en el dominio semántico publicado.
- `phases` — la fase actual si se invoca desde una skill de fase, o la lista de fases incluidas en el plan cuando se invoca desde `build-semantic-layer`.
- `include_globals` — elegir según la opción que escoja el usuario:
  - **Opción 1 (solo específicas)**: `include_globals=false`. Devuelve solo los tipos específicos de cada fase pedida (primario + cualquier tipo adicional por fase configurado en el profile).
  - **Opción 2 (específicas + globales)**: `include_globals=true`. Igual que la opción 1 más el tipo global cross-phase `GenAI Instructions`.

Mostrar al usuario un resumen compacto del retorno (una entrada por sección `(glossary_type, scope)`, conteo de items o preview del contenido bajo demanda). Preguntarle si quiere:

- aceptarlo todo tal cual,
- excluir items concretos de alguna sección,
- añadir comentarios propios en texto libre por encima.

Si la respuesta trae `error` o todas las secciones vienen vacías, informar al usuario y ofrecer caer a la opción 3 o 4.

### 11.4 Lectura desde fichero externo (opción 3)

Pedir una ruta local. Leer el fichero con la skill adecuada: Markdown / TXT directamente, DOCX vía `/docx-reader`, PPTX vía `/pptx-reader`, PDF vía `/pdf-reader`. Extraer el texto relevante; no inventar contenido que no esté en el fichero.

La opción 3 puede combinarse con las opciones 1 o 2 si el usuario quiere superponer ambas fuentes.

### 11.5 Consolidación

Combinar las fuentes elegidas en un único texto Markdown con encabezados explícitos: una sección para las instrucciones globales del glosario, una sección por tipo específico de fase, una sección para el contenido del fichero externo y una sección para los comentarios libres del usuario. Las secciones vacías pueden omitirse.

Cómo se consume el texto consolidado depende de la tool MCP destino:

- Para `create_technical_terms`, `create_sql_mappings`, `create_semantic_terms`: pasarlo directamente como argumento `user_instructions`.
- Para `create_ontology` / `update_ontology`: esas tools **no** aceptan `user_instructions` hoy. El texto consolidado se incorpora al `ontology_plan` / `update_plan` Markdown que el agente prepara antes de invocar la tool — orienta propuestas de clases, convenciones de nomenclatura, relaciones, etc. Si una versión futura de la tool empieza a aceptar `user_instructions`, ese mismo texto se pasará también a la llamada.

### 11.6 Reutilización del pre-load del orquestador

Cuando `build-semantic-layer` ya ha ejecutado este workflow al inicio del pipeline, el texto enriquecido por fase forma parte del contexto de planificación de la ejecución. Las sub-skills de fase deben:

1. Detectar que ya hay enriquecimiento pre-cargado para su fase y reutilizarlo como `user_instructions` sin volver a hacer las cuatro preguntas.
2. Opcionalmente preguntar al usuario una sola pregunta corta — si quiere añadir algo específico para esta fase encima del enriquecimiento ya cargado — y anexar la respuesta al texto consolidado si la hay.

Si una skill de fase se invoca **fuera** del orquestador (petición directa del usuario), ejecuta §11.2–§11.5 por su cuenta.

### 11.7 Sin enriquecimiento silencioso

Nunca invocar `get_glossary_instructions` e inyectar el resultado como `user_instructions` sin pasar por §11.2 (o el equivalente del orquestador). El sentido del workflow es que el usuario vea y pueda dar forma a lo que se va a aplicar.
