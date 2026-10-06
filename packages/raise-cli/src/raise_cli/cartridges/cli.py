"""CLI app for cartridge management — registered as `rai cartridge`."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

import typer
import yaml

from raise_cli.cartridges.formatter import (
    format_check_result,
    format_check_summary,
    format_gate_result,
    format_query_compact,
    format_query_human,
    format_query_json,
    format_status,
)
from raise_cli.cartridges.secret_scan import scan_for_secrets
from raise_cli.config.server import get_server_credentials
from raise_core.cartridges.audit import AuditReport, audit_cartridge
from raise_core.cartridges.extract import (
    CartridgeExtractor,
    MarkdownExtractor,
    YAMLExtractor,
    cartridge_project_root,
    extract_cartridge,
    read_cartridge_name,
)
from raise_core.cartridges.federated import federated_query
from raise_core.cartridges.hygiene import HygieneResult, apply_hygiene
from raise_core.cartridges.install import (
    CartridgeInstallError,
    install_cartridge,
    uninstall_cartridge,
)
from raise_core.cartridges.instances import iter_instance_files
from raise_core.cartridges.loader import (
    CartridgeConfigError,
    discover_cartridges,
    load_cartridge,
    resolve_adapter,
    resolve_builder,
    scaffold_cartridge,
)
from raise_core.cartridges.pack import pack_cartridge
from raise_core.cartridges.validate import validate_cartridge
from raise_core.graph.gates.runner import (
    run_coverage,
    run_graph,
    run_reconcile,
    run_validate,
)

if TYPE_CHECKING:
    from typing import Protocol

    from raise_cli.cartridges.server_client import CartridgeServerClient
    from raise_cli.cartridges.server_models import CartridgeEdgePayload
    from raise_cli.gates.models import GateResult as CliGateResult
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
    from raise_core.cartridges.models import CartridgeManifest, GateResult
    from raise_core.graph.engine import Graph
    from raise_core.graph.gates.models import GateConfig
    from raise_core.graph.retrieval.engine import SemanticScorer

    class GateRunner(Protocol):  # noqa: D101
        def __call__(self, config: GateConfig, domain: str = ...) -> GateResult: ...  # noqa: D102


logger = logging.getLogger(__name__)

app = typer.Typer(
    name="cartridge",
    help="Cartridge management and validation gates.",
    no_args_is_help=True,
)

DEFAULT_CARTRIDGES_DIR = Path(".raise/cartridges")

# Keys injected by ingest_cartridge() — promoted to dedicated fields (scope)
# or internal bookkeeping (cartridge). Filtered out of PublishRequest.properties.
_INTERNAL_METADATA_KEYS = frozenset({"cartridge", "scope"})

_GATE_RUNNERS = {
    "validate": run_validate,
    "reconcile": run_reconcile,
    "coverage": run_coverage,
    "graph": run_graph,
}

_GATE_NAMES = list(_GATE_RUNNERS.keys())


def resolve_semantic_scorer(
    embeddings_dirs: list[Path] | None = None,
    server_url: str | None = None,
    api_key: str | None = None,
    sem_alpha: float | None = None,
    tfidf_corpus: list[dict[str, Any]] | None = None,
) -> SemanticScorer | None:
    """Resolve semantic scorer lazily so CLI import does not require numpy."""
    from raise_core.graph.scorers import resolve_semantic_scorer as _resolve

    return _resolve(
        embeddings_dirs=embeddings_dirs,
        server_url=server_url,
        api_key=api_key,
        sem_alpha=sem_alpha,
        tfidf_corpus=tfidf_corpus,
    )


def _load_tfidf_corpus(instances_dir: Path) -> list[dict[str, Any]]:
    """Load raw node dicts from instances/*.json for TF-IDF indexing.

    Graceful degradation: directorio inexistente → lista vacía;
    JSON corrupto → skip + warning.
    """
    corpus: list[dict[str, Any]] = []
    if not instances_dir.is_dir():
        return corpus
    for json_file in iter_instance_files(instances_dir):
        try:
            nodes = json.loads(json_file.read_text(encoding="utf-8"))
            if isinstance(nodes, list):
                corpus.extend(nodes)
        except (json.JSONDecodeError, OSError):
            logger.warning("Skipping corrupt instances file: %s", json_file)
    return corpus


def _resolve_federated_hybrid_params(
    cartridges: list[tuple[Any, Any]],
) -> tuple[float | None, list[dict[str, Any]] | None]:
    """Compute α máximo y corpus unificado para el path federado.

    Returns (alpha_max, tfidf_corpus).  alpha_max=None cuando ningún cartridge
    declara sem_alpha; tfidf_corpus=None cuando alpha≤0 o corpus vacío.
    """
    alphas: list[float] = []
    for _manifest, _ in cartridges:
        if _manifest.retrieval:
            _alpha = _manifest.retrieval.resolve_alpha()
            if _alpha:
                alphas.append(_alpha)
    alpha_max = max(alphas) if alphas else None

    tfidf_corpus: list[dict[str, Any]] | None = None
    if alpha_max and alpha_max > 0:
        corpus_parts: list[dict[str, Any]] = []
        for _manifest, _config in cartridges:
            base = _config.domain_dir or _config.node_dir.parent
            corpus_parts.extend(_load_tfidf_corpus(base / "instances"))
        tfidf_corpus = corpus_parts or None

    return alpha_max, tfidf_corpus


def _resolve_cartridge_dir(cartridge: str) -> Path:
    """Resolve the cartridge directory path."""
    return DEFAULT_CARTRIDGES_DIR / cartridge


def _corpus_base_dir(cartridge_dir: Path) -> Path:
    """Resolve the base dir corpus manifest entries are relative to.

    ``scaffold_cartridge()`` stores ``-c/--corpus`` paths verbatim as typed by
    the developer at the **project root** (e.g. ``governance/*.md``), but
    ``cartridge_dir`` is nested three levels below it
    (``.raise/cartridges/<name>/``). Climb back out to the project root so
    corpus consumers (``build``, ``_read_corpus``) match what scaffold wrote
    (RAISE-11617).

    Delegates to `raise_core.cartridges.extract.cartridge_project_root` — the
    single canonical definition of this climb, shared with `resolve_sources`'
    project-root fallback (RAISE-11835), so the two packages can't drift
    apart on "how far does cartridge_dir climb to reach project root."
    """
    return cartridge_project_root(cartridge_dir)


def _build_edge_payloads(graph: Graph) -> list[CartridgeEdgePayload]:
    """Map materialized graph edges to publish payload edges (RAISE-8343)."""
    from raise_cli.cartridges.server_models import CartridgeEdgePayload

    return [
        CartridgeEdgePayload(
            source_node_id=edge.source,
            target_node_id=edge.target,
            edge_type=edge.type,
            weight=edge.weight,
        )
        for edge in graph.iter_relationships()
    ]


def _select_runners(gate: str | None) -> dict[str, GateRunner]:
    """Select gate runners — all or a specific one."""
    if gate is None:
        return _GATE_RUNNERS
    if gate not in _GATE_RUNNERS:
        typer.echo(
            f"Unknown gate '{gate}'. Available: {', '.join(_GATE_NAMES)}",
            err=True,
        )
        raise typer.Exit(1)
    return {gate: _GATE_RUNNERS[gate]}


def _run_integrity_check(cartridge_dir: Path) -> None:
    """Run manifest + structure validation; exit on failure."""
    check = validate_cartridge(cartridge_dir)
    if not check.valid:
        for err in check.errors:
            typer.echo(f"ERROR: {err}", err=True)
        raise typer.Exit(1)
    for warn in check.warnings:
        typer.echo(f"WARN: {warn}", err=True)


@app.command("check")
def check(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
    ],
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
) -> None:
    """Lightweight validation: manifest + structure + dependencies (no gates)."""
    cartridge_dir = _resolve_cartridge_dir(cartridge)
    result = validate_cartridge(cartridge_dir)

    if output_json:
        typer.echo(result.model_dump_json(indent=2))
    else:
        typer.echo(format_check_result(result, cartridge))

    if not result.valid:
        raise typer.Exit(1)


@app.command("validate")
def validate(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
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
    """Run validation gates for a cartridge."""
    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    try:
        manifest, config = load_cartridge(cartridge_dir)
    except CartridgeConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    runners = _select_runners(gate)
    results: list[GateResult] = []
    for runner in runners.values():
        result = runner(config, manifest.name)
        results.append(result)

    if output_json:
        data = [r.model_dump() for r in results]
        typer.echo(json.dumps(data, indent=2))
    elif len(results) == 1:
        typer.echo(format_gate_result(results[0]))
    else:
        typer.echo(format_check_summary(results, manifest.name))

    if not all(r.passed for r in results):
        raise typer.Exit(1)


@app.command("list")
def list_cartridges(
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: table, json"),
    ] = "table",
) -> None:
    """Show status of all registered cartridges (local + server-installed)."""
    cartridges_info = discover_cartridges(DEFAULT_CARTRIDGES_DIR)

    if fmt == "json":
        data: list[dict[str, object]] = []
        for manifest, config in cartridges_info:
            base = config.domain_dir or config.node_dir.parent
            instances = _count_instance_nodes(base / "instances")
            data.append(
                {
                    "name": manifest.name,
                    "display_name": manifest.display_name,
                    "instances": instances,
                    "source": "local",
                }
            )
        for (
            name,
            source,
            status,
            node_count,
            _installed_at,
            policy,
        ) in _get_installations():
            data.append(
                {
                    "name": name,
                    "source": source,
                    "status": status,
                    "nodes": node_count,
                    "policy": policy,
                }
            )
        typer.echo(json.dumps(data, indent=2))
    else:
        display_data: list[tuple[CartridgeManifest, int, int]] = []
        for manifest, config in cartridges_info:
            base = config.domain_dir or config.node_dir.parent
            instances = _count_instance_nodes(base / "instances")
            display_data.append((manifest, instances, 0))
        typer.echo(format_status(display_data))
        server_installs = _get_installations()
        if server_installs:
            lines = ["\nServer-installed:"]
            for (
                name,
                source,
                status,
                node_count,
                _installed_at,
                policy,
            ) in server_installs:
                count_text = (
                    f"{node_count} live nodes"
                    if node_count is not None
                    else "live nodes unknown"
                )
                lines.append(
                    f"  {name:<25} {source:<8} {status:<10} {policy:<9} {count_text}"
                )
            typer.echo("\n".join(lines))


def _get_installations() -> list[tuple[str, str, str, int | None, str, str]]:
    """List installed cartridges with active-project node counts.

    The server remains authoritative for org-installed names (RAISE-9781).
    Counts always come from the active project's local graph. The server's
    registry count and the local installation record are historical metadata,
    not evidence that those nodes are currently available to this project.
    """
    server = _server_installations()
    if server is not None:
        counts = _local_live_node_counts([row[0] for row in server])
        return [
            (
                name,
                source,
                status,
                counts.get(name, 0) if counts is not None else None,
                installed_at,
                policy,
            )
            for name, source, status, _stored_count, installed_at, policy in server
        ]
    return _local_installations()


def _server_installations() -> list[tuple[str, str, str, int, str, str]] | None:
    """Org-installed cartridges from the server API, or None when unavailable."""
    try:
        from raise_cli.cartridges.server_client import CartridgeServerClient
        from raise_cli.config.server import get_server_credentials

        creds = get_server_credentials()
        if creds is None:
            return None
        server_url, api_key = creds
        client = CartridgeServerClient(server_url, api_key)
        try:
            installed = client.list_installed()
        finally:
            client.close()
        return [
            (info.cartridge_name, "server", "installed", info.node_count, "", "")
            for info in installed
        ]
    except Exception:  # noqa: BLE001 — fall back to local on any server error
        return None


def _local_live_node_counts(cartridge_names: list[str]) -> dict[str, int] | None:
    """Return active-project counts, or None when live evidence is unavailable."""
    try:
        from raise_cli.config.paths import resolve_checkout_root
        from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
        from raise_cli.storage.connection import get_project_db_path, get_project_id

        repo_root = resolve_checkout_root()
        backend = SQLiteGraphBackend(
            get_project_id(repo_root),
            get_project_db_path(repo_root),
            checkout_id=str(repo_root),
        )
        return backend.cartridge_node_counts(cartridge_names)
    except Exception:  # noqa: BLE001
        return None


def _local_installations() -> list[tuple[str, str, str, int | None, str, str]]:
    """Fallback installations with counts reconciled to the active graph."""
    try:
        from raise_cli.config.paths import resolve_checkout_root
        from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
        from raise_cli.storage.connection import get_project_db_path, get_project_id

        repo_root = resolve_checkout_root()
        backend = SQLiteGraphBackend(
            get_project_id(repo_root),
            get_project_db_path(repo_root),
            checkout_id=str(repo_root),
        )
        rows = backend.list_cartridge_installations()
    except Exception:  # noqa: BLE001
        return []

    try:
        counts = backend.cartridge_node_counts([row[0] for row in rows])
    except Exception:  # noqa: BLE001
        counts = None

    return [
        (
            name,
            source,
            status,
            counts.get(name, 0) if counts is not None else None,
            installed_at,
            policy,
        )
        for name, source, status, _stored_count, installed_at, policy in rows
    ]


@app.command("init")
def init_cartridge(
    name: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'soc2-controls')"),
    ],
    corpus: Annotated[
        list[str] | None,
        typer.Option(
            "--corpus",
            "-c",
            help="Corpus file paths",
        ),
    ] = None,
    from_curation: Annotated[
        Path | None,
        typer.Option(
            "--from-curation",
            help="Build the cartridge from a curated corpus-curation.yaml "
            "(corpus paths + GraphNode schema). Closes the upgrade-pipeline "
            "curate→cartridge gap.",
        ),
    ] = None,
) -> None:
    """Initialize a new cartridge (scaffold)."""
    node_schema: tuple[str, str] | None = None
    if from_curation is not None:
        try:
            curation = yaml.safe_load(from_curation.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            typer.echo(f"Error reading curation file: {exc}", err=True)
            raise typer.Exit(1) from exc
        curated = (curation or {}).get("curated", [])
        curated_paths = [c["path"] for c in curated if c.get("path")]
        if not curated_paths:
            typer.echo("Error: curation file has no curated docs.", err=True)
            raise typer.Exit(1)
        # Merge any explicit -c paths after the curated ones.
        corpus = curated_paths + list(corpus or [])
        # Governance cartridges use the canonical graph node (closes KI #2).
        node_schema = ("raise_core.graph.models", "GraphNode")

    try:
        cartridge_dir = scaffold_cartridge(
            base_dir=DEFAULT_CARTRIDGES_DIR,
            cartridge_name=name,
            corpus_paths=corpus,
            node_schema=node_schema,
        )
    except CartridgeConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Created {cartridge_dir}/")
    typer.echo("  CARTRIDGE.yaml     # manifest")
    typer.echo("  schema/            # entity & relation types")
    typer.echo("  extractors/        # LLM prompts & validators")
    typer.echo("  instances/         # seed data")
    typer.echo("  skills/            # procedural skills")
    typer.echo("")
    typer.echo(
        "Next: edit CARTRIDGE.yaml (set schema module + class, author, license)."
    )


def _get_llm_client() -> Any:
    """Create an OpenAI-compatible LLM client via OpenRouter."""
    import os

    from openai import OpenAI

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


@app.command("build")
def build(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaling-up')"),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing extractors/config.yaml"),
    ] = False,
) -> None:
    """Analyze corpus and generate seed schema (config.yaml + relationships.yaml)."""
    cartridge_dir = _resolve_cartridge_dir(cartridge)
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    if not manifest_path.exists():
        typer.echo(f"Error: CARTRIDGE.yaml not found in {cartridge_dir}", err=True)
        raise typer.Exit(1)

    raw_manifest: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw_manifest, dict):
        typer.echo("Error: Invalid CARTRIDGE.yaml", err=True)
        raise typer.Exit(1)

    corpus_patterns: list[str] = raw_manifest.get("corpus", [])
    if not corpus_patterns:
        typer.echo(
            "Error: No corpus paths defined in CARTRIDGE.yaml. "
            "Add a 'corpus' list (e.g., corpus: [\"corpus/*.md\"]).",
            err=True,
        )
        raise typer.Exit(1)

    config_path = cartridge_dir / "extractors" / "config.yaml"
    if config_path.exists() and not force:
        typer.echo(
            f"Error: {config_path} already exists. Use --force to overwrite.",
            err=True,
        )
        raise typer.Exit(1)

    corpus_base_dir = _corpus_base_dir(cartridge_dir)
    corpus_paths: list[Path] = []
    for pattern in corpus_patterns:
        corpus_paths.extend(sorted(corpus_base_dir.glob(pattern)))
    if not corpus_paths:
        typer.echo(
            f"Error: No files matched corpus patterns {corpus_patterns} "
            f"in {corpus_base_dir}",
            err=True,
        )
        raise typer.Exit(1)

    from raise_core.cartridges.corpus_analyzer import analyze_corpus
    from raise_core.cartridges.seed_schema import (
        generate_extractor_config,
        generate_manifest_updates,
        generate_relationship_schema,
    )

    llm_client = _get_llm_client()
    typer.echo(
        f"Analyzing corpus ({len(corpus_paths)} files, "
        f"{sum(p.stat().st_size for p in corpus_paths) / 1024:.1f} KB)..."
    )

    analysis = analyze_corpus(corpus_paths, llm_client)

    if not analysis.proposed_node_types:
        typer.echo(
            "Error: Analysis returned no node types — corpus may be too small "
            "or not contain structured knowledge.",
            err=True,
        )
        raise typer.Exit(1)

    corpus_glob = corpus_patterns[0] if corpus_patterns else "corpus/*.md"
    config = generate_extractor_config(analysis, corpus_glob=corpus_glob)
    schema = generate_relationship_schema(analysis)
    manifest_updates = generate_manifest_updates(analysis)

    extractors_dir = cartridge_dir / "extractors"
    extractors_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir = extractors_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    config_path.write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    schema_path = schemas_dir / "relationships.yaml"
    schema_path.write_text(
        yaml.dump(schema, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    if manifest_updates.get("domain_context"):
        raw_manifest["domain_context"] = manifest_updates["domain_context"]
    # competency_questions in the manifest is a PATH to a CQ file (loader.py
    # resolves it as cartridge_dir / value). Write the questions to that file
    # and store only the filename — storing the inline text made query crash
    # with 'File name too long' (SP-project-upgrade gemba, la-aldea-erp).
    if manifest_updates.get("competency_questions"):
        cq_filename = "competency_questions.md"
        cq_text = manifest_updates["competency_questions"]
        (cartridge_dir / cq_filename).write_text(
            f"# Competency Questions\n\n{cq_text}\n", encoding="utf-8"
        )
        raw_manifest["competency_questions"] = cq_filename
    manifest_path.write_text(
        yaml.dump(raw_manifest, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    n_specs = len(config["extractors"])
    n_rels = len(schema["relationship_types"])
    typer.echo(f"Generated {config_path} ({n_specs} specs)")
    typer.echo(f"Generated {schema_path} ({n_rels} types)")
    typer.echo(f"Updated {manifest_path}")
    typer.echo(f"Next: rai cartridge extract {cartridge}")


def _load_instance_nodes(instances_dir: Path) -> list[Any]:
    """Load GraphNode instances from all JSON files in a directory."""
    from raise_core.graph.models import GraphNode

    nodes: list[GraphNode] = []
    for json_path in sorted(instances_dir.glob("*.json")):
        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
            items = raw if isinstance(raw, list) else [raw]
            for item in items:
                if isinstance(item, dict) and "id" in item:
                    nodes.append(GraphNode.model_validate(item))
        except (json.JSONDecodeError, OSError):
            pass
    return nodes


def _apply_review_feedback(
    cartridge_dir: Path,
    cartridge: str,
    drop_type: list[str] | None,
    add_type: list[str] | None,
) -> None:
    """Apply drop/add feedback to extractors/config.yaml."""
    from raise_core.cartridges.review import apply_feedback

    config_path = cartridge_dir / "extractors" / "config.yaml"
    if not config_path.exists():
        typer.echo(
            f"Error: {config_path} not found — cannot apply feedback.",
            err=True,
        )
        raise typer.Exit(1)

    config: dict[str, list[dict[str, object]]] = yaml.safe_load(
        config_path.read_text(encoding="utf-8")
    ) or {"extractors": []}

    updated = apply_feedback(
        config,
        drop_types=drop_type or [],
        add_types=add_type or [],
    )

    config_path.write_text(
        yaml.dump(updated, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    changes: list[str] = []
    if drop_type:
        changes.append(f"dropped: {', '.join(drop_type)}")
    if add_type:
        changes.append(f"added: {', '.join(add_type)}")
    typer.echo(f"\nUpdated {config_path} ({'; '.join(changes)})")
    typer.echo(f"Next: rai cartridge extract {cartridge}")


@app.command("review")
def review(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaling-up')"),
    ],
    drop_type: Annotated[
        list[str] | None,
        typer.Option("--drop-type", help="Remove extractor spec for this node type"),
    ] = None,
    add_type: Annotated[
        list[str] | None,
        typer.Option("--add-type", help="Add a new extractor spec for this node type"),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output summary as JSON"),
    ] = False,
) -> None:
    """Review extraction results and apply feedback to refine the schema."""
    from raise_core.cartridges.review import summarize_extraction

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    instances_dir = cartridge_dir / "instances"
    if not instances_dir.is_dir():
        typer.echo(
            f"Error: No instances/ directory in {cartridge_dir}. "
            "Run 'rai cartridge extract' first.",
            err=True,
        )
        raise typer.Exit(1)

    nodes = _load_instance_nodes(instances_dir)
    if not nodes:
        typer.echo("Error: No nodes found in instances/.", err=True)
        raise typer.Exit(1)

    summary = summarize_extraction(nodes)

    if output_json:
        typer.echo(summary.model_dump_json(indent=2))
    else:
        typer.echo(
            f"Extraction review for '{cartridge}' ({summary.total_nodes} nodes):"
        )
        typer.echo("")
        typer.echo("  By type:")
        for type_name, count in sorted(summary.by_type.items()):
            typer.echo(f"    {type_name:<20} {count} nodes")
        typer.echo("")
        typer.echo("  By source:")
        for source, count in sorted(summary.by_source.items()):
            typer.echo(f"    {source:<30} {count} nodes")

    has_feedback = bool(drop_type) or bool(add_type)
    if has_feedback:
        _apply_review_feedback(cartridge_dir, cartridge, drop_type, add_type)


@app.command("pack")
def pack(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output directory for the archive",
        ),
    ] = Path("."),
) -> None:
    """Pack a cartridge into a .cartridge.tar.gz archive with SHA-256 checksum."""
    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    archive = pack_cartridge(cartridge_dir, output)
    checksum_path = archive.parent / f"{archive.name}.sha256"
    typer.echo(f"Packed: {archive}")
    typer.echo(f"Checksum: {checksum_path}")


def _publish_post_message(
    result_visibility: str | None,
    result_org_plan: str | None,
    requested_private: bool,
    yes: bool,
) -> None:
    """Print tier-appropriate post-publish message (CTA for Community, note for Pro)."""
    import os

    upgrade_url = os.environ.get("RAISE_UPGRADE_URL", "https://raiseframework.ai/pro")

    is_community = result_org_plan not in (None, "pro", "team", "enterprise")
    forced_public = requested_private and result_visibility == "public"

    if forced_public:
        price = os.environ.get("RAISE_PRO_PRICE")
        upgrade_line = (
            f"Pro plan: ${price} · Upgrade → {upgrade_url}"
            if price
            else f"Upgrade → {upgrade_url}"
        )
        typer.echo(f"\nNote: Keep cartridges private with RaiSE Pro.\n{upgrade_line}")
        return

    # Pro + --yes: silent success — no post-publish message
    if not is_community and yes:
        return

    typer.echo(
        "\nPublished as "
        + (result_visibility or "public")
        + ". This cartridge may be cached once published;\n"
        "unpublish removes from marketplace but cannot recall copies."
    )
    if is_community:
        typer.echo(f"Go Pro to keep cartridges private → {upgrade_url}")


@app.command("publish")
def publish(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'soc2-controls')"),
    ],
    visibility: Annotated[
        str,
        typer.Option(help="Visibility: 'public' (community) or 'private' (org-only)"),
    ] = "public",
    private: Annotated[
        bool,
        typer.Option("--private", help="Publish as private (Pro plan required)"),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt (for CI use)"),
    ] = False,
) -> None:
    """Publish a local cartridge to the server registry."""
    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )
    from raise_cli.cartridges.server_models import CartridgeNodePayload, PublishRequest
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.config.server import get_server_credentials
    from raise_cli.storage.connection import get_project_id
    from raise_core.cartridges.ingest import ingest_cartridge

    creds = get_server_credentials()
    if creds is None:
        typer.echo(
            "Error: Server not configured — run 'rai connect <org>' "
            "or set RAISE_SERVER_URL + RAISE_API_KEY",
            err=True,
        )
        raise typer.Exit(1)
    server_url, api_key = creds

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    secret_matches = scan_for_secrets(cartridge_dir)
    if secret_matches:
        typer.echo("⚠  Potential secrets detected:")
        for m in secret_matches:
            typer.echo(f"   - {m.pattern_name} in {m.file_path}:{m.line_number}")
        if not yes:
            if not typer.confirm("Publish anyway?", default=False):
                raise typer.Exit(1)
        else:
            typer.echo("Publishing anyway (--yes).")

    graph = ingest_cartridge(cartridge_dir)

    nodes = [
        CartridgeNodePayload(
            node_id=node.id,
            node_type=node.type,
            scope=node.metadata.get("scope", "project"),
            content=node.content,
            source_file=node.source_file,
            properties={
                k: v
                for k, v in node.metadata.items()
                if k not in _INTERNAL_METADATA_KEYS
            },
        )
        for node in graph.iter_concepts()
    ]

    repo_root = resolve_checkout_root()
    project_id = get_project_id(repo_root)

    vis: str = (
        "private"
        if private
        else (visibility if visibility in ("public", "private") else "public")
    )

    if not yes:
        confirmed = typer.confirm(
            f"Publish '{cartridge}' as {vis}? This cannot be recalled once cached."
        )
        if not confirmed:
            raise typer.Exit(0)

    request = PublishRequest(
        cartridge_name=cartridge,
        project_id=project_id,
        nodes=nodes,
        edges=_build_edge_payloads(graph),
        visibility=vis,  # type: ignore[arg-type]
    )

    client = CartridgeServerClient(server_url, api_key)
    try:
        result = client.publish_cartridge(request)
    except CartridgeServerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        client.close()

    typer.echo(
        f"Published '{result.cartridge_name}' to server "
        f"({result.nodes_inserted} nodes, {result.edges_inserted} edges)"
    )
    _publish_post_message(
        result_visibility=result.visibility,
        result_org_plan=result.org_plan,
        requested_private=private,
        yes=yes,
    )


def _is_local_path(source: str) -> bool:
    """Detect if source is a local file path (vs a cartridge name)."""
    return "/" in source or "\\" in source or source.endswith(".tar.gz")


@app.command("install")
def install(
    source: Annotated[
        str,
        typer.Argument(help="Cartridge name (server) or path to .cartridge.tar.gz"),
    ],
    target: Annotated[
        Path,
        typer.Option(
            "--target",
            "-t",
            help="Installation directory (local archives only)",
        ),
    ] = DEFAULT_CARTRIDGES_DIR,
) -> None:
    """Install a cartridge from the server registry or a local archive."""
    if _is_local_path(source):
        try:
            result = install_cartridge(Path(source), target)
        except CartridgeInstallError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
        typer.echo(f"Installed: {result}")
    else:
        from raise_cli.cartridges.server_client import CartridgeServerError
        from raise_cli.cartridges.server_install import install_from_server
        from raise_cli.config.server import get_server_credentials
        from raise_cli.storage.connection import get_project_db_path, get_project_id

        creds = get_server_credentials()
        if creds is None:
            typer.echo(
                "Error: Server not configured — run 'rai connect <org>' "
                "or set RAISE_SERVER_URL + RAISE_API_KEY",
                err=True,
            )
            raise typer.Exit(1)
        server_url, api_key = creds

        from raise_cli.config.paths import resolve_checkout_root

        repo_root = resolve_checkout_root()
        project_id = get_project_id(repo_root)
        db_path = get_project_db_path(repo_root)

        try:
            count = install_from_server(
                source, server_url, api_key, project_id, db_path
            )
        except CartridgeServerError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
        typer.echo(f"Installed '{source}' from server ({count} nodes, status: enabled)")


@app.command("uninstall")
def uninstall(
    name: Annotated[
        str,
        typer.Argument(help="Cartridge name to uninstall"),
    ],
    target: Annotated[
        Path,
        typer.Option(
            "--target",
            "-t",
            help="Installation directory",
        ),
    ] = DEFAULT_CARTRIDGES_DIR,
) -> None:
    """Uninstall (remove) an installed cartridge."""
    import shutil

    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
    from raise_cli.storage.connection import get_project_db_path, get_project_id

    repo_root = resolve_checkout_root()
    project_id = get_project_id(repo_root)
    db_path = get_project_db_path(repo_root)
    backend = SQLiteGraphBackend(project_id, db_path)
    installation = backend.get_cartridge_installation(name)

    creds = get_server_credentials()

    source = installation.get("source") if installation else None
    if source == "server" and creds:
        server_url, api_key = creds
        client = CartridgeServerClient(server_url, api_key)
        try:
            client.org_uninstall(name)
        except CartridgeServerError as exc:
            if exc.status_code == 409 and exc.detail:
                typer.echo(
                    f"Error: {name} has active project assignments:",
                    err=True,
                )
                for proj in exc.detail.get("blocking_projects", []):
                    typer.echo(f"  - {proj}", err=True)
                typer.echo(
                    "Use 'rai cartridge unassign' to remove assignments first.",
                    err=True,
                )
                raise typer.Exit(1) from exc
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
        finally:
            client.close()

    if installation:
        backend.delete_cartridge_nodes(name)
        backend.remove_cartridge_installation(name)
        cartridge_dir = target / name
        if cartridge_dir.exists():
            shutil.rmtree(cartridge_dir)
    else:
        try:
            uninstall_cartridge(name, target)
        except CartridgeInstallError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(1) from exc
    typer.echo(f"Uninstalled: {name}")


_ABUSE_CONTACT = "abuse@raise.ai"


@app.command("delete")
def delete_cartridge(
    name: Annotated[
        str,
        typer.Argument(help="Cartridge name to delete from the registry"),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Delete a cartridge from the registry (owner-only, permanent).

    This removes the cartridge from the public marketplace and cascades to all
    org installs. It cannot be undone. To report abuse: abuse@raise.ai
    """
    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )

    creds = get_server_credentials()
    if not creds:
        typer.echo(
            "Error: not connected to a server — run 'rai connect' first.", err=True
        )
        raise typer.Exit(1)

    if not yes:
        typer.confirm(
            f"Permanently delete '{name}' from the registry? This cannot be undone.",
            abort=True,
        )

    server_url, api_key = creds
    client = CartridgeServerClient(server_url, api_key)
    try:
        client.delete_remote(name)
    except CartridgeServerError as exc:
        if exc.status_code == 429:
            typer.echo(f"Error: {exc}", err=True)
            typer.echo(
                f"To report abuse or request an emergency takedown: {_ABUSE_CONTACT}",
                err=True,
            )
            raise typer.Exit(1) from exc
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        client.close()

    typer.echo(f"Deleted '{name}' from the registry.")
    typer.echo(
        f"To report abuse or request a takedown of a cartridge: {_ABUSE_CONTACT}"
    )


def _build_extractors() -> dict[str, CartridgeExtractor]:
    """Build extractor registry, including LLM if deps are available."""
    from raise_cli.config.paths import get_claude_memory_dir
    from raise_cli.memory.frontmatter_extractor import MemoryFrontmatterExtractor

    extractors: dict[str, CartridgeExtractor] = {
        "yaml": YAMLExtractor(),
        "markdown": MarkdownExtractor(),
        # RAISE-13911 AR follow-up (gap #3): register the memory cartridge's
        # frontmatter extractor so a generic `rai cartridge extract` run (or
        # any future cartridge declaring `type: frontmatter` in its
        # extractors/config.yaml) resolves instead of silently warning
        # "No extractor registered for type 'frontmatter'". memory_root is
        # resolved from CWD, matching this module's existing convention
        # (DEFAULT_CARTRIDGES_DIR is CWD-relative too — no --project flag).
        # The real external memory cartridge does not rely on this: it
        # always builds its own MemoryFrontmatterExtractor with the caller's
        # project_root via ingest_memory_cartridge() (raise_cli/memory/
        # ingest_cartridge.py) — this registration is a defensive fallback
        # for the generic path, not the primary one.
        "frontmatter": MemoryFrontmatterExtractor(
            memory_root=get_claude_memory_dir(Path.cwd())
        ),
    }
    try:
        from raise_core.cartridges.llm_extract import LLMExtractor

        extractors["llm"] = LLMExtractor()
    except ImportError:
        pass
    return extractors


_BUILTIN_EXTRACTORS: dict[str, CartridgeExtractor] = _build_extractors()


def _run_retrieval_gate(cartridge_dir: Path) -> CliGateResult | None:
    """Run retrieval quality gate if the cartridge has eval fixtures."""
    from raise_cli.eval._paths import CARTRIDGE_EVAL_DIR
    from raise_cli.eval.gate import EvalGate
    from raise_cli.gates.models import GateContext

    eval_dir = cartridge_dir / CARTRIDGE_EVAL_DIR
    if not (eval_dir / "qrels.tsv").exists():
        return None

    gate = EvalGate()
    return gate.evaluate(GateContext(gate_id=gate.gate_id, working_dir=eval_dir))


def _enforce_retrieval_gate(cartridge_dir: Path) -> CliGateResult | None:
    """Run retrieval gate and abort on failure."""
    gate_result = _run_retrieval_gate(cartridge_dir)
    if gate_result is not None and not gate_result.passed:
        typer.echo(gate_result.message, err=True)
        for detail in gate_result.details:
            typer.echo(f"  {detail}", err=True)
        raise typer.Exit(1)
    return gate_result


@app.command("extract")
def extract(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
    ],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview without writing instances"),
    ] = False,
    embed: Annotated[
        bool,
        typer.Option(
            "--embed",
            help="Generate vector embeddings (requires sentence-transformers)",
        ),
    ] = False,
    emit_work: Annotated[
        bool,
        typer.Option(
            "--emit-work",
            help="Agent-native: write per-chunk work orders instead of calling an "
            "LLM. Fill each .work.json with your own inference, then run "
            "'rai cartridge ingest'. No API key required.",
        ),
    ] = False,
) -> None:
    """Extract corpus files into GraphNode instances."""
    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    if emit_work:
        from raise_core.cartridges.agent_extract import WORK_DIR_NAME, emit_work_orders

        summary = emit_work_orders(cartridge_dir)
        work_dir = cartridge_dir / WORK_DIR_NAME
        typer.echo(
            f"Wrote {len(summary.orders)} work order(s) to {work_dir}/ "
            f"({summary.new} new, {summary.reused} reused"
            + (f", {summary.orphaned} orphaned result(s)" if summary.orphaned else "")
            + ")"
        )
        typer.echo(
            "Fill each *.work.json's prompt with your own inference, writing the "
            "JSON node list to the sibling *.result.json, then run:\n"
            f"  rai cartridge ingest {cartridge}"
        )
        return

    embedding_provider = None
    if embed:
        from raise_cli.embeddings.provider import get_default_provider

        embedding_provider = get_default_provider()

    gate_result = _enforce_retrieval_gate(cartridge_dir)

    result = extract_cartridge(
        cartridge_dir,
        extractors=_BUILTIN_EXTRACTORS,
        embedding_provider=embedding_provider,
        dry_run=dry_run,
    )

    for warn in result.warnings:
        typer.echo(f"WARN: {warn}", err=True)
    for err in result.errors:
        typer.echo(f"ERROR: {err}", err=True)

    if dry_run:
        typer.echo(f"[dry-run] Would extract {result.node_count} nodes")
    else:
        typer.echo(f"Extracted {result.node_count} nodes")
        if gate_result is not None:
            for detail in gate_result.details:
                typer.echo(f"Retrieval gate: {detail}")
        if result.node_count > 0:
            typer.echo(f"Instances written to {cartridge_dir / 'instances'}/")

    if result.errors:
        raise typer.Exit(1)


@app.command("ingest")
def ingest(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
    ],
    embed: Annotated[
        bool,
        typer.Option(
            "--embed",
            help="Generate vector embeddings (requires sentence-transformers)",
        ),
    ] = False,
) -> None:
    """Ingest agent-filled work orders into GraphNode instances.

    Completes the agent-native flow started by 'extract --emit-work': reads each
    .result.json the agent produced, validates and de-duplicates the nodes, and
    writes cartridge instances — the same back-half as the API extractor, with
    no external LLM key required.
    """
    from raise_core.cartridges.agent_extract import ingest_work_results

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    embedding_provider = None
    if embed:
        from raise_cli.embeddings.provider import get_default_provider

        embedding_provider = get_default_provider()

    result = ingest_work_results(cartridge_dir, embedding_provider=embedding_provider)

    for warn in result.warnings:
        typer.echo(f"WARN: {warn}", err=True)
    for err in result.errors:
        typer.echo(f"ERROR: {err}", err=True)

    typer.echo(f"Ingested {result.node_count} nodes")
    if result.node_count > 0:
        typer.echo(f"Instances written to {cartridge_dir / 'instances'}/")

    if result.errors:
        raise typer.Exit(1)


@app.command("relate")
def relate(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
    ],
    emit_work: Annotated[
        bool,
        typer.Option(
            "--emit-work",
            help="Write a relationship work order over the full node inventory.",
        ),
    ] = False,
    ingest_work: Annotated[
        bool,
        typer.Option(
            "--ingest",
            help="Apply the agent-filled relationship result onto instances.",
        ),
    ] = False,
) -> None:
    """Second-pass relationship extraction over the full node inventory.

    Per-chunk entity extraction misses cross-section/cross-type relationships.
    This pass shows the agent every extracted node and asks it to link them,
    constrained to the cartridge's relationship schema — no API key required.

    Flow: `relate --emit-work` → fill relationships.result.json with your own
    inference → `relate --ingest`.
    """
    from raise_core.cartridges.relate import (
        emit_relationship_work,
        ingest_relationship_work,
    )

    if emit_work == ingest_work:
        typer.echo("Specify exactly one of --emit-work or --ingest.", err=True)
        raise typer.Exit(2)

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    if emit_work:
        order_path = emit_relationship_work(cartridge_dir)
        typer.echo(f"Wrote relationship work order to {order_path}")
        typer.echo(
            "Fill its prompt with your own inference, writing "
            '{"relationships": [...]} to the sibling relationships.result.json, '
            f"then run:\n  rai cartridge relate {cartridge} --ingest"
        )
        return

    count = ingest_relationship_work(cartridge_dir)
    typer.echo(f"Attached {count} relationship(s); instances updated.")


def _print_hygiene_report(result: HygieneResult, cartridge_name: str) -> None:
    """Print the hygiene report in human-readable form."""
    rep = result.report
    typer.echo(f"Hygiene report for '{cartridge_name}':")
    typer.echo(
        f"  nodes: {rep.dedup.total_in} -> {rep.dedup.total_out} unique "
        f"({rep.dedup.disambiguated} disambiguated, "
        f"{rep.dedup.dropped_duplicates} true duplicates dropped)"
    )
    if rep.dedup.collisions:
        top = sorted(rep.dedup.collisions.items(), key=lambda kv: -kv[1])[:5]
        formatted = ", ".join(f"{node_id} x{count}" for node_id, count in top)
        typer.echo(
            f"  id collisions: {len(rep.dedup.collisions)} ids (top: {formatted})"
        )
    non_canonical = ""
    if rep.edge_types.non_canonical:
        preserved = ", ".join(sorted(rep.edge_types.non_canonical))
        non_canonical = f" ({preserved} preserved as non-canonical)"
    typer.echo(
        f"  edge types: {rep.edge_types.types_before} -> "
        f"{rep.edge_types.types_after}{non_canonical}"
    )
    typer.echo(f"  broken relationships: {len(rep.broken_relationships)}")
    for broken in rep.broken_relationships[:10]:
        typer.echo(f"    {broken.source} -> {broken.type} -> {broken.target} (missing)")
    if len(rep.broken_relationships) > 10:
        typer.echo(f"    ... and {len(rep.broken_relationships) - 10} more")


@app.command("clean")
def clean(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'raise-methodology')"),
    ],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview without rewriting instances"),
    ] = False,
) -> None:
    """Apply data hygiene to existing instances — no LLM re-extraction.

    Dedups node IDs, normalizes edge types, and reports broken
    relationships, then rewrites instances/*.json in place.
    """
    from raise_core.graph.models import GraphNode

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    instances_dir = cartridge_dir / "instances"
    if not instances_dir.is_dir():
        typer.echo(f"Error: no instances directory in {cartridge_dir}", err=True)
        raise typer.Exit(1)

    cartridge_name = read_cartridge_name(cartridge_dir, default=cartridge)

    if (instances_dir / "embedding_index.json").exists():
        typer.echo(
            "WARN: embeddings exist and are keyed by node ID — IDs renamed by "
            "clean will desync them. Re-run extraction with embeddings after "
            "cleaning.",
            err=True,
        )

    nodes: list[GraphNode] = []
    file_stems: list[str] = []  # instances file that holds nodes[i]
    instance_files = sorted(instances_dir.glob("*.json"))
    for instance_file in instance_files:
        raw_nodes = json.loads(instance_file.read_text(encoding="utf-8"))
        if not isinstance(raw_nodes, list):
            typer.echo(f"WARN: skipping {instance_file.name} — not a list", err=True)
            continue
        for raw_node in raw_nodes:
            nodes.append(GraphNode.model_validate(raw_node))
            file_stems.append(instance_file.stem)
    if not nodes:
        typer.echo(f"Error: no instances found in {instances_dir}", err=True)
        raise typer.Exit(1)

    result = apply_hygiene(nodes, id_prefix=f"kc-{cartridge_name}-")
    _print_hygiene_report(result, cartridge_name)

    if dry_run:
        typer.echo("[dry-run] No files written")
        return

    by_stem: dict[str, list[GraphNode]] = {stem: [] for stem in file_stems}
    for node, source_index in zip(result.nodes, result.kept_indices, strict=True):
        by_stem[file_stems[source_index]].append(node)
    for stem, stem_nodes in by_stem.items():
        output = instances_dir / f"{stem}.json"
        output.write_text(
            json.dumps(
                [n.model_dump(mode="json") for n in stem_nodes],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    typer.echo(f"Instances rewritten to {instances_dir}/")


@app.command("extract-server")
def extract_server(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'soc2-controls')"),
    ],
    node_type: Annotated[
        str,
        typer.Option("--node-type", "-n", help="Node type for extraction"),
    ] = "concept",
) -> None:
    """Trigger server-side LLM extraction for a cartridge (Pro required)."""
    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )
    from raise_cli.cartridges.server_models import ExtractionRequest
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.config.server import get_server_credentials
    from raise_cli.storage.connection import get_project_id

    creds = get_server_credentials()
    if creds is None:
        typer.echo(
            "Error: Server not configured — run 'rai connect <org>' "
            "or set RAISE_SERVER_URL + RAISE_API_KEY",
            err=True,
        )
        raise typer.Exit(1)
    server_url, api_key = creds

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    try:
        manifest, _config = load_cartridge(cartridge_dir)
    except CartridgeConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    corpus = _read_corpus(manifest.corpus, cartridge_dir)
    if not corpus:
        typer.echo(f"Error: No corpus files found in cartridge '{cartridge}'", err=True)
        raise typer.Exit(1)

    corpus_kb = len(corpus.encode("utf-8")) / 1024
    typer.echo(
        f"Submitting extraction for '{cartridge}' ({corpus_kb:.1f} KB corpus)..."
    )

    repo_root = resolve_checkout_root()
    project_id = get_project_id(repo_root)

    request = ExtractionRequest(
        corpus=corpus,
        node_type=node_type,
        project_id=project_id,
    )

    client = CartridgeServerClient(server_url, api_key)
    try:
        job = client.submit_extraction(cartridge, request)
        typer.echo(f"Job {job.job_id}: {job.status}")

        delay = 1.0
        max_delay = 10.0
        while job.status in ("queued", "running"):
            time.sleep(delay)
            job = client.poll_extraction_job(job.job_id)
            typer.echo(
                f"Job {job.job_id}: {job.status}"
                + (f" — {job.node_count} nodes extracted" if job.node_count else "")
            )
            delay = min(delay * 2, max_delay)

        if job.status == "failed":
            typer.echo(
                f"Job {job.job_id}: failed — {job.error or 'unknown error'}",
                err=True,
            )
            typer.echo("Error: Extraction failed", err=True)
            raise typer.Exit(1)

    except CartridgeServerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        client.close()


def _read_corpus(corpus_paths: list[str], cartridge_dir: Path) -> str:
    """Read and concatenate corpus files from the manifest."""
    corpus_base_dir = _corpus_base_dir(cartridge_dir)
    parts: list[str] = []
    for path_str in corpus_paths:
        path = Path(path_str)
        if not path.is_absolute():
            path = corpus_base_dir / path
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            parts.append(f"--- {path.name} ---\n{content}")
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix in (".md", ".txt", ".yaml", ".yml"):
                    content = child.read_text(encoding="utf-8")
                    parts.append(f"--- {child.name} ---\n{content}")
    return "\n\n".join(parts)


def _run_extraction(
    client: CartridgeServerClient,
    cartridge: str,
    cartridge_dir: Path,
    node_type: str,
    project_id: str,
) -> None:
    """Run server-side extraction phase for update command.

    Gracefully skips on 403 (Pro plan required).
    """
    from raise_cli.cartridges.server_client import CartridgeServerError
    from raise_cli.cartridges.server_models import ExtractionRequest

    try:
        manifest, _config = load_cartridge(cartridge_dir)
    except CartridgeConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    corpus = _read_corpus(manifest.corpus, cartridge_dir)
    if not corpus:
        typer.echo("WARN: No corpus files — skipping extraction", err=True)
        return

    corpus_kb = len(corpus.encode("utf-8")) / 1024
    typer.echo(
        f"Submitting extraction for '{cartridge}' ({corpus_kb:.1f} KB corpus)..."
    )

    ext_request = ExtractionRequest(
        corpus=corpus,
        node_type=node_type,
        project_id=project_id,
    )

    try:
        job = client.submit_extraction(cartridge, ext_request)
        typer.echo(f"Job {job.job_id}: {job.status}")

        delay = 1.0
        max_delay = 10.0
        while job.status in ("queued", "running"):
            time.sleep(delay)
            job = client.poll_extraction_job(job.job_id)
            typer.echo(
                f"Job {job.job_id}: {job.status}"
                + (f" — {job.node_count} nodes extracted" if job.node_count else "")
            )
            delay = min(delay * 2, max_delay)

        if job.status == "failed":
            typer.echo(
                f"Job {job.job_id}: failed — {job.error or 'unknown error'}",
                err=True,
            )
            typer.echo("Error: Extraction failed", err=True)
            raise typer.Exit(1)

    except CartridgeServerError as exc:
        if exc.status_code == 403:
            typer.echo(
                "WARN: Server-side extraction requires Pro plan — skipping",
                err=True,
            )
            return
        raise


@app.command("update")
def update(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'soc2-controls')"),
    ],
    clean: Annotated[
        bool,
        typer.Option(
            "--clean", help="Delete namespace before publish (removes orphan nodes)"
        ),
    ] = False,
    node_type: Annotated[
        str,
        typer.Option("--node-type", "-n", help="Node type for extraction"),
    ] = "concept",
) -> None:
    """Publish + extract in one flow. Use --clean to remove orphan nodes."""
    import contextlib

    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )
    from raise_cli.cartridges.server_models import CartridgeNodePayload, PublishRequest
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.config.server import get_server_credentials
    from raise_cli.storage.connection import get_project_id
    from raise_core.cartridges.ingest import ingest_cartridge

    creds = get_server_credentials()
    if creds is None:
        typer.echo(
            "Error: Server not configured — run 'rai connect <org>' "
            "or set RAISE_SERVER_URL + RAISE_API_KEY",
            err=True,
        )
        raise typer.Exit(1)
    server_url, api_key = creds

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    _run_integrity_check(cartridge_dir)

    repo_root = resolve_checkout_root()
    project_id = get_project_id(repo_root)

    client = CartridgeServerClient(server_url, api_key)
    try:
        if clean:
            typer.echo(f"Cleaning namespace '{cartridge}'...")
            with contextlib.suppress(CartridgeServerError):
                client.delete_remote(cartridge)

        graph = ingest_cartridge(cartridge_dir)
        nodes = [
            CartridgeNodePayload(
                node_id=node.id,
                node_type=node.type,
                scope=node.metadata.get("scope", "project"),
                content=node.content,
                source_file=node.source_file,
                properties={
                    k: v
                    for k, v in node.metadata.items()
                    if k not in _INTERNAL_METADATA_KEYS
                },
            )
            for node in graph.iter_concepts()
        ]

        request = PublishRequest(
            cartridge_name=cartridge,
            project_id=project_id,
            nodes=nodes,
            edges=_build_edge_payloads(graph),
        )

        result = client.publish_cartridge(request)
        typer.echo(
            f"Published '{result.cartridge_name}' to server "
            f"({result.nodes_inserted} nodes, {result.edges_inserted} edges)"
        )

        _run_extraction(client, cartridge, cartridge_dir, node_type, project_id)

    except CartridgeServerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        client.close()


@app.command()
def query(
    query_or_cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name or query (auto-detect if 1 cartridge)"),
    ],
    query_str: Annotated[
        str | None,
        typer.Argument(help="Query string (omit if cartridge auto-detected)"),
    ] = None,
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human, compact, json"),
    ] = "human",
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum results"),
    ] = 10,
    all_cartridges: Annotated[
        bool,
        typer.Option("--all", help="Federated query across all cartridges"),
    ] = False,
    org: Annotated[
        list[str] | None,
        typer.Option(
            "--org", help="Filter federated results to org cartridges (repeatable)"
        ),
    ] = None,
) -> None:
    """Query a cartridge for relevant concepts."""
    if all_cartridges:
        _query_federated(query_or_cartridge, fmt, limit, org_ids=org)
        return

    cartridge_name, actual_query = _resolve_query_args(query_or_cartridge, query_str)

    cartridge_dir = _resolve_cartridge_dir(cartridge_name)
    try:
        manifest, config = load_cartridge(cartridge_dir)
    except CartridgeConfigError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    try:
        adapter = resolve_adapter(manifest)
        builder = resolve_builder(manifest)
    except CartridgeConfigError:
        _query_via_ingest(cartridge_dir, manifest, actual_query, fmt, limit)
        return

    from raise_core.graph.retrieval.engine import retrieve

    graph = builder.build_from_directory(config.node_dir)

    _creds = get_server_credentials()
    alpha = manifest.retrieval.resolve_alpha() if manifest.retrieval else None
    tfidf_corpus = (
        _load_tfidf_corpus(cartridge_dir / "instances") if alpha and alpha > 0 else None
    )
    scorer = resolve_semantic_scorer(
        embeddings_dirs=[cartridge_dir / "instances"],
        server_url=_creds[0] if _creds else None,
        api_key=_creds[1] if _creds else None,
        sem_alpha=alpha,
        tfidf_corpus=tfidf_corpus,
    )
    logger.info("scorer_type=%s alpha=%s", type(scorer).__name__, alpha or 0)

    result = retrieve(
        graph=graph,
        query=actual_query,
        adapter=adapter,
        top_k=limit,
        semantic_scorer=scorer,
    )

    prompting = manifest.prompting
    if fmt == "json":
        typer.echo(format_query_json(result, prompting))
    elif fmt == "compact":
        typer.echo(format_query_compact(result, manifest.name, prompting))
    else:
        typer.echo(format_query_human(result, manifest.display_name, prompting))


def _query_federated(
    query: str,
    fmt: str,
    limit: int,
    org_ids: list[str] | None = None,
) -> None:
    """Run federated query across all registered cartridges."""
    from raise_core.cartridges.ingest import ingest_cartridge
    from raise_core.graph.engine import Graph

    cartridges = discover_cartridges(DEFAULT_CARTRIDGES_DIR)
    if not cartridges:
        typer.echo("Error: No cartridges found.", err=True)
        raise typer.Exit(1)

    cartridges = list(cartridges)
    graph = Graph()
    instances_dirs: list[Path] = []
    for _manifest, _config in cartridges:
        base = _config.domain_dir or _config.node_dir.parent
        graph = ingest_cartridge(base, graph=graph)
        instances_dirs.append(base / "instances")

    alpha_max, tfidf_corpus = _resolve_federated_hybrid_params(cartridges)

    _creds = get_server_credentials()
    scorer = resolve_semantic_scorer(
        embeddings_dirs=instances_dirs,
        server_url=_creds[0] if _creds else None,
        api_key=_creds[1] if _creds else None,
        sem_alpha=alpha_max,
        tfidf_corpus=tfidf_corpus,
    )
    logger.info(
        "scorer_type=%s alpha=%s (federated)", type(scorer).__name__, alpha_max or 0
    )

    results = federated_query(
        graph, query=query, limit=limit, semantic_scorer=scorer, org_ids=org_ids
    )

    if not results:
        typer.echo("No results found.", err=True)
        raise typer.Exit(0)

    if fmt == "json":
        data = {
            "query": query,
            "mode": "federated",
            "results": [
                {
                    "node_id": r.node_id,
                    "cartridge": r.cartridge,
                    "score": r.score,
                    "type": r.node_type,
                    "content": r.content,
                }
                for r in results
            ],
        }
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
    elif fmt == "compact":
        lines = [
            f"# Federated: {query} ({len(results)} results, "
            f"{len({r.cartridge for r in results})} cartridges)"
        ]
        for r in results:
            content = r.content[:150] + "..." if len(r.content) > 150 else r.content
            lines.append(f"[{r.cartridge}] **{r.node_type}** {r.node_id}: {content}")
        typer.echo("\n".join(lines))
    else:
        cartridge_count = len({r.cartridge for r in results})
        lines = [
            f"═══ Federated Query: {query} "
            f"({len(results)} results from {cartridge_count} cartridges) ═══",
            "",
        ]
        for i, r in enumerate(results, 1):
            content = r.content[:200] + "..." if len(r.content) > 200 else r.content
            lines.append(
                f"{i}. [{r.cartridge}] {r.node_id} [{r.node_type}] {r.score:.4f}"
            )
            lines.append(f"   {content}")
            lines.append("")
        typer.echo("\n".join(lines))


def _query_via_ingest(
    cartridge_dir: Path,
    manifest: object,
    actual_query: str,
    fmt: str,
    limit: int,
) -> None:
    """Query using ingest_cartridge + QueryEngine (default path)."""
    import logging

    from raise_core.cartridges.ingest import ingest_cartridge
    from raise_core.graph.query import Query, QueryEngine

    class _SuppressNodeTypeWarnings(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return "not registered" not in record.getMessage()

    _suppress = _SuppressNodeTypeWarnings()
    engine_logger = logging.getLogger("raise_core.graph.engine")
    engine_logger.addFilter(_suppress)
    try:
        graph = ingest_cartridge(cartridge_dir)

        if graph.node_count == 0:
            typer.echo("No nodes found in cartridge instances.", err=True)
            raise typer.Exit(1)

        cartridge_name: str = getattr(manifest, "name", cartridge_dir.name)
        display_name: str = getattr(manifest, "display_name", cartridge_name)

        engine = QueryEngine(graph)
        result = engine.query(
            Query(query=actual_query, cartridge=cartridge_name, limit=limit)
        )

        if fmt == "json":
            data: dict[str, object] = {
                "query": actual_query,
                "cartridge": cartridge_name,
                "results": [
                    {
                        "id": c.id,
                        "type": c.type,
                        "content": c.content,
                    }
                    for c in result.concepts
                ],
            }
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
        elif fmt == "compact":
            lines = [
                f"# Knowledge: {actual_query} ({len(result.concepts)} results, {cartridge_name})"
            ]
            for c in result.concepts:
                content = c.content[:150] + "..." if len(c.content) > 150 else c.content
                lines.append(f"**{c.type}** {c.id}: {content}")
            typer.echo("\n".join(lines))
        else:
            lines = [
                f"═══ {display_name}: {actual_query} ({len(result.concepts)} results) ═══",
                "",
            ]
            if not result.concepts:
                lines.append("*No relevant nodes found.*")
            else:
                for i, c in enumerate(result.concepts, 1):
                    content = (
                        c.content[:200] + "..." if len(c.content) > 200 else c.content
                    )
                    lines.append(f"{i}. {c.id} [{c.type}]")
                    lines.append(f"   {content}")
                    lines.append("")
            typer.echo("\n".join(lines))
    finally:
        engine_logger.removeFilter(_suppress)


def _resolve_query_args(
    query_or_cartridge: str,
    query_str: str | None,
) -> tuple[str, str]:
    """Resolve cartridge name and query string from CLI args."""
    if query_str is not None:
        return query_or_cartridge, query_str

    cartridges = discover_cartridges(DEFAULT_CARTRIDGES_DIR)
    if len(cartridges) == 1:
        return cartridges[0][0].name, query_or_cartridge
    if len(cartridges) == 0:
        typer.echo("Error: No cartridges found.", err=True)
        raise typer.Exit(1)
    names = ", ".join(m.name for m, _ in cartridges)
    typer.echo(
        f"Error: Multiple cartridges found ({names}). Specify cartridge explicitly.",
        err=True,
    )
    raise typer.Exit(1)


def _count_instance_nodes(directory: Path) -> int:
    """Count materialized nodes in a cartridge instances directory.

    Instance payloads are stored as JSON arrays (`model.json`, `rules.json`,
    `repo.json`, etc.). Auxiliary JSON objects such as `embedding_index.json`
    are ignored.
    """
    if not directory.exists():
        return 0
    total = 0
    for path in directory.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001, S112
            continue
        if isinstance(data, list):
            total += len(data)
    return total


@app.command("catalog")
def catalog(
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: table, json"),
    ] = "table",
) -> None:
    """List cartridges available for this org from the server."""
    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )

    creds = get_server_credentials()
    if not creds:
        typer.echo(
            "Error: No server configured — set RAISE_SERVER_URL and RAISE_API_KEY",
            err=True,
        )
        raise typer.Exit(1)

    server_url, api_key = creds
    client = CartridgeServerClient(server_url, api_key)
    try:
        items = client.list_public()
    except CartridgeServerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        client.close()

    if not items:
        typer.echo("No cartridges available for this org.")
        return

    installed_names = {t[0] for t in _get_installations()}

    if fmt == "json":
        data = [
            {
                "name": item.cartridge_name,
                "publisher": item.author_org_id or "",
                "status": "installed"
                if item.cartridge_name in installed_names
                else "available",
                "node_count": item.node_count,
            }
            for item in items
        ]
        typer.echo(json.dumps(data, indent=2))
        return

    # Table output
    typer.echo(f"\nOrg cartridges (raise-server: {server_url}):\n")
    col_name = max(len(i.cartridge_name) for i in items)
    col_pub = max((len(i.author_org_id or "") for i in items), default=9)
    col_name = max(col_name, 4)
    col_pub = min(20, max(col_pub, 9))
    header = f"  {'NAME':<{col_name}}  {'PUBLISHER':<{col_pub}}  {'STATUS':<9}  NODES"
    sep = f"  {'-' * col_name}  {'-' * col_pub}  {'-' * 9}  -----"
    typer.echo(header)
    typer.echo(sep)
    for item in items:
        status = "installed" if item.cartridge_name in installed_names else "available"
        publisher = (item.author_org_id or "")[:20]
        typer.echo(
            f"  {item.cartridge_name:<{col_name}}  {publisher:<{col_pub}}  {status:<9}  {item.node_count}"
        )
    installed_count = sum(1 for i in items if i.cartridge_name in installed_names)
    typer.echo(f"\n{len(items)} cartridges available, {installed_count} installed.")


@app.command("curate")
def curate(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'scaleup')"),
    ],
    action: Annotated[
        str,
        typer.Argument(help="Action: start, status, accept, reject, skip, write"),
    ] = "status",
    reason: Annotated[
        str | None,
        typer.Option("--reason", "-r", help="Reason for accept/reject decision"),
    ] = None,
) -> None:
    """HITL curation of extracted cartridge nodes."""
    from raise_core.cartridges.curate import CurationDecision, CurationSession

    cartridge_dir = _resolve_cartridge_dir(cartridge)
    source_dir = cartridge_dir / "instances"
    output_dir = cartridge_dir / "curated"
    state_path = cartridge_dir / ".curation-state.yaml"

    if not source_dir.exists():
        typer.echo("No instances/ directory — run extract first.", err=True)
        raise typer.Exit(1)

    session = CurationSession.load(source_dir, output_dir, state_path)

    if action == "status":
        summary = session.summary()
        typer.echo(
            f"Curation: {summary.accepted} accepted, {summary.rejected} rejected, "
            f"{summary.edited} edited, {summary.remaining} remaining "
            f"(total: {summary.total})"
        )
    elif action == "start":
        node = session.current_node()
        typer.echo(f"Node: {node.id} ({node.type})")
        typer.echo(f"Content: {node.content[:200]}")
        typer.echo(f"Metadata: {json.dumps(node.metadata, default=str)}")
    elif action == "accept":
        node = session.current_node()
        session.record_decision(node.id, CurationDecision.ACCEPTED, reason=reason)
        typer.echo(f"Accepted: {node.id}")
    elif action == "reject":
        node = session.current_node()
        session.record_decision(node.id, CurationDecision.REJECTED, reason=reason)
        typer.echo(f"Rejected: {node.id}")
    elif action == "skip":
        session.skip()
        typer.echo("Skipped current node")
    elif action == "write":
        written = session.write_curated()
        typer.echo(f"Wrote {written} curated nodes to {output_dir}/")
    else:
        typer.echo(
            f"Unknown action: {action}. Use: start, status, accept, reject, skip, write",
            err=True,
        )
        raise typer.Exit(1)


def _project_backend() -> tuple[str, Path, SQLiteGraphBackend]:
    """Resolve (project_id, db_path, backend) for the current repo."""
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
    from raise_cli.storage.connection import get_project_db_path, get_project_id

    repo_root = resolve_checkout_root()
    project_id = get_project_id(repo_root)
    db_path = get_project_db_path(repo_root)
    return project_id, db_path, SQLiteGraphBackend(project_id, db_path)


@app.command("sync")
def sync() -> None:
    """Sync assigned cartridges from the server (server → local, one-way)."""
    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
        CartridgeServerError,
    )
    from raise_cli.cartridges.server_install import install_from_server

    creds = get_server_credentials()
    if not creds:
        typer.echo(
            "Error: No server configured — set RAISE_SERVER_URL and RAISE_API_KEY",
            err=True,
        )
        raise typer.Exit(1)

    server_url, api_key = creds
    project_id, db_path, backend = _project_backend()

    client = CartridgeServerClient(server_url, api_key)
    try:
        assignments = client.list_project_assignments(project_id)
    except CartridgeServerError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    finally:
        client.close()

    if not assignments:
        typer.echo("No cartridges assigned to this project.")
        return

    installed = {row[0]: row for row in backend.list_cartridge_installations()}

    typer.echo(f"Syncing cartridges for project '{project_id}' from {server_url}...")
    n_installed = 0
    n_updated = 0
    n_current = 0
    for item in assignments:
        existing = installed.get(item.cartridge_name)
        if existing is None:
            try:
                count = install_from_server(
                    item.cartridge_name,
                    server_url,
                    api_key,
                    project_id,
                    db_path,
                    policy=item.policy,
                    ensure_org_install=False,
                )
            except CartridgeServerError as exc:
                typer.echo(f"Error installing '{item.cartridge_name}': {exc}", err=True)
                raise typer.Exit(1) from exc
            typer.echo(
                f"  + {item.cartridge_name:<22} installed ({count} nodes)"
                f"  policy: {item.policy}"
            )
            n_installed += 1
        else:
            _name, source, _status, node_count, _installed_at, old_policy = existing
            if old_policy != item.policy:
                backend.register_cartridge_installation(
                    item.cartridge_name,
                    source,
                    server_url,
                    node_count,
                    policy=item.policy,
                )
                typer.echo(
                    f"  ~ {item.cartridge_name:<22} policy updated:"
                    f" {old_policy} → {item.policy}"
                )
                n_updated += 1
            else:
                typer.echo(
                    f"  = {item.cartridge_name:<22} up to date"
                    f"             policy: {item.policy}"
                )
                n_current += 1

    parts: list[str] = []
    for count, label in (
        (n_installed, "installed"),
        (n_updated, "policy updated"),
        (n_current, "up to date"),
    ):
        if count:
            parts.append(f"{count} {label}")
    typer.echo(f"Sync complete: {', '.join(parts)}.")


@app.command("enable")
def enable(
    name: Annotated[str, typer.Argument(help="Cartridge name")],
) -> None:
    """Re-enable a locally disabled cartridge."""
    _project_id, _db_path, backend = _project_backend()

    record = backend.get_cartridge_installation(name)
    if record is None:
        typer.echo(f"Error: '{name}' is not installed.", err=True)
        raise typer.Exit(1)

    backend.set_cartridge_status(name, "enabled")
    typer.echo(f"Enabled '{name}'.")


@app.command("disable")
def disable(
    name: Annotated[str, typer.Argument(help="Cartridge name")],
) -> None:
    """Disable a cartridge locally (blocked when policy is 'required')."""
    _project_id, _db_path, backend = _project_backend()

    record = backend.get_cartridge_installation(name)
    if record is None:
        typer.echo(f"Error: '{name}' is not installed.", err=True)
        raise typer.Exit(1)

    if record.get("policy") == "required":
        typer.echo(
            f"Error: '{name}' has policy 'required' (set by your org admin). "
            "It cannot be disabled locally.",
            err=True,
        )
        raise typer.Exit(1)

    backend.set_cartridge_status(name, "disabled")
    typer.echo(
        f"Disabled '{name}' (policy: optional). "
        f"Re-enable with: rai cartridge enable {name}"
    )


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

_AUDIT_STATUS_SYMBOL = {"pass": "✓", "warn": "⚠", "fail": "✗"}


def _print_audit_report(cartridge_name: str, report: AuditReport) -> None:
    """Render a human-readable audit report."""
    typer.echo(f"Cartridge: {cartridge_name}")
    typer.echo(f"Verdict: {report.verdict}")
    typer.echo("")
    typer.echo(f"{'Dimension':<22} {'Status':<8} Details")
    typer.echo("-" * 60)
    for dim_name, dim in report.dimensions.items():
        symbol = _AUDIT_STATUS_SYMBOL.get(dim.status, "?")
        detail = dim.findings[0] if dim.findings else str(dim.metrics)
        typer.echo(f"{dim_name:<22} {symbol} {dim.status:<6}  {detail}")


@app.command("audit")
def audit(
    cartridge: Annotated[
        str,
        typer.Argument(help="Cartridge name (e.g., 'raise-methodology')"),
    ],
    compare: Annotated[
        list[str],
        typer.Option(
            "--compare",
            help="Compare with another cartridge for aptitud cross-cartridge dimension",
        ),
    ] = [],  # noqa: B006
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output audit report as JSON"),
    ] = False,
) -> None:
    """Audit cartridge quality across 7 dimensions. Exit 0=GO, 1=NO-GO.

    Measures integridad, trazabilidad, frescura, cobertura, granularidad,
    relaciones, and aptitud cross-cartridge. Heuristic dimensions (granularidad,
    aptitud) can only warn, never fail.
    """
    cartridge_dir = _resolve_cartridge_dir(cartridge)
    other_dirs = [_resolve_cartridge_dir(c) for c in compare] if compare else None

    report = audit_cartridge(cartridge_dir, other_cartridges=other_dirs)

    if output_json:
        typer.echo(report.model_dump_json(indent=2))
    else:
        _print_audit_report(cartridge, report)

    if report.no_go:
        raise typer.Exit(1)
