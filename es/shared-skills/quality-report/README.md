# quality-report

Skill compartida que coordina la producción del informe formal de cobertura de calidad del dato. Guidance-first: orquesta el ensamblado del contenido y delega la generación de ficheros a las skills de escritura del agente (`pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`, `xlsx-writer`) más la skill centralizada de theming (`brand-kit`).

Cada agente host habilita los formatos permitidos en función de las writer skills que declare en su manifiesto `shared-skills`.

## Excepción a la regla de self-containment

Las skills compartidas son, por norma, autocontenidas — ningún SKILL.md en `shared-skills/` referencia a otra shared-skill por nombre, de modo que cualquiera pueda empaquetarse standalone.

`quality-report` es una **excepción explícita**: su `SKILL.md` referencia a `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`, `xlsx-writer` y `brand-kit` por nombre. La justificación es pragmática — la misma estructura de informe debe materializarse en 6 formatos distintos, y cada formato tiene una writer skill dedicada con su propio workflow guidance-first. Inlinar cada pipeline de formato dentro de `quality-report` duplicaría miles de líneas de instrucción que ya viven en las writer skills.

**Contrato que fija el monorepo**: cualquier agente que declare `quality-report` en su manifiesto `shared-skills` debería declarar también `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`, `xlsx-writer` y `brand-kit` para que la skill pueda materializar el rango completo de formatos de fichero. Un agente chat-oriented puede optar por no declarar el bundle de writers; en ese caso el pre-check de `quality-report` detecta la ausencia y restringe la oferta al formato Chat, con lo que las referencias a writer skills del SKILL.md nunca se disparan en runtime.

## Qué hace

- Recopila los datos de cobertura de calidad del contexto de la conversación (o vía MCP si faltan): inventario de reglas, definiciones de dimensiones, metadatos de tablas, profiling.
- Compone la estructura canónica de seis secciones (Resumen ejecutivo → Cobertura → Reglas → Gaps → Recomendaciones) en el idioma del usuario.
- Escribe un `quality-report.md` interno como única fuente de verdad dentro de `output/YYYY-MM-DD_HHMM_quality_<slug>/`.
- Para el formato Chat: renderiza directamente en la respuesta, sin invocar ninguna writer skill.
- Para formatos de fichero (PDF, DOCX, PPTX, Dashboard web, Póster/Infografía, XLSX): resuelve el tema de marca a través de la cascada del agente host, carga la writer skill correspondiente y produce el entregable aplicando tokens de marca y siguiendo `quality-report-layout.md`.

## Ficheros de la skill

- `SKILL.md` — punto de entrada, workflow y lógica de selección de formato.
- `quality-report-layout.md` — estructura canónica, iconografía, KPI cards, composición por formato, reglas de layout determinista para auditoría.
- `README.md` — este fichero.

## Guía local

- `quality-report-layout.md` — aplicada por las writer skills cuando producen un entregable de quality-report. Describe qué contiene el informe y cómo se comporta en cada formato; deja la voz visual (tono, tipografía, motion) a las writer skills.

## Dependencias

Ninguna directa en esta skill. Toda la generación de ficheros se delega a las writer skills que declare el agente host. Cada writer skill gestiona sus propias dependencias de runtime.

## Cómo incluir esta skill en un agente

Al añadir `quality-report` al manifiesto `shared-skills` de un agente, declararla junto a las writer skills `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` y `xlsx-writer`, más la skill centralizada de theming `brand-kit`. Ese bundle es lo que permite al agente entregar el rango completo de formatos (PDF, DOCX, PPTX, Dashboard web, Póster/Infografía, XLSX). Si el agente es chat-oriented y omite los writers por diseño, al usuario solo se le ofrecerá el formato Chat — que es una configuración válida y soportada.
