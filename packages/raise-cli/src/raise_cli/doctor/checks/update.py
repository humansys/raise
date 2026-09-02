"""UpdateCheck — surfaces the same update-availability aviso in `rai doctor`.

Wraps `check_update_available()` (session/open_service.py, RAISE-15715) —
the same detector `rai session open` already uses, including its 24h
cache and `RAI_NO_UPDATE_CHECK` short-circuit (RAISE-15660). This check
never re-implements the fetch/compare logic; it only translates the
session CheckResult into a doctor CheckResult.

`requires_online = False`: the underlying detector already degrades
safely (short timeout, silent fail, cache-first), so it does not need
the doctor `--online` gate.
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.session.open_service import check_update_available

_FIX_HINT = "run: rai self-update"


class UpdateCheck(DoctorCheck):
    """Detect a newer published `rai` release — same detector as session open.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "update"
    category: ClassVar[str] = "update"
    description: ClassVar[str] = (
        "Newer rai release available (mirrors rai session open)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Delegate to check_update_available() and present its CheckResult."""
        result = check_update_available()

        if result.status == "warn":
            current = result.data.get("current", "?")
            latest = result.data.get("latest", "?")
            message = f"{latest} disponible (estás en {current})"
            if result.data.get("severity") == "critical":
                message += " — CRÍTICA"
            results: list[CheckResult] = []
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                message,
                _FIX_HINT,
            )
            return results

        current = result.data.get("current")
        message = (
            f"estás en la última versión ({current})"
            if current is not None
            else "chequeo de versión omitido"
        )
        results: list[CheckResult] = []
        self._append_result(results, self.check_id, CheckStatus.PASS, message)
        return results
