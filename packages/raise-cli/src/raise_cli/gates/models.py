"""Gate dataclasses — context and result types.

Frozen dataclasses (not Pydantic) because these are internal infrastructure,
not boundary objects. Same rationale as hook events (ADR-039 §2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class GateContext:
    """Context passed to a gate's ``evaluate()`` method.

    Attributes:
        gate_id: Identifier of the gate being evaluated.
        working_dir: Project working directory. Defaults to ``Path.cwd()``.
        extra_args: Additional arguments appended to the gate command (e.g. a
            test scope path). Gates that do not use subprocess commands ignore
            this field.
        workflow_point: The workflow transition this invocation targets, or
            ``None`` for a blanket sweep (``rai gate check --all``). Context-aware
            gates (e.g. the architecture-review gates) enforce only when invoked
            at their own ``workflow_point`` and skip otherwise. Gates that are not
            context-aware ignore this field.
        changed_files: Repo-relative paths the current story touched, or
            ``None`` when unscoped (blanket sweeps, ``before:epic:close``, or
            when resolution failed). Scope-aware drift gates (RAISE-10933)
            intersect their findings with this set so pre-existing global
            drift outside the story's diff is not reported as story-caused.
            Gates that are not scope-aware ignore this field.
        session_id: The agent session id supplied out-of-band by the caller
            (RAISE-12207), or ``None`` to fall back to ambient discovery.
            Session-scoped gates (the architecture-review gates) resolve their
            marker under this id when set — required when the gate runs in a
            process (the MCP server) whose env is not the agent's. Gates that
            are not session-scoped ignore this field.
        issue_id: The Jira key of the work item being transitioned, when the
            caller has one. Gates that verify tracker state use this instead
            of inferring identity from a reusable worktree branch.
    """

    gate_id: str
    working_dir: Path = field(default_factory=Path.cwd)
    extra_args: tuple[str, ...] = field(default_factory=tuple)
    workflow_point: str | None = None
    changed_files: tuple[Path, ...] | None = None
    session_id: str | None = None
    issue_id: str | None = None


@dataclass(frozen=True)
class GateResult:
    """Result returned by a gate's ``evaluate()`` method.

    Attributes:
        passed: Whether the gate passed validation.
        gate_id: Identifier of the gate that produced this result.
        message: Human-readable summary (actionable for failures).
        details: Additional detail lines (e.g. individual errors).
        advisory: True when this result carries live drift findings that do
            NOT flip ``passed`` (violations visible, non-blocking by
            default). Default ``False`` is backward compatible — every
            existing gate keeps its current behavior unchanged. Set by
            ``gates.drift._base.advisory()`` (RAISE-14280 / S14262.5,
            supersedes PAT-E-1358/1364: advisory violations are visible via
            this flag, not silently indistinguishable from a clean pass).
            Consumed by ``--strict-drift`` (``cli/commands/gate.py``) to
            block only violations absent from the committed baseline
            (``governance/drift-baseline.json``).
    """

    passed: bool
    gate_id: str
    message: str = ""
    details: tuple[str, ...] = ()
    advisory: bool = False
