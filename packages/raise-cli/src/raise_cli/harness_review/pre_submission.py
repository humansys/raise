"""Pre-submission review orchestration (RAISE-17424).

Computes the diff against the target branch, packages design/scope context,
dispatches to the configured cross-harness reviewer, and emits telemetry on
PASS. Fail-closed: infrastructure errors produce a fail verdict.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

from raise_cli.harness_review.adapter import (
    HarnessCommandError,
    HarnessConfigError,
    ReviewContext,
    ReviewFinding,
    ReviewResult,
    from_config,
    resolve_review_harnesses,
)

logger = logging.getLogger(__name__)

_DEFAULT_DIMENSIONS: tuple[str, ...] = (
    "correctness",
    "architecture",
    "security",
    "tests",
)


@dataclass(frozen=True)
class PreSubmissionResult:
    """Result of a pre-submission review including telemetry status."""

    review: ReviewResult
    telemetry_emitted: bool
    diff_stats: str


def is_infrastructure_failure(result: PreSubmissionResult) -> bool:
    """True iff *result* is a fail-closed infrastructure failure, not a review.

    Two sentinels distinguish "the harness could not run" from "the harness
    ran and found problems" (RAISE-17464 D3):

    - ``pre_submission._infrastructure_fail`` sets ``harness="infrastructure"``
      (missing binary/timeout/empty diff/no harness configured/etc., raised
      before any adapter is invoked).
    - ``ClaudeCodeAdapter._fail_result`` sets ``harness="claude"`` with
      exactly one finding whose ``file == ""``, ``line == 0``, and
      ``dimension == "infrastructure"`` (the adapter ran but could not
      produce a real verdict — missing binary, timeout, malformed JSON).

    A real review failure (any other shape, including multiple findings)
    returns ``False`` — this must never suppress an actual verdict.
    """
    review = result.review
    if review.harness == "infrastructure":
        return True
    if review.verdict == "fail" and len(review.findings) == 1:
        finding = review.findings[0]
        if (
            finding.file == ""
            and finding.line == 0
            and finding.dimension == "infrastructure"
        ):
            return True
    return False


_PROVENANCE_LABELS: dict[str, str] = {"claude": "claude_code"}


def provenance_label(harness: str) -> str:
    """Map an internal harness identifier to its MR-provenance label (D6).

    Identity for unknown/unmapped harnesses (including ``"infrastructure"``),
    so the block never silently drops a value it does not recognize.
    """
    return _PROVENANCE_LABELS.get(harness, harness)


def _compute_diff(
    *,
    target_branch: str,
    cwd: Path,
) -> tuple[str, str]:
    """Compute unified diff and shortstat against the target branch.

    Returns:
        Tuple of (diff_text, stat_summary).

    Raises:
        RuntimeError: If git diff exits non-zero.
    """
    diff_proc = subprocess.run(
        ["git", "diff", f"{target_branch}...HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if diff_proc.returncode != 0:
        stderr = diff_proc.stderr.strip() if diff_proc.stderr else "unknown error"
        raise RuntimeError(f"git diff failed (exit {diff_proc.returncode}): {stderr}")

    stat_proc = subprocess.run(
        ["git", "diff", "--stat", f"{target_branch}...HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    stat_text = stat_proc.stdout.strip() if stat_proc.returncode == 0 else ""

    return diff_proc.stdout, stat_text


def _build_review_context(
    *,
    work_dir: Path,
    epic_dir: Path,
    story_id: str,
) -> ReviewContext:
    """Build ReviewContext from story artifacts on disk.

    Reads design.html and story.md (scope). Falls back gracefully when
    files are missing — review still proceeds with reduced context.

    Design excerpt probe order (D5, RAISE-17464): ``work_dir/design.html``,
    then ``work_dir/design.md`` — the layout used by bug/standalone-story/epic
    governance roots, none of which nest under ``epic_dir/stories/`` — then
    the original ``epic_dir/stories/{story_id}-design.html`` probe (RAISE-17422
    epic-story layout), then a fallback string.
    """
    story_num = story_id.lower()
    design_path = epic_dir / "stories" / f"{story_num}-design.html"
    work_dir_design_html = work_dir / "design.html"
    work_dir_design_md = work_dir / "design.md"

    if work_dir_design_html.exists():
        design_excerpt = work_dir_design_html.read_text(encoding="utf-8")[:2000]
    elif work_dir_design_md.exists():
        design_excerpt = work_dir_design_md.read_text(encoding="utf-8")[:2000]
    elif design_path.exists():
        design_excerpt = design_path.read_text(encoding="utf-8")[:2000]
    else:
        design_excerpt = f"No design document found at {design_path.name}"

    scope_path = work_dir / "story.md"
    if scope_path.exists():
        scope_summary = scope_path.read_text(encoding="utf-8")[:1000]
    else:
        scope_path = work_dir / "scope.md"
        if scope_path.exists():
            scope_summary = scope_path.read_text(encoding="utf-8")[:1000]
        else:
            scope_summary = "No scope document found"

    return ReviewContext(
        design_excerpt=design_excerpt,
        scope_summary=scope_summary,
    )


def request_pre_submission_review(
    *,
    target_branch: str,
    story_key: str,
    work_dir: Path,
    epic_dir: Path,
    story_id: str,
    cwd: Path,
    dimensions: tuple[str, ...] = _DEFAULT_DIMENSIONS,
) -> PreSubmissionResult:
    """Run a pre-submission cross-harness review.

    Orchestrates: diff computation → context packaging → adapter dispatch →
    telemetry emission. Fail-closed on infrastructure errors.

    Args:
        target_branch: Branch to diff against (e.g. "release/3.2.0").
        story_key: Jira key for telemetry (e.g. "RAISE-17424").
        work_dir: Story work directory containing story.md/scope.md.
        epic_dir: Epic directory containing stories/ with design artifacts.
        story_id: Story identifier (e.g. "S17422.2") for file resolution.
        cwd: Repository root for git operations.
        dimensions: Review dimensions to request.

    Returns:
        PreSubmissionResult with the adapter's verdict and telemetry status.
    """
    try:
        diff, diff_stats = _compute_diff(target_branch=target_branch, cwd=cwd)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        return _infrastructure_fail(str(exc), "diff computation")

    if not diff.strip():
        return _infrastructure_fail(
            "empty diff — no changes to review", "diff computation"
        )

    try:
        context = _build_review_context(
            work_dir=work_dir, epic_dir=epic_dir, story_id=story_id
        )
    except (OSError, ValueError) as exc:
        return _infrastructure_fail(str(exc), "context packaging")

    harnesses = resolve_review_harnesses(cwd)
    if not harnesses:
        return _infrastructure_fail(
            "no review harnesses configured", "harness resolution"
        )

    harness_name = harnesses[0]
    try:
        adapter = from_config(harness_name)
    except (HarnessConfigError, HarnessCommandError) as exc:
        return _infrastructure_fail(str(exc), "adapter creation")

    review = adapter.request_review(diff=diff, context=context, dimensions=dimensions)

    telemetry_emitted = False
    if review.verdict == "pass":
        telemetry_emitted = _emit_review_telemetry(story_key=story_key, cwd=cwd)

    return PreSubmissionResult(
        review=review,
        telemetry_emitted=telemetry_emitted,
        diff_stats=diff_stats,
    )


def _emit_review_telemetry(*, story_key: str, cwd: Path) -> bool:
    """Emit review_completed telemetry event. Returns True on success."""
    try:
        from raise_cli.telemetry.emit_work import emit_work_lifecycle

        emit_work_lifecycle(
            work_type="story",
            work_id=story_key,
            event="review_completed",
            phase_id="pre-submission",
            cwd=str(cwd),
        )
        return True
    except Exception:  # noqa: BLE001 — telemetry must never block the review result
        logger.warning("telemetry emission failed for %s", story_key, exc_info=True)
        return False


def _infrastructure_fail(reason: str, dimension: str) -> PreSubmissionResult:
    """Produce a fail-closed result for infrastructure errors."""
    return PreSubmissionResult(
        review=ReviewResult(
            verdict="fail",
            findings=(
                ReviewFinding(
                    file="",
                    line=0,
                    summary=reason,
                    fix_suggestion="",
                    dimension=dimension,
                ),
            ),
            harness="infrastructure",
            duration_seconds=0.0,
        ),
        telemetry_emitted=False,
        diff_stats="",
    )
