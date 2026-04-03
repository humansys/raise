"""Tests for FilesystemAdapter — atomic I/O primitives.

Story: S1040.1 | Epic: E1040 Local Persistence Adapter
"""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.adapters.filesystem_adapter import FilesystemAdapter

# ── T1: Core operations — write, read, list ──────────────────────────────


class TestWrite:
    """write() creates files atomically with correct content."""

    def test_write_creates_file(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.write(Path("hello.txt"), "world")
        assert (tmp_path / "hello.txt").exists()

    def test_write_creates_parent_dirs(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.write(Path("a/b/c/deep.txt"), "content")
        assert (tmp_path / "a" / "b" / "c" / "deep.txt").exists()

    def test_write_overwrites_existing(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.write(Path("file.txt"), "old")
        adapter.write(Path("file.txt"), "new")
        assert (tmp_path / "file.txt").read_text() == "new"

    def test_write_content_matches(self, tmp_path: Path) -> None:
        """AC1: write() produces identical content to direct write_text()."""
        adapter = FilesystemAdapter(root=tmp_path)
        content = "line1\nline2\n"
        adapter.write(Path("file.txt"), content)
        assert (tmp_path / "file.txt").read_text() == content


class TestRead:
    """read() returns file content or raises FileNotFoundError."""

    def test_read_returns_content(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        (tmp_path / "file.txt").write_text("hello")
        assert adapter.read(Path("file.txt")) == "hello"

    def test_read_missing_raises_file_not_found(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        with pytest.raises(FileNotFoundError):
            adapter.read(Path("does-not-exist.txt"))


class TestList:
    """list() returns relative paths matching glob pattern."""

    def test_list_returns_matching_paths(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "c.md").write_text("c")
        result = adapter.list("*.txt")
        assert sorted(result) == [Path("a.txt"), Path("b.txt")]

    def test_list_empty_returns_empty(self, tmp_path: Path) -> None:
        adapter = FilesystemAdapter(root=tmp_path)
        assert adapter.list("*.yaml") == []

    def test_paths_relative_to_root(self, tmp_path: Path) -> None:
        """AC8: All returned paths are relative to constructor root."""
        adapter = FilesystemAdapter(root=tmp_path)
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "file.txt").write_text("x")
        result = adapter.list("**/*.txt")
        assert result == [Path("sub/file.txt")]
        # Verify paths are relative, not absolute
        for p in result:
            assert not p.is_absolute()


# ── T2: append operation ─────────────────────────────────────────────────


class TestAppend:
    """append() adds a single line atomically."""

    def test_append_adds_line_to_existing_file(self, tmp_path: Path) -> None:
        """AC3: append adds exactly one line with trailing newline."""
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.write(Path("log.jsonl"), "line1\n")
        adapter.append(Path("log.jsonl"), "line2")
        assert adapter.read(Path("log.jsonl")) == "line1\nline2\n"

    def test_append_creates_new_file(self, tmp_path: Path) -> None:
        """AC4: append to non-existent file creates it."""
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.append(Path("new.jsonl"), "first")
        assert adapter.read(Path("new.jsonl")) == "first\n"

    def test_append_creates_parent_dirs(self, tmp_path: Path) -> None:
        """AC4: append creates parent directories."""
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.append(Path("deep/dir/file.jsonl"), "data")
        assert (tmp_path / "deep" / "dir" / "file.jsonl").exists()

    def test_append_preserves_existing_content(self, tmp_path: Path) -> None:
        """AC3: existing content is preserved after append."""
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.write(Path("file.jsonl"), "a\nb\n")
        adapter.append(Path("file.jsonl"), "c")
        content = adapter.read(Path("file.jsonl"))
        assert content.startswith("a\nb\n")
        assert content.endswith("c\n")

    def test_append_adds_trailing_newline(self, tmp_path: Path) -> None:
        """AC3: appended line always ends with newline."""
        adapter = FilesystemAdapter(root=tmp_path)
        adapter.append(Path("file.jsonl"), "no-newline-here")
        content = adapter.read(Path("file.jsonl"))
        assert content.endswith("\n")
