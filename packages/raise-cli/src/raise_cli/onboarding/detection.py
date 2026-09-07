"""Project type detection for RaiSE initialization.

Detects whether a directory is greenfield (no code) or brownfield (existing code)
by counting source code files while excluding common non-project directories.
Also detects dominant language and suggests toolchain commands.
"""

from __future__ import annotations

import os
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from raise_cli.core.files import EXCLUDED_DIRS, should_exclude_dir
from raise_cli.project_config.types import ProjectType

if TYPE_CHECKING:
    from raise_cli.onboarding.manifest import AppInfo

# Re-export for backward compatibility
__all__ = [
    "CODE_EXTENSIONS",
    "EXCLUDED_DIRS",
    "LANGUAGE_TOOLCHAIN",
    "DetectedValue",
    "DetectionTier",
    "ProjectType",
    "DetectionResult",
    "ToolchainInfo",
    "detect_apps",
    "detect_base_branch",
    "detect_ci",
    "detect_language",
    "detect_project_conventions",
    "detect_project_type",
    "detect_scm",
]

DetectionTier = Literal["explicit", "observed", "suggested", "default"]

# Common code file extensions to detect
CODE_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Python
        ".py",
        # JavaScript/TypeScript
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        # JVM
        ".java",
        ".kt",
        ".scala",
        # Systems
        ".c",
        ".cpp",
        ".cc",
        ".cxx",
        ".h",
        ".hpp",
        ".rs",
        ".go",
        # Scripting
        ".rb",
        ".php",
        ".pl",
        ".pm",
        # .NET
        ".cs",
        ".fs",
        ".vb",
        # Other
        ".swift",
        ".m",
        ".mm",
        ".lua",
        ".r",
        ".R",
        ".jl",
        ".dart",
        ".ex",
        ".exs",
        ".erl",
        ".hrl",
        ".clj",
        ".cljs",
        ".elm",
        ".hs",
    }
)


# Map file extensions to language names
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".cs": "csharp",
    ".fs": "fsharp",
    ".vb": "vb",
    ".java": "java",
    ".kt": "kotlin",
    ".scala": "scala",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".dart": "dart",
    ".swift": "swift",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hrl": "erlang",
    ".hs": "haskell",
    ".elm": "elm",
    ".clj": "clojure",
    ".cljs": "clojure",
    ".jl": "julia",
    ".lua": "lua",
    ".r": "r",
    ".R": "r",
    ".pl": "perl",
    ".pm": "perl",
    ".m": "objective-c",
    ".mm": "objective-c",
}


@dataclass(frozen=True)
class ToolchainInfo:
    """Suggested toolchain commands for a language.

    Attributes:
        language: Detected language name.
        test_command: Suggested test runner command.
        lint_command: Suggested linter command, if known.
        type_check_command: Suggested type checker command, if known.
        format_command: Suggested formatter check command, if known.
    """

    language: str
    test_command: str | None = None
    lint_command: str | None = None
    type_check_command: str | None = None
    format_command: str | None = None


# Default toolchain commands per language
LANGUAGE_TOOLCHAIN: dict[str, ToolchainInfo] = {
    "python": ToolchainInfo(
        language="python",
        test_command="uv run pytest --tb=short",
        lint_command="uv run ruff check",
        type_check_command="uv run pyright",
        format_command="uv run ruff format --check",
    ),
    "typescript": ToolchainInfo(
        language="typescript",
        test_command="npx vitest run",
        lint_command="npx eslint .",
        type_check_command="npx tsc --noEmit",
        format_command="npx prettier --check .",
    ),
    "javascript": ToolchainInfo(
        language="javascript",
        test_command="npx vitest run",
        lint_command="npx eslint .",
        format_command="npx prettier --check .",
    ),
    "csharp": ToolchainInfo(
        language="csharp",
        test_command="dotnet test --verbosity quiet",
        lint_command="dotnet format --verify-no-changes",
        type_check_command="dotnet build --no-restore",
        format_command="dotnet format --verify-no-changes",
    ),
    "java": ToolchainInfo(
        language="java",
        test_command="mvn test",
        lint_command="mvn checkstyle:check",
        format_command="mvn spotless:check",
    ),
    "go": ToolchainInfo(
        language="go",
        test_command="go test ./...",
        lint_command="golangci-lint run",
        type_check_command="go vet ./...",
        format_command="gofmt -l .",
    ),
    "rust": ToolchainInfo(
        language="rust",
        test_command="cargo test",
        lint_command="cargo clippy",
        type_check_command="cargo check",
        format_command="cargo fmt --check",
    ),
    "php": ToolchainInfo(
        language="php",
        test_command="vendor/bin/phpunit",
        lint_command="vendor/bin/php-cs-fixer fix --dry-run",
        type_check_command="vendor/bin/phpstan analyse",
        format_command="vendor/bin/php-cs-fixer fix --dry-run",
    ),
    "dart": ToolchainInfo(
        language="dart",
        test_command="flutter test",
        lint_command="dart fix --dry-run",
        type_check_command="dart analyze",
        format_command="dart format --set-exit-if-changed .",
    ),
    "ruby": ToolchainInfo(
        language="ruby",
        test_command="bundle exec rspec",
        lint_command="bundle exec rubocop",
        format_command="bundle exec rubocop --auto-correct-all --dry-run",
    ),
    "kotlin": ToolchainInfo(
        language="kotlin",
        test_command="./gradlew test",
        lint_command="./gradlew ktlintCheck",
        format_command="./gradlew ktlintCheck",
    ),
    "swift": ToolchainInfo(
        language="swift",
        test_command="swift test",
        lint_command="swiftlint",
        format_command="swiftformat --lint .",
    ),
    "elixir": ToolchainInfo(
        language="elixir",
        test_command="mix test",
        lint_command="mix credo",
        type_check_command="mix dialyzer",
        format_command="mix format --check-formatted",
    ),
}


@dataclass(frozen=True)
class DetectionResult:
    """Result of project type detection.

    Attributes:
        project_type: Whether the project is greenfield or brownfield.
        code_file_count: Number of code files detected.
        language: Dominant language detected, if any.
        toolchain: Suggested toolchain commands for the detected language.
    """

    project_type: ProjectType
    code_file_count: int
    language: str | None = None
    toolchain: ToolchainInfo | None = None


@dataclass(frozen=True)
class DetectedValue[T]:
    """A detected value paired with its source and confidence tier.

    High-confidence detection only: a value with tier "default"/value=None
    means no signal was observed — never a statistical or LLM guess
    (RAISE-16561).

    Attributes:
        value: The detected value, or None when nothing was observed.
        source: Where the value came from (e.g. a git command or file path).
        tier: Confidence tier — explicit/observed/suggested/default.
    """

    value: T | None
    source: str | None = None
    tier: DetectionTier = "default"


_GIT_TIMEOUT_S = 10.0


def _run_git(directory: Path, *args: str) -> str | None:
    """Run git in *directory*; return stripped stdout, or None on failure.

    Mirrors the shape of session/open_service.run_git and
    git/branch_guard.current_branch, kept local to this module so detection
    stays in its own tier without an upward import (RAISE-16462).
    """
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
            env={**os.environ, "LC_ALL": "C", "LANGUAGE": "en"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    stdout = proc.stdout.strip()
    return stdout or None


_SCM_HOST_MARKERS: tuple[tuple[str, str], ...] = (
    ("github.com", "github"),
    ("gitlab", "gitlab"),
)


def detect_scm(directory: Path) -> DetectedValue[str]:
    """Detect the SCM provider from the ``origin`` git remote.

    High-confidence only: maps a known host in the origin remote URL to a
    provider name. No inference when no remote is configured or the host
    doesn't match a known marker.

    Args:
        directory: Repository root to inspect.

    Returns:
        DetectedValue with tier "observed" when a known provider is found,
        else tier "default" with value=None.
    """
    url = _run_git(directory, "remote", "get-url", "origin")
    if not url:
        return DetectedValue(value=None)

    lowered = url.lower()
    for marker, provider in _SCM_HOST_MARKERS:
        if marker in lowered:
            return DetectedValue(
                value=provider, source="git remote origin", tier="observed"
            )
    return DetectedValue(value=None)


def detect_base_branch(directory: Path) -> DetectedValue[str]:
    """Detect the base branch from ``origin/HEAD``.

    High-confidence only: reads the symbolic ref that a normal clone (or
    ``git remote set-head origin -a``) already resolved. No inference when
    origin/HEAD is unset.

    Args:
        directory: Repository root to inspect.

    Returns:
        DetectedValue with tier "observed" when origin/HEAD resolves, else
        tier "default" with value=None.
    """
    ref = _run_git(directory, "symbolic-ref", "refs/remotes/origin/HEAD")
    if not ref:
        return DetectedValue(value=None)

    branch = ref.removeprefix("refs/remotes/origin/")
    if not branch or branch == ref:
        return DetectedValue(value=None)
    return DetectedValue(value=branch, source="origin/HEAD", tier="observed")


_CI_MARKERS: tuple[tuple[str, str], ...] = (
    (".github/workflows", "github-actions"),
    (".gitlab-ci.yml", "gitlab-ci"),
)


def detect_ci(directory: Path) -> DetectedValue[str]:
    """Detect the CI system from known workflow file/directory markers.

    High-confidence only: checks for the presence of a known CI config path
    (github-actions, gitlab-ci). No inference when none of the known markers
    exist — including a workflows directory that exists but is empty.

    Args:
        directory: Repository root to inspect.

    Returns:
        DetectedValue with tier "observed" when a marker is found, else
        tier "default" with value=None.
    """
    for marker, provider in _CI_MARKERS:
        marker_path = directory / marker
        if marker_path.is_dir():
            if any(marker_path.iterdir()):
                return DetectedValue(value=provider, source=marker, tier="observed")
        elif marker_path.is_file():
            return DetectedValue(value=provider, source=marker, tier="observed")
    return DetectedValue(value=None)


def _count_extensions(directory: Path) -> Counter[str]:
    """Count code file extensions in a directory recursively.

    Excludes hidden directories, node_modules, __pycache__, etc.

    Args:
        directory: Root directory to scan.

    Returns:
        Counter mapping file extensions to their counts.
    """
    counts: Counter[str] = Counter()
    if not directory.is_dir():
        return counts

    try:
        for item in directory.iterdir():
            if item.is_dir():
                if not should_exclude_dir(item):
                    counts += _count_extensions(item)
            elif item.is_file() and item.suffix in CODE_EXTENSIONS:
                counts[item.suffix] += 1
    except OSError:
        # PermissionError, and on Windows a FileNotFoundError/OSError from a
        # path at or beyond MAX_PATH (RAISE-17099 T5, D4) — this is a
        # heuristic count, not the scan of record, so an unlistable
        # directory degrades to "not counted" rather than a Typer traceback.
        pass

    return counts


def count_code_files(directory: Path) -> int:
    """Count code files in a directory recursively.

    Excludes hidden directories, node_modules, __pycache__, etc.

    Args:
        directory: Root directory to scan.

    Returns:
        Number of code files found.
    """
    return sum(_count_extensions(directory).values())


def detect_language(directory: Path) -> ToolchainInfo | None:
    """Detect the dominant language in a directory.

    Counts file extensions, maps them to languages, and returns the
    toolchain info for the most common language.

    Args:
        directory: Root directory to scan.

    Returns:
        ToolchainInfo for the dominant language, or None if no code files found.
    """
    ext_counts = _count_extensions(directory)
    if not ext_counts:
        return None

    # Map extensions to language counts
    lang_counts: Counter[str] = Counter()
    for ext, count in ext_counts.items():
        lang = EXTENSION_TO_LANGUAGE.get(ext)
        if lang:
            lang_counts[lang] += count

    if not lang_counts:
        return None

    dominant_lang = lang_counts.most_common(1)[0][0]
    return LANGUAGE_TOOLCHAIN.get(
        dominant_lang,
        ToolchainInfo(language=dominant_lang),
    )


def detect_project_type(directory: Path) -> DetectionResult:
    """Detect whether a directory is greenfield or brownfield.

    A greenfield project has no code files.
    A brownfield project has at least one code file.
    For brownfield projects, also detects the dominant language
    and suggests toolchain commands.

    Args:
        directory: Directory to analyze.

    Returns:
        DetectionResult with project type, file count, and language info.
    """
    ext_counts = _count_extensions(directory)
    code_file_count = sum(ext_counts.values())

    if code_file_count == 0:
        return DetectionResult(
            project_type=ProjectType.GREENFIELD,
            code_file_count=0,
        )

    # Detect dominant language from extension counts
    lang_counts: Counter[str] = Counter()
    for ext, count in ext_counts.items():
        lang = EXTENSION_TO_LANGUAGE.get(ext)
        if lang:
            lang_counts[lang] += count

    language: str | None = None
    toolchain: ToolchainInfo | None = None
    if lang_counts:
        language = lang_counts.most_common(1)[0][0]
        toolchain = LANGUAGE_TOOLCHAIN.get(
            language,
            ToolchainInfo(language=language),
        )

    return DetectionResult(
        project_type=ProjectType.BROWNFIELD,
        code_file_count=code_file_count,
        language=language,
        toolchain=toolchain,
    )


_PACKAGE_MARKERS: frozenset[str] = frozenset({"pyproject.toml", "package.json"})
_MONOREPO_DIRS: tuple[str, ...] = ("packages",)


def detect_apps(
    project_root: Path,
    toolchain: ToolchainInfo | None = None,
) -> list[AppInfo]:
    """Discover apps in a monorepo layout.

    Scans known monorepo directories (``packages/``) for subdirectories
    containing a package marker (``pyproject.toml`` or ``package.json``).

    Args:
        project_root: Root directory of the project.
        toolchain: Optional root toolchain to scope commands per-app.

    Returns:
        List of AppInfo for each discovered app, sorted by name.
    """
    from raise_cli.onboarding.manifest import AppInfo

    apps: list[AppInfo] = []

    for mono_dir_name in _MONOREPO_DIRS:
        mono_dir = project_root / mono_dir_name
        if not mono_dir.is_dir():
            continue

        for child in sorted(mono_dir.iterdir()):
            if not child.is_dir():
                continue
            has_marker = any((child / marker).exists() for marker in _PACKAGE_MARKERS)
            if not has_marker:
                continue

            rel_path = f"{mono_dir_name}/{child.name}"
            app = AppInfo(
                name=child.name,
                path=rel_path,
                **_scope_commands(rel_path, toolchain),
            )
            apps.append(app)

    return apps


def _scope_commands(
    app_path: str,
    toolchain: ToolchainInfo | None,
) -> dict[str, str | None]:
    """Scope root toolchain commands to an app path.

    Appends the app path to commands that operate on directories.

    Args:
        app_path: Relative app path (e.g. ``packages/raise-cli``).
        toolchain: Root toolchain info to scope.

    Returns:
        Dict with scoped command fields for AppInfo construction.
    """
    if toolchain is None:
        return {
            "test_command": None,
            "lint_command": None,
            "type_check_command": None,
            "format_command": None,
        }

    return {
        "test_command": f"{toolchain.test_command} {app_path}"
        if toolchain.test_command
        else None,
        "lint_command": f"{toolchain.lint_command} {app_path}"
        if toolchain.lint_command
        else None,
        "type_check_command": f"{toolchain.type_check_command} {app_path}"
        if toolchain.type_check_command
        else None,
        "format_command": f"{toolchain.format_command} {app_path}"
        if toolchain.format_command
        else None,
    }


def detect_project_conventions(project_root: Path) -> dict[str, object]:
    """Infer ADR-071 project.* convention defaults from project structure.

    Returns a dict suitable for merge_project_conventions(). Only infers keys
    that can be reliably determined from directory layout — keys requiring
    human knowledge (schema.file, learnings_dir) are not included.

    Current inference:
    - project.code.root_glob: "packages/*/src/" when monorepo layout detected
      (detect_apps finds ≥1 app with a package marker).
    """
    apps = detect_apps(project_root)
    if apps:
        return {"code": {"root_glob": "packages/*/src/"}}
    return {}
