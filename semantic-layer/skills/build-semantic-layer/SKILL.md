---
name: build-semantic-layer
description: Pipeline completo para construir la capa semantica de un dominio tecnico.
  Orquesta las 5 fases en secuencia con diagnostico de estado y seguimiento de progreso.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Construir Capa Semantica (Pipeline Completo)

Orquesta las 5 fases del pipeline de construccion de la capa semantica de un dominio tecnico. Si el dominio no existe, permite crear una nueva coleccion de datos como paso previo. Diagnostica el estado actual, propone un plan de ejecucion y ejecuta cada fase en secuencia.

**Importante**: Esta skill llama a las tools MCP directamente (inline). NO delega a otras skills — las skills no pueden invocar otras skills programaticamente. Las shared skills de cada fase existen para uso independiente por el usuario; el pipeline las replica de forma integrada.

Para referencia completa de tools y reglas, ver `skills-guides/stratio-semantic-layer-tools.md`.

## Workflow

### 1. Determinar dominio

Ejecutar `list_technical_domains` para listar dominios disponibles.

- Si `$ARGUMENTS` contiene nombre de dominio y coincide con uno existente → usarlo y continuar con el paso 2.
- Si no coincide o no hay argumento → presentar opciones al usuario siguiendo la convencion de preguntas al usuario:
  - Lista de dominios existentes (seleccion)
  - **Crear nueva coleccion de datos**

Si el usuario elige un dominio existente → continuar con el paso 2.

#### 1b. Crear coleccion de datos (si el usuario lo solicita)

1. **Busqueda**: Preguntar terminos de busqueda. Ejecutar `search_data_dictionary(search_text, search_type?)`. Presentar resultados en tabla (tipo, nombre, metadata_path, data_store, descripcion). Si no hay resultados, ofrecer refinar el termino o cambiar `search_type`. Permitir iteraciones de busqueda acumulando selecciones.

2. **Seleccion**: El usuario selecciona tablas y/o paths (seleccion multiple). Mostrar resumen acumulado por tipo (Tables/Paths). Ofrecer buscar mas o continuar.

3. **Nombre y descripcion**: Proponer `collection_name` (sin espacios, usar underscores) y `description`. El usuario puede editar. Verificar que el nombre no exista en `list_technical_domains`.

4. **Creacion**: Confirmar con el usuario. Separar seleccion por subtype: Table → `table_metadata_paths`, Path → `path_metadata_paths`. Invocar `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)`. Presentar resultado (tablas insertadas / fallidas). Si hay fallidas, ofrecer reintentar solo las fallidas (max 2 reintentos).

5. **Continuar pipeline**: Usar el nombre de la coleccion recien creada como `domain_name` para el resto del pipeline. Continuar con el paso 2 (diagnostico).

### 2. Diagnostico completo

Ejecutar en paralelo:
- `list_technical_domains` → verificar si el dominio tiene descripcion general
- `list_domain_tables(domain)` → tablas con/sin descripciones (= terminos tecnicos)
- `list_ontologies` → ontologias existentes
- `list_technical_domain_concepts(domain)` → vistas, mappings, terminos semanticos

Para cada ontologia relevante: `get_ontology_info(name)`.

Presentar **dashboard de estado**:
```
## Estado de la Capa Semantica — [domain_name]
| Fase | Estado | Detalle |
|------|--------|---------|
| Descripcion dominio | ✓ / ✗ | Tiene/no tiene descripcion |
| Terminos tecnicos | Parcial (15/20) | 5 tablas sin describir |
| Ontologia | ✓ Completa | "mi_ontologia" — 8 clases |
| Vistas de negocio | Parcial (6/8) | 2 clases sin vista |
| SQL Mappings | Parcial (5/6) | 1 vista sin mapping |
| Terminos semanticos | ✗ Pendiente | 0/6 vistas |
```

### 3. Contexto general

Pedir al usuario contexto global que aplique a todas las fases:
- "¿Tienes ficheros de referencia (documentacion, glosarios, especificaciones) que deba leer para entender mejor el dominio? ¿Hay definiciones de negocio, reglas o conceptos clave que quieras que se reflejen en la capa semantica? Si no, responde 'Continuar'."
- Si el usuario proporciona rutas a ficheros → **leerlos** y extraer informacion relevante como contexto global
- El contexto extraido se pasara como `user_instructions` en cada fase que lo soporte
- Solo preguntar de nuevo en fases especificas si el usuario necesita instrucciones diferentes

### 4. Plan de ejecucion

Basado en el diagnostico, listar las fases que necesitan trabajo:
- Indicar que fases estan completas (ofrecer saltar o forzar regeneracion)
- Indicar que fases estan pendientes o parciales
- Advertir dependencias entre fases (ej: "Las vistas requieren ontologia")

Pedir aprobacion global del plan antes de ejecutar.

### 5. Ejecucion secuencial

Ejecutar cada fase en orden estricto, llamando a las tools directamente:

**Fase 1 — Terminos tecnicos** (si necesario):
- `create_technical_terms(domain, table_names?, user_instructions?)` con las instrucciones globales
- Presentar resumen de la tool al usuario

**Fase 2 — Ontologia** (si necesario):
- Planificacion interactiva: preguntar al usuario sobre clases, ficheros de referencia (ontologias .owl/.ttl, documentos de negocio, CSVs), nomenclaturas
- Si el usuario proporciona rutas a ficheros locales → **leerlos** para extraer contexto y enriquecer el plan
- Explorar dominio: `list_domain_tables` + `get_tables_details` + `get_table_columns_details`
- Proponer plan de ontologia en Markdown → revisar con usuario → iterar (max 3)
- `create_ontology(domain, name, ontology_plan)` o `update_ontology(domain, name, update_plan)`
- Verificar: `get_ontology_info(name)` — presentar estructura y ofrecer: "Si quieres eliminar alguna clase antes de continuar, puedo hacerlo (clases con vistas Published no se pueden borrar)." Si el usuario pide borrar → `delete_ontology_classes(ontology_name, class_names)` → informar de borradas/saltadas → volver a verificar

**Fase 3 — Vistas de negocio** (si necesario):
- `create_business_views(domain, ontology, class_names?)` con la ontologia del paso anterior
- Presentar resumen de la tool al usuario
- Ofrecer: "Si alguna vista no te convence, puedo eliminarla antes de continuar con mappings (vistas Published no se pueden borrar)." Si el usuario pide borrar → `delete_business_views(domain, view_names)` → informar de borradas/saltadas

**Fase 4 — SQL Mappings** (si necesario; cubre vistas nuevas de Fase 3 y existentes sin mapping):
- `create_sql_mappings(domain, view_names?, user_instructions?)` con las instrucciones globales
- Presentar resumen de la tool al usuario

**Fase 5 — Terminos semanticos** (si necesario):
- Verificar que las vistas tienen mapping (pre-requisito)
- `create_semantic_terms(domain, view_names?, user_instructions?)` con las instrucciones globales
- Presentar resumen de la tool al usuario

**Tras cada fase**:
- Reportar progreso actualizado (mini-dashboard)
- Si falla: ofrecer opciones al usuario:
  - **Reintentar** con `user_instructions` mejoradas
  - **Saltar** esta fase (advertir dependencias: "Si saltas la ontologia, no se pueden crear vistas")
  - **Abortar** el pipeline

### 6. Resumen final

Presentar dashboard actualizado con el estado final:
```
## Capa Semantica Completada — [domain_name]
| Fase | Estado | Acciones realizadas |
|------|--------|---------------------|
| Terminos tecnicos | ✓ | 20 tablas procesadas |
| Ontologia | ✓ | "mi_ontologia" creada — 8 clases |
| Vistas de negocio | ✓ | 8 vistas creadas |
| SQL Mappings | ✓ | 8 mappings generados |
| Terminos semanticos | ✓ | 8 vistas con terminos |
```

Incluir:
- Acciones realizadas por fase
- Errores encontrados y como se resolvieron
- Sugerencias de siguientes pasos:
  - "Puedes crear business terms con `/manage-business-terms` para enriquecer el diccionario"
  - "La capa semantica esta lista para revision y aprobacion en la UI de Governance"
  - "Una vez aprobada, se publicara como dominio `semantic_[nombre]`"
