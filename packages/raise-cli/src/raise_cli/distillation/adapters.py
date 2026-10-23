"""SourceAdapter protocol and runtime-specific implementations for session JSONL discovery.

Supports Claude Code (primary), Hermes, and Codex CLI (stubs).
Multi-runtime disambiguation: when multiple adapters detect, use the JSONL with the
most recent mtime — the session that actually just closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from raise_cli.distillation.parser import TurnRecord

from raise_cli.distillation.parser import TurnRecord


@dataclass
class SessionContext:
    """Caller-supplied hints for session discovery."""

    project_root: Path
    session_id: str = field(default="")


@runtime_checkable
class SourceAdapter(Protocol):
    """Protocol for runtime-specific session JSONL discovery and parsing."""

    def detect(self, root: Path) -> bool:
        """Return True if this runtime appears to be installed/active for root."""
        ...

    def find_session(self, root: Path, ctx: SessionContext) -> Path | None:
        """Return the most relevant session JSONL path, or None if not found."""
        ...

    def parse(self, path: Path) -> list[TurnRecord]:
        """Parse a JSONL file into a list of TurnRecords."""
        ...


class ClaudeCodeAdapter:
    """SourceAdapter for Claude Code sessions stored in ~/.claude/projects/."""

    def detect(self, root: Path) -> bool:
        """True when ~/.claude/ exists (Claude Code is the active runtime)."""
        return (Path.home() / ".claude").is_dir()

    def find_session(self, root: Path, ctx: SessionContext) -> Path | None:
        """Find most recent Claude Code JSONL for root, with worktree fallback (RAISE-10219)."""
        result = self._find_in_cc_dir(root)
        if result is not None:
            return result
        toplevel = self._resolve_git_toplevel(root)
        if toplevel is not None and toplevel != root.resolve():
            return self._find_in_cc_dir(toplevel)
        return None

    def _find_in_cc_dir(self, project_path: Path) -> Path | None:
        base = Path.home() / ".claude" / "projects"
        if not base.exists():
            return None
        resolved = str(project_path.resolve())
        proj_name = resolved.replace("/", "-").replace(".", "-")
        proj_dir = base / proj_name
        if not proj_dir.exists():
            return None
        jsonl_files = list(proj_dir.glob("*.jsonl"))
        if not jsonl_files:
            return None
        return max(jsonl_files, key=lambda f: f.stat().st_mtime)

    def _resolve_git_toplevel(self, project_path: Path) -> Path | None:
        current = project_path.resolve()
        for _ in range(50):
            git_path = current / ".git"
            if git_path.is_file():
                try:
                    content = git_path.read_text(encoding="utf-8").strip()
                except OSError:
                    return None
                if content.startswith("gitdir:"):
                    gitdir = content[len("gitdir:") :].strip()
                    main_git = Path(gitdir).resolve()
                    if main_git.name != "worktrees":
                        main_git = main_git.parent
                    if main_git.name == "worktrees":
                        return main_git.parent.parent
                return None
            if git_path.is_dir():
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def parse(self, path: Path) -> list[TurnRecord]:
        """Parse a Claude Code JSONL; harness noise taxonomy applied by the parser."""
        from raise_cli.distillation.parser import parse_session_jsonl

        return parse_session_jsonl(path)


class HermesAdapter:
    """SourceAdapter stub for Hermes sessions (discovery: ~/.hermes/sessions/)."""

    def detect(self, root: Path) -> bool:
        """True when ~/.hermes/sessions/ exists."""
        return (Path.home() / ".hermes" / "sessions").is_dir()

    def find_session(self, root: Path, ctx: SessionContext) -> Path | None:
        """Not yet implemented — Hermes session discovery TBD."""
        return None

    def parse(self, path: Path) -> list[TurnRecord]:
        """Not yet implemented."""
        return []


class CodexAdapter:
    """SourceAdapter stub for Codex CLI sessions (discovery: ~/.codex/logs/)."""

    def detect(self, root: Path) -> bool:
        """True when ~/.codex/logs/ exists."""
        return (Path.home() / ".codex" / "logs").is_dir()

    def find_session(self, root: Path, ctx: SessionContext) -> Path | None:
        """Not yet implemented — Codex session discovery TBD."""
        return None

    def parse(self, path: Path) -> list[TurnRecord]:
        """Not yet implemented."""
        return []


class AdapterRegistry:
    """Ordered registry of SourceAdapters with multi-runtime disambiguation.

    When multiple adapters detect and return a JSONL, the one with the most
    recent mtime wins — it was the runtime that actually just closed its session.
    """

    def __init__(self, adapters: list[SourceAdapter] | None = None) -> None:
        """Initialize with an ordered list of adapters (default: CC, Hermes, Codex)."""
        if adapters is None:
            adapters = [ClaudeCodeAdapter(), HermesAdapter(), CodexAdapter()]
        self._adapters = adapters

    def find_session(self, root: Path, ctx: SessionContext) -> Path | None:
        """Find the most recently modified session JSONL across all detecting adapters."""
        candidates: list[Path] = []
        for adapter in self._adapters:
            if adapter.detect(root):
                path = adapter.find_session(root, ctx)
                if path is not None:
                    candidates.append(path)
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def parse(self, path: Path, root: Path) -> list[TurnRecord]:
        """Parse a JSONL using the first adapter that detects the runtime."""
        for adapter in self._adapters:
            if adapter.detect(root):
                return adapter.parse(path)
        return ClaudeCodeAdapter().parse(path)


#: Default registry — used by DistillationHook
DEFAULT_REGISTRY = AdapterRegistry()
