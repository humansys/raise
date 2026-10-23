"""PM gates opt-in config — reads project.pm_gates from .raise/manifest.yaml.

Gates in this package skip silently when pm_gates is not configured,
so they are safe to distribute without imposing PM discipline on all users.
Only repositories that opt in (project.pm_gates.enabled: true) activate them.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def pm_gates_enabled(working_dir: Path) -> bool:
    """Return True if pm_gates are opted-in for this project.

    Reads ``project.pm_gates.enabled`` from ``.raise/manifest.yaml``.
    Returns False if the manifest is absent, malformed, or the key is not set.
    """
    manifest = working_dir / ".raise" / "manifest.yaml"
    if not manifest.is_file():
        return False
    data: dict[str, object] = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    project = data.get("project", {})
    if not isinstance(project, dict):
        return False
    pm_gates = project.get("pm_gates", {})
    if not isinstance(pm_gates, dict):
        return False
    return bool(pm_gates.get("enabled", False))


def pm_gates_strictness(working_dir: Path) -> str:
    """Return the strictness level for PM gates (``advisory`` or ``block``).

    Defaults to ``"advisory"`` when not configured.
    """
    manifest = working_dir / ".raise" / "manifest.yaml"
    if not manifest.is_file():
        return "advisory"
    data: dict[str, object] = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    project = data.get("project", {})
    if not isinstance(project, dict):
        return "advisory"
    pm_gates = project.get("pm_gates", {})
    if not isinstance(pm_gates, dict):
        return "advisory"
    strictness = pm_gates.get("strictness", "advisory")
    return str(strictness) if strictness else "advisory"
