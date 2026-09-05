"""StashHygieneCheck — detect accumulated rai:-prefixed stashes (RAISE-15616).

The pipeline creates git stashes with the ``rai:`` prefix to preserve local
state during branch switches.  No automatic reaping exists; stashes accumulate
indefinitely in the shared ``.git/refs/stash``.

This check warns when ``rai:``-prefixed stashes older than 7 days are found so
the team can decide whether to pop or drop them.  It never deletes anything.

Architecture: ADR-045 (DoctorCheck protocol).
"""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime, timedelta
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

_STALE_THRESHOLD_DAYS: int = 7
_STASH_FORMAT: str = "%gd|%ci|%gs"
_RAI_PREFIX: str = "rai:"


def _parse_stale_rai_stashes(
    stash_output: str,
    *,
    now: datetime,
    threshold_days: int = _STALE_THRESHOLD_DAYS,
) -> list[tuple[str, str, str]]:
    """Parse ``git stash list`` output; return stale ``rai:`` entries.

    Args:
        stash_output: Raw output of ``git stash list --format="%gd|%ci|%gs"``.
        now: Reference datetime (UTC) for age computation.
        threshold_days: Stashes strictly older than this are considered stale.

    Returns:
        List of ``(ref, date_str, message)`` tuples for stale ``rai:`` stashes.
    """
    threshold = timedelta(days=threshold_days)
    results: list[tuple[str, str, str]] = []

    for raw_line in stash_output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        ref, date_str, message = parts
        if not message.startswith(_RAI_PREFIX):
            continue
        try:
            # git %ci format: "2026-01-15 10:30:00 +0000"
            stash_dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            # Malformed date — skip rather than crash
            continue
        if now - stash_dt > threshold:
            results.append((ref.strip(), date_str.strip(), message.strip()))
    return results


class StashHygieneCheck(DoctorCheck):
    """Warn when rai:-prefixed stashes older than 7 days accumulate.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "stash-hygiene"
    category: ClassVar[str] = "project"
    description: ClassVar[str] = (
        "rai:-prefixed git stashes older than 7 days (pipeline recovery stashes)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Scan git stash list for stale rai:-prefixed entries."""
        result = subprocess.run(
            [
                "git",
                "-C",
                str(context.working_dir),
                "stash",
                "list",
                f"--format={_STASH_FORMAT}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # Not a git repo, git not installed, or no stash at all — safe to skip
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="no git stash list available — skipping stash hygiene check",
                )
            ]

        now = datetime.now(tz=UTC)
        stale = _parse_stale_rai_stashes(result.stdout, now=now)

        if not stale:
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.PASS,
                    message=(
                        f"no rai:-prefixed stashes older than {_STALE_THRESHOLD_DAYS} days"
                    ),
                )
            ]

        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.WARN,
                message=(
                    f"{len(stale)} rai:-prefixed stash(es) older than "
                    f"{_STALE_THRESHOLD_DAYS} days — pipeline recovery stashes "
                    "accumulating"
                ),
                fix_hint=(
                    "Review with: git stash list | grep 'rai:'\n"
                    "Drop unneeded entries: git stash drop stash@{N}\n"
                    "Or pop to restore: git stash pop stash@{N}"
                ),
                details=tuple(
                    f"{ref}  ({date_str})  {msg}" for ref, date_str, msg in stale
                ),
            )
        ]
