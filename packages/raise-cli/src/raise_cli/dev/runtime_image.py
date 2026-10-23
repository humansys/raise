"""Runtime image builder & extractor — pre-baked dependency cache.

S16534.4 (RAISE-16544): Builds a Docker image with all Python and Node
dependencies pre-installed.  On ``rai dev up``, if a fresh image exists
locally, deps are extracted via ``docker cp`` instead of running
``uv sync`` and ``npm ci``.

Design decisions:
  DD3 — busybox artifact image (no Python/Node runtime in final image)
  DD5 — extract site-packages only (venv skeleton created on host)
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

IMAGE_REPO = "raise-dev-runtime"
_EXTRACT_CONTAINER_PREFIX = "raise-dep-extract"


def _unique_container_name(worktree_path: Path) -> str:
    """Generate a unique container name per invocation.

    Format: raise-dep-extract-<slug>-<uuid4_short>
    Avoids name collisions under concurrent fleet provisioning (C1).
    """
    slug = worktree_path.name[:20]  # truncate long names
    suffix = uuid.uuid4().hex[:8]
    return f"{_EXTRACT_CONTAINER_PREFIX}-{slug}-{suffix}"


@dataclass(frozen=True)
class DepFingerprint:
    """Content-addressable hash of lock files.

    Fingerprint = SHA-256 of ``uv.lock`` + ``package-lock.json``.
    Lock files are the single source of truth for installed deps (DD2).
    """

    hex_digest: str

    @classmethod
    def compute(cls, worktree_path: Path) -> DepFingerprint:
        """SHA-256 of uv.lock + packages/raise-admin/package-lock.json.

        Raises:
            FileNotFoundError: If either lock file is missing.
        """
        uv_lock = worktree_path / "uv.lock"
        pkg_lock = worktree_path / "packages" / "raise-admin" / "package-lock.json"

        h = hashlib.sha256()
        h.update(uv_lock.read_bytes())
        h.update(pkg_lock.read_bytes())

        return cls(hex_digest=h.hexdigest())

    @property
    def short(self) -> str:
        """First 12 hex characters of the digest."""
        return self.hex_digest[:12]


def image_tag(fp: DepFingerprint) -> str:
    """Return the Docker image tag for a given fingerprint."""
    return f"{IMAGE_REPO}:{fp.short}"


def image_exists_locally(tag: str) -> bool:
    """Check if the Docker image exists locally.

    Returns False if Docker is unavailable (graceful degradation).
    """
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", tag],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, PermissionError):
        return False


def build_image(worktree_path: Path, tag: str) -> None:
    """Build the runtime image from Dockerfile.dev-runtime.

    Uses the repo root as build context so all dependency files are available.
    Output streams to terminal so the user sees build progress (R5).

    Raises:
        subprocess.CalledProcessError: If the build fails.
    """
    dockerfile = worktree_path / "Dockerfile.dev-runtime"
    subprocess.run(
        [
            "docker",
            "build",
            "-f",
            str(dockerfile),
            "-t",
            tag,
            str(worktree_path),
        ],
        check=True,
    )


def extract_deps(tag: str, worktree_path: Path, frontend_dir: str) -> None:
    """Extract venv site-packages and node_modules from the runtime image.

    Strategy (DD5):
    1. Create venv skeleton on host via ``uv venv`` (correct pyvenv.cfg, symlinks)
    2. Remove stale node_modules (R4: docker cp merges, removed packages not pruned)
    3. Create a temp container from the image (unique name per invocation — C1)
    4. Copy ``/app/.venv.dev/lib/`` to ``worktree/.venv.dev/lib/``
    5. Copy ``/app/frontend/node_modules/`` to ``worktree/<frontend_dir>/node_modules/``
    6. Remove the temp container (``docker rm -f`` — C1)
    """
    import shutil

    venv_path = worktree_path / ".venv.dev"
    container_name = _unique_container_name(worktree_path)

    # 1. Create venv skeleton on host
    subprocess.run(
        ["uv", "venv", str(venv_path)],
        check=True,
        capture_output=True,
    )

    # 2. Remove stale node_modules before extraction (R4)
    frontend_path = worktree_path / frontend_dir
    nm_path = frontend_path / "node_modules"
    if nm_path.exists():
        shutil.rmtree(nm_path)

    # 3. Create temp container (not started, just filesystem access)
    subprocess.run(
        ["docker", "create", "--name", container_name, tag],
        check=True,
        capture_output=True,
    )

    try:
        # 4. Copy site-packages from image to host venv
        subprocess.run(
            [
                "docker",
                "cp",
                f"{container_name}:/app/.venv.dev/lib/.",
                str(venv_path / "lib"),
            ],
            check=True,
            capture_output=True,
        )

        # 5. Copy node_modules from image to frontend dir
        subprocess.run(
            [
                "docker",
                "cp",
                f"{container_name}:/app/frontend/node_modules/.",
                str(nm_path),
            ],
            check=True,
            capture_output=True,
        )
    finally:
        # 6. Always force-remove the temp container (C1: -f handles stale)
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            check=False,
            capture_output=True,
        )


def should_use_image(worktree_path: Path) -> tuple[bool, str]:
    """Check if a matching runtime image is available locally.

    Returns:
        (available, tag) — available is True if the image exists and matches
        the current lock file fingerprint.  When lock files are missing or
        the host is not Linux, returns (False, '') rather than raising.
    """
    # R1: Dockerfile builds Linux-x86 packages; non-Linux hosts get wrong binaries
    if sys.platform != "linux":
        logger.debug("Non-Linux platform (%s) — skipping runtime image", sys.platform)
        return False, ""

    try:
        fp = DepFingerprint.compute(worktree_path)
    except FileNotFoundError:
        logger.debug("Lock files missing — cannot compute fingerprint")
        return False, ""

    tag = image_tag(fp)
    return image_exists_locally(tag), tag
