---
name: update-memory
description: Actualizar la memoria persistente del agente con preferencias del usuario, patrones de datos y heuristicas descubiertas. Se invoca automaticamente al final de cada analisis o manualmente cuando el usuario quiera registrar preferencias.
argument-hint: [preferencia o patron a recordar (opcional)]
---

# Skill: Actualizacion de Memoria Persistente

Gestiona la escritura en `output/MEMORY.md` — el fichero de conocimiento curado del agente (preferencias, patrones de datos, heuristicas).

## 1. Leer Estado Actual

Leer `output/MEMORY.md`. Si no existe, crearlo con este template:

```markdown
# Memoria del Agente BI/BA

## Preferencias del Usuario

(Sin preferencias registradas)

## Patrones de Datos Conocidos

(Sin patrones registrados)

## Heuristicas Aprendidas

(Sin heuristicas registradas)
```

## 2. Determinar Origen y Detectar Actualizaciones

### 2.1 Si viene de /analyze (post-analisis)

Analizar la sesion completa para detectar:

**Preferencias del usuario** — Comparar las elecciones de este analisis con la sec "Preferencias del Usuario":
- Campos a rastrear: profundidad, formato(s), estilo, audiencia, dominio principal
- Si un campo no tenia valor previo → registrar el de esta sesion
- Si un campo ya tenia valor y coincide → no cambiar
- Si un campo ya tenia valor y difiere → actualizar solo si el usuario ha elegido el nuevo valor en 2+ analisis consecutivos (comparar con ANALYSIS_MEMORY.md para verificar)

**Patrones de datos** — Comparar hallazgos de calidad (EDA, validacion post-query, profiling) con sec "Patrones de Datos Conocidos":
- Agrupar por dominio (subseccion `### nombre_dominio`)
- Si el patron ya existe para ese dominio → incrementar contador `[observado N+1, YYYY-MM]`
- Si es nuevo → registrar con `[observado 1, YYYY-MM]`
- Tipos de patrones a capturar: nulos en columnas (>30%), filtros necesarios, rangos temporales incompletos, outliers sistematicos, registros a excluir

**Heuristicas aprendidas** — Hallazgos analiticos que trascienden un analisis individual:
- Solo registrar si confianza ALTA y aplica a multiples analisis o periodos
- Formato: `- [Hallazgo] [YYYY-MM, confianza]`
- Ejemplo: "Q4 muestra pico estacional >30% vs Q1-Q3 en ventas retail [2026-02, alta]"

### 2.2 Si viene del usuario directamente ($ARGUMENTS)

Parsear la peticion del usuario y escribir en la seccion correspondiente:
- Si menciona preferencia (formato, estilo, dominio, etc.) → sec Preferencias
- Si menciona patron de datos → sec Patrones (pedir dominio si no es obvio)
- Si es un hallazgo general → sec Heuristicas

## 3. Escribir Actualizaciones

- Editar `output/MEMORY.md` en la seccion correspondiente
- No duplicar entradas — actualizar contadores o valores existentes
- Mantener las secciones ordenadas: Preferencias primero, Patrones por dominio, Heuristicas cronologicas
- Si una seccion tenia el placeholder "(Sin ... registradas)", eliminarlo al anadir la primera entrada

## 4. Confirmar

Informar brevemente en chat (1-2 lineas) que se actualizo y que cambios se hicieron. Ejemplo:
> Memoria actualizada: preferencia de formato PDF+Web registrada, patron de nulos en `descuento` incrementado a [observado 3].
