"""DoctorCheck Protocol — contract for diagnostic check implementations.

Doctor checks diagnose RaiSE's own health. They inform and suggest fixes,
but never block operations (unlike WorkflowGates which guard transitions).

Architecture: ADR-045 (DoctorCheck protocol).
"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


@runtime_checkable
class DoctorCheck(Protocol):
    """Contract for diagnostic check implementations.

    Subclass explicitly to inherit ``_append_result``, which appends a
    ``CheckResult`` using ``self.category`` — no need to repeat the category
    string at every call site.

    Attributes:
        check_id: Unique identifier (e.g. ``"environment"``).
        category: Grouping key for output and pipeline ordering.
        description: Human-readable purpose.
        requires_online: If True, skipped unless ``--online`` flag is set.

    Example::

        class EnvironmentCheck(DoctorCheck):
            check_id = "environment"
            category = "environment"
            description = "Python version, raise-cli version, OS, installed extras"
            requires_online = False

            def evaluate(self, context: DoctorContext) -> list[CheckResult]:
                results: list[CheckResult] = []
                self._append_result(results, "env-python", CheckStatus.PASS, "ok")
                return results
    """

    check_id: ClassVar[str]
    category: ClassVar[str]
    description: ClassVar[str]
    requires_online: ClassVar[bool]

    def evaluate(self, context: DoctorContext) -> list[CheckResult]: ...

    def _append_result(
        self,
        results: list[CheckResult],
        check_id: str,
        status: CheckStatus,
        message: str,
        fix_hint: str = "",
    ) -> None:
        """Append a CheckResult using self.category — no hardcoded strings."""
        results.append(
            CheckResult(
                check_id=check_id,
                category=self.category,
                status=status,
                message=message,
                fix_hint=fix_hint,
            )
        )
