# create-data-collection

Busca en el diccionario técnico de datos tablas y paths, y luego crea una nueva **data collection** (dominio técnico) en Stratio Governance agrupando los activos seleccionados. **Fase 0 del pipeline de capa semántica** — el contenedor sobre el que trabaja cada fase posterior (`create-technical-terms`, `create-ontology`, `create-business-views`, `create-sql-mappings`, `create-semantic-terms`, `build-semantic-layer`).

## Qué hace

- Toma una semilla de búsqueda de `$ARGUMENTS` o pregunta al usuario qué tipo de datos busca.
- Ejecuta `search_data_dictionary` iterativamente — funciona mejor con keywords cortos que con frases largas; el usuario puede refinar y acumular selecciones entre iteraciones.
- Permite selección mixta de `Table` y `Path` por número; mantiene un resumen corriente de los activos elegidos.
- Pide nombre (guiones bajos, sin caracteres especiales) y descripción, usando solo lo que el usuario proporciona o la metadata real de los activos seleccionados — sin inventar contexto de negocio.
- Verifica que el nombre no esté ya en uso (`search_domains` / `list_domains` con `domain_type='technical'`).
- Confirma con el usuario e invoca `create_data_collection`, separando la selección por `subtype` en `table_metadata_paths` y `path_metadata_paths`.
- Calienta la caché (`list_domains(domain_type='technical', refresh=true)`) para que la colección sea visible inmediatamente para la siguiente skill.

## Cuándo usarla

- El usuario quiere registrar un nuevo dominio técnico en Governance para agrupar un conjunto de tablas y paths.
- El usuario necesita el contenedor creado antes de invocar `build-semantic-layer` o cualquier skill `create-*`.
- **No** la uses para construir la capa semántica en sí misma — para eso, encadena con `build-semantic-layer` (o las skills individuales `create-*`).

## Dependencias

### Otras skills
- **Siguiente paso típico:** `build-semantic-layer` (recomendado) o `create-technical-terms` directamente.

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Data (`sql`):** `search_data_dictionary`, `search_domains`, `list_domains`.
- **Governance (`gov`):** `create_data_collection`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Convención de naming:** sin espacios, sin caracteres especiales (usa guiones bajos). Misma regla que los nombres de ontologías.
- **Búsqueda por keywords:** `search_data_dictionary` rinde mejor con términos cortos. Divide las frases en lenguaje natural en búsquedas separadas y acumula selecciones.
- **La creación no es idempotente** — ejecutarla dos veces con el mismo nombre produce conflicto. La skill comprueba preexistencia antes de invocar el MCP.
- **El calentamiento de caché es best-effort.** Si la llamada de refresh falla, se ignora; la colección puede tardar 1–2 minutos en propagarse y la siguiente skill reintentará con `refresh=true`.
- **No inventes contexto de negocio.** Descripciones y nombres salen del usuario o de la metadata real de las tablas seleccionadas — nunca de temas inferidos.
