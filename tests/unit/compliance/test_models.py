"""Tests for compliance Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from raise_cli.compliance.models import (
    ControlConfig,
    ControlMapping,
    EvidenceSourceConfig,
)


class TestEvidenceSourceConfig:
    """Tests for EvidenceSourceConfig model."""

    def test_valid_git_source(self) -> None:
        source = EvidenceSourceConfig(
            type="git",
            extractor="commits",
            description="Commit history",
        )
        assert source.type == "git"
        assert source.extractor == "commits"
        assert source.description == "Commit history"

    def test_valid_gate_source(self) -> None:
        source = EvidenceSourceConfig(
            type="gate",
            extractor="tests",
            description="Test results",
        )
        assert source.type == "gate"

    def test_valid_session_source(self) -> None:
        source = EvidenceSourceConfig(
            type="session",
            extractor="journals",
            description="Session journals",
        )
        assert source.type == "session"

    def test_invalid_type_rejected(self) -> None:
        with pytest.raises(ValidationError, match="type"):
            EvidenceSourceConfig(
                type="invalid",  # type: ignore[arg-type]
                extractor="foo",
                description="bar",
            )

    def test_missing_extractor_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extractor"):
            EvidenceSourceConfig(
                type="git",
                description="bar",
            )  # type: ignore[call-arg]

    def test_missing_description_rejected(self) -> None:
        with pytest.raises(ValidationError, match="description"):
            EvidenceSourceConfig(
                type="git",
                extractor="foo",
            )  # type: ignore[call-arg]

    def test_frozen(self) -> None:
        source = EvidenceSourceConfig(
            type="git",
            extractor="commits",
            description="Commit history",
        )
        with pytest.raises(ValidationError):
            source.type = "gate"  # type: ignore[misc]


class TestControlConfig:
    """Tests for ControlConfig model."""

    def test_valid_control(self) -> None:
        control = ControlConfig(
            id="A.8.32",
            name="Change management",
            description="Changes shall be subject to change management.",
            evidence_sources=[
                EvidenceSourceConfig(
                    type="git",
                    extractor="commits",
                    description="Commit history",
                ),
            ],
        )
        assert control.id == "A.8.32"
        assert control.name == "Change management"
        assert len(control.evidence_sources) == 1

    def test_missing_id_rejected(self) -> None:
        with pytest.raises(ValidationError, match="id"):
            ControlConfig(
                name="Change management",
                description="desc",
                evidence_sources=[],
            )  # type: ignore[call-arg]

    def test_missing_name_rejected(self) -> None:
        with pytest.raises(ValidationError, match="name"):
            ControlConfig(
                id="A.8.32",
                description="desc",
                evidence_sources=[],
            )  # type: ignore[call-arg]

    def test_empty_evidence_sources_allowed(self) -> None:
        """Empty list is structurally valid (content validation is separate)."""
        control = ControlConfig(
            id="A.8.32",
            name="Change management",
            description="desc",
            evidence_sources=[],
        )
        assert control.evidence_sources == []


class TestControlMapping:
    """Tests for ControlMapping model."""

    def test_valid_mapping(self) -> None:
        mapping = ControlMapping(
            version="1.0",
            standard="ISO 27001:2022",
            controls=[
                ControlConfig(
                    id="A.8.32",
                    name="Change management",
                    description="desc",
                    evidence_sources=[
                        EvidenceSourceConfig(
                            type="git",
                            extractor="commits",
                            description="Commit history",
                        ),
                    ],
                ),
            ],
        )
        assert mapping.version == "1.0"
        assert mapping.standard == "ISO 27001:2022"
        assert len(mapping.controls) == 1

    def test_missing_version_rejected(self) -> None:
        with pytest.raises(ValidationError, match="version"):
            ControlMapping(
                standard="ISO 27001:2022",
                controls=[],
            )  # type: ignore[call-arg]

    def test_missing_standard_rejected(self) -> None:
        with pytest.raises(ValidationError, match="standard"):
            ControlMapping(
                version="1.0",
                controls=[],
            )  # type: ignore[call-arg]

    def test_nested_validation_propagates(self) -> None:
        """Invalid nested models should cause ValidationError."""
        with pytest.raises(ValidationError):
            ControlMapping(
                version="1.0",
                standard="ISO 27001:2022",
                controls=[
                    {  # type: ignore[list-item]
                        "id": "A.8.32",
                        "name": "Change management",
                        "description": "desc",
                        "evidence_sources": [
                            {
                                "type": "bad_type",
                                "extractor": "x",
                                "description": "y",
                            },
                        ],
                    },
                ],
            )
