---
name: create-sql-mappings
description: Crear o actualizar SQL mappings para vistas de negocio existentes en Stratio
  Governance. Para corregir, mejorar o crear mappings sin recrear vistas.
argument-hint: [dominio tecnico (opcional)]
---

# Skill: Crear SQL Mappings

Crea o actualiza SQL mappings para vistas de negocio existentes en Stratio Governance. Fase 4 del pipeline de capa semantica. Util para corregir o mejorar mappings sin necesidad de recrear las vistas.

## Tools MCP utilizadas

| Tool | Servidor | Proposito |
|------|----------|-----------|
| `list_technical_domains` | sql | Descubrir dominios tecnicos disponibles |
| `list_technical_domain_concepts(domain)` | gov | Listar vistas con estado de mapping |
| `create_sql_mappings(domain, view_names?, user_instructions?)` | gov | Crear o actualizar mappings SQL de vistas existentes |

**Reglas clave**: `domain_name` inmutable. Ofrecer `user_instructions` antes de invocar. `create_sql_mappings` sobrescribe mappings existentes (no es destructivo a nivel de vista, solo reemplaza el mapping SQL).

## Workflow

### 1. Determinar dominio

Si `$ARGUMENTS` contiene nombre de dominio, validar contra `list_technical_domains`. Si no, listar y preguntar al usuario siguiendo la convencion de preguntas al usuario.

### 2. Evaluar estado

Ejecutar `list_technical_domain_concepts(domain)` para obtener el listado de vistas con su estado de mapping.

Presentar resumen:
```
## Mappings SQL — [domain_name]
| Vista | Mapping |
|-------|---------|
| Vista1 | ✓ |
| Vista2 | ✗ |
| Vista3 | ✓ |
```

### 3. Seleccion de vistas

Preguntar al usuario con opciones:
1. **Todas las vistas sin mapping** — seguro, solo crea donde falta
2. **Vistas especificas** — seleccion multiple (puede incluir vistas con mapping existente para actualizarlo)
3. **Actualizar mappings existentes** — sobrescribe el mapping SQL, no borra la vista ni sus terminos semanticos

### 4. user_instructions

Ofrecer al usuario la oportunidad de aportar contexto adicional:
- **Ficheros locales**: Si el usuario tiene documentacion tecnica, diagramas ER, especificaciones de integracion o scripts SQL de referencia → **leerlos** y extraer informacion relevante para incluirla como contexto
- **Reglas de mapping**: Relaciones entre tablas, tipo de JOINs preferidos, filtros de exclusion, transformaciones de datos
- Ejemplos: "Usa LEFT JOIN para preservar registros sin correspondencia", "Tabla principal para los JOINs: accounts", "Excluir registros con estado='DELETED'", "Usar COALESCE para campos nullable", "Fechas en formato epoch milliseconds"

No sugerir opciones que la tool controla internamente (idioma, formato de salida). Si el usuario no aporta instrucciones, continuar sin el parametro. No es bloqueante.

### 5. Ejecucion

Invocar `create_sql_mappings(domain, view_names?, user_instructions?)`. La tool devuelve un resumen de lo procesado — presentar al usuario directamente.

Si hay errores, reintentar la vista fallida con `user_instructions` mejoradas (max 2 reintentos). Si persiste, documentar y continuar.

### 6. Resumen

Basado en la respuesta de la tool:
- Mappings creados/actualizados
- Errores si los hubo
- Siguiente paso sugerido: "Puedes generar los terminos semanticos con `/create-semantic-terms`"
