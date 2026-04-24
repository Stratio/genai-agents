# Changelog

## 0.1.0 (upcoming)

First release of the `genai-agents` monorepo: seven agents, the shared-skills system, multi-platform packaging and internationalization.

* **Agents**: `data-analytics` (full BI/BA with multi-format report generation), `data-analytics-light` (chat-oriented variant for Claude AI Projects and Claude Cowork), `semantic-layer` (building and maintaining semantic layers in Stratio Governance), `data-quality` (coverage assessment and quality-rule generation), `governance-officer` (combined semantic-layer + data-quality), `skill-creator` (interactive skill design) and `agent-creator` (interactive agent design).
* **Data and governance shared skills**: `propose-knowledge`, `explore-data`, `stratio-data`, `stratio-semantic-layer`, `create-technical-terms`, `create-ontology`, `create-business-views`, `create-sql-mappings`, `create-semantic-terms`, `manage-business-terms`, `create-data-collection`, `build-semantic-layer`, `assess-quality`, `create-quality-rules`, `create-quality-schedule` and `quality-report`.
* **Visual-craftsmanship family**: deliverable skills (`pdf-writer`, `docx-writer`, `pptx-writer`, `xlsx-writer`, `web-craft`, `canvas-craft`) and their companion readers (`pdf-reader`, `docx-reader`, `pptx-reader`, `xlsx-reader`), all following the guidance-first pattern and delegating visual identity tokens to the centralized `brand-kit` skill (ten curated themes, extensible by clients).
* **Stratio integration**: `stratio_data` and `stratio_gov` MCPs, long-running-task polling protocol, OpenSearch fallback for searches, and shared guides (`stratio-data-tools.md`, `stratio-semantic-layer-tools.md`, `quality-exploration.md`, `visual-craftsmanship.md`).
* **Multi-platform packaging**: generic root scripts (`pack_claude_code.sh`, `pack_opencode.sh`, `pack_shared_skills.sh`) and agent-specific scripts (`pack_claude_ai_project.sh`, `pack_claude_cowork.sh`), orchestrated by `bin/package.sh` and `make package`.
* **Internationalization**: English as the primary language with a full `es/` overlay (AGENTS.md, SKILL.md, guides, READMEs, templates); `bin/check-translations.sh` verifies parity and all pack scripts accept `--lang <code>`.
* **Runtime and CI/CD**: sandbox-provided venv (`/opt/venv` on Stratio Cowork, local `.venv` in dev), per-agent `requirements.txt` with the analytical stack (pandas, scipy, scikit-learn, matplotlib, seaborn, plotly) and deliverable-generation stack (reportlab, pypdf, python-docx, python-pptx, openpyxl, markdown). Jenkins pipeline (`Jenkinsfile`, `Makefile` and `bin/` utilities).
