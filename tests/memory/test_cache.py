"""Tests for memory cache."""

import time
from pathlib import Path

import pytest

from raise_cli.memory.cache import MemoryCache


class TestMemoryCache:
    """Tests for MemoryCache class."""

    def test_cache_empty_directory(self, tmp_path: Path) -> None:
        """Cache with empty directory returns empty graph."""
        cache = MemoryCache(tmp_path)
        graph = cache.get_graph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_cache_creates_graph_json(self, tmp_path: Path) -> None:
        """Cache creates graph.json after first access."""
        # Create test JSONL
        (tmp_path / "patterns.jsonl").write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
        )

        cache = MemoryCache(tmp_path)
        graph = cache.get_graph()

        # Cache file should exist
        assert cache.cache_path.exists()
        assert len(graph.nodes) == 1

    def test_cache_uses_cached_file(self, tmp_path: Path) -> None:
        """Cache uses cached file on second access."""
        # Create test JSONL
        (tmp_path / "patterns.jsonl").write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
        )

        cache = MemoryCache(tmp_path)

        # First access - builds and caches
        graph1 = cache.get_graph()
        cache_mtime = cache.cache_path.stat().st_mtime

        # Wait a tiny bit
        time.sleep(0.01)

        # Second access - should use cache (mtime unchanged)
        graph2 = cache.get_graph()
        assert cache.cache_path.stat().st_mtime == cache_mtime

        # Should have same content
        assert len(graph1.nodes) == len(graph2.nodes)

    def test_cache_detects_stale(self, tmp_path: Path) -> None:
        """Cache detects when JSONL files are newer."""
        # Create test JSONL
        patterns_file = tmp_path / "patterns.jsonl"
        patterns_file.write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
        )

        cache = MemoryCache(tmp_path)

        # First access - builds cache
        graph1 = cache.get_graph()
        assert len(graph1.nodes) == 1

        # Modify JSONL (make it newer)
        time.sleep(0.01)
        patterns_file.write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
            '{"id": "PAT-002", "type": "process", "content": "Test2", "created": "2026-01-31"}\n'
        )

        # Cache should be stale
        assert cache.is_stale()

        # Second access - should rebuild
        graph2 = cache.get_graph()
        assert len(graph2.nodes) == 2

    def test_is_stale_no_cache(self, tmp_path: Path) -> None:
        """is_stale returns True when no cache file exists."""
        cache = MemoryCache(tmp_path)
        assert cache.is_stale()

    def test_is_stale_no_jsonl(self, tmp_path: Path) -> None:
        """is_stale with no JSONL files."""
        cache = MemoryCache(tmp_path)
        # Create fake cache file
        cache.cache_path.write_text("{}")
        # Should not be stale (no JSONL to compare)
        assert not cache.is_stale()

    def test_get_jsonl_files(self, tmp_path: Path) -> None:
        """get_jsonl_files returns existing files."""
        # Create some files
        (tmp_path / "patterns.jsonl").write_text("")
        (tmp_path / "calibration.jsonl").write_text("")
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "index.jsonl").write_text("")

        cache = MemoryCache(tmp_path)
        files = cache.get_jsonl_files()

        assert len(files) == 3
        assert tmp_path / "patterns.jsonl" in files
        assert tmp_path / "calibration.jsonl" in files
        assert sessions_dir / "index.jsonl" in files

    def test_get_jsonl_files_partial(self, tmp_path: Path) -> None:
        """get_jsonl_files only returns existing files."""
        # Create only patterns
        (tmp_path / "patterns.jsonl").write_text("")

        cache = MemoryCache(tmp_path)
        files = cache.get_jsonl_files()

        assert len(files) == 1
        assert tmp_path / "patterns.jsonl" in files

    def test_invalidate(self, tmp_path: Path) -> None:
        """invalidate removes cache file."""
        # Create test JSONL
        (tmp_path / "patterns.jsonl").write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
        )

        cache = MemoryCache(tmp_path)
        cache.get_graph()  # Creates cache

        assert cache.cache_path.exists()

        cache.invalidate()

        assert not cache.cache_path.exists()

    def test_invalidate_no_cache(self, tmp_path: Path) -> None:
        """invalidate when no cache exists doesn't error."""
        cache = MemoryCache(tmp_path)
        cache.invalidate()  # Should not raise

    def test_load_corrupted_cache(self, tmp_path: Path) -> None:
        """Corrupted cache triggers rebuild."""
        # Create test JSONL
        (tmp_path / "patterns.jsonl").write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
        )

        cache = MemoryCache(tmp_path)

        # Write corrupted cache
        cache.cache_path.write_text("not valid json")

        # Should rebuild instead of failing
        graph = cache.get_graph()
        assert len(graph.nodes) == 1

    def test_get_latest_mtime_empty(self, tmp_path: Path) -> None:
        """get_latest_mtime returns 0.0 for empty directory."""
        cache = MemoryCache(tmp_path)
        assert cache.get_latest_mtime() == 0.0

    def test_cache_with_real_data(self) -> None:
        """Test cache with real .rai/memory directory."""
        rai_memory = Path(".rai/memory")
        if not rai_memory.exists():
            pytest.skip(".rai/memory directory not found")

        cache = MemoryCache(rai_memory)
        graph = cache.get_graph()

        # Should have loaded data
        assert len(graph.nodes) > 0
        # Should have created cache
        assert cache.cache_path.exists()
