"""Environment diagnostic check — Python, raise-cli, OS, optional extras.

Reports Python version, raise-cli version, OS platform, and whether optional
extras (mcp, api) are installed.

Also reports the Bash sandbox posture (``env-bash-sandbox``, RAISE-17962):
whether Claude Code's Bash tool sandbox is requested via ``sandbox.enabled``
in any settings layer, and whether ``bwrap`` can actually create an
unprivileged user namespace on this host. See ``dev/sops/agent-bash-sandbox.md``
for the accepted posture and AppArmor hardening steps.

Architecture: ADR-045.
"""

from __future__ import annotations

import importlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck
from raise_cli.project import resolve_project_root

_MIN_PYTHON: tuple[int, int] = (3, 11)

_OPTIONAL_EXTRAS: tuple[tuple[str, str, str], ...] = (
    ("mcp", "mcp", "pip install raise-cli[mcp]"),
    ("httpx", "httpx", "pip install raise-cli[api]"),
)

_SANDBOX_SOP_HINT = "See dev/sops/agent-bash-sandbox.md"


def _read_apparmor_restrict_unprivileged_userns() -> str:
    """Read ``kernel.apparmor_restrict_unprivileged_userns`` via sysctl.

    Returns "0" (the permissive default) on any failure — missing sysctl
    binary, non-Linux host, timeout, or a non-zero exit.
    """
    try:
        result = subprocess.run(
            ["sysctl", "-n", "kernel.apparmor_restrict_unprivileged_userns"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, OSError):
        return "0"
    if result.returncode != 0:
        return "0"
    return result.stdout.strip() or "0"


def _probe_bwrap_userns(bwrap_path: str) -> tuple[bool, str]:
    """Probe whether ``bwrap`` can create an unprivileged user namespace.

    Returns ``(can_start, detail)`` — ``detail`` is the combined
    stdout/stderr on failure, empty string on success.
    """
    try:
        result = subprocess.run(
            [bwrap_path, "--unshare-user", "--ro-bind", "/", "/", "/bin/true"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, ""
    detail = (result.stdout + result.stderr).strip()
    return False, detail or f"exit code {result.returncode}"


def _resolve_sandbox_settings(working_dir: Path) -> dict[str, Any]:
    """Resolve the effective ``sandbox.*`` config across settings layers.

    Reads user -> project -> managed settings, in ascending precedence
    (later layers override earlier ones, per-key, within the ``sandbox``
    object). Managed settings (``/etc/claude-code/managed-settings.json``)
    are resolved LAST and therefore win: this matches Claude Code's real
    precedence, where enterprise-managed policy is highest and
    non-overridable by user or project settings (RAISE-17962 QR R2).
    Missing or unparsable files are skipped silently — matches Claude
    Code's own tolerant settings loading.

    The project layer is read from the resolved project root (RAISE-17962
    QR R5), not a bare ``working_dir`` — running from a subdirectory (e.g.
    ``packages/raise-cli``) must not silently drop the project layer.
    """
    project_root = resolve_project_root(working_dir)
    layers = (
        Path.home() / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.local.json",
        project_root / ".claude" / "settings.json",
        project_root / ".claude" / "settings.local.json",
        Path("/etc/claude-code/managed-settings.json"),
    )
    merged: dict[str, Any] = {}
    for layer in layers:
        try:
            data = json.loads(layer.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001, S112 -- best-effort settings read
            continue
        sandbox = data.get("sandbox") if isinstance(data, dict) else None
        if isinstance(sandbox, dict):
            merged.update(sandbox)
    return merged


class EnvironmentCheck(DoctorCheck):
    """Validates Python version, raise-cli version, OS, and installed extras."""

    check_id: ClassVar[str] = "environment"
    category: ClassVar[str] = "environment"
    description: ClassVar[str] = (
        "Python version, raise-cli version, OS, installed extras"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run environment checks: Python version, rai version, OS, extras."""
        results: list[CheckResult] = []
        results.append(self._check_python_version())
        results.append(self._check_rai_version())
        results.append(self._check_os_info())
        results.extend(self._check_optional_extras())
        results.append(self._check_bash_sandbox(context))
        return results

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_python_version(self) -> CheckResult:
        current = sys.version_info[:2]
        version_str = f"{current[0]}.{current[1]}"
        if current >= _MIN_PYTHON:
            return CheckResult(
                check_id="env-python-version",
                category=self.category,
                status=CheckStatus.PASS,
                message=f"Python {version_str}",
            )
        return CheckResult(
            check_id="env-python-version",
            category=self.category,
            status=CheckStatus.ERROR,
            message=f"Python {version_str} (>= {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} required)",
            fix_hint=f"Install Python >= {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]}",
        )

    def _check_rai_version(self) -> CheckResult:
        from raise_cli import __version__

        return CheckResult(
            check_id="env-rai-version",
            category=self.category,
            status=CheckStatus.PASS,
            message=f"raise-cli {__version__}",
        )

    def _check_os_info(self) -> CheckResult:
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        return CheckResult(
            check_id="env-os-info",
            category=self.category,
            status=CheckStatus.PASS,
            message=os_info,
        )

    def _check_optional_extras(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        for extra_name, module_name, fix_hint in _OPTIONAL_EXTRAS:
            try:
                importlib.import_module(module_name)
                results.append(
                    CheckResult(
                        check_id=f"env-extra-{extra_name}",
                        category=self.category,
                        status=CheckStatus.PASS,
                        message=f"Optional extra '{extra_name}' installed",
                    )
                )
            except ImportError:
                results.append(
                    CheckResult(
                        check_id=f"env-extra-{extra_name}",
                        category=self.category,
                        status=CheckStatus.WARN,
                        message=f"Optional extra '{extra_name}' not installed",
                        fix_hint=fix_hint,
                    )
                )
        return results

    def _check_bash_sandbox(self, context: DoctorContext) -> CheckResult:
        """Report whether the Bash sandbox is requested and whether it could start.

        RAISE-17962 — status matrix (guardián condition is requested-but-cannot):

        | requested | can start | status |
        |---|---|---|
        | yes | yes | PASS  |
        | yes | no  | ERROR |
        | no  | yes | WARN  |
        | no  | no  | WARN  (today's state — accepted posture) |
        """
        check_id = "env-bash-sandbox"

        if platform.system() != "Linux":
            return CheckResult(
                check_id=check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message="Bash sandbox check not applicable on this platform (non-Linux)",
            )

        bwrap_path = shutil.which("bwrap")
        if bwrap_path is None:
            return CheckResult(
                check_id=check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message="bwrap not installed — Bash sandbox check not applicable",
            )

        sandbox_settings = _resolve_sandbox_settings(context.working_dir)
        requested = bool(sandbox_settings.get("enabled", False))
        can_start, detail = _probe_bwrap_userns(bwrap_path)

        if requested and can_start:
            return CheckResult(
                check_id=check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message=(
                    "Bash sandbox requested and bwrap can create a user "
                    "namespace — isolation active"
                ),
            )

        if requested and not can_start:
            return CheckResult(
                check_id=check_id,
                category=self.category,
                status=CheckStatus.ERROR,
                message=(
                    "Bash sandbox requested (sandbox.enabled=true) but bwrap "
                    f"cannot create a user namespace ({detail}) — would silently "
                    "degrade to unsandboxed execution"
                ),
                fix_hint=_SANDBOX_SOP_HINT,
            )

        if not requested and can_start:
            return CheckResult(
                check_id=check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    "Bash sandbox not requested (sandbox.enabled absent/false) — "
                    "bwrap could start one; running unsandboxed by choice"
                ),
                fix_hint=_SANDBOX_SOP_HINT,
            )

        restrict = _read_apparmor_restrict_unprivileged_userns()
        return CheckResult(
            check_id=check_id,
            category=self.category,
            status=CheckStatus.WARN,
            message=(
                "Bash sandbox not requested and bwrap cannot create a user "
                f"namespace (kernel.apparmor_restrict_unprivileged_userns="
                f"{restrict}) — accepted posture"
            ),
            fix_hint=_SANDBOX_SOP_HINT,
        )
