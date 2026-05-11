# Forensic Audit

High-contrast, monospace-forward, almost evidentiary. The theme reads as
"this document is a record, not a pitch". Built for auditors, compliance
officers and security reports where precision, traceability and sobriety
matter more than visual warmth.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #5a1c1c | titles, finding headers, classification marks |
| ink | #121212 | body text |
| muted | #5a5550 | metadata, footnotes, provenance labels |
| rule | #cccccc | divider lines, table grids |
| bg | #ffffff | page / main surface |
| bg_alt | #ecebe8 | sidebar for chain-of-custody blocks |
| accent | #b45309 | emphasis on critical findings |
| state_ok | #166534 | clean / compliant indicators |
| state_warn | #b45309 | observations requiring attention |
| state_danger | #991b1b | critical findings / breaches |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #5a1c1c | matches primary |
| 2 | #b45309 | matches accent |
| 3 | #374151 | forensic slate |
| 4 | #65a30d | regulatory green |
| 5 | #7c2d12 | deeper rust |
| 6 | #111827 | near-black filler |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | IBM Plex Sans | 24 | Arial, sans-serif |
| h2 | IBM Plex Sans | 16 | Arial, sans-serif |
| body | IBM Plex Mono | 10 | Consolas, monospace |
| caption | IBM Plex Mono | 9 | Consolas, monospace |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

The monospace body is deliberate: it reads as record-keeping and keeps
identifiers, hashes and evidence strings aligned legibly.

## Optional extensions

- **Motion budget**: `minimal` (no decorative transitions; evidence
  documents do not animate)
- **Border radius**: `0px` (hard edges)
- **Dark mode variant**: not shipped
- **Chart sequential**: base color `#5a1c1c`

## Tone family

`forensic-audit`.

## Best used for

- Internal and external audit reports
- Compliance and regulatory filings
- Security incident reports, findings registers
- Chain-of-custody, due-diligence and investigation documents

## Anti-patterns

- Do not use as a default for general BI reports — the tone is too
  severe and signals "something is being investigated".
- Do not replace the monospace body with a serif or proportional sans;
  the evidentiary legibility is the whole point.
- Do not add decorative iconography or warm neutrals.
