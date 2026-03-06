"""Tests for skill parser."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.skills.parser import ParseError, parse_frontmatter, parse_skill


class TestParseFrontmatter:
    """Tests for frontmatter extraction."""

    def test_parse_valid_frontmatter(self) -> None:
        """Parse valid YAML frontmatter."""
        content = dedent("""\
            ---
            name: test-skill
            description: A test skill
            license: MIT
            ---
            # Body content
        """)
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "test-skill"
        assert frontmatter["description"] == "A test skill"
        assert "# Body content" in body

    def test_parse_multiline_description(self) -> None:
        """Parse frontmatter with multiline description."""
        content = dedent("""\
            ---
            name: rai-session-start
            description: >
              Begin a session by loading memory, analyzing progress,
              and proposing focused work.
            license: MIT
            ---
            # Session Start
        """)
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "rai-session-start"
        assert "loading memory" in frontmatter["description"]

    def test_parse_with_metadata(self) -> None:
        """Parse frontmatter with nested metadata."""
        content = dedent("""\
            ---
            name: rai-story-plan
            description: Plan a feature
            metadata:
              raise.work_cycle: story
              raise.version: "1.0.0"
            ---
            # Story Plan
        """)
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["metadata"]["raise.work_cycle"] == "story"
        assert frontmatter["metadata"]["raise.version"] == "1.0.0"

    def test_parse_with_hooks(self) -> None:
        """Parse frontmatter with hooks structure."""
        content = dedent("""\
            ---
            name: test-skill
            description: Test
            hooks:
              Stop:
                - hooks:
                    - type: command
                      command: echo done
            ---
            # Body
        """)
        frontmatter, body = parse_frontmatter(content)
        assert "Stop" in frontmatter["hooks"]
        assert frontmatter["hooks"]["Stop"][0]["hooks"][0]["command"] == "echo done"

    def test_missing_frontmatter(self) -> None:
        """Raise error when frontmatter is missing."""
        content = "# Just markdown\n\nNo frontmatter here."
        with pytest.raises(ParseError, match="No YAML frontmatter found"):
            parse_frontmatter(content)

    def test_unclosed_frontmatter(self) -> None:
        """Raise error when frontmatter is not closed."""
        content = dedent("""\
            ---
            name: test-skill
            description: Test
            # Missing closing ---
        """)
        with pytest.raises(ParseError, match="Unclosed frontmatter"):
            parse_frontmatter(content)

    def test_invalid_yaml(self) -> None:
        """Raise error for invalid YAML."""
        content = dedent("""\
            ---
            name: test-skill
            description: [invalid: yaml: here
            ---
            # Body
        """)
        with pytest.raises(ParseError, match="Invalid YAML"):
            parse_frontmatter(content)

    def test_empty_frontmatter(self) -> None:
        """Handle empty frontmatter."""
        content = dedent("""\
            ---
            ---
            # Body only
        """)
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}
        assert "# Body only" in body


class TestParseSkill:
    """Tests for complete skill parsing."""

    def test_parse_minimal_skill(self, tmp_path: Path) -> None:
        """Parse a minimal valid skill file."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            dedent("""\
            ---
            name: test-skill
            description: A minimal test skill
            ---
            # Test Skill

            ## Purpose

            This is a test.
        """)
        )

        skill = parse_skill(skill_file)
        assert skill.name == "test-skill"
        assert skill.frontmatter.description == "A minimal test skill"
        assert "# Test Skill" in skill.body
        assert str(skill_file) in skill.path

    def test_parse_full_skill(self, tmp_path: Path) -> None:
        """Parse a complete skill with all fields."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            dedent("""\
            ---
            name: rai-session-start
            description: >
              Begin a session by loading memory.
            license: MIT
            metadata:
              raise.work_cycle: session
              raise.frequency: per-session
              raise.fase: "start"
              raise.prerequisites: ""
              raise.next: rai-session-close
              raise.gate: ""
              raise.adaptable: "true"
              raise.version: "3.0.0"
            hooks:
              Stop:
                - hooks:
                    - type: command
                      command: "RAISE_SKILL_NAME=rai-session-start script.sh"
            ---
            # Session Start

            ## Purpose

            Load context and propose work.
        """)
        )

        skill = parse_skill(skill_file)
        assert skill.name == "rai-session-start"
        assert skill.version == "3.0.0"
        assert skill.lifecycle == "session"
        assert skill.frontmatter.metadata is not None
        assert skill.frontmatter.metadata.next == "rai-session-close"
        assert skill.frontmatter.hooks is not None
        assert "Stop" in skill.frontmatter.hooks

    def test_parse_skill_file_not_found(self, tmp_path: Path) -> None:
        """Raise error when skill file doesn't exist."""
        skill_file = tmp_path / "nonexistent" / "SKILL.md"
        with pytest.raises(ParseError, match="Skill file not found"):
            parse_skill(skill_file)

    def test_parse_skill_with_path_string(self, tmp_path: Path) -> None:
        """Parse skill from string path."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            dedent("""\
            ---
            name: test-skill
            description: Test
            ---
            # Body
        """)
        )

        skill = parse_skill(str(skill_file))
        assert skill.name == "test-skill"
