"""Convention detection for brownfield projects.

Detects code style, naming, and structure conventions by analyzing source files
and reporting findings with confidence scores.
"""

from __future__ import annotations

import re
import time
from collections import Counter
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from raise_cli.core.files import should_exclude_dir


class Confidence(StrEnum):
    """Confidence level for a detected convention.

    Confidence is based on both consistency ratio and sample size:
    - HIGH: >90% consistency AND >10 samples
    - MEDIUM: 70-90% consistency OR 5-10 samples
    - LOW: <70% consistency OR <5 samples
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IndentationConvention(BaseModel):
    """Detected indentation convention.

    Attributes:
        style: Whether the project uses spaces, tabs, or mixed.
        width: Indentation width in spaces (None if tabs or mixed).
        confidence: How confident we are in this detection.
        sample_count: Number of files analyzed.
        consistent_count: Number of files matching the detected convention.
    """

    style: Literal["spaces", "tabs", "mixed"]
    width: int | None = None
    confidence: Confidence
    sample_count: int
    consistent_count: int


class QuoteConvention(BaseModel):
    """Detected string quote style convention.

    Attributes:
        style: Whether single quotes, double quotes, or mixed.
        confidence: How confident we are in this detection.
        sample_count: Number of string literals analyzed.
        consistent_count: Number matching the detected style.
    """

    style: Literal["single", "double", "mixed"]
    confidence: Confidence
    sample_count: int
    consistent_count: int


class LineLengthConvention(BaseModel):
    """Detected line length convention.

    Attributes:
        max_length: The 80th percentile line length (typical max).
        confidence: How confident we are in this detection.
        sample_count: Number of lines analyzed.
    """

    max_length: int
    confidence: Confidence
    sample_count: int


class StyleConventions(BaseModel):
    """Code style conventions detected in the project.

    Groups indentation, quote style, and line length conventions.
    """

    indentation: IndentationConvention
    quote_style: QuoteConvention
    line_length: LineLengthConvention


class NamingConvention(BaseModel):
    """Detected naming pattern for a symbol type.

    Attributes:
        pattern: The detected naming pattern (snake_case, PascalCase, etc.).
        confidence: How confident we are in this detection.
        sample_count: Number of symbols analyzed.
        consistent_count: Number matching the detected pattern.
    """

    pattern: Literal[
        "snake_case", "camelCase", "PascalCase", "UPPER_SNAKE_CASE", "mixed"
    ]
    confidence: Confidence
    sample_count: int
    consistent_count: int


class NamingConventions(BaseModel):
    """Naming conventions by symbol type.

    Tracks separate conventions for functions, classes, and constants
    since each typically follows different patterns.
    """

    functions: NamingConvention
    classes: NamingConvention
    constants: NamingConvention


class StructureConventions(BaseModel):
    """Project structure conventions.

    Attributes:
        source_dir: Detected source root (e.g., "src/mypackage").
        test_dir: Detected test directory (e.g., "tests").
        has_src_layout: Whether using the src/ layout pattern.
        common_patterns: Recurring directory patterns found.
    """

    source_dir: str | None = None
    test_dir: str | None = None
    has_src_layout: bool = False
    common_patterns: list[str] = Field(default_factory=list)


class ConventionResult(BaseModel):
    """Complete result of convention detection.

    This is the main return type from detect_conventions().

    Attributes:
        style: Code style conventions (indentation, quotes, line length).
        naming: Naming conventions by symbol type.
        structure: Project structure conventions.
        overall_confidence: Lowest confidence across key conventions.
        files_analyzed: Total Python files analyzed.
        analysis_time_ms: Time taken for analysis in milliseconds.
    """

    style: StyleConventions
    naming: NamingConventions
    structure: StructureConventions
    overall_confidence: Confidence
    files_analyzed: int
    analysis_time_ms: int = 0


# =============================================================================
# Confidence Calculation
# =============================================================================


def calculate_confidence(consistent: int, total: int) -> Confidence:
    """Calculate confidence based on consistency ratio and sample size.

    The confidence algorithm accounts for both how consistent the codebase is
    AND how much data we have to make that determination:

    1. <5 samples → always LOW (insufficient data to draw conclusions)
    2. 5-10 samples → cap at MEDIUM (small sample, even if 100% consistent)
    3. >10 samples → ratio determines confidence:
       - >90% consistent → HIGH
       - 70-90% consistent → MEDIUM
       - <70% consistent → LOW

    Args:
        consistent: Number of samples matching the detected convention.
        total: Total number of samples analyzed.

    Returns:
        Confidence level (HIGH, MEDIUM, or LOW).

    Examples:
        >>> calculate_confidence(4, 4)  # 100% but only 4 samples
        Confidence.LOW
        >>> calculate_confidence(10, 10)  # 100% but only 10 samples
        Confidence.MEDIUM
        >>> calculate_confidence(95, 100)  # 95% with 100 samples
        Confidence.HIGH
    """
    # Edge case: no samples
    if total == 0:
        return Confidence.LOW

    # Rule 1: <5 samples = insufficient data
    if total < 5:
        return Confidence.LOW

    ratio = consistent / total

    # Rule 2: 5-10 samples = cap at MEDIUM
    if total <= 10:
        return Confidence.MEDIUM if ratio >= 0.7 else Confidence.LOW

    # Rule 3: >10 samples = ratio determines confidence
    if ratio > 0.9:
        return Confidence.HIGH
    if ratio >= 0.7:
        return Confidence.MEDIUM
    return Confidence.LOW


# =============================================================================
# File Collection
# =============================================================================


def collect_python_files(directory: Path, max_files: int = 200) -> list[Path]:
    """Collect Python files from a directory recursively.

    Args:
        directory: Root directory to scan.
        max_files: Maximum number of files to return (for performance).

    Returns:
        List of paths to Python files.
    """
    if not directory.is_dir():
        return []

    files: list[Path] = []

    def _collect(path: Path) -> None:
        if len(files) >= max_files:
            return
        try:
            for item in path.iterdir():
                if len(files) >= max_files:
                    return
                if item.is_dir():
                    if not should_exclude_dir(item):
                        _collect(item)
                elif item.is_file() and item.suffix == ".py":
                    files.append(item)
        except PermissionError:
            pass

    _collect(directory)
    return files


# =============================================================================
# Style Detection
# =============================================================================


def _get_first_indent(file_path: Path) -> tuple[str, int] | None:
    """Get the first indentation character and width from a file.

    Returns:
        Tuple of (char, width) where char is 'tab' or 'space', or None if no indent found.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return None

    for line in content.splitlines():
        if not line or line[0] not in (" ", "\t"):
            continue
        if line[0] == "\t":
            return ("tab", 0)
        # Count leading spaces
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if indent > 0:
            return ("space", indent)

    return None


def _determine_indent_style(
    tabs_count: int, spaces_count: int, indent_widths: list[int]
) -> tuple[Literal["spaces", "tabs", "mixed"], int | None, int]:
    """Determine indentation style from collected samples.

    Returns:
        Tuple of (style, width, consistent_count).
    """
    if tabs_count > 0 and spaces_count > 0:
        return ("mixed", None, 0)

    if tabs_count > spaces_count:
        return ("tabs", None, tabs_count)

    # Spaces style - find most common width
    if indent_widths:
        width_counts = Counter(indent_widths)
        width = width_counts.most_common(1)[0][0]
        consistent = width_counts[width]
        return ("spaces", width, consistent)

    return ("spaces", 4, spaces_count)


def detect_indentation(files: list[Path]) -> IndentationConvention:
    """Detect indentation convention from Python files.

    Analyzes the first indented line of each file to determine
    whether spaces or tabs are used, and what width.

    Args:
        files: List of Python files to analyze.

    Returns:
        IndentationConvention with detected style and confidence.
    """
    indent_widths: list[int] = []
    tabs_count = 0
    spaces_count = 0

    for file_path in files:
        result = _get_first_indent(file_path)
        if result is None:
            continue
        char_type, width = result
        if char_type == "tab":
            tabs_count += 1
        else:
            spaces_count += 1
            indent_widths.append(width)

    total = tabs_count + spaces_count
    if total == 0:
        return IndentationConvention(
            style="spaces",
            width=4,
            confidence=Confidence.LOW,
            sample_count=0,
            consistent_count=0,
        )

    style, width, consistent = _determine_indent_style(
        tabs_count, spaces_count, indent_widths
    )
    confidence = calculate_confidence(consistent, total)

    return IndentationConvention(
        style=style,
        width=width,
        confidence=confidence,
        sample_count=total,
        consistent_count=consistent,
    )


# Regex to find string literals (simple version - not perfect but good enough)
STRING_PATTERN = re.compile(r"""(?<!\\)(["'])(?:(?!\1|\\).|\\.)*\1""")


def detect_quotes(files: list[Path]) -> QuoteConvention:
    """Detect quote style convention from Python files.

    Analyzes string literals to determine whether single or double
    quotes are preferred.

    Args:
        files: List of Python files to analyze.

    Returns:
        QuoteConvention with detected style and confidence.
    """
    single_count = 0
    double_count = 0

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            # Skip docstrings (triple quotes) and find regular strings
            # Simple heuristic: count ' vs " as string delimiters
            for match in STRING_PATTERN.finditer(content):
                quote_char = match.group(1)
                if quote_char == "'":
                    single_count += 1
                else:
                    double_count += 1
        except (OSError, UnicodeDecodeError):
            continue

    total = single_count + double_count

    if total == 0:
        return QuoteConvention(
            style="double",
            confidence=Confidence.LOW,
            sample_count=0,
            consistent_count=0,
        )

    # Determine style
    if single_count > 0 and double_count > 0:
        ratio = max(single_count, double_count) / total
        if ratio < 0.7:
            style: Literal["single", "double", "mixed"] = "mixed"
            consistent = 0
        elif single_count > double_count:
            style = "single"
            consistent = single_count
        else:
            style = "double"
            consistent = double_count
    elif single_count > double_count:
        style = "single"
        consistent = single_count
    else:
        style = "double"
        consistent = double_count

    confidence = calculate_confidence(consistent, total)

    return QuoteConvention(
        style=style,
        confidence=confidence,
        sample_count=total,
        consistent_count=consistent,
    )


def detect_line_length(files: list[Path]) -> LineLengthConvention:
    """Detect line length convention from Python files.

    Uses the 80th percentile of line lengths as the typical maximum.

    Args:
        files: List of Python files to analyze.

    Returns:
        LineLengthConvention with detected max length and confidence.
    """
    line_lengths: list[int] = []

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                # Skip empty lines and comments for better signal
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    line_lengths.append(len(line))
        except (OSError, UnicodeDecodeError):
            continue

    if not line_lengths:
        return LineLengthConvention(
            max_length=88,
            confidence=Confidence.LOW,
            sample_count=0,
        )

    # Calculate 80th percentile
    line_lengths.sort()
    idx = int(len(line_lengths) * 0.8)
    max_length = line_lengths[idx] if idx < len(line_lengths) else line_lengths[-1]

    # Round to common values (79, 88, 100, 120)
    common_lengths = [79, 88, 100, 120]
    max_length = min(common_lengths, key=lambda x: abs(x - max_length))

    # Confidence based on sample size
    confidence = calculate_confidence(len(line_lengths), len(line_lengths))

    return LineLengthConvention(
        max_length=max_length,
        confidence=confidence,
        sample_count=len(line_lengths),
    )


# =============================================================================
# Naming Detection
# =============================================================================


# Regex patterns for extracting names
FUNCTION_PATTERN = re.compile(r"^def\s+([a-zA-Z_]\w*)\s*\(", re.MULTILINE)
CLASS_PATTERN = re.compile(r"^class\s+([a-zA-Z_]\w*)\s*[\(:]", re.MULTILINE)
CONSTANT_PATTERN = re.compile(r"^([A-Z][A-Z0-9_]*)\s*[=:]", re.MULTILINE)


def classify_name(
    name: str,
) -> Literal["snake_case", "camelCase", "PascalCase", "UPPER_SNAKE_CASE", "mixed"]:
    """Classify a name into its naming pattern.

    Args:
        name: The identifier name to classify.

    Returns:
        The detected naming pattern.
    """
    # Skip private/dunder names for classification
    if name.startswith("_"):
        name = name.lstrip("_")
        if not name:
            return "snake_case"

    # UPPER_SNAKE_CASE requires underscore OR multiple uppercase chars
    # (single uppercase letter like "X" is PascalCase)
    if re.match(r"^[A-Z][A-Z0-9_]*$", name) and (len(name) > 1 or "_" in name):
        return "UPPER_SNAKE_CASE"
    if re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
        return "PascalCase"
    if re.match(r"^[a-z][a-z0-9_]*$", name):
        return "snake_case"
    if re.match(r"^[a-z][a-zA-Z0-9]*$", name):
        return "camelCase"
    return "mixed"


def _detect_naming_for_pattern(
    files: list[Path],
    pattern: re.Pattern[str],
    expected_style: Literal[
        "snake_case", "camelCase", "PascalCase", "UPPER_SNAKE_CASE", "mixed"
    ],
) -> NamingConvention:
    """Detect naming convention for symbols matching a pattern.

    Args:
        files: List of Python files to analyze.
        pattern: Regex pattern to extract symbol names.
        expected_style: The expected naming style for this symbol type.

    Returns:
        NamingConvention with detected pattern and confidence.
    """
    style_counts: Counter[str] = Counter()

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for match in pattern.finditer(content):
                name = match.group(1)
                style = classify_name(name)
                style_counts[style] += 1
        except (OSError, UnicodeDecodeError):
            continue

    total = sum(style_counts.values())

    if total == 0:
        return NamingConvention(
            pattern=expected_style,
            confidence=Confidence.LOW,
            sample_count=0,
            consistent_count=0,
        )

    # Find most common style
    most_common = style_counts.most_common(1)[0]
    detected_pattern = most_common[0]
    consistent = most_common[1]

    # Ensure it's a valid literal type
    valid_patterns: list[
        Literal["snake_case", "camelCase", "PascalCase", "UPPER_SNAKE_CASE", "mixed"]
    ] = ["snake_case", "camelCase", "PascalCase", "UPPER_SNAKE_CASE", "mixed"]
    if detected_pattern not in valid_patterns:
        detected_pattern = "mixed"

    confidence = calculate_confidence(consistent, total)

    return NamingConvention(
        pattern=detected_pattern,  # type: ignore[arg-type]
        confidence=confidence,
        sample_count=total,
        consistent_count=consistent,
    )


def detect_naming(files: list[Path]) -> NamingConventions:
    """Detect naming conventions for functions, classes, and constants.

    Args:
        files: List of Python files to analyze.

    Returns:
        NamingConventions with detected patterns for each symbol type.
    """
    return NamingConventions(
        functions=_detect_naming_for_pattern(files, FUNCTION_PATTERN, "snake_case"),
        classes=_detect_naming_for_pattern(files, CLASS_PATTERN, "PascalCase"),
        constants=_detect_naming_for_pattern(
            files, CONSTANT_PATTERN, "UPPER_SNAKE_CASE"
        ),
    )


# =============================================================================
# Structure Detection
# =============================================================================


def detect_structure(directory: Path) -> StructureConventions:  # noqa: C901 -- complexity 14, refactor deferred
    """Detect project structure conventions.

    Identifies source directories, test directories, and common patterns.

    Args:
        directory: Root directory to analyze.

    Returns:
        StructureConventions with detected structure.
    """
    source_dir: str | None = None
    test_dir: str | None = None
    has_src_layout = False
    common_patterns: list[str] = []

    # Check for src/ layout
    src_dir = directory / "src"
    if src_dir.is_dir():
        has_src_layout = True
        # Find package inside src/
        for item in src_dir.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and (item / "__init__.py").exists()
            ):
                source_dir = f"src/{item.name}"
                break
        if not source_dir:
            source_dir = "src"

    # If no src/, look for package at root
    if not source_dir:
        for item in directory.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and item.name not in {"tests", "test", "docs", "build", "dist"}
                and (item / "__init__.py").exists()
            ):
                source_dir = item.name
                break

    # Find test directory
    for test_name in ["tests", "test"]:
        test_path = directory / test_name
        if test_path.is_dir():
            test_dir = test_name
            break

    # Find common patterns (subdirectories that appear in source)
    if source_dir:
        source_path = directory / source_dir
        if source_path.is_dir():
            for item in source_path.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    common_patterns.append(f"{item.name}/")

    return StructureConventions(
        source_dir=source_dir,
        test_dir=test_dir,
        has_src_layout=has_src_layout,
        common_patterns=sorted(common_patterns)[:10],  # Limit to top 10
    )


# =============================================================================
# Main Detection Function
# =============================================================================


def detect_conventions(directory: Path) -> ConventionResult:
    """Detect all conventions in a project directory.

    This is the main entry point for convention detection. It analyzes
    Python files to detect code style, naming, and structure conventions.

    Args:
        directory: Root directory of the project to analyze.

    Returns:
        ConventionResult with all detected conventions and confidence scores.

    Example:
        >>> result = detect_conventions(Path("/path/to/project"))
        >>> print(result.style.indentation.width)  # e.g., 4
        >>> print(result.naming.functions.pattern)  # e.g., "snake_case"
    """
    start_time = time.perf_counter()

    # Collect Python files
    files = collect_python_files(directory)

    # Detect style conventions
    indentation = detect_indentation(files)
    quotes = detect_quotes(files)
    line_length = detect_line_length(files)

    style = StyleConventions(
        indentation=indentation,
        quote_style=quotes,
        line_length=line_length,
    )

    # Detect naming conventions
    naming = detect_naming(files)

    # Detect structure conventions
    structure = detect_structure(directory)

    # Calculate overall confidence (lowest of key conventions)
    key_confidences = [
        indentation.confidence,
        naming.functions.confidence,
    ]

    if Confidence.LOW in key_confidences:
        overall = Confidence.LOW
    elif Confidence.MEDIUM in key_confidences:
        overall = Confidence.MEDIUM
    else:
        overall = Confidence.HIGH

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return ConventionResult(
        style=style,
        naming=naming,
        structure=structure,
        overall_confidence=overall,
        files_analyzed=len(files),
        analysis_time_ms=elapsed_ms,
    )
