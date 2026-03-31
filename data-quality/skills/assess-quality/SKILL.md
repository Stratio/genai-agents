---
name: assess-quality
description: Evaluar la cobertura actual de calidad del dato para un dominio completo, una tabla especifica o una columna concreta. Devuelve un analisis de que dimensiones estan cubiertas, cuales faltan y cuales columnas son prioritarias para nuevas reglas. Usar cuando el usuario quiera conocer el estado de la calidad de sus datos.
argument-hint: [dominio] [tabla (opcional)] [columna (opcional)]
---

# Skill: Evaluacion de Cobertura de Calidad

Workflow completo para evaluar el estado de la calidad del dato en un dominio, tabla o columna gobernada.

## 1. Determinacion de Scope

Antes de ejecutar ninguna llamada MCP, determinar exactamente que se va a evaluar:

**Si el dominio no está claro o hay que validar el `domain_name`**: seguir `skills-guides/stratio-data-tools.md` sec 4.1-4.2 para el workflow estándar de discovery. Si el dominio es tecnico, usar `list_technical_domains` en lugar de `list_business_domains` (ver `skills-guides/exploration.md` sec 1 para la excepcion local de dominios tecnicos). Tener en cuenta que el analisis semantico sera mas limitado en dominios tecnicos: las descripciones de negocio, contexto de tablas y terminologia pueden estar ausentes o ser parciales.

**Determinar scope:**
- **Dominio completo**: evaluar todas sus tablas
- **Tabla especifica**: evaluar solo esa tabla
- **Multiples tablas**: evaluar el subconjunto indicado
- **Columna especifica**: evaluar una sola columna dentro de una tabla (requiere dominio + tabla + columna)

## 2. Recopilacion de Datos (en paralelo)

Una vez determinado el scope, lanzar en paralelo. Es **OBLIGATORIO** incluir `get_quality_rule_dimensions` para entender que dimensiones soporta el dominio y sus definiciones.

**Sobre dimensiones**: ver sección 2 de `skills-guides/exploration.md` para entender por qué `get_quality_rule_dimensions` es obligatorio y cómo usar sus resultados.

**Para dominio completo:**
```
Paralelo:
  A. list_domain_tables(domain_name)
  B. get_quality_rule_dimensions(collection_name=domain_name)  <-- OBLIGATORIO
  C. quality_rules_metadata(domain_name=domain_name)           <-- actualizar metadata AI, solo si no se ejecuto antes
```
Luego, con la lista de tablas obtenida en A, lanzar en paralelo para TODAS las tablas:
```
Por cada tabla (en paralelo):
  get_tables_quality_details(domain_name, [tabla])
  get_table_columns_details(domain_name, tabla)
  get_tables_details(domain_name, [tabla])
  generate_sql("obtener todos los campos de la tabla [tabla] sin filtros", domain_name)
```
Finalmente, usar los SQLs generados para lanzar `profile_data(query=[sql])` en paralelo.

**Para tabla especifica:**
```
Paralelo:
  A. get_tables_quality_details(domain_name, [tabla])
  B. get_table_columns_details(domain_name, tabla)
  C. get_quality_rule_dimensions(collection_name=domain_name)  <-- solo si no se obtuvo antes
  D. get_tables_details(domain_name, [tabla])                  <-- solo si no se obtuvo antes
  E. generate_sql("obtener todos los campos de la tabla [tabla] sin filtros", domain_name)
  F. quality_rules_metadata(domain_name=domain_name)           <-- solo si no se ejecuto antes
```
Tras obtener E, lanzar `profile_data(query=[sql])`.

**Para columna especifica:**
```
Paralelo:
  A. get_tables_quality_details(domain_name, [tabla])
  B. get_table_columns_details(domain_name, tabla)
  C. get_quality_rule_dimensions(collection_name=domain_name)  <-- solo si no se obtuvo antes
  D. generate_sql("obtener únicamente el campo [columna] de la tabla [tabla] sin filtros", domain_name)
  E. quality_rules_metadata(domain_name=domain_name)           <-- solo si no se ejecuto antes
```
Tras obtener D, lanzar `profile_data(query=[sql])`.
En el análisis posterior (sección 3), filtrar todo al scope de esa columna: inventario de reglas que afectan a esa columna, gaps solo para esa columna, EDA solo de esa columna.

**Nota sobre `quality_rules_metadata`**: Esta llamada actualiza la metadata AI de las reglas (descripcion, dimension). Se ejecuta sin `force_update` — solo procesa reglas sin metadata o modificadas. Si falla, continuar sin bloquear: el workflow no depende de ella.

**Nota**: El perfilado (EDA) es fundamental para detectar gaps reales (ej: nulos existentes sin regla de completeness). Si el dominio tiene >10 tablas, evaluar primero las que el usuario mencione explicitamente y preguntar si quiere continuar con el resto.

## 3. Analisis de Cobertura

Con los datos recopilados (incluyendo el EDA de `profile_data`), analizar semanticamente la cobertura:

### 3.1 Inventario de reglas existentes

Usando los resultados de `get_tables_quality_details` (ya obtenidos en la fase 2), construir para cada tabla el inventario de reglas actualmente definidas:

- **Nombre de la regla** y dimensión que cubre (`completeness`, `uniqueness`, `validity`, etc.)
- **Columna o columnas** a las que aplica (inferido del nombre y la descripción de la regla)
- **Estado actual**: OK / KO / Warning y porcentaje de paso

Este inventario es la línea base: **solo son gaps las dimensiones/columnas que NO están cubiertas por ninguna regla existente**. Nunca proponer una regla que duplique una ya existente, aunque su estado sea KO (en ese caso, reportarla como regla a revisar, no como gap).

Si `get_tables_quality_details` devuelve lista vacía para una tabla: la tabla no tiene ninguna regla definida → todos los checks semánticos que se identifiquen en 3.2 son gaps.

### 3.2 Evaluacion de gaps: Semantica primero, EDA como validador

El análisis tiene dos fuentes complementarias con roles distintos:

**1. Análisis semántico (fuente primaria — determina QUÉ reglas deben existir)**

La semántica del dominio es la base del razonamiento. Antes de mirar el EDA, estudiar en profundidad:
- **Descripción del dominio**: ¿qué representa este dominio de negocio? ¿qué garantías de calidad son inherentes a su naturaleza?
- **Contexto de negocio de cada tabla** (de `get_tables_details`): ¿qué proceso alimenta esta tabla? ¿qué uso se le da? ¿qué restricciones de negocio aplican?
- **Semántica de cada columna** (de `get_table_columns_details`): nombre, descripción, tipo de dato, si es obligatoria, si es clave, si es referencia a otro maestro
- **Reglas de negocio documentadas**: las restricciones ya descritas en la gobernanza del dominio son gaps inmediatos si no tienen regla asociada

Con esta lectura semántica, el modelo debe razonar **por qué** una columna necesita una dimensión concreta:

```
Columna ID / clave primaria     → completeness + uniqueness son obligatorios por definición
Columna importe / métrica       → validity (rango >= 0 o según negocio) es obligatorio
Columna fecha de negocio        → validity (rango lógico) y completeness si es campo clave
Columna estado / clasificación  → validity (enumerado con los valores permitidos del negocio)
Columna FK / referencia         → completeness si es obligatoria + consistency si hay maestro
Columna texto obligatorio       → completeness (por definición de negocio)
Columna texto libre / notas     → evaluación caso a caso; probablemente no necesita nada
```

**2. EDA con `profile_data` (fuente secundaria — confirma y cuantifica)**

Una vez determinadas semánticamente las reglas esperadas, el EDA sirve para:
- **Confirmar** que el problema existe realmente (un campo que debería ser no-nulo, ¿tiene nulos reales?)
- **Priorizar** gaps por impacto real: un 30% de nulos en un ID es más urgente que un 0,1%
- **Parametrizar** reglas de validity: los valores del EDA orientan rangos y enumerados (sin usarlos como límites exactos)
- **Detectar gaps que la semántica no anticipaba**: anomalías estadísticas que indican un problema de calidad no documentado

```
Uso del EDA por tipo de gap:
Completeness → ¿nulls > 0? Confirma el gap y da el % actual de fallo
Uniqueness   → ¿distinct_count < count? Confirma duplicados reales
Validity     → min/max/top_values orientan el rango o enumerado esperado
Consistency  → cruzar columnas relacionadas para detectar incoherencias
```

**El EDA nunca es el motivo para NO proponer una regla** que la semántica justifica. Si el EDA muestra 0 nulos en un ID, la regla de `completeness` sigue siendo necesaria: protege frente a futuros nulos. Si muestra el 100% de nulos en un campo supuestamente obligatorio, proponer la regla informando al usuario del estado actual.

**Dominios tecnicos — ajuste del analisis de gaps:**

Cuando el dominio es tecnico (`list_technical_domains`), las descripciones de negocio, contexto de tablas y terminologia pueden estar ausentes o muy limitadas. En este caso:
- **EDA pasa a ser la fuente principal** de razonamiento: los patrones estadisticos (nulos, duplicados, rangos, distribuciones) son la base para identificar gaps.
- **Razonar por nombres y tipos de columnas**: usar convenciones habituales (`*_id` → clave/FK, `*_date`/`*_dt` → fecha, `*_amount`/`*_amt` → importe, `*_code`/`*_status` → enumerado) para inferir la semantica probable.
- **Recomendaciones con menor confianza semantica**: al no disponer de descripciones de negocio, las reglas propuestas deben marcarse como basadas en inferencia tecnica. Validar las asunciones con el usuario antes de comprometerse con reglas de `validity` (rangos, enumerados) que requieren conocimiento de negocio.
- El flujo general (inventario → gaps → priorizar) se mantiene identico; solo cambia el peso relativo de las fuentes.

### 3.3 Calculo del gap score

Para cada tabla, estimar:
- **Reglas esperadas**: suma de reglas que semanticamente deberian existir
- **Reglas existentes**: cuantas de las esperadas existen realmente
- **Cobertura estimada**: reglas_existentes / reglas_esperadas × 100

Presentar como estimacion con razonamiento, no como cifra exacta. Usar rangos si hay incertidumbre ("entre el 40% y el 60% de cobertura").

## 4. Presentacion del Resultado

Estructurar el output en el chat con las siguientes secciones:

### Seccion 1: Resumen Ejecutivo
```
Dominio/Tabla: [nombre]
Fecha evaluacion: [hoy]
Tablas analizadas: N
Reglas existentes: N
Cobertura estimada: XX% (razonamiento resumido)
Gaps identificados: N criticos, N moderados
```

### Seccion 2: Tabla de Cobertura por Dimension

Para scope de **dominio o tabla**:
```markdown
| Tabla | Completeness | Uniqueness | Validity | Consistency | Cobertura |
|-------|-------------|------------|----------|-------------|-----------|
| account | Parcial (2/4) | OK | Gap | No aplica | ~50% |
| card | OK | OK | Parcial | Gap | ~70% |
```

Para scope de **columna especifica**:
```markdown
| Columna | Tipo | Completeness | Uniqueness | Validity | Consistency | Cobertura |
|---------|------|-------------|------------|----------|-------------|-----------|
| customer_id | INTEGER | OK | Gap | No aplica | No aplica | ~50% |
```

Usar iconos para mayor legibilidad:
- OK / cubierta: indicar que hay regla y pasa
- Parcial: hay alguna regla pero no cubre todo lo esperado
- Gap: no hay regla donde deberia haberla
- No aplica: esta dimension no tiene sentido para esta tabla/columna
- KO/Warning: hay regla pero esta fallando

### Seccion 3: Estado de Reglas Existentes

Para cada regla existente, mostrar en tabla:
```
| Regla | Tabla | Dimension | Estado | % Pass | Observaciones |
```

Si una regla esta en KO o WARNING, destacarla como accion prioritaria independientemente de los gaps.

### Seccion 4: Gaps Priorizados

Listar los gaps mas importantes, ordenados por prioridad:
1. Claves primarias / IDs sin completeness o uniqueness (CRITICO)
2. Campos obligatorios de negocio sin completeness (ALTO)
3. Importes/metricas sin validity (ALTO)
4. Fechas sin validity (MEDIO)
5. Estados/clasificaciones sin validity (MEDIO)
6. Campos secundarios sin cobertura (BAJO)

Para cada gap indicar: tabla, columna, dimension ausente, impacto potencial.

### Seccion 5: Recomendacion de Proximos Pasos

Resumir que acciones se recomiendan:
- Si hay reglas KO/WARNING: resolver primero antes de crear nuevas
- Si hay gaps criticos: proponer crear reglas con la skill `create-quality-rules`
- Si la cobertura es buena (>80%): felicitar y mencionar mejoras opcionales

## 5. Pregunta de Continuacion

Al finalizar, preguntar al usuario como quiere continuar (opciones seleccionables):
- **Crear reglas para cubrir los gaps**: activar skill `create-quality-rules`
- **Generar un informe**: activar skill `quality-report`
- **Profundizar en una tabla concreta**: volver a ejecutar esta skill con scope reducido
- **No hacer nada mas**: finalizar

No proponer continuacion automaticamente sin preguntar.
