# pyright: reportPrivateUsage=false
"""Copper & Patina HTML shell para artefactos locales (RAISE-19213)."""

from __future__ import annotations

import html

from raise_cli.ddd.tactical_report import _COPPER_PATINA_CSS


def wrap_html_shell(title: str, body: str) -> str:
    """Envolver body en un documento HTML con CSS Copper & Patina inline."""
    return (
        f"<!DOCTYPE html>\n"
        f'<html lang="es">\n'
        f"<head>\n"
        f'  <meta charset="utf-8">\n'
        f'  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{html.escape(title)}</title>\n"
        f"  <style>{_COPPER_PATINA_CSS}</style>\n"
        f"</head>\n"
        f"<body>\n"
        f"{body}\n"
        f"</body>\n"
        f"</html>"
    )
