"""Tests for PythonApiConfluenceAdapter.

S1051.2 (RAISE-1055)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from raise_cli.adapters.confluence_adapter import PythonApiConfluenceAdapter
from raise_cli.adapters.confluence_config import (
    ArtifactRouting,
    ConfluenceConfig,
    ConfluenceInstanceConfig,
)
from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.adapters.protocols import DocumentationTarget


def _make_config(**routing_overrides: Any) -> ConfluenceConfig:
    """Helper: create a ConfluenceConfig with optional routing."""
    routing = routing_overrides.get("routing", {})
    return ConfluenceConfig(
        default_instance="default",
        instances={
            "default": ConfluenceInstanceConfig(
                url="https://test.atlassian.net/wiki",
                username="test@test.com",
                space_key="TEST",
                instance_name="default",
                routing=routing,
            ),
        },
    )


_CONFIG_MOD = "raise_cli.adapters.confluence_adapter"


# ── T1: Constructor + protocol conformance ───────────────────────────────


class TestConstructorAndProtocol:
    """Adapter construction and protocol conformance."""

    @patch(f"{_CONFIG_MOD}.ConfluenceClient")
    @patch(f"{_CONFIG_MOD}.load_confluence_config")
    def test_satisfies_documentation_target(
        self, mock_load: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        mock_load.return_value = _make_config()
        adapter = PythonApiConfluenceAdapter(project_root=Path("/fake"))
        assert isinstance(adapter, DocumentationTarget)

    @patch(f"{_CONFIG_MOD}.ConfluenceClient")
    @patch(f"{_CONFIG_MOD}.load_confluence_config")
    def test_loads_config_and_creates_client(
        self, mock_load: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        config = _make_config()
        mock_load.return_value = config
        adapter = PythonApiConfluenceAdapter(project_root=Path("/fake"))
        mock_load.assert_called_once_with(Path("/fake"))
        mock_client_cls.assert_called_once_with(config.get_instance())

    @patch(f"{_CONFIG_MOD}.ConfluenceClient")
    @patch(f"{_CONFIG_MOD}.load_confluence_config")
    def test_default_project_root_is_cwd(
        self, mock_load: MagicMock, mock_client_cls: MagicMock, tmp_path: Path
    ) -> None:
        mock_load.return_value = _make_config()
        with patch(f"{_CONFIG_MOD}.Path") as mock_path:
            mock_path.cwd.return_value = tmp_path
            PythonApiConfluenceAdapter()
            mock_load.assert_called_once_with(tmp_path)
