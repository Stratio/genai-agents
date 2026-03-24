---
name: create-data-collection
description: Buscar tablas y paths en el diccionario de datos tecnico y crear una nueva coleccion de datos (dominio tecnico) en Stratio Governance.
argument-hint: [nombre de coleccion o terminos de busqueda (opcional)]
---

# Skill: Crear Coleccion de Datos

Busca tablas y paths en el diccionario de datos tecnico y crea una nueva coleccion de datos (dominio tecnico) en Stratio Governance. Fase 0 del pipeline de capa semantica — permite crear dominios nuevos antes de construir su capa semantica.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `stratio_search_data_dictionary(search_text, search_type?)` | sql | Buscar tablas y paths en el diccionario. `search_type`: `'tables'`, `'paths'` o `'both'` (defecto). Resultados ordenados por relevancia. Cada resultado: `metadata_path`, `name`, `subtype` (Table/Path), `alias?`, `data_store?`, `description?` |
| `stratio_create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | gov | Crear coleccion + asociar tablas/paths + refrescar vista tecnica. `collection_name` sin espacios (usar underscores). Al menos una de las dos listas obligatoria. Los `metadata_path` provienen de resultados de `stratio_search_data_dictionary` |
| `stratio_list_technical_domains` | sql | Verificar que el nombre de coleccion no exista ya |

**Reglas clave**: `collection_name` sin espacios ni caracteres especiales (usar underscores) — misma convencion que ontologias. Al menos un `table_metadata_paths` o `path_metadata_paths` requerido. Los `metadata_path` se obtienen de los resultados de `stratio_search_data_dictionary`. Confirmacion explicita antes de crear. La busqueda es read-only e idempotente; la creacion no es idempotente.

## Workflow

### 1. Determinar intencion

Si `$ARGUMENTS` contiene texto, usarlo como semilla de busqueda inicial y pasar directamente al paso 2. Si no hay argumento, preguntar al usuario que tipo de datos busca o que coleccion quiere crear, siguiendo la convencion de preguntas al usuario.

### 2. Busqueda iterativa en el diccionario

Ejecutar `stratio_search_data_dictionary(search_text, search_type?)` con el termino proporcionado. `search_type` por defecto `'both'`.

Presentar resultados en tabla:

```
| # | Tipo | Nombre | metadata_path | data_store | Descripcion |
|---|------|--------|---------------|------------|-------------|
| 1 | Table | clientes | /path/to/clientes | PostgreSQL | Tabla de clientes |
```

- **Sin resultados**: Ofrecer opciones: refinar termino de busqueda, cambiar `search_type` (`'tables'`, `'paths'` o `'both'`), o cancelar
- **Bucle de refinamiento**: El usuario puede buscar tantas veces como necesite. Acumular selecciones entre iteraciones

### 3. Seleccion de tablas/paths

El usuario selecciona elementos de la tabla por numero (seleccion multiple: numeros separados por coma). Mezcla de Table y Path permitida.

Mostrar resumen acumulado tras cada seleccion:
```
Seleccion actual: Tables: N, Paths: M
```

Ofrecer opciones: buscar mas elementos o continuar con la creacion.

### 4. Proponer nombre y descripcion

- Proponer `collection_name` basado en el contexto (sin espacios, usar underscores — misma convencion que ontologias)
- Proponer `description` basada en las tablas/paths seleccionados
- El usuario puede editar ambos valores

Verificar que el nombre propuesto no coincida con un dominio existente ejecutando `stratio_list_technical_domains`. Si ya existe, informar y pedir un nombre alternativo.

### 5. Confirmacion y ejecucion

Presentar resumen final completo antes de crear:
```
## Crear Coleccion de Datos
- Nombre: mi_coleccion
- Descripcion: ...
- Tables (N): [lista de metadata_paths]
- Paths (M): [lista de metadata_paths]
```

Solicitar confirmacion explicita del usuario (operacion de escritura).

Separar la seleccion por `subtype`:
- Resultados con subtype `Table` → parametro `table_metadata_paths`
- Resultados con subtype `Path` → parametro `path_metadata_paths`

Invocar `stratio_create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)`.

Presentar resultado: `tables_inserted`, `tables_failed`, `message`.

Si hay fallidas: informar cuales y ofrecer reintentar solo las fallidas (maximo 2 reintentos).

### 6. Resumen y siguiente paso

Presentar resumen de la coleccion creada con el resultado final.

Sugerir siguiente paso: "Puedes construir su capa semantica con `/build-semantic-layer [nombre]`"
