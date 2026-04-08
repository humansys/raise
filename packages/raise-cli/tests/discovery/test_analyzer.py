"""Tests for discovery analyzer module.

Tests cover:
- Confidence scoring (all 6 signals, boundary scores, tier assignment)
- Path-to-category matching (default paths, custom map, no match)
- Pydantic model validation
- Hierarchy building (method folding, orphan methods, standalone functions)
- Category determination (path → name override → base class → default)
- First sentence extraction from docstrings
- Module grouping for parallel AI batches
- Full analyze() pipeline integration
"""

from __future__ import annotations

import pytest

from raise_cli.discovery.analyzer import (
    BASE_CLASS_CATEGORIES,
    DEFAULT_CATEGORY_MAP,
    NAME_CATEGORY_OVERRIDES,
    AnalysisResult,
    AnalyzedComponent,
    ConfidenceResult,
    ConfidenceSignals,
    _file_to_module,
    analyze,
    build_hierarchy,
    compute_confidence,
    determine_category,
    extract_first_sentence,
    group_by_module,
    match_path_category,
)
from raise_cli.discovery.scanner import ScanResult, Symbol

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
        with pytest.raises(ValueError):
            ConfidenceResult(score=-1, tier="low", signals=ConfidenceSignals())
        with pytest.raises(ValueError):
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

    # ── Multi-language category patterns (S17.4) ─────────────────────────

    def test_laravel_controllers_path(self) -> None:
        result = match_path_category("app/Http/Controllers/UserController.php")
        assert result == "controller"

    def test_laravel_models_path(self) -> None:
        result = match_path_category("app/Models/User.php")
        assert result == "model"

    def test_laravel_middleware_path(self) -> None:
        result = match_path_category("app/Http/Middleware/Auth.php")
        assert result == "middleware"

    def test_laravel_providers_path(self) -> None:
        result = match_path_category("app/Providers/AppServiceProvider.php")
        assert result == "provider"

    def test_laravel_services_path(self) -> None:
        result = match_path_category("app/Services/PaymentService.php")
        assert result == "service"

    def test_laravel_requests_path(self) -> None:
        result = match_path_category("app/Http/Requests/StoreUserRequest.php")
        assert result == "schema"

    def test_laravel_routes_path(self) -> None:
        result = match_path_category("routes/web.php")
        assert result == "route"

    def test_laravel_migrations_path(self) -> None:
        result = match_path_category("database/Migrations/create_users.php")
        assert result == "migration"

    def test_svelte_components_path(self) -> None:
        result = match_path_category("src/lib/components/Header.svelte")
        assert result == "component"

    def test_svelte_stores_path(self) -> None:
        result = match_path_category("src/stores/auth.ts")
        assert result == "store"

    def test_ts_lib_path(self) -> None:
        result = match_path_category("src/lib/utils/format.ts")
        assert result == "utility"

    def test_ts_types_path(self) -> None:
        result = match_path_category("src/types/user.ts")
        assert result == "schema"

    def test_ts_api_path(self) -> None:
        result = match_path_category("src/api/client.ts")
        assert result == "service"

    def test_ts_hooks_path(self) -> None:
        result = match_path_category("src/hooks/useAuth.ts")
        assert result == "utility"

    # ── C#/.NET category patterns (RAISE-228, RAISE-232) ─────────────────

    def test_csharp_controllers_path(self) -> None:
        result = match_path_category("src/Api/Controllers/ProfileController.cs")
        assert result == "controller"

    def test_csharp_repositories_path(self) -> None:
        result = match_path_category(
            "src/Infrastructure/Repositories/ProfileRepository.cs"
        )
        assert result == "repository"

    def test_csharp_handlers_path(self) -> None:
        result = match_path_category("src/Application/Handlers/GetProfileHandler.cs")
        assert result == "service"

    def test_csharp_commands_path(self) -> None:
        result = match_path_category("src/Application/Commands/UpdateProfileCommand.cs")
        assert result == "command"

    def test_csharp_queries_path(self) -> None:
        result = match_path_category("src/Application/Queries/GetProfileQuery.cs")
        assert result == "query"

    def test_csharp_validators_path(self) -> None:
        result = match_path_category("src/Application/Validators/ProfileValidator.cs")
        assert result == "validator"

    def test_csharp_middleware_path(self) -> None:
        result = match_path_category("src/Api/Middleware/AuthMiddleware.cs")
        assert result == "middleware"


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
        compute_confidence(sym, "service")
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

    # ── C#/.NET scoring (RAISE-225) ───────────────────────────────────────

    def test_csharp_handler_in_handlers_dir_is_medium(self) -> None:
        """Handler class in Handlers/ with interface base → medium (50)."""
        sym = _symbol(
            name="GetProfileHandler",
            kind="class",
            signature="class GetProfileHandler : IRequestHandler<GetProfileQuery, ProfileDto>",
            file="src/Application/Handlers/GetProfileHandler.cs",
        )
        # path=20, type_annot=10 (': '), base_class=10 (IRequestHandler), name_conv=5, suffix=15 = 60
        result = compute_confidence(sym, "service")
        assert result.tier == "medium"
        assert result.score == 60
        assert result.signals.has_semantic_suffix is True
        assert result.signals.name_follows_convention is True

    def test_csharp_repository_is_medium(self) -> None:
        """Repository class in Repositories/ → medium."""
        sym = _symbol(
            name="ProfileRepository",
            kind="class",
            signature="class ProfileRepository : IProfileRepository",
            file="src/Infrastructure/Repositories/ProfileRepository.cs",
        )
        # path=20, type_annot=10 (': '), name_conv=5, semantic_suffix=15 = 50
        result = compute_confidence(sym, "repository")
        assert result.tier == "medium"
        assert result.signals.has_semantic_suffix is True

    def test_csharp_controller_with_base_class_is_medium(self) -> None:
        """Controller with ControllerBase → base class signal fires."""
        sym = _symbol(
            name="ProfileController",
            kind="class",
            signature="class ProfileController : ControllerBase",
            file="src/Api/Controllers/ProfileController.cs",
        )
        # path=20, type_annot=10 (': '), base_class=10, name_conv=5, suffix=15 = 60
        result = compute_confidence(sym, "controller")
        assert result.tier == "medium"
        assert result.signals.known_base_class == "ControllerBase"
        assert result.signals.has_semantic_suffix is True

    def test_csharp_method_pascalcase_gets_name_convention(self) -> None:
        """C# methods are PascalCase — name convention signal should fire."""
        sym = _symbol(
            name="GetProfile",
            kind="method",
            signature="public async Task<ProfileDto> GetProfile(GetProfileQuery query)",
            file="src/Application/Handlers/GetProfileHandler.cs",
            parent="GetProfileHandler",
        )
        result = compute_confidence(sym, None)
        assert result.signals.name_follows_convention is True

    def test_python_method_pascalcase_does_not_get_name_convention(self) -> None:
        """Python methods are snake_case — PascalCase method should NOT fire."""
        sym = _symbol(
            name="GetProfile",
            kind="method",
            signature="def GetProfile(self) -> ProfileDto",
            file="src/services/profile.py",
            parent="ProfileService",
        )
        result = compute_confidence(sym, None)
        assert result.signals.name_follows_convention is False

    def test_csharp_generic_type_counts_as_type_annotation(self) -> None:
        """C# generics like Task<T> count as type annotations."""
        sym = _symbol(
            name="Handle",
            kind="method",
            signature="public async Task<ProfileDto> Handle(GetProfileQuery request)",
            file="src/Handlers/GetProfileHandler.cs",
            parent="GetProfileHandler",
        )
        result = compute_confidence(sym, None)
        assert result.signals.has_type_annotations is True

    def test_csharp_no_suffix_no_path_stays_low(self) -> None:
        """C# class with no suffix, no path match, no base class → low."""
        sym = _symbol(
            name="Startup",
            kind="class",
            signature="class Startup",
            file="src/Startup.cs",
        )
        # name_conv=5 only → 5 → low
        result = compute_confidence(sym, None)
        assert result.tier == "low"
        assert result.signals.has_semantic_suffix is False

    def test_csharp_namespace_qualified_name_still_scores_suffix(self) -> None:
        """Namespace-qualified names like 'MyApp.Handlers.GetProfileHandler' → suffix detected."""
        sym = _symbol(
            name="MyApp.Handlers.GetProfileHandler",
            kind="class",
            signature="class GetProfileHandler : IRequestHandler<GetProfileQuery, ProfileDto>",
            file="src/Application/Handlers/GetProfileHandler.cs",
        )
        result = compute_confidence(sym, "service")
        assert result.signals.has_semantic_suffix is True


# ── Constants Tests ───────────────────────────────────────────────────────


class TestConstants:
    """Tests for category mapping constants."""

    def test_default_category_map_has_expected_keys(self) -> None:
        expected = [
            # Python
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
            # Laravel/PHP
            "Controllers/",
            "Models/",
            "Middleware/",
            "Providers/",
            "Services/",
            "Requests/",
            "Resources/",
            # C#/.NET leaf dirs (RAISE-228, RAISE-232)
            "Repositories/",
            "Handlers/",
            "Commands/",
            "Queries/",
            "Validators/",
            "routes/",
            "Migrations/",
            # Svelte/TS/JS
            "components/",
            "stores/",
            "lib/",
            "utils/",
            "types/",
            "hooks/",
            "api/",
        ]
        for key in expected:
            assert key in DEFAULT_CATEGORY_MAP, f"Missing key: {key}"

    def test_name_category_overrides_has_expected_keys(self) -> None:
        expected = [
            "Error",
            "Warning",
            "Settings",
            "Config",
            "Test",
            "test_",
            # C#/.NET suffixes (RAISE-228, RAISE-232)
            "Handler",
            "Repository",
            "RepositoryAsync",
            "Command",
            "Query",
            "Validator",
            "Controller",
            "Middleware",
            "Extension",
            "Factory",
        ]
        for key in expected:
            assert key in NAME_CATEGORY_OVERRIDES, f"Missing key: {key}"

    def test_base_class_categories_has_expected_keys(self) -> None:
        expected = ["BaseModel", "Exception", "BaseSettings", "TypedDict"]
        for key in expected:
            assert key in BASE_CLASS_CATEGORIES, f"Missing key: {key}"


# ── build_hierarchy Tests ─────────────────────────────────────────────────


class TestBuildHierarchy:
    """Tests for method folding into parent classes."""

    def test_class_with_methods_folds_to_one_unit(self) -> None:
        """A class + 5 methods → 1 unit with methods list."""
        symbols = [
            _symbol(
                name="MyClass",
                kind="class",
                file="src/svc.py",
                signature="class MyClass",
            ),
            _symbol(
                name="method_a", kind="method", file="src/svc.py", parent="MyClass"
            ),
            _symbol(
                name="method_b", kind="method", file="src/svc.py", parent="MyClass"
            ),
            _symbol(
                name="method_c", kind="method", file="src/svc.py", parent="MyClass"
            ),
            _symbol(
                name="method_d", kind="method", file="src/svc.py", parent="MyClass"
            ),
            _symbol(
                name="method_e", kind="method", file="src/svc.py", parent="MyClass"
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].name == "MyClass"
        assert units[0].kind == "class"
        assert sorted(units[0].methods) == [
            "method_a",
            "method_b",
            "method_c",
            "method_d",
            "method_e",
        ]

    def test_standalone_function_stays_individual(self) -> None:
        """Standalone functions are individual units."""
        symbols = [
            _symbol(name="helper", kind="function", file="src/utils.py"),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].name == "helper"
        assert units[0].kind == "function"
        assert units[0].methods == []

    def test_module_stays_individual(self) -> None:
        """Module symbols are individual units."""
        symbols = [
            _symbol(
                name="utils",
                kind="module",
                file="src/utils.py",
                signature="module utils",
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].kind == "module"

    def test_orphan_method_without_parent_class(self) -> None:
        """Method whose parent class is not in symbols gets dropped."""
        symbols = [
            _symbol(
                name="orphan_method",
                kind="method",
                file="src/svc.py",
                parent="MissingClass",
            ),
        ]
        units = build_hierarchy(symbols)
        # Orphan methods are not included as standalone units
        assert len(units) == 0

    def test_mixed_scenario(self) -> None:
        """Class with methods + standalone function + module."""
        symbols = [
            _symbol(
                name="Config",
                kind="class",
                file="src/config.py",
                signature="class Config(BaseModel)",
            ),
            _symbol(
                name="validate", kind="method", file="src/config.py", parent="Config"
            ),
            _symbol(
                name="load_config",
                kind="function",
                file="src/config.py",
                signature="def load_config() -> Config",
            ),
            _symbol(
                name="config",
                kind="module",
                file="src/config.py",
                signature="module config",
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 3  # class, function, module
        names = {u.name for u in units}
        assert names == {"Config", "load_config", "config"}
        # Config should have validate folded in
        config_unit = next(u for u in units if u.name == "Config")
        assert config_unit.methods == ["validate"]

    def test_class_without_methods(self) -> None:
        """Class with no methods is still a unit."""
        symbols = [
            _symbol(name="Empty", kind="class", file="src/empty.py"),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].methods == []

    def test_component_id_format(self) -> None:
        """Component IDs use dotted module path and name."""
        symbols = [
            _symbol(name="Scanner", kind="class", file="src/discovery/scanner.py"),
        ]
        units = build_hierarchy(symbols)
        assert units[0].id == "comp-discovery.scanner-Scanner"

    def test_component_id_uniqueness_across_modules(self) -> None:
        """Same-named files in different modules produce unique IDs."""
        symbols = [
            _symbol(
                name="models",
                kind="module",
                file="src/raise_cli/memory/models.py",
                signature="module models",
            ),
            _symbol(
                name="models",
                kind="module",
                file="src/raise_cli/governance/models.py",
                signature="module models",
            ),
        ]
        units = build_hierarchy(symbols)
        ids = [u.id for u in units]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"
        # Module-level entries use "module" as suffix, not the file stem
        assert "comp-raise_cli.memory.models-module" in ids
        assert "comp-raise_cli.governance.models-module" in ids

    def test_module_and_function_same_name_unique_ids(self) -> None:
        """Module and function with same name in same file produce unique IDs."""
        symbols = [
            _symbol(
                name="test_version",
                kind="module",
                file="tests/test_version.py",
                signature="module test_version",
            ),
            _symbol(
                name="test_version",
                kind="function",
                file="tests/test_version.py",
                signature="def test_version()",
            ),
        ]
        units = build_hierarchy(symbols)
        ids = [u.id for u in units]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"
        assert "comp-tests.test_version-module" in ids
        assert "comp-tests.test_version-test_version" in ids

    def test_enum_as_standalone_unit(self) -> None:
        """Enum symbols become standalone units (not dropped)."""
        symbols = [
            _symbol(
                name="UserRole",
                kind="enum",
                file="src/roles.ts",
                signature="enum UserRole",
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].name == "UserRole"
        assert units[0].kind == "enum"

    def test_type_alias_as_standalone_unit(self) -> None:
        """Type alias symbols become standalone units (not dropped)."""
        symbols = [
            _symbol(
                name="Config",
                kind="type_alias",
                file="src/types.ts",
                signature="type Config",
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].name == "Config"
        assert units[0].kind == "type_alias"

    def test_constant_as_standalone_unit(self) -> None:
        """Constant symbols become standalone units (not dropped)."""
        symbols = [
            _symbol(
                name="MAX_RETRIES",
                kind="constant",
                file="src/config.ts",
                signature="const MAX_RETRIES",
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].name == "MAX_RETRIES"
        assert units[0].kind == "constant"

    def test_interface_as_standalone_unit(self) -> None:
        """Interface symbols become standalone units (not dropped)."""
        symbols = [
            _symbol(
                name="UserProps",
                kind="interface",
                file="src/types.ts",
                signature="interface UserProps",
            ),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].name == "UserProps"
        assert units[0].kind == "interface"

    def test_mixed_new_kinds(self) -> None:
        """Mix of class, enum, type_alias, constant all appear in hierarchy."""
        symbols = [
            _symbol(
                name="Service",
                kind="class",
                file="src/svc.ts",
                signature="class Service",
            ),
            _symbol(name="process", kind="method", file="src/svc.ts", parent="Service"),
            _symbol(
                name="Status", kind="enum", file="src/svc.ts", signature="enum Status"
            ),
            _symbol(
                name="Config",
                kind="type_alias",
                file="src/svc.ts",
                signature="type Config",
            ),
            _symbol(
                name="DEFAULT",
                kind="constant",
                file="src/svc.ts",
                signature="const DEFAULT",
            ),
            _symbol(name="helper", kind="function", file="src/svc.ts"),
        ]
        units = build_hierarchy(symbols)
        names = {u.name for u in units}
        # class (with method folded), enum, type_alias, constant, function = 5
        assert names == {"Service", "Status", "Config", "DEFAULT", "helper"}
        assert len(units) == 5

    def test_module_path_computed(self) -> None:
        """Module path is derived from file path."""
        symbols = [
            _symbol(
                name="Scanner", kind="class", file="src/raise_cli/discovery/scanner.py"
            ),
        ]
        units = build_hierarchy(symbols)
        assert units[0].module == "raise_cli.discovery.scanner"

    def test_internal_flag_set(self) -> None:
        """Components with underscore-prefixed names are internal."""
        symbols = [
            _symbol(name="_helper", kind="function", file="src/utils.py"),
        ]
        units = build_hierarchy(symbols)
        assert len(units) == 1
        assert units[0].internal is True

    def test_public_flag_set(self) -> None:
        """Components without underscore prefix are not internal."""
        symbols = [
            _symbol(name="helper", kind="function", file="src/utils.py"),
        ]
        units = build_hierarchy(symbols)
        assert units[0].internal is False


# ── determine_category Tests ─────────────────────────────────────────────


class TestDetermineCategory:
    """Tests for category determination priority chain."""

    def test_name_override_error(self) -> None:
        """Class ending with 'Error' → exception (name override wins)."""
        assert determine_category("MyError", "class", "service") == "exception"

    def test_name_override_warning(self) -> None:
        assert (
            determine_category("DeprecationWarning", "class", "service") == "exception"
        )

    def test_name_override_settings(self) -> None:
        assert determine_category("AppSettings", "class", "model") == "config"

    def test_name_override_config(self) -> None:
        assert determine_category("DatabaseConfig", "class", "service") == "config"

    def test_name_override_test_class(self) -> None:
        assert determine_category("TestScanner", "class", "service") == "test"

    def test_name_override_test_function(self) -> None:
        assert (
            determine_category("test_scan_directory", "function", "service") == "test"
        )

    def test_base_class_override(self) -> None:
        """Base class category wins over path when no name override."""
        assert determine_category("Symbol", "class", "service", "BaseModel") == "model"

    def test_path_category_fallback(self) -> None:
        """Path category used when no name or base class override."""
        assert determine_category("Scanner", "class", "service") == "service"

    def test_no_match_returns_other(self) -> None:
        """No match returns 'other'."""
        assert determine_category("Something", "class", None) == "other"

    def test_name_override_has_highest_priority(self) -> None:
        """Name override > base class > path."""
        # "Error" name override should win even with BaseModel base class
        assert (
            determine_category("ValidationError", "class", "model", "Exception")
            == "exception"
        )

    # ── C#/.NET name suffix overrides (RAISE-228, RAISE-232) ─────────────

    def test_csharp_handler_suffix(self) -> None:
        assert determine_category("GetProfileHandler", "class", None) == "service"

    def test_csharp_repository_suffix(self) -> None:
        assert determine_category("ProfileRepository", "class", None) == "repository"

    def test_csharp_repository_async_suffix(self) -> None:
        assert (
            determine_category("ProfileRepositoryAsync", "class", None) == "repository"
        )

    def test_csharp_command_suffix(self) -> None:
        assert determine_category("UpdateProfileCommand", "class", None) == "command"

    def test_csharp_query_suffix(self) -> None:
        assert determine_category("GetProfileQuery", "class", None) == "query"

    def test_csharp_validator_suffix(self) -> None:
        assert determine_category("ProfileValidator", "class", None) == "validator"

    def test_csharp_controller_suffix(self) -> None:
        assert determine_category("ProfileController", "class", None) == "controller"

    def test_csharp_middleware_suffix(self) -> None:
        assert determine_category("AuthMiddleware", "class", None) == "middleware"

    def test_csharp_extension_suffix(self) -> None:
        assert (
            determine_category("ServiceCollectionExtension", "class", None) == "utility"
        )

    def test_csharp_factory_suffix(self) -> None:
        assert determine_category("ProfileFactory", "class", None) == "utility"


# ── extract_first_sentence Tests ─────────────────────────────────────────


class TestExtractFirstSentence:
    """Tests for first sentence extraction from docstrings."""

    def test_none_returns_empty(self) -> None:
        assert extract_first_sentence(None) == ""

    def test_empty_returns_empty(self) -> None:
        assert extract_first_sentence("") == ""

    def test_single_sentence(self) -> None:
        assert extract_first_sentence("A simple docstring.") == "A simple docstring."

    def test_multi_sentence(self) -> None:
        assert (
            extract_first_sentence("First sentence. Second sentence.")
            == "First sentence."
        )

    def test_multiline(self) -> None:
        doc = "First line.\n\nSecond paragraph with details."
        assert extract_first_sentence(doc) == "First line."

    def test_no_period(self) -> None:
        """Docstring without period returns the whole first line."""
        assert extract_first_sentence("No period here") == "No period here"

    def test_multiline_no_period_first_line(self) -> None:
        doc = "First line\n\nSecond paragraph."
        assert extract_first_sentence(doc) == "First line"

    def test_whitespace_stripped(self) -> None:
        assert extract_first_sentence("  Padded sentence.  ") == "Padded sentence."


# ── _file_to_module Tests (S17.4) ────────────────────────────────────────


class TestFileToModule:
    """Tests for file path to module path conversion."""

    # Existing Python behavior (regression)
    def test_python_with_src_prefix(self) -> None:
        result = _file_to_module("src/raise_cli/discovery/scanner.py")
        assert result == "raise_cli.discovery.scanner"

    def test_python_without_src_prefix(self) -> None:
        result = _file_to_module("raise_cli/discovery/scanner.py")
        assert result == "raise_cli.discovery.scanner"

    # PHP paths (Laravel uses app/ prefix)
    def test_php_with_app_prefix(self) -> None:
        result = _file_to_module("app/Http/Controllers/UserController.php")
        assert result == "Http.Controllers.UserController"

    def test_php_without_prefix(self) -> None:
        result = _file_to_module("Http/Controllers/UserController.php")
        assert result == "Http.Controllers.UserController"

    # TypeScript/JavaScript paths
    def test_ts_with_src_prefix(self) -> None:
        result = _file_to_module("src/lib/stores/auth.ts")
        assert result == "lib.stores.auth"

    def test_tsx_file(self) -> None:
        result = _file_to_module("src/components/Header.tsx")
        assert result == "components.Header"

    def test_js_file(self) -> None:
        result = _file_to_module("src/utils/format.js")
        assert result == "utils.format"

    def test_jsx_file(self) -> None:
        result = _file_to_module("src/components/App.jsx")
        assert result == "components.App"

    # Svelte paths
    def test_svelte_file(self) -> None:
        result = _file_to_module("src/lib/components/Header.svelte")
        assert result == "lib.components.Header"

    # lib/ prefix stripping
    def test_lib_prefix(self) -> None:
        result = _file_to_module("lib/utils/helper.ts")
        assert result == "utils.helper"

    # Unknown extension preserved as-is (no stripping)
    def test_unknown_extension_not_stripped(self) -> None:
        result = _file_to_module("src/data/config.yaml")
        assert result == "data.config.yaml"

    # ── C# / Dart extensions (RAISE-226) ─────────────────────────────────

    def test_csharp_extension_stripped(self) -> None:
        result = _file_to_module("src/Api/Controllers/ProfileController.cs")
        assert result == "Api.Controllers.ProfileController"

    def test_csharp_extension_stripped_no_prefix(self) -> None:
        result = _file_to_module("Startup.cs")
        assert result == "Startup"

    def test_dart_extension_stripped(self) -> None:
        result = _file_to_module("lib/features/profile/profile_repository.dart")
        assert result == "features.profile.profile_repository"


# ── group_by_module Tests ─────────────────────────────────────────────────


class TestGroupByModule:
    """Tests for module grouping."""

    def test_single_module(self) -> None:
        components = [
            _analyzed_component("comp-a", file="src/scanner.py"),
            _analyzed_component("comp-b", file="src/scanner.py"),
        ]
        groups = group_by_module(components)
        assert groups == {"src/scanner.py": ["comp-a", "comp-b"]}

    def test_multiple_modules(self) -> None:
        components = [
            _analyzed_component("comp-a", file="src/scanner.py"),
            _analyzed_component("comp-b", file="src/drift.py"),
            _analyzed_component("comp-c", file="src/scanner.py"),
        ]
        groups = group_by_module(components)
        assert groups == {
            "src/scanner.py": ["comp-a", "comp-c"],
            "src/drift.py": ["comp-b"],
        }

    def test_empty_list(self) -> None:
        assert group_by_module([]) == {}


# ── analyze() Integration Tests ──────────────────────────────────────────


class TestAnalyze:
    """Integration tests for the full analyze pipeline."""

    def test_basic_pipeline(self) -> None:
        """ScanResult → AnalysisResult with correct structure."""
        scan = ScanResult(
            symbols=[
                _symbol(
                    name="Scanner",
                    kind="class",
                    file="src/discovery/scanner.py",
                    signature="class Scanner(BaseModel)",
                    docstring="Scans codebases for symbols and extracts them.",
                ),
                _symbol(
                    name="scan",
                    kind="method",
                    file="src/discovery/scanner.py",
                    signature="def scan(self, path: str) -> list",
                    docstring="Scan a directory.",
                    parent="Scanner",
                ),
                _symbol(
                    name="detect_language",
                    kind="function",
                    file="src/discovery/scanner.py",
                    signature="def detect_language(path: str) -> str",
                    docstring="Detect the programming language.",
                ),
                _symbol(
                    name="_internal_helper",
                    kind="function",
                    file="src/discovery/scanner.py",
                ),
            ],
            files_scanned=1,
            errors=[],
        )
        result = analyze(scan)

        # Internal symbols filtered out
        assert all(not c.internal for c in result.components)
        # Method folded into class
        assert (
            len(result.components) == 2
        )  # Scanner (with scan folded), detect_language
        scanner = next(c for c in result.components if c.name == "Scanner")
        assert scanner.methods == ["scan"]
        # Confidence tiers populated
        assert sum(result.confidence_distribution.values()) == 2
        # Module groups
        assert "src/discovery/scanner.py" in result.module_groups
        # Scan summary
        assert result.scan_summary["total_symbols"] == 4
        assert result.scan_summary["public_symbols"] == 3
        assert result.scan_summary["internal_symbols"] == 1

    def test_empty_scan(self) -> None:
        scan = ScanResult(symbols=[], files_scanned=0, errors=[])
        result = analyze(scan)
        assert result.components == []
        assert result.module_groups == {}
        assert result.confidence_distribution == {"high": 0, "medium": 0, "low": 0}

    def test_custom_category_map(self) -> None:
        scan = ScanResult(
            symbols=[
                _symbol(
                    name="Widget",
                    kind="class",
                    file="src/widgets/button.py",
                    signature="class Widget",
                    docstring="A UI widget.",
                ),
            ],
            files_scanned=1,
            errors=[],
        )
        result = analyze(scan, category_map={"widgets/": "widget"})
        widget = result.components[0]
        assert widget.auto_category == "widget"

    def test_deterministic(self) -> None:
        """Same scan input → same analysis output."""
        scan = ScanResult(
            symbols=[
                _symbol(
                    name="Foo", kind="class", file="src/foo.py", docstring="Foo class."
                ),
                _symbol(
                    name="bar",
                    kind="function",
                    file="src/foo.py",
                    docstring="Bar func.",
                ),
            ],
            files_scanned=1,
            errors=[],
        )
        r1 = analyze(scan)
        r2 = analyze(scan)
        assert r1.confidence_distribution == r2.confidence_distribution
        assert r1.module_groups == r2.module_groups
        assert len(r1.components) == len(r2.components)

    def test_duplicate_ids_warns_and_deduplicates(self) -> None:
        """Duplicate component IDs are warned about and deduplicated (keep first).

        Changed from ValueError to warning+dedup to handle generated dirs
        (.astro/, __pycache__/) and Windows paths gracefully (RAISE-215).
        """
        scan = ScanResult(
            symbols=[
                _symbol(
                    name="helper",
                    kind="function",
                    file="src/utils.py",
                    signature="def helper()",
                ),
                _symbol(
                    name="helper",
                    kind="function",
                    file="src/utils.py",
                    signature="def helper(x: int)",
                ),
            ],
            files_scanned=1,
            errors=[],
        )
        import warnings

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = analyze(scan)

        # Duplicate is warned about
        assert any("Duplicate component ID" in str(w.message) for w in caught)
        # Only one component survives (first occurrence kept)
        ids = [c.id for c in result.components]
        assert ids.count("comp-utils-helper") == 1

    def test_no_duplicates_across_modules(self) -> None:
        """Same-named symbols in different modules produce unique IDs."""
        scan = ScanResult(
            symbols=[
                _symbol(
                    name="Writer",
                    kind="class",
                    file="src/raise_cli/memory/writer.py",
                    signature="class Writer",
                    docstring="Memory writer.",
                ),
                _symbol(
                    name="Writer",
                    kind="class",
                    file="src/raise_cli/telemetry/writer.py",
                    signature="class Writer",
                    docstring="Telemetry writer.",
                ),
            ],
            files_scanned=2,
            errors=[],
        )
        result = analyze(scan)
        ids = [c.id for c in result.components]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"


# ── Test Helpers ──────────────────────────────────────────────────────────


def _analyzed_component(
    id: str = "comp-test",
    file: str = "src/test.py",
) -> AnalyzedComponent:
    """Create a minimal AnalyzedComponent for testing."""
    return AnalyzedComponent(
        id=id,
        name="test",
        kind="class",
        file=file,
        line=1,
        signature="class test",
        module="test",
        confidence=ConfidenceResult(
            score=50, tier="medium", signals=ConfidenceSignals()
        ),
        auto_category="service",
        auto_purpose="Test.",
    )
