"""HooksCheck — verifies UserPromptSubmit hook registered in .claude/settings (S17495.5).

The UserPromptSubmit hook drives neuro-symbolic hint injection via
``rai hook user-prompt-submit``. Without it, governance pipeline context
injections are silently missing. This check reads .claude/settings.json
and .claude/settings.local.json relative to the project root.

Best-effort: never raises, returns PASS on missing/malformed files.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_FIX_HINT = "rai init --agent claude --apply"
_HOOK_MATCHER = "rai hook user-prompt-submit"
_log = logging.getLogger(__name__)


def _has_user_prompt_submit(settings_path: Path) -> bool:
    """Return True when settings_path registers a UserPromptSubmit hook invoking rai.

    Checks that the hooks.UserPromptSubmit list contains a command matching
    _HOOK_MATCHER. Best-effort: returns False on any parse/IO error.
    """
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False

    hooks = data.get("hooks", {})
    ups_list = hooks.get("UserPromptSubmit", [])
    if not isinstance(ups_list, list):
        return False

    for entry in ups_list:
        # Each entry is a dict with a "hooks" sub-list or a direct command dict.
        if isinstance(entry, dict):
            cmd = entry.get("command", "")
            if isinstance(cmd, str) and _HOOK_MATCHER in cmd:
                return True
            # Nested structure: {"hooks": [{"command": "..."}]}
            for sub in entry.get("hooks", []):
                if isinstance(sub, dict):
                    sub_cmd = sub.get("command", "")
                    if isinstance(sub_cmd, str) and _HOOK_MATCHER in sub_cmd:
                        return True
    return False


class HooksCheck(DoctorCheck):
    """Verify UserPromptSubmit hook is registered so hint injection works.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "hooks"
    category: ClassVar[str] = "hooks"
    description: ClassVar[str] = "UserPromptSubmit hook registered in .claude/settings"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Check .claude/settings.json and .claude/settings.local.json."""
        results: list[CheckResult] = []
        try:
            project = context.working_dir
            settings_files = [
                project / ".claude" / "settings.json",
                project / ".claude" / "settings.local.json",
            ]
            found = any(
                p.exists() and _has_user_prompt_submit(p) for p in settings_files
            )
            if found:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.PASS,
                    "UserPromptSubmit hook registered",
                )
            else:
                self._append_result(
                    results,
                    self.check_id,
                    CheckStatus.WARN,
                    "UserPromptSubmit hook missing — hint injection disabled",
                    _FIX_HINT,
                )
        except Exception:  # noqa: BLE001
            self._append_result(
                results, self.check_id, CheckStatus.PASS, "check skipped (error)"
            )
        return results
