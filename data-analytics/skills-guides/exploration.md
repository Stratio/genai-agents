# Guia Compartida: Descubrimiento y Exploracion de Dominios

Pasos comunes para explorar dominios gobernados. Usada por `/explore-data` y `/analyze`.

## 1. Listar Dominios

Ejecutar `stratio_list_business_domains` para mostrar todos los dominios disponibles con sus nombres de negocio.

Si el usuario proporciona un dominio:
- Si coincide con un dominio conocido, ir directamente al paso 3
- Si no, preguntar al usuario cual dominio explorar mostrando la lista

Si no hay dominio claro, preguntar al usuario cual le interesa (presentar dominios como opciones seleccionables).

## 2. Regla CRITICA de domain_name

El `domain_name` usado en TODAS las llamadas MCP posteriores debe ser **exactamente** el valor devuelto por `stratio_list_business_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo. Si hay duda, volver a llamar a `stratio_list_business_domains`.

## 3. Explorar Tablas

1. `stratio_list_domain_tables(domain_name)` para listar todas las tablas del dominio
2. Presentar las tablas con sus descripciones en formato tabla markdown

## 4. Detalle de Tablas

Para las tablas de interes:
1. `stratio_get_tables_details(domain_name, table_names)` para obtener:
   - Descripcion completa
   - Contexto de negocio
   - Terminos de negocio asociados
   - Reglas de negocio
   - Comportamientos SQL
2. Presentar la informacion de forma estructurada

## 5. Columnas

Para cada tabla de interes:
1. `stratio_get_table_columns_details(domain_name, table_name)` para obtener nombre, tipo y descripcion de negocio
2. Presentar en tabla markdown ordenada logicamente

**Lanzar en paralelo** los pasos 4 y 5 cuando sean sobre tablas independientes. Tambien lanzar paso 6 en paralelo si ya se conocen los terminos a buscar.

## 6. Terminologia de Negocio

`stratio_search_domain_knowledge(question, domain_name)` para buscar:
- Definiciones de terminos de negocio
- Reglas de calculo
- Politicas de datos
- Glosario del dominio

## 7. Perfilado Estadistico

`stratio_profile_data` requiere una query SQL como parametro. **NUNCA escribir esa SQL manualmente.**
Generar siempre la SQL primero con `stratio_generate_sql(data_question="...", domain_name="...")`
y pasar el resultado a `stratio_profile_data(query=<sql_generada>)`.

Usar `stratio_profile_data` con profiling adaptativo segun tamano estimado:

| Filas estimadas | Estrategia | Parametro limit |
|----------------|------------|-----------------|
| <100K | Completo | No configurar (default) |
| 100K - 1M | Muestreo | `limit=100000` |
| >1M | Muestreo + alerta | `limit=100000` + informar al usuario |

NUNCA modificar las queries SQL anadiendo LIMIT. Usar el parametro `limit` de la tool. Documentar en reasoning si se uso muestreo.

## 8. Respuestas de aclaracion del MCP

`stratio_query_data` y `stratio_generate_sql` pueden devolver una solicitud de aclaracion en lugar de datos. Reconocer este patron: el mensaje describe que informacion adicional necesita el motor para formular la query (ej: ambiguedad temporal, definicion de un termino de negocio, alcance de un segmento).

**Esto no es un error ni un dataset vacio** — es el MCP esperando contexto adicional para continuar.

Protocolo en cascada (aplicar en orden, parar en el primer paso que resuelva la ambiguedad):

1. **Resolver con conocimiento del dominio**: Llamar a `stratio_search_domain_knowledge` con el termino o concepto ambiguo. Si se encuentra la definicion, rellamar a la tool original anadiendo la definicion en `additional_context`.

2. **Inferir del contexto del analisis**: Si el plan ya establece el periodo, el segmento o la definicion relevante (hipotesis, KPIs definidos), incluirlo directamente en `additional_context` y rellamar sin preguntar al usuario.

3. **Preguntar al usuario**: Solo si los pasos 1-2 no resuelven la ambiguedad. Presentar la pregunta concreta que el MCP necesita, con las opciones disponibles si las hay (nunca preguntas abiertas si se pueden ofrecer opciones).

4. **Reformular la pregunta**: Si con el contexto disponible aun no se puede aclarar, reformular la pregunta de datos con mayor especificidad: fechas explicitas, definiciones incrustadas en el texto de la pregunta, acotacion del alcance.

5. **Informar y continuar**: Si tras los pasos anteriores el MCP sigue sin poder responder, documentar la limitacion y continuar el analisis con los datos disponibles. No bloquear el analisis por una sola metrica no resuelta.

**Limite**: Maximo 2 iteraciones de aclaracion por query. Si tras ambas iteraciones no hay datos, informar al usuario y omitir esa metrica.
