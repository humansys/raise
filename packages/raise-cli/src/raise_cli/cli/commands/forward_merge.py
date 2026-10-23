"""CLI commands: rai forward-merge — release-line propagation (RAISE-17076).

Deterministic parts (chain ordering, dual admission, conflict-free-when-
possible hop merge) live in Python and are exposed as three thin
subcommands; orchestration and MR creation are the ``rai-forward-merge``
skill's job, via the forward-merge contract path in ``rai-mr-create``.

``plan`` and ``prepare`` print machine-readable JSON on stdout only when
``-f json`` is requested — errors always go to stderr and stdout carries
nothing on failure, so a caller can safely ``... | jq`` without checking
exit codes for parse-ability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console

from raise_cli.exceptions import AdmissionError, AmbiguousTargetError

if TYPE_CHECKING:
    from raise_cli.project_config.manifest import ReleaseLine

console = Console()
err_console = Console(stderr=True)

forward_merge_app = typer.Typer(
    help="Compute and prepare forward-merge propagation hops across release lines."
)

EXIT_OK = 0
EXIT_AMBIGUOUS = 2
EXIT_CONFLICT = 2
EXIT_ADMISSION_REJECTED = 7


def _release_lines(project: Path) -> list[ReleaseLine]:
    from raise_cli.project_config.manifest import load_manifest

    manifest = load_manifest(project)
    if manifest is None:
        raise AmbiguousTargetError(
            "no .raise/manifest.yaml found — forward-merge requires "
            "branches.release_lines[]",
        )
    if not manifest.branches.release_lines:
        raise AmbiguousTargetError(
            "forward-merge requires branches.release_lines[] — single-line "
            "topology has nothing to propagate",
        )
    return list(manifest.branches.release_lines)


@forward_merge_app.command("plan")
def plan(
    source: Annotated[
        str, typer.Option("--source", help="Release line to propagate from")
    ],
    work_id: Annotated[
        str, typer.Option("--work-id", help="Jira key, used to name hop branches")
    ],
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="human | json")
    ] = "human",
) -> None:
    """Compute the ordered forward-merge chain from ``--source`` (AC-1).

    Sunset lines newer than the source are skipped and reported, never
    silently dropped (D6). Admission (D5, checkpoint 1) is checked per hop
    at plan time — a chain hop always targets an active or bugfix-only
    line, but bugfix admission is verified anyway, defense in depth.
    Exits 2 (E013) when the source is unknown/sunset, any declared release
    line is malformed, or the manifest has no ``release_lines[]``.
    """
    from raise_cli.project_config.branches import check_admission, propagation_chain

    project_path = Path(project).resolve()
    try:
        release_lines = _release_lines(project_path)
        hops, skipped = propagation_chain(release_lines, source)
        for hop in hops:
            check_admission(hop.target, "bugfix", release_lines)
    except (AmbiguousTargetError, AdmissionError) as exc:
        err_console.print(f"ERROR {exc.error_code} {exc}")
        raise typer.Exit(exc.exit_code) from None

    from raise_cli.project_config.branches import propagation_branch

    hop_payloads = [
        {
            "index": hop.index,
            "source": hop.source,
            "target": hop.target,
            "target_status": hop.target_status,
            "branch": propagation_branch(work_id, hop.source, hop.target),
        }
        for hop in hops
    ]
    skipped_payloads = [{"branch": s.branch, "reason": s.reason} for s in skipped]

    if output_format == "json":
        print(
            json.dumps(
                {
                    "source": source,
                    "work_id": work_id,
                    "hops": hop_payloads,
                    "skipped": skipped_payloads,
                }
            )
        )
        return

    if not hops:
        console.print(
            f"Forward-merge chain for {source} ({work_id}): "
            "no newer release line — nothing to propagate."
        )
        return

    console.print(f"Forward-merge chain for {source} ({work_id})")
    for payload in hop_payloads:
        console.print(
            f"  {payload['index']}. {payload['source']} -> {payload['target']}"
            f"   [{payload['target_status']}]      admission: ok"
        )
    if skipped_payloads:
        names = ", ".join(s["branch"] for s in skipped_payloads)
        console.print(f"Skipped: {names}")
    else:
        console.print("Skipped: none")
    last_target = hop_payloads[-1]["target"]
    console.print(
        f"Chain stops at {last_target} (newest release line); main is never a target."
    )


@forward_merge_app.command("prepare")
def prepare(
    source: Annotated[str, typer.Option("--source")],
    target: Annotated[str, typer.Option("--target")],
    work_id: Annotated[str, typer.Option("--work-id")],
    base_ref: Annotated[
        str | None,
        typer.Option(
            "--base-ref",
            help="Base ref for this hop; defaults to origin/{source}. "
            "Pass the previous hop's branch to stack (D3).",
        ),
    ] = None,
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
    output_format: Annotated[
        str, typer.Option("--format", "-f", help="human | json")
    ] = "human",
) -> None:
    """Prepare (or reuse) the local ref for one hop (AC-2/AC-3/AC-7).

    Never checks out or mutates the caller's working tree. Exits 0 on
    ``prepared``/``existing``, 2 on ``conflict`` — writing no ref and
    printing the HITL resolution recipe.
    """
    from raise_cli.exceptions import ConfigurationError
    from raise_cli.scm.adapter import ScmCommandError
    from raise_cli.scm.propagation import prepare_hop

    project_path = Path(project).resolve()
    try:
        result = prepare_hop(
            project_path,
            source=source,
            target=target,
            work_id=work_id,
            base_ref=base_ref,
        )
    except ConfigurationError as exc:
        err_console.print(f"ERROR {exc.error_code} {exc}")
        raise typer.Exit(exc.exit_code) from None
    except ScmCommandError as exc:
        err_console.print(f"ERROR {exc}")
        raise typer.Exit(1) from None

    if output_format == "json":
        print(result.model_dump_json())
        if result.status == "conflict":
            raise typer.Exit(EXIT_CONFLICT)
        return

    if result.status == "conflict":
        console.print(
            f"CONFLICT forward-merge {source} -> {target} — "
            "chain stopped, no ref written."
        )
        console.print("Conflicting files:")
        for path in result.conflicts:
            console.print(f"  {path}")
        console.print(
            "HITL — resolve, then re-run this command "
            "(it resumes from the resolved branch):"
        )
        console.print(
            f"  git worktree add ../fm-{work_id} -b {result.branch} {result.base_ref}"
        )
        console.print(f"  cd ../fm-{work_id} && git merge --no-edit origin/{target}")
        console.print(
            "  # resolve; git add ...; git commit --no-edit   "
            "(rai scm resolve-conflicts may help for declared mechanical files)"
        )
        console.print(
            f"  rai forward-merge prepare --source {source} --target {target} "
            f"--work-id {work_id}"
        )
        raise typer.Exit(EXIT_CONFLICT)

    console.print(f"status:       {result.status}")
    console.print(f"branch:       {result.branch}")
    console.print(f"base_ref:     {result.base_ref}")
    console.print(f"merge_sha:    {result.merge_sha}")
    console.print(f"commits_ahead:{result.commits_ahead}")


@forward_merge_app.command("admit")
def admit(
    target: Annotated[str, typer.Option("--target")],
    project: Annotated[str, typer.Option("--project", "-p")] = ".",
) -> None:
    """Admission checkpoint 2 (D5) — called inside the forward-merge contract.

    Exits 0 for an active or bugfix-only target, 7 (E014) for sunset.
    """
    from raise_cli.project_config.branches import check_admission

    project_path = Path(project).resolve()
    try:
        release_lines = _release_lines(project_path)
    except AmbiguousTargetError:
        # No declared release_lines — nothing to admit against; pass
        # defensively, same as check_admission's own unknown-branch stance.
        console.print(f"admitted: {target} (no release_lines declared)")
        return

    try:
        check_admission(target, "bugfix", release_lines)
    except AdmissionError as exc:
        err_console.print(f"ERROR {exc.error_code} {exc}")
        raise typer.Exit(exc.exit_code) from None

    matching = next((ln for ln in release_lines if ln.branch == target), None)
    status = matching.status if matching is not None else "unknown"
    console.print(f"admitted: {target} ({status})")
