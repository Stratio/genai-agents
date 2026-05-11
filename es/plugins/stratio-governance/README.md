# Plugin Stratio Governance

Plugin funcional que agrupa los agentes de gobierno del dato del monorepo en una unidad desplegable para Stratio Cowork.

## Qué incluye

| Agente | Rol |
|---|---|
| [governance-officer](../../agents/governance-officer/) | Gobierno integral: construye y mantiene capas semánticas Y gestiona calidad del dato, además de reporting en PDF/DOCX/PPTX/XLSX/web/poster/markdown. |
| [data-quality](../../agents/data-quality/) | Evaluación de calidad, creación de reglas con aprobación humana obligatoria, scheduling y reportes de cobertura en múltiples formatos. |
| [semantic-layer](../../agents/semantic-layer/) | Construcción de la capa semántica: colecciones de datos, términos técnicos, ontologías, vistas de negocio, mappings SQL y publicación de términos. |

## Plataformas soportadas

| Plataforma | Soportada | Razón |
|---|---|---|
| Stratio Cowork | sí | Los plugins con agentes se despliegan como bundles `agents/v1`. |
| Claude (claude-plugin) | no | Claude no soporta agentes en plugins; solo los plugins skills-only se empaquetan para Claude. |

## Instalación

El plugin produce `dist/stratio-governance-stratio-cowork-{version}.zip`. Para desplegarlo en un tenant de Stratio Cowork, usa la task `upload-plugin` de la skill compartida [`cowork-api`](../../skills/cowork-api/) — abre el bundle y reparte cada sub-ZIP al endpoint correspondiente de `genai-api`.

## Estructura del bundle generado

```
stratio-governance-stratio-cowork-{version}.zip
├── plugin.yaml                                  # manifest agregado
├── README.md                                    # este fichero
└── agents/
    ├── governance-officer-stratio-cowork.zip    # sub-bundle agents/v1
    ├── data-quality-stratio-cowork.zip          # sub-bundle agents/v1
    └── semantic-layer-stratio-cowork.zip        # sub-bundle agents/v1
```

Cada sub-ZIP es un contenedor `agents/v1` autocontenido; si prefieres, puedes extraer el envoltorio y subir cada sub-ZIP por separado con la task `upload-agent`.
