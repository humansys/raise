"""Tests for EvidenceItem model."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from raise_cli.compliance.evidence import EvidenceItem


class TestEvidenceItem:
    """Tests for EvidenceItem Pydantic model."""

    @pytest.fixture
    def sample_item(self) -> EvidenceItem:
        return EvidenceItem(
            control_id="A.8.32",
            control_name="Change management",
            evidence_type="git",
            title="Commit abc123",
            description="feat: add login endpoint",
            timestamp=datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC),
            source_ref="abc123",
        )

    def test_valid_creation(self, sample_item: EvidenceItem) -> None:
        assert sample_item.control_id == "A.8.32"
        assert sample_item.control_name == "Change management"
        assert sample_item.evidence_type == "git"
        assert sample_item.title == "Commit abc123"
        assert sample_item.description == "feat: add login endpoint"
        assert sample_item.source_ref == "abc123"
        assert sample_item.url is None

    def test_valid_with_url(self) -> None:
        item = EvidenceItem(
            control_id="A.8.32",
            control_name="Change management",
            evidence_type="git",
            title="PR #42",
            description="Review approved",
            timestamp=datetime(2025, 6, 1, tzinfo=UTC),
            source_ref="pr-42",
            url="https://github.com/org/repo/pull/42",
        )
        assert item.url == "https://github.com/org/repo/pull/42"

    def test_git_evidence_type(self, sample_item: EvidenceItem) -> None:
        assert sample_item.evidence_type == "git"

    def test_gate_evidence_type(self) -> None:
        item = EvidenceItem(
            control_id="A.8.25",
            control_name="Secure development lifecycle",
            evidence_type="gate",
            title="Test gate passed",
            description="All 150 tests passed",
            timestamp=datetime(2025, 6, 1, tzinfo=UTC),
            source_ref="gate-tests-20250601",
        )
        assert item.evidence_type == "gate"

    def test_session_evidence_type(self) -> None:
        item = EvidenceItem(
            control_id="A.8.15",
            control_name="Logging",
            evidence_type="session",
            title="Session journal entry",
            description="Design review decision recorded",
            timestamp=datetime(2025, 6, 1, tzinfo=UTC),
            source_ref="session-2025-06-01",
        )
        assert item.evidence_type == "session"

    def test_invalid_evidence_type_rejected(self) -> None:
        with pytest.raises(ValidationError, match="evidence_type"):
            EvidenceItem(
                control_id="A.8.32",
                control_name="Change management",
                evidence_type="invalid",  # type: ignore[arg-type]
                title="title",
                description="desc",
                timestamp=datetime(2025, 6, 1, tzinfo=UTC),
                source_ref="ref",
            )

    def test_missing_control_id_rejected(self) -> None:
        with pytest.raises(ValidationError, match="control_id"):
            EvidenceItem(
                control_name="Change management",
                evidence_type="git",
                title="title",
                description="desc",
                timestamp=datetime(2025, 6, 1, tzinfo=UTC),
                source_ref="ref",
            )  # type: ignore[call-arg]

    def test_missing_title_rejected(self) -> None:
        with pytest.raises(ValidationError, match="title"):
            EvidenceItem(
                control_id="A.8.32",
                control_name="Change management",
                evidence_type="git",
                description="desc",
                timestamp=datetime(2025, 6, 1, tzinfo=UTC),
                source_ref="ref",
            )  # type: ignore[call-arg]

    def test_missing_timestamp_rejected(self) -> None:
        with pytest.raises(ValidationError, match="timestamp"):
            EvidenceItem(
                control_id="A.8.32",
                control_name="Change management",
                evidence_type="git",
                title="title",
                description="desc",
                source_ref="ref",
            )  # type: ignore[call-arg]

    def test_frozen(self, sample_item: EvidenceItem) -> None:
        with pytest.raises(ValidationError):
            sample_item.control_id = "A.8.99"  # type: ignore[misc]
