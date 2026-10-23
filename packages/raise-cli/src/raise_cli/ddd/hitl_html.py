"""HITL HTML renderer — Copper & Patina tactical escalation review page.

Implements RAISE-16917 (D3):
  - Renders `tactical_hitl.html.j2` via Jinja2 with the provided verdicts.
  - Writes the rendered HTML to a temp file (or --output path).
  - Returns the Path to the rendered file.
  - Caller is responsible for `webbrowser.open()` (CLI handler in graph.py).

Template lives in `raise_cli/ddd/templates/tactical_hitl.html.j2`.
Palette: Copper & Patina (project decision, see copper-patina-html-extension memory).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.ddd.escalation import TacticalEscalationVerdict


def render_tactical_hitl(
    verdicts: list[TacticalEscalationVerdict],
    bc_map: dict[str, str],
    output_path: Path | None = None,
) -> Path:
    """Render the Copper & Patina HITL HTML for the given escalation verdicts.

    Args:
        verdicts: List of TacticalEscalationVerdict produced by
            :func:`raise_cli.ddd.escalation.escalate_tactical_symbols`.
        bc_map: Mapping of symbol_id → BC name for display.
        output_path: Write to this path. When None, a temp file is created
            in the system temp directory.

    Returns:
        Path to the rendered HTML file (guaranteed to exist after this call).
    """
    try:
        from jinja2 import Environment, FileSystemLoader  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Jinja2 is required for HITL HTML rendering. Install it with: uv add jinja2"
        ) from exc

    templates_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )
    template = env.get_template("tactical_hitl.html.j2")

    rendered = template.render(
        verdicts=verdicts,
        bc_map=bc_map,
    )

    if output_path is None:
        fd, tmp = tempfile.mkstemp(suffix=".html", prefix="ddd-hitl-")
        import os  # noqa: PLC0415

        os.close(fd)
        output_path = Path(tmp)

    output_path.write_text(rendered, encoding="utf-8")
    return output_path
