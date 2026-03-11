# Guia Compartida: Descubrimiento y Exploracion de Dominios

## 1. Listar Dominios

Ejecutar `stratio_list_business_domains` para mostrar todos los dominios disponibles con sus nombres de negocio.

Si el usuario proporciona un dominio:
- Si coincide con un dominio conocido, ir directamente al paso 3
- Si no, preguntar al usuario cual dominio explorar mostrando la lista

Si no hay dominio claro, preguntar al usuario cual le interesa (presentar dominios como opciones seleccionables).

## 2. Regla CRITICA de domain_name

Ver `skills-guides/stratio-data-tools.md` sec 3 (regla de inmutabilidad de `domain_name`). Aplicar siempre.

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

Para las reglas de uso de `stratio_profile_data` (generar SQL con `stratio_generate_sql`, nunca SQL manual, usar parametro `limit` en vez de LIMIT en SQL), ver `skills-guides/stratio-data-tools.md` sec 3.

Umbrales adaptativos de profiling segun tamano estimado:

| Filas estimadas | Estrategia | Parametro limit |
|----------------|------------|-----------------|
| <100K | Completo | No configurar (default) |
| 100K - 1M | Muestreo | `limit=100000` |
| >1M | Muestreo + alerta | `limit=100000` + informar al usuario |

Documentar en reasoning si se uso muestreo.

## 8. Respuestas de aclaracion del MCP

Ver `skills-guides/stratio-data-tools.md` sec 4 para el protocolo completo de cascada ante respuestas de aclaracion del MCP (5 pasos + maximo 2 iteraciones por query).
