# create-sql-mappings

Crea o actualiza los SQL mappings de business views existentes en Stratio Governance **sin recrear las views** (y sin perder sus términos semánticos). **Fase 4 del pipeline de capa semántica.** Opcionalmente publica las views Draft afectadas después.

## Qué hace

- Resuelve el dominio técnico e inspecciona las views existentes (`list_technical_domain_concepts`) con su estado y presencia de mapping.
- Ofrece tres alcances: todas las views sin mapping (seguro), views específicas (pueden incluir views que ya tienen mapping, para actualizarlo) o un camino explícito de "actualizar mappings existentes".
- Ofrece al usuario la oportunidad de aportar `user_instructions` — incluyendo lectura de ficheros locales (diagramas ER, specs de integración, SQL de referencia) para inyectar reglas de JOIN, transformaciones y filtros de exclusión en el generador.
- Invoca `create_sql_mappings` y reporta el resumen; reintenta las views fallidas hasta dos veces con instrucciones mejoradas.
- Tras la actualización, ofrece la publicación opcional de las views Draft afectadas.

## Cuándo usarla

- Corregir un mapping que no refleja el SQL esperado.
- Añadir una columna que falta en un mapping o arreglar la lógica de JOIN sin reconstruir la view.
- Recuperar de una generación parcial de mappings (views creadas sin su mapping).
- Para regeneración end-to-end de view + mapping, prefiere `create-business-views` con `regenerate=true`.
- Para el pipeline completo, prefiere `build-semantic-layer`.

## Dependencias

### Otras skills
- **Prerrequisitos:** `create-data-collection`, `create-ontology`, `create-business-views` (las views deben existir).
- **Siguiente paso típico:** `create-semantic-terms`.

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Governance (`gov`):** `list_technical_domain_concepts`, `create_sql_mappings`, `publish_business_views`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **No destructiva a nivel de view:** `create_sql_mappings` solo reemplaza el SQL mapping. La view y sus términos semánticos se preservan.
- **Sobrescribe los mappings existentes** cuando una view se procesa de nuevo — es comportamiento esperado e intencionado.
- **La publicación** es opcional y solo se sugiere para las views que quedaron en Draft tras la actualización.
