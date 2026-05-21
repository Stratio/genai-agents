# create-ontology

Skill interactiva para crear, extender o borrar clases de una ontología en Stratio Governance. Fase 2 del pipeline de capa semántica: parte de un dominio técnico (y opcionalmente de ficheros de referencia del usuario) y produce un plan en Markdown revisado que se convierte en ontología a través de los MCPs de gobierno.

## Qué hace

- Descubre el dominio técnico (`search_domains` / `list_domains`) y las ontologías que ya puedan existir para él.
- Lee ficheros de referencia locales que proporcione el usuario (`.owl`, `.ttl`, CSVs, docs de negocio) para seed de propuestas de clases.
- Ejecuta un bucle de planning interactivo: propone clases, propiedades de datos, relaciones y tablas origen; itera con el usuario hasta tres veces hasta que el plan se aprueba.
- Crea una ontología nueva, extiende una existente con nuevas clases, o borra clases específicas (el camino destructivo siempre se confirma y las clases ligadas a business views Published se omiten automáticamente).
- También puede borrar la ontología **entera** cuando el flujo de recuperación tras best-effort requiere un reseteo limpio antes de reintentar — siempre con confirmación explícita del usuario.
- Acepta opcionalmente un argumento `best_effort` en `create_ontology` / `update_ontology` para que, tras un fallo de generación, el usuario pueda elegir entregar el último resultado intentado con warnings en vez de seguir reintentando.
- Verifica el resultado con `get_ontology_info` y reporta lo creado frente a lo planificado.

## Cuándo usarla

- El usuario quiere modelar un dominio nuevo como ontología antes de construir business views.
- Una ontología existente necesita nuevas clases (la extensión es ADD-only).
- Hay que eliminar clases obsoletas (con la protección habitual de Published views).
- Antes de ejecutar la skill: la colección técnica debe existir (`create-data-collection`). La Fase 1 (`create-technical-terms`) es recomendada pero no estrictamente obligatoria.
- No la uses para generar business views o SQL mappings — eso es `create-business-views` y `create-sql-mappings`.

## Dependencias

### Otras skills
- **Prerrequisito:** `create-data-collection` (el dominio técnico debe existir).
- **Recomendada antes:** `create-technical-terms` (las descripciones de tablas mejoran el plan de ontología).
- **Siguiente paso típico:** `create-business-views`.

### Guides
Ninguno. La skill lleva su referencia de MCPs inline en `SKILL.md`.

### MCPs
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `create_ontology`, `update_ontology`, `delete_ontology_classes`, `delete_ontology`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Operaciones destructivas:** `delete_ontology_classes` y `delete_ontology` requieren confirmación explícita del usuario. Las clases (y ontologías) con business views Published dependientes están protegidas — `delete_ontology_classes` las reporta como `skipped_locked`; `delete_ontology` rechaza la operación.
- **Clases inmutables:** las clases existentes no se pueden modificar. Para cambiar una clase hay que borrarla y recrearla (permitido solo si ninguna Published view depende de ella).
- **Entrega best-effort:** `create_ontology` / `update_ontology` aceptan un argumento opcional `best_effort`. Cuando el usuario lo activa tras un fallo de generación, la chain entrega la última ontología/vistas intentadas con líneas `` `Warning (best-effort):` `` en el mensaje de respuesta en lugar de detenerse. La elección entre modo estricto y best-effort forma parte del flujo de recuperación tras error documentado en `SKILL.md` §4.b. Best-effort solo afecta a cómo se gestionan los rechazos de calidad durante la generación de clases/vistas; los fallos previos a la generación (plan no alcanzable con las tablas disponibles, se exceden topes de tablas/tamaño, servicios de governance no disponibles) siguen provocando el fallo de la llamada igualmente.
- **Naming:** sin espacios (usar guiones bajos), sin caracteres especiales. Misma convención que las colecciones.
- **Contexto de planificación construido mediante §11:** antes de proponer el plan de ontología en Markdown, la skill ejecuta el Workflow de Enriquecimiento con Instrucciones del Glosario (`stratio-semantic-layer-tools.md` §11), de modo que el usuario puede traerse las GenAI Ontology Instructions del diccionario de datos, aportar un fichero externo (`.owl` / `.ttl` / doc de negocio / CSV), añadir reglas en texto libre, o saltar el enriquecimiento. `create_ontology` / `update_ontology` no aceptan `user_instructions` hoy, así que el texto consolidado se incorpora al plan Markdown en su lugar.
