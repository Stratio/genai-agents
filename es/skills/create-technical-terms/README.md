# create-technical-terms

Crea o regenera descripciones técnicas (tablas y columnas) para un dominio técnico en Stratio Governance. **Fase 1 del pipeline de capa semántica.** También semilla la descripción de la colección cuando falta — no hay que invocar `create_collection_description` aparte.

## Qué hace

- Resuelve el dominio técnico (`search_domains` con `domain_type='technical'`, con fallback a `list_domains`).
- Reporta el estado actual: total de tablas, ya documentadas, pendientes, y si la colección tiene descripción.
- Ofrece cuatro opciones de alcance: todas las tablas pendientes (idempotente), un subconjunto específico, regeneración completa (destructiva) o regeneración de tablas específicas (destructiva).
- Construye `user_instructions` mediante el **Workflow de Enriquecimiento con Instrucciones del Glosario** (`stratio-semantic-layer-tools.md` §11): el usuario puede traerse las GenAI Technical Term Instructions del diccionario de datos (específicas de la fase, opcionalmente más globales), aportar un fichero externo (diccionarios de datos, specs, glosarios), superponer reglas en texto libre, o saltar el enriquecimiento por completo.
- Invoca `create_technical_terms` y reporta el resumen directamente; reintenta las entidades fallidas hasta dos veces con instrucciones mejoradas.

## Cuándo usarla

- Generar bulk de términos técnicos para una colección recién creada.
- Refrescar términos tras un cambio de esquema que añade tablas o columnas nuevas.
- Recuperar términos técnicos tras una ejecución parcial.
- Documentar una colección existente que fue importada pero nunca descrita.
- Para el pipeline end-to-end, prefiere `build-semantic-layer` — incluye la Fase 1 como primer paso.

## Dependencias

### Otras skills
- **Prerrequisito:** `create-data-collection` (el dominio técnico debe existir).
- **Siguiente paso típico:** `create-ontology`.
- **Seguimiento típico:** `refine-foreign-keys` para ediciones quirúrgicas de claves foráneas virtuales (añadir / modificar / eliminar) sin regenerar los términos técnicos.

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Governance (`gov`):** `create_technical_terms`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **`regenerate=true` es destructivo.** Confirmación explícita obligatoria; las descripciones existentes se borran y recrean.
- **Idempotente por defecto:** la herramienta omite las tablas que ya tienen descripción salvo que se pase `regenerate=true`.
- **La descripción de la colección se genera automáticamente** la primera vez, por lo que no hay un paso dedicado.
- **`user_instructions` se construye mediante §11**, el Workflow de Enriquecimiento con Instrucciones del Glosario definido en `stratio-semantic-layer-tools.md`. Nunca inyecta contenido del glosario silenciosamente; nunca pregunta por idioma ni formato de salida (se controlan internamente) — solo por contexto de dominio, definiciones de negocio y reglas de naming.
