# Agente Creador de Skills

Agente experto en diseñar y generar skills para agentes IA — los ficheros `SKILL.md` que amplían las capacidades de un agente, con scripts, guías y referencias de soporte cuando la skill los necesita.

## Qué hace este agente

Skill Creator te guía a través del ciclo completo de creación de una skill: desde entender lo que necesitas, diseñar la estructura, escribir el contenido, revisar la calidad contra un checklist de 14 puntos y empaquetar todo como un ZIP descargable. Sigue principios probados de diseño de skills para garantizar que tus skills sean efectivas, bien estructuradas y portables entre plataformas.

El flujo es **iterativo y human-in-the-loop**: tú confirmas cada hito (requisitos, diseño, contenido generado, revisión) antes de avanzar. También puedes entrar en cualquier fase — por ejemplo, pegar un `SKILL.md` existente y pedir una revisión, o entregar una carpeta de ficheros e ir directamente al empaquetado.

## Cómo funciona

1. **Triaje** — Entender si estás diseñando una skill nueva, revisando una existente, mejorando una descripción o empaquetando ficheros ya preparados.
2. **Recogida de requisitos** — Entrevista estructurada para capturar qué hace la skill, cuándo debe activarse, inputs/outputs y los ficheros de soporte que necesita.
3. **Diseño** — Define el frontmatter (name, description, triggers), la estructura del body y el layout de ficheros de soporte. Se presenta para tu aprobación.
4. **Generación** — Escribe el `SKILL.md` y los scripts, referencias o guías de soporte en `output/<skill-name>/`.
5. **Revisión** — Ejecuta el checklist de calidad de 14 puntos y te guía por los hallazgos. Pide cambios y el agente vuelve al paso correspondiente.
6. **Empaquetado** — Produce un ZIP de la carpeta de la skill, listo para integrarlo en un agente o compartirlo.

Puedes entrar en cualquier fase. "Revisa este SKILL.md" salta a la fase 5. "Empaqueta estos ficheros" salta a la fase 6. "Mejora la descripción de mi skill" se centra en la fase 3 sobre ese campo concreto.

## Estructura de salida

Las skills se generan bajo `output/<skill-name>/` con un layout predecible — las skills pequeñas son un único `SKILL.md`, las más grandes incluyen carpetas de soporte:

```
output/<skill-name>/
├── SKILL.md                    # Punto de entrada con frontmatter y body
├── scripts/                    # (Opcional) scripts auxiliares invocados por la skill
├── references/                 # (Opcional) documentos o datos de referencia que la skill lee
└── assets/                     # (Opcional) imágenes, plantillas, fixtures
```

## Capacidades

- Diseñar skills desde cero mediante entrevistas guiadas
- Generar ficheros `SKILL.md` con frontmatter adecuado y contenido estructurado
- Crear ficheros de soporte (guías, scripts, referencias, assets) para skills complejas
- Revisar skills existentes contra un checklist de calidad de 14 puntos
- Mejorar descripciones de skills para una activación más precisa
- Empaquetar skills como ficheros ZIP listos para desplegar

## Qué puedes preguntar

### Crear skills
- "Crea una skill para revisar pull requests"
- "Necesito una skill que genere documentación de API a partir del código"
- "Diseña una skill para flujos de migración de base de datos"

### Trabajar con contenido existente
- "Revisa esta skill y sugiere mejoras" (pega tu `SKILL.md`)
- "Mejora la descripción de mi skill de deploy"
- "Empaqueta mis ficheros de skill como ZIP"

### Aprender sobre diseño de skills
- "¿Cómo debería escribir una buena descripción de skill?"
- "¿Cuándo una skill debería tener ficheros de soporte vs contenido inline?"
- "¿Qué hace que una skill se active de forma fiable?"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/skill-creator` | Referencia completa para creación de skills: anatomía, frontmatter, patrones de escritura, checklist de calidad de 14 puntos |

## Cómo empezar

Inicia el agente y describe qué skill necesitas: "Crea una skill para [tu caso de uso]". El agente te guiará paso a paso por el proceso y esperará tu aprobación en cada hito.
