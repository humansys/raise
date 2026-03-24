"""Environment diagnostic check — Python, raise-cli, OS, optional extras.

Reports Python version, raise-cli version, OS platform, and whether optional
extras (mcp, api) are installed.

Architecture: ADR-045.
"""

from __future__ import annotations

import importlib
import platform
import sys
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext

_MIN_PYTHON: tuple[int, int] = (3, 11)

_OPTIONAL_EXTRAS: tuple[tuple[str, str, str], ...] = (
    ("mcp", "mcp", "pip install raise-cli[mcp]"),
    ("httpx", "httpx", "pip install raise-cli[api]"),
)


class EnvironmentCheck:
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
        return results

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    @staticmethod
    def _check_python_version() -> CheckResult:
        current = sys.version_info[:2]
        version_str = f"{current[0]}.{current[1]}"
        if current >= _MIN_PYTHON:
            return CheckResult(
                check_id="env-python-version",
                category="environment",
                status=CheckStatus.PASS,
                message=f"Python {version_str}",
            )
        return CheckResult(
            check_id="env-python-version",
            category="environment",
            status=CheckStatus.ERROR,
            message=f"Python {version_str} (>= {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} required)",
            fix_hint=f"Install Python >= {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]}",
        )

    @staticmethod
    def _check_rai_version() -> CheckResult:
        from raise_cli import __version__

        return CheckResult(
            check_id="env-rai-version",
            category="environment",
            status=CheckStatus.PASS,
            message=f"raise-cli {__version__}",
        )

    @staticmethod
    def _check_os_info() -> CheckResult:
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        return CheckResult(
            check_id="env-os-info",
            category="environment",
            status=CheckStatus.PASS,
            message=os_info,
        )

    @staticmethod
    def _check_optional_extras() -> list[CheckResult]:
        results: list[CheckResult] = []
        for extra_name, module_name, fix_hint in _OPTIONAL_EXTRAS:
            try:
                importlib.import_module(module_name)
                results.append(
                    CheckResult(
                        check_id=f"env-extra-{extra_name}",
                        category="environment",
                        status=CheckStatus.PASS,
                        message=f"Optional extra '{extra_name}' installed",
                    )
                )
            except ImportError:
                results.append(
                    CheckResult(
                        check_id=f"env-extra-{extra_name}",
                        category="environment",
                        status=CheckStatus.WARN,
                        message=f"Optional extra '{extra_name}' not installed",
                        fix_hint=fix_hint,
                    )
                )
        return results
