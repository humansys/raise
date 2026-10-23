"""Port allocator for worktree-isolated dev stacks."""

from __future__ import annotations

import hashlib
import logging
import socket
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raise_cli.storage.port_allocations import SqlitePortAllocationStore

logger = logging.getLogger(__name__)

PORT_RANGE_START = 30000
BLOCK_SIZE = 10
NUM_BLOCKS = 3000
MAX_FALLBACK_ATTEMPTS = 10

_SERVICE_NAMES = ("postgres", "server", "vite", "daemon")

if len(_SERVICE_NAMES) > BLOCK_SIZE:  # pragma: no cover — build-time guard
    _msg = f"_SERVICE_NAMES has {len(_SERVICE_NAMES)} entries but BLOCK_SIZE is {BLOCK_SIZE}"
    raise RuntimeError(_msg)


class PortAllocationError(Exception):
    """Raised when no free port block can be found after exhausting fallback attempts."""


@dataclass(frozen=True)
class PortBlock:
    """Immutable block of ports assigned to a worktree dev stack.

    Uses a mapping internally for extensibility: adding a service name to
    ``_SERVICE_NAMES`` assigns it a port with no change to allocation logic.
    Backward-compatible attribute access (``block.postgres``, etc.) is
    preserved via ``__getattr__``.
    """

    base: int
    ports: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def from_base(cls, base: int) -> PortBlock:
        """Create a port block with standard offsets from a base port."""
        return cls(
            base=base,
            ports=MappingProxyType(
                {name: base + i for i, name in enumerate(_SERVICE_NAMES)}
            ),
        )

    def __getattr__(self, name: str) -> int:
        """Allow attribute-style access to service ports (e.g. block.postgres)."""
        try:
            return self.ports[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __eq__(self, other: object) -> bool:  # noqa: D105
        if not isinstance(other, PortBlock):
            return NotImplemented
        return self.base == other.base and dict(self.ports) == dict(other.ports)

    def __hash__(self) -> int:  # noqa: D105
        return hash((self.base, tuple(sorted(self.ports.items()))))


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
    for name, port in block.ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError as exc:
                errors.append((name, port, str(exc)))
    return errors


def allocate_ports(
    worktree_path: Path,
    *,
    store: SqlitePortAllocationStore | None = None,
    max_attempts: int = MAX_FALLBACK_ATTEMPTS,
) -> PortBlock:
    """Allocate a deterministic port block for a worktree, with fallback on collision.

    With ``store``:
    1. Check for a prior persisted claim -- re-validate sockets; if still
       valid, return it (deterministic across restarts). If sockets now busy,
       release the stale claim and re-allocate (self-heal).
    2. Hash to candidate base (existing logic, unchanged).
    3. ``store.claim()`` first (DB arbiter), then ``validate_ports()`` socket
       probe; on either failure, fall back to next candidate.

    Without ``store``: today's behavior, unchanged (spike tests keep passing).
    """
    # Fast path: re-use persisted claim if sockets still free
    if store is not None:
        existing = store.get(worktree_path)
        if existing is not None:
            block = PortBlock.from_base(existing.base)
            errors = validate_ports(block)
            if not errors:
                return block
            # Stale claim -- ports busy; release and re-allocate below
            logger.info(
                "Stale claim for %s (base %d) -- ports busy, re-allocating",
                worktree_path,
                existing.base,
            )
            store.release(worktree_path)

    posix_path = _normalize_path(worktree_path)
    base = _hash_to_base(posix_path)

    for attempt in range(max_attempts):
        candidate_base = (base + attempt * BLOCK_SIZE - PORT_RANGE_START) % (
            NUM_BLOCKS * BLOCK_SIZE
        ) + PORT_RANGE_START
        block = PortBlock.from_base(candidate_base)

        # DB arbiter: claim first, then validate sockets
        if store is not None:
            from raise_cli.storage.port_allocations import PortBlockClaimedError

            try:
                store.claim(worktree_path, block)
            except PortBlockClaimedError:
                logger.info(
                    "Base %d claimed by another worktree -- falling back",
                    candidate_base,
                )
                continue

        errors = validate_ports(block)
        if not errors:
            return block

        # Socket probe failed -- release DB claim if we made one
        if store is not None:
            store.release(worktree_path)

    raise PortAllocationError(
        f"No free port block found after {max_attempts} attempts "
        f"(starting from base {base}). "
        f"Free some ports in range {PORT_RANGE_START}-{PORT_RANGE_START + NUM_BLOCKS * BLOCK_SIZE - 1}."
    )
