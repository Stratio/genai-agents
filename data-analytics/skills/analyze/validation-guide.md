# Final Output Validation Guide

Validation checklist of the finished product before reporting to the user. Validation is structured in 4 blocks with PASS/WARNING/FAIL criteria per item.

## When to generate

| Depth | Blocks | Format |
|-------|--------|--------|
| Quick | Block A only (file integrity) | Chat only (no file) |
| Standard | Blocks A + B + C | Generate `validation/validation.md` + summary in chat |
| Deep | Blocks A + B + C + D | Generate `validation/validation.md` + summary in chat |

**User override**: If the user explicitly requests validation in other formats (PDF, HTML, DOCX), generate the .md first and then convert with:
```bash
python3 skills/analyze/report/tools/md_to_report.py output/[ANALYSIS_DIR]/validation/validation.md --style corporate
```
Add `--html` if HTML was requested. Add `--docx` if DOCX was requested.

## Validation Blocks

### Block A — File integrity

**Verification command (MANDATORY to execute):**
```bash
ls -lh output/[ANALYSIS_DIR]/
```
Check that each file declared in the plan appears in the listing with size > 0 bytes.

**If a deliverable is missing or has 0 bytes → blocking FAIL**: regenerate the file before continuing with the validation. Do not proceed to Block B until Block A is PASS.

| Item | Verification | Criterion |
|------|-------------|----------|
| report.md | Exists in `output/[ANALYSIS_DIR]/` | PASS if exists, FAIL if not |
| Requested deliverables | Each requested format has its file | PASS if all exist, FAIL if any is missing |
| Referenced assets | Each chart referenced in report.md exists in `assets/` | PASS if all exist, WARNING if any is missing |
| Referenced CSVs | Intermediate data referenced in scripts exists in `data/` | PASS if all exist, WARNING if any is missing |
| Reasoning | reasoning.md exists in `reasoning/` | PASS if exists (only check in Standard/Deep) |
| Validation | validation.md exists in `validation/` | PASS if exists (only check in Standard/Deep) |

**Quick depth adjustment**: In Quick depth, only verify deliverables (report.md, requested formats, assets). Do not verify reasoning or validation since they are not generated as files.

**Criteria:**
- **PASS**: All expected files exist
- **WARNING**: Non-critical files are missing (assets, intermediate CSVs)
- **FAIL**: A main deliverable is missing (report.md, requested format)

### Block B — Visualization quality

For each chart in `output/[ANALYSIS_DIR]/assets/`:

| Item | Verification | Criterion |
|------|-------------|----------|
| Minimum size | File > 1 KB | PASS if > 1KB, WARNING if <= 1KB |
| Sufficient data | > 5 non-null values in main column | PASS if sufficient, WARNING if not |

**Thresholds by chart type:**

| Type | Minimum data points |
|------|-------------------|
| Trend (line chart) | > 6 temporal points |
| Ranking (bar chart) | > 3 categories |
| Distribution (histogram, box) | > 10 values |
| Scatter | > 10 points |
| Heatmap | > 2 rows and > 2 columns |

**Criteria:**
- **PASS**: Chart meets size and data minimums
- **WARNING**: Chart exists but does not meet thresholds → exclude from deliverable and document why
- **FAIL**: Chart was not generated (covered in Block A)

### Block C — Analysis completeness

| Item | Verification | Criterion |
|------|-------------|----------|
| Dimensions covered | Each dimension requested by the user appears in at least one analysis/chart | PASS if all covered, WARNING if any is missing |
| Reasoning sections | All mandatory sections present (see reasoning-guide.md) | PASS if complete, WARNING if any is missing |
| Hypotheses validated | Each formulated hypothesis has a result (CONFIRMED/REFUTED/PARTIAL) | PASS if all have results, WARNING if any remains unvalidated |
| So What test | Executive summary findings pass the 4 mandatory questions | PASS if all pass, WARNING if any does not |

**Criteria:**
- **PASS**: Analysis covers all expected dimensions and sections
- **WARNING**: A dimension or section is missing — document what is missing and why
- **FAIL**: Not applicable (completeness is always WARNING, never blocking)

### Block D — Data consistency

For 1-2 key KPIs of the analysis:

| Item | Verification | Criterion |
|------|-------------|----------|
| KPI in deliverable vs data | Compare reported value in deliverable with calculated value from `output/[ANALYSIS_DIR]/data/` | PASS if discrepancy <= 1% |
| Cross-totals | If there are subtotals, verify they sum to the total | PASS if they match, WARNING if discrepancy <= 5% |

**Criteria:**
- **PASS**: KPIs are consistent between deliverable and source data (discrepancy <= 1%)
- **WARNING**: Discrepancy > 1% and <= 5% — document the difference and possible cause (rounding, filters)
- **FAIL**: Discrepancy > 5% — investigate before delivering

## validation.md file format

```markdown
# Output Validation

## Summary
- **Overall status**: PASS / WARNING / FAIL
- **Blocks executed**: A, B, C [, D]
- **Date**: YYYY-MM-DD HH:MM

## Block A — File integrity
| Item | Status | Detail |
|------|--------|--------|
| report.md | PASS | Exists |
| ... | ... | ... |

## Block B — Visualization quality
| Chart | Size | Data | Status | Detail |
|-------|------|------|--------|--------|
| ventas_por_region.png | 45 KB | 12 categories | PASS | — |
| ... | ... | ... | ... | ... |

## Block C — Analysis completeness
| Item | Status | Detail |
|------|--------|--------|
| Dimensions covered | PASS | region, time, product |
| ... | ... | ... |

## Block D — Data consistency
| KPI | Deliverable value | Data value | Discrepancy | Status |
|-----|-------------------|------------|-------------|--------|
| Total sales | EUR1.2M | EUR1.2M | 0.0% | PASS |
| ... | ... | ... | ... | ... |
```

## General rule

- **Block A (file integrity)**: FAIL is **blocking** — regenerate the missing files before continuing.
- **Blocks B, C, D**: validation **does not block delivery**. If there are WARNINGs or FAILs, they are reported in chat along with the findings summary, but the analysis is delivered regardless. The goal is transparency, not blocking.
