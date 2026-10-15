---
name: import-dcat-dmp
description: >
  Importa metadatos DCAT-AP-ES (ficheros RDF en Turtle, JSON-LD o RDF/XML) en el
  DataMarketPlace de Stratio a través de las herramientas import_dcat_file,
  get_import_report y get_import_reports. El import es asíncrono: cada llamada
  devuelve un importId en estado PENDING que hay que consultar hasta que finalice.
  Puede importar un dataset individual o procesar en batch los descargados por
  fetch-dcat-ckan. Genera un reporte detallado de éxitos, errores y warnings.
argument-hint: [dataset_id concreto, o "all" para importar lo descargado con fetch-dcat-ckan]
---

# Skill: Import DCAT-AP en el DataMarketPlace

## Fase 0: Decidir estrategia de batching (OBLIGATORIO — no saltar, no asumir)

**Antes de hacer ninguna llamada MCP**, pregunta al usuario. No hay valor por defecto — no puedes continuar sin su respuesta:

> "¿Cómo quieres hacer el import?
> - **Opción A — Uno por dataset** (recomendado): cada dataset se importa por separado, seguimiento granular.
> - **Opción B — Fichero único**: todos los datasets combinados en un solo import, más simple pero puede ser lento con muchos datasets."

**Opción A — Un import por dataset**
- Lanza `import_dcat_file` para cada dataset por separado.
- Recoge todos los `importId` devueltos.
- Consulta el estado de todos con `get_import_reports` hasta que ninguno esté en PENDING/IN_PROGRESS.

**Opción B — Un único import con todos los datasets combinados**
- Combina todos los RDF en un único fichero antes de enviar.
- Un solo `import_dcat_file` → un solo `importId` → polling más simple.
- Puede ser lento si el fichero resultante es muy grande (todo en memoria).
- Para combinar: usa `merge_jsonld_files(file_paths=[...], output_path="/tmp/dcat-combined.jsonld")`
  si los ficheros son JSON-LD. Para Turtle (.ttl), la concatenación directa de ficheros es válida.

## Fase 1: Validación previa

1. Verifica que hay ficheros RDF disponibles:
   - Si el usuario llegó desde `/fetch-dcat-ckan`: usa las rutas de fichero devueltas por esa skill
     (campo `file_path`, típicamente `/tmp/dcat-{dataset_id}.ttl`).
   - Si el usuario proporciona un dataset_id: descárgalo primero con
     `fetch_dcat_dataset(base_url, dataset_id)` — la tool devuelve el `file_path` del fichero guardado.
     Usa ese `file_path`, no el contenido RDF.
   - Si el usuario proporciona directamente el contenido RDF como texto: úsalo en `rdf_content`.

2. Comprueba la configuración del entorno:
   - `DATAMARKET_TEMPLATE_ID` y `DATAMARKET_PATH_ID` deben estar configurados.
   - Si no están, informa al usuario que debe configurarlos en el `.env` del MCP server
     o proporcionarlos explícitamente como argumentos.

## Fase 2: Lanzar imports

**Regla clave**: usa siempre `rdf_file_path` en lugar de `rdf_content` cuando el RDF esté en un fichero.
El contenido RDF nunca debe aparecer en el chat ni en los argumentos de las tools.

### Opción A (un import por dataset)

Lanza **todos** los imports sin esperar a ninguno (wait implícito está en el servidor, pero el agente
no debe esperar entre llamadas). Recoge todos los `importId` y consulta al final de una sola vez:

```
1. Para CADA dataset (en paralelo si es posible, o en ráfaga sin esperas entre llamadas):
     import_dcat_file(rdf_file_path="/tmp/dcat-{id}.ttl", rdf_format="ttl")
     → guarda el importId devuelto

2. Si alguno ya viene en ERROR desde el POST, regístralo directamente como fallo.

3. Muestra: "[N] imports lanzados, esperando resultados..."

4. Un único get_import_reports(import_ids=[...todos los importIds...], wait=True)
   para obtener todos los resultados de una sola vez.
```

No hagas `get_import_report` o `get_import_reports` entre grupos — espera a tener TODOS los importIds
antes de consultar.

### Opción B (fichero combinado)

```
1. Combina todos los ficheros RDF:
   - Si son JSON-LD: merge_jsonld_files(file_paths=["/tmp/dcat-1.jsonld", ...], output_path="/tmp/dcat-combined.jsonld")
   - Si son Turtle (.ttl): concatenación directa de ficheros en /tmp/dcat-combined.ttl
2. Llama a import_dcat_file(rdf_file_path="/tmp/dcat-combined.ttl") una única vez.
3. Recoge el único importId.
4. Llama a get_import_report(import_id=..., wait=True) para obtener el resultado.
```

## Fase 3: Obtener resultados finales

Las tools `get_import_report` y `get_import_reports` hacen el polling automáticamente
(parámetro `wait=true` por defecto) — bloquean hasta que todos los imports finalicen
o se agote el timeout (300s por defecto).

- **Opción A** (varios imports): llama a `get_import_reports(import_ids=[...todos los ids...], wait=True)`
  **una única vez** después de haber lanzado todos los imports.
  La tool espera a que todos terminen y devuelve el reporte final completo.
- **Opción B** (un único import): llama a `get_import_report(import_id=..., wait=True)`.

No es necesario hacer polling manual — la tool lo gestiona internamente.
Si el import tarda más de 5 minutos, la tool devuelve el estado actual con los que sigan en PENDING.

## Fase 4: Clasificación de errores y warnings

Cuando todos los imports han finalizado, clasifica los resultados:

| Tipo de error | Causa probable | Acción sugerida |
|---------------|----------------|-----------------|
| `RDF_IMPORT_TEMPLATE_NOT_FOUND` | UUID de template incorrecto | Verificar DATAMARKET_TEMPLATE_ID |
| `RDF_IMPORT_PATH_ID_ERROR` | UUID de path incorrecto | Verificar DATAMARKET_PATH_ID |
| `RDF_IMPORT_FILE_ERROR` | RDF malformado en origen | El portal publicó un fichero inválido |
| `RDF_IMPORT_NO_IMPORTABLE_TEMPLATE_ERROR` | Template sin configuración DCAT-AP | Revisar configuración del template |
| Otros | Error interno DMP | Registrar para revisión manual |

Los **warnings** no son errores — el dataset se importó, pero con advertencias (campos opcionales faltantes, valores no reconocidos, etc.). Muéstralos siempre.

## Fase 5: Reporte final

```
✅ Importación completada

  Total procesados:     58
  Importados con éxito: 55
  Con warnings:         8
  Errores:              3

Datasets importados:
  ✅ <URI>  →  Data Product ID: 12345
  ✅ <URI>  →  Data Product ID: 12346  ⚠ warning: campo dct:publisher vacío
  ...

Errores:
  ❌ <URI>  →  RDF_IMPORT_FILE_ERROR: Unexpected token at line 42
  ...

Datasets importados disponibles en el DMP.
¿Deseas configurar sincronización automática? Usa /sync-dcat-changes.
```

**Si el usuario pidió publicar tras el import** (p.ej. "importa y publícalo"):
extrae los `Data Product ID` de los items SUCCESS y úsalos directamente —
no hagas una nueva búsqueda por nombre o descripción:

```
publish_data_products(
  data_product_ids=[12345, 12346, ...],   # IDs del import report
  dry_run=true                            # primero preview, luego confirmar
)
```

## Reglas invariables

- Un error en un dataset NO debe abortar el proceso completo.
- No modifiques el contenido RDF antes de enviarlo al DMP.
- **Usa siempre `rdf_file_path` en `import_dcat_file`, nunca `rdf_content`** cuando el RDF esté en un fichero.
  El contenido RDF nunca debe aparecer en el chat ni en los argumentos de las tools.
- Lanza todos los imports antes de esperar ninguno. Usa un único `get_import_reports(wait=True)` al final.
- Si el DMP devuelve 403, informa al usuario sobre permisos (necesita rol WRITE en METADATA_IMPORT).
- Si el DMP devuelve 404 en template o path, para el proceso y pide corrección antes de continuar.
- Siempre muestra los warnings aunque el import sea exitoso — ayudan a detectar metadatos incompletos.
