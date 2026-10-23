r"""Utility for configurable work-item ID regex — RAISE-18508.

Centralizes the pattern used to validate work-item keys across gates,
pipeline modules, and adapters.  Callers compile the regex once via
``work_id_re`` and should NOT hardcode ``[A-Z][A-Z0-9]*-\\d+`` directly.
"""

from __future__ import annotations

import re
from pathlib import Path

DEFAULT_ID_PATTERN: str = r"[A-Z][A-Z0-9]*-\d+"


def work_id_re(pattern: str) -> re.Pattern[str]:
    """Return a compiled regex for the given work-item ID pattern."""
    return re.compile(pattern)


def load_id_pattern(project_root: Path) -> str:
    """Read ``id_pattern`` from ``.raise/backlog.yaml``.

    Returns ``DEFAULT_ID_PATTERN`` on any error (missing file, invalid YAML,
    adapter not found) so callers never need to handle the failure.
    """
    try:
        from raise_cli.adapters.backlog_config import (
            get_configured_adapters,
            load_backlog_config,
        )

        adapters = get_configured_adapters(project_root)
        if not adapters:
            return DEFAULT_ID_PATTERN
        adapter_name = next(iter(adapters))
        cfg = load_backlog_config(project_root, adapter_name)
        re.compile(cfg.id_pattern)  # validate — re.error falls through to except
        return cfg.id_pattern
    except Exception:  # noqa: BLE001 — fail-open: always return a usable pattern
        return DEFAULT_ID_PATTERN
