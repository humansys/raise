"""Shared fixtures for backlog integration tests.

Architecture: S347.7 (E347 Backlog Automation)
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

from raise_cli.adapters.filesystem import FilesystemPMAdapter


@pytest.fixture
def backlog_dir(tmp_path: Path) -> Path:
    """Create the YAML store directory structure and return it."""
    items_dir = tmp_path / ".raise" / "backlog" / "items"
    items_dir.mkdir(parents=True)
    return items_dir


@pytest.fixture
def file_adapter(backlog_dir: Path) -> FilesystemPMAdapter:
    """Return a FilesystemPMAdapter rooted at the tmp_path with YAML store."""
    # backlog_dir parent chain: tmp_path / .raise / backlog / items
    project_root = backlog_dir.parent.parent.parent
    return FilesystemPMAdapter(project_root=project_root)



def _write_yaml_item(path: Path, **fields: Any) -> None:
    """Write a BacklogItem-compatible YAML file to disk."""
    defaults: dict[str, Any] = {
        "key": "E1",
        "summary": "Test Item",
        "issue_type": "Epic",
        "status": "pending",
        "created": "2026-03-03T00:00:00+00:00",
        "updated": "2026-03-03T00:00:00+00:00",
    }
    defaults.update(fields)
    path.write_text(yaml.safe_dump(defaults, sort_keys=False), encoding="utf-8")


@pytest.fixture
def write_yaml_item() -> Callable[..., None]:
    """Fixture providing a helper to write BacklogItem YAML files to disk."""
    return _write_yaml_item
