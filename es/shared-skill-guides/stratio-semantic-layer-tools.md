# Guía de Uso de MCPs de Capa Semántica Stratio

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
| **Vistas de negocio** | `create_business_views(domain, ontology, class_names?, regenerate?)` | Crear vistas + mappings. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| | `delete_business_views(domain, view_names)` | DESTRUCTIVO: borrar vistas específicas sin recrear (protegido por Published) |
| | `publish_business_views(domain, view_names?)` | Publicar vistas (Draft → Pending Publish). Sin `view_names`, publica todas. Devuelve `published`, `failed` (transicion no permitida) y `not_found`. Idempotente |
| **Mappings SQL** | `create_sql_mappings(domain, view_names?, user_instructions?)` | Crear o actualizar mappings SQL de vistas existentes |
| **Términos semánticos** | `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | Generar términos semánticos. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |
| **Business terms** | `create_business_term(domain, name, description, type, related_assets)` | Crear business term en el diccionario con relaciones a activos |
| | `list_business_asset_types()` | Listar tipos de activos disponibles para business terms |
| **Colecciones** | `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | Crear colección de datos (dominio técnico) con tablas y paths. `collection_name` sin espacios (usar underscores). Refresca vista técnica automáticamente |
| **Utilidad** | `list_technical_domain_concepts(domain)` | Listar vistas de negocio existentes con estado de gobernanza (Draft/Pending Publish/Published), mappings y términos semánticos |
| | `create_collection_description(domain, user_instructions?)` | Generar SOLO la descripción del dominio/colección (sin tocar tablas) |

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

## 3. Reglas Estrictas

- **INMUTABILIDAD de `domain_name`**: El parámetro `domain_name` en TODAS las llamadas MCP debe ser **exactamente** el valor devuelto por `list_domains` o `search_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo. Si el dominio se llama `AnaliticaBanca`, usar `"AnaliticaBanca"` — no `"Banca Particulares"`, no `"Analítica Banca"`, no `"banca"`. Si hay duda sobre el nombre exacto, volver a llamar a `search_domains` o `list_domains` para confirmarlo
- **Dominios técnicos para creación y publicación**: Las tools de creación (`create_technical_terms`, `create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms`) y publicación (`publish_business_views`) usan dominios técnicos. Descubrirlos con `list_domains(domain_type='technical')` o `search_domains(texto, domain_type='technical')`. Los dominios semánticos (`semantic_*`) son el RESULTADO del proceso, no la entrada
- **Dominios semánticos para exploración**: `list_domains(domain_type='business')`, `search_domains(texto, domain_type='business')` y `search_domain_knowledge` permiten explorar capas semánticas ya publicadas
- **`user_instructions` siempre ofrecido**: Antes de invocar cualquier tool que acepte `user_instructions`, ofrecer al usuario la oportunidad de aportar contexto adicional. El agente puede **leer ficheros locales** del usuario (documentación, glosarios, especificaciones, CSVs, ontologías .owl/.ttl) para extraer información relevante y pasarla como contexto. Preguntar si tiene ficheros o contexto de dominio que quiera aportar. No es bloqueante — si el usuario no aporta, continuar sin el parámetro. **No sugerir opciones que la tool controla internamente** (idioma, formato de salida) — centrarse en contexto de dominio, definiciones de negocio y reglas específicas
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

- `list_technical_domain_concepts(domain)` → vistas de negocio existentes con estado de mappings y términos semánticos
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
| SQL Mappings | `list_technical_domain_concepts(domain)` → estado de mapping por vista | `create_sql_mappings` sobrescribe mappings existentes |
| Términos semánticos | `list_technical_domain_concepts(domain)` → estado de términos por vista | Informar. Opciones: saltar / regenerar (destructivo) / cancelar |

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
