"""Git evidence extractor for ISO 27001 compliance.

Extracts commits, merge commits, tags, and branches from git history
and maps them to EvidenceItem instances for audit reporting.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import date, datetime
from pathlib import Path

from raise_cli.compliance.evidence import EvidenceItem
from raise_cli.compliance.models import ControlConfig, ControlMapping

logger = logging.getLogger(__name__)

# Git extractors handled by this module
_COMMIT_EXTRACTORS = frozenset({"commits"})
_MERGE_EXTRACTORS = frozenset({"pull_requests", "approvals"})
_TAG_EXTRACTORS = frozenset({"tags"})
_BRANCH_EXTRACTORS = frozenset({"branches"})

# Git log format: hash|author|ISO-date|subject
_LOG_FORMAT = "%H|%an|%aI|%s"


class GitEvidenceExtractor:
    """Extracts evidence from git repository history.

    Reads ControlMapping to identify controls with git-type evidence sources,
    then runs git commands to extract matching evidence items.

    Args:
        repo_path: Path to the git repository root.
    """

    def __init__(self, repo_path: Path) -> None:
        self._repo_path = repo_path

    def extract(
        self,
        mapping: ControlMapping,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EvidenceItem]:
        """Extract git evidence for all controls in the mapping.

        Args:
            mapping: Control mapping with evidence source definitions.
            start_date: Start of the audit period (inclusive). None for no lower bound.
            end_date: End of the audit period (inclusive). None for no upper bound.

        Returns:
            List of EvidenceItem instances extracted from git history.
        """
        items: list[EvidenceItem] = []

        for control in mapping.controls:
            for source in control.evidence_sources:
                if source.type != "git":
                    continue

                if source.extractor in _COMMIT_EXTRACTORS:
                    items.extend(
                        self._extract_commits(control, start_date, end_date),
                    )
                elif source.extractor in _MERGE_EXTRACTORS:
                    items.extend(
                        self._extract_merge_commits(control, start_date, end_date),
                    )
                elif source.extractor in _TAG_EXTRACTORS:
                    items.extend(
                        self._extract_tags(control, start_date, end_date),
                    )
                elif source.extractor in _BRANCH_EXTRACTORS:
                    items.extend(
                        self._extract_branches(control, start_date, end_date),
                    )

        return items

    def _extract_commits(
        self,
        control: ControlConfig,
        start_date: date | None,
        end_date: date | None,
    ) -> list[EvidenceItem]:
        """Extract regular commits from git log."""
        cmd = self._build_log_command(start_date, end_date, merges_only=False)
        output = self._run_git(cmd)
        return self._parse_log_output(output, control)

    def _extract_merge_commits(
        self,
        control: ControlConfig,
        start_date: date | None,
        end_date: date | None,
    ) -> list[EvidenceItem]:
        """Extract merge commits from git log."""
        cmd = self._build_log_command(start_date, end_date, merges_only=True)
        output = self._run_git(cmd)
        return self._parse_log_output(output, control)

    def _build_log_command(
        self,
        start_date: date | None,
        end_date: date | None,
        *,
        merges_only: bool,
    ) -> list[str]:
        """Build a git log command with optional date range and merge filter."""
        cmd = ["git", "log", f"--format={_LOG_FORMAT}"]

        if merges_only:
            cmd.append("--merges")

        if start_date is not None:
            cmd.append(f"--after={start_date.isoformat()}")
        if end_date is not None:
            cmd.append(f"--before={end_date.isoformat()}")

        return cmd

    def _parse_log_output(
        self,
        output: str,
        control: ControlConfig,
    ) -> list[EvidenceItem]:
        """Parse git log output into EvidenceItem instances."""
        items: list[EvidenceItem] = []

        for line in output.strip().splitlines():
            if not line.strip():
                continue

            parts = line.split("|", maxsplit=3)
            if len(parts) < 4:  # noqa: PLR2004
                logger.warning("Skipping malformed git log line: %s", line)
                continue

            commit_hash, author, date_str, subject = parts

            try:
                timestamp = datetime.fromisoformat(date_str)
            except ValueError:
                logger.warning("Skipping line with invalid date: %s", line)
                continue

            items.append(
                EvidenceItem(
                    control_id=control.id,
                    control_name=control.name,
                    evidence_type="git",
                    title=subject,
                    description=f"Commit by {author}: {subject}",
                    timestamp=timestamp,
                    source_ref=commit_hash,
                ),
            )

        return items

    def _extract_tags(
        self,
        control: ControlConfig,
        start_date: date | None,
        end_date: date | None,
    ) -> list[EvidenceItem]:
        """Extract tags from git.

        Tags lack --after/--before support, so date filtering is post-extraction.
        """
        cmd = [
            "git",
            "tag",
            "--sort=-creatordate",
            "--format=%(refname:short)|%(creatordate:iso-strict)|%(subject)",
        ]
        output = self._run_git(cmd)
        items: list[EvidenceItem] = []

        for line in output.strip().splitlines():
            if not line.strip():
                continue

            parts = line.split("|", maxsplit=2)
            if len(parts) < 3:  # noqa: PLR2004
                logger.warning("Skipping malformed tag line: %s", line)
                continue

            tag_name, date_str, subject = parts

            try:
                timestamp = datetime.fromisoformat(date_str)
            except ValueError:
                logger.warning("Skipping tag with invalid date: %s", line)
                continue

            # Post-extraction date filtering
            tag_date = timestamp.date()
            if start_date is not None and tag_date < start_date:
                continue
            if end_date is not None and tag_date > end_date:
                continue

            items.append(
                EvidenceItem(
                    control_id=control.id,
                    control_name=control.name,
                    evidence_type="git",
                    title=f"Tag {tag_name}: {subject}"
                    if subject
                    else f"Tag {tag_name}",
                    description=f"Release tag {tag_name}",
                    timestamp=timestamp,
                    source_ref=tag_name,
                ),
            )

        return items

    def _extract_branches(
        self,
        control: ControlConfig,
        start_date: date | None,
        end_date: date | None,
    ) -> list[EvidenceItem]:
        """Extract branch information from git."""
        cmd = [
            "git",
            "branch",
            "-a",
            "--format=%(refname:short)|%(committerdate:iso-strict)",
        ]
        output = self._run_git(cmd)
        items: list[EvidenceItem] = []

        for line in output.strip().splitlines():
            if not line.strip():
                continue

            parts = line.split("|", maxsplit=1)
            if len(parts) < 2:  # noqa: PLR2004
                logger.warning("Skipping malformed branch line: %s", line)
                continue

            branch_name, date_str = parts

            try:
                timestamp = datetime.fromisoformat(date_str)
            except ValueError:
                logger.warning("Skipping branch with invalid date: %s", line)
                continue

            items.append(
                EvidenceItem(
                    control_id=control.id,
                    control_name=control.name,
                    evidence_type="git",
                    title=f"Branch: {branch_name}",
                    description=f"Git branch {branch_name}",
                    timestamp=timestamp,
                    source_ref=branch_name,
                ),
            )

        return items

    def _run_git(self, cmd: list[str]) -> str:
        """Run a git command and return stdout."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=self._repo_path,
        )
        return result.stdout
