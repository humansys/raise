"""DeveloperYamlCheck — detects orphan entries in ~/.rai/developer.yaml.

Presents ``scan_developer_yaml()`` results as doctor ``CheckResult``
objects, split into a projects group and a sessions group. Status is
always WARN (never ERROR) -- orphan developer.yaml entries are advisory
hygiene, not blocking (AC exit-code deviation recorded at S16227.8
design DD5).

Single source of truth with ``rai clean``: both call
``scan_developer_yaml()`` so doctor and clean can never disagree.

Architecture: Epic RAISE-16227 story S16227.8 design DD5.
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_FIX_HINT = "run: rai clean --dry-run"


class DeveloperYamlCheck(DoctorCheck):
    """Detect orphan project entries and stale sessions in developer.yaml.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "developer-yaml"
    category: ClassVar[str] = "developer-yaml"
    description: ClassVar[str] = (
        "Orphan project entries and stale sessions in ~/.rai/developer.yaml"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Scan developer.yaml and present orphan entries as WARN results."""
        from raise_cli.legacy.scanner import scan_developer_yaml

        residues = scan_developer_yaml()

        if not residues:
            return [
                CheckResult(
                    check_id="developer-yaml-clean",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no orphan entries in developer.yaml",
                )
            ]

        results: list[CheckResult] = []

        project_residues = [r for r in residues if r.kind == "orphan-project-entry"]
        if project_residues:
            results.append(
                CheckResult(
                    check_id="developer-yaml-projects",
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=(
                        f"{len(project_residues)} orphan project "
                        f"entr{'y' if len(project_residues) == 1 else 'ies'}"
                        " in developer.yaml"
                    ),
                    fix_hint=_FIX_HINT,
                    details=tuple(
                        f"{r.evidence.get('entry', r.path)} -- {r.action_hint}"
                        for r in project_residues
                    ),
                )
            )

        session_residues = [r for r in residues if r.kind == "orphan-session-entry"]
        if session_residues:
            results.append(
                CheckResult(
                    check_id="developer-yaml-sessions",
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=(
                        f"{len(session_residues)} stale session "
                        f"entr{'y' if len(session_residues) == 1 else 'ies'}"
                        " in developer.yaml"
                    ),
                    fix_hint=_FIX_HINT,
                    details=tuple(
                        f"{r.evidence.get('session_id', '?')} "
                        f"(started {r.evidence.get('started_at', '?')}, "
                        f"project {r.evidence.get('project', '?')}) -- {r.action_hint}"
                        for r in session_residues
                    ),
                )
            )

        return results
