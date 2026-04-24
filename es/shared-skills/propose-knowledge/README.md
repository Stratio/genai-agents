# propose-knowledge

Analiza una conversación de análisis y **propone** conocimiento de negocio descubierto a la capa semántica de Stratio Governance de un dominio. Las propuestas son revisadas por un administrador en la consola de Governance antes de integrarse — la skill no escribe entradas definitivas por sí misma.

## Qué hace

- Resuelve el dominio objetivo desde `$ARGUMENTS`, el contexto de la conversación (llamadas MCP previas) o preguntando al usuario.
- Lee `output/MEMORY.md` (cuando existe) y aflora patrones de datos maduros (observados 3+ veces) como candidatos.
- Clasifica los hallazgos en tres tipos de propuesta:
  - **`business_concept`** — definiciones de términos, segmentaciones, métricas, umbrales;
  - **`sql_preference`** — patrones SQL específicos del dominio (JOINs, filtros) descubiertos durante el análisis;
  - **`chart_preference`** — preferencias de visualización **atadas a métricas del dominio**.
- Aplica filtros estrictos: rechaza preferencias de workflow/sesión/formato (formatos de salida, estilo visual, audiencia, profundidad de análisis) — esas pertenecen a la Fase 2 del flujo de análisis, no al conocimiento de dominio.
- Verifica no duplicación con `get_tables_details` y `search_domain_knowledge` antes de proponer.
- Limita a **5 propuestas por ejecución** (excepcionalmente 6), priorizadas P1 → P2 → P3 con límites por prioridad.
- Presenta las propuestas al usuario para aprobación (enviar todas / seleccionar / modificar / cancelar) antes de llamar a `propose_knowledge`.

## Cuándo usarla

- Tras una sesión de análisis en la que emergieron nuevas definiciones, métricas o patrones SQL/visuales.
- Cuando `output/MEMORY.md` ha acumulado patrones maduros que merece formalizar en Governance.
- Cuando el usuario dice "guarda esto como término de negocio", "registra que X significa Y" o "añade esto a gobierno".
- Para autoría explícita, one-shot, de un business term con relaciones conocidas, prefiere `manage-business-terms`.

## Dependencias

### Otras skills
- **Predecesores típicos:** `explore-data`, cualquier flujo de análisis o `assess-quality`.
- **Alternativa / complemento:** `manage-business-terms` (autoría explícita de un único término con activos relacionados).

### Guides
Ninguno. Las reglas y parámetros de MCPs están inline en `SKILL.md`.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `get_tables_details`, `search_domain_knowledge`.
- **Governance (`gov`):** `propose_knowledge`.

### Python
Ninguna — skill de solo prompt.

### Sistema
Ninguna.

## Activos empaquetados
Ninguno.

## Notas

- **Solo específico de dominio.** Las preferencias que aplican a cualquier dominio (formato de salida, estilo visual, audiencia, profundidad) nunca se proponen. El criterio de validación: la propuesta debe mencionar tablas, columnas o métricas específicas del dominio.
- **Calidad mínima para `business_concept`:** un concepto debe cumplir al menos 2 de (definición precisa con fórmula/umbral, usado activamente en el análisis, relevante para tablas/columnas existentes, definido explícitamente por el usuario) para ser propuesto.
- **Las propuestas son Draft** y se revisan en la UI de Governance por un administrador antes de integrarse.
