"""Memory graph caching with staleness detection.

This module provides caching for memory graphs with mtime-based
staleness detection to avoid unnecessary rebuilds.
"""

from __future__ import annotations

from pathlib import Path

from raise_cli.memory.builder import MemoryGraph, MemoryGraphBuilder
from raise_cli.memory.loader import load_memory_from_directory


class MemoryCache:
    """Cache for memory graph with staleness detection.

    Caches the built graph to a JSON file and checks JSONL file mtimes
    to determine if a rebuild is needed.

    Attributes:
        memory_dir: Path to the .rai/memory/ directory.
        cache_path: Path to the cached graph.json file.
    """

    def __init__(self, memory_dir: Path) -> None:
        """Initialize cache.

        Args:
            memory_dir: Path to the memory directory.
        """
        self.memory_dir = memory_dir
        self.cache_path = memory_dir / "graph.json"
        self._builder = MemoryGraphBuilder()

    def get_jsonl_files(self) -> list[Path]:
        """Get all JSONL files in the memory directory.

        Returns:
            List of JSONL file paths.
        """
        files: list[Path] = []

        patterns_file = self.memory_dir / "patterns.jsonl"
        if patterns_file.exists():
            files.append(patterns_file)

        calibration_file = self.memory_dir / "calibration.jsonl"
        if calibration_file.exists():
            files.append(calibration_file)

        sessions_file = self.memory_dir / "sessions" / "index.jsonl"
        if sessions_file.exists():
            files.append(sessions_file)

        return files

    def get_latest_mtime(self) -> float:
        """Get the latest modification time of JSONL files.

        Returns:
            Latest mtime as a float, or 0.0 if no files exist.
        """
        jsonl_files = self.get_jsonl_files()
        if not jsonl_files:
            return 0.0
        return max(f.stat().st_mtime for f in jsonl_files)

    def is_stale(self) -> bool:
        """Check if the cache is stale.

        Cache is stale if:
        - Cache file doesn't exist
        - Any JSONL file is newer than cache

        Returns:
            True if cache needs rebuild, False otherwise.
        """
        if not self.cache_path.exists():
            return True

        cache_mtime = self.cache_path.stat().st_mtime
        jsonl_mtime = self.get_latest_mtime()

        return jsonl_mtime > cache_mtime

    def load_from_cache(self) -> MemoryGraph | None:
        """Load graph from cache file.

        Returns:
            MemoryGraph if cache exists and is valid, None otherwise.
        """
        if not self.cache_path.exists():
            return None

        try:
            json_str = self.cache_path.read_text(encoding="utf-8")
            return MemoryGraph.from_json(json_str)
        except Exception:
            # Cache corrupted, return None to trigger rebuild
            return None

    def save_to_cache(self, graph: MemoryGraph) -> None:
        """Save graph to cache file.

        Args:
            graph: MemoryGraph to cache.
        """
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(graph.to_json(), encoding="utf-8")

    def rebuild(self) -> MemoryGraph:
        """Rebuild graph from JSONL files.

        Returns:
            Newly built MemoryGraph.
        """
        result = load_memory_from_directory(self.memory_dir)
        graph = self._builder.build(result.concepts)
        return graph

    def get_graph(self) -> MemoryGraph:
        """Get memory graph, using cache if fresh.

        If cache is stale or doesn't exist, rebuilds from JSONL files
        and updates the cache.

        Returns:
            MemoryGraph (from cache or freshly built).
        """
        if not self.is_stale():
            cached = self.load_from_cache()
            if cached is not None:
                return cached

        # Rebuild and cache
        graph = self.rebuild()
        self.save_to_cache(graph)
        return graph

    def invalidate(self) -> None:
        """Invalidate the cache by deleting the cache file."""
        if self.cache_path.exists():
            self.cache_path.unlink()
