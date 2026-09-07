"""CLI commands for portfolio metadata management."""

from __future__ import annotations

import json as _json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from raise_cli.portfolio.storage import VALID_CHANGE_MODES, PortfolioStore

# DA-4: M0 built-in fixVersion constant for RaiSE project (D7 explicit list, never >=)
_DEFAULT_TRACKED_VERSIONS: tuple[str, ...] = ("3.0.0", "3.1.0", "3.1.0b1")

portfolio_app = typer.Typer(
    name="portfolio",
    help="Manage portfolio metadata (components, epic profiles)",
    no_args_is_help=True,
)

epic_profile_app = typer.Typer(
    name="epic-profile",
    help="Manage epic planning-time portfolio profiles",
    no_args_is_help=True,
)
portfolio_app.add_typer(epic_profile_app, name="epic-profile")

initiative_profile_app = typer.Typer(
    name="initiative-profile",
    help="Manage initiative-level portfolio profiles",
    no_args_is_help=True,
)
portfolio_app.add_typer(initiative_profile_app, name="initiative-profile")


@epic_profile_app.command("create")
def epic_profile_create(
    epic_key: Annotated[str, typer.Argument(help="Jira epic key (e.g. RAISE-15210)")],
    components: Annotated[
        str,
        typer.Option(
            "--components",
            "-c",
            help="Comma-separated component IDs (e.g. portfolio,storage,gates)",
        ),
    ],
    change_mode: Annotated[
        str,
        typer.Option(
            "--change-mode",
            "-m",
            help=f"Change mode: {', '.join(sorted(VALID_CHANGE_MODES))}",
        ),
    ],
    project: Annotated[
        Path,
        typer.Option(
            "--project",
            "-p",
            help="Project root (default: current directory)",
        ),
    ] = Path("."),
) -> None:
    """Record planning-time portfolio metadata for an epic."""
    components_touched = [c.strip() for c in components.split(",") if c.strip()]
    store = PortfolioStore(project.resolve())
    valid = store.get_valid_component_names()
    if valid:
        unknown = [c for c in components_touched if c not in valid]
        if unknown:
            typer.echo(
                f"Error: unknown component(s): {', '.join(unknown)}\n"
                f"Valid: {', '.join(sorted(valid))}",
                err=True,
            )
            raise typer.Exit(1)
    try:
        profile = store.create_epic_profile(
            epic_key=epic_key,
            components_touched=components_touched,
            change_mode=change_mode,
        )
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(
        f"epic_profile: {profile.epic_key} | {profile.change_mode}"
        f" | {profile.components_touched}"
    )


@portfolio_app.command("dsm")
def portfolio_dsm(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Write artifact to PATH instead of stdout.",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: markdown (default) | json (raw adjacency dict).",
        ),
    ] = "markdown",
    gate_initiative: Annotated[
        str | None,
        typer.Option(
            "--gate-initiative",
            help="Initiative key to evaluate with BeforeReadyGate (appends verdict).",
        ),
    ] = None,
    project: Annotated[
        Path,
        typer.Option(
            "--project",
            "-p",
            help="Project root (default: current directory).",
        ),
    ] = Path("."),
) -> None:
    """Render the Portfolio DSM (Dependency Structure Matrix) as a governance artifact.

    Reads confirmed edges and initiative profiles from the local project DB,
    builds DependencyGraph + advisory derivation, and emits a Markdown or JSON
    snapshot.  Use --output to commit the artifact; omit to preview on stdout.

    Examples::

        rai portfolio dsm
        rai portfolio dsm --output work/epics/e15198-portfolio-impact-model/stories/raise-15209-dsm.md
        rai portfolio dsm --format json
        rai portfolio dsm --gate-initiative RAISE-15165 --output dsm.md
    """
    from raise_cli.portfolio.dependency.graph import DependencyGraph
    from raise_cli.portfolio.derivation import derive_advisory_edges
    from raise_cli.portfolio.dsm_render import render_dsm_markdown

    project_root = project.resolve()
    store = PortfolioStore(project_root)

    deps = store.list_deps()
    profiles = store.list_initiative_profiles()

    snapshot_at = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    if format == "json":
        advisory = derive_advisory_edges(profiles)
        graph = DependencyGraph(deps=deps, advisory=advisory)
        content = _json.dumps(graph.dsm_view(), indent=2)
    else:
        gate_verdict: str | None = None
        if gate_initiative:
            import os

            from raise_cli.gates.governance.before_ready_gate import (
                BeforeReadyGate,
            )
            from raise_cli.gates.models import GateContext

            os.environ["RAISE_PORTFOLIO_GATE_INITIATIVE_KEY"] = gate_initiative
            ctx = GateContext(gate_id="gate-before-ready", working_dir=project_root)
            result = BeforeReadyGate().evaluate(ctx)
            gate_verdict = "PASS" if result.passed else "FAIL"

        content = render_dsm_markdown(
            deps,
            profiles,
            snapshot_at=snapshot_at,
            gate_verdict=gate_verdict,
            gate_initiative=gate_initiative,
        )

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        typer.echo(f"DSM written to {output}")
    else:
        typer.echo(content)


@portfolio_app.command("suggest")
def portfolio_suggest(
    key: Annotated[
        str, typer.Argument(help="Jira key (any level: initiative, epic, story, bug)")
    ],
    project: Annotated[
        Path,
        typer.Option(
            "--project",
            "-p",
            help="Project root (default: current directory)",
        ),
    ] = Path("."),
) -> None:
    """Print a draft portfolio suggestion for a Jira key based on git history.

    Searches git log for commits mentioning KEY, maps changed files to
    portfolio components, and infers change_mode from graph contract nodes
    and numstat deletions.  Nothing is persisted — use the output to inform
    ``portfolio epic-profile create`` or ``portfolio initiative-profile create``.
    """
    from raise_cli.portfolio.suggest import suggest_for_key

    result = suggest_for_key(key, project.resolve())
    pct = (
        int(100 * result.mapped_count / result.total_count) if result.total_count else 0
    )
    typer.echo(f"Suggestion for {result.key}:")
    typer.echo(f"  components_touched : {result.components_touched}")
    typer.echo(f"  change_mode        : {result.change_mode or '(unknown)'}")
    typer.echo(f"  contracts_affected : {result.contracts_affected}")
    typer.echo(f"  commit_count       : {result.commit_count}")
    typer.echo(
        f"  coverage           : {result.mapped_count}/{result.total_count} archivos mapeados ({pct}%)"
    )
    if result.unmapped_files:
        typer.echo("  unmapped files:")
        for path in result.unmapped_files:
            typer.echo(f"    - {path}")
    typer.echo(f"  note               : {result.note}")


@epic_profile_app.command("get")
def epic_profile_get(
    epic_key: Annotated[str, typer.Argument(help="Jira epic key")],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root"),
    ] = Path("."),
) -> None:
    """Print the epic profile for the given key, or exit 1 if not found."""
    store = PortfolioStore(project.resolve())
    profile = store.get_epic_profile(epic_key)
    if profile is None:
        typer.echo(f"No profile found for {epic_key}", err=True)
        raise typer.Exit(1)
    typer.echo(
        f"epic_profile: {profile.epic_key} | {profile.change_mode}"
        f" | {profile.components_touched}"
    )


# ── Initiative Profile sub-app ───────────────────────────────────────────────


@initiative_profile_app.command("create")
def initiative_profile_create(
    initiative_key: Annotated[
        str, typer.Argument(help="Jira initiative key (e.g. RAISE-15165)")
    ],
    components: Annotated[
        str,
        typer.Option(
            "--components",
            "-c",
            help="Comma-separated component IDs (e.g. portfolio,storage,gates)",
        ),
    ],
    change_mode: Annotated[
        str,
        typer.Option(
            "--change-mode",
            "-m",
            help=f"Change mode: {', '.join(sorted(VALID_CHANGE_MODES))}",
        ),
    ],
    contracts: Annotated[
        str,
        typer.Option(
            "--contracts",
            help="Comma-separated contract IDs affected (optional)",
        ),
    ] = "",
    rationale: Annotated[
        str,
        typer.Option(
            "--rationale", "-r", help="One-line rationale for the classification"
        ),
    ] = "",
    project: Annotated[
        Path,
        typer.Option(
            "--project", "-p", help="Project root (default: current directory)"
        ),
    ] = Path("."),
) -> None:
    """Record initiative-level portfolio metadata."""
    components_touched = [c.strip() for c in components.split(",") if c.strip()]
    contracts_affected = [c.strip() for c in contracts.split(",") if c.strip()]
    store = PortfolioStore(project.resolve())
    valid = store.get_valid_component_names()
    if valid:
        unknown = [c for c in components_touched if c not in valid]
        if unknown:
            typer.echo(
                f"Error: unknown component(s): {', '.join(unknown)}\n"
                f"Valid: {', '.join(sorted(valid))}",
                err=True,
            )
            raise typer.Exit(1)
    try:
        profile = store.create_initiative_profile(
            initiative_key=initiative_key,
            components_touched=components_touched,
            change_mode=change_mode,
            contracts_affected=contracts_affected,
            rationale=rationale,
        )
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(
        f"initiative_profile: {profile.initiative_key} | {profile.change_mode}"
        f" | {profile.components_touched}"
    )


@initiative_profile_app.command("get")
def initiative_profile_get(
    initiative_key: Annotated[str, typer.Argument(help="Jira initiative key")],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root"),
    ] = Path("."),
) -> None:
    """Print the initiative profile for the given key, or exit 1 if not found."""
    store = PortfolioStore(project.resolve())
    profile = store.get_initiative_profile(initiative_key)
    if profile is None:
        typer.echo(f"No profile found for {initiative_key}", err=True)
        raise typer.Exit(1)
    typer.echo(
        f"initiative_profile: {profile.initiative_key} | {profile.change_mode}"
        f" | {profile.components_touched}"
    )


@initiative_profile_app.command("list")
def initiative_profile_list(
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root"),
    ] = Path("."),
) -> None:
    """List all initiative profiles for the current project."""
    store = PortfolioStore(project.resolve())
    profiles = store.list_initiative_profiles()
    if not profiles:
        typer.echo("No initiative profiles found.")
        return
    for p in profiles:
        typer.echo(
            f"{p.initiative_key:20s} | {p.change_mode:12s} | {p.components_touched}"
        )


# ── Portfolio cartridge sub-app ───────────────────────────────────────────────


def _resolve_portfolio_versions(
    project_root: Path,
    flag_versions: str | None,
) -> Sequence[str] | None:
    """DA-4 precedence: --versions flag > manifest tracked_versions > built-in constant.

    Returns None when --all-versions should suppress the fixVersion clause entirely.
    Caller passes flag_versions=None when --all-versions is set.
    """
    if flag_versions is not None:
        return [v.strip() for v in flag_versions.split(",") if v.strip()]
    resolved_version: str | None = None
    try:
        import yaml

        from raise_cli.release_version import (
            resolve_fix_version_with_source,
        )

        manifest = project_root / ".raise" / "manifest.yaml"
        if manifest.is_file():
            data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
            development_branch = str(
                (data.get("branches") or {}).get("development") or ""
            )
            resolved_version = resolve_fix_version_with_source(
                project_root, development_branch
            ).version
            tracked = (
                (data.get("project") or {}).get("portfolio", {}).get("tracked_versions")
            )
            if tracked and isinstance(tracked, list):
                versions = [str(v) for v in tracked]
                if resolved_version and resolved_version not in versions:
                    versions.append(resolved_version)
                return versions
    except Exception:  # noqa: BLE001, S110
        pass
    versions = list(_DEFAULT_TRACKED_VERSIONS)
    if resolved_version and resolved_version not in versions:
        versions.append(resolved_version)
    return versions


def build_portfolio_jql(
    project_key: str,
    profile_keys: Sequence[str],
    *,
    versions: Sequence[str] | None,
    since: datetime | None = None,
) -> str:
    """D6 ∪ D7: build the portfolio JQL for the CLI fetch.

    versions=None → --all-versions (no fixVersion clause, only issuetype guard).
    since is reserved for RAISE-15272 delta support; currently unused (DA-4).
    """
    base = f"project = {project_key} AND issuetype in (Epic, Initiative)"
    if versions:
        quoted = ", ".join(f'"{v}"' for v in versions)
        scope_clause = f"fixVersion in ({quoted})"
    else:
        scope_clause = None

    # D6: always union with profile keys so no local profile is orphaned
    if profile_keys:
        key_list = ", ".join(profile_keys)
        profile_clause = f"key in ({key_list})"
        if scope_clause:
            filter_clause = f"({scope_clause} OR {profile_clause})"
        else:
            filter_clause = profile_clause
    elif scope_clause:
        filter_clause = scope_clause
    else:
        filter_clause = None

    jql = base
    if filter_clause:
        jql = f"{jql} AND {filter_clause}"
    jql += " ORDER BY updated DESC"

    # DA-4 / RAISE-15272: delta clause reserved (since param exists for frozen UX contract)
    _ = since

    return jql


cartridge_app = typer.Typer(
    name="cartridge",
    help="Manage portfolio issue cartridges (.raise/cartridges/portfolio-issues-*).",
    no_args_is_help=True,
)
portfolio_app.add_typer(cartridge_app, name="cartridge")


@cartridge_app.command("generate")
def cartridge_generate(
    project_key: Annotated[str, typer.Argument(help="Jira project key (e.g. RAISE)")],
    org: Annotated[str, typer.Argument(help="Organisation identifier (e.g. humansys)")],
    versions: Annotated[
        str | None,
        typer.Option(
            "--versions",
            help="Comma-separated fixVersion list; overrides manifest tracked_versions",
        ),
    ] = None,
    all_versions: Annotated[
        bool,
        typer.Option(
            "--all-versions",
            help="Drop the fixVersion scope (issuetype guard stays). Deliberate full-history act.",
        ),
    ] = False,
    delta: Annotated[
        bool,
        typer.Option(
            "--delta",
            help="Incremental fetch since last run (RAISE-15272; not yet implemented)",
        ),
    ] = False,
    since: Annotated[
        datetime | None,
        typer.Option(
            "--since",
            formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"],
            help="Lower bound for --delta (default: manifest generation.last_fetch_at)",
        ),
    ] = None,
    adapter: Annotated[
        str | None,
        typer.Option("--adapter", help="Adapter name override"),
    ] = None,
) -> None:
    """Generate a portfolio issues cartridge from Jira epics + local profiles.

    Fetches epics and initiatives via JQL, merges with local epic/initiative
    profiles, writes instances/model.json and CARTRIDGE.yaml under
    .raise/cartridges/portfolio-issues-{org}-{project}/.

    After generating, run `rai graph build` to make portfolio nodes queryable.
    """
    # DA-3: guard delta/since before any side effects — zero network calls, zero writes
    if delta or since is not None:
        raise NotImplementedError(
            "--delta/--since land in RAISE-15272; run without them for a full snapshot"
        )

    if all_versions and versions:
        raise typer.BadParameter(
            "--all-versions and --versions are mutually exclusive",
            param_hint="'--all-versions'",
        )

    from raise_cli.cli.commands._resolve import resolve_adapter

    pm = resolve_adapter(adapter)
    project_root = Path.cwd()
    store = PortfolioStore(project_root)

    profiles = store.list_epic_profiles() + store.list_initiative_profiles()
    profile_keys = [
        str(getattr(p, "epic_key", None) or getattr(p, "initiative_key", ""))
        for p in profiles
    ]

    resolved_versions: Sequence[str] | None
    if all_versions:
        resolved_versions = None
    else:
        resolved_versions = _resolve_portfolio_versions(project_root, versions)

    jql = build_portfolio_jql(project_key, profile_keys, versions=resolved_versions)
    issues = pm.search(jql, fetch_all=True)

    from raise_core.cartridges.portfolio_issues import (
        generate_portfolio_issues_cartridge,
    )

    cartridges_dir = (project_root / ".raise" / "cartridges").resolve()
    cartridge_dir = generate_portfolio_issues_cartridge(
        issues,
        profiles,
        cartridges_dir,
        org_id=org,
        project_key=project_key,
    )

    typer.echo(f"✓ Cartridge generated: {cartridge_dir.name}")
    typer.echo("Next: run `rai graph build` to make portfolio nodes queryable.")
