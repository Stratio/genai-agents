# create-business-views

Crea, regenera, borra y opcionalmente publica business views (con sus SQL mappings) en Stratio Governance, a partir de una ontología existente. **Fase 3 del pipeline de capa semántica.** Los SQL mappings se generan automáticamente junto con cada view.

## Qué hace

- Resuelve el dominio técnico y la ontología objetivo (`search_ontologies` o `list_ontologies`).
- Reporta el estado actual en paralelo: clases de la ontología (`get_ontology_info`) vs. views ya creadas (`list_technical_domain_concepts`), con su estado de gobierno, mapping y términos semánticos.
- Ofrece cinco operaciones: crear views para clases sin view (idempotente), crear para clases específicas, regenerar todo (destructivo), regenerar views seleccionadas (destructivo) o borrar views específicas sin recrear.
- Tras crear o regenerar, ofrece un paso opcional de publicación (`publish_business_views`) para pasar views de Draft a Pending Publish.

## Cuándo usarla

- Generar business views por primera vez a partir de una ontología revisada.
- Reconstruir views tras extender la ontología con nuevas clases.
- Eliminar views obsoletas (las Published se omiten automáticamente).
- Publicar un lote de views Draft tras la creación.
- Para ajustes solo de SQL sin recrear la view, prefiere `create-sql-mappings`.
- Para el pipeline end-to-end, prefiere `build-semantic-layer`.

## Dependencias

### Otras skills
- **Prerrequisitos:** `create-data-collection` y `create-ontology`.
- **Siguientes pasos típicos:** `create-sql-mappings` (para refinar los mappings) o `create-semantic-terms`.

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `list_technical_domain_concepts`, `create_business_views`, `delete_business_views`, `publish_business_views`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Los mappings se autogeneran** junto con las views. Usa `create-sql-mappings` después solo si hay que ajustar un mapping manualmente.
- **`regenerate=true` es destructivo** y también elimina los términos semánticos asociados. Confirmación explícita obligatoria.
- **Las views Published están protegidas** — `delete_business_views` las reporta como `skipped_published`.
- **`user_instructions` está pendiente de implementación en la herramienta** al momento de escribir esto; la skill ya soporta el parámetro para cuando esté disponible.
- **Publicar es un cambio de estado de gobierno** (no destructivo) pero aún requiere aprobación explícita del usuario y reporta `published` / `failed` / `not_found`.
