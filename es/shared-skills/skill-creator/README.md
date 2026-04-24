# skill-creator

Referencia completa para diseñar y escribir skills de agente de alta calidad (ficheros SKILL.md). Cubre anatomía, frontmatter YAML, progressive disclosure, patrones de escritura, ficheros de soporte y un checklist de calidad de 15 puntos. Autocontenida — sin dependencia de docs externas ni web.

## Qué hace

- Enseña la anatomía de una skill: layout de directorios (`SKILL.md` + `scripts/`, `references/`, `assets/` opcionales), convenciones de naming (kebab-case) y los dos tipos de skills (contenido de referencia vs. contenido de tarea).
- Especifica el **contrato de frontmatter YAML**: campos obligatorios `name` y `description`, opcional `argument-hint`, reglas de formato (siempre entre comillas dobles en una línea) y patrones de optimización de descripción ("verbo acción + qué + Use when... + keywords").
- Explica la **progressive disclosure**: metadata siempre en memoria, body cargado en activación, ficheros de soporte on demand. Impulsa la regla "mantén SKILL.md por debajo de 500 líneas".
- Proporciona guía de escritura: explica *por qué*, no solo *qué*, voz imperativa, secciones numeradas para flujos secuenciales, tablas de routing de decisiones, ejemplos input/output, presupuesto de instrucciones (objetivo 150–200 discretas).
- Documenta la estrategia de ficheros de soporte: cuándo extraer a `scripts/` / `references/` / `assets/`, cómo referenciarlos, cómo usar inyección dinámica de contexto (`` !`command` ``).
- Cataloga patrones (human-in-the-loop, output estructurado, comportamiento condicional, operaciones paralelas, descripción proactiva) y antipatrones.
- Ejecuta un **checklist de calidad de 15 puntos** antes de dar por terminada una skill (frontmatter bien formado, body < 500 líneas, sin referencias a ficheros específicos de plataforma, pasos con WHY explicado, acciones destructivas con pausa, kebab-case, descripción proactiva…).

## Cuándo usarla

- El usuario quiere crear una skill nueva, refactorizar una existente o revisar una skill escrita en otro sitio.
- Antes de añadir una skill a `shared-skills/` o a la carpeta `skills/` de un agente — el checklist detecta la mayoría de bugs de portabilidad (referencias directas a `AGENTS.md`, rutas específicas de plataforma, descripciones vagas).
- Al mejorar una skill que no se activa (suele ser problema de descripción) o que carga demasiado contexto (suele ser problema de longitud del body).

## Dependencias

### Otras skills
Ninguna. Es una skill de referencia standalone.

### Guides
Ninguno (compartido). La skill empaqueta dos ficheros de soporte dentro de su propia carpeta:
- `writing-patterns.md` — catálogo de patrones reutilizables con ejemplos de código concretos.
- `frontmatter-reference.md` — referencia completa de campos YAML del frontmatter con ejemplos y detalles de control de invocación.

### MCPs
Ninguno.

### Python
Ninguno — skill de solo prompt.

### Sistema
Ninguno.

## Activos empaquetados

- `writing-patterns.md` (catálogo de patrones con ejemplos de código)
- `frontmatter-reference.md` (referencia completa YAML)

Ambos se consultan on demand desde `SKILL.md`.

## Notas

- **Regla de portabilidad:** nunca referencies nombres de ficheros específicos de plataforma (`AGENTS.md`, `CLAUDE.md`, `opencode.json`) directamente en un SKILL.md. Usa frases genéricas como "las instrucciones del agente" o "sigue la convención de preguntas al usuario" — los pack scripts renombran estos ficheros según la plataforma.
- **La calidad de la descripción determina la activación.** Los agentes tienden a *infra-activar* skills; una descripción vaga ("quality assessment tool") rara vez se dispara. Sigue el patrón "verbo acción + Use when... + keywords" e incluye 3–5 palabras que el usuario efectivamente dice.
- **Presupuesto de instrucciones:** pasadas ~200 instrucciones discretas, el cumplimiento del LLM tiende a caer. Por cada línea pregunta "¿fallaría el agente sin esta instrucción?" y bórrala si la respuesta es no.
