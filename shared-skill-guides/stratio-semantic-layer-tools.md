# Guia de Uso de MCPs de Capa Semantica Stratio

## 1. Regla Fundamental

**El agente nunca modifica el modelo de datos directamente.** Opera a traves de tools MCP de gobernanza que usan IA interna para generar contenido (descripciones, ontologias, mappings SQL, terminos semanticos). El agente orquesta, planifica, valida y proporciona contexto — las tools hacen el trabajo de generacion.

## 2. Herramientas MCP Disponibles

### Servidor `gov` (gobernanza)

| Categoria | Herramienta MCP | Proposito |
|-----------|----------------|-----------|
| **Ontologia** | `stratio_list_ontologies` | Listar ontologias existentes |
| | `stratio_get_ontology_info(name)` | Estructura de clases, data properties y relaciones de una ontologia |
| | `stratio_create_ontology(domain, name, ontology_plan)` | Crear ontologia nueva con plan en Markdown |
| | `stratio_update_ontology(domain, name, update_plan)` | Anadir clases nuevas a ontologia existente |
| | `stratio_delete_ontology_classes(ontology_name, class_names)` | DESTRUCTIVO: borrar clases especificas (protegido por Published) |
| **Terminos tecnicos** | `stratio_create_technical_terms(domain, table_names?, user_instructions?, regenerate?)` | Generar descripciones de tablas y columnas. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| **Vistas de negocio** | `stratio_create_business_views(domain, ontology, class_names?, regenerate?)` | Crear vistas + mappings. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| | `stratio_delete_business_views(domain, view_names)` | DESTRUCTIVO: borrar vistas especificas sin recrear (protegido por Published) |
| **Mappings SQL** | `stratio_create_sql_mappings(domain, view_names?, user_instructions?)` | Crear o actualizar mappings SQL de vistas existentes |
| **Terminos semanticos** | `stratio_create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | Generar terminos semanticos. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| **Business terms** | `stratio_create_business_term(domain, name, description, type, related_assets)` | Crear business term en el diccionario con relaciones a activos |
| | `stratio_list_business_asset_types()` | Listar tipos de activos disponibles para business terms |
| **Colecciones** | `stratio_create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | Crear coleccion de datos (dominio tecnico) con tablas y paths. `collection_name` sin espacios (usar underscores). Refresca vista tecnica automaticamente |
| **Utilidad** | `stratio_list_technical_domain_concepts(domain)` | Listar vistas de negocio existentes con estado de mappings y terminos semanticos |
| | `stratio_create_collection_description(domain, user_instructions?)` | Generar SOLO la descripcion del dominio/coleccion (sin tocar tablas) |

### Servidor `sql` (exploracion de dominios)

| Herramienta MCP | Proposito |
|----------------|-----------|
| `stratio_list_technical_domains` | Descubrir dominios tecnicos disponibles (incluye descripcion si existe) |
| `stratio_list_domain_tables(domain)` | Listar tablas de un dominio con sus descripciones (indica si tienen terminos tecnicos) |
| `stratio_get_tables_details(domain, tables)` | Detalle de tablas: reglas de negocio, contexto |
| `stratio_get_table_columns_details(domain, table)` | Columnas de una tabla: nombres, tipos, descripciones de negocio |
| `stratio_list_business_domains` | Listar dominios semanticos publicados (prefijo `semantic_`) |
| `stratio_search_domain_knowledge(question, domain)` | Buscar conocimiento en dominios tecnicos y semanticos |
| `stratio_search_data_dictionary(search_text, search_type?)` | Buscar tablas y paths en el diccionario de datos tecnico. `search_type`: `'tables'`, `'paths'` o `'both'` (defecto). Resultados ordenados por relevancia, con `metadata_path`, `name`, `subtype` (Table/Path), `alias`, `data_store`, `description` |

## 3. Reglas Estrictas

- **INMUTABILIDAD de `domain_name`**: El parametro `domain_name` en TODAS las llamadas MCP debe ser **exactamente** el valor devuelto por `stratio_list_technical_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo. Si el dominio se llama `AnaliticaBanca`, usar `"AnaliticaBanca"` — no `"Banca Particulares"`, no `"Analítica Banca"`, no `"banca"`. Si hay duda sobre el nombre exacto, volver a llamar a `stratio_list_technical_domains` para confirmarlo
- **Dominios tecnicos para creacion**: Las tools de creacion (`stratio_create_technical_terms`, `stratio_create_ontology`, `stratio_create_business_views`, `stratio_create_sql_mappings`, `stratio_create_semantic_terms`) usan dominios tecnicos. Los dominios semanticos (`semantic_*`) son el RESULTADO del proceso, no la entrada
- **Dominios semanticos para exploracion**: `stratio_list_business_domains` y `stratio_search_domain_knowledge` permiten explorar capas semanticas ya publicadas
- **`user_instructions` siempre ofrecido**: Antes de invocar cualquier tool que acepte `user_instructions`, ofrecer al usuario la oportunidad de aportar contexto adicional. El agente puede **leer ficheros locales** del usuario (documentacion, glosarios, especificaciones, CSVs, ontologias .owl/.ttl) para extraer informacion relevante y pasarla como contexto. Preguntar si tiene ficheros o contexto de dominio que quiera aportar. No es bloqueante — si el usuario no aporta, continuar sin el parametro. **No sugerir opciones que la tool controla internamente** (idioma, formato de salida) — centrarse en contexto de dominio, definiciones de negocio y reglas especificas
- **Operaciones destructivas (`regenerate=true`, `delete_*`)**: SIEMPRE confirmacion explicita del usuario con advertencia clara de que se pierde. Patron: detectar existencia → informar que se pierde → preguntar (saltar/ejecutar/cancelar) → confirmacion adicional para la accion destructiva
- **Ontologias son ADD+DELETE**: `stratio_update_ontology` anade clases nuevas. `stratio_delete_ontology_classes` borra clases especificas (protegido: clases con vistas Published dependientes se saltan automaticamente). No se pueden modificar clases existentes
- **Nomenclatura de ontologias**: Sin espacios (usar guiones bajos), sin caracteres especiales
- **Nomenclatura de colecciones**: Sin espacios (usar guiones bajos), sin caracteres especiales — misma convencion que ontologias

## 4. Workflow de Descubrimiento de Dominio Tecnico

Pasos para explorar un dominio tecnico antes de construir su capa semantica.

### 4.1 Listar Dominios

Ejecutar `stratio_list_technical_domains` para mostrar todos los dominios tecnicos disponibles con sus nombres y descripciones.

Si el usuario proporciona un dominio:
- Si coincide con un dominio conocido, ir directamente al paso 4.2
- Si no coincide, preguntar al usuario cual dominio explorar mostrando la lista

Si no hay dominio claro, preguntar al usuario cual le interesa (presentar dominios como opciones seleccionables).

### 4.2 Explorar Tablas

`stratio_list_domain_tables(domain)` para listar todas las tablas del dominio. Las tablas con descripcion ya tienen terminos tecnicos generados.

### 4.3 Detalle de Tablas

Para las tablas de interes:
1. `stratio_get_tables_details(domain, table_names)` para obtener reglas de negocio y contexto
2. `stratio_get_table_columns_details(domain, table)` para columnas, tipos y descripciones

Lanzar 4.3 en paralelo cuando sean sobre tablas independientes.

### 4.4 Conocimiento Existente

- `stratio_list_technical_domain_concepts(domain)` → vistas de negocio existentes con estado de mappings y terminos semanticos
- `stratio_list_ontologies` + `stratio_get_ontology_info` → ontologias existentes y su estructura
- `stratio_search_domain_knowledge(question, domain)` → buscar terminologia y definiciones

## 5. Exploracion de Capas Semanticas Publicadas

Cuando una capa semantica generada se aprueba en la UI de Stratio Governance, se publica como un nuevo dominio de negocio con prefijo `semantic_` (ej: `semantic_mi_dominio`).

- `stratio_list_business_domains` → buscar dominios con prefijo `semantic_`
- `stratio_list_domain_tables(domain)` → tablas del dominio semantico publicado
- `stratio_search_domain_knowledge(question, domain)` → buscar conocimiento en dominio tecnico o semantico

Util para: planificacion de ontologias (ver que se ha hecho antes), verificar resultado final, ayudar al usuario a entender el estado actual.

## 6. Deteccion de Estado (Idempotencia)

Antes de cualquier operacion, verificar que no exista ya:

| Artefacto | Como detectar | Si ya existe |
|-----------|--------------|-------------|
| Coleccion de datos | `stratio_list_technical_domains` → verificar si el dominio ya existe | Si ya existe, informar. Opciones: usar existente / crear nueva con otro nombre |
| Terminos tecnicos | `stratio_list_domain_tables(domain)` → tablas con descripcion | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |
| Descripcion de dominio | `stratio_list_technical_domains` → si el dominio tiene descripcion | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |
| Ontologia | `stratio_list_ontologies` + `stratio_get_ontology_info` | Opciones: ampliar (`update_ontology`) / borrar clases (`delete_ontology_classes`) / crear nueva |
| Vistas de negocio | `stratio_list_technical_domain_concepts(domain)` | Informar vistas existentes. Opciones: saltar / borrar especificas (`delete_business_views`) / regenerar (`create_business_views(regenerate=true)`) |
| SQL Mappings | `stratio_list_technical_domain_concepts(domain)` → estado de mapping por vista | `stratio_create_sql_mappings` sobrescribe mappings existentes |
| Terminos semanticos | `stratio_list_technical_domain_concepts(domain)` → estado de terminos por vista | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |

## 7. Manejo de Errores y Recuperacion

- Analizar el error → intentar diagnosticar la causa
- Si el agente puede resolverlo → reintentar con `user_instructions` mejoradas (reformular, anadir contexto especifico)
- Si no puede → preguntar al usuario que contexto adicional aportar → pasarlo como `user_instructions` en el reintento
- Reintentar SOLO la entidad fallida (tabla, clase, vista especifica), no todo el lote
- Maximo 2 reintentos por entidad. Si persiste → documentar en resumen y continuar con las demas

## 8. Ejecucion en Paralelo

- **Tools de lectura** (`list_*`, `get_*`, `search_*`): Lanzar en paralelo siempre que sean independientes
- **Creacion**: Secuencial dentro de una misma fase
- **Entre fases**: Secuencia estricta obligatoria: terminos tecnicos → ontologia → vistas de negocio → mappings SQL → terminos semanticos. Cada fase depende de los artefactos de la anterior
