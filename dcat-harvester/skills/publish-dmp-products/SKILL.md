# Skill: Publicar Data Products en el DMP

Publica en el DataMarketPlace uno o varios Data Products que hayan sido importados
previamente (vía DCAT-AP o cualquier otro mecanismo), con soporte de filtros por nombre
y/o keywords, o una lista explícita de IDs.

---

## Cuándo usar esta skill

Cuando el usuario pide algo como:
- "publica los dataproducts de biodiversidad"
- "publica todos los que importé de MITECO"
- "cambia a publicado el dataproduct ID 42"
- "publica los dataproducts relacionados con calidad del agua"

---

## Fase 0 — Entender el alcance

Antes de ejecutar nada, identifica de qué tipo es la petición:

| Caso | Parámetro a usar |
|------|-----------------|
| El usuario da un tema/palabra clave en el nombre | `name_like` |
| El usuario menciona algo que aparece en la descripción | `description_like` |
| El usuario menciona keywords o etiquetas concretas | `keywords` |
| El usuario da IDs explícitos | `data_product_ids` |
| El usuario quiere actuar sobre lo importado en una fecha concreta | `created_after` / `created_before` |
| El usuario quiere publicar "todos" sin filtro | **No permitido** — pide al menos un criterio |

Los filtros son combinables entre sí (p.ej. `name_like` + `created_after`).

Si la petición es ambigua, formula **una sola pregunta** para clarificar el criterio.
No procedas si no tienes al menos un filtro claro.

---

## Fase 1 — Preview con dry_run

**Siempre** empieza con una llamada en modo dry_run para mostrar al usuario qué se va a publicar:

```
publish_data_products(
  name_like="<término>",         # si aplica
  description_like="<texto>",    # si aplica
  keywords=["<kw1>", ...],       # si aplica
  data_product_ids=[...],        # si aplica
  created_after="YYYY-MM-DD",    # si aplica
  created_before="YYYY-MM-DD",   # si aplica
  dry_run=true
)
```

Muestra el resultado al usuario:
- Si `total == 0`: informa que no hay productos que coincidan con los filtros y termina.
- Si `total > 0`: muestra la lista y el recuento.

---

## Fase 2 — Confirmación para operaciones masivas

- Si `total <= 10`: procede directamente sin pedir confirmación.
- Si `total > 10`: muestra el resumen y pide confirmación explícita:
  > "Se van a publicar **N dataproducts**. ¿Confirmas?"
  Espera la respuesta. No publiques sin confirmación cuando N > 10.

---

## Fase 3 — Publicar

Ejecuta la publicación con los mismos parámetros pero `dry_run=false` (o sin el parámetro):

```
publish_data_products(
  name_like="<término>",
  description_like="<texto>",
  keywords=["<kw1>", ...],
  data_product_ids=[...],
  created_after="YYYY-MM-DD",
  created_before="YYYY-MM-DD",
  dry_run=false
)
```

La tool maneja la paginación y publica en paralelo — una sola llamada es suficiente.

---

## Fase 4 — Informe de resultados

Tras la llamada, muestra al usuario:
- Cuántos se publicaron correctamente
- Cuántos fallaron (con el error)
- Si hay fallos, sugiere revisar el estado del DMP o reintentar con los IDs fallidos usando `data_product_ids`

Ejemplo de resumen:
```
✅ Publicados 23/25 dataproducts
❌ 2 errores:
  • [ID 101] Dataset biodiversidad marina — BPM timeout
  • [ID 208] Inventario especies — Permission denied
```

---

## Reglas

- **Si los IDs son conocidos de un paso anterior** (p.ej. vienen de un import report),
  usa siempre `data_product_ids` directamente — no hagas una búsqueda por nombre o descripción.
  Los IDs son exactos e inequívocos; una búsqueda puede devolver falsos positivos.
- Nunca publiques sin haber mostrado primero el dry_run al usuario.
- Si el usuario ya sabe exactamente qué quiere publicar (da IDs), el dry_run es opcional pero recomendado.
- No uses `search_data_products` por separado para luego publicar manualmente — usa siempre `publish_data_products` que lo hace internamente de forma más eficiente.
- Si el usuario quiere publicar "todos sin filtro", explica que es necesario al menos un criterio de selección para evitar publicaciones accidentales masivas.
