"""Download, verify, and atomically swap rai + rai-mcp-pipeline (RAISE-15632).

The swap unit is the onedir install directory, not a single executable
(design.md D1) — the epic committed to `onedir`, so the on-disk layout is
a directory tree (`rai` + `_internal/`), never a lone file.
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import tarfile
import tempfile
from pathlib import Path

import httpx

from raise_cli.compat import IS_WINDOWS, spawn_detached
from raise_cli.self_update.manifest import PlatformArtifact

DEFAULT_TIMEOUT = 30
CHUNK_SIZE = 1024 * 1024

_PLATFORM_TAGS = {
    ("Linux", "x86_64"): "linux-x86_64",
    ("Darwin", "arm64"): "darwin-arm64",
    ("Darwin", "x86_64"): "darwin-x86_64",
    ("Windows", "AMD64"): "windows-x86_64",
}


class ChecksumMismatchError(Exception):
    """Downloaded artifact does not match the manifest's SHA256."""


class UnsupportedPlatformError(Exception):
    """Current OS/architecture has no published artifact."""


def detect_platform_tag() -> str:
    """Return the manifest platform tag for the current OS/architecture."""
    key = (platform.system(), platform.machine())
    tag = _PLATFORM_TAGS.get(key)
    if tag is None:
        msg = f"Unsupported platform: {key[0]} {key[1]}"
        raise UnsupportedPlatformError(msg)
    return tag


def download_and_verify(
    url: str,
    expected_sha256: str,
    dest: Path,
    *,
    transport: httpx.BaseTransport | None = None,
) -> None:
    """Download `url` to `dest`, verifying its SHA256 matches `expected_sha256`.

    Raises:
        ChecksumMismatchError: If the downloaded content does not match —
            `dest` is removed so no partial/tampered file is left behind.
        httpx.HTTPStatusError: On a non-2xx response.
    """
    digest = hashlib.sha256()
    with (
        httpx.Client(
            transport=transport, timeout=DEFAULT_TIMEOUT, follow_redirects=True
        ) as client,
        client.stream("GET", url) as resp,
    ):
        resp.raise_for_status()
        with dest.open("wb") as f:
            for chunk in resp.iter_bytes(CHUNK_SIZE):
                digest.update(chunk)
                f.write(chunk)

    actual = digest.hexdigest()
    if actual != expected_sha256:
        dest.unlink(missing_ok=True)
        msg = f"Checksum mismatch for {url}: expected {expected_sha256}, got {actual}"
        raise ChecksumMismatchError(msg)


def extract_bundle(archive_path: Path, dest_dir: Path) -> None:
    """Extract an onedir bundle tarball into `dest_dir`."""
    with tarfile.open(archive_path) as tar:
        tar.extractall(dest_dir, filter="data")


def atomic_replace_dir(new_dir: Path, target_dir: Path) -> None:
    """Atomically replace `target_dir` with `new_dir` (same filesystem).

    Keeps a `.bak` sibling during the swap. If the process crashes between
    the two renames, at most one directory is briefly missing — never a
    mixed/corrupt install. This is an accepted residual risk (design.md
    D5), not a full two-phase commit.
    """
    backup = target_dir.parent / f"{target_dir.name}.bak"
    if backup.exists():
        shutil.rmtree(backup)
    if target_dir.exists():
        os.replace(target_dir, backup)
    os.replace(new_dir, target_dir)
    if backup.exists():
        shutil.rmtree(backup)


def generate_windows_swap_script(swaps: list[tuple[Path, Path]], *, pid: int) -> str:
    """Return a batch script that replaces each target dir with its new dir.

    Waits for `pid` to exit, then applies every (new_dir, target_dir) pair
    in `swaps`, in order, then deletes itself. Windows cannot overwrite a
    running executable's own file (locked) — the running `rai` process
    must exit first; this script is launched detached and performs the
    swap afterward.
    """
    lines = [
        "@echo off",
        ":wait",
        f'tasklist /FI "PID eq {pid}" 2>NUL | find "{pid}" >NUL',
        "if not errorlevel 1 (",
        "    timeout /t 1 /nobreak >NUL",
        "    goto wait",
        ")",
    ]
    for new_dir, target_dir in swaps:
        lines.append(f'rmdir /s /q "{target_dir}"')
        lines.append(f'move "{new_dir}" "{target_dir}"')
    lines.append('del "%~f0"')
    return "\n".join(lines) + "\n"


def _download_and_extract_both(
    platform_artifact: PlatformArtifact,
    scratch_dir: Path,
    transport: httpx.BaseTransport | None,
) -> tuple[Path, Path]:
    """Download+verify both bundles into `scratch_dir`, then extract them.

    Both checksums are verified before anything is extracted (design.md
    D5) — if either download/checksum fails, this raises and nothing in
    `scratch_dir` beyond the two archives exists yet.
    """
    rai_archive = scratch_dir / "rai.tar.gz"
    mcp_archive = scratch_dir / "rai-mcp-pipeline.tar.gz"

    download_and_verify(
        platform_artifact.rai.url,
        platform_artifact.rai.sha256,
        rai_archive,
        transport=transport,
    )
    download_and_verify(
        platform_artifact.rai_mcp_pipeline.url,
        platform_artifact.rai_mcp_pipeline.sha256,
        mcp_archive,
        transport=transport,
    )

    rai_new = scratch_dir / "rai.new"
    mcp_new = scratch_dir / "rai-mcp-pipeline.new"
    extract_bundle(rai_archive, rai_new)
    extract_bundle(mcp_archive, mcp_new)
    return rai_new, mcp_new


def update_both_binaries(
    *,
    platform_artifact: PlatformArtifact,
    rai_install_dir: Path,
    mcp_install_dir: Path,
    transport: httpx.BaseTransport | None = None,
) -> None:
    """Download, verify, and swap both binaries — both update or neither does.

    POSIX only — `target_dir` can be renamed while its own executable is
    running. On Windows use `schedule_windows_update` instead (the running
    `rai.exe` holds its own file locked).

    Both archives are downloaded and checksum-verified into a scratch
    directory before either install directory is touched (design.md D5).
    If anything fails before both verifications succeed, this raises and
    `rai_install_dir`/`mcp_install_dir` are left exactly as they were.
    """
    with tempfile.TemporaryDirectory(
        prefix="rai-self-update-", dir=rai_install_dir.parent
    ) as scratch:
        rai_new, mcp_new = _download_and_extract_both(
            platform_artifact, Path(scratch), transport
        )
        atomic_replace_dir(rai_new, rai_install_dir)
        atomic_replace_dir(mcp_new, mcp_install_dir)


def schedule_windows_update(
    *,
    platform_artifact: PlatformArtifact,
    rai_install_dir: Path,
    mcp_install_dir: Path,
    transport: httpx.BaseTransport | None = None,
    pid: int,
) -> Path:
    """Download+verify both bundles, then schedule the swap for after exit.

    Unlike `update_both_binaries`, the scratch directory is intentionally
    NOT cleaned up by this function — the generated batch script deletes
    it after performing the swap, once `pid` (this process) has exited.

    Returns the path to the generated (and already launched) script.
    """
    scratch_dir = Path(
        tempfile.mkdtemp(prefix="rai-self-update-", dir=rai_install_dir.parent)
    )
    rai_new, mcp_new = _download_and_extract_both(
        platform_artifact, scratch_dir, transport
    )

    script = generate_windows_swap_script(
        [(rai_new, rai_install_dir), (mcp_new, mcp_install_dir)],
        pid=pid,
    )
    script_path = scratch_dir / "rai-self-update-swap.bat"
    script_path.write_text(script)
    spawn_detached(["cmd", "/c", str(script_path)])
    return script_path


def update_binaries(
    *,
    platform_artifact: PlatformArtifact,
    rai_install_dir: Path,
    mcp_install_dir: Path,
    transport: httpx.BaseTransport | None = None,
    pid: int | None = None,
) -> Path | None:
    """Update both binaries, dispatching to the right strategy per OS.

    Returns the scheduled swap script path on Windows (the update finishes
    after the caller exits), or None on POSIX (the swap already happened).
    """
    if IS_WINDOWS:
        return schedule_windows_update(
            platform_artifact=platform_artifact,
            rai_install_dir=rai_install_dir,
            mcp_install_dir=mcp_install_dir,
            transport=transport,
            pid=pid if pid is not None else os.getpid(),
        )
    update_both_binaries(
        platform_artifact=platform_artifact,
        rai_install_dir=rai_install_dir,
        mcp_install_dir=mcp_install_dir,
        transport=transport,
    )
    return None
