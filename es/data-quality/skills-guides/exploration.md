# Guia de Exploracion y Contexto de Calidad

Pasos para explorar y validar dominios antes de ejecutar cualquier evaluacion de calidad.

## 1. Descubrimiento de Dominio

Para el workflow estandar de descubrimiento (listar dominios, regla critica de domain_name, explorar tablas, detalle de tablas y columnas), seguir las secciones 4.1 a 4.4 de `skills-guides/stratio-data-tools.md`.

**Dominios tecnicos**: Este agente tambien soporta dominios tecnicos ademas de los semanticos. Si el usuario solicita trabajar con un dominio tecnico, usar `search_domains(search_text, domain_type="technical")` o `list_domains(domain_type="technical")`. En dominios tecnicos, los pasos 4.3 (detalle de tablas via `get_tables_details`) y 4.5 (terminologia via `search_domain_knowledge`) pueden devolver informacion limitada o vacia — esto es esperable y no debe bloquear el workflow. Compensar con mayor peso del EDA (seccion 3) y validacion directa con el usuario.

**Lanzar en paralelo** cuando sean tablas independientes.

## 2. Contexto de Calidad (OBLIGATORIO)

Debe obtenerse siempre las definiciones de dimensiones antes de evaluar:

`get_quality_rule_dimensions(collection_name=domain_name)` para conocer exactamente que significa cada dimension en este dominio especifico y cuantas dimensiones soporta.

Ademas, ejecutar `quality_rules_metadata(domain_name=domain_name)` antes de evaluar para tener metadata AI fresca en las reglas (descripcion, dimension). Sin `force_update` — solo procesa reglas sin metadata o modificadas. No bloqueante: si falla, continuar con el workflow normalmente.

Este paso es **OBLIGATORIO** y fundamental por las siguientes razones:
- **Dimensiones Propias del Dominio**: Cada dominio puede tener definidas sus propias dimensiones en su documento de calidad, mas alla de las estandar.
- **Definiciones y Ambiguedad**: Como algunas dimensiones son ambiguas por naturaleza, la definicion del dominio puede diferir de la estandar (ej: lo que un dominio considera `consistency` puede ser distinto a la definicion general). La definicion del dominio SIEMPRE prevalece.
- **Variabilidad**: No asumir que `completeness` siempre significa lo mismo ni que todos los dominios soportan el mismo set de dimensiones.

## 3. Perfilado Estadistico (EDA)

Para las reglas base de uso de `profile_data` (generar SQL con `generate_sql`, nunca SQL manual, usar parametro `limit` en vez de LIMIT en SQL), ver `skills-guides/stratio-data-tools.md` sec 3 y 5.

`profile_data` es la herramienta principal para entender la realidad de los datos y fundamentar las reglas de calidad. **Requiere una query SQL como parametro.**

**Procedimiento obligatorio:**
1. Generar la SQL primero con `generate_sql(data_question="todos los campos de la tabla X", domain_name="Y")`.
2. Pasar el resultado al parametro `query` de `profile_data`.
3. Usar profiling adaptativo segun el tamaño estimado del dataset (parametro `limit`).

| Tipo de columna    | Que mirar en el perfilado                                                           |
|--------------------|-------------------------------------------------------------------------------------|
| **Cualquier tipo** | `missing_count`: si hay nulos, justifica regla de `completeness`.                   |
| **Claves/IDs**     | `distinct_count`: si es menor que el total, hay duplicados (invalida `uniqueness`). |
| **Numericas**      | `min`, `max`, `mean`: detecta outliers o valores invalidos para `validity`.         |
| **Categoricas**    | `top_values`: base para reglas de `validity` (enumerados).                          |
| **Fechas**         | `min`, `max`: detecta fechas en el futuro o valores "dummy" (1900/9999).            |
| **...**            | ...                                                                                 |

**Lanzar en paralelo** para todas las tablas de interes durante la fase de evaluacion inicial.
