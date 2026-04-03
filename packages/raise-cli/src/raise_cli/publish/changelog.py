"""Changelog parsing and updating for Keep a Changelog format."""

from __future__ import annotations

import re


def has_unreleased_entries(content: str) -> bool:
    """Check if the changelog has entries under the [Unreleased] section.

    Args:
        content: Full changelog text.

    Returns:
        True if there are non-whitespace entries between [Unreleased] and the next section.
    """
    match = re.search(
        r"^## \[Unreleased\]\s*$(.*?)(?=(?:^## \[|\Z))",
        content,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        return False
    return len(match.group(1).strip()) > 0


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
    replacement = f"{unreleased_header}\n\n## [{version}] - {date}\n{unreleased_body}"
    content = content[: match.start()] + replacement + content[match.end() :]

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
