# Guía de artesanía visual

Principios compartidos para cualquier skill que produzca salida visual — interfaces interactivas, artefactos estáticos, documentos tipográficos, dashboards, informes. Trátala como la fuente de verdad para decisiones estéticas en todo el monorepo.

## Por qué existe esta guía

La salida visual generada por defecto tiene un aspecto inconfundible: Inter o system sans por todas partes, violetas suaves sobre blanco roto, tarjetas equiespaciadas con sombras idénticas, tablas centradas en la página sin personalidad en los márgenes. Esa estética es *segura* en el peor sentido — comunica "nadie ha decidido nada".

Las skills que referencian esta guía resisten ese por defecto. Cada artefacto que llega al usuario debe llevar la huella de una decisión deliberada: un tono al que se compromete, una paleta con saturación, una tipografía elegida por significado y no por disponibilidad, espacio organizado con intención. Incluso una gráfica de un minuto merece tres minutos de criterio visual antes.

## Principios fundamentales

### 1. Diseñar antes de codificar
Declara la dirección estética en palabras antes de escribir una línea de markup, reportlab o CSS. Dos párrafos de intención cuestan menos que refactorizar un artefacto terminado.

Cinco decisiones, en este orden:
1. **Clase de artefacto** — ¿qué es esto? (Dashboard, brief ejecutivo, póster, certificado, informe técnico, factura, zine, landing page.) Su clase gobierna todo lo demás.
2. **Tono** — elige uno y comprométete. Editorial-serio, técnico-minimal, revista-cálida, brutalista-crudo, lujo-refinado, industrial-utilitario, juguetón-lúdico, forense-auditor. Una mezcla tibia de dos tonos es peor que cualquier extremo.
3. **Emparejamiento tipográfico** — una fuente display para titulares o momentos de display, una fuente body para prosa o datos. Dos tipografías cubren casi cualquier artefacto; tres es el techo práctico.
4. **Paleta** — un acento dominante con saturación real, un neutro profundo para texto (raramente negro puro), un neutro claro para fondos o filetes, más acentos opcionales usados con parquedad.
5. **Ritmo** — márgenes, estructura de columnas, línea base, presupuesto de motion (para artefactos interactivos). Márgenes generosos leen como seguridad; márgenes apretados leen como un default de procesador de textos.

### 2. Comprometerse con la dirección
La intensidad importa menos que la coherencia. Minimalismo y maximalismo ambos funcionan; "un poco de todo" nunca. Una vez elegida la dirección, cada elemento — textura de fondo, hover, color de gráfica, borde de tabla — se gana su sitio sirviendo a esa dirección o se elimina.

### 3. Artesanía como estándar, no como eslogan
Un artefacto terminado debe llevar las marcas de trabajo deliberado: línea base consistente, márgenes alineados, contraste intencional, ninguna pauta de stock por accidente, ninguna leyenda huérfana, ningún texto solapado. El último pase es para pulir, no para añadir. Si el instinto pide dibujar una forma más, párate y refina lo que ya está.

### 4. Hacerlo inconfundible
Un movimiento memorable supera a diez toques educados. Un contraste tipográfico inusual, un único momento hero que rompe la rejilla, una textura de fondo acorde al tema, un hover que sorprende — cualquiera de estos, ejecutado con cuidado, eleva un artefacto de genérico a considerado.

## Anti-patrones a rechazar

Son los delatores de la salida por defecto. Ninguno es absolutamente prohibido, pero cada uno debe ser una elección consciente contra la alternativa, no un reflejo.

- **Sans genérica como única tipografía**: Arial, Helvetica, Roboto, Inter y system-ui sin estilo por todas partes. Si el artefacto merece atención, su tipografía debe ser parte de lo que se la gana.
- **Paletas deslavadas**: tintes pastel sin saturación, grises sin temperatura, y especialmente los degradados violeta sobre blanco (la estética de IA más sobreexpuesta).
- **Simetría por costumbre**: todo centrado, sombras idénticas en todas las tarjetas, márgenes iguales en los cuatro lados cuando el contenido no lo pide.
- **Tarjetas con forma de Bootstrap**: rectángulos con sombra de 6–8 px y padding de 1 rem, dispuestos en rejilla de tres columnas, en cada página, sin importar el contenido.
- **Aglomeración tipográfica de tres fuentes**: display + body + fuente "acento" apiladas sin razón. Dos bastan para casi cualquier artefacto.
- **Decoración de gráficas**: cuadrículas en todas las direcciones, barras en 3D, paletas categóricas arcoíris, leyendas flotando por dentro de los datos.
- **Tabla como caja negra**: zebrado por defecto, bordes internos pesados, columnas numéricas centradas.
- **Rectángulos blancos sueltos**: titulares flotando en medio del espacio blanco sin anclaje estructural (sin filete, sin pista de margen, sin variación de fondo).

## Roles de paleta

Define los colores por rol, no por nombre de tono. Cuatro roles cubren casi cualquier artefacto:

| Rol | Propósito | Guía |
|---|---|---|
| Acento dominante | El color único que marca la marca o el tema del artefacto. | Saturación real. Aplica a un 5–15 % del área visible — titulares, marcas clave, momentos hero. |
| Neutro profundo | Cuerpo de texto, trazos primarios, datos densos. | Raramente `#000`. Prefiere un carbón desaturado, un café oscuro, un índigo profundo. |
| Neutro claro | Fondos, filetes, divisores de tabla. | No blanco puro. Un blanco roto, hueso o una superficie apenas tintada lee más intencional. |
| Acentos aceptables | Segundo y tercer color para estado (positivo/negativo, éxito/error, anotaciones). | Uso parco. Saturación coherente con el dominante — nada de un neón suelto junto a un primario apagado. |

Seis colores renderizados son suficientes. Tokenízalos; nunca teclees un hex dos veces a mano.

## Filosofía del emparejamiento tipográfico

Elige una fuente display y una body. El emparejamiento debe crear contraste deliberado, no una combinación segura.

Ejes de contraste útiles:
- Serif display + sans body (editorial clásico).
- Sans display + serif body (revista moderna).
- Mono display + sans body (técnico-forense).
- Sans condensada display + sans ancha body (editorial-gráfico).

Reglas prácticas:
- Fuente body: cobertura amplia de idiomas, humanista lo bastante para leerse a 9–11 pt en prosa, con itálica y bold.
- Fuente display: gana atención a partir de 24 pt. Puede ser idiosincrática; no necesita itálica completa.
- Trata a los números en serio. Si el artefacto muestra muchas cifras, usa una fuente monoespaciada o de cifras tabulares/lining.
- No mezcles dos serif ni dos sans-serif con siluetas parecidas. El emparejamiento debe leerse a simple vista: *estas son claramente distintas*.

Cada skill que use esta guía debe definir su lista corta de emparejamientos por clase de artefacto. Esta guía no prescribe familias concretas — las foundries cambian, las licencias cambian, y cada medio tiene restricciones distintas.

## Checklist de artesanía

Antes de entregar, haz un último pase. El objetivo de este pase es contención, no adición.

- Todo elemento alineado lo está de verdad. Líneas base, bordes izquierdos, parte superior de columnas.
- Los márgenes son consistentes y respetan el ritmo propuesto.
- Ningún texto solapado, ninguna etiqueta huérfana, ninguna leyenda invadiendo la zona de la gráfica.
- Los colores aparecen en las cantidades para las que se diseñaron. Una paleta de cinco colores no debe mostrar siete.
- La tipografía no tiene pesos ni estilos no intencionales. Un peso "light" no se ha colado en un titular.
- Cada imagen, textura o patrón tiene una razón. Si se puede eliminar sin debilitar el artefacto, elimínalo.
- Cualquier texto que parezca relleno — "Lorem ipsum", captions placeholder, cadenas demo por defecto — ha desaparecido.
- Para artefactos con motion: respeta las preferencias de movimiento reducido; ninguna animación en bucle sin razón; nada se mueve donde el usuario necesita leer.

## Disambiguación entre skills visuales

Tres skills del monorepo producen salida visual y comparten deliberadamente esta guía. Son complementarias, no solapadas.

| Skill | Medio | Cuándo usarla |
|---|---|---|
| `web-craft` | Frontend interactivo (HTML/CSS/JS, React, Vue) | Componentes, páginas, landings, dashboards, artefactos interactivos. El artefacto vive en un navegador. |
| `canvas-craft` | Artefacto estático de una sola página (PDF o PNG) | Pósters, portadas, certificados, one-pagers de marketing, infografías. La composición visual domina (aproximadamente un setenta por ciento o más de la superficie). Texto mínimo, tipografía como elemento visual. |
| `pdf-writer` | Documento tipográfico multi-página, o documento de una sola página dominado por prosa, tablas o datos (PDF) | Informes analíticos, estados financieros, facturas, contratos, zines editoriales, documentación técnica. Tipo y ritmo dominan; la disposición sirve a la lectura. |

### Casos frontera

- **One-pager ejecutivo, prosa densa y KPIs** → `pdf-writer`. El artefacto se lee; no posa.
- **One-pager de marketing, imagen hero y una afirmación** → `canvas-craft`. El artefacto posa; no se lee.
- **Dashboard interactivo con KPIs** → `web-craft`. La interacción es el punto.
- **Informe con portada diseñada** → pipeline combinada: `canvas-craft` produce la portada, `pdf-writer` ensambla el cuerpo, merge final con `pypdf`.

Cuando ninguna de estas encaja limpiamente, es probable que el artefacto necesite más definición antes de elegir herramienta. Vuelve a las cinco decisiones del principio de esta guía y clasifica primero el artefacto.

## Nota sobre distribución standalone

Si esta guía se empaqueta dentro de una única skill para distribución externa (sin las otras skills visuales al lado), la tabla de disambiguación de arriba sigue aportando contexto. Indica que la skill pertenece a una familia de tres skills con responsabilidades distintas. Los consumidores sin las skills compañeras pueden seguir usando los principios — la selección de tono, los anti-patrones, los roles de paleta y el checklist son autocontenidos y no dependen de las otras skills.
