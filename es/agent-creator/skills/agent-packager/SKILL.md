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
# Crear un directorio de staging limpio
AGENT_NAME="{nombre}"
STAGING=$(mktemp -d)

# Copiar ficheros del agente al staging
cp output/$AGENT_NAME/AGENTS.md "$STAGING/"
cp output/$AGENT_NAME/README.md "$STAGING/"
cp output/$AGENT_NAME/opencode.json "$STAGING/"

# Copiar skills internas (si existen)
if [ -d "output/$AGENT_NAME/.opencode" ]; then
  cp -r "output/$AGENT_NAME/.opencode" "$STAGING/"
fi

# Copiar ficheros adicionales del agente (scripts, templates, etc.)
for item in output/$AGENT_NAME/scripts output/$AGENT_NAME/templates; do
  [ -d "$item" ] && cp -r "$item" "$STAGING/"
done

# Crear el agent ZIP
(cd "$STAGING" && zip -r "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip" .)

# Limpiar
rm -rf "$STAGING"
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
BUNDLE_DIR=$(mktemp -d)

# Copiar componentes al staging del bundle
cp "output/$AGENT_NAME/metadata.yaml" "$BUNDLE_DIR/"
cp "output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip" "$BUNDLE_DIR/"

# Incluir shared skills ZIP solo si existe
if [ -f "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" ]; then
  cp "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" "$BUNDLE_DIR/"
fi

# Crear el ZIP contenedor
(cd "$BUNDLE_DIR" && zip -r "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.zip" .)

# Limpiar
rm -rf "$BUNDLE_DIR"
```

**Fallback**: Si `zip` no está disponible, usar `tar`:

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

Después de empaquetar exitosamente, reportar:

1. **Ruta del fichero**: ruta completa al ZIP contenedor
2. **Tamaño del fichero**: tamaño legible
3. **Contenido del bundle**: listar los ficheros dentro del ZIP contenedor
4. **Próximos pasos**:
   - Subir el ZIP a la interfaz de gestión de agentes de Stratio Cowork
   - Configurar servidores MCP desde la interfaz web (si el agente necesita herramientas externas)
   - Probar el agente con los escenarios de uso definidos durante el diseño
