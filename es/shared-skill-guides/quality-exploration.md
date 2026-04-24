# Guía de Exploración y Contexto de Calidad del Dato

Pasos para explorar y validar dominios antes de ejecutar cualquier evaluación de calidad.

## 1. Descubrimiento de Dominio

Para el workflow estándar de descubrimiento (listar dominios, regla crítica de domain_name, explorar tablas, detalle de tablas y columnas), seguir las secciones 4.1 a 4.4 de `skills-guides/stratio-data-tools.md`.

**Dominios técnicos**: Este agente también soporta dominios técnicos además de los semánticos. Si el usuario solicita trabajar con un dominio técnico, usar `search_domains(search_text, domain_type="technical")` o `list_domains(domain_type="technical")`. En dominios técnicos, los pasos 4.3 (detalle de tablas vía `get_tables_details`) y 4.5 (terminología vía `search_domain_knowledge`) pueden devolver información limitada o vacía — esto es esperable y no debe bloquear el workflow. Compensar con mayor peso del EDA (sección 3) y validación directa con el usuario.

**Lanzar en paralelo** cuando sean tablas independientes.

## 2. Contexto de Calidad (OBLIGATORIO)

Debe obtenerse siempre las definiciones de dimensiones antes de evaluar:

`get_quality_rule_dimensions(domain_name=domain_name)` para conocer exactamente qué significa cada dimensión en este dominio específico y cuántas dimensiones soporta.

Además, ejecutar `quality_rules_metadata(domain_name=domain_name)` antes de evaluar para tener metadata AI fresca en las reglas (descripción, dimensión). Sin `force_update` — solo procesa reglas sin metadata o modificadas. No bloqueante: si falla, continuar con el workflow normalmente.

Este paso es **OBLIGATORIO** y fundamental por las siguientes razones:
- **Dimensiones Propias del Dominio**: Cada dominio puede tener definidas sus propias dimensiones en su documento de calidad, más allá de las estándar.
- **Definiciones y Ambigüedad**: Como algunas dimensiones son ambiguas por naturaleza, la definición del dominio puede diferir de la estándar (ej: lo que un dominio considera `consistency` puede ser distinto a la definición general). La definición del dominio SIEMPRE prevalece.
- **Variabilidad**: No asumir que `completeness` siempre significa lo mismo ni que todos los dominios soportan el mismo set de dimensiones.

## 3. Perfilado Estadístico (EDA)

Para las reglas base de uso de `profile_data` (generar SQL con `generate_sql`, nunca SQL manual, usar parámetro `limit` en vez de LIMIT en SQL), ver `skills-guides/stratio-data-tools.md` sec 3 y 5.

`profile_data` es la herramienta principal para entender la realidad de los datos y fundamentar las reglas de calidad. **Requiere una query SQL como parámetro.**

**Procedimiento obligatorio:**
1. Generar la SQL primero con `generate_sql(data_question="todos los campos de la tabla X", domain_name="Y")`.
2. Pasar el resultado al parámetro `query` de `profile_data`.
3. Usar profiling adaptativo según el tamaño estimado del dataset (parámetro `limit`).

| Tipo de columna    | Qué mirar en el perfilado                                                           |
|--------------------|-------------------------------------------------------------------------------------|
| **Cualquier tipo** | `missing_count`: si hay nulos, justifica regla de `completeness`.                   |
| **Claves/IDs**     | `distinct_count`: si es menor que el total, hay duplicados (invalida `uniqueness`). |
| **Numéricas**      | `min`, `max`, `mean`: detecta outliers o valores inválidos para `validity`.         |
| **Categóricas**    | `top_values`: base para reglas de `validity` (enumerados).                          |
| **Fechas**         | `min`, `max`: detecta fechas en el futuro o valores "dummy" (1900/9999).            |
| **...**            | ...                                                                                 |

**Lanzar en paralelo** para todas las tablas de interés durante la fase de evaluación inicial.
