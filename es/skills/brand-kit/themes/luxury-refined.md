# Luxury Refined (draft v1)

Neutro cálido sobre crema, display serif, espaciado generoso, un único
accent metálico contenido. El tema se lee como considerado, premium,
sin prisa — construido para decks de consejo, resúmenes ejecutivos y
entregables a clientes premium donde la forma misma comunica calidad.

> **Draft v1** — este tema se diseñó para este kit desde el tono
> `luxury-refined` definido en `skills-guides/visual-craftsmanship.md`. No hay
> precedente directo en el monorepo. Itérese según feedback de los
> primeros usos.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #2a211a | cabeceras, capitulares, reglas de acento |
| ink | #2a211a | texto cuerpo (igual que primary para cohesión tonal) |
| muted | #7a6f63 | captions, atribuciones |
| rule | #e8dfd2 | divisores delicados |
| bg | #f8f0e3 | página color crema |
| bg_alt | #efe5d3 | sidebar, pull quotes |
| accent | #8b6f47 | restricción bronce / metálica |
| state_ok | #4d7c3a | positivo (atenuado, no vivo) |
| state_warn | #a17c2a | alertas (coordinadas con el bronce del accent) |
| state_danger | #7a2121 | errores críticos (profundo, no rojo urgente) |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #2a211a | coincide con primary |
| 2 | #8b6f47 | coincide con accent |
| 3 | #4d7c3a | verde atenuado |
| 4 | #5c4a6c | berenjena |
| 5 | #a17c2a | segundo metálico |
| 6 | #7a6f63 | neutro de relleno |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Italiana | 34 | Didot, Bodoni, serif |
| h2 | Italiana | 22 | Didot, Bodoni, serif |
| body | Crimson Pro | 11 | Georgia, serif |
| caption | Crimson Pro Italic | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

Serif display de alto contraste (Italiana es de trazo fino y elegante)
emparejada con un serif de libro sólido para el body.

## Optional extensions

- **Motion budget**: `restrained` (reveals lentos, nunca bruscos)
- **Border radius**: `1px`
- **Dark mode variant**: no incluido (los temas de lujo raramente van
  oscuros — la calidez del crema es el punto)
- **Chart sequential**: color base `#8b6f47`

## Tone family

`luxury-refined`.

## Best used for

- Decks de consejo, cartas del presidente, libros de visión anual
- Entregables de asesoramiento a cliente privado
- Documentos para steering committee y resúmenes ejecutivos
- Cualquier artefacto donde "premium" forma parte del mensaje

## Anti-patterns

- No usar colores vivos saturados en charts — la paleta entera vive
  en cálidos atenuados y un metálico contenido.
- No usar para dashboards de datos densos; el espaciado generoso y
  la display elegante se desperdician en componentes pequeños
  repetidos.
- No sustituir el `bg` crema por blanco puro; el off-white cálido es
  lo que separa este tema del corporativo genérico.
