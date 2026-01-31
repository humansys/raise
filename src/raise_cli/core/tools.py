"""Subprocess wrappers for external tools.

This module provides typed interfaces for external tools used by raise-cli:
- git: Version control operations
- ast-grep (sg): AST-based code search
- ripgrep (rg): Fast text search

Each wrapper checks tool availability and raises DependencyError if missing.

Example:
    >>> from raise_cli.core.tools import git_root, check_tool
    >>> if check_tool("git"):
    ...     root = git_root()
    ...     print(f"Git root: {root}")
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from raise_cli.exceptions import DependencyError


@dataclass
class ToolResult:
    """Result from running an external tool.

    Attributes:
        returncode: Process exit code.
        stdout: Standard output (stripped).
        stderr: Standard error (stripped).
    """

    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.returncode == 0


@dataclass
class GitStatus:
    """Parsed git status output.

    Attributes:
        staged: Files staged for commit.
        modified: Modified but unstaged files.
        untracked: Untracked files.
        branch: Current branch name.
    """

    staged: list[str] = field(default_factory=lambda: list[str]())
    modified: list[str] = field(default_factory=lambda: list[str]())
    untracked: list[str] = field(default_factory=lambda: list[str]())
    branch: str = ""


@dataclass
class SearchMatch:
    """A search match from rg or sg.

    Attributes:
        path: File path containing the match.
        line: Line number (1-indexed).
        text: Matched line text.
    """

    path: Path
    line: int
    text: str


def check_tool(name: str) -> bool:
    """Check if an external tool is available.

    Args:
        name: Tool name (git, sg, rg).

    Returns:
        True if tool is available, False otherwise.

    Example:
        >>> check_tool("git")
        True
    """
    return shutil.which(name) is not None


def require_tool(name: str) -> None:
    """Require an external tool, raising if unavailable.

    Args:
        name: Tool name (git, sg, rg).

    Raises:
        DependencyError: If tool is not available.

    Example:
        >>> require_tool("nonexistent")
        Traceback (most recent call last):
            ...
        raise_cli.exceptions.DependencyError: ...
    """
    if not check_tool(name):
        hints = {
            "git": "Install git: https://git-scm.com/downloads",
            "sg": "Install ast-grep: https://ast-grep.github.io/",
            "rg": "Install ripgrep: https://github.com/BurntSushi/ripgrep",
        }
        raise DependencyError(
            f"Required tool '{name}' is not installed",
            hint=hints.get(name, f"Install {name} and ensure it's in PATH"),
        )


def run_tool(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = False,
) -> ToolResult:
    """Run an external tool and capture output.

    Args:
        args: Command and arguments.
        cwd: Working directory. Defaults to current directory.
        check: If True, raise on non-zero exit code.

    Returns:
        ToolResult with returncode, stdout, stderr.

    Raises:
        DependencyError: If tool is not available.
        subprocess.CalledProcessError: If check=True and command fails.

    Example:
        >>> result = run_tool(["git", "status", "--porcelain"])
        >>> print(result.stdout)
    """
    if not args:
        raise ValueError("args must not be empty")

    tool_name = args[0]
    require_tool(tool_name)

    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )

    return ToolResult(
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


# -----------------------------------------------------------------------------
# Git Operations
# -----------------------------------------------------------------------------


def git_root(cwd: Path | None = None) -> Path:
    """Get the root directory of the git repository.

    Args:
        cwd: Working directory. Defaults to current directory.

    Returns:
        Path to the git repository root.

    Raises:
        DependencyError: If git is not available or not in a repo.

    Example:
        >>> root = git_root()
        >>> (root / ".git").exists()
        True
    """
    result = run_tool(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    if not result.success:
        raise DependencyError(
            "Not in a git repository",
            hint="Run this command from within a git repository",
        )
    return Path(result.stdout)


def git_branch(cwd: Path | None = None) -> str:
    """Get the current git branch name.

    Args:
        cwd: Working directory. Defaults to current directory.

    Returns:
        Current branch name.

    Raises:
        DependencyError: If git is not available or not in a repo.

    Example:
        >>> branch = git_branch()
        >>> isinstance(branch, str)
        True
    """
    result = run_tool(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if not result.success:
        raise DependencyError(
            "Cannot determine git branch",
            hint="Ensure you're in a git repository with at least one commit",
        )
    return result.stdout


def git_status(cwd: Path | None = None) -> GitStatus:
    """Get structured git status.

    Args:
        cwd: Working directory. Defaults to current directory.

    Returns:
        GitStatus with staged, modified, untracked files and branch.

    Raises:
        DependencyError: If git is not available.

    Example:
        >>> status = git_status()
        >>> isinstance(status.staged, list)
        True
    """
    status = GitStatus()

    # Get branch
    try:
        status.branch = git_branch(cwd)
    except DependencyError:
        status.branch = ""

    # Get file status with porcelain format
    result = run_tool(["git", "status", "--porcelain"], cwd=cwd)
    if not result.success:
        return status

    for line in result.stdout.splitlines():
        if len(line) < 3:
            continue

        index_status = line[0]
        worktree_status = line[1]
        filepath = line[3:]

        # Staged changes (index has changes)
        if index_status in "MADRC":
            status.staged.append(filepath)

        # Modified in worktree (not staged)
        if worktree_status == "M":
            status.modified.append(filepath)

        # Untracked
        if index_status == "?" and worktree_status == "?":
            status.untracked.append(filepath)

    return status


def git_diff(staged: bool = False, cwd: Path | None = None) -> str:
    """Get git diff output.

    Args:
        staged: If True, show staged changes only. Defaults to False.
        cwd: Working directory. Defaults to current directory.

    Returns:
        Diff output as string.

    Raises:
        DependencyError: If git is not available.

    Example:
        >>> diff = git_diff(staged=True)
        >>> isinstance(diff, str)
        True
    """
    args = ["git", "diff"]
    if staged:
        args.append("--staged")

    result = run_tool(args, cwd=cwd)
    return result.stdout


# -----------------------------------------------------------------------------
# Ripgrep Operations
# -----------------------------------------------------------------------------


def rg_search(
    pattern: str,
    path: Path | None = None,
    *,
    glob: str | None = None,
    ignore_case: bool = False,
) -> list[SearchMatch]:
    """Search files using ripgrep.

    Args:
        pattern: Regex pattern to search for.
        path: Directory or file to search. Defaults to current directory.
        glob: Glob pattern to filter files (e.g., "*.py").
        ignore_case: If True, search case-insensitively.

    Returns:
        List of SearchMatch results.

    Raises:
        DependencyError: If ripgrep is not available.

    Example:
        >>> matches = rg_search("def ", Path("."), glob="*.py")
        >>> all(isinstance(m, SearchMatch) for m in matches)
        True
    """
    args = ["rg", "--line-number", "--no-heading", pattern]

    if glob:
        args.extend(["--glob", glob])

    if ignore_case:
        args.append("--ignore-case")

    if path:
        args.append(str(path))

    result = run_tool(args)

    matches: list[SearchMatch] = []
    if not result.success:
        return matches

    for line in result.stdout.splitlines():
        # Format: path:line:text
        parts = line.split(":", 2)
        if len(parts) >= 3:
            matches.append(
                SearchMatch(
                    path=Path(parts[0]),
                    line=int(parts[1]),
                    text=parts[2],
                )
            )

    return matches


# -----------------------------------------------------------------------------
# ast-grep Operations
# -----------------------------------------------------------------------------


def sg_search(
    pattern: str,
    path: Path | None = None,
    *,
    lang: str | None = None,
) -> list[SearchMatch]:
    """Search files using ast-grep.

    Args:
        pattern: AST pattern to search for.
        path: Directory or file to search. Defaults to current directory.
        lang: Language to parse (e.g., "python", "typescript").

    Returns:
        List of SearchMatch results.

    Raises:
        DependencyError: If ast-grep is not available.

    Example:
        >>> matches = sg_search("def $NAME($$$ARGS)", Path("."), lang="python")
        >>> all(isinstance(m, SearchMatch) for m in matches)
        True
    """
    args = ["sg", "--pattern", pattern]

    if lang:
        args.extend(["--lang", lang])

    if path:
        args.append(str(path))

    result = run_tool(args)

    matches: list[SearchMatch] = []
    if not result.success:
        return matches

    # ast-grep default output: path:line:column: matched text
    for line in result.stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) >= 3:
            try:
                line_num = int(parts[1])
                matches.append(
                    SearchMatch(
                        path=Path(parts[0]),
                        line=line_num,
                        text=parts[3] if len(parts) > 3 else "",
                    )
                )
            except ValueError:
                continue

    return matches


__all__ = [
    "ToolResult",
    "GitStatus",
    "SearchMatch",
    "check_tool",
    "require_tool",
    "run_tool",
    "git_root",
    "git_branch",
    "git_status",
    "git_diff",
    "rg_search",
    "sg_search",
]
