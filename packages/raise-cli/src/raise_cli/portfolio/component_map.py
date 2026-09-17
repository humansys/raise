"""Shared portfolio component resolver (RAISE-15251).

Provides ``resolve_component()`` — the canonical function for mapping a
repo-relative file path to a portfolio component identifier, using
src-root normalization and longest-prefix matching against the
``portfolio.component_paths`` manifest section.

Used by the graph builder (T3) and eventually by ``rai portfolio suggest`` (S3).
"""

from __future__ import annotations

import re

# Ordered list of src-root pattern to strip before prefix matching.
# Only the first matching pattern is applied (break after first strip).
_SRC_ROOT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^packages/[^/]+/src/"),
    re.compile(r"^src/"),
]


def resolve_component(
    rel_path: str,
    component_paths: dict[str, list[str]],
) -> str | None:
    """Map a repo-relative file path to a portfolio component identifier.

    Normalizes ``rel_path`` by stripping a leading src-root prefix
    (``packages/<pkg>/src/`` or ``src/``) then performs a longest-prefix
    match against each component's path list.

    Args:
        rel_path: Repo-relative file path
            (e.g. ``"packages/raise-cli/src/raise_cli/storage/connection.py"``).
        component_paths: Mapping of component name → list of path prefixes
            as configured in ``project.portfolio.component_paths`` of the
            manifest.  Empty dict is valid and causes a ``None`` return.

    Returns:
        The matched component name, or ``None`` if no prefix matches.
        Never raises.

    Examples:
        >>> resolve_component(
        ...     "packages/raise-cli/src/raise_cli/storage/connection.py",
        ...     {"storage": ["raise_cli/storage"]},
        ... )
        'storage'
        >>> resolve_component("unknown/path.py", {"storage": ["raise_cli/storage"]})
    """
    if not rel_path or not component_paths:
        return None

    # Strip the first matching src-root prefix
    normalized = rel_path
    for pat in _SRC_ROOT_PATTERNS:
        stripped = pat.sub("", normalized, count=1)
        if stripped != normalized:
            normalized = stripped
            break

    best: str | None = None
    best_len = -1
    for component, prefixes in component_paths.items():
        for prefix in prefixes:
            if (normalized == prefix or normalized.startswith(prefix + "/")) and len(
                prefix
            ) > best_len:
                best = component
                best_len = len(prefix)
    return best
