---
name: create-semantic-terms
description: Generar o regenerar terminos semanticos de negocio en el glosario de Stratio
  Governance para las vistas de negocio de un dominio.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Crear Terminos Semanticos

Genera o regenera terminos semanticos de negocio en el glosario de Stratio Governance para las vistas de negocio de un dominio. Fase 5 del pipeline de capa semantica.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `list_technical_domains` | sql | Descubrir dominios tecnicos disponibles |
| `list_technical_domain_concepts(domain)` | gov | Listar vistas con estado de terminos semanticos y mappings |
| `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | gov | Crear terminos semanticos. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |

**Reglas clave**: `domain_name` inmutable. Confirmacion obligatoria para `regenerate=true`. Ofrecer `user_instructions` antes de invocar. Pre-requisito: las vistas deben tener SQL mapping antes de generar terminos semanticos.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, validar contra `list_technical_domains`. Si no, listar y preguntar al usuario siguiendo la convencion de preguntas al usuario.

### 2. Evaluar estado

Ejecutar `list_technical_domain_concepts(domain)` para obtener el listado de vistas con su estado de terminos semanticos y mappings.

Presentar resumen:
```
## Terminos Semanticos — [domain_name]
| Vista | Mapping | Terminos semanticos |
|-------|---------|---------------------|
| Vista1 | ✓ | ✓ |
| Vista2 | ✓ | ✗ |
| Vista3 | ✗ | — |
```

### 3. Verificar pre-requisito

Las vistas necesitan SQL mapping para poder generar terminos semanticos. Si hay vistas sin mapping:
- Advertir al usuario: "Las siguientes vistas no tienen mapping SQL: [lista]. No se pueden generar terminos semanticos para ellas."
- Sugerir: "Usa `/create-sql-mappings` o `/create-business-views` para generar los mappings primero"
- Continuar solo con las vistas que tienen mapping

### 4. Seleccion de alcance

Preguntar al usuario con opciones (solo vistas con mapping):
1. **Crear para vistas sin terminos** — idempotente
2. **Vistas especificas** — seleccion multiple
3. **Regenerar todas** — DESTRUCTIVO: borra terminos existentes y recrea. Requiere confirmacion explicita
4. **Regenerar vistas especificas** — DESTRUCTIVO para las seleccionadas. Requiere confirmacion

### 5. user_instructions

Ofrecer al usuario la oportunidad de aportar contexto adicional:
- **Ficheros locales**: Si el usuario tiene glosarios de negocio, documentacion funcional o guias de estilo terminologico → **leerlos** y extraer definiciones relevantes para incluirlas como contexto
- **Definiciones de dominio**: Significado de negocio de conceptos clave, relaciones entre entidades, reglas que la IA deberia reflejar en los terminos
- Ejemplos: "El concepto 'actor' en este dominio se refiere a actores de cine, no a actores del sistema", "Las vistas de `film` deben reflejar que rental_rate es el precio de alquiler por dia"

No sugerir opciones que la tool controla internamente (idioma, audiencia, formato). Si el usuario no aporta instrucciones, continuar sin el parametro. No es bloqueante.

### 6. Ejecucion

Invocar `create_semantic_terms`. Para regenerar: pasar `regenerate=true` (DESTRUCTIVO). La tool devuelve un resumen de lo procesado — presentar al usuario directamente.

Si hay errores, reintentar la vista fallida con `user_instructions` mejoradas (max 2 reintentos). Si persiste, documentar y continuar.

### 7. Resumen

Basado en la respuesta de la tool:
- Terminos creados/regenerados
- Errores si los hubo
- Siguiente paso sugerido: "La capa semantica esta lista para revision en la UI de Governance. Puedes crear business terms con `/manage-business-terms` para enriquecer el diccionario"
