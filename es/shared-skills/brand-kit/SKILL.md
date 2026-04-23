---
name: brand-kit
description: "Catálogo centralizado de temas de identidad visual (colores, tipografía, tono, paleta de charts, tamaños) que cualquier skill de output (docx-writer, pptx-writer, pdf-writer, web-craft, canvas-craft) consume para producir entregables con branding coherente. Incluye 10 temas curados y es extensible — los clientes pueden añadir sus propios temas como ficheros markdown individuales. Usa esta skill antes de generar cualquier entregable visual para fijar los tokens de marca que aplicarán las skills de output."
argument-hint: "[nombre del tema | 'personalizado' | 'scaffold']"
---

# Skill: brand-kit

El branding vive en un solo sitio. Esta skill proporciona un catálogo
curado de temas de identidad visual — cada uno un paquete completo y
coherente de colores, tipografía, paleta de charts, tamaños y tono —
que cualquier skill de output sabe consumir. Elige un tema una vez y
todos los artefactos derivados (DOCX, PPTX, PDF, web, visual de una
sola página) lo heredan de forma consistente.

La skill no genera artefactos por sí misma. Proporciona tokens.

## Available themes

| Theme | Tone family | Best for |
|---|---|---|
| [editorial-serious](themes/editorial-serious.md) | editorial-serious | informes analíticos largos, legal, policy |
| [technical-minimal](themes/technical-minimal.md) | technical-minimal | dashboards, docs de ingeniería, runbooks |
| [warm-magazine](themes/warm-magazine.md) | warm-magazine | comunicaciones, marketing, storytelling |
| [forensic-audit](themes/forensic-audit.md) | forensic-audit | auditoría, compliance, informes de seguridad |
| [academic-sober](themes/academic-sober.md) | editorial-serious | papers de investigación, whitepapers, policy |
| [modern-product](themes/modern-product.md) | technical-minimal | decks de producto, lanzamientos, pitch |
| [brutalist-raw](themes/brutalist-raw.md) | brutalist-raw | volcados de datos, informes dev, exploratorios |
| [luxury-refined](themes/luxury-refined.md) | luxury-refined | decks de consejo, resúmenes ejecutivos |
| [industrial-utilitarian](themes/industrial-utilitarian.md) | industrial-utilitarian | informes de operaciones, logística, SRE |
| [corporate-formal](themes/corporate-formal.md) | editorial-serious | steering committees, reporting regulado |

El catálogo vive aquí inline para que el agente lo vea en el momento
en que carga la skill, sin lectura adicional.

## Flujo (invoca este flujo ANTES de cualquier skill de output con dimensión visual)

Siempre que el agente vaya a generar un entregable que tenga cualquier
expresión visual (informe DOCX, deck PPTX, documento PDF, landing HTML,
PDF / PNG de una sola página), ejecuta este flujo primero para fijar
los tokens de marca. Saltarse este paso produce artefactos
inconsistentes — fuentes distintas, acentos distintos, sin paleta
compartida de charts entre piezas del mismo proyecto.

### 1. Presenta el catálogo al usuario

Muestra al usuario la tabla "Available themes" de arriba. Manténlo
breve — una línea por tema con `Theme · Tone · Best for` es suficiente.

### 2. Pregunta qué fuente quiere el usuario

Siguiendo la convención de preguntas del agente, ofrece tres vías:

- **Tema predefinido** — elige uno del catálogo por nombre.
- **Personalizado ad-hoc** — el usuario proporciona colores (hex) y
  fuentes directamente en la conversación. Mapea las entradas al
  contrato canónico de tokens (ver §Contrato de tokens).
- **Scaffold externo** — el usuario apunta a un fichero (guía de marca
  en PDF, documento de branding del cliente, memo de diseño). Lee el
  fichero y deriva tokens — normalizando al contrato canónico.

### 3. Carga el tema elegido

Si el usuario eligió un tema predefinido, lee `themes/<nombre>.md` —
ese fichero contiene el set completo de tokens. Si aportó entradas
ad-hoc o un scaffold, construye la misma estructura en memoria desde
esas entradas.

### 4. Pasa los tokens a la skill de output

Cuando invoques la skill de output (docx-writer, pptx-writer,
pdf-writer, web-craft, canvas-craft), proporciónale los tokens
cargados. Cada skill de output sabe mapear los tokens canónicos a su
formato nativo (dict Python para python-docx / python-pptx, HexColor
para reportlab, CSS custom properties para web).

## Contrato de tokens

Cada fichero de tema sigue el mismo contrato para que las skills de
output puedan consumir cualquier tema indistintamente. El contrato
tiene un **core** (obligatorio) y **extensiones opcionales**.

### Core (todo tema debe proveerlo)

**Colores** (10 tokens hex):

| Token | Rol |
|---|---|
| `primary` | títulos, reglas superiores, acentos de portada |
| `ink` | texto cuerpo (rara vez negro puro — un slate medio suele ser más amable) |
| `muted` | captions, notas al pie, texto secundario |
| `rule` | divisores finos, bordes sutiles |
| `bg` | página / superficie principal |
| `bg_alt` | bandas de tabla, callouts, superficies alternas |
| `accent` | CTAs, highlights, pops intencionales (5–15 % de superficie) |
| `state_ok` | indicadores positivos |
| `state_warn` | alertas |
| `state_danger` | errores críticos |

**Tipografía** (3 familias + 4 tamaños):

| Token | Rol |
|---|---|
| `display` | h1/h2/portada — normalmente la más expresiva |
| `body` | texto corrido |
| `mono` | código, cifras en tablas, strings técnicos |
| `size_h1`, `size_h2`, `size_body`, `size_caption` | tamaños en pt |

Cada entrada de fuente incluye una pila de fallbacks para que el tema
degrade dignamente cuando la primera familia no esté disponible.

**Chart categorical**: lista ordenada de 5–8 colores hex, curada para
que los primeros N se vean equilibrados con cualquier número N de
series. Las dos primeras entradas suelen coincidir con `primary` y
`accent` para mantener los charts en diálogo con el resto del artefacto.

### Extensiones opcionales (los temas pueden proveerlas; las skills de output las consumen si están)

- `motion_budget` — `"minimal"` / `"restrained"` / `"expressive"`.
  Usado por web-craft para transiciones y por pptx para animaciones.
- `radius` — border-radius en píxeles. Usado por web-craft.
- `dark_mode` — subset con `primary` / `ink` / `bg` / `accent` de modo
  oscuro. Usado por web-craft cuando se pide variante dark. Si el tema
  omite `dark_mode` y hace falta una variante oscura, deriva
  invirtiendo `bg` ↔ `ink` manteniendo `primary` / `accent`.
- `chart_sequential` — color base para escalas secuenciales / heatmaps.
- `print` — subset de tokens afinados para PDF impreso (`paper`, `ink`,
  `rule`, opcionalmente `accent`). Usado por `pdf-writer`. Decláralo
  cuando los tokens de pantalla se degradarían en papel (`bg` blanco
  puro o `ink` negro puro). Si está ausente, `pdf-writer` aplica
  sensibilidades genéricas de impresión.

## Temas personalizados y externos (cuando ninguno de los 10 encaja)

Si el usuario aporta su propia marca (hex + fuentes ad-hoc, o un
fichero externo de marca como scaffold), incorpórala al mismo contrato
antes de pasarla a la skill de output. Respeta los valores explícitos
del usuario y rellena los huecos con defaults coordinados:

- `ink`, `muted`, `rule`: neutrales derivados de o afinados contra
  `primary` (slate oscuro más suave, gris medio de baja croma, un
  tinte pálido).
- `bg` / `bg_alt`: casi blanco y un tinte al 2–4 % de este.
- Colores de estado: semánticos (verde / ámbar / rojo), afinados a
  la calidez del tema.
- Chart categorical: empieza con `primary` y `accent`, extiende a
  5–8 matices con amplia separación perceptual.

Muestra el set derivado al usuario para confirmación antes de pasar
a la skill de output.

## Extensibilidad

El contrato de tokens es estable: los clientes pueden añadir sus
propios ficheros de tema en `themes/` (misma estructura que los
incluidos) o mantener su branding en una skill local separada. Las
skills de output referencian "skill de theming centralizada" de forma
genérica — la regla `local skill wins` del monorepo hace que un
`<agent>/skills/<marca>/` local sobreescriba la compartida cuando
ambas existan.

## Cuándo NO usar esta skill

- **No hay artefacto visual** (respuesta de chat pura, consulta SQL,
  refactor de código). Sáltate la skill.
- **El AGENTS.md del agente fija un único tema.** Cárgalo directamente
  y sáltate la pregunta.
