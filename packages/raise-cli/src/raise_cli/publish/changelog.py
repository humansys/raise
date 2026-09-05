"""Changelog parsing and updating for Keep a Changelog format."""

from __future__ import annotations

import re


def _extract_section(content: str, header_pattern: str) -> str | None:
    """Return the body text of the first section matching header_pattern.

    A section runs from its header to the next `## [` header or EOF.
    Returns None if no section matches.
    """
    match = re.search(
        rf"^{header_pattern}[^\n]*$(.*?)(?=(?:^## \[|\Z))",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        return None
    return match.group(1)


def has_unreleased_entries(content: str) -> bool:
    """Check if the changelog has entries under the [Unreleased] section.

    Args:
        content: Full changelog text.

    Returns:
        True if there are non-whitespace entries between [Unreleased] and the next section.
    """
    body = _extract_section(content, r"## \[Unreleased\]")
    if body is None:
        return False
    return len(body.strip()) > 0


def extract_severity(content: str, version: str | None = None) -> str | None:
    """Extract the declared severity for a CHANGELOG section (RAISE-15661).

    Args:
        content: Full changelog text.
        version: Version to look up (e.g. "3.1.0rc6"). None reads [Unreleased].

    Returns:
        The declared severity string (e.g. "critical"), or None if the
        section is absent or has no `severity: <value>` line.
    """
    header_pattern = (
        r"## \[Unreleased\]" if version is None else rf"## \[{re.escape(version)}\]"
    )
    body = _extract_section(content, header_pattern)
    if body is None:
        return None
    match = re.search(r"^severity:\s*(\S+)\s*$", body, re.MULTILINE)
    if not match:
        return None
    return match.group(1)


def promote_unreleased(content: str, version: str, date: str) -> str:
    """Move unreleased entries into a new versioned section.

    Args:
        content: Full changelog text.
        version: New version string (e.g. "2.0.0").
        date: Release date string (e.g. "2026-02-14").

    Returns:
        Updated changelog text.

    Raises:
        ValueError: If there are no unreleased entries to promote.
    """
    if not has_unreleased_entries(content):
        msg = "No unreleased entries to promote"
        raise ValueError(msg)

    # Extract the unreleased body
    match = re.search(
        r"(^## \[Unreleased\])\s*$(.*?)(?=(?:^## \[|\Z))",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        msg = "No unreleased entries to promote"
        raise ValueError(msg)

    unreleased_header = match.group(1)
    unreleased_body = match.group(2).rstrip()

    # Build replacement: empty Unreleased + new version section
    rest = content[match.end() :]
    separator = "\n\n" if rest.startswith("## [") else ""
    replacement = (
        f"{unreleased_header}\n\n## [{version}] - {date}\n{unreleased_body}{separator}"
    )
    content = content[: match.start()] + replacement + rest

    # Update link references if they exist
    # Replace: [Unreleased]: .../compare/vOLD...HEAD
    # With:    [Unreleased]: .../compare/vNEW...HEAD
    #          [NEW]: .../compare/vOLD...vNEW
    old_link_match = re.search(
        r"\[Unreleased\]:\s*(https?://\S+/compare/)v([\d.]+\S*)\.\.\.HEAD",
        content,
    )
    if old_link_match:
        base_url = old_link_match.group(1)
        old_version = old_link_match.group(2)
        new_unreleased_link = f"[Unreleased]: {base_url}v{version}...HEAD"
        new_version_link = f"[{version}]: {base_url}v{old_version}...v{version}"
        content = content.replace(
            old_link_match.group(0),
            f"{new_unreleased_link}\n{new_version_link}",
        )

    return content
