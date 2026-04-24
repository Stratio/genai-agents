# governance-officer

Agente governance officer que combina la construcción de capas semánticas y la gestión de calidad del dato. Orquesta el ciclo de vida completo de los artefactos de gobierno: ontologías, vistas, mappings, términos, reglas de calidad e informes de cobertura.

## Capacidades

### Capa semántica
- Construcción y mantenimiento de capas semánticas vía MCPs de gobierno
- Publicación de business views (Draft → Pending Publish)
- Exploración de dominios técnicos y capas semánticas publicadas
- Planificación interactiva de ontologías con lectura de ficheros locales
- Creación de data collections a partir de busquedas en el diccionario de datos
- Gestión de business terms en el diccionario de gobierno

### Calidad del dato
- Evaluación de cobertura de calidad por dominio, colección, tabla o columna
- Identificación de gaps: dimensiones de calidad no cubiertas
- Propuesta razonada de reglas de calidad basada en contexto semántico y datos reales
- Creación de reglas de calidad con aprobación humana obligatoria
- Planificación de ejecución automática de reglas de calidad
- Generación de informes de cobertura (chat, PDF, DOCX, PPTX, Dashboard web, Póster/Infografía, XLSX, Markdown)

## Requisitos

- Python 3.10+ con las dependencias listadas en `requirements.txt`. En Stratio Cowork la imagen del sandbox las provee; en dev local, `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. Paquetes del sistema (poppler-utils, tesseract-ocr, ghostscript, qpdf, pdftk-java, libcairo2, libpango-1.0-0, libpangoft2-1.0-0) — ver la sección "System dependencies" del `README.md` del monorepo
- Acceso a dos servidores MCP de Stratio:
  - `gov` (gobierno): herramientas de capa semántica, dimensiones de calidad, creación de reglas
  - `sql` (exploración): descubrimiento, generación SQL, profiling, ejecución

La configuración MCP está en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer URL y credenciales de variables de entorno.

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `MCP_SQL_URL` | URL del servidor MCP SQL de Stratio |
| `MCP_SQL_API_KEY` | API key del servidor MCP SQL |
| `MCP_GOV_URL` | URL del servidor MCP de Gobierno de Stratio |
| `MCP_GOV_API_KEY` | API key del servidor MCP de Gobierno |

## Skills

| Skill | Comando | Descripción |
|-------|---------|-------------|
| Pipeline completo | `/build-semantic-layer` | Construir capa semántica completa: términos, ontología, vistas, mappings, términos semánticos |
| Términos técnicos | `/create-technical-terms` | Crear descripciones técnicas para tablas y columnas |
| Ontología | `/create-ontology` | Crear, extender o eliminar clases de ontología |
| Business views | `/create-business-views` | Crear, regenerar o eliminar business views |
| SQL mappings | `/create-sql-mappings` | Crear o actualizar SQL mappings para vistas |
| Términos semánticos | `/create-semantic-terms` | Generar términos semánticos de negocio |
| Business terms | `/manage-business-terms` | Crear business terms en el diccionario de gobierno |
| Data collection | `/create-data-collection` | Buscar y crear nuevos dominios técnicos |
| Evaluación de calidad | `/assess-quality` | Evaluar la cobertura de calidad por dominio o tabla |
| Creación de reglas | `/create-quality-rules` | Diseñar y crear reglas de calidad con aprobación humana |
| Planificación de calidad | `/create-quality-schedule` | Crear planificaciones de ejecución automática |
| Informe de calidad | `/quality-report` | Generar informe formal de cobertura (PDF, DOCX, PPTX, Dashboard web, Póster/Infografía, XLSX, Markdown, Chat) |
| Lectura de PDF | `/pdf-reader` | Extraer texto, tablas y datos de archivos PDF proporcionados por el usuario |
| Escritura de PDF | `/pdf-writer` | Crear PDFs personalizados, combinar/dividir, marca de agua, cifrar, rellenar formularios |
| Lectura de DOCX | `/docx-reader` | Extraer texto, tablas, imágenes y metadatos de ficheros `.docx` o `.doc` heredado (políticas, specs de ontología, documentos de negocio) |
| Escritura de DOCX | `/docx-writer` | DOCX de gobernanza (notas de política, documentación de ontología, informes de cumplimiento). Combinar/dividir, find-replace, convertir `.doc` a `.docx` |
| Lectura de XLSX | `/xlsx-reader` | Extraer valores de celda, tablas, fórmulas y metadatos de ficheros `.xlsx`/`.xlsm` (o `.xls`/`.xlsb` heredado vía LibreOffice) — diccionarios de datos, catálogos de términos, libros de rule-specs, matrices de compliance |
| Escritura de XLSX | `/xlsx-writer` | XLSX de gobernanza (exports de ontología, catálogos de términos, matrices de compliance, libros checklist de política). Libros multi-hoja de cobertura de calidad. Combinar/dividir, find-replace, conversión `.xls` legacy, refresco de fórmulas |

## Scripts de empaquetado

Todos los scripts aceptan `--lang <code>` para generar la salida en un idioma específico (ej. `--lang es` para español). Cuando se usa `--lang`, la salida va a `dist/<lang>/...` en lugar de `dist/...`.

### Scripts específicos (desde esta carpeta)

| Script | Plataforma destino | Salida | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<name>/` | `bash pack_claude_ai_project.sh --name governance-officer` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<name>/` | `bash pack_claude_cowork.sh --name governance-officer` |

El script de cowork también acepta `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>` y `--sql-key <KEY>` para configurar los dos servidores MCP. Si se omiten, permanecen como plantillas de variables de entorno para configurar posteriormente.

### Scripts genéricos (desde la raíz del monorepo)

| Script | Plataforma destino | Salida | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent governance-officer` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent governance-officer` |

## Inicio rápido

```bash
# 1. Configurar variables de entorno
export MCP_SQL_URL="https://my-sql-server.example.com/mcp"
export MCP_SQL_API_KEY="my-sql-api-key"
export MCP_GOV_URL="https://my-governance-server.example.com/mcp"
export MCP_GOV_API_KEY="my-governance-api-key"

# 2. Instalar dependencias (para generación de informes PDF/DOCX) — solo dev local
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 3. Empaquetar para la plataforma deseada
bash ../pack_opencode.sh --agent governance-officer
# o
bash ../pack_claude_code.sh --agent governance-officer
```
