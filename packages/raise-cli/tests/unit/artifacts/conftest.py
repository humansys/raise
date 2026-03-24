"""Fixtures for artifact tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest


@pytest.fixture
def artifacts_dir(tmp_path: Path) -> Path:
    """Temporary .raise/artifacts/ directory."""
    d = tmp_path / ".raise" / "artifacts"
    d.mkdir(parents=True)
    return d


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Temporary project root with .raise/ structure."""
    return tmp_path


@pytest.fixture
def sample_created() -> datetime:
    """Fixed datetime for deterministic tests."""
    return datetime(2026, 3, 3, 10, 0, 0, tzinfo=UTC)
