"""Tests for DeclarativeAdapterConfig schema models.

TDD RED phase — all tests should fail until implementation.
AC refs: s337.1-story.md scenarios 8-9.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from raise_cli.adapters.declarative.schema import (
    AdapterMeta,
    DeclarativeAdapterConfig,
    MethodMapping,
    ResponseMapping,
    ServerRef,
)
from raise_cli.mcp.schema import ServerConnection

FIXTURES = Path(__file__).parent / "fixtures"


def _load_yaml(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return yaml.safe_load(f)


# --- AC Scenario 8: Valid YAML config ---


class TestValidConfig:
    def test_full_config_parses(self) -> None:
        data = _load_yaml("valid.yaml")
        config = DeclarativeAdapterConfig(**data)
        assert config.adapter.name == "github"
        assert config.adapter.protocol == "pm"
        assert config.server.command == "uvx"
        assert config.server.args == ["mcp-github"]
        assert config.server.env == ["GITHUB_TOKEN"]

    def test_methods_parsed(self) -> None:
        data = _load_yaml("valid.yaml")
        config = DeclarativeAdapterConfig(**data)
        assert "create_issue" in config.methods
        assert "search" in config.methods
        assert config.methods["link_to_parent"] is None
        assert config.methods["link_issues"] is None

    def test_method_mapping_fields(self) -> None:
        data = _load_yaml("valid.yaml")
        config = DeclarativeAdapterConfig(**data)
        create = config.methods["create_issue"]
        assert isinstance(create, MethodMapping)
        assert create.tool == "github_create_issue"
        assert "title" in create.args
        assert create.response is not None
        assert "key" in create.response.fields

    def test_response_with_items_path(self) -> None:
        data = _load_yaml("valid.yaml")
        config = DeclarativeAdapterConfig(**data)
        search = config.methods["search"]
        assert isinstance(search, MethodMapping)
        assert search.response is not None
        assert search.response.items_path == "data.items"

    def test_minimal_config(self) -> None:
        data = _load_yaml("minimal.yaml")
        config = DeclarativeAdapterConfig(**data)
        assert config.adapter.name == "minimal"
        assert config.adapter.description is None
        assert config.server.env is None

    def test_docs_protocol(self) -> None:
        data = _load_yaml("docs_adapter.yaml")
        config = DeclarativeAdapterConfig(**data)
        assert config.adapter.protocol == "docs"


# --- AC Scenario 9: Invalid config ---


class TestInvalidConfig:
    def test_missing_adapter_name_raises(self) -> None:
        data = _load_yaml("invalid_missing_name.yaml")
        with pytest.raises(ValidationError, match="name"):
            DeclarativeAdapterConfig(**data)

    def test_missing_server_ref_and_command_raises(self) -> None:
        data = {
            "adapter": {"name": "test", "protocol": "pm"},
            "server": {"args": ["test"]},
            "methods": {},
        }
        with pytest.raises(ValidationError, match="ref.*command|command.*ref"):
            DeclarativeAdapterConfig(**data)

    def test_invalid_protocol_raises(self) -> None:
        data = {
            "adapter": {"name": "test", "protocol": "invalid"},
            "server": {"command": "echo", "args": ["test"]},
            "methods": {},
        }
        with pytest.raises(ValidationError, match="protocol"):
            DeclarativeAdapterConfig(**data)

    def test_missing_tool_in_method_raises(self) -> None:
        data = {
            "adapter": {"name": "test", "protocol": "pm"},
            "server": {"command": "echo", "args": ["test"]},
            "methods": {"search": {"args": {"q": "{{ query }}"}}},
        }
        with pytest.raises(ValidationError, match="tool"):
            DeclarativeAdapterConfig(**data)

    def test_empty_methods_allowed(self) -> None:
        """Empty methods dict is valid — all methods will raise NotImplementedError."""
        data = {
            "adapter": {"name": "test", "protocol": "pm"},
            "server": {"command": "echo", "args": ["test"]},
            "methods": {},
        }
        config = DeclarativeAdapterConfig(**data)
        assert config.methods == {}


# --- Model unit tests ---


class TestAdapterMeta:
    def test_required_fields(self) -> None:
        meta = AdapterMeta(name="test", protocol="pm")
        assert meta.name == "test"
        assert meta.protocol == "pm"
        assert meta.description is None

    def test_with_description(self) -> None:
        meta = AdapterMeta(name="test", protocol="pm", description="A test")
        assert meta.description == "A test"


class TestServerConnection:
    def test_required_fields(self) -> None:
        server = ServerConnection(command="uvx", args=["mcp-test"])
        assert server.command == "uvx"
        assert server.args == ["mcp-test"]
        assert server.env is None

    def test_with_env(self) -> None:
        server = ServerConnection(
            command="uvx", args=["mcp-test"], env=["TOKEN", "URL"]
        )
        assert server.env == ["TOKEN", "URL"]


class TestServerRef:
    """S338.5: ServerRef model — ref-only, inline-only, neither rejected."""

    def test_inline_only(self) -> None:
        """Inline command works — backwards compat."""
        ref = ServerRef(command="uvx", args=["mcp-test"])
        assert ref.command == "uvx"
        assert ref.ref is None

    def test_ref_only(self) -> None:
        """Ref-only works — no command needed."""
        ref = ServerRef(ref="context7")
        assert ref.ref == "context7"
        assert ref.command is None

    def test_neither_ref_nor_command_raises(self) -> None:
        """Neither ref nor command → ValidationError."""
        with pytest.raises(ValidationError, match="ref.*command|command.*ref"):
            ServerRef(args=["test"])

    def test_ref_with_no_args(self) -> None:
        """Ref-only with defaults for args/env."""
        ref = ServerRef(ref="my-server")
        assert ref.args == []
        assert ref.env is None

    def test_config_with_server_ref(self) -> None:
        """DeclarativeAdapterConfig accepts server.ref."""
        data = {
            "adapter": {"name": "test", "protocol": "pm"},
            "server": {"ref": "context7"},
            "methods": {},
        }
        config = DeclarativeAdapterConfig(**data)
        assert config.server.ref == "context7"
        assert config.server.command is None


class TestResponseMapping:
    def test_fields_only(self) -> None:
        resp = ResponseMapping(fields={"key": "{{ data.id }}"})
        assert resp.items_path is None

    def test_with_items_path(self) -> None:
        resp = ResponseMapping(fields={"key": "{{ item.id }}"}, items_path="data.items")
        assert resp.items_path == "data.items"
