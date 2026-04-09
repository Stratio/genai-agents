# Catálogo de Patrones de Diseño de AGENTS.md

Catálogo de patrones probados para escribir instrucciones de agentes efectivas. Cada patrón incluye: qué es, cuándo usarlo, el formato exacto y un ejemplo genérico.

---

## 1. Patrón de Triaje

**Qué es**: Una tabla de routing que clasifica la intención del usuario antes de activar cualquier flujo de trabajo o skill. Siempre es la primera fase (Fase 0) y determina la ruta de ejecución.

**Cuándo usarlo**: Todo agente debe tener una fase de triaje. Sin ella, el agente aplica el flujo completo a cada petición — incluyendo las triviales.

**Por qué importa**: No todas las peticiones requieren el flujo completo. Una pregunta factual simple no debería activar un proceso de múltiples fases. El triaje previene esto separando las peticiones de acción directa de las que requieren cargar una skill o activar un flujo completo.

**Formato** — Dos columnas (agentes simples):

```markdown
| Intención del usuario | Acción |
|----------------------|--------|
| "..." | Resolver directamente: [describir acción] |
| "..." | Cargar `/nombre-skill`, luego seguir su flujo |
| "..." | Flujo completo (Fases 1-N) |
```

**Formato** — Tres columnas (agentes con skills distintas y acciones directas):

```markdown
| Intención del usuario | Acción directa | Skill a cargar |
|----------------------|----------------|----------------|
| "..." | — | `nombre-skill` |
| "..." | [describir llamada a herramienta o respuesta en chat] | — |
```

**Criterio de triaje**: Establecer la regla de decisión explícitamente:

```markdown
**Criterio de triaje**: ¿Se puede responder la petición con una acción directa (1-2 llamadas
a herramientas) sin un flujo de múltiples pasos? → Resolver directamente. En caso contrario → Cargar
la skill correspondiente.
```

**Ejemplo**:

```markdown
| Intención del usuario | Acción directa | Skill a cargar |
|----------------------|----------------|----------------|
| "¿Cuál es el estado de X?" | Consultar vía MCP, responder en chat | — |
| "Construye un X completo para el dominio Y" | — | `/build-x` |
| "Revisa este X" | — | Saltar a Fase N (Revisión) |
```

---

## 2. Patrón de Fases Secuenciales

**Qué es**: Fases numeradas que definen el flujo de trabajo del agente como una progresión lineal con condiciones claras de entrada/salida.

**Cuándo usarlo**: Cuando el trabajo del agente implica etapas distintas que deben ocurrir en orden (ej: descubrimiento → planificación → ejecución → validación).

**Por qué importa**: Las fases claras evitan que el agente salte pasos o mezcle responsabilidades. Cada fase tiene un propósito definido y criterios de completitud.

**Formato**:

```markdown
### Fase N — {Nombre}

**Entrada**: {qué activa esta fase — ej: "El usuario confirmó el plan de diseño"}

1. {Paso 1}
2. {Paso 2}
3. ...

**Salida**: {qué debe ser cierto antes de pasar a la siguiente fase — ej: "Todos los ficheros generados y reportados al usuario"}
```

**Ejemplo**:

```markdown
### Fase 1 — Descubrimiento

**Entrada**: El triaje clasificó la petición como flujo completo.

1. Identificar el alcance (dominio, tabla o columna)
2. Ejecutar consultas de descubrimiento para entender el estado actual
3. Presentar un resumen de hallazgos al usuario

**Salida**: El usuario ha confirmado el alcance y entiende el estado actual.
```

---

## 3. Patrón de Activación de Skills

**Qué es**: Una regla de carga condicional que indica al agente cargar una skill específica antes de continuar con su flujo de trabajo.

**Cuándo usarlo**: Siempre que el agente delegue detalle operativo a una skill. La skill se carga bajo demanda, no al inicio del agente.

**Por qué importa**: Las skills contienen instrucciones operativas detalladas que inflarían el AGENTS.md si se pusieran inline. La carga condicional mantiene las instrucciones del agente ligeras asegurando que el detalle correcto esté disponible cuando se necesite.

**Formato**:

```markdown
**Activación de skills**: Cargar la skill correspondiente ANTES de continuar con el flujo de trabajo.
La skill contiene el detalle operativo necesario.
```

Para entradas específicas del triaje:

```markdown
| "Construir X para el dominio Y" | — | `/build-x` |
```

En el texto del flujo de trabajo:

```markdown
Cargar `/nombre-skill` como referencia autoritativa para [tema].
```

**Anti-patrón**: Nunca referenciar una skill sin instruir explícitamente a cargarla. Decir "ver /nombre-skill para detalles" no es suficiente — hay que indicar al agente que la cargue.

---

## 4. Patrón Human-in-the-Loop

**Qué es**: Un protocolo de doble confirmación para acciones que tienen efectos secundarios, son destructivas o irreversibles.

**Cuándo usarlo**: Antes de cualquier acción que modifique sistemas externos, cree artefactos, borre datos o no se pueda deshacer fácilmente.

**Por qué importa**: Los LLMs pueden malinterpretar la intención. Requerir confirmación explícita antes de ejecutar asegura que el usuario es consciente de lo que pasará y está de acuerdo. Esto previene errores costosos.

**Formato**:

```markdown
1. Diseñar la acción (planificar qué se hará)
2. Presentar el plan completo al usuario, incluyendo:
   - Qué se creará/modificará/eliminará
   - Resultado esperado
   - Riesgos o efectos secundarios
3. **Esperar confirmación explícita**: palabras como "sí", "adelante", "ok", "procede",
   "aprobado", o equivalentes en el idioma del usuario
4. Ejecutar solo después de la confirmación

- Si el usuario rechaza: ajustar el plan y presentar de nuevo
- Si el usuario aprueba parcialmente: ejecutar solo las partes aprobadas
- Si el usuario pide cambios: incorporar feedback y re-presentar
```

**Formato de regla crítica** (para acciones que NUNCA deben saltarse la confirmación):

```markdown
**CRÍTICO**: `{nombre_herramienta}` NUNCA se invoca sin confirmación explícita del usuario.
```

---

## 5. Patrón de Matriz de Profundidad

**Qué es**: Una tabla de activación de capacidades que ajusta el comportamiento según el nivel de profundidad elegido por el usuario.

**Cuándo usarlo**: Cuando el mismo flujo de trabajo puede ejecutarse a diferentes niveles de exhaustividad (ej: revisión rápida vs. análisis profundo).

**Por qué importa**: No todas las peticiones necesitan el mismo nivel de detalle. Una matriz de profundidad da al usuario control sobre el trade-off entre velocidad y exhaustividad, y hace el comportamiento del agente predecible en cada nivel.

**Formato**:

```markdown
| Capacidad | Rápido | Estándar | Profundo |
|-----------|--------|----------|----------|
| Descubrimiento | Básico | Completo | Completo + perfilado extendido |
| Hipótesis | Opcional | Obligatorio | Todas + testing sistemático |
| Validación | Omitir | Cuando sea relevante | Obligatorio para todo |
| Iteraciones | 0 | Máx 1 | Máx 2 |
```

**Uso**: Preguntar al usuario el nivel de profundidad al inicio del flujo:

```markdown
Preguntar al usuario con opciones: "¿Qué nivel de profundidad?"
1. **Rápido** — Vista general rápida, mínimo detalle
2. **Estándar** — Análisis equilibrado (recomendado)
3. **Profundo** — Investigación exhaustiva con validación completa
```

---

## 6. Patrón de Delegación a Guides

**Qué es**: Una referencia a un fichero de guía externo que contiene reglas operativas detalladas, delegando los detalles a un documento separado.

**Cuándo usarlo**: Cuando un tema (ej: uso de herramientas MCP, reglas de perfilado de datos) tiene reglas operativas detalladas que excederían 30-50 líneas si se pusieran inline en el AGENTS.md.

**Por qué importa**: Mantiene el AGENTS.md enfocado en el flujo de trabajo y la toma de decisiones. Los detalles operativos como parámetros de herramientas, manejo de errores y casos límite pertenecen a guides que la skill carga.

**Formato**:

```markdown
Todas las reglas para [tema] (herramientas disponibles, reglas estrictas, [listar temas clave])
están en `skills-guides/[nombre-guia].md`. Seguir TODAS las reglas definidas ahí.
```

**Importante**: El formato de ruta `skills-guides/nombre.md` se usa en el AGENTS.md fuente. Los scripts de empaquetado pueden reescribir esta ruta a una local al incrustar guides dentro de skills.

---

## 7. Patrón de Convención de Preguntas

**Qué es**: Una forma estandarizada de preguntar al usuario con opciones estructuradas, usando una herramienta interactiva cuando esté disponible.

**Cuándo usarlo**: Todo agente debe incluir esta convención en su sección de Interacción con el Usuario. Es referenciada por todas las fases y skills que necesitan input del usuario.

**Por qué importa**: Un formato consistente de preguntas mejora la experiencia del usuario. La herramienta interactiva (cuando está disponible) proporciona mejor UX que opciones en texto plano. El fallback asegura que el agente funcione en todas las plataformas.

**Formato** (texto exacto — copiar textualmente en la sección de Interacción con el Usuario del agente):

```markdown
**Convención de preguntas**: Cuando estas instrucciones digan "preguntar al usuario con opciones",
presentar las opciones de forma clara y estructurada. Si el entorno dispone de una herramienta
interactiva de preguntas{{TOOL_QUESTIONS}}, invocarla obligatoriamente — nunca escribir las
preguntas en el chat cuando haya una herramienta de preguntas disponible. En caso contrario,
presentar las opciones como lista numerada en el chat, con formato legible, e indicar al usuario
que responda con el número o nombre de su elección. Para selección múltiple, indicar que puede
elegir varias separadas por coma.
```

> `{{TOOL_QUESTIONS}}` es un placeholder que se sustituye automáticamente según la plataforma en tiempo de empaquetado/despliegue. En el AGENTS.md fuente debe dejarse tal cual.

---

## 8. Patrón de Reglas Críticas

**Qué es**: Declaraciones NUNCA/SIEMPRE para restricciones firmes que nunca deben violarse.

**Cuándo usarlo**: Para reglas que, si se rompen, causarían pérdida de datos, problemas de seguridad, resultados incorrectos o mala experiencia del usuario.

**Por qué importa**: Los LLMs siguen mejor las instrucciones cuando las restricciones se establecen como reglas absolutas con la razón detrás. La razón permite al modelo aplicar la regla correctamente en casos límite.

**Formato**:

```markdown
**CRÍTICO**: NUNCA [acción] sin [condición] porque [consecuencia si se viola].
```

```markdown
**SIEMPRE** [acción] antes de [otra acción] porque [razón].
```

**Ejemplo**:

```markdown
**CRÍTICO**: NUNCA ejecutar una consulta sin validar el SQL primero,
porque una consulta mal formada puede devolver resultados parciales silenciosamente
llevando a un análisis incorrecto.

**SIEMPRE** presentar el estado actual antes de proponer acciones,
porque el usuario necesita contexto para tomar decisiones informadas.
```

---

## 9. Patrón de Idioma

**Qué es**: Una instrucción explícita para responder siempre en el idioma del usuario.

**Cuándo usarlo**: Todo agente debe incluir esto. Es innegociable.

**Formato** (texto exacto — colocar en la subsección de Estilo de comunicación de Descripción y Rol):

```markdown
**Idioma**: Responder SIEMPRE en el mismo idioma que el usuario usa para formular su pregunta
```

Versión expandida (para la sección de Interacción con el Usuario):

```markdown
- **Idioma**: Responder en el mismo idioma que usa el usuario, incluyendo resúmenes,
  tablas de estado y todo el contenido generado
```

---

## 10. Patrón de Reporte de Progreso

**Qué es**: Reglas para mantener al usuario informado durante operaciones de múltiples pasos.

**Cuándo usarlo**: Cuando el flujo de trabajo del agente implica operaciones que requieren múltiples pasos (ej: crear múltiples ficheros, ejecutar varias consultas, procesar un pipeline).

**Por qué importa**: Sin reporte de progreso, las operaciones largas parecen como si el agente estuviera bloqueado. Reportar también ayuda al usuario a detectar problemas temprano.

**Formato**:

```markdown
- Reportar progreso durante operaciones de múltiples fases
- Al completar: resumen de acciones realizadas + sugerencias para próximos pasos
```

**Ejemplo en una fase de generación**:

```markdown
Para cada fichero generado:
1. Escribir el fichero
2. Reportar: ruta del fichero, tamaño, highlights clave
3. Continuar con el siguiente fichero
```

---

## Combinaciones de Patrones

Los agentes más efectivos combinan varios patrones. Un agente típico usa:

1. **Triaje** (siempre) → enruta a la acción apropiada
2. **Fases secuenciales** → estructura el flujo principal
3. **Activación de skills** → carga detalle operativo bajo demanda
4. **Human-in-the-loop** → protege acciones destructivas
5. **Convención de preguntas** → estandariza interacción con el usuario
6. **Idioma** → asegura soporte multilingüe
7. **Reporte de progreso** → mantiene al usuario informado

Adiciones opcionales:
- **Matriz de profundidad** → cuando el mismo flujo puede ejecutarse a diferentes niveles
- **Delegación a guides** → cuando las reglas operativas exceden 30-50 líneas
- **Reglas críticas** → cuando existen restricciones firmes
