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
    """

    gate_id: str
    working_dir: Path = field(default_factory=Path.cwd)


@dataclass(frozen=True)
class GateResult:
    """Result returned by a gate's ``evaluate()`` method.

    Attributes:
        passed: Whether the gate passed validation.
        gate_id: Identifier of the gate that produced this result.
        message: Human-readable summary (actionable for failures).
        details: Additional detail lines (e.g. individual errors).
    """

    passed: bool
    gate_id: str
    message: str = ""
    details: tuple[str, ...] = ()
