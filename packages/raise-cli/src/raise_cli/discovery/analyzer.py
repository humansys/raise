"""Deterministic analyzer for discovery scan results.

Enriches raw scan output with confidence scores, path-based categories,
hierarchical folding (methods into classes), and module grouping for
parallel AI synthesis. No AI inference required — all signals are deterministic.

Architecture: E13 Discovery improvement (discover-validate-scaling story)

Example:
    >>> from raise_cli.discovery.analyzer import compute_confidence, match_path_category
    >>> from raise_cli.discovery.scanner import Symbol
    >>> sym = Symbol(name="Foo", kind="class", file="src/schemas/foo.py",
    ...             line=1, signature="class Foo(BaseModel)")
    >>> cat = match_path_category(sym.file)
    >>> result = compute_confidence(sym, cat)
    >>> result.tier
    'high'
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, Field

from raise_cli.discovery.scanner import ScanResult, Symbol

# ── Type aliases ──────────────────────────────────────────────────────────

ConfidenceTier = Literal["high", "medium", "low"]

# ── Category mapping constants ────────────────────────────────────────────

DEFAULT_CATEGORY_MAP: dict[str, str] = {
    # Python (raise-cli conventions)
    "cli/commands/": "command",
    "cli/": "utility",
    "schemas/": "schema",
    "models/": "model",
    "output/": "formatter",
    "governance/": "parser",
    "context/": "builder",
    "discovery/": "service",
    "memory/": "service",
    "onboarding/": "service",
    "config/": "utility",
    "core/": "utility",
    "telemetry/": "service",
    # Laravel/PHP
    "Controllers/": "controller",
    "Models/": "model",
    "Middleware/": "middleware",
    "Providers/": "provider",
    "Services/": "service",
    "Requests/": "schema",
    "Resources/": "formatter",
    "routes/": "route",
    "Migrations/": "migration",
    # Svelte/TS/JS
    "components/": "component",
    "stores/": "store",
    "lib/": "utility",
    "utils/": "utility",
    "types/": "schema",
    "hooks/": "utility",
    "api/": "service",
    # C#/.NET (Clean Architecture conventions — leaf directories only,
    # avoid broad layer dirs like Infrastructure/ that shadow more specific ones)
    "Repositories/": "repository",
    "Handlers/": "service",
    "Commands/": "command",
    "Queries/": "query",
    "Validators/": "validator",
}

NAME_CATEGORY_OVERRIDES: dict[str, str] = {
    "Error": "exception",
    "Warning": "exception",
    "Settings": "config",
    "Config": "config",
    "Test": "test",
    "test_": "test",
    # C#/.NET name suffixes
    "Handler": "service",
    "Repository": "repository",
    "RepositoryAsync": "repository",
    "Command": "command",
    "Query": "query",
    "Validator": "validator",
    "Controller": "controller",
    "Middleware": "middleware",
    "Extension": "utility",
    "Factory": "utility",
}

BASE_CLASS_CATEGORIES: dict[str, str] = {
    "BaseModel": "model",
    "Exception": "exception",
    "BaseSettings": "config",
    "TypedDict": "schema",
    # C#/.NET common base classes
    "ControllerBase": "controller",
    "Controller": "controller",
    "DbContext": "service",
    "IRequestHandler": "service",
}

# C# name suffixes that indicate clear semantic intent.
# When present, confidence gets a +15 boost (same as parent context).
CSHARP_SEMANTIC_SUFFIXES: frozenset[str] = frozenset(
    {
        "Handler",
        "Repository",
        "RepositoryAsync",
        "Command",
        "Query",
        "Validator",
        "Controller",
        "Middleware",
        "Factory",
        "Extension",
        "Service",
        "Manager",
    }
)


# ── Pydantic models ──────────────────────────────────────────────────────


class ConfidenceSignals(BaseModel):
    """Deterministic signals used to compute confidence score.

    Each signal maps to a specific condition detected in the source symbol.
    All signals are boolean or simple values — no AI inference involved.
    """

    has_docstring: bool = False
    docstring_length: int = 0
    has_type_annotations: bool = False
    path_matches_convention: bool = False
    known_base_class: str | None = None
    name_follows_convention: bool = False
    parent_validated: bool = False
    has_semantic_suffix: bool = False  # C#: name ends with known semantic suffix


class ConfidenceResult(BaseModel):
    """Confidence assessment for a component.

    Attributes:
        score: Confidence score from 0 to 100.
        tier: Derived tier — high (>=70), medium (40-69), low (<40).
        signals: Individual signals that contributed to the score.
    """

    score: int = Field(ge=0, le=100)
    tier: ConfidenceTier
    signals: ConfidenceSignals


class AnalyzedComponent(BaseModel):
    """A component enriched with deterministic analysis.

    Attributes:
        id: Unique component ID (e.g., "comp-scanner-symbol").
        name: Symbol name.
        kind: Symbol kind (class, function, method, module).
        file: Relative path to source file.
        line: Line number (1-indexed).
        signature: Full signature string.
        module: Python module path (dotted).
        confidence: Confidence assessment.
        auto_category: Deterministic category from path/name conventions.
        auto_purpose: First sentence of docstring, or empty string.
        depends_on: Dependencies extracted from signature.
        internal: Whether this is an internal (underscore-prefixed) symbol.
        methods: Method names if kind=class (folded in).
        docstring: Original docstring, if available.
    """

    id: str
    name: str
    kind: str
    file: str
    line: int
    signature: str
    module: str
    confidence: ConfidenceResult
    auto_category: str
    auto_purpose: str
    depends_on: list[str] = Field(default_factory=list)
    internal: bool = False
    methods: list[str] = Field(default_factory=list)
    docstring: str | None = None


class AnalysisResult(BaseModel):
    """Complete analysis output — deterministic, no AI needed.

    Attributes:
        scan_summary: Aggregate scan statistics.
        confidence_distribution: Count of components per confidence tier.
        categories: Count of components per category.
        components: All analyzed components.
        module_groups: Components grouped by source file (for parallel AI synthesis batches).
    """

    scan_summary: dict[str, int | list[str]]
    confidence_distribution: dict[str, int]
    categories: dict[str, int]
    components: list[AnalyzedComponent]
    module_groups: dict[str, list[str]] = Field(default_factory=dict)


# ── Functions ─────────────────────────────────────────────────────────────


def match_path_category(
    file_path: str,
    category_map: dict[str, str] | None = None,
) -> str | None:
    """Match a file path against convention-based category patterns.

    Uses longest-prefix matching to ensure more specific paths
    (e.g., "cli/commands/") win over less specific ones (e.g., "cli/").

    Args:
        file_path: Relative path to the source file.
        category_map: Custom category map. If None, uses DEFAULT_CATEGORY_MAP.

    Returns:
        Category string if a match is found, None otherwise.

    Example:
        >>> match_path_category("src/raise_cli/cli/commands/discover.py")
        'command'
        >>> match_path_category("src/raise_cli/unknown/foo.py")
    """
    categories = category_map if category_map is not None else DEFAULT_CATEGORY_MAP

    # Match on directory boundaries: pattern must be preceded by "/" or be at
    # the start of the path. This prevents "cli/" matching "raise_cli/".
    # Check all occurrences of the pattern (not just the first).
    best_match: str | None = None
    best_length = 0

    for pattern, category in categories.items():
        # Search all occurrences of pattern in file_path
        start = 0
        while True:
            idx = file_path.find(pattern, start)
            if idx < 0:
                break
            # Ensure directory boundary (preceded by "/" or at start)
            if idx == 0 or file_path[idx - 1] == "/":
                if len(pattern) > best_length:
                    best_match = category
                    best_length = len(pattern)
                break  # Found valid match for this pattern
            start = idx + 1

    return best_match


def compute_confidence(  # noqa: C901 -- multi-factor confidence scoring; inherent complexity
    symbol: Symbol,
    path_category: str | None,
) -> ConfidenceResult:
    """Compute deterministic confidence score for a symbol.

    Scoring signals (total possible = 100):
    - Has docstring: +30
    - Substantial docstring (>20 chars): +10
    - Has type annotations in signature: +10
    - Path matches a known convention: +20
    - Known base class in signature: +10
    - Name follows convention: +5
    - Parent class context (methods): +15
    - Semantic suffix in name [C# only]: +15

    Tier thresholds:
    - High: score >= 70
    - Medium: 40 <= score < 70
    - Low: score < 40

    C# note: XML doc comments (///) are not yet extracted by the scanner.
    Until then, Signal 1 will always be 0 for C#
    symbols. Signals 2, 5, and 7 compensate for this gap.

    Args:
        symbol: The Symbol to score.
        path_category: Category from match_path_category(), or None.

    Returns:
        ConfidenceResult with score, tier, and detailed signals.
    """
    score = 0
    signals = ConfidenceSignals()
    is_csharp = symbol.file.endswith(".cs")

    # Signal 1: Has docstring (+30)
    if symbol.docstring:
        signals.has_docstring = True
        signals.docstring_length = len(symbol.docstring)
        score += 30
        # Bonus for substantial docstring (+10)
        if len(symbol.docstring) > 20:
            score += 10

    # Signal 2: Has type annotations in signature (+10)
    # Python: looks for '->' (return type) or ': ' (param type hints)
    # C#: also counts generic types '<' (e.g. Task<T>, IRequestHandler<Q,R>)
    if is_csharp:
        if ": " in symbol.signature or "<" in symbol.signature:
            signals.has_type_annotations = True
            score += 10
    elif "->" in symbol.signature or ": " in symbol.signature:
        signals.has_type_annotations = True
        score += 10

    # Signal 3: Path matches a known convention (+20)
    if path_category:
        signals.path_matches_convention = True
        score += 20

    # Signal 4: Known base class in signature (+10)
    for base_class in BASE_CLASS_CATEGORIES:
        if base_class in symbol.signature:
            signals.known_base_class = base_class
            score += 10
            break

    # Signal 5: Name follows convention (+5)
    # Python: classes PascalCase, functions/methods snake_case
    # C#: all public symbols are PascalCase (classes AND methods)
    if is_csharp:
        short_name = symbol.name.split(".")[-1]  # strip namespace if present
        if short_name and short_name[0].isupper():
            signals.name_follows_convention = True
            score += 5
    elif (
        symbol.kind == "class"
        and symbol.name
        and symbol.name[0].isupper()
        or symbol.kind in ("function", "method")
        and symbol.name.islower()
    ):
        signals.name_follows_convention = True
        score += 5

    # Signal 6: Parent class context (+15)
    if symbol.parent:
        signals.parent_validated = True
        score += 15

    # Signal 7: Semantic suffix in name [C# only] (+15)
    # Handler, Repository, Command, Query, Validator, Controller, etc.
    # These suffixes are intentional architectural markers in C#/.NET.
    if is_csharp:
        short_name = symbol.name.split(".")[-1]
        if any(short_name.endswith(s) for s in CSHARP_SEMANTIC_SUFFIXES):
            signals.has_semantic_suffix = True
            score += 15

    # Cap at 100
    score = min(score, 100)

    # Tier assignment
    tier: ConfidenceTier
    if score >= 70:
        tier = "high"
    elif score >= 40:
        tier = "medium"
    else:
        tier = "low"

    return ConfidenceResult(score=score, tier=tier, signals=signals)


def extract_first_sentence(docstring: str | None) -> str:
    """Extract the first sentence from a docstring.

    Args:
        docstring: Raw docstring text, or None.

    Returns:
        First sentence (up to first period), or first line if no period.
        Empty string if docstring is None or empty.
    """
    if not docstring:
        return ""
    text = docstring.strip()
    if not text:
        return ""
    # Take first line
    first_line = text.split("\n")[0].strip()
    # If it contains a period, take up to and including the first period
    dot_idx = first_line.find(".")
    if dot_idx >= 0:
        return first_line[: dot_idx + 1]
    return first_line


def determine_category(
    name: str,
    kind: str,
    path_category: str | None,
    base_class: str | None = None,
) -> str:
    """Determine component category using priority chain.

    Priority: name override → base class → path convention → "other".

    Args:
        name: Symbol name.
        kind: Symbol kind (class, function, etc.).
        path_category: Category from match_path_category(), or None.
        base_class: Known base class from confidence signals, or None.

    Returns:
        Category string.
    """
    # Priority 1: Name-based overrides
    for suffix, category in NAME_CATEGORY_OVERRIDES.items():
        if suffix == "test_" and name.startswith("test_"):
            return category
        if suffix == "Test" and kind == "class" and name.startswith("Test"):
            return category
        if suffix not in ("test_", "Test") and name.endswith(suffix):
            return category

    # Priority 2: Base class
    if base_class and base_class in BASE_CLASS_CATEGORIES:
        return BASE_CLASS_CATEGORIES[base_class]

    # Priority 3: Path convention
    if path_category:
        return path_category

    return "other"


_SOURCE_PREFIXES = ("src", "app", "lib")
_CODE_EXTENSIONS = {
    ".py",
    ".php",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".svelte",
    ".cs",
    ".dart",
}


def _file_to_module(file_path: str) -> str:
    """Convert a file path to a dotted module path.

    Strips common source prefixes (src/, app/, lib/) and known code
    extensions (.py, .php, .ts, .tsx, .js, .jsx, .svelte).

    Args:
        file_path: Relative file path (e.g., "src/raise_cli/discovery/scanner.py"
            or "app/Http/Controllers/UserController.php").

    Returns:
        Dotted module path (e.g., "raise_cli.discovery.scanner"
            or "Http.Controllers.UserController").
    """
    # Normalize Windows backslashes before PurePosixPath — paths may arrive
    # with backslashes on Windows or from PHP/C# namespace-derived paths.
    p = PurePosixPath(file_path.replace("\\", "/"))
    parts = list(p.parts)
    # Strip common source prefixes
    if parts and parts[0] in _SOURCE_PREFIXES:
        parts = parts[1:]
    # Remove known code extension from last part
    if parts:
        last = PurePosixPath(parts[-1])
        if last.suffix in _CODE_EXTENSIONS:
            parts[-1] = last.stem
    return ".".join(parts)


def build_hierarchy(symbols: list[Symbol]) -> list[AnalyzedComponent]:
    """Fold methods into their parent classes.

    Classes become single units with a methods list.
    Standalone functions and modules remain individual units.
    Methods with missing parent classes are dropped.

    Args:
        symbols: List of Symbol objects to organize.

    Returns:
        List of AnalyzedComponent units with methods folded into classes.
    """
    class_symbols: dict[str, Symbol] = {}
    class_methods: dict[str, list[Symbol]] = {}

    for s in symbols:
        if s.kind == "class":
            class_symbols[s.name] = s
            class_methods.setdefault(s.name, [])
        elif s.kind == "method" and s.parent:
            class_methods.setdefault(s.parent, []).append(s)

    units: list[AnalyzedComponent] = []

    # Create class units (with methods folded in)
    for class_name, class_sym in class_symbols.items():
        methods = class_methods.get(class_name, [])
        comp_id = f"comp-{_file_to_module(class_sym.file)}-{class_name}"
        units.append(
            AnalyzedComponent(
                id=comp_id,
                name=class_name,
                kind="class",
                file=class_sym.file,
                line=class_sym.line,
                signature=class_sym.signature,
                module=_file_to_module(class_sym.file),
                confidence=ConfidenceResult(
                    score=0, tier="low", signals=ConfidenceSignals()
                ),
                auto_category="other",
                auto_purpose="",
                internal=class_name.startswith("_"),
                methods=[m.name for m in methods],
                docstring=class_sym.docstring,
                depends_on=class_sym.depends_on,
            )
        )

    # Add standalone symbols: everything that's not class or method
    # (exclude-based routing — future kinds automatically become standalone)
    for s in symbols:
        if s.kind not in ("class", "method"):
            # Use "module" as suffix for module-level entries to avoid
            # collisions with same-named functions (e.g., test_version.py
            # has both module "test_version" and function "test_version")
            id_name = "module" if s.kind == "module" else s.name
            comp_id = f"comp-{_file_to_module(s.file)}-{id_name}"
            units.append(
                AnalyzedComponent(
                    id=comp_id,
                    name=s.name,
                    kind=s.kind,
                    file=s.file,
                    line=s.line,
                    signature=s.signature,
                    module=_file_to_module(s.file),
                    confidence=ConfidenceResult(
                        score=0, tier="low", signals=ConfidenceSignals()
                    ),
                    auto_category="other",
                    auto_purpose="",
                    internal=s.name.startswith("_"),
                    methods=[],
                    docstring=s.docstring,
                )
            )

    return units


def _build_hierarchy_with_symbols(
    symbols: list[Symbol],
) -> tuple[list[AnalyzedComponent], dict[str, Symbol]]:
    """Build hierarchy and return a map of component ID → original Symbol.

    Used internally by analyze() to preserve original Symbol objects
    for type-safe confidence scoring.
    """
    units = build_hierarchy(symbols)
    # Build a lookup from symbol name+file to original Symbol
    sym_lookup: dict[tuple[str, str], Symbol] = {}
    for s in symbols:
        sym_lookup[(s.name, s.file)] = s

    symbol_map: dict[str, Symbol] = {}
    for unit in units:
        original = sym_lookup.get((unit.name, unit.file))
        if original:
            symbol_map[unit.id] = original
        else:
            # Fallback: create a minimal Symbol (shouldn't happen normally)
            symbol_map[unit.id] = Symbol(
                name=unit.name,
                kind="class",
                file=unit.file,
                line=unit.line,
                signature=unit.signature,
                docstring=unit.docstring,
            )
    return units, symbol_map


def group_by_module(components: list[AnalyzedComponent]) -> dict[str, list[str]]:
    """Group component IDs by their source module file.

    Each module group becomes a batch for parallel AI synthesis.

    Args:
        components: List of analyzed components.

    Returns:
        Dict mapping file path to list of component IDs.
    """
    groups: dict[str, list[str]] = {}
    for comp in components:
        groups.setdefault(comp.file, []).append(comp.id)
    return groups


def analyze(
    scan_result: ScanResult,
    category_map: dict[str, str] | None = None,
) -> AnalysisResult:
    """Run the full deterministic analysis pipeline.

    Pipeline: filter internal → build hierarchy → score confidence →
    categorize → group by module.

    Args:
        scan_result: Raw scan output from raise discover scan.
        category_map: Optional custom path-to-category mapping.

    Returns:
        AnalysisResult with scored, categorized, module-grouped components.
    """
    all_symbols = scan_result.symbols
    public = [s for s in all_symbols if not s.name.startswith("_")]
    internal = [s for s in all_symbols if s.name.startswith("_")]

    # Build hierarchy (fold methods into classes)
    # Returns (units, symbol_map) so we can reuse original Symbols for scoring
    units, symbol_map = _build_hierarchy_with_symbols(public)

    # Deduplicate IDs — can occur with generated dirs (.astro/, __pycache__/)
    # or Windows paths. Keep first occurrence, warn about duplicates.
    import warnings

    seen_ids: dict[str, str] = {}
    deduped: list[AnalyzedComponent] = []
    for unit in units:
        if unit.id in seen_ids:
            warnings.warn(
                f"Duplicate component ID '{unit.id}' in {unit.file} "
                f"(already seen in {seen_ids[unit.id]}) — skipping duplicate.",
                stacklevel=2,
            )
        else:
            seen_ids[unit.id] = unit.file
            deduped.append(unit)
    units = deduped

    # Score confidence + categorize + extract purpose
    for unit in units:
        path_category = match_path_category(unit.file, category_map)
        original_sym = symbol_map[unit.id]
        conf = compute_confidence(original_sym, path_category)
        unit.confidence = conf
        unit.auto_category = determine_category(
            unit.name, unit.kind, path_category, conf.signals.known_base_class
        )
        unit.auto_purpose = extract_first_sentence(unit.docstring)

    # Aggregate statistics
    tier_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    cat_counts: dict[str, int] = {}
    for unit in units:
        tier_counts[unit.confidence.tier] += 1
        cat_counts[unit.auto_category] = cat_counts.get(unit.auto_category, 0) + 1

    return AnalysisResult(
        scan_summary={
            "files_scanned": scan_result.files_scanned,
            "total_symbols": len(all_symbols),
            "public_symbols": len(public),
            "internal_symbols": len(internal),
            "errors": scan_result.errors,
        },
        confidence_distribution=tier_counts,
        categories=cat_counts,
        components=units,
        module_groups=group_by_module(units),
    )
