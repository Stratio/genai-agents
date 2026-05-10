---
name: stratio-semantic-layer
description: "Referencia de MCPs de capa semántica Stratio — reglas obligatorias, patrones de uso y buenas prácticas para las herramientas MCP de gobernanza (create_ontology, create_business_views, create_sql_mappings, create_semantic_terms, create_business_term, etc.). Cargar antes de interactuar con tools de gobernanza sin una skill dedicada, cuando haya dudas sobre el orden de invocación o los parámetros, o para refrescar las reglas de uso. Para un flujo concreto, preferir la skill create-* correspondiente."
argument-hint: ""
---

# Stratio Semantic Layer — Referencia de MCPs de gobernanza

Carga esta skill cuando vayas a trabajar con herramientas MCP de gobernanza semántica de Stratio:
crear ontologías, generar términos técnicos, construir vistas de negocio, mappings SQL o términos
semánticos. Contiene las reglas obligatorias, patrones de uso y buenas prácticas para todas las
herramientas MCP de gobernanza (create_ontology, create_business_views,
create_technical_terms, etc.).

**Cuando invocarla**: Antes de la primera interacción con cualquier tool de gobernanza semántica
en una conversación, o cuando necesites refrescar las reglas de uso (domain_name inmutable,
user_instructions, confirmación de destructivas, ontologías ADD+DELETE, detección de estado).

Leer `skills-guides/stratio-semantic-layer-tools.md` para la referencia completa.
