"""Tests for AcliJiraAdapter — full protocol implementation over ACLI."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
from rai_pro.adapters.acli_jira import AcliJiraAdapter, normalize_status

from raise_cli.adapters.models import AdapterHealth

# ── Fixtures ────────────────────────────────────────────────────────────────

JIRA_YAML = """\
projects:
  RAISE:
    name: RAISE
    site: humansys.atlassian.net
workflow:
  status_mapping:
    backlog: 11
    in-progress: 31
    done: 41
"""


def _run(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    return asyncio.run(coro)


def _make_adapter(tmp_path: Path, yaml_content: str = JIRA_YAML) -> AcliJiraAdapter:
    """Create adapter with a temporary jira.yaml."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()
    (raise_dir / "jira.yaml").write_text(yaml_content)
    return AcliJiraAdapter(project_root=tmp_path)


# ── Config loading ──────────────────────────────────────────────────────────


class TestConfigLoading:
    """__init__ loads jira.yaml and creates bridge."""

    def test_loads_config_successfully(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        # Verify via public behavior: build_url works (needs project config)
        assert (
            adapter.build_url("RAISE-99")
            == "https://humansys.atlassian.net/browse/RAISE-99"
        )

    def test_raises_on_missing_jira_yaml(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="jira.yaml"):
            AcliJiraAdapter(project_root=tmp_path)


# ── Status normalization ────────────────────────────────────────────────────


class TestNormalizeStatus:
    """normalize_status uses convention: replace('-', ' ').title()."""

    def test_in_progress(self) -> None:
        assert normalize_status("in-progress") == "In Progress"

    def test_done(self) -> None:
        assert normalize_status("done") == "Done"

    def test_backlog(self) -> None:
        assert normalize_status("backlog") == "Backlog"

    def test_selected_for_development(self) -> None:
        assert (
            normalize_status("selected for development") == "Selected For Development"
        )


# ── URL construction ────────────────────────────────────────────────────────


class TestBuildUrl:
    """build_url constructs web URL from site + key."""

    def test_builds_browse_url(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert (
            adapter.build_url("RAISE-99")
            == "https://humansys.atlassian.net/browse/RAISE-99"
        )

    def test_unknown_project_returns_empty(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        assert adapter.build_url("UNKNOWN-1") == ""


# ── Health ──────────────────────────────────────────────────────────────────


class TestHealth:
    """health() delegates to AcliJiraBridge.health()."""

    def test_delegates_to_bridge(self, tmp_path: Path) -> None:
        adapter = _make_adapter(tmp_path)
        expected = AdapterHealth(
            name="jira-acli", healthy=True, message="OK", latency_ms=100
        )
        adapter._bridge.health = AsyncMock(return_value=expected)  # pyright: ignore[reportPrivateUsage]

        result = _run(adapter.health())
        assert result.healthy is True
        assert result.name == "jira-acli"
