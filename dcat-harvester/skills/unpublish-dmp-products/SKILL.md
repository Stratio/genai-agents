# Skill: Despublicar Data Products en el DMP

Cambia el estado de uno o varios Data Products del DataMarketPlace a Unpublished,
con soporte de filtros por nombre y/o keywords, o una lista explícita de IDs.

---

## Cuándo usar esta skill

Cuando el usuario pide algo como:
- "despublica los dataproducts de biodiversidad"
- "quita de publicado todos los que importé de MITECO"
- "cambia a despublicado el dataproduct ID 42"
- "despublica los dataproducts relacionados con calidad del agua"
- "archiva / retira los datasets de X"

---

## Fase 0 — Entender el alcance

`unpublish_data_products` tiene **tres modos de búsqueda** — elige el correcto:

### Modo A — OpenSearch (preferente para productos Published)

Usa `text_query` y/o `searcher_filters` cuando los productos estén publicados.
Es más rápido y preciso que el modo REST.

| Cuándo usarlo | Parámetro |
|---|---|
| El usuario describe el tema en lenguaje natural ("los de Málaga", "calidad del aire") | `text_query` |
| El usuario menciona una etiqueta, publisher o tema exactos | `searcher_filters` con `keysValues` |

Ejemplos de `searcher_filters.keysValues`:
- `"tags:=Cercanias"` — por etiqueta exacta
- `"publisher:=Ayuntamiento de Málaga"` — por publicador
- `"theme:=Medio ambiente"` — por tema

Combina `text_query` + `searcher_filters` si el usuario da varios criterios.

### Modo B — REST API (para Draft/Unpublished o búsqueda por nombre/descripción)

Usa cuando los productos **no** están en OpenSearch (Draft, Unpublished) o cuando
el usuario busca por nombre o descripción exactos:

| Caso | Parámetro a usar |
|---|---|
| Palabra clave en el nombre | `name_like` |
| Texto en la descripción | `description_like` |
| Etiquetas (solo para Draft/Unpublished) | `keywords` |
| Importados en una fecha concreta | `created_after` / `created_before` |

Los filtros del Modo B son combinables entre sí.

### Modo C — IDs explícitos

| Caso | Parámetro a usar |
|---|---|
| El usuario da IDs concretos | `data_product_ids` |

---

**No permitido**: despublicar "todos" sin ningún filtro — pide al menos un criterio.

Si la petición es ambigua, formula **una sola pregunta** para clarificar el criterio.
No procedas si no tienes al menos un filtro claro.
No uses `search_published_data_products` para "listar todo y luego despublicar":
esta skill debe trabajar directamente con `unpublish_data_products`.

---

## Fase 1 — Preview con dry_run

**Siempre** empieza con una llamada en modo dry_run para mostrar al usuario qué se va a despublicar:

```
# Modo A (OpenSearch):
unpublish_data_products(
  text_query="<texto libre>",                         # si aplica
  searcher_filters={"keysValues": ["tags:=<tag>"]},   # si aplica
  dry_run=true
)

# Modo B (REST API):
unpublish_data_products(
  name_like="<término>",          # si aplica
  description_like="<texto>",     # si aplica
  keywords=["<kw1>", ...],        # si aplica (solo Draft/Unpublished)
  created_after="YYYY-MM-DD",     # si aplica
  created_before="YYYY-MM-DD",    # si aplica
  dry_run=true
)

# Modo C (IDs):
unpublish_data_products(
  data_product_ids=[...],
  dry_run=true
)
```

Muestra el resultado al usuario:
- Si `total == 0`: informa que no hay productos que coincidan con los filtros y termina.
- Si `total > 0`: muestra la lista y el recuento.

---

## Fase 2 — Confirmación (siempre obligatoria)

A diferencia de la publicación, **despublicar siempre requiere confirmación explícita**,
independientemente del número de productos:

> "Se van a despublicar **N dataproducts**. Esta acción los retirará del catálogo público. ¿Confirmas?"

Espera la respuesta. No despubliques sin confirmación.

---

## Fase 3 — Despublicar

Ejecuta la operación con los mismos parámetros pero `dry_run=false` (o sin el parámetro):

```
unpublish_data_products(
  # Modo A:
  text_query="<texto libre>",
  searcher_filters={"keysValues": ["..."]},
  # Modo B:
  name_like="<término>",
  description_like="<texto>",
  keywords=["<kw1>", ...],
  created_after="YYYY-MM-DD",
  created_before="YYYY-MM-DD",
  # Modo C:
  data_product_ids=[...],
  dry_run=false
)
```

La tool maneja la paginación y despublica en paralelo — una sola llamada es suficiente.

Si el entorno requiere un estado BPM diferente a `"Unpublished"` (p.ej. `"Draft"`),
pásalo en `unpublish_status`:

```
unpublish_data_products(
  ...,
  unpublish_status="Draft"
)
```

---

## Fase 4 — Informe de resultados

Tras la llamada, muestra al usuario:
- Cuántos se despublicaron correctamente
- Cuántos fallaron (con el error)
- Si hay fallos, sugiere reintentar con los IDs fallidos usando `data_product_ids`

Ejemplo de resumen:
```
✅ Despublicados 23/25 dataproducts
❌ 2 errores:
  • [ID 101] Dataset biodiversidad marina — BPM timeout
  • [ID 208] Inventario especies — Permission denied
```

---

## Reglas

- Nunca despubliques sin haber mostrado primero el dry_run al usuario.
- **Siempre pide confirmación explícita** antes de despublicar, incluso para un solo producto.
- No uses `search_data_products` por separado para luego despublicar manualmente — usa siempre `unpublish_data_products` que lo hace internamente de forma más eficiente.
- Si por petición del usuario necesitas una búsqueda exploratoria previa, usa paginación estricta (`size=10`, `page` incremental) para evitar respuestas gigantes.
- Si el usuario quiere despublicar "todos sin filtro", explica que es necesario al menos un criterio de selección para evitar operaciones accidentales masivas.
