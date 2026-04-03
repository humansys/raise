"""Tests for file utilities."""

from pathlib import Path

from raise_cli.core.files import atomic_write


class TestAtomicWrite:
    """Tests for atomic_write function."""

    def test_creates_file(self, tmp_path: Path) -> None:
        """Should create the target file with correct content."""
        target = tmp_path / "state.yaml"
        atomic_write(target, "key: value\n")

        assert target.read_text() == "key: value\n"

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Should create parent directories if missing."""
        target = tmp_path / "deep" / "nested" / "file.yaml"
        atomic_write(target, "content")

        assert target.exists()

    def test_no_tmp_file_left(self, tmp_path: Path) -> None:
        """Should not leave .tmp file after successful write."""
        target = tmp_path / "state.yaml"
        atomic_write(target, "content")

        tmp_file = target.with_suffix(".yaml.tmp")
        assert not tmp_file.exists()

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        """Should overwrite existing file atomically."""
        target = tmp_path / "state.yaml"
        target.write_text("old")

        atomic_write(target, "new")

        assert target.read_text() == "new"

    def test_encoding(self, tmp_path: Path) -> None:
        """Should respect encoding parameter."""
        target = tmp_path / "state.yaml"
        atomic_write(target, "cafecito: bueno\n", encoding="utf-8")

        assert "cafecito" in target.read_text(encoding="utf-8")
