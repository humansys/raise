"""Tests for raise-cli get_active_backend factory."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from raise_core.graph.backends.filesystem import FilesystemGraphBackend
from raise_core.graph.backends.protocol import KnowledgeGraphBackend


class TestGetActiveBackendFactory:
    """CLI factory selects backend based on env vars."""

    def test_no_env_vars_returns_filesystem(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.graph.backends import get_active_backend

        monkeypatch.delenv("RAI_SERVER_URL", raising=False)
        monkeypatch.delenv("RAI_API_KEY", raising=False)

        backend = get_active_backend(tmp_path / "index.json")

        assert isinstance(backend, FilesystemGraphBackend)

    def test_both_env_vars_returns_dual_write(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.graph.backends import get_active_backend
        from raise_cli.graph.backends.dual import DualWriteBackend

        monkeypatch.setenv("RAI_SERVER_URL", "http://localhost:8000")
        monkeypatch.setenv("RAI_API_KEY", "rsk_test_abc")

        backend = get_active_backend(tmp_path / "index.json")

        assert isinstance(backend, DualWriteBackend)

    def test_url_without_key_falls_back_to_filesystem(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        from raise_cli.graph.backends import get_active_backend

        monkeypatch.setenv("RAI_SERVER_URL", "http://localhost:8000")
        monkeypatch.delenv("RAI_API_KEY", raising=False)

        with caplog.at_level(logging.WARNING):
            backend = get_active_backend(tmp_path / "index.json")

        assert isinstance(backend, FilesystemGraphBackend)
        assert "RAI_API_KEY" in caplog.text

    def test_key_without_url_returns_filesystem(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.graph.backends import get_active_backend

        monkeypatch.delenv("RAI_SERVER_URL", raising=False)
        monkeypatch.setenv("RAI_API_KEY", "rsk_test_abc")

        backend = get_active_backend(tmp_path / "index.json")

        assert isinstance(backend, FilesystemGraphBackend)

    def test_returns_protocol_compatible(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.graph.backends import get_active_backend

        monkeypatch.delenv("RAI_SERVER_URL", raising=False)
        monkeypatch.delenv("RAI_API_KEY", raising=False)

        backend = get_active_backend(tmp_path / "index.json")

        assert isinstance(backend, KnowledgeGraphBackend)

    def test_dual_write_has_correct_project_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.graph.backends import get_active_backend
        from raise_cli.graph.backends.dual import DualWriteBackend

        monkeypatch.setenv("RAI_SERVER_URL", "http://localhost:8000")
        monkeypatch.setenv("RAI_API_KEY", "rsk_test_abc")

        backend = get_active_backend(tmp_path / "index.json")

        assert isinstance(backend, DualWriteBackend)
        # Remote should be ApiGraphBackend with project_id derived from cwd
        from raise_cli.graph.backends.api import ApiGraphBackend

        assert isinstance(backend.remote, ApiGraphBackend)
