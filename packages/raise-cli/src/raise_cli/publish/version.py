"""Version parsing, validation, and bumping for PEP 440 compliance."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# PEP 440 pattern: N.N.N[{a|b|rc}N]
_PEP440_RE = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:(?P<pre_type>a|b|rc)(?P<pre_num>\d+))?$"
)

BumpType = Literal["major", "minor", "patch", "alpha", "beta", "rc", "release"]


@dataclass(frozen=True)
class VersionInfo:
    """Parsed PEP 440 version."""

    major: int
    minor: int
    patch: int
    pre_type: str | None = None
    pre_num: int | None = None

    def __str__(self) -> str:
        """Return semantic version string (e.g. '2.1.0' or '2.1.0rc1')."""
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_type is not None and self.pre_num is not None:
            return f"{base}{self.pre_type}{self.pre_num}"
        return base

    @property
    def is_prerelease(self) -> bool:
        """Check if this is a pre-release version."""
        return self.pre_type is not None


def is_pep440(version: str) -> bool:
    """Check if a version string is PEP 440 compliant.

    Args:
        version: Version string to validate.

    Returns:
        True if the version is valid PEP 440.
    """
    return _PEP440_RE.match(version) is not None


def parse_version(version: str) -> VersionInfo:
    """Parse a PEP 440 version string into components.

    Args:
        version: Version string to parse.

    Returns:
        Parsed version info.

    Raises:
        ValueError: If the version is not valid PEP 440.
    """
    match = _PEP440_RE.match(version)
    if not match:
        msg = f"'{version}' is not a valid PEP 440 version"
        raise ValueError(msg)

    pre_type = match.group("pre_type")
    pre_num_str = match.group("pre_num")

    return VersionInfo(
        major=int(match.group("major")),
        minor=int(match.group("minor")),
        patch=int(match.group("patch")),
        pre_type=pre_type,
        pre_num=int(pre_num_str) if pre_num_str is not None else None,
    )


def bump_version(current: str, bump_type: BumpType) -> str:  # noqa: C901 -- complexity 11, refactor deferred
    """Bump a version string according to the bump type.

    Args:
        current: Current version string (must be PEP 440 compliant).
        bump_type: Type of bump to apply.

    Returns:
        New version string.

    Raises:
        ValueError: If the current version is not valid PEP 440.
    """
    v = parse_version(current)

    if bump_type == "major":
        return str(VersionInfo(major=v.major + 1, minor=0, patch=0))

    if bump_type == "minor":
        return str(VersionInfo(major=v.major, minor=v.minor + 1, patch=0))

    if bump_type == "patch":
        return str(VersionInfo(major=v.major, minor=v.minor, patch=v.patch + 1))

    if bump_type == "alpha":
        if v.pre_type == "a":
            return str(
                VersionInfo(v.major, v.minor, v.patch, "a", (v.pre_num or 0) + 1)
            )
        # From stable or other pre-release: next patch alpha
        if v.pre_type is None:
            return str(VersionInfo(v.major, v.minor, v.patch + 1, "a", 1))
        return str(VersionInfo(v.major, v.minor, v.patch, "a", 1))

    if bump_type == "beta":
        if v.pre_type == "b":
            return str(
                VersionInfo(v.major, v.minor, v.patch, "b", (v.pre_num or 0) + 1)
            )
        return str(VersionInfo(v.major, v.minor, v.patch, "b", 1))

    if bump_type == "rc":
        if v.pre_type == "rc":
            return str(
                VersionInfo(v.major, v.minor, v.patch, "rc", (v.pre_num or 0) + 1)
            )
        return str(VersionInfo(v.major, v.minor, v.patch, "rc", 1))

    # bump_type == "release"
    return str(VersionInfo(v.major, v.minor, v.patch))


def sync_version_files(
    new_version: str,
    *,
    pyproject_path: Path,
    init_path: Path,
) -> None:
    """Update version in pyproject.toml and __init__.py.

    Args:
        new_version: New version string (must be PEP 440 compliant).
        pyproject_path: Path to pyproject.toml.
        init_path: Path to __init__.py.

    Raises:
        ValueError: If the new version is not valid PEP 440.
    """
    if not is_pep440(new_version):
        msg = f"'{new_version}' is not a valid PEP 440 version"
        raise ValueError(msg)

    # Update pyproject.toml
    pyproject_content = pyproject_path.read_text(encoding="utf-8")
    pyproject_content = re.sub(
        r'version\s*=\s*"[^"]*"',
        f'version = "{new_version}"',
        pyproject_content,
        count=1,
    )
    pyproject_path.write_text(pyproject_content, encoding="utf-8")

    # Update __init__.py
    init_content = init_path.read_text(encoding="utf-8")
    init_content = re.sub(
        r'__version__\s*=\s*"[^"]*"',
        f'__version__ = "{new_version}"',
        init_content,
        count=1,
    )
    init_path.write_text(init_content, encoding="utf-8")
