"""Tests for compliance config loader."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from raise_cli.compliance.loader import load_control_mapping


class TestLoadControlMapping:
    """Tests for load_control_mapping function."""

    def test_load_default_config(self) -> None:
        """Default config loads without arguments."""
        mapping = load_control_mapping()
        assert mapping.version == "1.0"
        assert mapping.standard == "ISO 27001:2022"
        assert len(mapping.controls) == 8

    def test_load_custom_path(self, tmp_path: Path) -> None:
        """Custom YAML path loads correctly."""
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            "version: '2.0'\n"
            "standard: 'Custom Standard'\n"
            "controls:\n"
            "  - id: 'C.1'\n"
            "    name: 'Custom control'\n"
            "    description: 'A custom control'\n"
            "    evidence_sources:\n"
            "      - type: git\n"
            "        extractor: commits\n"
            "        description: 'Commit history'\n"
        )
        mapping = load_control_mapping(custom)
        assert mapping.version == "2.0"
        assert mapping.standard == "Custom Standard"
        assert len(mapping.controls) == 1

    def test_missing_path_raises_file_not_found(self, tmp_path: Path) -> None:
        """Missing file raises FileNotFoundError."""
        missing = tmp_path / "does_not_exist.yaml"
        with pytest.raises(FileNotFoundError):
            load_control_mapping(missing)

    def test_invalid_yaml_raises_validation_error(self, tmp_path: Path) -> None:
        """Invalid YAML content raises ValidationError."""
        bad = tmp_path / "bad.yaml"
        bad.write_text(
            "version: '1.0'\n"
            "standard: 'ISO 27001:2022'\n"
            "controls:\n"
            "  - id: 'A.8.32'\n"
            "    name: 'Change management'\n"
            "    description: 'desc'\n"
            "    evidence_sources:\n"
            "      - type: invalid_type\n"
            "        extractor: x\n"
            "        description: y\n"
        )
        with pytest.raises(ValidationError):
            load_control_mapping(bad)

    def test_default_controls_have_required_fields(self) -> None:
        """Every control in default config has id, name, description."""
        mapping = load_control_mapping()
        for control in mapping.controls:
            assert control.id, "Control must have an id"
            assert control.name, "Control must have a name"
            assert control.description, "Control must have a description"
