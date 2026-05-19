# data-governance-officer

Agente governance officer que combina la construcción de capas semánticas y la gestión de calidad del dato. Orquesta el ciclo de vida completo de los artefactos de gobierno: ontologías, vistas, mappings, términos, reglas de calidad e informes de cobertura.

## Capacidades

### Capa semántica
- Construcción y mantenimiento de capas semánticas vía MCPs de gobierno
- Publicación de business views (Draft → Pending Publish)
- Exploración de dominios técnicos y capas semánticas publicadas
- Validación con datos de muestra de la SQL del mapping antes de publicar, y sanity-checks del `semantic_<domain>` publicado
- Planificación interactiva de ontologías con lectura de ficheros locales
- Creación de data collections a partir de busquedas en el diccionario de datos
- Gestión de business terms en el diccionario de gobierno

### Calidad del dato
- Evaluación de cobertura de calidad por dominio, colección, tabla o columna
- Identificación de gaps: dimensiones de calidad no cubiertas
- Propuesta razonada de reglas de calidad basada en contexto semántico y datos reales
- Creación de reglas de calidad con aprobación humana obligatoria
- Planificación de ejecución automática de reglas de calidad
- Consulta y definición de Critical Data Elements (CDEs): identificar los activos más críticos de un dominio, recomendarlos y etiquetarlos con aprobación humana obligatoria
- Generación de informes de cobertura (chat, PDF, DOCX, PPTX, Dashboard web, Informe web / Artículo web, Póster/Infografía, XLSX, Markdown)

## Requisitos

- Python 3.10+ con las dependencias listadas en `requirements.txt`. En Stratio Cowork la imagen del sandbox las provee; en dev local, `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. Paquetes del sistema (poppler-utils, tesseract-ocr, ghostscript, qpdf, pdftk-java, libcairo2, libpango-1.0-0, libpangoft2-1.0-0) — ver la sección "System dependencies" del `README.md` del monorepo
- Acceso a dos servidores MCP de Stratio:
  - `gov` (gobierno): herramientas de capa semántica, dimensiones de calidad, creación de reglas
  - `sql` (exploración): descubrimiento, generación SQL, profiling, ejecución

La configuración MCP está en `opencode.json` (OpenCode), preconfigurado para leer URL y credenciales de variables de entorno. El fichero `mcps` en la raíz del agente lista los nombres de MCP que se registran al desplegar el bundle `agents/v1` en Stratio Cowork.

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
| Informe de calidad | `/quality-report` | Generar informe formal de cobertura (PDF, DOCX, PPTX, Dashboard web, Informe web / Artículo web, Póster/Infografía, XLSX, Markdown, Chat) |
| Critical Data Elements | `/manage-critical-data-elements` | Consultar o definir Critical Data Elements (CDEs) para un dominio gobernado, con aprobación humana obligatoria antes de etiquetar |
| Lectura de PDF | `/pdf-reader` | Extraer texto, tablas y datos de archivos PDF proporcionados por el usuario |
| Escritura de PDF | `/pdf-writer` | Crear PDFs personalizados, combinar/dividir, marca de agua, cifrar, rellenar formularios |
| Lectura de DOCX | `/docx-reader` | Extraer texto, tablas, imágenes y metadatos de ficheros `.docx` o `.doc` heredado (políticas, specs de ontología, documentos de negocio) |
| Escritura de DOCX | `/docx-writer` | DOCX de gobernanza (notas de política, documentación de ontología, informes de cumplimiento). Combinar/dividir, find-replace, convertir `.doc` a `.docx` |
| Lectura de XLSX | `/xlsx-reader` | Extraer valores de celda, tablas, fórmulas y metadatos de ficheros `.xlsx`/`.xlsm` (o `.xls`/`.xlsb` heredado vía LibreOffice) — diccionarios de datos, catálogos de términos, libros de rule-specs, matrices de compliance |
| Escritura de XLSX | `/xlsx-writer` | XLSX de gobernanza (exports de ontología, catálogos de términos, matrices de compliance, libros checklist de política). Libros multi-hoja de cobertura de calidad. Combinar/dividir, find-replace, conversión `.xls` legacy, refresco de fórmulas |

## Scripts de empaquetado

Todos los scripts aceptan `--lang <code>` para generar la salida en un idioma específico (ej. `--lang es` para español). Cuando se usa `--lang`, la salida va a `dist/<lang>/...` en lugar de `dist/...`.

| Script | Destino | Salida | Ejemplo |
|--------|---------|--------|---------|
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent data-governance-officer` |
| `pack_stratio_cowork.sh` | Stratio Cowork (`agents/v1`) | `dist/<name>-stratio-cowork.zip` | `bash ../pack_stratio_cowork.sh --agent data-governance-officer` |

## Inicio rápido

```bash
# 1. Configurar variables de entorno
export MCP_SQL_URL="https://my-sql-server.example.com/mcp"
export MCP_SQL_API_KEY="my-sql-api-key"
export MCP_GOV_URL="https://my-governance-server.example.com/mcp"
export MCP_GOV_API_KEY="my-governance-api-key"

# 2. Instalar dependencias (para generación de informes PDF/DOCX) — solo dev local
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 3. Empaquetar para OpenCode
bash ../pack_opencode.sh --agent data-governance-officer

# 4. Empaquetar para Stratio Cowork
bash ../pack_stratio_cowork.sh --agent data-governance-officer
```
