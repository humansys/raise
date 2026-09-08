"""DDD CLI group — rai ddd discover / rai ddd refine / rai ddd validate / rai ddd report.

RAISE-16761: Python-first BC discovery command using static signals only.
RAISE-16803: refine subcommand — incremental BC refinement with HITL gate.
RAISE-16918: validate subcommand — tactical accuracy gate; report subcommand — BC breakdown HTML.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.table import Table

from raise_cli.cli.error_handler import cli_error
from raise_cli.config.paths import get_memory_dir, resolve_checkout_root
from raise_cli.ddd.discover import (
    DEFAULT_SWEEP_STEPS,
    BCDiscoveryResult,
    BCSuggestion,
    ThresholdSweepResult,
    discover_bcs,
    prepare_discovery_inputs,
    sweep_thresholds,
)
from raise_cli.ddd.domain_model import (
    BoundedContext,
    DomainModel,
    domain_model_to_prompt_context,
    get_domain_model_draft_path,
    get_domain_model_path,
    load_domain_model,
)
from raise_cli.ddd.pipeline import classify_graph

logger = logging.getLogger(__name__)

ddd_app = typer.Typer(
    name="ddd",
    help="DDD ontological tooling — BC discovery, classification, and validation.",
    no_args_is_help=True,
)


# Stub forces Typer to treat ddd_app as a group (single-command apps bypass routing).
@ddd_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # type: ignore[reportUnusedFunction]
    pass  # pragma: no cover


console = Console()
err_console = Console(stderr=True)

# Default index file — mirrors graph.py convention
_INDEX_FILE = "index.json"


def _get_default_index_path() -> Path:
    return get_memory_dir() / _INDEX_FILE


def _load_graph(index_path: Path | None) -> object:
    """Load the graph from the active backend. Exits with error on failure."""
    from raise_cli.graph.backends import get_active_backend

    unified_path = index_path or _get_default_index_path()
    try:
        backend = get_active_backend(unified_path, explicit_path=index_path is not None)
        graph = backend.load()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first to create the index, then 'rai graph classify' to classify symbols.",
            exit_code=4,
        )
        raise  # unreachable — cli_error exits
    return graph


def _preview_suggestions(result: BCDiscoveryResult) -> None:
    """Render BC suggestions as a Rich table."""
    r = result
    if not r.bc_suggestions:
        console.print("\n[yellow]No Domain-classified symbols found in graph.[/yellow]")
        console.print(
            "Hint: run [bold]rai graph classify[/bold] first to classify symbols.\n"
        )
        return

    table = Table(
        title=f"BC Discovery — {len(r.bc_suggestions)} suggestion(s)  "
        f"[dim](overall confidence: {r.confidence})[/dim]",
        show_lines=True,
    )
    table.add_column("BC Name", style="bold cyan", no_wrap=True)
    table.add_column("Symbols", justify="right")
    table.add_column("Confidence", justify="right")
    table.add_column("Rationale")

    for s in r.bc_suggestions:
        conf_style = (
            "green"
            if s.confidence >= 0.7
            else ("yellow" if s.confidence >= 0.4 else "red")
        )
        name_col = f"{s.name} [red]\\[!][/red]" if s.split_candidate else s.name
        table.add_row(
            name_col,
            str(len(s.symbols)),
            f"[{conf_style}]{s.confidence:.2f}[/{conf_style}]",
            s.rationale,
        )

    console.print()
    console.print(table)
    if any(s.split_candidate for s in r.bc_suggestions):
        console.print("[dim][!] = split candidate (confidence < 0.15)[/dim]")
    console.print(f"\n[dim]Signal sources: {', '.join(r.signal_sources)}[/dim]\n")


def _build_domain_model_yaml(result: BCDiscoveryResult) -> dict[str, object]:
    """Build a domain-model.yaml draft dict from BCDiscoveryResult."""
    r = result
    bcs: list[dict[str, object]] = []
    for s in r.bc_suggestions:
        bcs.append(
            {
                "name": s.name,
                "description": s.description or s.rationale,
                "modules": list(s.symbols),  # placeholder — architect will refine
                "confidence": round(s.confidence, 3),
            }
        )
    return {
        "# generated": f"by rai ddd discover on {datetime.now(tz=UTC).isoformat()}",
        "# signals": ", ".join(r.signal_sources),
        "# overall_confidence": r.confidence,
        "bounded_contexts": bcs,
    }


def _preview_sweep(sweep: ThresholdSweepResult) -> None:
    """Render threshold sweep advisory as a Rich table."""
    table = Table(
        title=f"Threshold Sweep — target {sweep.target_bcs} BC(s)  "
        f"[dim](recommended: --merge-threshold {sweep.recommended_threshold})[/dim]",
        show_lines=True,
    )
    table.add_column("Threshold", justify="right", style="cyan")
    table.add_column("BC Count", justify="right")
    table.add_column("Stable", justify="center")
    table.add_column("Merges")
    table.add_column("", no_wrap=True)

    for step in sweep.steps:
        stable_marker = "[green]✓[/green]" if step.is_stable else "[dim]–[/dim]"
        recommended_marker = (
            "[bold green]← RECOMENDADO[/bold green]" if step.is_recommended else ""
        )
        merges_str = ", ".join(step.merges) if step.merges else "[dim]none[/dim]"
        table.add_row(
            str(step.threshold),
            str(step.bc_count),
            stable_marker,
            merges_str,
            recommended_marker,
        )

    console.print()
    console.print(table)
    console.print(
        f"\n[dim]Recommended threshold:[/dim] [bold]{sweep.recommended_threshold}[/bold]"
        f"  [dim](closest stable step to target {sweep.target_bcs} BCs)[/dim]\n"
    )


def _write_run_artifact(
    result: BCDiscoveryResult,
    run_artifact: Path,
    sweep: ThresholdSweepResult | None = None,
) -> None:
    """Write the BCDiscoveryResult as JSON run artifact."""
    run_artifact.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "run_at": datetime.now(tz=UTC).isoformat(),
        "confidence": result.confidence,
        "overall_confidence": result.overall_confidence,
        "signal_sources": result.signal_sources,
        "bc_suggestions": [s.model_dump() for s in result.bc_suggestions],
    }
    if sweep is not None:
        payload["threshold_sweep"] = sweep.model_dump()
    run_artifact.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


@ddd_app.command("discover")
def discover(
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Path to project root (default: cwd). Graph must already be built.",
        ),
    ] = None,
    language: Annotated[
        str,
        typer.Option(
            "--language", "-l", help="Primary language filter (default: python)."
        ),
    ] = "python",
    n_bcs: Annotated[
        int,
        typer.Option(
            "--n-bcs", "-n", help="Maximum number of BC suggestions (default: 7)."
        ),
    ] = 7,
    merge_threshold: Annotated[
        int | None,
        typer.Option(
            "--merge-threshold",
            "-t",
            help="Fixed merge threshold (skips advisor). Mutually exclusive with --target-bcs.",
        ),
    ] = None,
    target_bcs: Annotated[
        int | None,
        typer.Option(
            "--target-bcs",
            help=(
                "Run threshold sweep advisor and pick the threshold closest to this BC count. "
                "Mutually exclusive with --merge-threshold. Default: runs advisor with n_bcs."
            ),
        ),
    ] = None,
    sweep_steps: Annotated[
        str,
        typer.Option(
            "--sweep-steps",
            help="Comma-separated threshold values for advisor sweep (default: 3,6,10,14,20,30).",
        ),
    ] = ",".join(str(s) for s in DEFAULT_SWEEP_STEPS),
    out: Annotated[
        Path | None,
        typer.Option(
            "--out",
            "-o",
            help="Output path for domain-model draft (default: .raise/domain-model.draft.yaml). Use .raise/domain-model.yaml to promote to canonical.",
        ),
    ] = None,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation gate and write domain-model.yaml directly (for CI).",
        ),
    ] = False,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path (default: auto-detect)."),
    ] = None,
    no_naming: Annotated[
        bool,
        typer.Option(
            "--no-naming",
            help=(
                "Skip the LLM naming step; keep static module-path BC names "
                "(reproducible output for CI / no API key)."
            ),
        ),
    ] = False,
) -> None:
    """Discover Bounded Context proposals from Domain-classified symbols.

    Reads the knowledge graph, clusters Domain-classified ('D') symbols using
    static signals (module co-location + import coupling), and proposes N
    Bounded Contexts with confidence gradients.

    By default the threshold advisor sweeps candidate merge thresholds and
    picks the one closest to n_bcs BCs. Use --target-bcs to set a different
    target, or --merge-threshold to bypass the advisor entirely.

    The proposal is printed to stdout for architect review. You are asked for
    confirmation before domain-model.yaml is written. Use --yes to skip the
    interactive gate (CI mode).

    Examples:
        # Discover BCs using advisor (default)
        $ rai ddd discover

        # Advisor targeting 5 BCs
        $ rai ddd discover --target-bcs 5

        # Fixed threshold, no advisor
        $ rai ddd discover --merge-threshold 8

        # CI mode: skip confirmation gate
        $ rai ddd discover --yes

        # Use a specific graph index
        $ rai ddd discover --index .raise/rai/memory/index.json
    """
    # Post-parse mutual exclusion
    if merge_threshold is not None and target_bcs is not None:
        cli_error(
            "--merge-threshold and --target-bcs are mutually exclusive.",
            hint="Use --merge-threshold to fix the threshold or --target-bcs to run the advisor.",
        )
        raise typer.Exit(1)

    # Resolve project root for run artifact and output paths
    project_root = resolve_checkout_root(path or Path.cwd())

    # Run artifact: work/ directory, timestamped
    ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S")
    run_artifact = project_root / "work" / f"bc-discovery-{ts}.json"

    # RAISE-16895: default to draft path to avoid overwriting human-authored BC catalog.
    # The canonical path (.raise/domain-model.yaml) is only written when --out targets it.
    output_yaml = out or get_domain_model_draft_path(project_root)

    console.print(
        f"\n[bold]rai ddd discover[/bold]  language={language}  n_bcs={n_bcs}"
    )
    console.print(
        f"Graph: loading from {'custom index' if index_path else 'default path'}"
    )

    # Load graph
    graph = _load_graph(index_path)

    # Determine effective merge_threshold: advisor or fixed
    sweep: ThresholdSweepResult | None = None
    effective_threshold: int

    if merge_threshold is not None:
        # Fixed threshold — bypass advisor
        effective_threshold = merge_threshold
    else:
        # Advisor mode: sweep thresholds
        groups, coupling = prepare_discovery_inputs(graph)  # type: ignore[arg-type]

        try:
            parsed_steps = [int(s.strip()) for s in sweep_steps.split(",") if s.strip()]
        except ValueError as exc:
            cli_error(
                f"--sweep-steps value {sweep_steps!r} contains non-integer tokens.",
                hint="Provide a comma-separated list of positive integers, e.g. '3,6,9,12'.",
            )
            raise typer.Exit(1) from exc
        if not parsed_steps:
            cli_error(
                f"--sweep-steps value {sweep_steps!r} produced an empty list.",
                hint="Provide at least one positive integer, e.g. '3,6,9,12'.",
            )
            raise typer.Exit(1)
        if any(s <= 0 for s in parsed_steps):
            cli_error(
                "--sweep-steps values must all be positive integers (> 0).",
                hint=f"Got: {parsed_steps}. Remove any zero or negative entries.",
            )
            raise typer.Exit(1)
        advisor_target = target_bcs if target_bcs is not None else n_bcs

        sweep_result: ThresholdSweepResult = sweep_thresholds(
            groups,
            coupling,
            target_bcs=advisor_target,
            sweep_steps=parsed_steps,
        )
        sweep = sweep_result
        _preview_sweep(sweep_result)
        effective_threshold = sweep_result.recommended_threshold

    # Run discovery with effective threshold
    result = discover_bcs(
        graph,  # type: ignore[arg-type]
        n_bcs=n_bcs,
        run_artifact=run_artifact,
        merge_threshold=effective_threshold,
    )

    # LLM naming step (RAISE-16790): enrich BC names for preview + artifact only.
    # domain-model.yaml keeps static names so `rai ddd refine` can compute deltas
    # without mismatching LLM names against its own static discover output.
    if not no_naming and result.bc_suggestions:
        from raise_cli.ddd.naming import name_bcs_with_llm

        named = name_bcs_with_llm(result.bc_suggestions)
        display_result = result.model_copy(update={"bc_suggestions": named})
    else:
        display_result = result

    # Write run artifact with LLM names (always — before confirmation gate)
    _write_run_artifact(display_result, run_artifact, sweep=sweep)
    console.print(f"[dim]Run artifact: {run_artifact}[/dim]")

    # Preview suggestions (LLM names when available)
    _preview_suggestions(display_result)

    # Early exit if no suggestions
    if not result.bc_suggestions:
        raise typer.Exit(code=0)

    # Confirmation gate
    if not yes:
        llm_note = (
            " (LLM-suggested names in artifact; YAML uses static names for refine compatibility)"
            if display_result is not result
            else ""
        )
        confirmed = typer.confirm(
            f"Write {len(result.bc_suggestions)} BC suggestions to {output_yaml}?{llm_note}",
            default=False,
        )
        if not confirmed:
            console.print("[yellow]Aborted — domain-model.yaml not written.[/yellow]\n")
            raise typer.Exit(code=0)

    # Write domain-model.yaml with static names (refine-compatible)
    draft = _build_domain_model_yaml(result)
    output_yaml.parent.mkdir(parents=True, exist_ok=True)

    # Remove non-YAML-standard comment keys before serialising, then re-add as
    # a YAML comment block via a raw prepend.
    comments = {k: v for k, v in draft.items() if k.startswith("#")}
    data = {k: v for k, v in draft.items() if not k.startswith("#")}

    comment_block = "\n".join(f"{k}: {v}" for k, v in comments.items())
    yaml_body = yaml.dump(data, default_flow_style=False, allow_unicode=True)

    output_yaml.write_text(
        f"{comment_block}\n\n{yaml_body}",
        encoding="utf-8",
    )
    console.print(
        f"[green]domain-model.yaml written:[/green] {output_yaml}\n"
        f"  Review and ratify with your team before running [bold]rai graph classify[/bold].\n"
    )


# =============================================================================
# Helpers for `refine` command (RAISE-16803)
# =============================================================================

_DEFAULT_REFINE_TARGET = 7  # fallback when domain-model has no BCs


def _load_graph_and_backend(index_path: Path | None) -> tuple[object, object]:
    """Load the graph and return (graph, backend). Exits with error on failure."""
    from raise_cli.graph.backends import get_active_backend

    unified_path = index_path or _get_default_index_path()
    try:
        backend = get_active_backend(unified_path, explicit_path=index_path is not None)
        graph = backend.load()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint=(
                "Run 'rai graph build' first to create the index, "
                "then 'rai ddd discover' to generate a domain model."
            ),
            exit_code=4,
        )
        raise  # unreachable — cli_error raises typer.Exit
    return graph, backend


def _compute_delta(
    current_bcs: list[BoundedContext],
    suggested_bcs: list[BCSuggestion],
) -> dict[str, set[str]]:
    """Compute the set-difference delta between current domain model and suggestions.

    Returns a dict with keys:
    - ``new``      — BC names present in suggestions but not in the current model.
    - ``removed``  — BC names present in the current model but not in suggestions.
    - ``retained`` — BC names present in both.
    """
    current_names: set[str] = {bc.name for bc in current_bcs}
    suggested_names: set[str] = {bc.name for bc in suggested_bcs}
    return {
        "new": suggested_names - current_names,
        "removed": current_names - suggested_names,
        "retained": current_names & suggested_names,
    }


def _serialize_accepted_bcs(
    original: DomainModel,
    accepted: list[tuple[str, BCSuggestion]],
) -> DomainModel:
    """Build an updated DomainModel from the list of accepted (final_name, suggestion) pairs.

    For each accepted pair:
    - If ``final_name`` matches an existing BC in ``original``, the original
      BoundedContext is preserved (retaining its description, modules, terms).
    - Otherwise, a new BoundedContext is created from the suggestion's rationale
      and symbols.

    Args:
        original:  The current validated DomainModel loaded from domain-model.yaml.
        accepted:  Ordered list of ``(final_name, suggestion)`` pairs decided by
                   the HITL gate or ``--yes`` flag.

    Returns:
        A new :class:`DomainModel` with ``bounded_contexts`` set to the accepted list.
    """
    original_by_name: dict[str, BoundedContext] = {
        bc.name: bc for bc in original.bounded_contexts
    }
    bcs: list[BoundedContext] = []
    for final_name, suggestion in accepted:
        if final_name in original_by_name:
            # Retained — preserve original metadata (description, modules, terms)
            bcs.append(original_by_name[final_name])
        else:
            # New or renamed — create from discovery suggestion
            bcs.append(
                BoundedContext(
                    name=final_name,
                    description=suggestion.rationale,
                    modules=list(suggestion.symbols),
                )
            )
    return DomainModel(
        version=original.version,
        bounded_contexts=bcs,
        ratified_by=original.ratified_by,
        ratified_at=original.ratified_at,
    )


def _discover_bcs_from_graph(
    graph: object,
    merge_threshold: int,
    n_bcs: int,
    project_root: Path,
) -> BCDiscoveryResult:
    """Run discover_bcs with a timestamped run artifact path under *project_root*.

    Thin wrapper so the CLI can mock discovery without coupling to the artifact path.
    """
    ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S")
    run_artifact = project_root / "work" / f"bc-refine-{ts}.json"
    return discover_bcs(
        graph,  # type: ignore[arg-type]
        n_bcs=n_bcs,
        run_artifact=run_artifact,
        merge_threshold=merge_threshold,
    )


def _write_domain_model_yaml(path: Path, model: DomainModel) -> None:
    """Write a validated DomainModel to a YAML file at *path*.

    Creates parent directories if they do not exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = model.model_dump(exclude_none=False)
    path.write_text(
        yaml.safe_dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


def _print_refine_delta(
    delta: dict[str, set[str]],
    suggestions: list[BCSuggestion],
) -> None:
    """Print a Rich table summarising the delta between current model and suggestions."""
    table = Table(
        title=f"DDD Refine — delta  "
        f"[dim]new: {len(delta['new'])}  "
        f"retained: {len(delta['retained'])}  "
        f"removed: {len(delta['removed'])}[/dim]",
        show_lines=True,
    )
    table.add_column("BC Name", style="bold cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Confidence", justify="right")
    table.add_column("Rationale")

    suggestion_by_name: dict[str, BCSuggestion] = {s.name: s for s in suggestions}

    for name in sorted(delta["retained"]):
        s = suggestion_by_name.get(name)
        conf = f"{s.confidence:.2f}" if s else "—"
        table.add_row(name, "[green]retained[/green]", conf, s.rationale if s else "")

    for name in sorted(delta["new"]):
        s = suggestion_by_name.get(name)
        conf = f"{s.confidence:.2f}" if s else "—"
        table.add_row(name, "[blue]new[/blue]", conf, s.rationale if s else "")

    for name in sorted(delta["removed"]):
        table.add_row(name, "[yellow]removed[/yellow]", "—", "not in new suggestions")

    console.print()
    console.print(table)
    console.print()


def _run_hitl_gate(
    original: DomainModel,
    suggestions: list[BCSuggestion],
    delta: dict[str, set[str]],
    *,
    yes: bool,
    no_naming: bool,
) -> list[tuple[str, BCSuggestion]]:
    """Run the per-BC HITL gate.

    Returns a list of ``(final_name, suggestion)`` pairs for all accepted BCs.

    Retained BCs are always included without prompting.  New BCs are presented
    one at a time with a Y/n confirm and an optional rename prompt (unless
    ``--yes`` or ``--no-naming`` suppresses them).
    """
    suggestion_by_name: dict[str, BCSuggestion] = {s.name: s for s in suggestions}
    accepted: list[tuple[str, BCSuggestion]] = []

    # Retained — auto-accept, preserve original
    for bc in original.bounded_contexts:
        if bc.name in delta["retained"]:
            s = suggestion_by_name.get(bc.name)
            if s is not None:
                accepted.append((bc.name, s))

    # New — HITL per suggestion
    for name in sorted(delta["new"]):
        s = suggestion_by_name.get(name)
        if s is None:
            continue
        if yes or typer.confirm(f"Add BC '{name}'?", default=True):
            final_name = name
            if not yes and not no_naming:
                final_name = typer.prompt(f"  Name [{name}]", default=name)
            accepted.append((final_name, s))

    # Removed — HITL: ask user whether to keep BCs absent from new suggestions
    accepted.extend(_hitl_removed_bcs(original, delta, yes=yes))

    return accepted


def _hitl_removed_bcs(
    original: DomainModel,
    delta: dict[str, set[str]],
    *,
    yes: bool,
) -> list[tuple[str, BCSuggestion]]:
    """Return (name, suggestion) pairs for removed BCs the user chooses to keep.

    For each BC present in the current domain-model but absent from new suggestions,
    the user is prompted: keep it (Y) or drop it (n).  ``--yes`` preserves all.
    """
    original_by_name: dict[str, BoundedContext] = {
        bc.name: bc for bc in original.bounded_contexts
    }
    kept: list[tuple[str, BCSuggestion]] = []
    for name in sorted(delta["removed"]):
        bc = original_by_name.get(name)
        if bc is None:
            continue
        keep = yes or typer.confirm(
            f"BC '{name}' was not found in suggestions — keep it?", default=True
        )
        if keep:
            kept.append(
                (
                    name,
                    BCSuggestion(
                        name=name,
                        symbols=list(bc.modules or []),
                        confidence=1.0,
                        rationale="preserved by user (not in new suggestions)",
                    ),
                )
            )
    return kept


# =============================================================================
# `refine` command (RAISE-16803)
# =============================================================================


@ddd_app.command("refine")
def refine(
    path: Annotated[
        Path | None,
        typer.Argument(
            help=(
                "Path to project root (default: cwd). "
                "domain-model.yaml must already exist (run 'rai ddd discover' first)."
            ),
        ),
    ] = None,
    target_bcs: Annotated[
        int | None,
        typer.Option(
            "--target-bcs",
            help=(
                "Target BC count for threshold advisor. "
                "Defaults to the current BC count in domain-model.yaml."
            ),
        ),
    ] = None,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path (default: auto-detect)."),
    ] = None,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Accept all suggestions without interactive confirmation (CI mode).",
        ),
    ] = False,
    no_naming: Annotated[
        bool,
        typer.Option(
            "--no-naming",
            help="Skip the rename prompt — accepted BCs keep their suggested names.",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Print delta and HITL output but do not write files or persist graph.",
        ),
    ] = False,
) -> None:
    """Refine the domain-model.yaml using fresh BC discovery suggestions.

    Reads the existing domain-model.yaml, re-classifies the graph with the
    current domain context, discovers new BC proposals, computes the delta
    (new / retained / removed BCs), and presents an interactive gate for
    per-BC accept / rename / reject decisions before writing the updated file.

    Use ``--yes`` to skip all interactive prompts (CI mode).
    Use ``--dry-run`` to preview the delta without writing anything.

    Examples:
        # Interactive refinement
        $ rai ddd refine

        # CI mode — accept all suggestions
        $ rai ddd refine --yes

        # Preview only
        $ rai ddd refine --yes --dry-run

        # Target 5 BCs in the advisor sweep
        $ rai ddd refine --target-bcs 5
    """
    # ------------------------------------------------------------------
    # 1. Load domain-model.yaml (abort if missing)
    # RAISE-16895: if canonical path absent, fall back to draft path so
    # the rai ddd discover → rai ddd refine workflow still functions.
    # ------------------------------------------------------------------
    project_root = resolve_checkout_root(path or Path.cwd())
    dm_path = get_domain_model_path(project_root)
    if not dm_path.exists():
        draft_path = get_domain_model_draft_path(project_root)
        if draft_path.exists():
            console.print(
                f"[yellow]domain-model.yaml not found; using draft at {draft_path}[/yellow]\n"
                "  To promote: copy or rename it to .raise/domain-model.yaml"
            )
            dm_path = draft_path
    # load_domain_model raises typer.Exit(2) via cli_error if file missing
    model = load_domain_model(dm_path)

    console.print(
        f"\n[bold]rai ddd refine[/bold]  "
        f"current BCs: {len(model.bounded_contexts)}  "
        f"{'dry-run' if dry_run else ''}"
    )

    # ------------------------------------------------------------------
    # 2. Load graph + classify with domain-model hints
    # ------------------------------------------------------------------
    graph, backend = _load_graph_and_backend(index_path)

    domain_ctx = domain_model_to_prompt_context(model)
    cls_report = classify_graph(
        graph,  # type: ignore[arg-type]
        domain_context=domain_ctx or None,
        dry_run=dry_run,
    )
    console.print(
        f"[dim]Classified {cls_report.total} symbols "
        f"({cls_report.classified} updated)[/dim]"
    )

    # ------------------------------------------------------------------
    # 3. Discover BC suggestions via threshold sweep
    # ------------------------------------------------------------------
    effective_target = target_bcs or max(
        len(model.bounded_contexts), _DEFAULT_REFINE_TARGET
    )
    groups, coupling = prepare_discovery_inputs(graph)  # type: ignore[arg-type]
    sweep = sweep_thresholds(groups, coupling, target_bcs=effective_target)
    effective_threshold = sweep.recommended_threshold

    result = _discover_bcs_from_graph(
        graph, effective_threshold, effective_target, project_root
    )

    if not result.bc_suggestions:
        console.print(
            "\n[yellow]No Domain-classified symbols found — "
            "run 'rai graph classify' first.[/yellow]\n"
        )
        raise typer.Exit(code=0)

    # ------------------------------------------------------------------
    # 4. Compute delta vs current domain-model.yaml
    # ------------------------------------------------------------------
    delta = _compute_delta(model.bounded_contexts, result.bc_suggestions)

    # ------------------------------------------------------------------
    # 5. Print delta table
    # ------------------------------------------------------------------
    _print_refine_delta(delta, result.bc_suggestions)

    # ------------------------------------------------------------------
    # 6. HITL gate
    # ------------------------------------------------------------------
    accepted = _run_hitl_gate(
        model,
        result.bc_suggestions,
        delta,
        yes=yes,
        no_naming=no_naming,
    )

    # ------------------------------------------------------------------
    # 7. Dry-run guard — print summary and exit without writing
    # ------------------------------------------------------------------
    if dry_run:
        console.print(
            f"[yellow]--dry-run: {len(accepted)} BC(s) would be written "
            f"to {dm_path} — no changes made.[/yellow]\n"
        )
        raise typer.Exit(code=0)

    # ------------------------------------------------------------------
    # 8. Write updated domain-model.yaml
    # ------------------------------------------------------------------
    updated_model = _serialize_accepted_bcs(model, accepted)
    _write_domain_model_yaml(dm_path, updated_model)
    console.print(
        f"[green]domain-model.yaml updated:[/green] {dm_path}\n"
        f"  {len(accepted)} BC(s) written "
        f"({len(delta['new'])} new, {len(delta['retained'])} retained, "
        f"{len(delta['removed'])} removed).\n"
        f"  Run [bold]rai graph classify --context {dm_path}[/bold] to propagate hints.\n"
    )

    # ------------------------------------------------------------------
    # 9. Persist graph (classification mutations from step 2)
    # ------------------------------------------------------------------
    backend.persist(graph)  # type: ignore[union-attr]


# =============================================================================
# GT auto-discovery helper (shared by validate + report commands)
# =============================================================================

_GT_CANDIDATES = [
    "packages/raise-cli/tests/ddd/gt_tactical.yaml",
    "tests/ddd/gt_tactical.yaml",
]

_TACTICAL_TYPES = [
    "entity",
    "value_object",
    "domain_service",
    "domain_event",
    "aggregate_root",
    "factory",
    "repository_interface",
]


def _auto_discover_gt(cwd: Path) -> Path | None:
    """Search for gt_tactical.yaml relative to *cwd*."""
    for rel in _GT_CANDIDATES:
        candidate = cwd / rel
        if candidate.exists():
            return candidate
    return None


def _load_graph_or_exit(index_path: Path | None) -> object:
    """Load the graph backend and graph, exiting with error on failure."""
    from raise_cli.graph.backends import get_active_backend

    unified_path = index_path or _get_default_index_path()
    try:
        backend = get_active_backend(unified_path, explicit_path=index_path is not None)
        return backend.load()
    except FileNotFoundError as e:
        cli_error(
            str(e),
            hint="Run 'rai graph build' first, then 'rai graph ddd type' to annotate symbols.",
            exit_code=4,
        )
        raise  # unreachable — cli_error exits


def _extract_classified(graph: object) -> dict[str, str]:
    """Extract symbol_id → tactical_type from graph annotations.

    Annotations are merged into node metadata at load time (RAISE-16596);
    ``graph.annotations`` is not a Graph attribute — iterate concepts instead.
    """
    classified: dict[str, str] = {}
    if hasattr(graph, "annotations"):
        for sym_id, ann_map in graph.annotations.items():  # type: ignore[union-attr]
            t = ann_map.get("ddd_tactical_type")
            if t:
                classified[sym_id] = str(t)
    elif hasattr(graph, "iter_concepts"):
        for concept in graph.iter_concepts():  # type: ignore[union-attr]
            t = (concept.metadata or {}).get("ddd_tactical_type")
            if t:
                classified[concept.id] = str(t)
    return classified


def _print_accuracy_table(
    report: object,
    threshold: float,
) -> None:
    """Print Rich per-type accuracy table + summary line."""
    from raise_cli.ddd.tactical_validation import TacticalAccuracyReport

    r: TacticalAccuracyReport = report  # type: ignore[assignment]
    table = Table(
        title=f"Tactical Accuracy  [dim](threshold: {threshold:.0%})[/dim]",
        show_lines=True,
    )
    table.add_column("Type", style="bold cyan", no_wrap=True)
    table.add_column("Correct", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Precision", justify="right")

    for t, counts in sorted(r.per_type.items()):
        c, tot = counts["correct"], counts["total"]
        prec = c / tot if tot > 0 else 0.0
        style = "green" if prec >= threshold else "red"
        table.add_row(t, str(c), str(tot), f"[{style}]{prec:.1%}[/{style}]")

    console.print()
    console.print(table)

    gate_style = "green" if r.gate_passed else "red"
    console.print(
        f"\nMicro-avg precision: [{gate_style}]{r.micro_avg_precision:.1%}[/{gate_style}]  "
        f"(correct={r.correct_count}/{r.total_gt}, "
        f"missing={r.missing_count}, "
        f"threshold={threshold:.0%})"
    )
    if r.drift_entries:
        console.print(
            f"\n[yellow]{len(r.drift_entries)} drift(s) detected "
            f"(gt≠current annotation)[/yellow]"
        )
    if r.gate_passed:
        console.print("\n[green]Gate PASSED[/green]\n")
    else:
        console.print("\n[red]Gate FAILED — precision below threshold.[/red]\n")


def _annotations_from_graph(graph: object) -> dict[str, dict[str, object]]:
    """Extract tactical annotations keyed by symbol_id.

    Annotations live in node metadata (merged at load time, RAISE-16596).
    """
    if hasattr(graph, "annotations"):
        return {
            sym_id: dict(ann_map)
            for sym_id, ann_map in graph.annotations.items()  # type: ignore[union-attr]
            if ann_map.get("ddd_tactical_type")
        }
    if hasattr(graph, "iter_concepts"):
        return {
            concept.id: dict(meta)
            for concept in graph.iter_concepts()  # type: ignore[union-attr]
            if (meta := concept.metadata or {}) and meta.get("ddd_tactical_type")
        }
    return {}


def _bc_map_from_graph(graph: object) -> dict[str, str]:
    """Extract symbol_id → BC-name map from graph edges."""
    if hasattr(graph, "nodes"):
        bc_map: dict[str, str] = {}
        for sym_id, node in graph.nodes.items():  # type: ignore[union-attr]
            bc_val = getattr(node, "bc", None) or (
                node.get("bc") if isinstance(node, dict) else None
            )
            if bc_val:
                bc_map[sym_id] = str(bc_val)
        return bc_map
    if hasattr(graph, "iter_relationships"):
        return {
            rel.source: rel.target.removeprefix("BC-")
            for rel in graph.iter_relationships()  # type: ignore[union-attr]
            if rel.type == "belongs_to" and rel.target.startswith("BC-")
        }
    return {}


def _extract_annotations_and_bc_map(
    graph: object,
) -> tuple[dict[str, dict[str, object]], dict[str, str]]:
    """Extract tactical annotations and BC assignments from graph."""
    return _annotations_from_graph(graph), _bc_map_from_graph(graph)


def _print_bc_table(
    breakdown: dict[str, dict[str, int]],
    total: int,
) -> None:
    """Print Rich BC breakdown table."""
    table = Table(
        title=f"Tactical BC Breakdown  [dim]({total} classified symbols)[/dim]",
        show_lines=True,
    )
    table.add_column("BC", style="bold cyan", no_wrap=True)
    for t in _TACTICAL_TYPES:
        table.add_column(t[:8], justify="right")
    table.add_column("Total", justify="right", style="bold")
    for bc_name in sorted(breakdown):
        counts = breakdown[bc_name]
        row: list[str] = [bc_name]
        row.extend(str(counts.get(t, 0)) for t in _TACTICAL_TYPES)
        row.append(str(sum(counts.values())))
        table.add_row(*row)
    console.print()
    console.print(table)
    console.print()


# =============================================================================
# `validate` command (RAISE-16918 D3)
# =============================================================================


@ddd_app.command("validate")
def validate(
    tactical: Annotated[
        bool,
        typer.Option(
            "--tactical/--no-tactical",
            help="Run tactical type accuracy validation (default: True).",
        ),
    ] = True,
    gt: Annotated[
        Path | None,
        typer.Option(
            "--gt",
            help=(
                "Path to the ground-truth YAML file. "
                "Auto-discovers packages/raise-cli/tests/ddd/gt_tactical.yaml by default."
            ),
        ),
    ] = None,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold", help="Micro-average precision threshold (default: 0.80)."
        ),
    ] = 0.80,
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path (default: auto-detect)."),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Write JSON report to this path (optional)."),
    ] = None,
) -> None:
    """Validate tactical type classification accuracy against the GT YAML.

    Loads ``ddd_tactical`` annotations from the graph backend, compares them
    against the ground-truth file, and reports micro-average precision.
    Exits 0 if the gate passes (precision >= threshold), exits 1 if it fails.

    Examples:
        # Run against default GT file (auto-discovered)
        $ rai ddd validate --tactical

        # Explicit GT path
        $ rai ddd validate --gt /path/to/gt_tactical.yaml

        # Custom threshold
        $ rai ddd validate --tactical --threshold 0.85

        # Write JSON report
        $ rai ddd validate --tactical --out work/tactical-accuracy.json
    """
    import json

    from raise_cli.ddd.tactical_validation import validate_tactical_accuracy

    if not tactical:
        console.print("[yellow]No validation mode selected. Use --tactical.[/yellow]")
        raise typer.Exit(0)

    gt_path = gt or _auto_discover_gt(Path.cwd())
    if gt_path is None:
        cli_error(
            "gt_tactical.yaml not found.",
            hint=(
                "Place the GT file at packages/raise-cli/tests/ddd/gt_tactical.yaml "
                "or pass --gt PATH explicitly."
            ),
        )
        raise typer.Exit(1)  # unreachable — cli_error exits

    graph = _load_graph_or_exit(index_path)
    classified = _extract_classified(graph)
    report = validate_tactical_accuracy(classified, gt_path, threshold=threshold)
    _print_accuracy_table(report, threshold)

    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
        console.print(f"[dim]Report written: {out}[/dim]")

    raise typer.Exit(0 if report.gate_passed else 1)


# =============================================================================
# `report` command (RAISE-16918 D4)
# =============================================================================


@ddd_app.command("report")
def report_cmd(
    index_path: Annotated[
        Path | None,
        typer.Option("--index", "-i", help="Graph index path (default: auto-detect)."),
    ] = None,
    bc: Annotated[
        str | None,
        typer.Option("--bc", help="Filter to a single BC name (optional)."),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option(
            "--out",
            "-o",
            help="Write HTML report to this path. Without --out only the terminal table is shown.",
        ),
    ] = None,
) -> None:
    """Render a tactical type breakdown by Bounded Context.

    Loads ``ddd_tactical`` annotations from the graph backend, groups counts
    by BC, and prints a Rich table. Use ``--out PATH`` to also write an HTML
    report with the Copper & Patina palette.

    Examples:
        # Terminal table only
        $ rai ddd report

        # Write HTML
        $ rai ddd report --out work/tactical-report.html

        # Filter to one BC
        $ rai ddd report --bc governance
    """
    from datetime import UTC, datetime

    from raise_cli.ddd.tactical_report import (
        build_tactical_bc_breakdown,
        render_tactical_html_report,
    )

    graph = _load_graph_or_exit(index_path)
    annotations, bc_map = _extract_annotations_and_bc_map(graph)
    breakdown = build_tactical_bc_breakdown(annotations, bc_map)

    if bc:
        breakdown = {k: v for k, v in breakdown.items() if k == bc}
        if not breakdown:
            console.print(f"[yellow]No data for BC '{bc}'.[/yellow]")
            raise typer.Exit(0)

    total = sum(sum(counts.values()) for counts in breakdown.values())
    _print_bc_table(breakdown, total)

    if out is not None:
        generated_at = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        html = render_tactical_html_report(breakdown, total, generated_at)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        console.print(f"[green]HTML report written:[/green] {out}\n")
