---
name: propose-knowledge
description: "Analizar la conversación para proponer business terms, definiciones y preferencias descubiertas a la capa de Stratio Governance del dominio. Usar cuando el usuario quiera enriquecer la capa semántica, guardar una definición encontrada durante el análisis, registrar que un concepto significa X, persistir una regla o preferencia, o añadir un término a governance. Para términos autorizados explícitamente con relaciones, preferir manage-business-terms."
argument-hint: "[dominio (opcional)]"
---

# Skill: Propuesta de Conocimiento a Gobernanza

Guía para analizar una conversación de análisis y proponer conocimiento de negocio descubierto al semantic layer de `Stratio Governance`.

## 1. Determinar Dominio

- Si `$ARGUMENTS` contiene un nombre de dominio, validarlo con `search_domains($ARGUMENTS)` antes de usarlo. Usar el nombre exacto del resultado, no la interpretación del usuario
- Si no, inferir el dominio de la conversación actual (buscar llamadas previas a MCPs con `domain_name`)
- Si no es posible inferirlo, listar dominios disponibles vía `list_domains()` y preguntar al usuario siguiendo la convención de preguntas al usuario (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no)

## 2. Recopilar Contexto de la Conversación

Revisar `output/MEMORY.md` sec "Patrones de Datos Conocidos" si existe — si hay patrones maduros del dominio (observados 3+ veces), considerar incluirlos como candidatos a propuesta de conocimiento gobernado.

Analizar TODO lo ocurrido en la conversación — pregunta original, plan de análisis, datos obtenidos, cálculos realizados, insights descubiertos, conclusiones y recomendaciones.

Clasificar los hallazgos en dos categorías:

### 2.1 Definiciones de negocio
- Términos de negocio usados o descubiertos (ej: "Clientes VIP", "Tasa de retención")
- Segmentaciones aplicadas (ej: "Top 10% por facturación")
- Umbrales o criterios (ej: "Churn: sin compras en 90 días")
- Métricas con fórmula (ej: "ARPU = ingresos totales / usuarios activos")

### 2.2 Preferencias

**REGLA CRITICA**: Solo proponer preferencias **específicas del dominio de datos**. NUNCA proponer preferencias de workflow, sesión o formato de análisis — estas son opciones transitorias que el usuario elige en cada análisis (Fase 2 del workflow) y no constituyen conocimiento reutilizable del dominio.

#### 2.2.1 Exclusiones explícitas

Las siguientes categorías NUNCA se proponen como conocimiento de dominio:

| Categoría | Ejemplos | Origen (no es conocimiento de dominio) |
|-----------|----------|----------------------------------------|
| Formatos de salida | PDF, Web, PowerPoint | Bloque 2, Fase 2 del workflow |
| Estilo visual | Corporativo, Académico, Moderno | Bloque 2, Fase 2 del workflow |
| Estructura de reporte | Scaffold, Al vuelo | Bloque 2, Fase 2 del workflow |
| Audiencia | C-level, Manager, Técnico | Bloque 1, Fase 2 del workflow |
| Profundidad de análisis | Rápido, Estándar, Profundo | Bloque 1, Fase 2 del workflow |

#### 2.2.2 Que SI proponer como preferencia

**Criterio de validación**: La preferencia debe mencionar tablas, columnas o métricas específicas del dominio. Si aplica a cualquier dominio de forma genérica → descartar.

- Patrones SQL específicos del dominio (ej: "LEFT JOIN entre clientes y pedidos en el dominio retail porque pedidos tiene clientes sin registro")
- Preferencias de visualización ligadas a métricas del dominio (ej: "Heatmap para matriz de retención por cohorte en la tabla suscripciones")
- Convenciones de filtrado del dominio (ej: "Excluir registros con estado='TEST' en la tabla transacciones")

## 3. Consultar Metadata Existente

Antes de proponer, verificar que no se duplique conocimiento ya gobernado:

1. Usar `get_tables_details(domain_name, table_names)` para revisar términos de negocio ya definidos en las tablas relevantes
2. Usar `search_domain_knowledge(question, domain_name)` para buscar cada término/concepto candidato

Para cada hallazgo:
- **Ya existe con misma definición** (aunque redaccion diferente): Descartar (no proponer duplicado)
- **Ya existe con definición diferente**: Proponer actualizacion SOLO si la nueva definición aporta información sustancialmente nueva (fórmula, umbral, contexto adicional). No proponer si es simplemente una reformulacion
- **No existe**: Proponer como nuevo

## 4. Priorizar y Limitar Propuestas

**Limite total: máximo 5 propuestas por ejecución** (excepcionalmente 6 si hay un sexto `business_concept` de alta relevancia).

Clasificar cada propuesta candidata según esta tabla de prioridades:

| Prioridad | Tipo | Criterio de inclusion | Limite |
|-----------|------|----------------------|--------|
| **P1 — Crítica** | `business_concept` (nuevo) | Término descubierto o definido en el análisis que NO existe en el dominio gobernado | Max 3 |
| **P2 — Alta** | `business_concept` (actualizacion) | Término que ya existe pero con definición diferente/mejorada | Max 2 |
| **P3 — Media** | `sql_preference` | Patrón SQL descubierto que mejora las queries del dominio | Max 1 |
| **P3 — Media** | `chart_preference` | Preferencia de visualización específica del dominio | Max 1 |

Si hay más candidatos que el limite, aplicar prioridad (P1 primero) y dentro de cada prioridad, ordenar por relevancia para la pregunta original del usuario.

### Criterios de calidad para business_concept

Un `business_concept` solo se propone si cumple **AL MENOS 2** de estos criterios:
- Tiene una **definición precisa** con fórmula o umbral numérico
- Fue **usado activamente** en el análisis (no solo mencionado)
- Es **relevante para el dominio** (aplica a tablas/columnas existentes)
- Fue **definido explícitamente** por el usuario en la conversación

Si un candidato no cumple al menos 2 criterios, descartarlo y documentar el motivo en el reporte.

## 5. Preparar Propuestas

Clasificar cada propuesta en uno de los 3 tipos soportados:

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `business_concept` | Definiciones de términos, segmentaciones, métricas, umbrales | "Clientes VIP: facturación anual > 10.000 EUR" |
| `sql_preference` | Patrones SQL preferidos | "LEFT JOIN para clientes-pedidos" |
| `chart_preference` | Preferencias de visualización | "Área charts para series temporales, barras para categorías" |

Para cada propuesta, documentar:
- **Tipo**: Uno de los 3 anteriores
- **Prioridad**: P1, P2 o P3
- **Nombre**: Nombre corto del término o preferencia
- **Definición**: Descripción completa y precisa
- **Contexto**: Cita o referencia de donde surgio en el análisis
- **Tablas relacionadas**: Tablas del dominio donde aplica (si corresponde)

## 6. Presentar al Usuario para Aprobación

Mostrar las propuestas organizadas por prioridad y tipo al usuario. Para cada una, indicar:
- Prioridad (P1/P2/P3)
- Tipo
- Nombre
- Definición
- Contexto (de donde surgio)
- Tablas relacionadas

Preguntar al usuario siguiendo la convención de preguntas al usuario (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no):
- **Enviar todas**: Proponer todo tal como está
- **Seleccionar**: El usuario indica cuales enviar (preguntar permitiendo selección múltiple)
- **Modificar**: El usuario quiere ajustar alguna definición antes de enviar
- **Cancelar**: No proponer nada

Si el usuario elige "Modificar", preguntar que cambios quiere hacer, aplicarlos y volver a presentar para aprobación.

## 7. Enviar vía MCP

Para las propuestas aprobadas, llamar a `propose_knowledge(business_context=..., domain_name=...)`.

El parámetro `business_context` debe ser un texto markdown estructurado con el siguiente formato:

```markdown
## Propuestas de Conocimiento

### business_concept
- **[Nombre del término]**: [Definición completa]
  - Contexto: [De dónde surgió en el análisis]
  - Tablas relacionadas: [tabla1, tabla2]

### sql_preference
- **[Nombre de la preferencia]**: [Descripción del patrón SQL]
  - Contexto: [De donde surgio]

### chart_preference
- **[Nombre de la preferencia]**: [Descripción de la preferencia visual]
  - Contexto: [De donde surgio]
```

Solo incluir las secciones que tengan propuestas. No incluir secciones vacias.

## 8. Reporte

Presentar al usuario un resumen final:

- Propuestas enviadas desglosadas por prioridad (P1/P2/P3) y tipo
- Resumen de cada propuesta enviada
- Propuestas descartadas y motivo (duplicado, baja prioridad, no cumple criterios de calidad)
- Errores encontrados (si los hubo)
- Nota: "Las propuestas serán revisadas por un administrador en la consola de Gobernanza antes de integrarse al semantic layer del dominio"
