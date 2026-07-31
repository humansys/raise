"""Port allocator for worktree-isolated dev stacks."""

from __future__ import annotations

import hashlib
import socket
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

PORT_RANGE_START = 30000
BLOCK_SIZE = 10
NUM_BLOCKS = 3000
MAX_FALLBACK_ATTEMPTS = 10

_SERVICE_NAMES = ("postgres", "server", "vite", "daemon")


class PortAllocationError(Exception):
    """Raised when no free port block can be found after exhausting fallback attempts."""


@dataclass(frozen=True)
class PortBlock:
    """Immutable block of ports assigned to a worktree dev stack."""

    base: int
    postgres: int
    server: int
    vite: int
    daemon: int

    @classmethod
    def from_base(cls, base: int) -> PortBlock:
        """Create a port block with standard offsets from a base port."""
        return cls(
            base=base,
            postgres=base,
            server=base + 1,
            vite=base + 2,
            daemon=base + 3,
        )


def _normalize_path(worktree_path: Path) -> str:
    path_str = str(worktree_path)
    return PurePosixPath(path_str.replace("\\", "/")).as_posix()


def _hash_to_base(posix_path: str) -> int:
    digest = hashlib.md5(posix_path.encode(), usedforsecurity=False).hexdigest()[:4]
    hash_int = int(digest, 16)
    return PORT_RANGE_START + (hash_int % NUM_BLOCKS) * BLOCK_SIZE


def validate_ports(block: PortBlock) -> list[tuple[str, int, str]]:
    """Check all ports in the block are available via socket.bind()."""
    errors: list[tuple[str, int, str]] = []
    for name in _SERVICE_NAMES:
        port = getattr(block, name)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError as exc:
                errors.append((name, port, str(exc)))
    return errors


def allocate_ports(
    worktree_path: Path,
    *,
    max_attempts: int = MAX_FALLBACK_ATTEMPTS,
) -> PortBlock:
    """Allocate a deterministic port block for a worktree, with fallback on collision."""
    posix_path = _normalize_path(worktree_path)
    base = _hash_to_base(posix_path)

    for attempt in range(max_attempts):
        candidate_base = (base + attempt * BLOCK_SIZE - PORT_RANGE_START) % (
            NUM_BLOCKS * BLOCK_SIZE
        ) + PORT_RANGE_START
        block = PortBlock.from_base(candidate_base)
        errors = validate_ports(block)
        if not errors:
            return block

    raise PortAllocationError(
        f"No free port block found after {max_attempts} attempts "
        f"(starting from base {base}). "
        f"Free some ports in range {PORT_RANGE_START}-{PORT_RANGE_START + NUM_BLOCKS * BLOCK_SIZE - 1}."
    )
