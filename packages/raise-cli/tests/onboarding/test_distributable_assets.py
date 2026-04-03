"""Tests that distributable assets contain no project-specific leakage.

These tests guard against raise-commons-specific values (branch names,
developer names, etc.) leaking into assets that get distributed to
end users via raise-cli (PyPI).

See: RAISE-203
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

# Paths to distributable assets (relative to repo root)
RAI_BASE = Path(__file__).parent.parent.parent / "src" / "raise_cli" / "rai_base"
SKILLS_BASE = Path(__file__).parent.parent.parent / "src" / "raise_cli" / "skills_base"


class TestMethodologyYaml:
    """Ensure methodology.yaml template has no hardcoded branch names."""

    @pytest.fixture
    def methodology(self) -> dict:
        """Load methodology.yaml."""
        path = RAI_BASE / "framework" / "methodology.yaml"
        assert path.exists(), f"methodology.yaml not found at {path}"
        with open(path) as f:
            return yaml.safe_load(f)

    def test_no_hardcoded_v2_in_structure(self, methodology: dict) -> None:
        """Branch structure must use placeholder, not literal 'v2'."""
        structure = methodology.get("branches", {}).get("structure", "")
        assert "v2" not in structure, (
            "methodology.yaml branches.structure contains hardcoded 'v2'"
        )

    def test_no_hardcoded_v2_in_flow(self, methodology: dict) -> None:
        """Branch flow items must use placeholder, not literal 'v2'."""
        flow = methodology.get("branches", {}).get("flow", [])
        for item in flow:
            assert "v2" not in item, (
                f"methodology.yaml branches.flow contains hardcoded 'v2': {item}"
            )

    def test_uses_development_branch_placeholder(self, methodology: dict) -> None:
        """Branch section must use {development_branch} placeholder."""
        structure = methodology.get("branches", {}).get("structure", "")
        assert "{development_branch}" in structure, (
            "methodology.yaml branches.structure missing {development_branch} placeholder"
        )

    def test_flow_uses_development_branch_placeholder(self, methodology: dict) -> None:
        """Flow items must use {development_branch} placeholder."""
        flow = methodology.get("branches", {}).get("flow", [])
        has_placeholder = any("{development_branch}" in item for item in flow)
        assert has_placeholder, (
            "methodology.yaml branches.flow missing {development_branch} placeholder"
        )


class TestSkillsBaseTemplates:
    """Ensure skills_base templates have no personal name leakage."""

    def test_no_emilio_in_session_close(self) -> None:
        """rai-session-close SKILL.md must not reference 'Emilio' as example user."""
        path = SKILLS_BASE / "rai-session-close" / "SKILL.md"
        assert path.exists(), f"SKILL.md not found at {path}"
        content = path.read_text(encoding="utf-8")
        assert "Emilio" not in content, (
            "rai-session-close/SKILL.md still references 'Emilio'"
        )

    def test_no_personal_names_in_skill_examples(self) -> None:
        """No skill template should use personal names in user-facing examples."""
        # Names that should not appear as example users in templates
        # (author credits are excluded — they're legitimate)
        for skill_dir in SKILLS_BASE.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            # Check for "Emilio" not in author/credit context
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "Emilio" in line:
                    # Allow in author credits (lines with "author", "credit", "@")
                    lower = line.lower()
                    is_credit = any(
                        word in lower
                        for word in ("author", "credit", "@", "created by")
                    )
                    assert is_credit, (
                        f"{skill_dir.name}/SKILL.md line {i + 1} references 'Emilio' "
                        f"outside of author credits: {line.strip()}"
                    )


class TestMigrationFunction:
    """Ensure migration module has no project-specific naming."""

    def test_no_emilio_function_name(self) -> None:
        """Migration module must not export 'migrate_emilio_profile'."""
        from raise_cli.onboarding import __all__

        assert "migrate_emilio_profile" not in __all__, (
            "onboarding.__all__ still exports 'migrate_emilio_profile'"
        )
        assert "migrate_developer_profile" in __all__, (
            "onboarding.__all__ missing 'migrate_developer_profile'"
        )

    def test_migrate_developer_profile_importable(self) -> None:
        """migrate_developer_profile must be importable from onboarding."""
        from raise_cli.onboarding import migrate_developer_profile

        assert callable(migrate_developer_profile)

    def test_default_name_is_generic(self) -> None:
        """Default name parameter must be generic, not 'Emilio'."""
        import inspect

        from raise_cli.onboarding.migration import migrate_developer_profile

        sig = inspect.signature(migrate_developer_profile)
        default_name = sig.parameters["name"].default
        assert default_name != "Emilio", (
            f"migrate_developer_profile default name is still 'Emilio': {default_name}"
        )
