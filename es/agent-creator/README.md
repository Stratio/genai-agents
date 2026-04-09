# agent-creator

Agente para diseñar y generar agentes IA completos para la plataforma Stratio Cowork. Guía al usuario a través de un flujo interactivo: recopilación de requisitos, diseño de arquitectura, generación del AGENTS.md, creación de skills, revisión de calidad y empaquetado como ZIP agents/v1.

## Capacidades

- Recopilación interactiva de requisitos mediante entrevistas estructuradas (3 rondas)
- Diseño de arquitectura del agente: fases del flujo de trabajo, tablas de triaje, descomposición en skills
- Generación de AGENTS.md siguiendo patrones de diseño probados
- Creación de skills para el agente (delegando a `/skill-creator`)
- Generación de ficheros de soporte: README.md, opencode.json
- Revisión de calidad con un checklist de 26 puntos
- Empaquetado como ZIP `agents/v1` de Stratio Cowork

## Requisitos

- Sin dependencias externas (ni Python, ni MCPs)
- Comando `zip` para empaquetado (fallback a `tar` si no está disponible)

## Skills

| Skill | Comando | Descripción |
|-------|---------|-------------|
| Agent Designer | `/agent-designer` | Diseño de arquitectura de agentes: patrones de flujo de trabajo, plantillas de triaje, generación de AGENTS.md, checklist de calidad |
| Agent Packager | `/agent-packager` | Empaquetado agents/v1 de Stratio Cowork: estructura ZIP, metadatos, validación |
| Skill Creator | `/skill-creator` | Guía completa para crear skills de calidad (shared skill del monorepo) |

## Scripts de empaquetado

### Scripts genéricos (desde la raíz del monorepo)

| Script | Plataforma destino | Output | Ejemplo |
|--------|--------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent agent-creator` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent agent-creator` |
| `pack_stratio_cowork.sh` | Stratio Cowork | `dist/<name>-stratio-cowork.zip` | `bash ../pack_stratio_cowork.sh --agent agent-creator` |

Todos los scripts aceptan `--lang <code>` para generar la salida en un idioma específico (ej: `--lang es` para español).

## Inicio rápido

```bash
# Empaquetar para Claude Code
bash ../pack_claude_code.sh --agent agent-creator

# Empaquetar para OpenCode
bash ../pack_opencode.sh --agent agent-creator

# Empaquetar para Stratio Cowork
bash ../pack_stratio_cowork.sh --agent agent-creator

# Empaquetar en español
bash ../pack_claude_code.sh --agent agent-creator --lang es
```
