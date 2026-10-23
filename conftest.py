"""Workspace root conftest.

Adds rai-agent package root to sys.path so that rai-agent knowledge tests
can use ``importlib.import_module("tests.knowledge.conftest")`` for dynamic
schema loading in domain config fixtures.
"""

from __future__ import annotations

import sys
from pathlib import Path

_RAI_AGENT_PKG = str(Path(__file__).resolve().parent / "packages" / "rai-agent")


def pytest_configure(config: object) -> None:  # noqa: ARG001
    """Add rai-agent package root to sys.path before collection."""
    if _RAI_AGENT_PKG not in sys.path:
        sys.path.insert(0, _RAI_AGENT_PKG)
