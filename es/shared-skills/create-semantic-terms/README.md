# create-semantic-terms

Genera o regenera **términos semánticos** (descripciones orientadas a negocio de views y sus columnas) en el glosario de Stratio Governance. **Fase 5 del pipeline de capa semántica** — el paso final antes de que la capa semántica esté lista para revisión.

## Qué hace

- Resuelve el dominio técnico e inspecciona las views existentes con su estado, mappings y términos semánticos (`list_technical_domain_concepts`).
- Impone el prerrequisito: **las views deben tener un SQL mapping** para producir términos semánticos. Las views sin mapping se muestran y se excluyen, con un puntero a `create-sql-mappings` o `create-business-views`.
- Ofrece cuatro opciones de alcance: crear para views sin términos (idempotente), un subconjunto específico, regeneración completa (destructiva) o regeneración de views seleccionadas (destructiva).
- Ofrece al usuario la oportunidad de aportar `user_instructions` — incluyendo lectura de ficheros locales (glosarios de negocio, docs funcionales, guías de estilo terminológico) para guiar al generador.
- Invoca `create_semantic_terms` y reporta el resumen; reintenta las views fallidas hasta dos veces con instrucciones mejoradas.

## Cuándo usarla

- Poblar términos semánticos por primera vez cuando el pipeline llega a Fase 4.
- Refrescar términos tras cambios en la ontología o en las views.
- Recuperar términos que faltan tras una generación parcial.
- Para entradas de diccionario de negocio (KPIs, conceptos, acrónimos) que cruzan múltiples activos, prefiere `manage-business-terms` — ese es un artefacto de gobierno distinto.

## Dependencias

### Otras skills
- **Prerrequisitos:** el stack completo hasta la Fase 4 (`create-data-collection` → `create-technical-terms` → `create-ontology` → `create-business-views` → `create-sql-mappings`).
- **Siguiente paso opcional:** `manage-business-terms` para enriquecer el diccionario con conceptos transversales.

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Governance (`gov`):** `list_technical_domain_concepts`, `create_semantic_terms`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **`regenerate=true` es destructivo.** Confirmación explícita obligatoria; los términos existentes de las views seleccionadas se borran y recrean.
- **Prerrequisito duro: debe existir mapping.** La skill rehúsa operar sobre views sin SQL mapping y apunta a la skill de remediación.
- **La capa semántica se considera completa** una vez tiene éxito esta fase. Si las views siguen en Draft, el usuario puede publicarlas vía UI de Governance o pidiéndoselo al agente.
