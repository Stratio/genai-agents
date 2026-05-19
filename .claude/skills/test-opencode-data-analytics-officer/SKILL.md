---
name: test-opencode-data-analytics-officer
description: Empaqueta el agente data-analytics-officer para OpenCode en español y despliega el resultado en la carpeta de tests de OpenCode (~/genai-agents-tests/opencode/data-analytics-officer), sobreescribiendo solo los ficheros del paquete sin borrar contenido extra (p. ej. carpeta output/). Usar cuando el usuario diga que quiere "testear", "probar" o "desplegar para test" el agente data-analytics-officer en OpenCode, o invoque /test-opencode-data-analytics-officer.
---

# test-opencode-data-analytics-officer

Empaqueta `data-analytics-officer` para OpenCode (español) y despliega el output sobre la carpeta de tests de OpenCode, preservando contenido extra que pueda haber en destino.

## Cuándo usar esta skill

- El usuario dice variantes de: "quiero testear el data-analytics-officer en opencode", "prueba data-analytics-officer en opencode", "despliega data-analytics-officer para test", "regenera el data-analytics-officer de tests".
- El usuario invoca `/test-opencode-data-analytics-officer`.

## Pasos

Ejecuta esta secuencia en una sola llamada Bash:

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
bash pack_opencode.sh --agent data-analytics-officer --lang es
mkdir -p ~/genai-agents-tests/opencode/data-analytics-officer
rsync -a agents/data-analytics-officer/dist/es/opencode/data-analytics-officer/ ~/genai-agents-tests/opencode/data-analytics-officer/
echo "OK: data-analytics-officer opencode-es desplegado en ~/genai-agents-tests/opencode/data-analytics-officer"
```

Notas:
- `git rev-parse --show-toplevel` resuelve la raíz del repo, así funciona aunque el clon esté en otra ruta para otros compañeros.
- `rsync -a` (sin `--delete`) sobreescribe/añade los ficheros del paquete pero **no borra** lo que ya hubiera en destino (p. ej. una carpeta `output/` con artefactos previos).
- `mkdir -p` por si es la primera ejecución y el destino aún no existe.

## Confirmación

Tras ejecutar, confirma al usuario en una sola frase qué se desplegó y dónde.
