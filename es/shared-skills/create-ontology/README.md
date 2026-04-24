# create-ontology

Skill interactiva para crear, extender o borrar clases de una ontología en Stratio Governance. Fase 2 del pipeline de capa semántica: parte de un dominio técnico (y opcionalmente de ficheros de referencia del usuario) y produce un plan en Markdown revisado que se convierte en ontología a través de los MCPs de gobierno.

## Qué hace

- Descubre el dominio técnico (`search_domains` / `list_domains`) y las ontologías que ya puedan existir para él.
- Lee ficheros de referencia locales que proporcione el usuario (`.owl`, `.ttl`, CSVs, docs de negocio) para seed de propuestas de clases.
- Ejecuta un bucle de planning interactivo: propone clases, propiedades de datos, relaciones y tablas origen; itera con el usuario hasta tres veces hasta que el plan se aprueba.
- Crea una ontología nueva, extiende una existente con nuevas clases, o borra clases específicas (el camino destructivo siempre se confirma y las clases ligadas a business views Published se omiten automáticamente).
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
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `create_ontology`, `update_ontology`, `delete_ontology_classes`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Operación destructiva:** `delete_ontology_classes` requiere confirmación explícita del usuario. Las clases con business views Published dependientes se omiten automáticamente (reportadas como `skipped_locked`).
- **Clases inmutables:** las clases existentes no se pueden modificar. Para cambiar una clase hay que borrarla y recrearla (permitido solo si ninguna Published view depende de ella).
- **Naming:** sin espacios (usar guiones bajos), sin caracteres especiales. Misma convención que las colecciones.
- **`user_instructions`:** la skill siempre ofrece al usuario la oportunidad de aportar contexto extra (glosarios, docs de negocio) antes de invocar la herramienta de creación; si el usuario proporciona rutas de ficheros, la skill los lee e inyecta el contenido en el plan.
