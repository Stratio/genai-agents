---
name: sync-dcat-changes
description: >
  Sincroniza los cambios en un portal de datos abiertos con el DataMarketPlace: detecta datasets
  nuevos o modificados desde la última sincronización y los importa en el DMP.
  Implementa sincronización delta — solo procesa lo que ha cambiado.
  Soporta CKAN, SPARQL, DKAN. Para ODS y ArcGIS Hub, requiere sincronización completa.
argument-hint: [URL del portal, e.g. https://catalogo.datosabiertos.miteco.gob.es]
---

# Skill: Sincronización delta DCAT-AP → DMP

## Fase 0: Identificar la plataforma

Si la plataforma del portal ya se conoce (de una sesión anterior o porque el usuario la especificó),
omite este paso. Si no:

1. Llama a `fingerprint_portal(<URL>)` para identificar la plataforma.
2. Anota la plataforma detectada — determina la estrategia de detección de cambios:

| Plataforma | Estrategia delta |
|---|---|
| **CKAN** | `list_ckan_datasets(since_modified=<fecha>)` — nativo |
| **SPARQL** | `fetch_sparql_dcat_catalog(from_date=<fecha>)` — nativo |
| **DKAN** | `list_dkan_datasets` + filtrado local por fecha — sin soporte nativo |
| **OpenDataSoft** | Sin delta nativo — descarga catálogo completo |
| **ArcGIS Hub** | Sin delta nativo — descarga catálogo completo |

## Fase 1: Determinar punto de referencia

1. Pregunta al usuario la fecha desde la que sincronizar:
   ```
   ¿Desde qué fecha sincronizamos?
     [1] Desde la última sincronización registrada: {ultima_fecha}
     [2] Introducir fecha manualmente (ISO 8601, e.g. 2024-06-01T00:00:00Z)
     [3] Sincronización completa (todos los datasets)
   ```
2. Guarda la fecha de inicio de esta sincronización para futuras referencias
   (anótala en la respuesta al usuario para que pueda usarla la próxima vez).

## Fase 2: Descubrimiento de cambios

### Si el portal es CKAN:

1. Llama a `list_ckan_datasets(base_url=<portal>, since_modified=<fecha_referencia>)`.
2. Si `total == 0`: informa que no hay cambios desde esa fecha. Proceso completado.
3. Si `total > 0`: muestra resumen y pide confirmación antes de continuar.

### Si el portal tiene endpoint SPARQL con DCAT:

1. Llama a `fetch_sparql_dcat_catalog(sparql_url=<url>, from_date=<fecha_referencia>)`.
   - El tool filtra directamente en el triplestore — solo devuelve datasets modificados desde la fecha.
2. Si no hay datasets: informa que no hay cambios. Proceso completado.
3. Si hay datasets: muestra el total descargado (los `file_path`) y pide confirmación.
4. **Importante**: para SPARQL el resultado ya es el fichero RDF listo para importar — salta a Fase 3 directamente con esos `file_path`.

### Si el portal es DKAN:

DKAN no tiene filtro de fecha nativo en su API. Estrategia de filtrado local:

1. Pagina todos los datasets con `list_dkan_datasets(base_url=<url>)` hasta obtener el listado completo.
2. Filtra localmente los datasets cuyo campo `modified` >= `fecha_referencia`.
3. Muestra resumen:
   ```
   📋 Datasets DKAN revisados: {total_paginados}
      Modificados desde {fecha}: {total_modificados}
      {preview de los primeros 5}
   ```
4. Si `total_modificados == 0`: informa que no hay cambios. Proceso completado.
5. Si `total_modificados > 200`: advierte antes de proceder (puede indicar una referencia de fecha muy antigua).
6. Descarga los datasets filtrados con `fetch_dcat_dataset(base_url, dataset_id)` en batches de 20.

### Si el portal es OpenDataSoft o ArcGIS Hub:

Estos portales no exponen una API de cambios — no es posible sincronización delta nativa. Informa al usuario:

```
⚠️ El portal {plataforma} no soporta sincronización delta nativa.
Es necesario descargar el catálogo completo para detectar cambios.

¿Quieres proceder con una sincronización completa?
  - ODS: fetch_ods_catalog → descarga todo el catálogo en un fichero
  - ArcGIS: fetch_arcgis_catalog → descarga todo el catálogo en un fichero

El DMP detectará automáticamente qué datasets son nuevos y cuáles son actualizaciones.
```

Si el usuario confirma: descarga el catálogo completo con `fetch_ods_catalog` / `fetch_arcgis_catalog`
y continúa con Fase 3. Si no: cancela el proceso.

## Fase 3: Descarga y import de cambios

Sigue el mismo flujo que `/import-dcat-dmp` (mismas estrategias de batching y polling):

- **Para CKAN y DKAN** (lista de dataset IDs):
  1. `fetch_dcat_dataset(base_url, dataset_id, format="auto")` para cada dataset → guarda `file_path`.
     Acumula solo `file_path`, nunca el contenido RDF.
  2. Lanza todos los imports con `import_dcat_file(rdf_file_path=..., wait=False)` → recoge importIds.
  3. Un único `get_import_reports(import_ids=[...], wait=True)` para obtener todos los resultados.

- **Para SPARQL** (fichero RDF ya descargado en Fase 2):
  1. El `file_path` del catálogo SPARQL ya está disponible — lanza directamente `import_dcat_file`.
  2. Un único `get_import_reports(import_ids=[...], wait=True)`.

- **Para ODS y ArcGIS Hub** (fichero único de catálogo completo):
  1. El `file_path` del catálogo ya está disponible — lanza `import_dcat_file`.
  2. `get_import_report(import_id=..., wait=True)`.

El DMP gestiona internamente si el dataset es nuevo o es una actualización (basado en URI).

## Fase 4: Reporte de sincronización

```
🔄 Sincronización completada

  Plataforma:             {plataforma}
  Fecha de referencia:    {fecha_referencia}
  Datasets procesados:    {total}
  Actualizados/creados:   {successful}
  Errores:                {errors}

  Próxima sincronización: usa since_modified="{fecha_inicio_esta_sync}"
```

## Reglas invariables

- La sincronización delta es preferible a la sincronización completa para portales grandes.
- El DMP gestiona internamente si el dataset es nuevo o es una actualización.
- Guarda siempre la fecha de inicio de la sync para que el usuario pueda usarla como
  referencia en la próxima ejecución.
- Si hay más de 500 datasets modificados, advierte antes de proceder — puede indicar
  una sincronización completa accidental o una referencia de fecha demasiado antigua.
- Para DKAN, el filtrado local es correcto pero más lento — avisa al usuario si el
  catálogo es muy grande (>1000 datasets) antes de paginar todo.
