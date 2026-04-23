# brand-kit

Catálogo centralizado de identidad visual (colores, tipografía, paletas
de charts, tamaños, tono) que cualquier skill de output del monorepo
(`docx-writer`, `pptx-writer`, `pdf-writer`, `web-craft`,
`canvas-craft`) sabe consumir. Incluye **10 temas curados de serie** y
es **extensible por el cliente**: añade los tuyos siguiendo la guía
al final de este fichero.

## Qué resuelve

Cuando un agente va a generar un entregable visual — un informe DOCX,
un deck PPTX, una landing, un PDF analítico — necesita tokens de
diseño coherentes: qué color primario usar, qué fuente display, qué
paleta de charts, qué tono. Antes de existir esta skill, cada skill de
output definía su propia paleta de ejemplo inline, los valores
derivaban entre skills, y los clientes no tenían un sitio único donde
decir "esta es mi marca". `brand-kit` resuelve eso: un solo lugar para
los tokens, todas las skills de output consumen el mismo contrato.

## Temas incluidos

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

Cada fichero de tema contiene el set completo de tokens: los 10
colores core, la paleta categórica de charts, el bloque tipográfico
(familias + tamaños + fallbacks), la familia de tono, los casos
recomendados de uso y los antipatrones.

## Cómo lo usan los agentes

Cuando el agente va a generar cualquier entregable visual, ejecuta
este flujo:

1. Presenta el catálogo anterior al usuario.
2. Pregunta si quiere usar uno de los temas predefinidos, definir un
   tema ad-hoc (proporcionando hex y fuentes directamente) o apuntar
   a un fichero externo de marca como scaffold.
3. Carga el tema elegido (o lo deriva de las entradas del usuario).
4. Pasa los tokens a la skill de output que genera el artefacto.

El flujo completo vive en `SKILL.md` (el contrato que sigue el LLM).
Este README es para ti, la persona que lee el repo.

## Añadir un tema propio

### 1. Duplica un tema existente como plantilla

`editorial-serious.md` es el punto de partida más neutro:

```
cp themes/editorial-serious.md themes/acme-corporate.md
```

El nombre del fichero es el **identificador técnico** — kebab-case,
preferentemente en inglés (el identificador permanece igual en todos
los overlays de idioma).

### 2. Rellena los tokens

Abre el fichero nuevo y sustituye los valores. **Mantén los nombres
de los tokens exactamente como están** — las skills de output los
buscan por nombre:

**Core (obligatorio, no omitir):**
- 10 colores: `primary`, `ink`, `muted`, `rule`, `bg`, `bg_alt`,
  `accent`, `state_ok`, `state_warn`, `state_danger`
- 3 familias de fuente con fallbacks: `display`, `body`, `mono`
- 4 tamaños en pt: `h1`, `h2`, `body`, `caption`
- Paleta categórica de charts: 5–8 colores hex ordenados

**Extensiones opcionales (omítelas si no aplican):**
- `motion_budget` (`minimal` / `restrained` / `expressive`)
- `radius` (píxeles, para web-craft)
- `dark_mode` (subset con `primary` / `ink` / `bg` / `accent` en
  variante oscura)
- `chart_sequential` (color base para heatmaps / escalas secuenciales)
- `print` (subset de tokens afinados para PDF impreso: `paper` cálido
  en vez de blanco puro, `ink` casi negro cálido, hairlines más
  cálidas — consumido por `pdf-writer`. Decláralo si el tema se va a
  usar en impresión y los valores de pantalla se degradarían en papel)

La sección `## Tone family` debe apuntar a uno de los ocho tonos
definidos en `skills-guides/visual-craftsmanship.md` (`editorial-serious`,
`technical-minimal`, `warm-magazine`, `brutalist-raw`,
`luxury-refined`, `industrial-utilitarian`, `playful-toy`,
`forensic-audit`), o declarar un tono nuevo con una descripción corta.

### 3. Registra el tema en DOS sitios

Añade una fila para el tema nuevo en ambas tablas para que el
catálogo quede consistente:

1. La tabla **"Temas incluidos"** de este `README.md` (para que los
   humanos lo vean al abrir la carpeta).
2. La tabla **"Available themes"** de `SKILL.md` de esta misma skill
   (para que el agente lo descubra al cargar la skill).

Con esas dos entradas en su sitio, cualquier agente que incluya
`brand-kit` ofrecerá el tema nuevo como una opción más, exactamente
como los diez de serie.

## Tu marca NO tiene que vivir aquí

Si prefieres mantener el branding del cliente en una skill separada
(p.ej. `<agent>/skills/acme-brand-kit/`), las skills de output la
consumen igual — referencian el concepto de skill de theming
centralizada sin nombrar a `brand-kit`. La regla `local skill wins`
del monorepo garantiza que un `brand-kit` local (o un `acme-brand-kit`)
sobreescriba a este compartido para ese agente.

## Antipatrones al extender

- **No renombres los tokens core** — las skills de output los buscan
  por nombre.
- **No embebas imágenes o logos en el fichero del tema** — un tema
  define tokens, no assets.
- **No inventes tokens fuera del contrato** — las claves desconocidas
  se ignoran en silencio.
- Para traducciones, usa el overlay `es/` en lugar de mezclar idiomas
  dentro de un fichero.
