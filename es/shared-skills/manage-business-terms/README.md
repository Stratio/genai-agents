# manage-business-terms

Crea business terms (singular o batch) en el diccionario de Stratio Governance con relaciones a activos de datos. Incluye un paso de planning guiado para definir nombre, descripción, tipo y activos relacionados a la granularidad correcta (collection / table / column).

Opera tanto contra dominios **técnicos** como **semánticos** (`semantic_*`) — los business terms abarcan todo el diccionario, no una sola capa.

## Qué hace

- Resuelve el dominio objetivo (técnico o semántico) y pregunta al usuario qué término(s) crear.
- Ejecuta un paso de planning guiado por término: propone o pide nombre y descripción en Markdown, lista los tipos de activo vía `list_business_asset_types` y ayuda al usuario a elegir la granularidad de activos relacionados:
  - aplica a columnas específicas → relacionar a columnas;
  - aplica a tablas específicas → relacionar a tablas;
  - aplica a más de ~2 tablas del mismo dominio → relacionar a la colección.
- Presenta el término completo para aprobación del usuario y permite ediciones antes de ejecutar.
- Soporta **modo batch**: planificar una lista de términos, aprobarlos juntos, crearlos secuencialmente y reportar resultados al final.
- Reintenta creaciones fallidas con ajustes (máx. 2 reintentos por término).

## Cuándo usarla

- Documentar un KPI, concepto o acrónimo surgido durante un análisis.
- Enlazar un concepto de negocio existente a tablas y columnas concretas en el diccionario.
- Registrar un término que abarca varias tablas del mismo dominio (relacionar a la colección).
- Registrar en bulk un glosario de business terms para un dominio nuevo (modo batch).
- Para descripciones automáticas de views, prefiere `create-semantic-terms` — ese es el equivalente a nivel de view.
- Para proponer conceptos *candidatos* durante exploración, prefiere `propose-knowledge`.

## Dependencias

### Otras skills
- **Predecesores típicos:** `explore-data` o `assess-quality` (afloran los conceptos a documentar).
- **Relacionadas:** `create-semantic-terms` (descripciones a nivel de view), `propose-knowledge` (propuestas antes de creación formal).

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Governance (`gov`):** `list_business_asset_types`, `create_business_term`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_table_columns_details`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Los términos se crean en estado Draft** y deben revisarse en la UI de Governance antes de publicación.
- **La granularidad la decide el usuario.** La skill presenta una recomendación basada en a cuántos activos aplica el término, pero respeta la decisión final.
- **Se aceptan dominios técnicos y semánticos** — `domain_name` puede ser `my_collection` o `semantic_my_collection` según dónde deba vivir el término.
- **Agrupar vs. separar** es una decisión de planning: la skill pregunta si fundir conceptos relacionados en un único término o mantenerlos separados.
