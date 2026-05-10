# web-craft

Skill compartida para construir frontends web interactivos de calidad producción (HTML/CSS/JS, React, Vue) con dirección estética deliberada. Produce código que funciona — componentes, páginas, landings, dashboards, artefactos interactivos — evitando el "Inter + púrpura suave + cards de Bootstrap" genérico por defecto.

Skills visuales compañeras: `canvas-craft` para artefactos estáticos de página única (posters, portadas, certificados) y `pdf-writer` para documentos tipográficos multipágina. Las tres comparten el guide `visual-craftsmanship.md` y se complementan — usa la tabla de disambiguation de ese guide cuando tengas dudas.

## Qué hace

- Toma el brief del usuario (qué construir, quién lo usa, restricciones técnicas) y ejecuta una pasada de cinco decisiones antes de escribir código: clase de artefacto, tono, pareado tipográfico, paleta, ritmo / motion.
- Elige un tono único y comprometido de una taxonomía de 10 (8 familias compartidas + 4 específicas de web: playful-toy, retro-futuristic, natural-organic, forensic-audit).
- Produce CSS con paletas de custom properties, fuentes variables vía `@import` o WOFF2 empaquetado, escalas tipográficas modulares y motion budgets que respetan `prefers-reduced-motion`.
- Genera componentes React (Motion library para coreografía) o Vue (Vue Motion o CSS nativo) cuando el stack lo pide.
- Aplica un checklist de craftsmanship al output: alineación en cada breakpoint, color de acento dentro del 5–15% de la superficie, sin cadenas placeholder, estados hover/focus/active coherentes con el tono.

## Cuándo usarla

- El usuario pide un componente, página, landing, dashboard o artefacto interactivo.
- Un artefacto estático con tipografía como elemento visual (poster, portada, one-pager) — **no** uses `web-craft`, usa `canvas-craft`.
- Un documento multipágina de prosa o tablas (informe, invoice, contrato) — **no** uses `web-craft`, usa `pdf-writer`.
- Un dashboard interactivo con KPIs es un caso claro de `web-craft`.

## Dependencias

### Otras skills
- **Skills visuales compañeras:** `canvas-craft` (estático de página única), `pdf-writer` (documentos tipográficos).
- **Skill de theming opcional:** una skill centralizada de theming (p.ej. `brand-kit`) es **muy recomendable**. Cuando está disponible, el agente ejecuta su workflow de selección de tema *antes* de programar; el tema elegido provee los tokens del bloque `:root`. Cuando no hay skill de theming presente, la skill improvisa tokens siguiendo `visual-craftsmanship.md`.

### Guides
- `visual-craftsmanship.md` — principios estéticos compartidos para toda skill visual: las cinco decisiones de diseño, taxonomía de tonos, roles de paleta, filosofía de pareado tipográfico, antipatrones a rechazar y tabla de disambiguation entre `web-craft` / `canvas-craft` / `pdf-writer`.

### MCPs
Ninguno.

### Python
Ninguno — esta skill produce código web, no Python.

### Sistema
- **Runtime de navegador solamente** — el output corre en cualquier navegador moderno.
- **Opcional:** Node.js / npm si el proyecto host compila componentes React o Vue con bundler. La skill no requiere un paso de build por sí misma; ship código consumible de ambas formas.
- **Opcional:** ficheros de fuentes — las fuentes se sirven desde Google Fonts / foundries oficiales vía `@import` por defecto; empaqueta WOFF2 localmente solo cuando el artefacto es para distribución externa (incluir ficheros de licencia).

## Activos empaquetados
Ninguno. Las fuentes y las imágenes se traen en runtime (Google Fonts) o las provee el proyecto host.

## Notas

- **Comprométete con un solo tono.** La mezcla tibia de dos tonos es la causa más común de output genérico.
- **Escasez del color de acento:** aplica el acento dominante al 5–15% de la superficie visible; la saturación se gana por restricción.
- **El motion budget es explícito:** `none`, `minimal` o `expressive`. Cualquier animación debe respetar `@media (prefers-reduced-motion: reduce)`.
- **Las fuentes de Google Fonts son válidas para artefactos internos;** para distribución externa, empaqueta WOFF2 con ficheros de licencia.
