---
name: test-opencode-data-analytics
description: Empaqueta el agente data-analytics para OpenCode en español y despliega el resultado en la carpeta de tests de OpenCode (~/genai-agents-tests/opencode/data-analytics), sobreescribiendo solo los ficheros del paquete sin borrar contenido extra (p. ej. carpeta output/). Usar cuando el usuario diga que quiere "testear", "probar" o "desplegar para test" el agente data-analytics en OpenCode, o invoque /test-opencode-data-analytics.
---

# test-opencode-data-analytics

Empaqueta `data-analytics` para OpenCode (español) y despliega el output sobre la carpeta de tests de OpenCode, preservando contenido extra que pueda haber en destino.

## Cuándo usar esta skill

- El usuario dice variantes de: "quiero testear el data-analytics en opencode", "prueba data-analytics en opencode", "despliega data-analytics para test", "regenera el data-analytics de tests".
- El usuario invoca `/test-opencode-data-analytics`.

## Pasos

Ejecuta esta secuencia en una sola llamada Bash:

```bash
set -e
cd "$(git rev-parse --show-toplevel)"
bash pack_opencode.sh --agent data-analytics --lang es
mkdir -p ~/genai-agents-tests/opencode/data-analytics
rsync -a data-analytics/dist/es/opencode/data-analytics/ ~/genai-agents-tests/opencode/data-analytics/
echo "OK: data-analytics opencode-es desplegado en ~/genai-agents-tests/opencode/data-analytics"
```

Notas:
- `git rev-parse --show-toplevel` resuelve la raíz del repo, así funciona aunque el clon esté en otra ruta para otros compañeros.
- `rsync -a` (sin `--delete`) sobreescribe/añade los ficheros del paquete pero **no borra** lo que ya hubiera en destino (p. ej. una carpeta `output/` con artefactos previos).
- `mkdir -p` por si es la primera ejecución y el destino aún no existe.

## Confirmación

Tras ejecutar, confirma al usuario en una sola frase qué se desplegó y dónde.
