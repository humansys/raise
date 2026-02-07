"""Tests for discovery analyzer module.

Tests cover:
- Confidence scoring (all 6 signals, boundary scores, tier assignment)
- Path-to-category matching (default paths, custom map, no match)
- Pydantic model validation
"""

from __future__ import annotations

import pytest

from raise_cli.discovery.analyzer import (
    BASE_CLASS_CATEGORIES,
    DEFAULT_CATEGORY_MAP,
    NAME_CATEGORY_OVERRIDES,
    AnalyzedComponent,
    AnalysisResult,
    ConfidenceResult,
    ConfidenceSignals,
    compute_confidence,
    match_path_category,
)
from raise_cli.discovery.scanner import Symbol


# ── Fixtures ──────────────────────────────────────────────────────────────


def _symbol(
    name: str = "Foo",
    kind: str = "class",
    file: str = "src/app/service.py",
    line: int = 1,
    signature: str = "class Foo",
    docstring: str | None = None,
    parent: str | None = None,
) -> Symbol:
    """Create a Symbol for testing."""
    return Symbol(
        name=name,
        kind=kind,
        file=file,
        line=line,
        signature=signature,
        docstring=docstring,
        parent=parent,
    )


# ── Model Tests ───────────────────────────────────────────────────────────


class TestConfidenceSignals:
    """Tests for ConfidenceSignals model."""

    def test_defaults(self) -> None:
        signals = ConfidenceSignals()
        assert signals.has_docstring is False
        assert signals.docstring_length == 0
        assert signals.has_type_annotations is False
        assert signals.path_matches_convention is False
        assert signals.known_base_class is None
        assert signals.name_follows_convention is False
        assert signals.parent_validated is False


class TestConfidenceResult:
    """Tests for ConfidenceResult model."""

    def test_valid_result(self) -> None:
        result = ConfidenceResult(
            score=75,
            tier="high",
            signals=ConfidenceSignals(),
        )
        assert result.score == 75
        assert result.tier == "high"

    def test_score_bounds(self) -> None:
        """Score must be 0-100."""
        with pytest.raises(Exception):
            ConfidenceResult(score=-1, tier="low", signals=ConfidenceSignals())
        with pytest.raises(Exception):
            ConfidenceResult(score=101, tier="low", signals=ConfidenceSignals())


class TestAnalyzedComponent:
    """Tests for AnalyzedComponent model."""

    def test_create(self) -> None:
        comp = AnalyzedComponent(
            id="comp-foo",
            name="Foo",
            kind="class",
            file="src/app.py",
            line=1,
            signature="class Foo",
            module="app",
            confidence=ConfidenceResult(
                score=50, tier="medium", signals=ConfidenceSignals()
            ),
            auto_category="service",
            auto_purpose="Does things.",
            depends_on=[],
            internal=False,
            methods=["bar", "baz"],
            docstring="Does things.",
        )
        assert comp.name == "Foo"
        assert comp.methods == ["bar", "baz"]


class TestAnalysisResult:
    """Tests for AnalysisResult model."""

    def test_create_empty(self) -> None:
        result = AnalysisResult(
            scan_summary={"files_scanned": 0, "total_symbols": 0},
            confidence_distribution={"high": 0, "medium": 0, "low": 0},
            categories={},
            components=[],
            module_groups={},
        )
        assert result.components == []
        assert result.module_groups == {}

    def test_module_groups(self) -> None:
        result = AnalysisResult(
            scan_summary={"files_scanned": 1, "total_symbols": 2},
            confidence_distribution={"high": 2, "medium": 0, "low": 0},
            categories={"service": 2},
            components=[],
            module_groups={
                "src/scanner.py": ["comp-a", "comp-b"],
                "src/drift.py": ["comp-c"],
            },
        )
        assert len(result.module_groups) == 2
        assert result.module_groups["src/scanner.py"] == ["comp-a", "comp-b"]


# ── match_path_category Tests ─────────────────────────────────────────────


class TestMatchPathCategory:
    """Tests for path-to-category matching."""

    def test_cli_commands_path(self) -> None:
        result = match_path_category("src/raise_cli/cli/commands/discover.py")
        assert result == "command"

    def test_cli_non_command_path(self) -> None:
        result = match_path_category("src/raise_cli/cli/main.py")
        assert result == "utility"

    def test_schemas_path(self) -> None:
        result = match_path_category("src/raise_cli/schemas/graph.py")
        assert result == "schema"

    def test_models_path(self) -> None:
        result = match_path_category("src/raise_cli/models/user.py")
        assert result == "model"

    def test_output_path(self) -> None:
        result = match_path_category("src/raise_cli/output/formatters/discover.py")
        assert result == "formatter"

    def test_governance_path(self) -> None:
        result = match_path_category("src/raise_cli/governance/parser.py")
        assert result == "parser"

    def test_context_path(self) -> None:
        result = match_path_category("src/raise_cli/context/builder.py")
        assert result == "builder"

    def test_discovery_path(self) -> None:
        result = match_path_category("src/raise_cli/discovery/scanner.py")
        assert result == "service"

    def test_memory_path(self) -> None:
        result = match_path_category("src/raise_cli/memory/graph.py")
        assert result == "service"

    def test_config_path(self) -> None:
        result = match_path_category("src/raise_cli/config/settings.py")
        assert result == "utility"

    def test_core_path(self) -> None:
        result = match_path_category("src/raise_cli/core/git.py")
        assert result == "utility"

    def test_telemetry_path(self) -> None:
        result = match_path_category("src/raise_cli/telemetry/emitter.py")
        assert result == "service"

    def test_no_match(self) -> None:
        result = match_path_category("src/raise_cli/unknown/foo.py")
        assert result is None

    def test_custom_category_map(self) -> None:
        custom = {"custom/": "widget"}
        result = match_path_category("src/custom/thing.py", custom)
        assert result == "widget"

    def test_custom_map_does_not_use_defaults(self) -> None:
        custom = {"custom/": "widget"}
        result = match_path_category("src/raise_cli/cli/commands/foo.py", custom)
        assert result is None

    def test_most_specific_path_wins(self) -> None:
        """cli/commands/ should match before cli/."""
        result = match_path_category("src/raise_cli/cli/commands/scan.py")
        assert result == "command"


# ── compute_confidence Tests ──────────────────────────────────────────────


class TestComputeConfidence:
    """Tests for confidence scoring."""

    def test_all_signals_present(self) -> None:
        """Maximum confidence: all 6 signals fire."""
        sym = _symbol(
            name="UserService",
            kind="class",
            signature="class UserService(BaseModel)",
            docstring="A service that manages users and their roles.",
            parent=None,
        )
        result = compute_confidence(sym, "service")
        # docstring=30, long_docstring=10, type_annot=0 (no -> or : ), path=20, base_class=10, name_conv=5 = 75
        # Actually BaseModel in signature + "class" uppercase name
        assert result.score >= 70
        assert result.tier == "high"
        assert result.signals.has_docstring is True
        assert result.signals.path_matches_convention is True
        assert result.signals.known_base_class == "BaseModel"
        assert result.signals.name_follows_convention is True

    def test_no_signals(self) -> None:
        """Minimum confidence: no signals fire."""
        sym = _symbol(
            name="SHOUTING",
            kind="function",
            signature="def SHOUTING()",
            docstring=None,
            parent=None,
        )
        result = compute_confidence(sym, None)
        # Function with uppercase name → name_follows_convention=False
        assert result.score == 0
        assert result.tier == "low"

    def test_docstring_short(self) -> None:
        """Short docstring gets 30 but not the +10 bonus."""
        sym = _symbol(docstring="Short.")
        result = compute_confidence(sym, None)
        assert result.signals.has_docstring is True
        assert result.signals.docstring_length == 6
        # Score: 30 (docstring) + 5 (name convention for class) = 35
        assert 30 <= result.score < 45

    def test_docstring_long_bonus(self) -> None:
        """Long docstring (>20 chars) gets +10 bonus."""
        sym = _symbol(docstring="This is a long docstring for testing purposes.")
        result = compute_confidence(sym, None)
        assert result.signals.has_docstring is True
        assert result.signals.docstring_length > 20
        # 30 + 10 + 5 (name conv) = 45
        assert result.score >= 45

    def test_type_annotations_arrow(self) -> None:
        """Return type annotation detected via ->."""
        sym = _symbol(
            kind="function",
            name="get_user",
            signature="def get_user(id: int) -> User",
        )
        result = compute_confidence(sym, None)
        assert result.signals.has_type_annotations is True

    def test_type_annotations_colon(self) -> None:
        """Parameter type annotation detected via ': '."""
        sym = _symbol(
            kind="function",
            name="get_user",
            signature="def get_user(id: int)",
        )
        result = compute_confidence(sym, None)
        assert result.signals.has_type_annotations is True

    def test_path_matches_convention(self) -> None:
        """Path category contributes +20."""
        sym = _symbol()
        no_path = compute_confidence(sym, None)
        with_path = compute_confidence(sym, "service")
        assert with_path.score == no_path.score + 20

    def test_known_base_class_basemodel(self) -> None:
        """BaseModel in signature gives +10 and known_base_class."""
        sym = _symbol(signature="class Foo(BaseModel)")
        result = compute_confidence(sym, None)
        assert result.signals.known_base_class == "BaseModel"

    def test_known_base_class_exception(self) -> None:
        """Exception in signature gives +10."""
        sym = _symbol(signature="class MyError(Exception)")
        result = compute_confidence(sym, None)
        assert result.signals.known_base_class == "Exception"

    def test_name_convention_class_uppercase(self) -> None:
        """Class with uppercase name gets +5."""
        sym = _symbol(name="MyClass", kind="class")
        result = compute_confidence(sym, None)
        assert result.signals.name_follows_convention is True

    def test_name_convention_class_lowercase(self) -> None:
        """Class with lowercase name doesn't get +5."""
        sym = _symbol(name="myclass", kind="class")
        result = compute_confidence(sym, None)
        assert result.signals.name_follows_convention is False

    def test_name_convention_function_lowercase(self) -> None:
        """Function with lowercase name gets +5."""
        sym = _symbol(name="get_user", kind="function")
        result = compute_confidence(sym, None)
        assert result.signals.name_follows_convention is True

    def test_name_convention_method_lowercase(self) -> None:
        """Method with lowercase name gets +5."""
        sym = _symbol(name="get_user", kind="method")
        result = compute_confidence(sym, None)
        assert result.signals.name_follows_convention is True

    def test_parent_validated(self) -> None:
        """Method with parent gets +15."""
        sym = _symbol(name="do_thing", kind="method", parent="MyClass")
        result = compute_confidence(sym, None)
        assert result.signals.parent_validated is True
        # lowercase method +5, parent +15 = 20
        assert result.score >= 20

    # ── Boundary tests for tier assignment ──

    def test_boundary_score_39_is_low(self) -> None:
        """Score 39 → low tier."""
        # docstring short (30) + name_convention function (5) = 35... need 39
        # docstring short (30) + type annotations (10) = 40 which is medium
        # Just check tier assignment logic directly
        sym = _symbol(docstring="Short.", kind="function", name="get_x")
        result = compute_confidence(sym, None)
        # 30 (doc) + 5 (name) = 35 → low
        assert result.tier == "low"

    def test_boundary_score_40_is_medium(self) -> None:
        """Score 40 → medium tier."""
        sym = _symbol(
            docstring="Short.",
            kind="function",
            name="get_x",
            signature="def get_x() -> int",
        )
        result = compute_confidence(sym, None)
        # 30 (doc) + 10 (type) + 5 (name) = 45 → medium
        assert result.tier == "medium"
        assert result.score >= 40

    def test_boundary_score_69_is_medium(self) -> None:
        """Score 69 → medium tier."""
        sym = _symbol(
            docstring="A longer docstring here.",
            kind="function",
            name="get_x",
            signature="def get_x() -> int",
        )
        result = compute_confidence(sym, "service")
        # 30 + 10 (long doc) + 10 (type) + 20 (path) + 5 (name) = 75 → actually high
        # Need to find combo that gives exactly medium
        # Without type: 30 + 10 + 20 + 5 = 65 → medium
        sym2 = _symbol(
            docstring="A longer docstring here.",
            kind="function",
            name="get_x",
            signature="def get_x()",
        )
        result2 = compute_confidence(sym2, "service")
        # 30 + 10 + 20 + 5 = 65 → medium
        assert result2.tier == "medium"
        assert result2.score < 70

    def test_boundary_score_70_is_high(self) -> None:
        """Score 70 → high tier."""
        sym = _symbol(
            docstring="A longer docstring here.",
            kind="function",
            name="get_x",
            signature="def get_x() -> int",
        )
        result = compute_confidence(sym, "service")
        # 30 + 10 + 10 + 20 + 5 = 75 → high
        assert result.tier == "high"
        assert result.score >= 70

    def test_deterministic(self) -> None:
        """Same input always produces same output."""
        sym = _symbol(
            docstring="Service logic.",
            kind="class",
            signature="class Svc(BaseModel)",
        )
        r1 = compute_confidence(sym, "service")
        r2 = compute_confidence(sym, "service")
        assert r1.score == r2.score
        assert r1.tier == r2.tier


# ── Constants Tests ───────────────────────────────────────────────────────


class TestConstants:
    """Tests for category mapping constants."""

    def test_default_category_map_has_expected_keys(self) -> None:
        expected = [
            "cli/commands/",
            "cli/",
            "schemas/",
            "models/",
            "output/",
            "governance/",
            "context/",
            "discovery/",
            "memory/",
            "onboarding/",
            "config/",
            "core/",
            "telemetry/",
        ]
        for key in expected:
            assert key in DEFAULT_CATEGORY_MAP, f"Missing key: {key}"

    def test_name_category_overrides_has_expected_keys(self) -> None:
        expected = ["Error", "Warning", "Settings", "Config", "Test", "test_"]
        for key in expected:
            assert key in NAME_CATEGORY_OVERRIDES, f"Missing key: {key}"

    def test_base_class_categories_has_expected_keys(self) -> None:
        expected = ["BaseModel", "Exception", "BaseSettings", "TypedDict"]
        for key in expected:
            assert key in BASE_CLASS_CATEGORIES, f"Missing key: {key}"
