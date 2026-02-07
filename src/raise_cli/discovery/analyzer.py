"""Deterministic analyzer for discovery scan results.

Enriches raw scan output with confidence scores, path-based categories,
hierarchical folding (methods into classes), and semantic chunking.
No AI inference required — all signals are deterministic.

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

from typing import Literal

from pydantic import BaseModel, Field

from raise_cli.discovery.scanner import Symbol

# ── Type aliases ──────────────────────────────────────────────────────────

ConfidenceTier = Literal["high", "medium", "low"]

# ── Category mapping constants ────────────────────────────────────────────

DEFAULT_CATEGORY_MAP: dict[str, str] = {
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
}

NAME_CATEGORY_OVERRIDES: dict[str, str] = {
    "Error": "exception",
    "Warning": "exception",
    "Settings": "config",
    "Config": "config",
    "Test": "test",
    "test_": "test",
}

BASE_CLASS_CATEGORIES: dict[str, str] = {
    "BaseModel": "model",
    "Exception": "exception",
    "BaseSettings": "config",
    "TypedDict": "schema",
}


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


class SemanticChunk(BaseModel):
    """A group of related components for batch AI processing.

    Attributes:
        chunk_id: Unique chunk ID (e.g., "chunk-scanner").
        module: File path of the source module.
        module_docstring: Module-level docstring for context.
        package: Python package path (dotted).
        unit_count: Number of component units in this chunk.
        estimated_tokens: Estimated token count for LLM context.
        confidence_tier: Dominant confidence tier in this chunk.
        units: Component IDs belonging to this chunk.
    """

    chunk_id: str
    module: str
    module_docstring: str
    package: str
    unit_count: int
    estimated_tokens: int
    confidence_tier: ConfidenceTier
    units: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Complete analysis output — deterministic, no AI needed.

    Attributes:
        scan_summary: Aggregate scan statistics.
        confidence_distribution: Count of components per confidence tier.
        categories: Count of components per category.
        components: All analyzed components.
        chunks: Semantic chunks for batch processing.
    """

    scan_summary: dict[str, int | list[str]]
    confidence_distribution: dict[str, int]
    categories: dict[str, int]
    components: list[AnalyzedComponent]
    chunks: list[SemanticChunk]


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


def compute_confidence(
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

    Tier thresholds:
    - High: score >= 70
    - Medium: 40 <= score < 70
    - Low: score < 40

    Args:
        symbol: The Symbol to score.
        path_category: Category from match_path_category(), or None.

    Returns:
        ConfidenceResult with score, tier, and detailed signals.
    """
    score = 0
    signals = ConfidenceSignals()

    # Signal 1: Has docstring (+30)
    if symbol.docstring:
        signals.has_docstring = True
        signals.docstring_length = len(symbol.docstring)
        score += 30
        # Bonus for substantial docstring (+10)
        if len(symbol.docstring) > 20:
            score += 10

    # Signal 2: Has type annotations in signature (+10)
    if "->" in symbol.signature or ": " in symbol.signature:
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
    if symbol.kind == "class" and symbol.name and symbol.name[0].isupper():
        signals.name_follows_convention = True
        score += 5
    elif symbol.kind in ("function", "method") and symbol.name.islower():
        signals.name_follows_convention = True
        score += 5

    # Signal 6: Parent class context (+15)
    if symbol.parent:
        signals.parent_validated = True
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
