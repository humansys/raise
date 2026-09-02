"""FF-S7: Auth invariant gate (RAISE-15093).

Ensures zero password fields in Pydantic models and no email/password auth
patterns under ``packages/raise-server/``. All auth must go through the
OIDC broker. Fail-closed: any error returns ``passed=False``.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_SERVER_SRC = Path("packages") / "raise-server"

# Patterns that indicate password-based auth (case-insensitive)
_PASSWORD_FIELD_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Pydantic model fields named *password*
    re.compile(r"^\s+password\s*[:=]", re.IGNORECASE),
    re.compile(r"^\s+\w*password\w*\s*:", re.IGNORECASE),
    # String literals suggesting password auth
    re.compile(r"""["']password["']\s*:""", re.IGNORECASE),
)

_AUTH_ANTI_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"email.*password|password.*email", re.IGNORECASE),
        "email+password auth pattern",
    ),
    (
        re.compile(r"verify_password|check_password|hash_password", re.IGNORECASE),
        "password verification function",
    ),
    (
        re.compile(r"PasswordBearer|PasswordAuth|BasicAuth", re.IGNORECASE),
        "password-based auth class",
    ),
)

_EXCLUDE_DIRS = frozenset(
    {
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        ".git",
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
    }
)

_IGNORE_MARKER = "# auth-invariant: ignore"


def _is_excluded(path: Path, root: Path) -> bool:
    """Return True if path is inside an excluded directory."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    return bool(_EXCLUDE_DIRS & set(parts))


class AuthInvariantGate:
    """Zero password fields; all auth via OIDC broker."""

    gate_id: ClassVar[str] = "ff-s7-auth-invariant"
    description: ClassVar[str] = "Zero password fields; all auth via OIDC broker"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Grep for password fields and email/password auth patterns."""
        try:
            return self._evaluate(context)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Auth invariant gate error: {exc}",
            )

    def _evaluate(self, context: GateContext) -> GateResult:
        server_path = context.working_dir / _SERVER_SRC
        if not server_path.is_dir():
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message="raise-server directory not found",
                details=(f"Expected: {_SERVER_SRC}",),
            )

        try:
            violations = self._scan_tree(server_path)
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"Auth invariant scan failed: {exc}",
            )

        if violations:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=f"{len(violations)} auth invariant violation(s)",
                details=tuple(violations),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message="No password auth patterns found -- OIDC invariant holds",
        )

    def _scan_tree(self, root: Path) -> list[str]:
        """Walk the tree and return violation descriptions."""
        violations: list[str] = []
        for py_file in sorted(root.rglob("*.py")):
            if _is_excluded(py_file, root):
                continue
            file_violations = self._scan_file(py_file, root)
            violations.extend(file_violations)
        return violations

    def _scan_file(self, path: Path, root: Path) -> list[str]:
        """Return violations for a single Python file."""
        violations: list[str] = []
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return violations

        if _IGNORE_MARKER in text:
            return violations

        rel = path.relative_to(root)
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            for pattern in _PASSWORD_FIELD_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        f"{rel}:{lineno}: password field: {stripped[:80]}"
                    )
                    break

            for pattern, desc in _AUTH_ANTI_PATTERNS:
                if pattern.search(line):
                    violations.append(f"{rel}:{lineno}: {desc}: {stripped[:80]}")
                    break

        return violations
