# propose-knowledge

Analyses an analysis conversation and **proposes** discovered business knowledge to the Stratio Governance semantic layer of a domain. Proposals are reviewed by an administrator in the Governance console before integration — the skill does not write definitive entries by itself.

## What it does

- Resolves the target domain from `$ARGUMENTS`, the conversation context (previous MCP calls), or by asking the user.
- Reads `output/MEMORY.md` (when present) and surfaces mature data patterns (observed 3+ times) as candidates.
- Classifies findings into three proposal types:
  - **`business_concept`** — term definitions, segmentations, metrics, thresholds;
  - **`sql_preference`** — domain-specific SQL patterns (JOINs, filters) discovered during the analysis;
  - **`chart_preference`** — visualisation preferences **tied to domain metrics**.
- Applies strict filters: rejects workflow/session/format preferences (output formats, visual style, audience, analysis depth) — those belong to Phase 2 of the analysis flow, not to domain knowledge.
- Verifies non-duplication with `get_tables_details` and `search_domain_knowledge` before proposing.
- Caps at **5 proposals per execution** (exceptionally 6), prioritised P1 → P2 → P3 with per-priority limits.
- Presents proposals to the user for approval (send all / select / modify / cancel) before calling `propose_knowledge`.

## When to use it

- After an analysis session in which new definitions, metrics or SQL/visual patterns emerged.
- When `output/MEMORY.md` has accumulated mature patterns worth formalising in Governance.
- When the user says "save this as a business term", "record that X means Y", or "add this to governance".
- For explicit, one-shot authoring of a business term with known relationships, prefer `manage-business-terms`.

## Dependencies

### Other skills
- **Typical predecessors:** `explore-data`, any analysis flow, or `assess-quality`.
- **Alternative / complement:** `manage-business-terms` (explicit, single-term authoring with related assets).

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `get_tables_details`, `search_domain_knowledge`.
- **Governance (`gov`):** `propose_knowledge`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Domain-specific only.** Preferences that apply to any domain (output format, visual style, audience, depth) are never proposed. The validation criterion is: the proposal must mention specific tables, columns or metrics from the domain.
- **Quality bar for `business_concept`:** a concept must meet at least 2 of (precise definition with formula/threshold, actively used in the analysis, relevant to existing tables/columns, explicitly defined by the user) to be proposed.
- **Proposals are Draft** and reviewed in the Governance UI by an administrator before integration.
