"""Tests for rai memory reinforce CLI command (RAISE-170)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


def _make_patterns_file(memory_dir: Path, patterns: list[dict]) -> Path:
    """Create a patterns.jsonl file in a tmp memory directory."""
    memory_dir.mkdir(parents=True, exist_ok=True)
    f = memory_dir / "patterns.jsonl"
    f.write_text(
        "\n".join(json.dumps(p) for p in patterns) + "\n",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def memory_dir(tmp_path: Path) -> Path:
    """Tmp memory dir with one pattern."""
    d = tmp_path / "memory"
    _make_patterns_file(
        d,
        [
            {
                "id": "PAT-E-001",
                "content": "planning estimation",
                "created": "2026-02-01",
            }
        ],
    )
    return d


class TestReinforceCommand:
    """Tests for `rai memory reinforce` command."""

    def test_positive_vote_succeeds(self, memory_dir: Path) -> None:
        """--vote 1 updates pattern and prints summary."""
        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-001",
                "--vote",
                "1",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "PAT-E-001" in result.output
        assert "positives=1" in result.output
        assert "evaluations=1" in result.output

    def test_negative_vote_succeeds(self, memory_dir: Path) -> None:
        """--vote -1 updates pattern and prints summary."""
        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-001",
                "--vote",
                "-1",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "negatives=1" in result.output
        assert "evaluations=1" in result.output

    def test_zero_vote_prints_na(self, memory_dir: Path) -> None:
        """--vote 0 prints N/A and does not update file."""
        f = memory_dir / "patterns.jsonl"
        original = f.read_text(encoding="utf-8")

        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-001",
                "--vote",
                "0",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "N/A" in result.output
        assert f.read_text(encoding="utf-8") == original

    def test_from_flag_accepted(self, memory_dir: Path) -> None:
        """--from flag is accepted without error."""
        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-001",
                "--vote",
                "1",
                "--from",
                "RAISE-170",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        assert result.exit_code == 0, result.output

    def test_pattern_not_found_exits_nonzero(self, memory_dir: Path) -> None:
        """Unknown pattern ID exits with non-zero code."""
        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-999",
                "--vote",
                "1",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        assert result.exit_code != 0

    def test_invalid_vote_exits_nonzero(self, memory_dir: Path) -> None:
        """Invalid vote value exits with non-zero code."""
        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-001",
                "--vote",
                "2",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        assert result.exit_code != 0

    def test_low_wilson_flags_for_review(self, tmp_path: Path) -> None:
        """Pattern with low Wilson score shows review warning."""
        d = tmp_path / "memory"
        _make_patterns_file(
            d,
            [
                {
                    "id": "PAT-E-BAD",
                    "content": "test",
                    "created": "2026-02-01",
                    "positives": 0,
                    "negatives": 9,
                    "evaluations": 9,
                }
            ],
        )
        result = runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-BAD",
                "--vote",
                "-1",
                "--memory-dir",
                str(d),
            ],
        )
        assert result.exit_code == 0, result.output
        assert "consider" in result.output.lower()

    def test_file_updated_after_positive_vote(self, memory_dir: Path) -> None:
        """File is rewritten with updated counts after --vote 1."""
        runner.invoke(
            app,
            [
                "memory",
                "reinforce",
                "PAT-E-001",
                "--vote",
                "1",
                "--memory-dir",
                str(memory_dir),
            ],
        )
        data = json.loads(
            (memory_dir / "patterns.jsonl").read_text(encoding="utf-8").strip()
        )
        assert data["positives"] == 1
        assert data["evaluations"] == 1
