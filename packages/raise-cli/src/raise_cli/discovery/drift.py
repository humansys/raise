"""Drift detection for codebase components.

This module detects architectural drift between new/modified code
and established component patterns in the baseline.

Drift types detected:
- Location drift: Files in unexpected directories
- Naming drift: Symbols not following naming conventions
- Documentation drift: Missing docstrings on public APIs

Example:
    >>> from raise_cli.discovery.drift import detect_drift
    >>> warnings = detect_drift(baseline=components, scanned=symbols)
    >>> for w in warnings:
    ...     print(f"{w.severity}: {w.issue}")
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from raise_cli.discovery.scanner import Symbol

# Severity levels for drift warnings
DriftSeverity = Literal["info", "warning", "error"]


class DriftWarning(BaseModel):
    """A warning about architectural drift.

    Attributes:
        file: Path to the file with drift.
        issue: Description of the drift issue.
        severity: Severity level (info, warning, error).
        suggestion: Suggested fix for the issue.

    Examples:
        >>> warning = DriftWarning(
        ...     file="src/new.py",
        ...     issue="File in unexpected location",
        ...     severity="warning",
        ...     suggestion="Move to src/raise_cli/",
        ... )
    """

    file: str = Field(..., description="Path to file with drift")
    issue: str = Field(..., description="Description of the drift issue")
    severity: DriftSeverity = Field(default="warning", description="Severity level")
    suggestion: str = Field(default="", description="Suggested fix")


class BaselineComponentMetadata(BaseModel):
    """Metadata for a baseline component."""

    name: str = Field(default="", description="Symbol name")
    kind: str = Field(
        default="unknown", description="Symbol kind (class, function, etc.)"
    )


class BaselineComponent(BaseModel):
    """A component from the validated baseline.

    Represents a component from work/discovery/components-validated.json
    used for drift detection.

    Attributes:
        source_file: Path to the source file.
        content: Content/docstring of the component.
        metadata: Component metadata (name, kind).
    """

    source_file: str = Field(default="", description="Path to source file")
    content: str = Field(default="", description="Component content/docstring")
    metadata: BaselineComponentMetadata = Field(
        default_factory=BaselineComponentMetadata,
        description="Component metadata",
    )


def _extract_directory_patterns(
    baseline: list[BaselineComponent],
) -> dict[str, set[str]]:
    """Extract directory patterns from baseline by category/kind.

    Groups baseline components by their kind and extracts the directories
    they're typically found in.

    Args:
        baseline: List of validated baseline components.

    Returns:
        Dict mapping kind (class, function, etc.) to set of valid directories.
    """
    patterns: dict[str, set[str]] = {}

    for comp in baseline:
        if comp.source_file:
            kind = comp.metadata.kind
            directory = str(Path(comp.source_file).parent)
            if kind not in patterns:
                patterns[kind] = set()
            patterns[kind].add(directory)

    return patterns


def _extract_naming_patterns(
    baseline: list[BaselineComponent],
) -> dict[str, dict[str, int]]:
    """Extract naming patterns from baseline by kind.

    Looks for common prefixes/suffixes in symbol names and counts occurrences.

    Args:
        baseline: List of validated baseline components.

    Returns:
        Dict mapping kind to dict of prefix -> count.
    """
    patterns: dict[str, dict[str, int]] = {}

    for comp in baseline:
        kind = comp.metadata.kind
        name = comp.metadata.name

        if not name:
            continue

        if kind not in patterns:
            patterns[kind] = {}

        # Extract prefix (e.g., "extract_" from "extract_python_symbols")
        if "_" in name:
            prefix = name.split("_")[0] + "_"
            patterns[kind][prefix] = patterns[kind].get(prefix, 0) + 1

    return patterns


def _check_baseline_has_docstrings(baseline: list[BaselineComponent]) -> bool:
    """Check if baseline components typically have docstrings.

    Args:
        baseline: List of validated baseline components.

    Returns:
        True if majority of baseline components have content (docstrings).
    """
    if not baseline:
        return False

    with_content = sum(1 for c in baseline if c.content)
    return with_content / len(baseline) > 0.5


def _is_private_symbol(name: str) -> bool:
    """Check if symbol is private (starts with underscore).

    Args:
        name: Symbol name.

    Returns:
        True if private (single underscore prefix).
    """
    return name.startswith("_") and not name.startswith("__")


def _normalize_path(path: str) -> str:
    """Normalize path for comparison (remove leading src/, trailing slashes)."""
    normalized = path.strip("/")
    # Handle both "src/module" and "module" as equivalent
    normalized = normalized.removeprefix("src/")
    return normalized


def _check_location_drift(
    symbol: Symbol,
    directory_patterns: dict[str, set[str]],
) -> DriftWarning | None:
    """Check if symbol is in an expected location.

    Args:
        symbol: Scanned symbol to check.
        directory_patterns: Valid directories by kind.

    Returns:
        DriftWarning if location drift detected, None otherwise.
    """
    kind = symbol.kind
    if kind not in directory_patterns:
        return None

    valid_dirs = directory_patterns[kind]
    if not valid_dirs:
        return None

    symbol_dir = _normalize_path(str(Path(symbol.file).parent))

    # Check if symbol is in any valid directory (normalized comparison)
    for valid_dir in valid_dirs:
        normalized_valid = _normalize_path(valid_dir)
        if (
            symbol_dir == normalized_valid
            or symbol_dir.startswith(normalized_valid + "/")
            or normalized_valid.startswith(symbol_dir + "/")
        ):
            return None

    # Location drift detected
    return DriftWarning(
        file=symbol.file,
        issue=f"Location drift: {kind} '{symbol.name}' in unexpected directory",
        severity="warning",
        suggestion=f"Expected directories: {', '.join(sorted(valid_dirs))}",
    )


def _check_naming_drift(
    symbol: Symbol,
    naming_patterns: dict[str, dict[str, int]],
) -> DriftWarning | None:
    """Check if symbol follows naming conventions.

    Args:
        symbol: Scanned symbol to check.
        naming_patterns: Dict mapping kind to dict of prefix -> count.

    Returns:
        DriftWarning if naming drift detected, None otherwise.
    """
    kind = symbol.kind
    name = symbol.name

    # Check class naming (PascalCase)
    if kind == "class" and not name[0].isupper():
        return DriftWarning(
            file=symbol.file,
            issue=f"Naming drift: class '{name}' should use PascalCase",
            severity="warning",
            suggestion=f"Rename to '{name.title().replace('_', '')}'",
        )

    # Check function naming patterns
    if kind == "function" and kind in naming_patterns:
        prefix_counts = naming_patterns[kind]
        if prefix_counts:
            # Check if new function follows any established prefix
            matches_pattern = any(name.startswith(p) for p in prefix_counts)
            if not matches_pattern:
                # Find prefixes that appear 2+ times (established pattern)
                common_prefixes = [
                    p for p, count in prefix_counts.items() if count >= 2
                ]
                if common_prefixes:
                    return DriftWarning(
                        file=symbol.file,
                        issue=f"Naming drift: function '{name}' doesn't follow naming pattern",
                        severity="info",
                        suggestion=f"Consider using prefix: {common_prefixes[0]}",
                    )

    return None


def _check_docstring_drift(
    symbol: Symbol,
    baseline_has_docstrings: bool,
) -> DriftWarning | None:
    """Check if symbol has docstring when baseline expects them.

    Args:
        symbol: Scanned symbol to check.
        baseline_has_docstrings: Whether baseline typically has docstrings.

    Returns:
        DriftWarning if docstring missing when expected, None otherwise.
    """
    if not baseline_has_docstrings:
        return None

    # Only check classes and public functions
    if symbol.kind not in ("class", "function"):
        return None

    if symbol.docstring is None or symbol.docstring.strip() == "":
        return DriftWarning(
            file=symbol.file,
            issue=f"Missing docstring: {symbol.kind} '{symbol.name}' has no documentation",
            severity="warning",
            suggestion="Add a docstring describing purpose and usage",
        )

    return None


def detect_drift(
    baseline: list[BaselineComponent],
    scanned: list[Symbol],
) -> list[DriftWarning]:
    """Detect architectural drift between baseline and new code.

    Compares scanned symbols against established patterns from the baseline
    to identify potential drift issues.

    Args:
        baseline: List of validated baseline components from
            work/discovery/components-validated.json.
        scanned: List of Symbol objects from scanning new/modified files.

    Returns:
        List of DriftWarning objects describing detected issues.

    Examples:
        >>> baseline = [BaselineComponent(metadata=BaselineComponentMetadata(name="Foo", kind="class"))]
        >>> scanned = [Symbol(name="bar", kind="class", ...)]
        >>> warnings = detect_drift(baseline, scanned)
        >>> len(warnings) > 0
        True
    """
    if not baseline or not scanned:
        return []

    warnings: list[DriftWarning] = []

    # Extract patterns from baseline
    directory_patterns = _extract_directory_patterns(baseline)
    naming_patterns = _extract_naming_patterns(baseline)
    baseline_has_docstrings = _check_baseline_has_docstrings(baseline)

    for symbol in scanned:
        # Skip private symbols
        if _is_private_symbol(symbol.name):
            continue

        # Check for location drift
        location_warning = _check_location_drift(symbol, directory_patterns)
        if location_warning:
            warnings.append(location_warning)

        # Check for naming drift
        naming_warning = _check_naming_drift(symbol, naming_patterns)
        if naming_warning:
            warnings.append(naming_warning)

        # Check for docstring drift
        docstring_warning = _check_docstring_drift(symbol, baseline_has_docstrings)
        if docstring_warning:
            warnings.append(docstring_warning)

    return warnings
