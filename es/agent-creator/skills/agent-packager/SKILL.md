---
name: agent-packager
description: "Empaquetar un agente como bundle ZIP agents/v1 de Stratio Cowork. Usar cuando los ficheros del agente están listos y necesitan ensamblarse en un ZIP desplegable con metadatos."
argument-hint: "[nombre-del-agente]"
---

# Skill: Empaquetador de Agentes para Stratio Cowork

Instrucciones paso a paso para empaquetar un agente en el formato de bundle `agents/v1` de Stratio Cowork.

## 1. Estructura del Bundle

Un bundle de Stratio Cowork es un fichero ZIP que contiene:

```
{nombre}-stratio-cowork.zip            # ZIP contenedor
  metadata.yaml                        # Manifiesto del bundle (agents/v1)
  {nombre}-opencode-agent.zip          # Ficheros del agente (sin shared skills)
  {nombre}-shared-skills.zip           # Shared skills (opcional, solo si hay nuevas)
```

## 2. Generar el Agent ZIP

El agent ZIP contiene todos los ficheros necesarios para ejecutar el agente.

### Convención del directorio de staging

Todo el staging durante el empaquetado ocurre bajo `output/<nombre-agente>/.pack-staging/` (oculto, dentro del workdir). **No usar `/tmp/` ni `mktemp -d`** — en algunos entornos de ejecución (p. ej. el sandbox de Stratio) esas rutas no son escribibles, y la improvisación silenciosa filtra directorios de staging dentro del bundle final. La limpieza de `.pack-staging/` ocurre **una sola vez, al final de la sección 5**, después de construir el ZIP contenedor.

### Ficheros a incluir

| Fichero/Directorio | Obligatorio | Notas |
|-------------------|-------------|-------|
| `AGENTS.md` | Sí | Instrucciones del agente — debe estar en la raíz del ZIP |
| `README.md` | Sí | Documentación para el usuario |
| `opencode.json` | Sí | Configuración de plataforma con permisos |
| `.opencode/skills/` | Si hay skills | Skills internas: `.opencode/skills/{nombre}/SKILL.md` |
| `scripts/` | Opcional | Scripts auxiliares usados por el agente |
| `templates/` | Opcional | Plantillas de salida usadas por el agente |
| Otros ficheros | Opcional | Cualquier fichero adicional que el agente necesite |

### Ficheros a NO incluir

- `cowork-metadata.yaml` — la descripción va directamente en `metadata.yaml`
- Manifiesto `shared-skills` — las referencias de shared skills van en `metadata.yaml`
- Directorio `_shared-skills/` — estos van en el shared-skills ZIP separado
- Ficheros temporales, artefactos de build, `dist/`, `.git/`

### Comandos

```bash
# El staging vive bajo el workdir del agente (oculto, dentro del workdir)
AGENT_NAME="{nombre}"
STAGING="output/$AGENT_NAME/.pack-staging/agent"
mkdir -p "$STAGING"

# Copiar ficheros del agente al staging
cp "output/$AGENT_NAME/AGENTS.md"     "$STAGING/"
cp "output/$AGENT_NAME/README.md"     "$STAGING/"
cp "output/$AGENT_NAME/opencode.json" "$STAGING/"

# Copiar skills internas (si existen)
if [ -d "output/$AGENT_NAME/.opencode" ]; then
  cp -r "output/$AGENT_NAME/.opencode" "$STAGING/"
fi

# Copiar ficheros adicionales del agente (scripts, templates, etc.)
for item in "output/$AGENT_NAME/scripts" "output/$AGENT_NAME/templates"; do
  [ -d "$item" ] && cp -r "$item" "$STAGING/"
done

# Crear el agent ZIP (el destino vive fuera del directorio de staging)
(cd "$STAGING" && zip -rq "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip" .)

# IMPORTANTE: NO borrar .pack-staging aquí. La sección 5 se encarga del cleanup
# después de construir el ZIP contenedor, así el staging del bundle puede reutilizar
# el mismo directorio padre sin race condition.
```

## 3. Generar el Shared Skills ZIP

Crear esto solo si el agente tiene shared skills **nuevas** (creadas durante el flujo de trabajo). Las skills que ya existen en la plataforma NO se incluyen — se cargan en runtime.

### Estructura

```
{nombre-skill-1}/
  SKILL.md
  [fichero-soporte-1.md]
  [fichero-soporte-2.md]
{nombre-skill-2}/
  SKILL.md
```

Cada skill es un directorio con el nombre de la skill, que contiene al menos un `SKILL.md`.

### Sustituciones de rutas

Si algún SKILL.md referencia `skills-guides/nombre.md`, y el fichero de guía está incrustado junto al SKILL.md, reemplazar la ruta por solo `nombre.md` (eliminar el prefijo `skills-guides/`).

### Comandos

```bash
AGENT_NAME="{nombre}"
SHARED_DIR="output/$AGENT_NAME/_shared-skills"

if [ -d "$SHARED_DIR" ] && [ "$(ls -A "$SHARED_DIR")" ]; then
  (cd "$SHARED_DIR" && zip -r "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" .)
fi
```

## 4. Generar metadata.yaml

El manifiesto describe el contenido del bundle.

### Campos obligatorios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `format_version` | string | Siempre `"agents/v1"` |
| `name` | string | Nombre del agente en kebab-case (ej: `"mi-agente"`) |
| `agent_zip` | string | Nombre del fichero del agent ZIP (ej: `"mi-agente-opencode-agent.zip"`) |
| `description` | string | Descripción en una frase de qué hace el agente |

### Campos opcionales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `skills_zip` | string | Nombre del fichero del shared skills ZIP (solo si existe) |
| `external_version` | string | Versión semántica (ej: `"1.0.0"`) |

### Ejemplo

```yaml
format_version: "agents/v1"
name: "mi-agente"
agent_zip: "mi-agente-opencode-agent.zip"
skills_zip: "mi-agente-shared-skills.zip"
description: "Agente experto en analizar cobertura de calidad de datos y crear reglas de calidad."
```

Sin shared skills:

```yaml
format_version: "agents/v1"
name: "mi-agente"
agent_zip: "mi-agente-opencode-agent.zip"
description: "Agente experto en analizar cobertura de calidad de datos y crear reglas de calidad."
```

### Comandos

```bash
AGENT_NAME="{nombre}"
DESCRIPTION="{descripción del agente}"
METADATA="output/$AGENT_NAME/metadata.yaml"

cat > "$METADATA" <<EOF
format_version: "agents/v1"
name: "$AGENT_NAME"
agent_zip: "${AGENT_NAME}-opencode-agent.zip"
EOF

# Añadir skills_zip solo si hay shared skills
if [ -f "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" ]; then
  echo "skills_zip: \"${AGENT_NAME}-shared-skills.zip\"" >> "$METADATA"
fi

echo "description: \"$DESCRIPTION\"" >> "$METADATA"
```

## 5. Crear el ZIP Contenedor

Ensamblar el bundle final:

```bash
AGENT_NAME="{nombre}"
BUNDLE_DIR="output/$AGENT_NAME/.pack-staging/bundle"
mkdir -p "$BUNDLE_DIR"

# Copiar componentes al staging del bundle
cp "output/$AGENT_NAME/metadata.yaml"                       "$BUNDLE_DIR/"
cp "output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip"    "$BUNDLE_DIR/"

# Incluir shared skills ZIP solo si existe
if [ -f "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" ]; then
  cp "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" "$BUNDLE_DIR/"
fi

# Crear el ZIP contenedor (el destino vive fuera del directorio de staging)
(cd "$BUNDLE_DIR" && zip -rq "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.zip" .)

# Limpieza de TODO el staging del empaquetado en una sola pasada (cubre sección 2 y 5)
rm -rf "output/$AGENT_NAME/.pack-staging"
```

**Fallback**: Si `zip` no está disponible, usar `tar` (ejecutar antes del cleanup anterior para que `$BUNDLE_DIR` siga existiendo):

```bash
(cd "$BUNDLE_DIR" && tar -czf "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.tar.gz" .)
```

### Verificación de integridad

Después de crear el ZIP contenedor, verificar:

1. `metadata.yaml` existe en el ZIP contenedor
2. `metadata.yaml` contiene `format_version: "agents/v1"`
3. El agent ZIP referenciado por `agent_zip` existe en el contenedor
4. El agent ZIP contiene `AGENTS.md` en la raíz
5. Si `skills_zip` está declarado, el shared skills ZIP existe en el contenedor
6. Si el shared skills ZIP existe, cada skill tiene un `SKILL.md`

```bash
AGENT_NAME="{nombre}"
BUNDLE="output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.zip"

# Listar contenidos
echo "Contenido del bundle:"
unzip -l "$BUNDLE"

# Verificar metadata
unzip -p "$BUNDLE" metadata.yaml

# Verificar AGENTS.md en el agent ZIP
unzip -p "$BUNDLE" "${AGENT_NAME}-opencode-agent.zip" | funzip | unzip -l /dev/stdin 2>/dev/null | grep AGENTS.md
```

## 6. Entregar al Usuario

### Verificación previa a la entrega

Antes de reportar al usuario, asegurarse de que `output/<nombre-agente>/` está en un estado limpio.

**Debe haber** (lista abierta — el contenido exacto depende totalmente del diseño del agente):

- Los ficheros y directorios fuente del agente generados durante el flujo. Como mínimo: `AGENTS.md`, `README.md`, `opencode.json`. Más allá de eso, **cualquier cosa** que el diseño defina — `.opencode/`, `scripts/`, `templates/`, directorios de datos internos, librerías de prompts, documentación adicional, subcarpetas personalizadas, etc. No hay lista fija: cualquier fichero o carpeta que el agente necesite legítimamente es válido.
- `metadata.yaml`
- `<nombre>-opencode-agent.zip`
- `<nombre>-stratio-cowork.zip`
- Opcional: `<nombre>-shared-skills.zip` (solo si se crearon nuevas shared skills)

**NO debe haber** (lista cerrada — son artefactos prohibidos):

- `.pack-staging/` — staging del empaquetado de las secciones 2 y 5. La limpieza al final de la sección 5 debería haberlo eliminado; si sigue presente, la limpieza no se ejecutó.
- `_pack_tmp/` — nombre de staging heredado de improvisaciones anteriores. El flujo actual no debería crearlo nunca, pero límpialo defensivamente si aparece.
- Ficheros parciales o temporales dejados por ejecuciones fallidas (p. ej. ZIPs a medio construir, sufijos `.tmp`).

Si hay cualquier artefacto prohibido, eliminarlo antes de reportar. El directorio debe quedar lo bastante limpio como para que el usuario — o el mecanismo de exportación del sandbox — pueda identificar el entregable sin ambigüedad.

```bash
AGENT_NAME="{nombre}"
ls -la "output/$AGENT_NAME/"
[ -d "output/$AGENT_NAME/.pack-staging" ] && rm -rf "output/$AGENT_NAME/.pack-staging"
[ -d "output/$AGENT_NAME/_pack_tmp" ]     && rm -rf "output/$AGENT_NAME/_pack_tmp"
```

### Reporte

Después de empaquetar exitosamente, reportar:

1. **Ruta del fichero**: ruta completa al ZIP contenedor
2. **Tamaño del fichero**: tamaño legible
3. **Contenido del bundle**: listar los ficheros dentro del ZIP contenedor
4. **Próximos pasos**:
   - Proceder a la sección 7 (despliegue en Stratio Cowork) — es el siguiente paso del flujo.
   - Como referencia: el artefacto identificado como unidad desplegable es `<nombre>-stratio-cowork.zip` (el ZIP contenedor). Si en algún momento se necesita una subida manual, ese es el fichero a usar — NO el agent ZIP, ni el shared-skills ZIP, ni la carpeta de trabajo.
   - Tras el despliegue, configurar servidores MCP desde la interfaz web (si el agente necesita herramientas externas).
   - Probar el agente con los escenarios de uso definidos durante el diseño.

## 7. Desplegar el bundle a Stratio Cowork

Este es un **paso obligatorio** del flujo de empaquetado, no una opción. Cargar la skill `/cowork-api` y ejecutar `tasks/upload-agent.md` de principio a fin. Ese sub-fichero se encarga de: el pre-check (vía `skills-guides/external-api-calls.md` §2), la pregunta al usuario sobre `on_conflict`, la invocación de curl contra `/v1/agents/bundle/import` y cómo mostrar el código HTTP y la respuesta JSON.

La ruta del ZIP a pasar es `output/<agent-name>/<agent-name>-stratio-cowork.zip` (el ZIP contenedor producido en la sección 5).

El `metadata.yaml` generado en la sección 4 ya incluye `name`, así que la API lo lee del bundle — `cowork-api` no necesita preguntarlo ni pasarlo.

El pre-check dentro de `cowork-api` es un **health check del entorno** (variables de entorno, certificados), no un detector de sandbox. El agente anfitrión siempre se ejecuta dentro del sandbox de Stratio; si el pre-check reporta prerequisites faltantes (p. ej. `GENAI_API_URL`, `USER_CERT_PATH`, `USER_KEY_PATH`, `CA_CERT_PATH`), trasládale las piezas que faltan al usuario como un incidente del entorno — NO silencies el fallo y NO rechaces con un genérico "no puedo". El bundle ya está empaquetado correctamente; solo el paso de despliegue no se completó, y el usuario puede decidir cómo proceder.
