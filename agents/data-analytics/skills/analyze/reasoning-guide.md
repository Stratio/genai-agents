# Reasoning Guide (Process Documentation)

Detailed guide for generating reasoning for each analysis. Reasoning documents the analyst's complete thought process: from the original question to the conclusions and suggestions.

## When to generate

| Depth | Reasoning | Format |
|-------|-----------|--------|
| Quick | Do not generate file. Include key notes in chat (see SKILL.md sec 7.1) | Chat only |
| Standard | Generate in `output/[ANALYSIS_DIR]/reasoning/reasoning.md` | .md only |
| Deep | Generate in `output/[ANALYSIS_DIR]/reasoning/reasoning.md` | .md only (full + detailed suggestions) |

**User override**: If the user explicitly requests reasoning in another format (PDF, DOCX, PPTX, HTML), generate the `.md` first and then route to the corresponding skill per the agent's format→skill contract (AGENTS.md §8): `pdf-writer` for PDF, `docx-writer` for DOCX, `pptx-writer` for deck, `web-craft` for standalone HTML. `brand-kit` does NOT apply to reasoning — internal documentation.

## Mandatory content

The reasoning must include all of the following sections:

1. **User's original question** — Verbatim transcription of the request
2. **Hypotheses formulated and validation results** — Mandatory summary table:
   ```
   | ID | Hypothesis | Result | Expected | Actual | So What |
   ```
3. **Domain and tables used** — Exact domain name and list of tables queried
4. **Data quality summary** — Both signals from Phase 1.1: Data Profiling Score (HIGH/MEDIUM/LOW with %) AND Governance Quality Status (rule counts OK/KO/WARNING, with any KO rule affecting analysed columns called out explicitly)
5. **Decisions made and justification** — Methodological choices, applied filters, exclusions
6. **Questions asked to the MCP and summary of data obtained** — Each query with result description
7. **Analyses performed and key findings** — Techniques applied and main insights
8. **Clustering or feature importance** (if applicable) — Approach, variables, results, limitations
9. **Limitations identified** — In the data or in the analysis
10. **Suggestions for future analyses** — Questions that remained open or lines of investigation
11. **Paths of all generated files** — Complete listing of deliverables, scripts, data, and assets

## Differences by depth

### Standard
- Full content (all sections above)
- Suggestions for future analyses: brief, 2-3 lines of investigation

### Deep
- Full content (all sections above)
- Detailed follow-up analysis suggestions: for each suggestion include business question, initial hypothesis, required data, and recommended analytical technique
- If advanced techniques were used (statistical tests, Monte Carlo, root cause analysis): document parameters, assumptions, and sensitivity of the results
