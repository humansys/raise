"""Tests for CLAUDE.md generation backward-compat aliases."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.onboarding.claudemd import ClaudeMdGenerator, generate_claude_md
from raise_cli.onboarding.detection import DetectionResult, ProjectType

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def brownfield_detection() -> DetectionResult:
    """Detection result for a brownfield project."""
    return DetectionResult(
        project_type=ProjectType.BROWNFIELD,
        code_file_count=25,
    )


IDENTITY_CONTENT = dedent("""\
    values:
      - number: 1
        name: "Honesty over Agreement"
        description: "tell you when you're wrong"

    boundaries:
      will:
        - "push back on bad ideas"
      wont:
        - "pretend certainty I don't have"
""")

METHODOLOGY_CONTENT = dedent("""\
    version: 1

    lifecycle:
      session:
        phases: [start, work, close]
        flow: "/rai-session-start → [work] → /rai-session-close"

    gates:
      quality:
        - gate: Tests pass
          when: Before any commit

    principles:
      process:
        - name: TDD Always
          rule: RED-GREEN-REFACTOR, no exceptions
          rationale: Tests are specification

    branches:
      flow:
        - "Stories branch from and merge to dev"
""")

MANIFEST_CONTENT = dedent("""\
    version: '1.0'
    project:
      name: my-project
    branches:
      development: dev
      main: main
""")


@pytest.fixture
def raise_project_dir(tmp_path: Path) -> Path:
    """Create a tmp directory with .raise/ structure for testing."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()

    identity_dir = raise_dir / "rai" / "identity"
    identity_dir.mkdir(parents=True)
    (identity_dir / "core.yaml").write_text(IDENTITY_CONTENT)

    framework_dir = raise_dir / "rai" / "framework"
    framework_dir.mkdir(parents=True)
    (framework_dir / "methodology.yaml").write_text(METHODOLOGY_CONTENT)

    (raise_dir / "manifest.yaml").write_text(MANIFEST_CONTENT)

    return tmp_path


# =============================================================================
# Backward-compat alias tests
# =============================================================================


class TestClaudeMdGenerator:
    """Tests for ClaudeMdGenerator backward-compat alias."""

    def test_generates_markdown_string(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should generate a markdown string via backward-compat alias."""
        generator = ClaudeMdGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Generated from .raise/ canonical source" in result


class TestConvenienceFunction:
    """Tests for generate_claude_md convenience function."""

    def test_returns_markdown_string(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """generate_claude_md should return markdown string."""
        result = generate_claude_md(
            project_name="my-api",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert isinstance(result, str)
        assert "Generated from .raise/ canonical source" in result
