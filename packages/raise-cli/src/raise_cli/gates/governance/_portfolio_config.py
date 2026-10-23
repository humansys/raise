"""Portfolio gates opt-in config — reads project.portfolio_gates from manifest.

Mirrors ``gates/pm/_config.py::pm_gates_enabled``. A distinct semantic tier
from ``pm_gates`` (which gates PM discipline — ICP/JTBD — at epic/story
scope): ``portfolio_gates`` gates strategic/portfolio invariants at
Initiative scope (S14559.1, RAISE-14588). Gates in this package skip
silently when portfolio_gates is not configured, so they are safe to
distribute without imposing portfolio discipline on all users.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def portfolio_gates_enabled(working_dir: Path) -> bool:
    """Return True if portfolio_gates are opted-in for this project.

    Reads ``project.portfolio_gates.enabled`` from ``.raise/manifest.yaml``.
    Returns False if the manifest is absent, malformed, or the key is not set.
    """
    manifest = working_dir / ".raise" / "manifest.yaml"
    if not manifest.is_file():
        return False
    data: dict[str, object] = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    project = data.get("project", {})
    if not isinstance(project, dict):
        return False
    portfolio_gates = project.get("portfolio_gates", {})
    if not isinstance(portfolio_gates, dict):
        return False
    return bool(portfolio_gates.get("enabled", False))
