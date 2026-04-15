"""Internationalisation catalogue for data-analytics tools.

Provides a flat, key-based catalogue of labels in every supported language,
plus a `get_labels(lang, overrides)` helper that resolves the effective label
set used by the generators (DOCX, PDF, dashboard, markdown).

Resolution priority (highest wins):

1. `overrides` dict passed by the caller — always wins for the provided keys.
2. Explicit `lang` argument — selects the language from the catalogue.
3. `.agent_lang` file at the root of the packaged agent — written at packaging
   time by `pack_*.sh --lang <code>`. Walks up from CWD and from this file's
   location to find it.
4. `"en"` as final fallback.

For keys missing in the resolved language, the English value is used so the
output is never empty.

Adding a new language:

- Add a new top-level key to `CATALOG` with the same set of keys translated.
- No changes needed elsewhere; tools read from whatever is in `CATALOG`.
"""

from __future__ import annotations

from pathlib import Path


CATALOG: dict[str, dict[str, str]] = {
    "en": {
        # Scaffold section headings (used by docx_generator.render_scaffold
        # and pdf_generator via Jinja templates)
        "report.executive_summary": "Executive Summary",
        "report.methodology": "Methodology",
        "report.data_sources": "Data and Sources",
        "report.analysis": "Analysis",
        "report.conclusions": "Conclusions",

        # Cover page metadata labels (DOCX + markdown HTML covers)
        "cover.author": "Author",
        "cover.domain": "Domain",
        "cover.date": "Date",

        # Dashboard UI chrome (dashboard_builder.py)
        "dashboard.filters": "Filters",
        "dashboard.all": "All",
        "dashboard.clear_filters": "Clear filters",
        "dashboard.kpis_nav": "KPIs",
        "dashboard.footer_default": "Dashboard generated automatically",

        # Default titles used when the caller does not provide one
        "report.default_title": "Report",

        # HTML lang attribute (used by dashboard_builder and md_to_report)
        "html.lang_attr": "en",
    },
    "es": {
        "report.executive_summary": "Resumen Ejecutivo",
        "report.methodology": "Metodología",
        "report.data_sources": "Datos y Fuentes",
        "report.analysis": "Análisis",
        "report.conclusions": "Conclusiones",

        "cover.author": "Autor",
        "cover.domain": "Dominio",
        "cover.date": "Fecha",

        "dashboard.filters": "Filtros",
        "dashboard.all": "Todos",
        "dashboard.clear_filters": "Limpiar filtros",
        "dashboard.kpis_nav": "KPIs",
        "dashboard.footer_default": "Dashboard generado automáticamente",

        "report.default_title": "Informe",

        "html.lang_attr": "es",
    },
}


_AGENT_LANG_FILENAME = ".agent_lang"


def _read_agent_lang() -> str | None:
    """Walk up from CWD and from this file's directory looking for `.agent_lang`.

    Returns the language code written inside the first match, or None.
    """
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
    """Resolve the effective language for this invocation.

    Priority: explicit arg → `.agent_lang` file → `"en"`. Unknown language
    codes are accepted and returned as-is; the caller-facing `get_labels`
    handles the fallback per key.
    """
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
    """Return the resolved label dict for the given language.

    - Starts from the English catalogue so every key is always defined.
    - Overlays the chosen language's catalogue (if present).
    - Applies caller overrides last (highest priority).
    """
    effective_lang = resolve_lang(lang)

    labels: dict[str, str] = dict(CATALOG["en"])
    if effective_lang != "en" and effective_lang in CATALOG:
        labels.update(CATALOG[effective_lang])

    if overrides:
        labels.update(overrides)

    return labels
