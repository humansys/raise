"""SessionIndexCheck — validates MEMORY.md presence for project slug (S17495.5).

The session open bundle warns "MEMORY.md was not regenerated this session" when
the project's Claude memory directory (~/.claude/projects/<slug>/memory/) is
missing or does not contain a MEMORY.md. This check surfaces the same condition
in rai doctor so developers can act without running a full session open.

fix_hint: rai memory validate (spec-mandated; command is deprecated but redirects
to rai graph validate — kept as-is per S17495.5 scope).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_FIX_HINT = "rai memory validate"
_log = logging.getLogger(__name__)


def _project_memory_dir(working_dir: Path) -> Path | None:
    """Resolve ~/.claude/projects/<slug>/memory/ for *working_dir*.

    Returns None when HOME is unavailable or the slug cannot be derived.
    Best-effort: never raises.
    """
    try:
        home = Path.home()
        claude_projects = home / ".claude" / "projects"
        if not claude_projects.is_dir():
            return None

        # Derive the slug the same way Claude Code does:
        # replace path separators with dashes, strip leading dash.
        slug = str(working_dir.resolve()).replace("/", "-").lstrip("-")
        return claude_projects / slug / "memory"
    except Exception:  # noqa: BLE001
        return None


class SessionIndexCheck(DoctorCheck):
    """Check that the project's Claude memory directory has a MEMORY.md index.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "session-index"
    category: ClassVar[str] = "session"
    description: ClassVar[str] = "Claude memory index (MEMORY.md) presence for project"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Check that MEMORY.md exists and is non-empty for this project."""
        results: list[CheckResult] = []
        try:
            memory_dir = _project_memory_dir(context.working_dir)
            if memory_dir is None:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.PASS,
                    "memory directory discovery skipped (HOME unavailable)",
                )
                return results

            memory_md = memory_dir / "MEMORY.md"
            if not memory_md.exists():
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.WARN,
                    "MEMORY.md missing for project — memory index not generated",
                    _FIX_HINT,
                )
            elif memory_md.stat().st_size == 0:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.WARN,
                    "MEMORY.md is empty — memory index may be stale",
                    _FIX_HINT,
                )
            else:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.PASS,
                    "MEMORY.md present",
                )
        except Exception:  # noqa: BLE001
            self._append_result(
                results, self.check_id, CheckStatus.PASS, "check skipped (error)"
            )
        return results
