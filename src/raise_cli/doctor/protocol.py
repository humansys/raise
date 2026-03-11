"""DoctorCheck Protocol — contract for diagnostic check implementations.

Doctor checks diagnose RaiSE's own health. They inform and suggest fixes,
but never block operations (unlike WorkflowGates which guard transitions).

Architecture: ADR-045 (DoctorCheck protocol).
"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from raise_cli.doctor.models import CheckResult, DoctorContext


@runtime_checkable
class DoctorCheck(Protocol):
    """Contract for diagnostic check implementations.

    Attributes:
        check_id: Unique identifier (e.g. ``"environment"``).
        category: Grouping key for output and pipeline ordering.
        description: Human-readable purpose.
        requires_online: If True, skipped unless ``--online`` flag is set.

    Example::

        class EnvironmentCheck:
            check_id = "environment"
            category = "environment"
            description = "Python version, raise-cli version, OS, installed extras"
            requires_online = False

            def evaluate(self, context: DoctorContext) -> list[CheckResult]:
                ...
    """

    check_id: ClassVar[str]
    category: ClassVar[str]
    description: ClassVar[str]
    requires_online: ClassVar[bool]

    def evaluate(self, context: DoctorContext) -> list[CheckResult]: ...
