"""CLI command: ``rai scm pre-review`` — pre-submission review bridge (RAISE-17464).

The D-S3-2 seam pattern (see ``scm.py``'s ``create-mr`` docstring) applied to
``harness_review.request_pre_submission_review()``: a thin adapter from the
pure Python API to the THIN admission contract's bash conventions — one
stdout token pair (or, with ``--format json``, the full serialized result),
findings on stderr, and a fail-closed exit-code ladder the contract can branch
on with a plain ``case`` statement.

Registered onto ``scm_app`` from ``cli.commands.scm`` via a side-effect
import, mirroring ``scm_conflict.py`` — this keeps ``harness_review`` imports
out of the git-only ``scm.py`` (the package docstring insists the domains
stay separate: parallel, unrelated failure modes).
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.cli.commands.scm import (
    EXIT_CONFIG_ERROR,
    EXIT_OK,
    EXIT_REVIEW_FAILED,
    scm_app,
)
from raise_cli.config.paths import resolve_checkout_root
from raise_cli.harness_review import (
    PreSubmissionResult,
    is_infrastructure_failure,
    provenance_label,
    request_pre_submission_review,
)
from raise_cli.session.open_service import run_git

console = Console()
# Findings, warnings, and diagnostics go here so stdout carries only the
# token pair (or, with --format json, the serialized result) — same
# discipline as create-mr's MR-URL-only stdout.
err_console = Console(stderr=True)

_OUTPUT_FORMATS = ("tokens", "json")


def derive_context_dirs(work_dir: Path) -> tuple[Path, str]:
    """Derive ``(epic_dir, story_id)`` from a governance root (design D5).

    The QR-bearing governance root varies by work type: epic-owned stories
    nest under ``epic_dir/stories/{story_id}`` (``work_dir.parent.name ==
    "stories"``); bug, standalone-story, epic, spike, and initiative
    governance roots are flat (``work/bugs/KEY``, ``work/stories/KEY``,
    ``work/epics/eNNN``) and ``epic_dir`` is ``work_dir`` itself.

    Args:
        work_dir: The governance root (``GOVERNANCE_ROOT`` in the contract).

    Returns:
        ``(epic_dir, story_id)`` — ``story_id`` is always ``work_dir.name``.
    """
    story_id = work_dir.name
    epic_dir = work_dir.parent.parent if work_dir.parent.name == "stories" else work_dir
    return epic_dir, story_id


def _print_pass_summary(result: PreSubmissionResult) -> None:
    review = result.review
    err_console.print(
        f"pre-review: {review.harness} reviewed {result.diff_stats} "
        f"in {review.duration_seconds:.1f}s — PASS",
        markup=False,
        soft_wrap=True,
    )


def _print_findings(result: PreSubmissionResult) -> None:
    review = result.review
    err_console.print(
        f"pre-review: {review.harness} verdict FAIL "
        f"({len(review.findings)} findings, {review.duration_seconds:.1f}s)",
        markup=False,
        soft_wrap=True,
    )
    for finding in review.findings:
        err_console.print(
            f"  [{finding.dimension}] {finding.file}:{finding.line}",
            markup=False,
            soft_wrap=True,
        )
        err_console.print(f"    {finding.summary}", markup=False, soft_wrap=True)
        if finding.fix_suggestion:
            err_console.print(
                f"    fix: {finding.fix_suggestion}", markup=False, soft_wrap=True
            )
    err_console.print(
        "pre-review: MR not created — address findings, commit, "
        "re-run rai-quality-review, then /rai-mr-create",
        markup=False,
        soft_wrap=True,
    )


def _print_json(result: PreSubmissionResult) -> None:
    # Bare print, not console.print: rich would soft-wrap long JSON.
    print(json.dumps(dataclasses.asdict(result)))


def _validate_repo_root(repo_root: Path) -> None:
    """Exit 1 when *repo_root* is not a git repository (usage/config error)."""
    repo_check = run_git(repo_root, "rev-parse", "--show-toplevel")
    if repo_check is None or repo_check.returncode != 0:
        err_console.print(f"[red]ERROR {repo_root} is not a git repository[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR)


def _resolve_work_dir(work_dir: Path | None, repo_root: Path) -> Path:
    """Resolve ``--work-dir``, defaulting to *repo_root* (reduced context, D5)."""
    if work_dir is None:
        return repo_root
    effective_work_dir = work_dir.resolve()
    if not effective_work_dir.is_dir():
        err_console.print(f"[red]ERROR --work-dir {work_dir} is not a directory[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR)
    return effective_work_dir


def _emit_infrastructure_failure(
    result: PreSubmissionResult, *, strict: bool, output_format: str
) -> None:
    """Fallback policy for infra failures (D3): warn-and-proceed, or --strict."""
    review = result.review
    reason = review.findings[0].summary if review.findings else "unknown reason"
    if strict:
        err_console.print(
            "[red]pre-review: harness unavailable and --strict set — blocking.[/red]"
        )
        if output_format == "json":
            _print_json(result)
        raise typer.Exit(EXIT_REVIEW_FAILED)

    err_console.print(
        f"[yellow]pre-review: WARNING harness unavailable ({reason}) — "
        "proceeding without review provenance. Use --strict to block "
        "instead.[/yellow]"
    )
    if output_format == "json":
        _print_json(result)
    else:
        print("skipped none")
    raise typer.Exit(EXIT_OK)


def _emit_review_outcome(result: PreSubmissionResult, *, output_format: str) -> None:
    """Emit the token/JSON contract and exit for a real (non-infra) verdict."""
    review = result.review
    if review.verdict == "fail":
        _print_findings(result)
        if output_format == "json":
            _print_json(result)
        raise typer.Exit(EXIT_REVIEW_FAILED)

    _print_pass_summary(result)
    if output_format == "json":
        _print_json(result)
    else:
        print(f"pass {provenance_label(review.harness)}")
    raise typer.Exit(EXIT_OK)


@scm_app.command("pre-review")
def pre_review_command(
    target: Annotated[
        str,
        typer.Option(
            "--target",
            help="Git revision to diff against, e.g. refs/remotes/origin/release/3.2.0",
        ),
    ],
    story_key: Annotated[
        str,
        typer.Option("--story-key", help="Work id for telemetry, e.g. RAISE-17464"),
    ],
    work_dir: Annotated[
        Path | None,
        typer.Option(
            "--work-dir",
            help="Governance dir holding design/scope (default: repo root, reduced context)",
        ),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict", help="Treat harness unavailability as a failing verdict"
        ),
    ] = False,
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: tokens or json")
    ] = "tokens",
    project: Annotated[
        Path | None,
        typer.Option(
            "--project", "-p", help="Repository root (default: this checkout)"
        ),
    ] = None,
) -> None:
    """Run a synchronous pre-submission cross-harness review before push.

    stdout carries exactly one token pair — ``pass <label>`` or
    ``skipped none`` — so the calling shell contract can ``read`` it directly;
    with ``--format json`` stdout instead carries the full serialized
    ``PreSubmissionResult``, for tests and future cockpit use. Every other
    message (pass summary, findings, warnings) goes to stderr.

    Exit codes:
      0  verdict ``pass``, or harness unavailable under default policy
         (``skipped``)
      1  usage/config error — bad ``--format``, bad ``--work-dir``, or
         ``--project`` is not a git repository
      6  a harness actually reviewed and returned ``fail``, or the harness
         was unavailable and ``--strict`` was set
    """
    if output_format not in _OUTPUT_FORMATS:
        err_console.print(f"[red]ERROR unknown --format {output_format!r}[/red]")
        raise typer.Exit(EXIT_CONFIG_ERROR)

    repo_root = (project or resolve_checkout_root()).resolve()
    _validate_repo_root(repo_root)
    effective_work_dir = _resolve_work_dir(work_dir, repo_root)
    epic_dir, story_id = derive_context_dirs(effective_work_dir)

    result = request_pre_submission_review(
        target_branch=target,
        story_key=story_key,
        work_dir=effective_work_dir,
        epic_dir=epic_dir,
        story_id=story_id,
        cwd=repo_root,
    )

    if is_infrastructure_failure(result):
        _emit_infrastructure_failure(result, strict=strict, output_format=output_format)

    _emit_review_outcome(result, output_format=output_format)
