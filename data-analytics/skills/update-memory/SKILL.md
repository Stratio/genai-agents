---
name: update-memory
description: "Update the agent's persistent memory file with user preferences, data patterns, and discovered heuristics so future sessions can pick them up. Use when an analysis finishes, when the user asks to save or remember a preference, or when a reusable decision (naming convention, excluded domain, preferred chart type) emerges during the conversation. For governance / semantic-layer persistence, prefer propose-knowledge."
argument-hint: "[preference or pattern to remember (optional)]"
---

# Skill: Persistent Memory Update

Manages writing to `output/MEMORY.md` — the agent's curated knowledge file (preferences, data patterns, heuristics).

## 1. Read Current State

Read `output/MEMORY.md`.

If the file does not yet exist, do **not** create it here — section 3 will
initialize it from the template (`templates/memory/MEMORY.md`) before the first
write. Just continue with section 2 treating the memory as empty.

## 2. Determine Source and Detect Updates

### 2.1 If coming from /analyze (post-analysis)

Analyze the complete session to detect:

**User preferences** — Compare this analysis's choices with the "User Preferences" sec:
- Fields to track: depth, format(s), style, audience, main domain
- If a field had no previous value → record the one from this session
- If a field already had a value and it matches → do not change
- If a field already had a value and it differs → update only if the user has chosen the new value in 2+ consecutive analyses (compare with ANALYSIS_MEMORY.md to verify)

**Data patterns** — Compare quality findings (EDA, post-query validation, profiling) with the "Known Data Patterns" sec:
- Group by domain (subsection `### domain_name`)
- If the pattern already exists for that domain → increment counter `[observed N+1, YYYY-MM]`
- If it is new → record with `[observed 1, YYYY-MM]`
- Types of patterns to capture: nulls in columns (>30%), necessary filters, incomplete time ranges, systematic outliers, records to exclude

**Learned heuristics** — Analytical findings that transcend an individual analysis:
- Only record if confidence is HIGH and applies to multiple analyses or periods
- Format: `- [Finding] [YYYY-MM, confidence]`
- Example: "Q4 shows seasonal peak >30% vs Q1-Q3 in retail sales [2026-02, high]"

### 2.2 If coming directly from the user ($ARGUMENTS)

Parse the user's request and write in the corresponding section:
- If they mention a preference (format, style, domain, etc.) → Preferences sec
- If they mention a data pattern → Patterns sec (ask for domain if not obvious)
- If it is a general finding → Heuristics sec

## 3. Write Updates

- If `output/MEMORY.md` does not exist, initialize it by copying the template
  before writing:

      mkdir -p output
      cp templates/memory/MEMORY.md output/MEMORY.md

- Edit `output/MEMORY.md` in the corresponding section
- Do not duplicate entries — update counters or existing values
- Keep sections ordered: Preferences first, Patterns by domain, Heuristics chronological
- If a section had the placeholder "(No ... recorded)", remove it when adding the first entry
- Write all entries in the user's language (the language used in the conversation)

## 4. Confirm

Briefly report in chat (1-2 lines) what was updated and what changes were made. Example:
> Memory updated: PDF+Web format preference recorded, null pattern in `descuento` incremented to [observed 3].
