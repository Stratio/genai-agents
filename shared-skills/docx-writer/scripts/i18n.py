"""Internationalisation catalogue for the docx-writer skill.

Subset of the labels consumed by DOCXBuilder: cover metadata, generic section
headings, page chrome. Keys that belong to other output surfaces (HTML
dashboards, PDF paged-media) are intentionally not duplicated here — this
skill is only responsible for DOCX output.

Resolution priority (highest wins):

1. ``overrides`` dict passed by the caller — always wins for the provided keys.
2. Explicit ``lang`` argument — selects the language from the catalogue.
3. ``.agent_lang`` file at the root of the packaged agent (written at
   packaging time by ``pack_*.sh --lang <code>``). Walked up from CWD and from
   this file's directory to find it.
4. ``"en"`` as final fallback.

For keys missing in the resolved language, the English value is used so the
output is never empty.
"""
from __future__ import annotations

from pathlib import Path

CATALOG: dict[str, dict[str, str]] = {
    "en": {
        "cover.author": "Author",
        "cover.domain": "Domain",
        "cover.date": "Date",
        "cover.default_title": "Document",
        "page.footer_page_label": "Page",
        "page.footer_of_label": "of",
    },
    "es": {
        "cover.author": "Autor",
        "cover.domain": "Dominio",
        "cover.date": "Fecha",
        "cover.default_title": "Documento",
        "page.footer_page_label": "Página",
        "page.footer_of_label": "de",
    },
}

_AGENT_LANG_FILENAME = ".agent_lang"


def _read_agent_lang() -> str | None:
    starts = {Path.cwd(), Path(__file__).resolve().parent}
    for start in starts:
        p = start
        while True:
            candidate = p / _AGENT_LANG_FILENAME
            if candidate.is_file():
                try:
                    value = candidate.read_text(encoding="utf-8").strip()
                except OSError:
                    value = ""
                return value or None
            if p.parent == p:
                break
            p = p.parent
    return None


def resolve_lang(lang: str | None = None) -> str:
    if lang:
        return lang
    from_file = _read_agent_lang()
    if from_file:
        return from_file
    return "en"


def get_labels(
    lang: str | None = None,
    overrides: dict[str, str] | None = None,
) -> dict[str, str]:
    effective = resolve_lang(lang)
    labels: dict[str, str] = dict(CATALOG["en"])
    if effective != "en" and effective in CATALOG:
        labels.update(CATALOG[effective])
    if overrides:
        labels.update(overrides)
    return labels
