---
name: fetch-dcat-ckan
description: >
  Descarga todos los metadatos DCAT-AP-ES de un portal CKAN de una administración
  pública española. Detecta automáticamente si el portal usa CKAN y obtiene los
  datasets en formato RDF (Turtle, JSON-LD o RDF/XML) listos para importar en el DMP.
argument-hint: [URL del portal, e.g. https://catalogo.datosabiertos.miteco.gob.es]
---

# Skill: Fetch DCAT-AP desde portal CKAN

## Fase 1: Detección del portal (fingerprinting)

1. Llama a `fingerprint_portal(portal_url=<URL_del_argumento>)`.
2. Evalúa el resultado:
   - Si `primary_platform == "ckan"` → usa `ckan.api_base_url` para continuar.
     Anota también `datos_gob_es.dir3_code` si está disponible (lo usarás en Fase 2).
   - Si `primary_platform` es `"dkan"` o `"opendatasoft"` → informa al usuario e indica
     que para esas plataformas deberían usarse las skills específicas.
   - Si `primary_platform == "unknown"` → informa que no se detectó API estándar.
     Pregunta si desea proporcionar la URL base de CKAN directamente.
3. Confirma con el usuario la URL base que se usará antes de continuar.

## Fase 2: Descubrimiento de datasets + comparación con datos.gob.es

1. Pregunta al usuario qué datasets desea descargar:
   ```
   ¿Qué datasets deseas descargar?
     [1] Todos
     [2] Solo los modificados desde una fecha (para sincronización)
     [3] Filtrar por texto / tema
     [4] Seleccionar un subset manualmente
   ```

2. Según la elección, obtén los parámetros de filtro: `query`, `since_modified`.

3. Lanza en paralelo:
   - `list_ckan_datasets(base_url=<api_base_url>, page=0, page_size=1, query=..., since_modified=...)`
     → para obtener el total del portal
   - Si hay `dir3_code` del fingerprint:
     `compare_portal_counts(portal_url=<api_base_url>, dir3_code=..., keyword=..., from_date=...)`
     → para obtener el conteo de datos.gob.es con los mismos filtros

4. Muestra al usuario el resumen comparativo:
   ```
   Portal propio (CKAN): {total_portal} datasets
   datos.gob.es:         {total_datosgob} datasets (solo comparación)
   ```
   Si los conteos difieren notablemente, menciónalo brevemente.

5. Confirma el volumen antes de proceder si son más de 200 datasets.

## Fase 3: Descarga de metadatos DCAT-AP-ES

**Elige la estrategia según lo que haya pedido el usuario:**

- Si el usuario quiere **todos los datasets** (sin límite ni filtro) → usa `fetch_dcat_catalog`:
  1. Llama a `fetch_dcat_catalog(base_url=<api_base_url>, format="ttl")`.
     - Siempre devuelve un **único fichero** con todos los datasets.
     - Si el portal tiene el plugin ckanext-dcat → fichero TTL/RDF nativo (`transformation_applied=false`).
     - Si no lo tiene → el MCP hace el fallback automáticamente via `package_search` y devuelve
       un fichero JSON-LD construido por transformación (`transformation_applied=true`).
     - En ambos casos → ve directamente a Fase 4.
     - Solo continúa con descarga individual si `fetch_dcat_catalog` lanza una excepción real
       (timeout, error HTTP 5xx, etc.).

- Si el usuario especifica **un subconjunto** (N primeros, filtro por fecha, por texto, selección manual) → ve directamente a la descarga individual, no uses `fetch_dcat_catalog`.

**Descarga individual por dataset** (subconjunto o fallback del catálogo completo):

Procesa los datasets en **batches de 20** para no saturar el portal.
Mantén tres contadores separados: `ok_native`, `ok_transformed`, `failed`.

Para cada dataset:
1. Llama a `fetch_dcat_dataset(base_url=<api_base_url>, dataset_id=<name>, format="auto")`.
2. Si tiene éxito:
   - Acumula `file_path` y `dataset_id`. **No acumules ni menciones el contenido RDF.**
   - Si `transformation_applied == true` → incrementa `ok_transformed`.
   - Si `transformation_applied == false` → incrementa `ok_native`.
3. Si falla: registra el error con el motivo e incrementa `failed`. Continúa (no abortes).

Muestra progreso tras cada batch indicando el modo de descarga:
```
[20/847] descargados — 18 DCAT nativo · 2 via transformación CKAN
[40/847] descargados — 35 DCAT nativo · 5 via transformación CKAN
```

Si en un batch todos los datasets usan transformación, avisa una vez (no en cada batch):
```
⚠️  Este portal no expone el plugin RDF — todos los metadatos se están
    generando via transformación CKAN→DCAT-AP. Ver nota final.
```

## Fase 4: Resumen y siguiente paso

Al terminar, presenta:
```
✅ Descarga completada
   Total en el portal:          847
   DCAT nativo (plugin RDF):    701
   Via transformación CKAN:     140
   Fallidos:                      6

Datasets fallidos:
  - calidad-aire-2010: package_show no devolvió datos válidos
  - ...

Ficheros guardados en /tmp/dcat-*.{ttl,jsonld}
```

Si `ok_transformed > 0`, añade siempre esta nota explicativa:

```
ℹ️  Nota sobre los {ok_transformed} datasets via transformación CKAN
────────────────────────────────────────────────────────────────────
Este portal no tiene el plugin ckanext-dcat habilitado, así que el
agente ha construido el JSON-LD DCAT-AP-ES directamente desde el JSON
interno de CKAN (package_show).

La transformación es fiel al JSON de CKAN: solo incluye los campos
que el portal realmente publica. No se ha inventado ningún metadato.

Campos que pueden estar incompletos respecto a un export DCAT nativo:
  · dcat:theme       — solo se emite si el portal usa el extra "dcat_theme"
                       con URI (muchos no lo hacen)
  · dct:spatial      — solo si hay extra "spatial" o "spatial-text"
  · dct:temporal     — solo si hay extras "temporal_start"/"temporal_end"
  · dct:language     — solo si hay extra "language"; si no, no se asume español
  · dct:accrualPeriodicity — solo si hay extra "frequency"

Para mejorar la cobertura de estos campos en el futuro, el portal
debería habilitar ckanext-dcat o rellenar los extras estándar.
────────────────────────────────────────────────────────────────────
```

Cierra con:
```
¿Deseas importar los {ok_native + ok_transformed} datasets descargados en el DMP?
Usa /import-dcat-dmp para proceder.
```

## Reglas invariables

- **Nunca acumules ni muestres el contenido RDF** — solo trabaja con `file_path`. El RDF está en disco.
- Si un dataset falla, registra y continúa. No abortes el proceso completo.
- Informa del progreso cada 20 datasets para que el usuario sepa que el proceso avanza.
- Respeta siempre el rate limiting del portal: añade una pausa de 0.5s entre batches si
  el portal devuelve errores 429 o 503.
