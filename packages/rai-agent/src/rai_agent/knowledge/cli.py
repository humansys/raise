"""CLI app for knowledge domain management — registered as `rai knowledge`."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003 — used at runtime by typer
from typing import TYPE_CHECKING, Annotated

import typer

from rai_agent.knowledge.domain import (
    DomainConfigError,
    discover_domains,
    load_domain,
    resolve_adapter,
    resolve_builder,
    scaffold_domain,
)
from rai_agent.knowledge.formatter import (
    format_check_summary,
    format_gate_result,
    format_query_compact,
    format_query_human,
    format_query_json,
    format_status,
)
from rai_agent.knowledge.gates import (
    run_coverage,
    run_graph,
    run_reconcile,
    run_validate,
)

if TYPE_CHECKING:
    from rai_agent.knowledge.models import DomainManifest, GateResult

app = typer.Typer(
    name="knowledge",
    help="Knowledge domain management and validation gates.",
    no_args_is_help=True,
)

# Where domains live
_DEFAULT_KNOWLEDGE_DIR = Path(".raise/knowledge")

_GATE_RUNNERS = {
    "validate": run_validate,
    "reconcile": run_reconcile,
    "coverage": run_coverage,
    "graph": run_graph,
}

_GATE_NAMES = list(_GATE_RUNNERS.keys())


def _resolve_domain_dir(domain: str) -> Path:
    """Resolve the domain directory path."""
    return _DEFAULT_KNOWLEDGE_DIR / domain


@app.command()
def check(
    domain: Annotated[
        str,
        typer.Argument(help="Domain name (e.g., 'scaleup')"),
    ],
    gate: Annotated[
        str | None,
        typer.Option(
            "--gate",
            "-g",
            help=f"Run specific gate: {', '.join(_GATE_NAMES)}",
        ),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
) -> None:
    """Run validation gates for a knowledge domain."""
    domain_dir = _resolve_domain_dir(domain)
    try:
        manifest, config = load_domain(domain_dir)
    except DomainConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    # Select gates to run
    if gate:
        if gate not in _GATE_RUNNERS:
            typer.echo(
                f"Unknown gate '{gate}'. Available: {', '.join(_GATE_NAMES)}",
                err=True,
            )
            raise typer.Exit(1)
        runners = {gate: _GATE_RUNNERS[gate]}
    else:
        runners = _GATE_RUNNERS

    # Run gates
    results: list[GateResult] = []
    for _gate_name, runner in runners.items():
        result = runner(config, domain=manifest.name)
        results.append(result)

    # Output
    if output_json:
        data = [r.model_dump() for r in results]
        typer.echo(json.dumps(data, indent=2))
    elif len(results) == 1:
        typer.echo(format_gate_result(results[0]))
    else:
        typer.echo(format_check_summary(results, manifest.name))

    # Exit code
    all_passed = all(r.passed for r in results)
    if not all_passed:
        raise typer.Exit(1)


@app.command()
def status(
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
) -> None:
    """Show status of all registered knowledge domains."""
    domains_info = discover_domains(_DEFAULT_KNOWLEDGE_DIR)

    if output_json:
        data: list[dict[str, object]] = []
        for manifest, config in domains_info:
            base = config.domain_dir or config.node_dir.parent
            extracted = _count_yaml(base / "extracted")
            curated = _count_yaml(base / "curated")
            data.append(
                {
                    "name": manifest.name,
                    "display_name": manifest.display_name,
                    "extracted": extracted,
                    "curated": curated,
                }
            )
        typer.echo(json.dumps(data, indent=2))
    else:
        display_data: list[tuple[DomainManifest, int, int]] = []
        for manifest, config in domains_info:
            base = config.domain_dir or config.node_dir.parent
            extracted = _count_yaml(base / "extracted")
            curated = _count_yaml(base / "curated")
            display_data.append((manifest, extracted, curated))
        typer.echo(format_status(display_data))


@app.command("init")
def init_domain(
    domain: Annotated[
        str,
        typer.Argument(help="Domain name (e.g., 'gtd')"),
    ],
    corpus: Annotated[
        list[str] | None,
        typer.Option(
            "--corpus",
            "-c",
            help="Corpus file paths",
        ),
    ] = None,
) -> None:
    """Initialize a new knowledge domain (scaffold)."""
    try:
        domain_dir = scaffold_domain(
            base_dir=_DEFAULT_KNOWLEDGE_DIR,
            domain_name=domain,
            corpus_paths=corpus,
        )
    except DomainConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Created {domain_dir}/")
    typer.echo("  domain.yaml        # template")
    typer.echo("  extracted/          # empty")
    typer.echo("  curated/            # empty")
    typer.echo("")
    typer.echo(
        "Next: edit domain.yaml (set schema module + class), add competency questions."
    )


@app.command()
def query(
    query_or_domain: Annotated[
        str,
        typer.Argument(help="Domain name or query (auto-detect if 1 domain)"),
    ],
    query_str: Annotated[
        str | None,
        typer.Argument(help="Query string (omit if domain auto-detected)"),
    ] = None,
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human, compact, json"),
    ] = "human",
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum results"),
    ] = 10,
) -> None:
    """Query a knowledge domain for relevant concepts.

    Examples:
        $ rai knowledge query scaleup "cash flow tools"
        $ rai knowledge query "leadership team"  # auto-detect
        $ rai knowledge query scaleup "people" --format json
    """
    from rai_agent.knowledge.retrieval.engine import retrieve

    # Resolve domain and query
    domain_name, actual_query = _resolve_query_args(query_or_domain, query_str)

    # Load domain
    domain_dir = _resolve_domain_dir(domain_name)
    try:
        manifest, config = load_domain(domain_dir)
    except DomainConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    # Resolve adapter and builder dynamically
    try:
        adapter = resolve_adapter(manifest)
        builder = resolve_builder(manifest)
    except DomainConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    # Build graph from nodes
    graph = builder.build_from_directory(config.node_dir)

    # Retrieve
    result = retrieve(
        graph=graph,
        query=actual_query,
        adapter=adapter,
        top_k=limit,
    )

    # Format output
    prompting = manifest.prompting
    if fmt == "json":
        typer.echo(format_query_json(result, prompting))
    elif fmt == "compact":
        typer.echo(format_query_compact(result, manifest.name, prompting))
    else:
        typer.echo(format_query_human(result, manifest.display_name, prompting))


def _resolve_query_args(
    query_or_domain: str,
    query_str: str | None,
) -> tuple[str, str]:
    """Resolve domain name and query string from CLI args.

    If query_str is provided, query_or_domain is the domain name.
    If query_str is None, auto-detect domain (must be exactly 1).
    """
    if query_str is not None:
        return query_or_domain, query_str

    # Auto-detect: query_or_domain is the query, find the single domain
    domains = discover_domains(_DEFAULT_KNOWLEDGE_DIR)
    if len(domains) == 1:
        return domains[0][0].name, query_or_domain
    if len(domains) == 0:
        typer.echo("Error: No knowledge domains found.", err=True)
        raise typer.Exit(1)
    names = ", ".join(m.name for m, _ in domains)
    typer.echo(
        f"Error: Multiple domains found ({names}). Specify domain explicitly.",
        err=True,
    )
    raise typer.Exit(1)


def _count_yaml(directory: Path) -> int:
    """Count YAML files in a directory."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.yaml")))
