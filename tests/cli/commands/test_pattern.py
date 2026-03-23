"""Tests for pattern CLI commands.

The pattern group owns commands that write to pattern memory: add, reinforce.
These were extracted from memory.py in S247.2 (RAISE-247).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.memory.models import MemoryScope
from raise_cli.memory.writer import PatternInput, append_pattern

runner = CliRunner()


@pytest.fixture
def patterns_file(tmp_path: Path) -> Path:
    """Create a patterns.jsonl file with one pattern for reinforce tests."""
    memory_dir = tmp_path / ".raise" / "rai" / "memory"
    memory_dir.mkdir(parents=True)
    pattern_data = {
        "id": "PAT-E-001",
        "content": "Test pattern for reinforcement",
        "sub_type": "process",
        "context": ["testing"],
        "positives": 1,
        "negatives": 0,
        "evaluations": 1,
        "created": "2026-01-01",
        "learned_from": None,
    }
    pf = memory_dir / "patterns.jsonl"
    pf.write_text(json.dumps(pattern_data) + "\n", encoding="utf-8")
    return pf


# =============================================================================
# rai pattern add
# =============================================================================


class TestPatternAddCommand:
    """Tests for `rai pattern add` command."""

    def test_add_pattern_basic(self, tmp_path: Path) -> None:
        """Test basic pattern add command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Test pattern content", "-c", "testing,python"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            assert "Test pattern content" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_with_type(self, tmp_path: Path) -> None:
        """Test pattern add with explicit type."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Architecture pattern", "-t", "architecture"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_invalid_type(self, tmp_path: Path) -> None:
        """Test pattern add with invalid type fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Test", "-t", "invalid_type"],
            )

            assert result.exit_code == 7
            assert "Invalid pattern type" in result.output
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_creates_missing_dir(self, tmp_path: Path) -> None:
        """Test pattern add auto-creates project memory directory if missing (default scope)."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["pattern", "add", "Test pattern"])

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            assert memory_dir.exists()
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_with_scope_global(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test pattern add with --scope global writes to global dir."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            global_rai = tmp_path / "global_rai"
            global_rai.mkdir()
            monkeypatch.setenv("RAI_HOME", str(global_rai))
            (global_rai / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Global pattern", "--scope", "global"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            patterns_file = global_rai / "patterns.jsonl"
            content = patterns_file.read_text(encoding="utf-8")
            assert "Global pattern" in content
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_with_scope_personal(self, tmp_path: Path) -> None:
        """Test pattern add with --scope personal writes to personal dir."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            personal_dir = tmp_path / ".raise" / "rai" / "personal"
            personal_dir.mkdir(parents=True)
            (personal_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Personal pattern", "--scope", "personal"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            patterns_file = personal_dir / "patterns.jsonl"
            content = patterns_file.read_text(encoding="utf-8")
            assert "Personal pattern" in content
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_defaults_to_project_scope(self, tmp_path: Path) -> None:
        """Test pattern add without --scope writes to project dir, not personal.

        RAISE-608: default scope must be project so that the add→reinforce
        round-trip works without explicit --scope flags on both commands.
        """
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create both dirs so we can check which one gets written to
            personal_dir = tmp_path / ".raise" / "rai" / "personal"
            personal_dir.mkdir(parents=True)
            (personal_dir / "patterns.jsonl").write_text("")
            project_dir = tmp_path / ".raise" / "rai" / "memory"
            project_dir.mkdir(parents=True)
            (project_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Default scope test", "-c", "test"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            # Should write to project, not personal
            personal_content = (personal_dir / "patterns.jsonl").read_text(
                encoding="utf-8"
            )
            project_content = (project_dir / "patterns.jsonl").read_text(
                encoding="utf-8"
            )
            assert "Default scope test" in project_content
            assert "Default scope test" not in personal_content
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_invalid_scope(self, tmp_path: Path) -> None:
        """Test pattern add with invalid scope fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["pattern", "add", "Test", "--scope", "invalid"],
            )

            assert result.exit_code == 7
            assert "Invalid scope" in result.output
        finally:
            os.chdir(original_cwd)

    def test_add_then_reinforce_default_scope_round_trip(self, tmp_path: Path) -> None:
        """Regression test RAISE-608: add→reinforce round-trip works without --scope.

        Without explicit --scope, both commands must operate on the same file.
        Previously: add defaulted to personal scope, reinforce to project scope —
        so reinforce always failed with 'not found' after a default add.
        """
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            add_result = runner.invoke(
                app,
                ["pattern", "add", "Round-trip test pattern", "-c", "test"],
            )
            assert add_result.exit_code == 0
            pat_id = next(
                line.split("ID:")[1].strip()
                for line in add_result.stdout.splitlines()
                if "ID:" in line
            )

            reinforce_result = runner.invoke(
                app,
                ["pattern", "reinforce", pat_id, "--vote", "1"],
            )
            assert reinforce_result.exit_code == 0, reinforce_result.output
            assert pat_id in reinforce_result.stdout
        finally:
            os.chdir(original_cwd)


# =============================================================================
# rai pattern reinforce
# =============================================================================


class TestPatternReinforceCommand:
    """Tests for `rai pattern reinforce` command."""

    def test_reinforce_positive_vote(self, tmp_path: Path, patterns_file: Path) -> None:
        """Test reinforce with positive vote updates scores."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "1",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 0
            assert "PAT-E-001" in result.stdout
            assert "positives" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_reinforce_negative_vote(self, tmp_path: Path, patterns_file: Path) -> None:
        """Test reinforce with negative vote updates scores."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "-1",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 0
            assert "PAT-E-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_reinforce_not_applicable_vote(
        self, tmp_path: Path, patterns_file: Path
    ) -> None:
        """Test reinforce with vote=0 (N/A) does not update evaluations."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "0",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 0
            assert "N/A (not counted)" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_reinforce_invalid_vote(self, tmp_path: Path, patterns_file: Path) -> None:
        """Test reinforce with invalid vote value fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "2",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 7
            assert "Invalid vote" in result.output
        finally:
            os.chdir(original_cwd)

    def test_reinforce_pattern_not_found(
        self, tmp_path: Path, patterns_file: Path
    ) -> None:
        """Test reinforce with non-existent pattern ID fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-NOT-EXIST",
                    "--vote",
                    "1",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 4
            assert "not found" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_reinforce_patterns_file_missing(self, tmp_path: Path) -> None:
        """Test reinforce fails when patterns file does not exist."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            empty_dir = tmp_path / "empty"
            empty_dir.mkdir()
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "1",
                    "--memory-dir",
                    str(empty_dir),
                ],
            )

            assert result.exit_code == 4
            assert "not found" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_reinforce_invalid_scope(self, tmp_path: Path, patterns_file: Path) -> None:
        """Test reinforce with invalid scope fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "1",
                    "--scope",
                    "invalid",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 7
            assert "Invalid scope" in result.output
        finally:
            os.chdir(original_cwd)

    def test_reinforce_with_from_flag_updates_score(
        self, tmp_path: Path, patterns_file: Path
    ) -> None:
        """Test reinforce with --from updates the score (story_id is traceability-only, not stored in v1)."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "pattern",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "1",
                    "--from",
                    "S247.2",
                    "--memory-dir",
                    str(patterns_file.parent),
                ],
            )

            assert result.exit_code == 0
            # Fixture starts with positives=1; a second positive vote → positives=2
            assert "positives=2" in result.stdout
        finally:
            os.chdir(original_cwd)


# =============================================================================
# rai pattern promote
# =============================================================================


class TestPatternPromoteCommand:
    """Tests for `rai pattern promote` command."""

    def test_promote_pattern_moves_to_project(self, tmp_path: Path) -> None:
        """Happy path: pattern in personal, after promote it's in project and not in personal."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            personal_dir = tmp_path / ".raise" / "rai" / "personal"
            personal_dir.mkdir(parents=True)
            project_dir = tmp_path / ".raise" / "rai" / "memory"
            project_dir.mkdir(parents=True)

            pattern_data = {
                "id": "PAT-E-042",
                "content": "Always validate inputs at boundaries",
                "sub_type": "process",
                "context": ["validation"],
                "positives": 3,
                "negatives": 0,
                "evaluations": 3,
                "created": "2026-01-15",
                "learned_from": "S100.1",
            }
            other_pattern = {
                "id": "PAT-E-043",
                "content": "Another pattern that stays",
                "sub_type": "technical",
                "context": ["other"],
                "positives": 1,
                "negatives": 0,
                "evaluations": 1,
                "created": "2026-01-16",
                "learned_from": None,
            }
            personal_file = personal_dir / "patterns.jsonl"
            personal_file.write_text(
                json.dumps(pattern_data) + "\n" + json.dumps(other_pattern) + "\n",
                encoding="utf-8",
            )
            project_file = project_dir / "patterns.jsonl"
            project_file.write_text("", encoding="utf-8")

            result = runner.invoke(app, ["pattern", "promote", "PAT-E-042"])

            assert result.exit_code == 0
            assert "PAT-E-042" in result.stdout
            assert "Always validate" in result.stdout

            # Pattern should be in project file
            project_content = project_file.read_text(encoding="utf-8")
            assert "PAT-E-042" in project_content
            assert "Always validate inputs at boundaries" in project_content

            # Pattern should NOT be in personal file
            personal_content = personal_file.read_text(encoding="utf-8")
            assert "PAT-E-042" not in personal_content
            # Other pattern should still be there
            assert "PAT-E-043" in personal_content
        finally:
            os.chdir(original_cwd)

    def test_promote_pattern_not_found(self, tmp_path: Path) -> None:
        """Pattern ID doesn't exist in personal, exits with error."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            personal_dir = tmp_path / ".raise" / "rai" / "personal"
            personal_dir.mkdir(parents=True)
            personal_file = personal_dir / "patterns.jsonl"
            personal_file.write_text(
                json.dumps({"id": "PAT-E-099", "content": "other"}) + "\n",
                encoding="utf-8",
            )
            project_dir = tmp_path / ".raise" / "rai" / "memory"
            project_dir.mkdir(parents=True)
            (project_dir / "patterns.jsonl").write_text("", encoding="utf-8")

            result = runner.invoke(app, ["pattern", "promote", "PAT-E-999"])

            assert result.exit_code != 0
            assert "not found" in result.output.lower()
        finally:
            os.chdir(original_cwd)

    def test_promote_pattern_no_personal_file(self, tmp_path: Path) -> None:
        """Personal patterns.jsonl doesn't exist, exits with error."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create project dir but NOT personal dir
            project_dir = tmp_path / ".raise" / "rai" / "memory"
            project_dir.mkdir(parents=True)
            (project_dir / "patterns.jsonl").write_text("", encoding="utf-8")

            result = runner.invoke(app, ["pattern", "promote", "PAT-E-001"])

            assert result.exit_code != 0
            assert "not found" in result.output.lower()
        finally:
            os.chdir(original_cwd)


# =============================================================================
# RAISE-520 — path injection regression tests
# =============================================================================


class TestMemoryDirPathTraversal:
    """Regression tests for RAISE-520: --memory-dir path traversal sanitization.

    Tests are at the writer unit level because the CLI output does not expose
    the full path — only the filename. The fix lives in append_pattern (writer.py)
    and is verified via WriteResult.file_path.
    """

    def test_append_pattern_resolves_traversal_in_file_path(
        self, tmp_path: Path
    ) -> None:
        """append_pattern resolves ../ traversal — WriteResult.file_path is canonical."""
        sub = tmp_path / "sub"
        sub.mkdir()
        target = tmp_path / "memory"
        target.mkdir()
        traversal = tmp_path / "sub" / ".." / "memory"

        result = append_pattern(
            traversal,
            PatternInput(content="test pattern"),
            scope=MemoryScope.PROJECT,
        )

        assert result.success
        # file_path must be canonical — no .. path components
        assert "/.." not in result.file_path

    def test_append_pattern_file_written_to_canonical_location(
        self, tmp_path: Path
    ) -> None:
        """File is written to the resolved canonical path, not the traversal path."""
        sub = tmp_path / "sub"
        sub.mkdir()
        target = tmp_path / "memory"
        target.mkdir()
        traversal = tmp_path / "sub" / ".." / "memory"

        result = append_pattern(
            traversal,
            PatternInput(content="test pattern"),
            scope=MemoryScope.PROJECT,
        )

        assert result.success
        written_path = Path(result.file_path)
        # Resolved path matches the canonical target — no symlink/traversal games
        assert written_path.resolve() == (target / "patterns.jsonl").resolve()
