"""Tests for GitEvidenceExtractor — commits, merge commits, tags, and branches."""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path
from unittest.mock import patch

from raise_cli.compliance.evidence import EvidenceItem
from raise_cli.compliance.extractors.git import GitEvidenceExtractor
from raise_cli.compliance.models import (
    ControlConfig,
    ControlMapping,
    EvidenceSourceConfig,
)


def _make_mapping(
    *,
    extractors: list[tuple[str, str, str]] | None = None,
) -> ControlMapping:
    """Build a minimal ControlMapping for testing.

    Args:
        extractors: List of (control_id, control_name, extractor_name) tuples.
            All will be type="git".
    """
    if extractors is None:
        extractors = [
            ("A.8.32", "Change management", "commits"),
        ]
    controls: list[ControlConfig] = []
    for ctrl_id, ctrl_name, ext_name in extractors:
        controls.append(
            ControlConfig(
                id=ctrl_id,
                name=ctrl_name,
                description=f"Description for {ctrl_id}",
                evidence_sources=[
                    EvidenceSourceConfig(
                        type="git",
                        extractor=ext_name,
                        description=f"{ext_name} evidence",
                    ),
                ],
            ),
        )
    return ControlMapping(
        version="1.0",
        standard="ISO 27001:2022",
        controls=controls,
    )


GIT_LOG_OUTPUT = (
    "abc123def456|Alice Dev|2025-06-15T10:30:00+00:00|feat: add login endpoint\n"
    "789012ghi345|Bob Dev|2025-06-14T09:00:00+00:00|fix: correct password hashing\n"
)

MERGE_LOG_OUTPUT = "merge111aaa|Alice Dev|2025-06-15T11:00:00+00:00|Merge pull request #42 from feature/login\n"

TAG_OUTPUT = (
    "v2.1.0|2025-06-10T14:00:00+00:00|Release 2.1.0\n"
    "v2.0.0|2025-05-01T10:00:00+00:00|Release 2.0.0\n"
    "v1.0.0|2024-12-01T08:00:00+00:00|Initial release\n"
)

BRANCH_OUTPUT = (
    "main|2025-06-15T12:00:00+00:00\n"
    "dev|2025-06-14T11:00:00+00:00\n"
    "story/s479.1/control-mapping|2025-06-10T09:00:00+00:00\n"
)


class TestGitEvidenceExtractorCommits:
    """Tests for commit extraction."""

    def test_extract_commits_produces_evidence_items(self) -> None:
        mapping = _make_mapping()
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=GIT_LOG_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        assert len(items) == 2
        assert all(isinstance(i, EvidenceItem) for i in items)

    def test_commit_evidence_fields(self) -> None:
        mapping = _make_mapping()
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=GIT_LOG_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        first = items[0]
        assert first.control_id == "A.8.32"
        assert first.control_name == "Change management"
        assert first.evidence_type == "git"
        assert first.source_ref == "abc123def456"
        assert "Alice Dev" in first.description
        assert "feat: add login endpoint" in first.title

    def test_date_range_passed_to_git(self) -> None:
        mapping = _make_mapping()
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            extractor.extract(
                mapping, start_date=date(2025, 3, 1), end_date=date(2025, 3, 31)
            )

        call_args = mock_run.call_args[0][0]
        assert "--after=2025-03-01" in call_args
        assert "--before=2025-03-31" in call_args

    def test_empty_output_returns_empty_list(self) -> None:
        mapping = _make_mapping()
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            items = extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        assert items == []

    def test_malformed_line_skipped(self) -> None:
        mapping = _make_mapping()
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        malformed = "this-is-not-valid-format\nabc123|Alice|2025-06-15T10:30:00+00:00|good commit\n"
        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=malformed, stderr=""
            )
            items = extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        assert len(items) == 1
        assert items[0].source_ref == "abc123"


class TestGitEvidenceExtractorMergeCommits:
    """Tests for merge commit extraction."""

    def test_merge_commits_extracted(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.32", "Change management", "pull_requests")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=MERGE_LOG_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        assert len(items) == 1
        assert items[0].source_ref == "merge111aaa"
        assert "Merge pull request" in items[0].title

    def test_merge_commits_use_merges_flag(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.32", "Change management", "pull_requests")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        call_args = mock_run.call_args[0][0]
        assert "--merges" in call_args


class TestGitEvidenceExtractorNonGitControls:
    """Test that non-git controls are skipped."""

    def test_session_controls_ignored(self) -> None:
        mapping = ControlMapping(
            version="1.0",
            standard="ISO 27001:2022",
            controls=[
                ControlConfig(
                    id="A.8.15",
                    name="Logging",
                    description="Session-only control",
                    evidence_sources=[
                        EvidenceSourceConfig(
                            type="session",
                            extractor="journals",
                            description="Session journals",
                        ),
                    ],
                ),
            ],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            items = extractor.extract(
                mapping, start_date=date(2025, 6, 1), end_date=date(2025, 6, 30)
            )

        assert items == []
        mock_run.assert_not_called()

    def test_none_dates_omit_date_flags(self) -> None:
        mapping = _make_mapping()
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            extractor.extract(mapping)

        call_args = mock_run.call_args[0][0]
        assert not any(arg.startswith("--after") for arg in call_args)
        assert not any(arg.startswith("--before") for arg in call_args)


class TestGitEvidenceExtractorTags:
    """Tests for tag extraction."""

    def test_tags_extracted(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "tags")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=TAG_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
            )

        # v2.1.0 and v2.0.0 are in range; v1.0.0 is 2024 (out of range)
        assert len(items) == 2
        assert items[0].source_ref == "v2.1.0"
        assert items[1].source_ref == "v2.0.0"

    def test_tag_evidence_fields(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "tags")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=TAG_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
            )

        first = items[0]
        assert first.control_id == "A.8.9"
        assert first.evidence_type == "git"
        assert "Release 2.1.0" in first.title

    def test_tags_date_filtered_post_extraction(self) -> None:
        """Tags don't support --after/--before; date filtering happens post-extraction."""
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "tags")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=TAG_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping,
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 30),
            )

        # Only v2.1.0 (2025-06-10) is in June
        assert len(items) == 1
        assert items[0].source_ref == "v2.1.0"

    def test_tags_no_date_range_returns_all(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "tags")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=TAG_OUTPUT, stderr=""
            )
            items = extractor.extract(mapping)

        assert len(items) == 3

    def test_tags_empty_output(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "tags")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            items = extractor.extract(
                mapping,
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
            )

        assert items == []


class TestGitEvidenceExtractorBranches:
    """Tests for branch extraction."""

    def test_branches_extracted(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "branches")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=BRANCH_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping,
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 30),
            )

        assert len(items) == 3
        assert all(i.evidence_type == "git" for i in items)

    def test_branch_evidence_fields(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "branches")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=BRANCH_OUTPUT, stderr=""
            )
            items = extractor.extract(
                mapping,
                start_date=date(2025, 6, 1),
                end_date=date(2025, 6, 30),
            )

        first = items[0]
        assert first.control_id == "A.8.9"
        assert first.source_ref == "main"
        assert "main" in first.title

    def test_branches_empty_output(self) -> None:
        mapping = _make_mapping(
            extractors=[("A.8.9", "Configuration management", "branches")],
        )
        extractor = GitEvidenceExtractor(repo_path=Path("/fake/repo"))

        with patch("raise_cli.compliance.extractors.git.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=[], returncode=0, stdout="", stderr=""
            )
            items = extractor.extract(mapping)

        assert items == []
