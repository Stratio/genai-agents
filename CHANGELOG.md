# Changelog

## 0.1.0 (upcoming)

* Initial version: monorepo with data-analytics and data-analytics-light agents
* Unify packaging artifacts under dist/, add CLI args to pack scripts, make MCP config optional in plugin scripts, add CI/CD scaffolding (Jenkinsfile, Makefile, bin/)
* Document build output structure in README, update pack script output paths in table
* Add skills normalization (flat .md → canonical format), output-templates support, sources zip generation and improve agent docs
* Remove interactive prompts from data-analytics-light pack scripts to make them fully CI/CD-friendly
