---
name: create-data-collection
description: "Crear una nueva data collection (dominio técnico) en Stratio Governance y buscar en el diccionario de datos técnico las tablas y paths a incluir. Usar cuando el usuario quiera crear un nuevo dominio técnico, agrupar un conjunto de tablas bajo una nueva colección, o preparar el contenedor antes de cualquier trabajo de capa semántica. Para construir la capa semántica de una colección existente, preferir build-semantic-layer."
argument-hint: "[nombre de colección o términos de búsqueda (opcional)]"
---

# Skill: Crear Colección de Datos

Busca tablas y paths en el diccionario de datos técnico y crea una nueva colección de datos (dominio técnico) en Stratio Governance. Fase 0 del pipeline de capa semántica — permite crear dominios nuevos antes de construir su capa semántica.

## Tools MCP utilizadas

| Tool | Servidor | Propósito |
|------|----------|-----------|
| `search_data_dictionary(search_text, search_type?)` | sql | Buscar tablas y paths en el diccionario. `search_type`: `'tables'`, `'paths'` o `'both'` (defecto). Resultados ordenados por relevancia. Cada resultado: `metadata_path`, `name`, `subtype` (Table/Path), `alias?`, `data_store?`, `description?` |
| `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | gov | Crear colección + asociar tablas/paths + refrescar vista técnica. `collection_name` sin espacios (usar underscores). Al menos una de las dos listas obligatoria. Los `metadata_path` provienen de resultados de `search_data_dictionary` |
| `list_domains(domain_type='technical', refresh?)` | sql | Verificar que el nombre no exista ya. Tras crear la colección, llamar con `refresh=true` para precalentar la cache |

**Reglas clave**: `collection_name` sin espacios ni caracteres especiales (usar underscores) — misma convención que ontologías. Al menos un `table_metadata_paths` o `path_metadata_paths` requerido. Los `metadata_path` se obtienen de los resultados de `search_data_dictionary`. Confirmación explícita antes de crear. La búsqueda es read-only e idempotente; la creación no es idempotente.

## Workflow

### 1. Determinar intencion

Si `$ARGUMENTS` contiene texto, usarlo como semilla de búsqueda inicial y pasar directamente al paso 2. Si no hay argumento, preguntar al usuario que tipo de datos busca o que colección quiere crear, siguiendo la convención de preguntas al usuario.

### 2. Busqueda iterativa en el diccionario

Ejecutar `search_data_dictionary(search_text, search_type?)` con el término proporcionado. `search_type` por defecto `'both'`.

**Busqueda por palabras clave**: La herramienta funciona mejor con términos cortos o palabras clave individuales que con frases largas o múltiples palabras. Si el usuario describe lo que busca en lenguaje natural, extraer los términos más relevantes y buscarlos por separado (ej: "tablas de clientes con sus contratos" → buscar primero "clientes", luego "contratos"). Evitar enviar frases completas como search_text.

Presentar resultados en tabla:

```
| # | Tipo | Nombre | metadata_path | data_store | Descripción |
|---|------|--------|---------------|------------|-------------|
| 1 | Table | clientes | /path/to/clientes | PostgreSQL | Tabla de clientes |
```

- **Sin resultados**: Ofrecer opciones: refinar término de búsqueda, cambiar `search_type` (`'tables'`, `'paths'` o `'both'`), o cancelar
- **Bucle de refinamiento**: El usuario puede buscar tantas veces como necesite. Acumular selecciones entre iteraciones

### 3. Selección de tablas/paths

El usuario selecciona elementos de la tabla por número (selección múltiple: números separados por coma). Mezcla de Table y Path permitida.

Mostrar resumen acumulado tras cada selección:
```
Selección actual: Tables: N, Paths: M
```

Ofrecer opciones: buscar más elementos o continuar con la creación.

### 4. Solicitar nombre y descripción

- **Nombre**: Preguntar al usuario que nombre quiere para la colección (`collection_name` sin espacios, usar underscores — misma convención que ontologías). Si el usuario no tiene preferencia, puede sugerirse un nombre derivado únicamente de los términos de búsqueda reales usados (ej: busco "clientes" → sugiere `clientes`). No inferir temas o propósitos de negocio no mencionados por el usuario.
- **Descripción**: Preguntar al usuario que descripción quiere para la colección. No inventar descripción. Si el usuario no tiene preferencia, presentar los nombres y descripciones disponibles de las tablas/paths seleccionados como contexto para que el decida, pero no fabricar contexto de negocio ni temáticas.

**Regla**: No inventar contexto de negocio, temáticas ni propósitos que no hayan sido aportados por el usuario o derivados de los metadatos reales de las tablas seleccionadas (nombres, descripciones devueltas por `search_data_dictionary`).

Verificar que el nombre propuesto no coincida con un dominio existente ejecutando `search_domains(nombre, domain_type='technical')` o `list_domains(domain_type='technical')`. Si ya existe, informar y pedir un nombre alternativo.

### 5. Confirmación y ejecución

Presentar resumen final completo antes de crear:
```
## Crear Colección de Datos
- Nombre: mi_coleccion
- Descripción: ...
- Tables (N): [lista de metadata_paths]
- Paths (M): [lista de metadata_paths]
```

Solicitar confirmación explícita del usuario (operación de escritura).

Separar la selección por `subtype`:
- Resultados con subtype `Table` → parámetro `table_metadata_paths`
- Resultados con subtype `Path` → parámetro `path_metadata_paths`

Invocar `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)`.

Presentar resultado: `tables_inserted`, `tables_failed`, `message`.

Si hay fallidas: informar cuales y ofrecer reintentar solo las fallidas (máximo 2 reintentos).

### 6. Precalentar cache

Tras una creación exitosa, ejecutar `list_domains(domain_type='technical', refresh=true)` para forzar el refresco de la cache. No es necesario esperar ni reintentar — el objetivo es que cuando el usuario invoque `/build-semantic-layer` a continuación, el dominio ya esté visible sin esperas. Si la llamada falla, ignorar el error (no es crítico).

### 7. Resumen y siguiente paso

Presentar resumen de la colección creada con el resultado final.

Sugerir siguiente paso: "Puedes construir su capa semántica con `/build-semantic-layer [nombre]`"
