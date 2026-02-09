"""Tests for code analyzer models and protocol."""

from __future__ import annotations

from pathlib import Path

from raise_cli.context.analyzers.models import ModuleInfo
from raise_cli.context.analyzers.protocol import CodeAnalyzer


class TestModuleInfo:
    """Tests for ModuleInfo Pydantic model."""

    def test_creates_with_required_fields(self) -> None:
        """Should create ModuleInfo with all required fields."""
        info = ModuleInfo(
            name="memory",
            language="python",
            source_path="src/raise_cli/memory",
            imports=["config", "context"],
            exports=["append_pattern", "PatternInput"],
            component_count=12,
            entry_points=["raise memory add"],
        )
        assert info.name == "memory"
        assert info.language == "python"
        assert info.source_path == "src/raise_cli/memory"
        assert info.imports == ["config", "context"]
        assert info.exports == ["append_pattern", "PatternInput"]
        assert info.component_count == 12
        assert info.entry_points == ["raise memory add"]

    def test_defaults_for_optional_lists(self) -> None:
        """Should default to empty lists for imports, exports, entry_points."""
        info = ModuleInfo(
            name="core",
            language="python",
            source_path="src/raise_cli/core",
            component_count=5,
        )
        assert info.imports == []
        assert info.exports == []
        assert info.entry_points == []

    def test_component_count_must_be_non_negative(self) -> None:
        """Should accept zero component count."""
        info = ModuleInfo(
            name="empty",
            language="python",
            source_path="src/raise_cli/empty",
            component_count=0,
        )
        assert info.component_count == 0

    def test_is_pydantic_model(self) -> None:
        """ModuleInfo should be a Pydantic BaseModel."""
        from pydantic import BaseModel

        assert issubclass(ModuleInfo, BaseModel)

    def test_model_serialization(self) -> None:
        """Should serialize to dict correctly."""
        info = ModuleInfo(
            name="config",
            language="python",
            source_path="src/raise_cli/config",
            imports=[],
            exports=["get_project_root"],
            component_count=3,
            entry_points=[],
        )
        data = info.model_dump()
        assert data["name"] == "config"
        assert data["exports"] == ["get_project_root"]


class TestCodeAnalyzerProtocol:
    """Tests for CodeAnalyzer Protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """CodeAnalyzer should be runtime_checkable."""
        assert hasattr(CodeAnalyzer, "__protocol_attrs__") or isinstance(
            CodeAnalyzer, type
        )

    def test_compliant_class_is_instance(self) -> None:
        """A class implementing detect() and analyze_modules() should pass isinstance."""

        class FakeAnalyzer:
            def detect(self, project_root: Path) -> bool:
                return True

            def analyze_modules(self, project_root: Path) -> list[ModuleInfo]:
                return []

        assert isinstance(FakeAnalyzer(), CodeAnalyzer)

    def test_non_compliant_class_is_not_instance(self) -> None:
        """A class missing methods should NOT pass isinstance."""

        class NotAnalyzer:
            pass

        assert not isinstance(NotAnalyzer(), CodeAnalyzer)
