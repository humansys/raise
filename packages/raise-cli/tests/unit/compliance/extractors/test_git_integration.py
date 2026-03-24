"""Integration test: GitEvidenceExtractor against the actual raise-commons repo."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from raise_cli.compliance.extractors.git import GitEvidenceExtractor
from raise_cli.compliance.loader import load_control_mapping


def _git_root() -> Path:
    """Find the git repository root."""
    path = Path(__file__).resolve()
    while path != path.parent:
        if (path / ".git").exists():
            return path
        path = path.parent
    msg = "Could not find git repository root"
    raise RuntimeError(msg)


class TestGitEvidenceExtractorIntegration:
    """Integration tests against the real raise-commons git history."""

    def test_extract_produces_non_empty_results(self) -> None:
        repo = _git_root()
        mapping = load_control_mapping()
        extractor = GitEvidenceExtractor(repo_path=repo)

        items = extractor.extract(
            mapping,
            start_date=date(2020, 1, 1),
            end_date=date(2030, 12, 31),
        )

        assert len(items) > 0

    def test_at_least_one_commit_evidence(self) -> None:
        repo = _git_root()
        mapping = load_control_mapping()
        extractor = GitEvidenceExtractor(repo_path=repo)

        items = extractor.extract(
            mapping,
            start_date=date(2020, 1, 1),
            end_date=date(2030, 12, 31),
        )

        commit_items = [i for i in items if "Commit by" in i.description]
        assert len(commit_items) > 0

    def test_all_items_have_git_evidence_type(self) -> None:
        repo = _git_root()
        mapping = load_control_mapping()
        extractor = GitEvidenceExtractor(repo_path=repo)

        items = extractor.extract(
            mapping,
            start_date=date(2020, 1, 1),
            end_date=date(2030, 12, 31),
        )

        assert all(i.evidence_type == "git" for i in items)

    def test_all_items_have_required_fields(self) -> None:
        repo = _git_root()
        mapping = load_control_mapping()
        extractor = GitEvidenceExtractor(repo_path=repo)

        items = extractor.extract(
            mapping,
            start_date=date(2020, 1, 1),
            end_date=date(2030, 12, 31),
        )

        for item in items:
            assert item.control_id
            assert item.control_name
            assert item.title is not None
            assert item.description is not None
            assert item.source_ref
            assert item.timestamp is not None
