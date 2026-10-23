"""HooksCheck — verifies UserPromptSubmit hook registered in .claude/settings (S17495.5).

The UserPromptSubmit hook drives neuro-symbolic hint injection via
``rai hook user-prompt-submit``. Without it, governance pipeline context
injections are silently missing. This check reads .claude/settings.json
and .claude/settings.local.json relative to the project root.

Also validates (RAISE-17964) that every configured hook's script path
resolves on disk, across ALL hook types (PreCompact, PostToolUse,
SessionStart, ...), not just UserPromptSubmit. A stale/deleted script
path fails silently at hook-execution time — this check surfaces it
during ``rai doctor`` instead.

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


def _load_hooks_dict(settings_path: Path) -> dict[str, object]:
    """Parse settings_path and return its ``hooks`` mapping, best-effort.

    Returns ``{}`` on any parse/IO error or when ``hooks`` isn't a dict —
    shared by both the UserPromptSubmit check and the path-existence check.
    """
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    hooks = data.get("hooks", {})
    return hooks if isinstance(hooks, dict) else {}


def _has_user_prompt_submit(settings_path: Path) -> bool:
    """Return True when settings_path registers a UserPromptSubmit hook invoking rai.

    Checks that the hooks.UserPromptSubmit list contains a command matching
    _HOOK_MATCHER. Best-effort: returns False on any parse/IO error.
    """
    hooks = _load_hooks_dict(settings_path)
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


def _iter_hook_commands(settings_path: Path) -> list[str]:
    """Return every hook ``command`` string across all hook types in settings_path.

    Covers both entry shapes: a direct ``{"command": ...}`` dict and the
    nested ``{"hooks": [{"command": ...}]}`` matcher structure. Best-effort:
    returns an empty list on any parse/IO error (RAISE-17964).
    """
    hooks = _load_hooks_dict(settings_path)
    commands: list[str] = []
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            cmd = entry.get("command", "")
            if isinstance(cmd, str) and cmd:
                commands.append(cmd)
            for sub in entry.get("hooks", []):
                if isinstance(sub, dict):
                    sub_cmd = sub.get("command", "")
                    if isinstance(sub_cmd, str) and sub_cmd:
                        commands.append(sub_cmd)
    return commands


def _extract_script_path(command: str) -> str | None:
    r"""Return the leading script-path token of a hook command, or None.

    Only the first whitespace-delimited token is considered. A bare
    executable name with no path separator (e.g. ``uv``, ``bash``) is
    assumed to resolve via PATH and is not a file-existence candidate —
    only tokens containing ``/`` or ``\\`` are treated as paths.

    Surrounding quotes are stripped (Claude Code hook commands are often
    written as ``"$CLAUDE_PROJECT_DIR"/.claude/hooks/x.sh`` — a quoted
    variable segment concatenated with a bare path segment). If ``$``
    remains anywhere in the token after stripping, it's an unresolved
    shell variable reference we can't safely check without a shell —
    skip it (return None) rather than false-flag it as missing, matching
    the established idiom in skills/validator.py:158.
    """
    token = command.strip().split()[0] if command.strip() else ""
    if not token:
        return None
    stripped = token.strip("\"'")
    if "$" in stripped:
        return None
    if "/" not in stripped and "\\" not in stripped:
        return None
    return stripped


def _resolve_hook_path(token: str, project_root: Path) -> Path:
    """Resolve a hook script token to an absolute path.

    ``~`` is expanded to the user's home directory (RAISE-17964 C1).
    Absolute tokens (post-expansion) are used as-is; relative tokens
    resolve from project_root (RAISE-17964 AC #2 — "relative paths
    resolved from project root").
    """
    path = Path(token).expanduser()
    if path.is_absolute():
        return path
    return project_root / path


def _find_missing_hook_paths(
    settings_files: list[Path], project_root: Path
) -> tuple[int, list[str]]:
    """Return (checked_count, missing_tokens) for path-like hook commands.

    ``checked_count`` is the number of path-like tokens actually examined
    (RAISE-17964 R2) — commands with no path-like leading token (bare
    executables, or ``$``-prefixed unresolved variables) are not counted,
    so callers can word a PASS result honestly instead of claiming "all"
    resolved when zero were ever checked.

    A per-token OSError (e.g. PermissionError from an unreadable parent
    directory) is treated as unresolvable and added to ``missing`` rather
    than propagating — one bad path must not abort the whole check and
    mask other genuinely missing paths found earlier (RAISE-17964 R1).
    """
    checked = 0
    missing: list[str] = []
    for settings_path in settings_files:
        if not settings_path.exists():
            continue
        for cmd in _iter_hook_commands(settings_path):
            token = _extract_script_path(cmd)
            if token is None:
                continue
            checked += 1
            try:
                exists = _resolve_hook_path(token, project_root).exists()
            except OSError:
                _log.debug(
                    "Unable to check existence of hook path %r (unreadable?)",
                    token,
                    exc_info=True,
                )
                missing.append(token)
                continue
            if not exists:
                missing.append(token)
    return checked, missing


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
        project = context.working_dir
        settings_files = [
            project / ".claude" / "settings.json",
            project / ".claude" / "settings.local.json",
        ]

        try:
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

        try:
            checked, missing = _find_missing_hook_paths(settings_files, project)
            if missing:
                self._append_result(
                    results,
                    "hooks-paths",
                    CheckStatus.ERROR,
                    "Hook script path(s) not found on disk: " + ", ".join(missing),
                    "Remove or fix the stale hook entry in "
                    ".claude/settings.json or .claude/settings.local.json",
                )
            elif checked > 0:
                self._append_result(
                    results,
                    "hooks-paths",
                    CheckStatus.PASS,
                    f"{checked} hook script path(s) resolve",
                )
            else:
                self._append_result(
                    results,
                    "hooks-paths",
                    CheckStatus.PASS,
                    "no path-like hook commands to validate",
                )
        except Exception:  # noqa: BLE001
            self._append_result(
                results, "hooks-paths", CheckStatus.PASS, "check skipped (error)"
            )
        return results
