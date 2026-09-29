"""Git changed-file collection for impact analysis."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitDiffError(RuntimeError):
    """Raised when changed files cannot be collected from Git."""


def collect_changed_files(
    base_ref: str,
    head_ref: str | None,
    cwd: Path,
) -> list[Path]:
    r"""Return changed files between base and head as sorted relative paths.

    C5 (quality-review, RAISE-15878): ``-c core.quotePath=false`` disables
    git's default C-quoting of non-ASCII paths (e.g. an accented dir name
    would otherwise come back as the literal string
    ``"work/epics/e-migraci\\303\\263n/scope.md"``, quotes and all). That
    default is client-side and independent of the repo's own config, so
    every caller of this function — including the governance-trail CI
    backstop, which matches on the raw path string — would silently
    misclassify a real, tracked non-ASCII path. No caller wants quoted
    paths; they are never the "real" path.

    R8 (quality-review round 5, RAISE-15878): the C5 fix removed the
    guarantee that git's stdout is pure ASCII, so decoding is pinned to an
    explicit ``encoding="utf-8"`` rather than left to the process locale — a
    locale without UTF-8 coercion could otherwise raise ``UnicodeDecodeError``
    on a real non-ASCII path, which is neither ``OSError`` (handled below)
    nor ``GitDiffError`` (handled by the gate) and would escape both error
    contracts instead of degrading to the documented honest-skip.

    R11 (architecture review, RAISE-15878): pinning the encoding removed the
    *locale* dependency but not the escape path R8 described — ``except
    OSError`` never caught ``UnicodeDecodeError``. Git stores path names as
    raw bytes, so a tracked filename whose bytes are not valid UTF-8 still
    raised straight through, crashing the fail-closed backstop with a
    traceback instead of degrading to its honest-skip. Undecodable output is
    now folded into this function's declared ``GitDiffError`` contract,
    symmetric with the R10 fix to ``read_at_ref``.
    """
    revision_range = f"{base_ref}...{head_ref or 'HEAD'}"
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                "core.quotePath=false",
                "diff",
                "--name-only",
                revision_range,
            ],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        raise GitDiffError(f"git diff failed: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise GitDiffError(f"git diff output is not valid UTF-8: {exc}") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise GitDiffError(f"git diff failed: {detail}")

    return sorted(
        {Path(line.strip()) for line in result.stdout.splitlines() if line.strip()},
        key=lambda path: path.as_posix(),
    )
