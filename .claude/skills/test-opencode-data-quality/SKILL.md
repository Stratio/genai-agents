---
name: test-opencode-data-quality
description: Empaqueta el agente data-quality para OpenCode en español y despliega el resultado en la carpeta de tests de OpenCode (~/genai-agents-tests/opencode/data-quality), sobreescribiendo solo los ficheros del paquete sin borrar contenido extra (p. ej. carpeta output/). Usar cuando el usuario diga que quiere "testear", "probar" o "desplegar para test" el agente data-quality en OpenCode, o invoque /test-opencode-data-quality.
---

# test-opencode-data-quality

Empaqueta `data-quality` para OpenCode (español) y despliega el output sobre la carpeta de tests de OpenCode, preservando contenido extra que pueda haber en destino.

## Cuándo usar esta skill

- El usuario dice variantes de: "quiero testear el data-quality en opencode", "prueba data-quality en opencode", "despliega data-quality para test", "regenera el data-quality de tests".
- El usuario invoca `/test-opencode-data-quality`.

## Pasos

Ejecuta esta secuencia en una sola llamada Bash:

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
bash pack_opencode.sh --agent data-quality --lang es
mkdir -p ~/genai-agents-tests/opencode/data-quality
rsync -a data-quality/dist/es/opencode/data-quality/ ~/genai-agents-tests/opencode/data-quality/
echo "OK: data-quality opencode-es desplegado en ~/genai-agents-tests/opencode/data-quality"
```

Notas:
- `git rev-parse --show-toplevel` resuelve la raíz del repo, así funciona aunque el clon esté en otra ruta para otros compañeros.
- `rsync -a` (sin `--delete`) sobreescribe/añade los ficheros del paquete pero **no borra** lo que ya hubiera en destino (p. ej. una carpeta `output/` con artefactos previos).
- `mkdir -p` por si es la primera ejecución y el destino aún no existe.

## Confirmación

Tras ejecutar, confirma al usuario en una sola frase qué se desplegó y dónde.
