"""CLI surface for Layer 2 architecture doc synthesis (S15884.2).

Provides ``rai docs architecture bundle|validate|status`` and
``rai docs architecture region write|check``. Every command here is a
thin wrapper over ``raise_cli.docs.architecture`` — no LLM call lives in
this module or anywhere under ``packages/raise-cli/`` (AC12); synthesis
itself is one agent turn in the ``rai-docs-update`` skill.

Architecture: ADR-146, S15884.2 design.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.docs.architecture.bundle import ModuleNotFoundInGraphError, build_bundle
from raise_cli.docs.architecture.fingerprint import fingerprint
from raise_cli.docs.architecture.module_id import module_id_for_doc
from raise_cli.docs.architecture.regions import (
    OrphanMarkerError,
    PayloadContainsMarkerError,
    parse_regions,
    region_hash_matches,
    write_region,
)
from raise_cli.docs.architecture.validate import DialectError, validate_mermaid_block
from raise_cli.output.symbols import CHECK, CROSS

architecture_app = typer.Typer(
    name="architecture",
    help="Layer 2 — deterministic scaffolding for generated architecture docs",
    no_args_is_help=True,
)
region_app = typer.Typer(
    name="region",
    help="Read/write rai:auto regions (ADR-146)",
    no_args_is_help=True,
)
architecture_app.add_typer(region_app, name="region")

console = Console()


def _read_stdin() -> str:
    content = sys.stdin.read()
    if not content.strip():
        console.print("[red]Error:[/red] no content received from stdin")
        raise typer.Exit(1)
    return content


@architecture_app.command("bundle")
def bundle_cmd(
    module: Annotated[
        str,
        typer.Option(
            "--module",
            "-m",
            help="Module id, e.g. mod-graph (mod-<package>--<module> in a "
            "packages/* monorepo, RAISE-16033)",
        ),
    ],
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format (only json today)")
    ] = "json",
    index_path: Annotated[
        Path | None, typer.Option("--index", "-i", help="Graph index path")
    ] = None,
) -> None:
    """Assemble the complete synthesis input for a module — one payload.

    This is the entire LLM input: if the caller needs anything not in
    here, that is a bundle.py change, not a second graph query (D-S2).
    """
    del (
        format
    )  # single supported format today; option kept for symmetry with `rai docs`
    try:
        result = build_bundle(module, index_path=index_path)
    except ModuleNotFoundInGraphError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    # Builtin print, never console.print: rich soft-wraps long string
    # values under a narrow COLUMNS (inserting a raw newline mid-string)
    # and its markup-tag regex misparses bracket characters such as
    # `list[str]` inside a real symbol signature as a markup tag and
    # strips them. Either failure corrupts machine-readable JSON output
    # (C1 — the exact bug class build_bundle's in-process graph read was
    # written to avoid, resurfacing at the CLI's own print boundary).
    print(result.model_dump_json(indent=2))


@architecture_app.command("validate")
def validate_cmd(
    stdin: Annotated[
        bool, typer.Option("--stdin", help="Read synthesized markdown from stdin")
    ] = True,
) -> None:
    """Validate the mermaid dialect of synthesized content (AC4).

    Enforces the D-S1 allowlist: only ``flowchart``(+subgraph) passes.
    Rejected content is never written — pair this before every
    ``region write`` call.
    """
    if not stdin:
        console.print("[red]Error:[/red] --stdin is currently the only input mode")
        raise typer.Exit(1)
    content = _read_stdin()
    try:
        dialect = validate_mermaid_block(content)
    except DialectError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]{CHECK}[/green] valid mermaid dialect: {dialect}")


@region_app.command("write")
def region_write_cmd(
    file: Annotated[Path, typer.Option("--file", help="Target markdown doc")],
    region_id: Annotated[
        str, typer.Option("--id", help="Region id, e.g. c4-component")
    ],
    src: Annotated[
        str, typer.Option("--src", help="Input bundle fingerprint (sha256:...)")
    ],
    stdin: Annotated[
        bool, typer.Option("--stdin", help="Read the synthesized payload from stdin")
    ] = True,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Compute the would-be diff without writing anything to disk",
        ),
    ] = False,
) -> None:
    """Write synthesized content into a delimited ``rai:auto`` region.

    Idempotent by construction (AC1): an unchanged payload against an
    unchanged ``src`` is a zero-cost no-op — the file is never opened
    for write. Malformed markers abort with nothing written (AC3).

    ``--dry-run`` stages the diff for human review (C3): it runs the
    identical hash/fingerprint comparison and prints the would-be
    action and content, but never calls ``path.write_text``. Callers
    (e.g. the ``rai-docs-update`` skill's Step 3.5) must present this
    preview at the HITL gate and only re-invoke this command without
    ``--dry-run`` after a human approves it — that second, non-dry-run
    call is the only point that commits to disk.
    """
    if not stdin:
        console.print("[red]Error:[/red] --stdin is currently the only input mode")
        raise typer.Exit(1)
    payload = _read_stdin()

    try:
        result = write_region(
            file, region_id=region_id, payload=payload, src=src, dry_run=dry_run
        )
    except OrphanMarkerError as exc:
        console.print(f"[red]Error:[/red] orphan marker in {file}\n  {exc}")
        console.print(
            "  No write performed. Restore the end marker or delete the begin marker."
        )
        raise typer.Exit(1) from exc
    except PayloadContainsMarkerError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    # Builtin print, not console.print: `result.message` carries a
    # `[dry-run]` prefix on the dry-run path, and `result.preview` is the
    # literal would-be region content, which can contain `[...]`
    # node-label syntax. rich's markup-tag regex silently strips both —
    # the same class of bug fixed at the JSON boundary in C1, here
    # hiding exactly the text a human is meant to review/approve.
    print(result.message)
    if dry_run and result.preview:
        print(result.preview)


@region_app.command("check")
def region_check_cmd(
    file: Annotated[Path, typer.Option("--file", help="Markdown doc to inspect")],
) -> None:
    """Read-only diagnostic over a doc's ``rai:auto`` regions.

    Reports orphan markers (noisy failure) and hand-tampering (content
    hash mismatch) without writing anything.
    """
    if not file.exists():
        console.print(f"[red]Error:[/red] file not found: {file}")
        raise typer.Exit(1)

    text = file.read_text(encoding="utf-8")
    try:
        regions = parse_regions(text)
    except OrphanMarkerError as exc:
        console.print(f"[red]Error:[/red] orphan marker in {file}")
        console.print(f"  {exc}")
        console.print(
            "  No write performed. Restore the end marker or delete the begin marker."
        )
        raise typer.Exit(1) from exc

    if not regions:
        console.print(f"[green]{CHECK}[/green] no rai:auto regions in {file}")
        return

    exit_code = 0
    for region in regions:
        if region_hash_matches(region):
            console.print(
                f"[green]{CHECK}[/green] {file}#{region.id} — content hash ok"
            )
        else:
            exit_code = 1
            console.print(
                f"[yellow]![/yellow] {file}#{region.id} — content hash mismatch"
            )
            console.print(
                "  Region was edited by hand; the next regeneration will overwrite it."
            )
            console.print("  Move the edit outside the rai:auto markers to keep it.")

    if exit_code:
        raise typer.Exit(exit_code)


@architecture_app.command("status")
def status_cmd(
    modules_dir: Annotated[
        Path,
        typer.Option(
            "--modules-dir", help="Directory of module docs carrying rai:auto regions"
        ),
    ] = Path("governance/architecture/modules"),
    index_path: Annotated[
        Path | None, typer.Option("--index", "-i", help="Graph index path")
    ] = None,
) -> None:
    """Report per-doc fresh/stale verdicts (the human-facing form of the gate).

    Skips silently when ``modules_dir`` doesn't exist yet — pre-first-run
    repos must not see an error here.
    """
    if not modules_dir.exists():
        console.print(f"[green]{CHECK}[/green] no {modules_dir} — nothing to check")
        return

    any_region = False
    stale_count = 0
    for doc_path in sorted(modules_dir.glob("*.md")):
        text = doc_path.read_text(encoding="utf-8")
        try:
            regions = parse_regions(text)
        except OrphanMarkerError as exc:
            console.print(f"[red]{CROSS}[/red] {doc_path} — orphan marker: {exc}")
            stale_count += 1
            continue

        # RAISE-16033 C1: read the doc's own package: frontmatter (same
        # rule discovery and the curated sidecar loader use) instead of
        # the bare filename stem — a package-qualified module's real
        # graph id no longer matches `mod-{stem}`.
        module_id = module_id_for_doc(doc_path)
        for region in regions:
            any_region = True
            try:
                bundle = build_bundle(module_id, index_path=index_path)
            except ModuleNotFoundInGraphError:
                console.print(
                    f"[yellow]?[/yellow] {doc_path}#{region.id} — module {module_id} not in graph"
                )
                continue
            computed_src = fingerprint(bundle)
            if computed_src == region.src:
                console.print(f"[green]{CHECK}[/green] {doc_path}#{region.id} — fresh")
            else:
                stale_count += 1
                console.print(f"[red]{CROSS}[/red] {doc_path}#{region.id} — stale")
                console.print(f"    src {region.src} -> {computed_src} (graph changed)")

    if not any_region:
        console.print(
            f"[green]{CHECK}[/green] no rai:auto regions found under {modules_dir}"
        )
        return

    if stale_count:
        console.print("\nRegenerate with: /rai-docs-update")
        raise typer.Exit(1)
