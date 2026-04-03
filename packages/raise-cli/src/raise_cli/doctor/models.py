"""Doctor check result types.

Frozen dataclasses (not Pydantic) — internal infrastructure, not boundary
objects. Same rationale as gate models (ADR-039 S2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class CheckStatus(Enum):
    """Three-level severity for doctor checks."""

    PASS = "pass"  # noqa: S105 -- enum value, not a password
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class CheckResult:
    """Result from a single diagnostic check.

    Attributes:
        check_id: Unique identifier (e.g. ``"env-python-version"``).
        category: Grouping key for output (e.g. ``"environment"``).
        status: Pass, warning, or error.
        message: Human-readable summary.
        fix_hint: Actionable suggestion (e.g. ``"run: pip install raise-cli[mcp]"``).
        details: Additional detail lines.
    """

    check_id: str
    category: str
    status: CheckStatus
    message: str
    fix_hint: str = ""
    fix_id: str = ""
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class DoctorContext:
    """Context passed to each check's ``evaluate()`` method.

    Attributes:
        working_dir: Project root directory.
        online: Whether online checks (MCP, adapters) should run.
        verbose: Whether to include extra detail.
    """

    working_dir: Path = field(default_factory=Path.cwd)
    online: bool = False
    verbose: bool = False
