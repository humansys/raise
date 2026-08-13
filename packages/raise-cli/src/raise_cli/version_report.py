"""Git-aware augmentation for the declared ``raise-cli`` package version.

``raise_cli.__version__`` is (and stays) static package metadata: several
call sites compare it for exact equality (skill manifest auto-upgrade,
onboarding version-consistency checks) so it must not gain a suffix that
changes on every commit.

This module answers a narrower question for ``rai --version``: for a
raise-commons dev checkout, does the declared version actually correspond to
a published release tag, and if so, how far ahead of it is HEAD? RAISE-16225:
the declared version can drift arbitrarily far from git state, and can even
name a release that was never published at all.

Tag convention (see ``dev/sops/release-common.md`` "Tag Format"): every
release — prerelease or stable — gets a monorepo tag ``v{version}`` (e.g.
``v3.1.0rc3``) that ``rai release publish`` creates locally and pushes to
origin, so that's the tag actually reachable in a local checkout. The
per-package ``raise-cli-v{version}`` tag is stable-only and is pushed only
to the GitHub mirror as an orphan-commit ref, so it's checked as a fallback
but will essentially never be found here.

The comparison only runs when the enclosing git root is actually the
raise-commons checkout (detected via ``packages/raise-cli/pyproject.toml``)
— otherwise an ordinary ``pip install raise-cli`` inside any unrelated
git-tracked project would be compared against that project's unrelated tags
and always warn "never published".
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel


class VersionReport(BaseModel):
    """Git-state context for a declared package version."""

    declared_version: str
    is_git_checkout: bool
    expected_tag: str | None = None
    git_describe: str | None = None
    published_tag_exists: bool | None = None
    commits_ahead_of_tag: int | None = None


def build_version_report(
    declared_version: str, *, start_path: Path | None = None
) -> VersionReport:
    """Inspect the git checkout containing the package, if there is one.

    Args:
        declared_version: The version string from package metadata
            (``raise_cli.__version__``).
        start_path: Directory to start the git lookup from. Defaults to the
            directory containing this module, so the report reflects the
            installed package's own source location rather than the
            caller's current working directory.

    Returns:
        A ``VersionReport``. When ``start_path`` is not inside a git work
        tree, or the enclosing work tree isn't actually the raise-commons
        checkout, only ``declared_version`` and ``is_git_checkout=False`` are
        populated — there is nothing to compare against.
    """
    root = _find_git_root(start_path or Path(__file__).resolve().parent)
    if root is None or not _is_raise_commons_checkout(root):
        return VersionReport(declared_version=declared_version, is_git_checkout=False)

    git_describe = _run_git(root, "describe", "--tags", "--always", "--dirty")

    # Prefer the monorepo tag — that's what `rai release publish` actually
    # creates in a local checkout for every channel. Fall back to the
    # per-package tag for the rare case it was also created locally.
    candidates = (f"v{declared_version}", f"raise-cli-v{declared_version}")
    matched_tag: str | None = None
    for candidate in candidates:
        if (
            _run_git(root, "rev-parse", "-q", "--verify", f"refs/tags/{candidate}")
            is not None
        ):
            matched_tag = candidate
            break

    commits_ahead: int | None = None
    if matched_tag is not None:
        count = _run_git(root, "rev-list", "--count", f"{matched_tag}..HEAD")
        if count is not None and count.isdigit():
            commits_ahead = int(count)

    return VersionReport(
        declared_version=declared_version,
        is_git_checkout=True,
        expected_tag=matched_tag or candidates[0],
        git_describe=git_describe,
        published_tag_exists=matched_tag is not None,
        commits_ahead_of_tag=commits_ahead,
    )


def format_version_report(report: VersionReport) -> str:
    """Render a one-line warning for ``rai --version``, or ``""`` when clean.

    Silent when the checkout sits exactly on its declared release tag (or
    when there's no git checkout at all) — a warning only earns its place
    when something is actually off.
    """
    if not report.is_git_checkout:
        return ""

    if report.published_tag_exists is False:
        suffix = f" ({report.git_describe})" if report.git_describe else ""
        return (
            f"warning: '{report.expected_tag}' was never published — this "
            f"version does not correspond to a released build{suffix}"
        )

    if report.commits_ahead_of_tag:
        n = report.commits_ahead_of_tag
        plural = "s" if n != 1 else ""
        suffix = f" ({report.git_describe})" if report.git_describe else ""
        return (
            f"warning: {n} commit{plural} ahead of released tag "
            f"'{report.expected_tag}' — development build{suffix}"
        )

    return ""


def _find_git_root(start_path: Path) -> Path | None:
    toplevel = _run_git(start_path, "rev-parse", "--show-toplevel")
    return Path(toplevel) if toplevel is not None else None


def _is_raise_commons_checkout(root: Path) -> bool:
    """Confirm ``root`` is the raise-commons monorepo, not some other repo.

    RAISE-16225: without this check, an ordinary ``pip install raise-cli``
    inside any unrelated git-tracked project would have its version compared
    against that project's unrelated tags — a guaranteed false "never
    published" warning for every ordinary non-editable install.
    """
    return (root / "packages" / "raise-cli" / "pyproject.toml").is_file()


def _run_git(cwd: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(  # noqa: S603 — fixed git executable and controlled args
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    return output or None
