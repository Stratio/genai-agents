---
name: web-craft
description: "Construye frontends interactivos (HTML/CSS/JS, React, Vue) distintivos y de calidad producción, con dirección estética deliberada. Úsala cuando el usuario pida un componente, página, landing, dashboard, artefacto interactivo o cualquier UI web con estilo. Produce código que funciona — tipografía, paleta, motion y composición se eligen, no se asumen."
argument-hint: "[componente|pagina|dashboard|landing] [proposito o brief]"
---

# Skill: Web Craft

Guía para construir artefactos web interactivos con intención estética real. El entregable es código que se ejecuta: HTML, CSS, JavaScript; componentes de React o Vue cuando el stack circundante lo pide. Cada artefacto debe llevar la huella de una elección visual deliberada — no el aspecto por defecto que produciría un generador.

El usuario aporta el brief: qué construir, quién lo usa, qué restricciones técnicas aplican. El alcance puede ser un componente único o una landing completa.

**Alcance**: esta skill gestiona artefactos que viven en un navegador y responden a interacción. Para artefactos estáticos de una sola página (pósters, portadas, certificados, one-pagers de marketing, infografías) el artefacto no es interactivo y pertenece a otra herramienta. Para documentos tipográficos multi-página (informes, facturas, contratos, zines) la salida es un documento, no una interfaz web, y también pertenece a otra herramienta. Cuando haya duda, consulta `skills-guides/visual-craftsmanship.md` para el criterio de selección.

## 1. Lee la base

Lee y sigue `skills-guides/visual-craftsmanship.md`. Define los principios compartidos, anti-patrones, roles de paleta, filosofía de emparejamiento tipográfico y checklist de artesanía usados en todas las skills visuales del monorepo. Esta skill añade encima las decisiones específicas de web.

## 2. Decide antes de codificar

Trabaja las cinco decisiones de abajo antes de escribir markup. Captura el resultado brevemente — dos o tres párrafos en chat bastan — para que la implementación sirva a una intención declarada, no a una sensación que deriva.

### 2.1 Clasifica el artefacto
Elige uno:
- **Componente interactivo** — un elemento discreto pensado para encajar en un contenedor (botón, tarjeta, formulario, bloque de gráfica, menú).
- **Página** — una página completa con header, contenido y footer si procede.
- **Landing** — una página de marketing o de producto optimizada para un único mensaje y una única acción.
- **Dashboard** — una superficie interactiva orientada a datos (KPIs, filtros, gráficas, tablas).
- **Artefacto interactivo** — una pieza experiencial: un juguete, una demo, un experimento visual.

La clase condiciona el emparejamiento tipográfico, el presupuesto de motion y la densidad esperada de contenido.

### 2.2 Elige un tono (uno, comprometido)
Escoge exactamente uno:
- Editorial-serio
- Técnico-minimal
- Revista-cálida
- Brutalista-crudo
- Lujo-refinado
- Industrial-utilitario
- Juguetón-lúdico
- Retro-futurista
- Natural-orgánico
- Forense-auditor

El tono no comprometido es la causa más frecuente de salida genérica. Si dos tonos parecen igual de correctos para el brief, fuerza la elección — la mitad-y-mitad pierde ambos.

Los primeros seis tonos siguen la taxonomía compartida de `skills-guides/visual-craftsmanship.md`; los cuatro restantes son adiciones específicas de web que rara vez se aplican a artefactos estáticos.

### 2.3 Elige un emparejamiento tipográfico
Una fuente display + una fuente body, con contraste deliberado. Emparejamientos que funcionan bien en el navegador:

| Tono | Display | Body |
|---|---|---|
| Editorial-serio | Fraunces o Instrument Serif | Inter variable o IBM Plex Sans |
| Técnico-minimal | Work Sans o Instrument Sans | JetBrains Mono (para cifras) + Inter body |
| Revista-cálida | Big Shoulders Display | Lora |
| Brutalista-crudo | Boldonse o Archivo Black | Inter condensed |
| Lujo-refinado | Italiana o Fraunces Italic | Crimson Pro |
| Juguetón-lúdico | Bungee | Work Sans |
| Natural-orgánico | Young Serif | Fraunces body |
| Forense-auditor | IBM Plex Mono | IBM Plex Serif |

Son puntos de partida, no mandatos. Sustituye cuando el brief pida otra cosa. El objetivo es no acabar defaulteando a Inter + Arial en todo.

Sirve fuentes mediante `@import` desde Google Fonts o desde la distribución oficial del foundry, o empaqueta WOFF2 junto al artefacto. No distribuyas fuentes sin sus licencias si el artefacto se distribuye externamente.

### 2.4 Comprométete con una paleta
Un acento dominante, un neutro profundo para texto (raramente negro puro), un neutro claro para fondos (no blanco puro), colores de acento opcionales. Declara la paleta en custom properties CSS; nunca teclees el mismo hex dos veces a mano.

Los valores concretos vienen del tema, no de esta skill.

- **Si el agente tiene disponible una skill de theming centralizada** (una skill tipo brand-kit que aporta un catálogo de temas más un flujo para que el usuario elija o defina uno), ejecuta ese flujo ANTES de codear. El tema elegido provee el set de tokens que se mapea al `:root` de abajo.
- **Si no hay tal skill disponible**, improvisa tokens coherentes con el contexto del entregable siguiendo los roles de paleta tonal en `skills-guides/visual-craftsmanship.md`.

El bloque `:root` de abajo usa placeholders para dejar claro de dónde vienen los valores:

```css
:root {
    --accent: <hex>;               /* dominante — parco, 5–15% de la superficie */
    --text: <hex>;                 /* neutro profundo */
    --surface: <hex>;              /* neutro claro */
    --rule: <hex>;                 /* divisores sutiles (a menudo derivados de --text) */
    --positive: <hex>;             /* acento de estado — solo para estado */
    --negative: <hex>;
}
```

### 2.5 Define ritmo, presupuesto de motion y composición
- **Márgenes y columnas**: márgenes generosos comunican seguridad; márgenes apretados leen como procesador de textos. Decide la rejilla base (habitualmente 4 u 8 px).
- **Presupuesto de motion**: `none` (estático), `minimal` (fade-in al montar, transiciones en hover), `expressive` (reveal escalonado, scroll-triggered, transiciones hero). Respeta `prefers-reduced-motion: reduce` sin excepción.
- **Composición**: un único momento hero por vista basta. Romper la rejilla en un sitio; rejilla estricta en el resto. Asimetría donde sirva al contenido.

## 3. Implementa

Con las cinco decisiones registradas, escribe el código. Algunas reglas prácticas:

### Tipografía
- Usa una variable font cuando esté disponible; menos peticiones HTTP, más flexibilidad de peso.
- Establece una escala tipográfica modular (por ejemplo 1.250 × o 1.333 ×) y respétala.
- Interlineado: 1.4–1.6 para body; 1.05–1.2 para display.
- Evita sombras de texto en el body.

### Color y tema
- Custom properties CSS para todo. Override en `:root` para modo oscuro vía `@media (prefers-color-scheme: dark)` cuando el diseño lo soporte.
- Aplica el acento al 5–15 % de la superficie visible — no más. La saturación se gana su sitio por escasez.

### Motion
- Prefiere animaciones CSS-only con `@keyframes` prefijados para evitar colisiones con la página host.
- Respeta `@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }`.
- En React: librería Motion (antes Framer Motion) para transiciones coreografiadas. En Vue: Vue Motion o transiciones CSS nativas.
- El motion de carga de página debe ser breve (~250–400 ms total). Reveal escalonado con `animation-delay: calc(var(--index) * 80ms)`.

### Composición
- La asimetría es herramienta, no regla. Úsala cuando sirva a la jerarquía.
- El espacio negativo es contenido. Las regiones vacías comunican.
- Un elemento que rompa la rejilla por vista; el resto la respeta.

### Fondos
- Un color sólido está bien. El blanco plano rara vez es la mejor elección.
- Gradientes de malla, texturas de ruido y overlays de grano añaden atmósfera sin imágenes.
- Si usas imágenes, recorta con audacia. Las imágenes recortadas parecen compuestas; el full-bleed centrado normalmente no.

### Específicamente para dashboards
- Fuente display para los números hero de los KPIs; fuente body para etiquetas, captions, tooltips.
- Cifras monoespaciadas o tabulares/lining en tablas de datos densas.
- Hover states en cada elemento interactivo; deben comunicar affordance, no solo cambiar de color.
- Filtros y controles agrupados y alineados — no dispersos en una fila.
- Gráficas: paletas de un solo color o dos colores por gráfica; evita categóricos arcoíris salvo que los datos tengan de verdad muchas categorías sin relación ordinal.

## 4. Pase final

Trabaja el checklist de artesanía de `visual-craftsmanship.md` antes de dar por terminado:
- La alineación se sostiene en todos los breakpoints.
- Se respeta la preferencia de movimiento reducido.
- Nada de Lorem, ninguna imagen placeholder, ninguna cadena demo por defecto.
- Las fuentes cargan con `font-display: swap` o equivalente; el stack de fallback es sensato.
- El acento aparece en la proporción prevista — no se escapa por toda la superficie.
- Hover, focus y active existen todos y todos siguen el tono.

Pulido sobre adición. Si el instinto pide añadir un elemento más, refina en su lugar lo que ya está.
