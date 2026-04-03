"""FilesystemAdapter — atomic I/O primitives for steward persistence.

Provides write, read, list, and append operations with atomic write
semantics (temp file + rename). No domain knowledge — stewards handle
validation, this adapter handles bytes.

Story: S1040.1 | Epic: E1040 Local Persistence Adapter
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


class FilesystemAdapter:
    """Atomic file I/O adapter rooted at a given directory.

    All paths are resolved relative to ``root``. Write operations use
    temp-file-then-rename for atomicity on POSIX systems.
    """

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def write(self, path: Path, content: str) -> None:
        """Write *content* to *path* atomically.

        Creates parent directories as needed. Uses a temporary file in
        the target directory followed by ``os.rename`` to ensure the
        write is atomic on POSIX (same-filesystem guarantee).
        """
        target = self._root / path
        target.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=target.parent,
            delete=False,
            suffix=".tmp",
        ) as fd:
            tmp_name = fd.name
            try:
                fd.write(content)
                fd.flush()
                os.fsync(fd.fileno())
            except BaseException:
                with contextlib.suppress(OSError):
                    os.unlink(tmp_name)
                raise
        os.rename(tmp_name, target)

    def read(self, path: Path) -> str:
        """Read content from *path*.

        Raises ``FileNotFoundError`` if the file does not exist.
        """
        target = self._root / path
        if not target.exists():
            raise FileNotFoundError(target)
        return target.read_text(encoding="utf-8")

    def list(self, pattern: str) -> list[Path]:
        """Return paths matching *pattern* relative to root.

        Uses ``Path.glob`` with the given pattern. Results are sorted
        for deterministic output.
        """
        return sorted(p.relative_to(self._root) for p in self._root.glob(pattern))
