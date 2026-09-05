"""AgentRuntimeAdapter — cross-runtime skill invocation abstraction.

RAISE-16286: rai-pipeline-run and rai-story-run invoke subagents by name
(subagent_type: "rai-story-design") — Codex/Kimi/Hermes have no lookup-by-name:
skill content must be injected as message/prompt.

This module provides:
    AgentRuntime       — enum of supported runtimes
    ClaudeCodeInvocation — Agent(subagent_type=skill_name) spec
    CodexInvocation    — spawn_agent(task_name, message) spec
    KimiInvocation     — Agent(prompt=skill_content) spec
    HermesInvocation   — delegate_task(goal=skill_content, role="worker") spec
    AgentRuntimeAdapter — reads developer.yaml, builds runtime-specific specs

Usage::

    adapter = AgentRuntimeAdapter.from_developer_yaml(skill_base=skills_dir)
    inv = adapter.build_invocation("rai-story-design", args="RAISE-100")
    # inv is a typed invocation spec; caller uses it to construct the prompt

Design: NO ``from __future__ import annotations`` (PAT-E-597).
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal

import yaml

logger = logging.getLogger(__name__)


# ─── Runtime Enum ────────────────────────────────────────────────────────────


class AgentRuntime(str, Enum):
    """Supported agent runtimes.

    Values match the ``agent_runtime`` key in ``~/.rai/developer.yaml``.
    """

    CLAUDE_CODE = "claude-code"
    CODEX = "codex"
    KIMI = "kimi"
    HERMES = "hermes"


# ─── Invocation Specs ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ClaudeCodeInvocation:
    """Claude Code: Agent(subagent_type=skill_name).

    Claude Code resolves named agents by the subagent_type registry.
    No content injection needed — the runtime knows the skill.
    """

    subagent_type: str
    runtime: Literal["claude-code"] = field(default="claude-code", init=False)


@dataclass(frozen=True)
class CodexInvocation:
    """Codex: spawn_agent(task_name, message).

    Codex has no named agent lookup. The full skill content + args
    must be injected as the ``message`` parameter.
    """

    task_name: str
    message: str
    runtime: Literal["codex"] = field(default="codex", init=False)


@dataclass(frozen=True)
class KimiInvocation:
    """Kimi Code: Agent(prompt=skill_content).

    Kimi supports only built-in subagent_types. The skill content
    is injected as the ``prompt`` parameter.
    """

    prompt: str
    runtime: Literal["kimi"] = field(default="kimi", init=False)


@dataclass(frozen=True)
class HermesInvocation:
    """Hermes: delegate_task(goal=skill_content, role="worker").

    Hermes has no named agent lookup. The skill content is injected
    as the ``goal`` with a fixed ``role: worker``.
    """

    goal: str
    role: str = field(default="worker", init=False)
    runtime: Literal["hermes"] = field(default="hermes", init=False)


#: Union type for all runtime invocation specs.
AgentInvocation = (
    ClaudeCodeInvocation | CodexInvocation | KimiInvocation | HermesInvocation
)


# ─── Adapter ─────────────────────────────────────────────────────────────────


class AgentRuntimeAdapter:
    """Builds runtime-specific invocation specs for skill dispatch.

    Reads ``agent_runtime`` from ``~/.rai/developer.yaml`` (via
    ``from_developer_yaml``) and dispatches to the correct invocation
    format. Claude Code uses name-based lookup; all others inject
    the full skill content so the runtime can execute it without a
    named agent registry.

    Args:
        runtime:    Target agent runtime. Defaults to CLAUDE_CODE.
        skill_base: Directory containing skill subdirectories
                    (e.g. ``{skill_base}/rai-story-design/SKILL.md``).
                    Required for non-Claude-Code runtimes.
    """

    def __init__(
        self,
        runtime: AgentRuntime = AgentRuntime.CLAUDE_CODE,
        skill_base: Path | None = None,
    ) -> None:
        self.runtime = runtime
        self._skill_base = skill_base

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def from_developer_yaml(
        cls,
        yaml_path: Path | None = None,
        skill_base: Path | None = None,
    ) -> "AgentRuntimeAdapter":
        """Create an adapter from ``~/.rai/developer.yaml``.

        Reads the ``agent_runtime`` key. Falls back to CLAUDE_CODE when:
        - The file is missing or unreadable
        - The key is absent
        - The value is not a known runtime

        Args:
            yaml_path:  Override the default ``~/.rai/developer.yaml`` path.
                        Useful for testing.
            skill_base: Forwarded to the adapter constructor.

        Returns:
            AgentRuntimeAdapter configured for the resolved runtime.
        """
        if yaml_path is None:
            from raise_cli.config.paths import get_global_rai_dir

            yaml_path = get_global_rai_dir() / "developer.yaml"

        runtime = AgentRuntime.CLAUDE_CODE  # safe default

        if yaml_path.is_file():
            try:
                raw: object = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    raw_runtime = raw.get("agent_runtime")
                    if raw_runtime is not None:
                        try:
                            runtime = AgentRuntime(str(raw_runtime))
                        except ValueError:
                            logger.warning(
                                "Unknown agent_runtime %r in %s — defaulting to claude-code",
                                raw_runtime,
                                yaml_path,
                            )
            except Exception:  # noqa: BLE001 — intentional broad catch (RAISE-15490 pattern)
                logger.warning(
                    "Failed to read agent_runtime from %s — defaulting to claude-code",
                    yaml_path,
                )

        return cls(runtime=runtime, skill_base=skill_base)

    @classmethod
    def from_harness(
        cls,
        harness: str,
        skill_base: Path | None = None,
    ) -> "AgentRuntimeAdapter":
        """Create an adapter from an already-resolved harness string.

        Used by ``_phase_instruction`` which has already called
        ``_resolve_harness()`` — avoids re-reading developer.yaml.

        Args:
            harness:    Harness string (e.g. ``"codex"``, ``"kimi"``).
            skill_base: Directory containing skill subdirectories.

        Returns:
            AgentRuntimeAdapter configured for the resolved runtime.

        Raises:
            ValueError: If ``harness`` does not map to a known AgentRuntime.
                        The caller should catch this and fall back.
        """
        try:
            runtime = AgentRuntime(harness.lower())
        except ValueError as exc:
            raise ValueError(
                f"Harness {harness!r} does not map to a known AgentRuntime. "
                "Known values: claude-code, codex, kimi, hermes."
            ) from exc
        return cls(runtime=runtime, skill_base=skill_base)

    # ── Invocation builder ───────────────────────────────────────────────────

    def build_invocation(
        self,
        skill_name: str,
        args: str | None = None,
    ) -> AgentInvocation:
        """Build a runtime-specific invocation spec for ``skill_name``.

        Claude Code returns a name-based lookup spec (no skill read).
        All other runtimes read the skill content and inject it into
        the appropriate message/prompt/goal field.

        Args:
            skill_name: The skill identifier (e.g. ``"rai-story-design"``).
            args:       Optional arguments to append after the skill content.

        Returns:
            A typed invocation spec for the configured runtime.

        Raises:
            FileNotFoundError: If the skill file is not found and the
                runtime requires content injection.
            ValueError: If skill_base is None and content injection is needed.
        """
        if self.runtime == AgentRuntime.CLAUDE_CODE:
            return ClaudeCodeInvocation(subagent_type=skill_name)

        content = self._read_skill_content(skill_name)
        message = content
        if args:
            message = f"{content}\n\n## Arguments\n\n{args}"

        if self.runtime == AgentRuntime.CODEX:
            return CodexInvocation(task_name=skill_name, message=message)

        if self.runtime == AgentRuntime.KIMI:
            return KimiInvocation(prompt=message)

        # HERMES
        return HermesInvocation(goal=message)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _read_skill_content(self, skill_name: str) -> str:
        """Read SKILL.md content from ``skill_base/{skill_name}/SKILL.md``.

        Args:
            skill_name: The skill identifier.

        Returns:
            The full text content of the SKILL.md file.

        Raises:
            ValueError: If skill_base is not configured.
            FileNotFoundError: If the SKILL.md file does not exist.
        """
        if self._skill_base is None:
            raise ValueError(
                "skill_base must be set to read skill content for non-Claude-Code runtimes"
            )
        skill_file = self._skill_base / skill_name / "SKILL.md"
        if not skill_file.is_file():
            raise FileNotFoundError(
                f"Skill file not found for '{skill_name}': {skill_file}"
            )
        return skill_file.read_text(encoding="utf-8")

    def build_phase_instruction(
        self,
        skill_name: str,
        args: str | None = None,
    ) -> str:
        """Build a pipeline dispatch instruction string for non-CC runtimes.

        Returns a human-readable instruction the orchestrating AI executes
        to dispatch the skill in the target runtime. Unlike
        ``build_invocation``, this method does NOT pre-read skill content —
        it instructs the orchestrating AI to read and inject it.

        Args:
            skill_name: The skill identifier (e.g. ``"rai-story-design"``).
            args:       Optional arguments to include in the dispatch call.

        Returns:
            Instruction string for the orchestrating AI.

        Raises:
            ValueError: If called for the Claude Code runtime (CC uses name
                        lookup, not content injection — the CC path in
                        ``_phase_instruction`` handles it separately).
            FileNotFoundError: If skill_base is set and the skill file is
                               absent (surface early rather than silently
                               omitting the skill path).
        """
        if self.runtime == AgentRuntime.CLAUDE_CODE:
            raise ValueError(
                "build_phase_instruction must not be called for the Claude Code "
                "runtime; use the existing Agent(subagent_type=...) path."
            )

        # Resolve the skill path for display; also validates existence.
        skill_path = self._resolve_skill_path(skill_name)
        args_note = f"\n\nARGUMENTS: {args}" if args else ""

        if self.runtime == AgentRuntime.CODEX:
            return (
                f"Read {skill_path} in full, then call:\n"
                f'spawn_agent(task_name="{skill_name}", '
                f'message=<that content + "{args_note}">)'
            )
        if self.runtime == AgentRuntime.KIMI:
            return (
                f"Read {skill_path} in full, then call:\n"
                f'Agent(prompt=<that content + "{args_note}">)'
            )
        # HERMES
        return (
            f"Read {skill_path} in full, then call:\n"
            f'delegate_task(goal=<that content + "{args_note}">, role="worker")'
        )

    def _resolve_skill_path(self, skill_name: str) -> str:
        """Return a displayable skill file path; raise FileNotFoundError if absent.

        Uses skill_base when configured; falls back to the conventional
        relative path ``.claude/skills/{skill_name}/SKILL.md``.
        """
        if self._skill_base is not None:
            skill_file = self._skill_base / skill_name / "SKILL.md"
            if not skill_file.is_file():
                raise FileNotFoundError(
                    f"Skill file not found for '{skill_name}': {skill_file}"
                )
            return str(skill_file)
        return f".claude/skills/{skill_name}/SKILL.md"
