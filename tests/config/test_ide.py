"""Tests for IDE configuration model and factory."""

from __future__ import annotations

import pytest

from rai_cli.config.ide import (
    IDE_CONFIGS,
    IdeConfig,
    IdeType,
    get_ide_config,
)


class TestIdeConfig:
    """Tests for IdeConfig model."""

    def test_claude_config_fields(self) -> None:
        """Claude config has correct paths."""
        config = IdeConfig(
            ide_type="claude",
            skills_dir=".claude/skills",
            instructions_file="CLAUDE.md",
        )
        assert config.ide_type == "claude"
        assert config.skills_dir == ".claude/skills"
        assert config.instructions_file == "CLAUDE.md"
        assert config.workflows_dir is None

    def test_antigravity_config_fields(self) -> None:
        """Antigravity config has correct paths."""
        config = IdeConfig(
            ide_type="antigravity",
            skills_dir=".agent/skills",
            instructions_file=".agent/rules/raise.md",
            workflows_dir=".agent/workflows",
        )
        assert config.ide_type == "antigravity"
        assert config.skills_dir == ".agent/skills"
        assert config.instructions_file == ".agent/rules/raise.md"
        assert config.workflows_dir == ".agent/workflows"

    def test_workflows_dir_defaults_to_none(self) -> None:
        """workflows_dir defaults to None when not provided."""
        config = IdeConfig(
            ide_type="claude",
            skills_dir=".claude/skills",
            instructions_file="CLAUDE.md",
        )
        assert config.workflows_dir is None

    def test_frozen_immutability(self) -> None:
        """IdeConfig is frozen — cannot mutate after creation."""
        config = IdeConfig(
            ide_type="claude",
            skills_dir=".claude/skills",
            instructions_file="CLAUDE.md",
        )
        with pytest.raises(Exception):
            config.skills_dir = ".other/skills"  # type: ignore[misc]

    def test_invalid_ide_type_rejected(self) -> None:
        """Invalid IDE type is rejected by Pydantic validation."""
        with pytest.raises(Exception):
            IdeConfig(
                ide_type="invalid",  # type: ignore[arg-type]
                skills_dir=".invalid/skills",
                instructions_file="INVALID.md",
            )


class TestIdeConfigs:
    """Tests for IDE_CONFIGS registry."""

    def test_claude_in_registry(self) -> None:
        """Claude config exists in registry."""
        assert "claude" in IDE_CONFIGS

    def test_antigravity_in_registry(self) -> None:
        """Antigravity config exists in registry."""
        assert "antigravity" in IDE_CONFIGS

    def test_claude_registry_values(self) -> None:
        """Claude registry entry has correct values."""
        config = IDE_CONFIGS["claude"]
        assert config.ide_type == "claude"
        assert config.skills_dir == ".claude/skills"
        assert config.instructions_file == "CLAUDE.md"
        assert config.workflows_dir is None

    def test_antigravity_registry_values(self) -> None:
        """Antigravity registry entry has correct values."""
        config = IDE_CONFIGS["antigravity"]
        assert config.ide_type == "antigravity"
        assert config.skills_dir == ".agent/skills"
        assert config.instructions_file == ".agent/rules/raise.md"
        assert config.workflows_dir == ".agent/workflows"

    def test_registry_covers_all_ide_types(self) -> None:
        """Every IdeType has an entry in IDE_CONFIGS."""
        expected: set[IdeType] = {"claude", "antigravity"}
        assert set(IDE_CONFIGS.keys()) == expected


class TestGetIdeConfig:
    """Tests for get_ide_config factory function."""

    def test_returns_claude_config(self) -> None:
        """Factory returns correct config for claude."""
        config = get_ide_config("claude")
        assert config.ide_type == "claude"
        assert config.skills_dir == ".claude/skills"

    def test_returns_antigravity_config(self) -> None:
        """Factory returns correct config for antigravity."""
        config = get_ide_config("antigravity")
        assert config.ide_type == "antigravity"
        assert config.skills_dir == ".agent/skills"

    def test_defaults_to_claude(self) -> None:
        """Factory defaults to claude when called with no args."""
        config = get_ide_config()
        assert config.ide_type == "claude"

    def test_returns_same_instance_from_registry(self) -> None:
        """Factory returns the registry instance (not a copy)."""
        config = get_ide_config("claude")
        assert config is IDE_CONFIGS["claude"]
