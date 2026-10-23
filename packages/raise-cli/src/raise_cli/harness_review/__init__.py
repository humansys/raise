"""Cross-harness review adapter — local subprocess dispatch (RAISE-17422).

This package is the single dispatch point for requesting technical reviews
from locally-installed harness binaries (claude, codex, kimi-k3). It is
parallel to ``raise_cli.scm`` (SCM operations) — different domain, different
failure modes, no shared interface.
"""

from __future__ import annotations

from raise_cli.harness_review.adapter import (
    HarnessCommandError,
    HarnessConfigError,
    HarnessReviewAdapter,
    HarnessReviewError,
    ReviewContext,
    ReviewFinding,
    ReviewResult,
    ReviewVerdict,
    from_config,
    resolve_review_harnesses,
)
from raise_cli.harness_review.claude_adapter import ClaudeCodeAdapter
from raise_cli.harness_review.detection import (
    KNOWN_HARNESS_BINARIES,
    detect_installed_harnesses,
)
from raise_cli.harness_review.pre_submission import (
    PreSubmissionResult,
    is_infrastructure_failure,
    provenance_label,
    request_pre_submission_review,
)

__all__ = [
    "ClaudeCodeAdapter",
    "HarnessCommandError",
    "HarnessConfigError",
    "HarnessReviewAdapter",
    "HarnessReviewError",
    "KNOWN_HARNESS_BINARIES",
    "PreSubmissionResult",
    "ReviewContext",
    "ReviewFinding",
    "ReviewResult",
    "ReviewVerdict",
    "detect_installed_harnesses",
    "from_config",
    "is_infrastructure_failure",
    "provenance_label",
    "request_pre_submission_review",
    "resolve_review_harnesses",
]
