"""Integration tests for ISO 27001 control mapping.

Verifies the default bundled config loads correctly and matches
the expected control structure from the design spec.
"""

from __future__ import annotations

from raise_cli.compliance.loader import load_control_mapping
from raise_cli.compliance.models import ControlConfig, ControlMapping


class TestDefaultControlMapping:
    """End-to-end tests for the shipped controls.yaml."""

    def test_exactly_eight_controls(self) -> None:
        mapping = load_control_mapping()
        assert len(mapping.controls) == 8

    def test_every_control_has_evidence_sources(self) -> None:
        mapping = load_control_mapping()
        for control in mapping.controls:
            assert len(control.evidence_sources) >= 1, (
                f"{control.id} has no evidence sources"
            )

    def test_all_evidence_source_types_valid(self) -> None:
        mapping = load_control_mapping()
        valid_types = {"git", "gate", "session"}
        for control in mapping.controls:
            for source in control.evidence_sources:
                assert source.type in valid_types, (
                    f"{control.id}: invalid type '{source.type}'"
                )

    def test_a84_access_to_source_code(self) -> None:
        mapping = load_control_mapping()
        control = _find_control(mapping, "A.8.4")
        assert control is not None, "A.8.4 not found"
        assert any(s.type == "git" for s in control.evidence_sources)
        assert any(s.extractor == "permissions" for s in control.evidence_sources)

    def test_a825_secure_development_lifecycle(self) -> None:
        mapping = load_control_mapping()
        control = _find_control(mapping, "A.8.25")
        assert control is not None, "A.8.25 not found"
        extractors = {s.extractor for s in control.evidence_sources}
        assert "tests" in extractors
        assert "type_check" in extractors
        assert "lint" in extractors

    def test_a832_change_management(self) -> None:
        mapping = load_control_mapping()
        control = _find_control(mapping, "A.8.32")
        assert control is not None, "A.8.32 not found"
        extractors = {s.extractor for s in control.evidence_sources}
        assert "commits" in extractors
        assert "pull_requests" in extractors

    def test_control_ids_match_expected_set(self) -> None:
        mapping = load_control_mapping()
        ids = {c.id for c in mapping.controls}
        expected = {
            "A.8.4",
            "A.8.9",
            "A.8.15",
            "A.8.25",
            "A.8.26",
            "A.8.27",
            "A.8.32",
            "A.8.33",
        }
        assert ids == expected


def _find_control(mapping: ControlMapping, control_id: str) -> ControlConfig | None:
    """Find a control by ID in a mapping."""
    for control in mapping.controls:
        if control.id == control_id:
            return control
    return None
