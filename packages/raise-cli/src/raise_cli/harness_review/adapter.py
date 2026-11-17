"""HarnessReviewAdapter Protocol, models, and factory (RAISE-17423).

Single dispatch point for cross-harness review requests. Follows the
``ScmAdapter`` pattern: Protocol + factory + lazy registry.

``HarnessReviewAdapter``
    The Protocol. One method: ``request_review()``.

``from_config()``
    Factory. Delegates to ``resolve_review_harnesses()`` for config
    resolution, fails closed on unknown harness (same as ``from_manifest()``
    in ``scm/adapter.py``).

``ReviewResult``
    Fail-closed verdict: ``pass`` or ``fail``, no third value. Findings
    are required on fail, empty on pass.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, field_validator

ReviewVerdict = Literal["pass", "fail"]
"""Review verdict — fail-closed.

Only ``pass`` is permission to proceed. Timeout, malformed response,
unreachable harness, and every other non-pass condition resolve to ``fail``
before ``request_review()`` returns. No third value exists in the type.
"""


class HarnessReviewError(Exception):
    """Base class for every failure originating in this package."""


class HarnessConfigError(HarnessReviewError):
    """The harness could not be resolved, or is not one we implement."""


class HarnessCommandError(HarnessReviewError):
    """The harness CLI was missing, failed, timed out, or returned junk."""


@dataclass(frozen=True)
class ReviewFinding:
    """A single defect found by the reviewing harness."""

    file: str
    line: int
    summary: str
    fix_suggestion: str
    dimension: str


@dataclass(frozen=True)
class ReviewResult:
    """Verdict from a cross-harness review."""

    verdict: ReviewVerdict
    findings: tuple[ReviewFinding, ...]
    harness: str
    duration_seconds: float


class ReviewContext(BaseModel, frozen=True):
    """Context sent to the reviewing harness alongside the diff."""

    design_excerpt: str
    scope_summary: str
    patterns: tuple[str, ...] = ()

    @field_validator("design_excerpt", "scope_summary")
    @classmethod
    def _not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v


@runtime_checkable
class HarnessReviewAdapter(Protocol):
    """Provider-agnostic review request dispatch."""

    def request_review(
        self,
        *,
        diff: str,
        context: ReviewContext,
        dimensions: tuple[str, ...],
    ) -> ReviewResult:
        """Request a review of the given diff and return a structured verdict."""
        ...


_DEFAULT_HARNESSES: list[str] = ["claude"]


def resolve_review_harnesses(project: Path) -> list[str]:
    """Configured harnesses for pre-submission review.

    Override chain: ``RAISE_REVIEW_HARNESSES`` env → manifest → default.
    Same pattern as ``resolve_scm()`` in ``project_config/branches.py``.

    Args:
        project: Repository root (reserved for manifest read in a future story).

    Returns:
        List of harness identifiers matching the adapter registry.
    """
    override = os.environ.get("RAISE_REVIEW_HARNESSES", "").strip()
    if override:
        return [h.strip() for h in override.split(",") if h.strip()]
    # TODO: manifest read (review.harnesses key) — deferred until manifest
    # model is extended; env + default are sufficient for the walking skeleton.
    _ = project  # reserved for manifest read
    return list(_DEFAULT_HARNESSES)


def _harness_registry() -> dict[str, type]:
    """Import adapters lazily to keep this module importable in isolation."""
    from raise_cli.harness_review.claude_adapter import ClaudeCodeAdapter

    return {
        "claude": ClaudeCodeAdapter,
    }


def from_config(harness: str) -> HarnessReviewAdapter:
    """Build the adapter for the named harness.

    Args:
        harness: Harness identifier (e.g. ``"claude"``).

    Returns:
        An adapter conforming to :class:`HarnessReviewAdapter`.

    Raises:
        HarnessConfigError: The harness name is unknown or has no adapter.
    """
    registry = _harness_registry()
    accepted = ", ".join(sorted(registry))

    adapter_cls = registry.get(harness.strip().lower())
    if adapter_cls is None:
        raise HarnessConfigError(
            f"Unknown review harness {harness!r} — accepted values are: {accepted}."
        )
    adapter: HarnessReviewAdapter = adapter_cls()
    return adapter
