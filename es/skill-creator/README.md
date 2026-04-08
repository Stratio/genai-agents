# skill-creator

Agente para diseñar y generar skills de alta calidad para agentes IA (ficheros SKILL.md). Guía al usuario a través de un flujo interactivo: recopilación de requisitos, diseño de la skill, generación, revisión de calidad y empaquetado como ZIP.

## Capacidades

- Recopilación interactiva de requisitos mediante entrevistas estructuradas
- Generación de SKILL.md siguiendo principios probados de diseño de skills
- Generación de ficheros de soporte (guías, scripts, referencias)
- Revisión de calidad con un checklist de 14 puntos
- Mejora iterativa basada en feedback del usuario
- Empaquetado como ZIP del paquete completo de la skill

## Requisitos

- Sin dependencias externas (ni Python, ni MCPs)
- Comando `zip` para empaquetado (fallback a `tar` si no está disponible)

## Skills

| Skill | Comando | Descripción |
|-------|---------|-------------|
| Skill Creator | `/skill-creator` | Guía completa para crear skills de calidad: anatomía, frontmatter, patrones de escritura y checklist de calidad |

## Scripts de empaquetado

### Scripts genéricos (desde la raíz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|--------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent skill-creator` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent skill-creator` |

Todos los scripts aceptan `--lang <code>` para generar la salida en un idioma específico (ej: `--lang es` para español).

## Inicio rápido

```bash
# Empaquetar para Claude Code
bash ../pack_claude_code.sh --agent skill-creator

# Empaquetar para OpenCode
bash ../pack_opencode.sh --agent skill-creator

# Empaquetar en español
bash ../pack_claude_code.sh --agent skill-creator --lang es
```
