---
name: propose-knowledge
description: Analizar la conversacion para proponer terminos de negocio y preferencias descubiertos a la capa de `Stratio Governance` del dominio. Usar cuando el usuario quiera enriquecer el semantic layer con definiciones, reglas o preferencias descubiertas durante un analisis.
argument-hint: [dominio (opcional)]
---

# Skill: Propuesta de Conocimiento a Gobernanza

Guia para analizar una conversacion de analisis y proponer conocimiento de negocio descubierto al semantic layer de `Stratio Governance`.

## 1. Determinar Dominio

- Si `$ARGUMENTS` contiene un nombre de dominio, validarlo contra `stratio_list_business_domains` antes de usarlo. Usar el nombre exacto del listado, no la interpretacion del usuario
- Si no, inferir el dominio de la conversacion actual (buscar llamadas previas a MCPs con `domain_name`)
- Si no es posible inferirlo, listar dominios disponibles via `stratio_list_business_domains` y preguntar al usuario siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md)

## 2. Recopilar Contexto de la Conversacion

Revisar `output/MEMORY.md` sec "Patrones de Datos Conocidos" — si hay patrones maduros del dominio (observados 3+ veces), considerar incluirlos como candidatos a propuesta de conocimiento gobernado.

Analizar TODO lo ocurrido en la conversacion — pregunta original, plan de analisis, datos obtenidos, calculos realizados, insights descubiertos, conclusiones y recomendaciones.

Clasificar los hallazgos en dos categorias:

### 2.1 Definiciones de negocio
- Terminos de negocio usados o descubiertos (ej: "Clientes VIP", "Tasa de retencion")
- Segmentaciones aplicadas (ej: "Top 10% por facturacion")
- Umbrales o criterios (ej: "Churn: sin compras en 90 dias")
- Metricas con formula (ej: "ARPU = ingresos totales / usuarios activos")

### 2.2 Preferencias

**REGLA CRITICA**: Solo proponer preferencias **especificas del dominio de datos**. NUNCA proponer preferencias de workflow, sesion o formato de analisis — estas son opciones transitorias que el usuario elige en cada analisis (Fase 2 del workflow) y no constituyen conocimiento reutilizable del dominio.

#### 2.2.1 Exclusiones explicitas

Las siguientes categorias NUNCA se proponen como conocimiento de dominio:

| Categoria | Ejemplos | Origen (no es conocimiento de dominio) |
|-----------|----------|----------------------------------------|
| Formatos de salida | PDF, Web, PowerPoint | Bloque 2, Fase 2 del workflow |
| Estilo visual | Corporativo, Academico, Moderno | Bloque 2, Fase 2 del workflow |
| Estructura de reporte | Scaffold, Al vuelo | Bloque 2, Fase 2 del workflow |
| Audiencia | C-level, Manager, Tecnico | Bloque 1, Fase 2 del workflow |
| Profundidad de analisis | Rapido, Estandar, Profundo | Bloque 1, Fase 2 del workflow |

#### 2.2.2 Que SI proponer como preferencia

**Criterio de validacion**: La preferencia debe mencionar tablas, columnas o metricas especificas del dominio. Si aplica a cualquier dominio de forma generica → descartar.

- Patrones SQL especificos del dominio (ej: "LEFT JOIN entre clientes y pedidos en el dominio retail porque pedidos tiene clientes sin registro")
- Preferencias de visualizacion ligadas a metricas del dominio (ej: "Heatmap para matriz de retencion por cohorte en la tabla suscripciones")
- Convenciones de filtrado del dominio (ej: "Excluir registros con estado='TEST' en la tabla transacciones")

## 3. Consultar Metadata Existente

Antes de proponer, verificar que no se duplique conocimiento ya gobernado:

1. Usar `stratio_get_tables_details(domain_name, table_names)` para revisar terminos de negocio ya definidos en las tablas relevantes
2. Usar `stratio_search_domain_knowledge(question, domain_name)` para buscar cada termino/concepto candidato

Para cada hallazgo:
- **Ya existe con misma definicion** (aunque redaccion diferente): Descartar (no proponer duplicado)
- **Ya existe con definicion diferente**: Proponer actualizacion SOLO si la nueva definicion aporta informacion sustancialmente nueva (formula, umbral, contexto adicional). No proponer si es simplemente una reformulacion
- **No existe**: Proponer como nuevo

## 4. Priorizar y Limitar Propuestas

**Limite total: maximo 5 propuestas por ejecucion** (excepcionalmente 6 si hay un sexto `business_concept` de alta relevancia).

Clasificar cada propuesta candidata segun esta tabla de prioridades:

| Prioridad | Tipo | Criterio de inclusion | Limite |
|-----------|------|----------------------|--------|
| **P1 — Critica** | `business_concept` (nuevo) | Termino descubierto o definido en el analisis que NO existe en el dominio gobernado | Max 3 |
| **P2 — Alta** | `business_concept` (actualizacion) | Termino que ya existe pero con definicion diferente/mejorada | Max 2 |
| **P3 — Media** | `sql_preference` | Patron SQL descubierto que mejora las queries del dominio | Max 1 |
| **P3 — Media** | `chart_preference` | Preferencia de visualizacion especifica del dominio | Max 1 |

Si hay mas candidatos que el limite, aplicar prioridad (P1 primero) y dentro de cada prioridad, ordenar por relevancia para la pregunta original del usuario.

### Criterios de calidad para business_concept

Un `business_concept` solo se propone si cumple **AL MENOS 2** de estos criterios:
- Tiene una **definicion precisa** con formula o umbral numerico
- Fue **usado activamente** en el analisis (no solo mencionado)
- Es **relevante para el dominio** (aplica a tablas/columnas existentes)
- Fue **definido explicitamente** por el usuario en la conversacion

Si un candidato no cumple al menos 2 criterios, descartarlo y documentar el motivo en el reporte.

## 5. Preparar Propuestas

Clasificar cada propuesta en uno de los 3 tipos soportados:

| Tipo | Descripcion | Ejemplo |
|------|-------------|---------|
| `business_concept` | Definiciones de terminos, segmentaciones, metricas, umbrales | "Clientes VIP: facturacion anual > 10.000 EUR" |
| `sql_preference` | Patrones SQL preferidos | "LEFT JOIN para clientes-pedidos" |
| `chart_preference` | Preferencias de visualizacion | "Area charts para series temporales, barras para categorias" |

Para cada propuesta, documentar:
- **Tipo**: Uno de los 3 anteriores
- **Prioridad**: P1, P2 o P3
- **Nombre**: Nombre corto del termino o preferencia
- **Definicion**: Descripcion completa y precisa
- **Contexto**: Cita o referencia de donde surgio en el analisis
- **Tablas relacionadas**: Tablas del dominio donde aplica (si corresponde)

## 6. Presentar al Usuario para Aprobacion

Mostrar las propuestas organizadas por prioridad y tipo al usuario. Para cada una, indicar:
- Prioridad (P1/P2/P3)
- Tipo
- Nombre
- Definicion
- Contexto (de donde surgio)
- Tablas relacionadas

Preguntar al usuario siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md) (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no):
- **Enviar todas**: Proponer todo tal como esta
- **Seleccionar**: El usuario indica cuales enviar (preguntar permitiendo seleccion multiple)
- **Modificar**: El usuario quiere ajustar alguna definicion antes de enviar
- **Cancelar**: No proponer nada

Si el usuario elige "Modificar", preguntar que cambios quiere hacer, aplicarlos y volver a presentar para aprobacion.

## 7. Enviar via MCP

Para las propuestas aprobadas, llamar a `stratio_propose_knowledge(business_context=..., domain_name=...)`.

El parametro `business_context` debe ser un texto markdown estructurado con el siguiente formato:

```markdown
## Propuestas de Conocimiento

### business_concept
- **[Nombre del termino]**: [Definicion completa]
  - Contexto: [De donde surgio en el analisis]
  - Tablas relacionadas: [tabla1, tabla2]

### sql_preference
- **[Nombre de la preferencia]**: [Descripcion del patron SQL]
  - Contexto: [De donde surgio]

### chart_preference
- **[Nombre de la preferencia]**: [Descripcion de la preferencia visual]
  - Contexto: [De donde surgio]
```

Solo incluir las secciones que tengan propuestas. No incluir secciones vacias.

## 8. Reporte

Presentar al usuario un resumen final:

- Propuestas enviadas desglosadas por prioridad (P1/P2/P3) y tipo
- Resumen de cada propuesta enviada
- Propuestas descartadas y motivo (duplicado, baja prioridad, no cumple criterios de calidad)
- Errores encontrados (si los hubo)
- Nota: "Las propuestas seran revisadas por un administrador en la consola de Gobernanza antes de integrarse al semantic layer del dominio"
