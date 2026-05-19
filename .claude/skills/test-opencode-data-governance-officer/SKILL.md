---
name: test-opencode-data-governance-officer
description: Empaqueta el agente data-governance-officer para OpenCode en español y despliega el resultado en la carpeta de tests de OpenCode (~/genai-agents-tests/opencode/data-governance-officer), sobreescribiendo solo los ficheros del paquete sin borrar contenido extra (p. ej. carpeta output/). Usar cuando el usuario diga que quiere "testear", "probar" o "desplegar para test" el agente data-governance-officer en OpenCode, o invoque /test-opencode-data-governance-officer.
---

# test-opencode-data-governance-officer

Empaqueta `data-governance-officer` para OpenCode (español) y despliega el output sobre la carpeta de tests de OpenCode, preservando contenido extra que pueda haber en destino.

## Cuándo usar esta skill

- El usuario dice variantes de: "quiero testear el data-governance-officer en opencode", "prueba data-governance-officer en opencode", "despliega data-governance-officer para test", "regenera el data-governance-officer de tests".
- El usuario invoca `/test-opencode-data-governance-officer`.

## Pasos

Ejecuta esta secuencia en una sola llamada Bash:

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
bash pack_opencode.sh --agent data-governance-officer --lang es
mkdir -p ~/genai-agents-tests/opencode/data-governance-officer
rsync -a agents/data-governance-officer/dist/es/opencode/data-governance-officer/ ~/genai-agents-tests/opencode/data-governance-officer/
echo "OK: data-governance-officer opencode-es desplegado en ~/genai-agents-tests/opencode/data-governance-officer"
```

Notas:
- `git rev-parse --show-toplevel` resuelve la raíz del repo, así funciona aunque el clon esté en otra ruta para otros compañeros.
- `rsync -a` (sin `--delete`) sobreescribe/añade los ficheros del paquete pero **no borra** lo que ya hubiera en destino (p. ej. una carpeta `output/` con artefactos previos).
- `mkdir -p` por si es la primera ejecución y el destino aún no existe.

## Confirmación

Tras ejecutar, confirma al usuario en una sola frase qué se desplegó y dónde.
