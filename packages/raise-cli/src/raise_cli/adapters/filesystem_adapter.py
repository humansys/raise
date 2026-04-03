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

    Path containment is enforced — all resolved paths must stay within
    the root directory.
    """

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _resolve(self, path: Path) -> Path:
        """Resolve *path* relative to root with containment check."""
        target = (self._root / path).resolve()
        if not target.is_relative_to(self._root):
            msg = f"Path escapes root: {path}"
            raise ValueError(msg)
        return target

    def write(self, path: Path, content: str) -> None:
        """Write *content* to *path* atomically.

        Creates parent directories as needed. Uses a temporary file in
        the target directory followed by ``os.rename`` to ensure the
        write is atomic on POSIX (same-filesystem guarantee).
        """
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
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
        target = self._resolve(path)
        return target.read_text(encoding="utf-8")

    def list(self, pattern: str) -> list[Path]:
        """Return paths matching *pattern* relative to root.

        Uses ``Path.glob`` with the given pattern. Results are sorted
        for deterministic output.
        """
        return sorted(p.relative_to(self._root) for p in self._root.glob(pattern))

    def append(self, path: Path, line: str) -> None:
        r"""Append *line* with a trailing newline to *path* atomically.

        Reads existing content (empty string if file does not exist),
        appends the line with ``\n``, and writes the result atomically
        via :meth:`write`. Creates parent directories as needed.

        Does **not** use ``open('a')`` --- the full file is rewritten
        atomically per DD-3.
        """
        target = self._resolve(path)
        try:
            existing = target.read_text(encoding="utf-8")
        except FileNotFoundError:
            existing = ""
        self.write(path, existing + line + "\n")
