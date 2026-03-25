---
name: generate-technical-terms
description: Generar o regenerar terminos tecnicos (descripciones de tablas y columnas) en
  Stratio Governance para un dominio tecnico.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Generar Terminos Tecnicos

Genera descripciones tecnicas de tablas y columnas de un dominio en Stratio Governance. Fase 1 del pipeline de capa semantica.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `list_technical_domains` | sql | Descubrir dominios tecnicos disponibles (incluye descripcion si existe) |
| `list_domain_tables(domain)` | sql | Listar tablas con sus descripciones (indica si ya tienen terminos tecnicos) |
| `create_technical_terms(domain, table_names?, user_instructions?, regenerate?)` | gov | Crear terminos tecnicos. Salta existentes. Con `regenerate=true`: DESTRUCTIVO, borra y recrea |

**Reglas clave**: `domain_name` inmutable (valor exacto de `list_technical_domains`). Confirmacion obligatoria para `regenerate=true`. Ofrecer `user_instructions` antes de invocar.

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene un nombre de dominio, validar contra `list_technical_domains`. Si coincide, continuar. Si no coincide, reintentar con `list_technical_domains(refresh=true)` por si es una coleccion recien creada. Si ahora coincide, continuar. Si sigue sin coincidir o no hay argumento, listar dominios disponibles y preguntar al usuario siguiendo la convencion de preguntas al usuario.

### 2. Evaluar estado

Ejecutar `list_domain_tables(domain)` para evaluar el estado actual:
- Tablas con descripcion → ya tienen terminos tecnicos generados
- Tablas sin descripcion → pendientes de generar
- Si el dominio tiene descripcion (visible en `list_technical_domains`) → la descripcion general ya existe

Presentar resumen al usuario:
```
## Estado — [domain_name]
- Tablas totales: N
- Con terminos tecnicos: X
- Pendientes: Y
- Descripcion del dominio: Si/No
```

### 3. Seleccion de alcance

Preguntar al usuario con opciones:
1. **Crear para todas las tablas** — idempotente: `create_technical_terms` salta tablas que ya tienen descripcion
2. **Crear para tablas especificas** — seleccion multiple de las tablas pendientes
3. **Regenerar todas** — DESTRUCTIVO: borra y recrea. Requiere confirmacion explicita
4. **Regenerar tablas especificas** — DESTRUCTIVO para las seleccionadas. Requiere confirmacion explicita

### 4. user_instructions

Antes de ejecutar, ofrecer al usuario la oportunidad de aportar contexto adicional:
- **Ficheros locales**: Si el usuario tiene documentacion, glosarios, diccionarios de datos o especificaciones → **leerlos** y extraer definiciones relevantes para incluirlas como contexto
- **Definiciones de dominio**: Conceptos de negocio, valores especificos de columnas, relaciones entre entidades que la IA deberia conocer
- Ejemplos: "La columna `status` tiene valores: A=activo, I=inactivo, S=suspendido", "Las tablas `film_*` pertenecen al modulo de catalogo de peliculas", "El campo `last_update` es un timestamp de auditoria, no de negocio"

No sugerir opciones que la tool controla internamente (idioma, audiencia, formato). Si el usuario no aporta instrucciones, continuar sin el parametro. No es bloqueante.

### 5. Ejecucion

Invocar `create_technical_terms`. Para regenerar: pasar `regenerate=true` (DESTRUCTIVO). La tool devuelve un resumen de lo procesado — presentar ese resumen al usuario directamente. No llamar a tools adicionales post-creacion para no llenar contexto.

**Nota sobre descripcion de dominio**: `create_technical_terms` genera automaticamente la descripcion del dominio/coleccion si no tiene. No es necesario llamar a `create_collection_description` como paso separado.

### 6. Resumen

Basado en la respuesta de la tool, presentar:
- Tablas procesadas
- Errores si los hubo (reintentar entidades fallidas con `user_instructions` mejoradas, max 2 reintentos)
- Siguiente paso sugerido: "Puedes crear una ontologia con `/create-ontology`"
