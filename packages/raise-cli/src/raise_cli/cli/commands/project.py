"""CLI commands: rai project — manage projects on RaiSE server."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

import httpx
import typer
from rich.console import Console
from rich.table import Table

from raise_cli.config.server import get_server_credentials
from raise_cli.core.text import slugify as _slugify

if TYPE_CHECKING:
    from raise_cli.storage.migrate_project_slug import ProjectSlugMigrationReport

console = Console()

project_app = typer.Typer(
    name="project",
    help="Manage projects on RaiSE server.",
    no_args_is_help=True,
)


@project_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]
    pass


def _server_config() -> tuple[str, str] | None:
    return get_server_credentials()


def _require_config() -> tuple[str, str]:
    cfg = _server_config()
    if not cfg:
        console.print(
            "[red]Not connected to a RaiSE server.[/red] "
            "Run [bold]rai connect[/bold] first."
        )
        raise typer.Exit(1)
    return cfg


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _handle_error(resp: httpx.Response) -> None:
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        detail = resp.text
    console.print(f"[red]Error ({resp.status_code}):[/red] {detail}")
    raise typer.Exit(1)


@project_app.command("create")
def create_command(
    name: Annotated[str, typer.Argument(help="Project name")],
    slug: Annotated[str, typer.Option("--slug", "-s", help="Slug override")] = "",
    description: Annotated[
        str, typer.Option("--description", "-d", help="Project description")
    ] = "",
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
    allow_org_mismatch: Annotated[
        bool,
        typer.Option(
            "--allow-org-mismatch",
            help="Write even if the project is bound to a different org (RAISE-9823)",
        ),
    ] = False,
) -> None:
    """Create a project on the RaiSE server."""
    from pathlib import Path

    from raise_cli.cli.commands._server_write import confirm_server_write
    from raise_cli.config.org_binding import bind_org

    project_root = Path.cwd()
    target = confirm_server_write(
        "project creation",
        yes=yes,
        project_root=project_root,
        allow_org_mismatch=allow_org_mismatch,
    )
    server_url, api_key = target.server_url, target.api_key

    if not slug:
        slug = _slugify(name)

    payload: dict[str, str | None] = {"name": name, "slug": slug}
    if description:
        payload["description"] = description

    resp = httpx.post(
        f"{server_url}/api/v2/projects",
        json=payload,
        headers=_auth_headers(api_key),
        timeout=10,
    )

    if resp.status_code == 409:
        console.print(f"[red]Project with slug '{slug}' already exists.[/red]")
        raise typer.Exit(1)

    if resp.status_code >= 400:
        _handle_error(resp)

    data = resp.json()
    if target.org_id:
        bind_org(project_root, target.org_name, target.org_id)
    org_label = target.org_name or target.server_url
    console.print(f"[green]✓ Project created[/green] in org '{org_label}'")
    console.print(f"  Name: {data.get('name', name)}")
    console.print(f"  Slug: {data.get('slug', slug)}")
    if data.get("description"):
        console.print(f"  Description: {data['description']}")


def _resolve_repo_uuid(server_url: str, api_key: str, repo_slug: str) -> str | None:
    """Resolve a repository slug to its UUID via the list endpoint."""
    resp = httpx.get(
        f"{server_url}/api/v2/repositories",
        headers=_auth_headers(api_key),
        timeout=10,
    )
    if resp.status_code >= 400:
        return None
    repos: list[dict[str, str]] = resp.json()
    for repo in repos:
        if repo.get("slug") == repo_slug:
            return repo.get("id", "")
    return None


@project_app.command("link-repo")
def link_repo_command(
    project: Annotated[str, typer.Argument(help="Project slug")],
    repo: Annotated[str, typer.Argument(help="Repository slug")],
    primary: Annotated[
        bool, typer.Option("--primary", help="Set as primary repository")
    ] = False,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
    allow_org_mismatch: Annotated[
        bool,
        typer.Option(
            "--allow-org-mismatch",
            help="Write even if the project is bound to a different org (RAISE-9823)",
        ),
    ] = False,
) -> None:
    """Link a repository to a project on the RaiSE server."""
    from pathlib import Path

    from raise_cli.cli.commands._server_write import confirm_server_write
    from raise_cli.config.org_binding import bind_org

    project_root = Path.cwd()
    target = confirm_server_write(
        "repository link",
        yes=yes,
        project_root=project_root,
        allow_org_mismatch=allow_org_mismatch,
    )
    server_url, api_key = target.server_url, target.api_key

    repo_uuid = _resolve_repo_uuid(server_url, api_key, repo)
    if not repo_uuid:
        console.print(f"[red]Repository '{repo}' not found.[/red]")
        raise typer.Exit(1)

    resp = httpx.post(
        f"{server_url}/api/v2/projects/{project}/repositories",
        json={"repository_id": repo_uuid, "is_primary": primary},
        headers=_auth_headers(api_key),
        timeout=10,
    )

    if resp.status_code == 409:
        console.print(
            f"[red]Repository '{repo}' is already linked to project '{project}'.[/red]"
        )
        raise typer.Exit(1)

    if resp.status_code >= 400:
        _handle_error(resp)

    if target.org_id:
        bind_org(project_root, target.org_name, target.org_id)
    label = " (primary)" if primary else ""
    org_label = target.org_name or target.server_url
    console.print(
        f"[green]✓ Repository '{repo}' linked to project '{project}'{label}[/green] "
        f"in org '{org_label}'"
    )


_SENSITIVE_FRAGMENTS = {"token", "password", "secret", "api_key"}


def _filter_credentials(data: dict[str, object]) -> dict[str, object]:
    """Recursively strip keys that look like credentials."""
    result: dict[str, object] = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(frag in key_lower for frag in _SENSITIVE_FRAGMENTS):
            continue
        if isinstance(value, dict):
            result[key] = _filter_credentials(value)
        elif isinstance(value, list):
            result[key] = [
                _filter_credentials(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


@project_app.command("list")
def list_command() -> None:
    """List projects on the RaiSE server."""
    server_url, api_key = _require_config()

    resp = httpx.get(
        f"{server_url}/api/v2/projects",
        headers=_auth_headers(api_key),
        timeout=10,
    )
    if resp.status_code >= 400:
        _handle_error(resp)

    projects: list[dict[str, str]] = resp.json()
    if not projects:
        console.print("No projects registered.")
        return

    table = Table(title="Projects")
    table.add_column("Name", style="bold")
    table.add_column("Slug")
    table.add_column("Description", style="dim")
    for p in projects:
        table.add_row(
            p.get("name", ""), p.get("slug", ""), p.get("description", "") or ""
        )
    console.print(table)


def _resolve_project_slug(explicit: str, config_dir: Path) -> str:
    """Resolve project slug: explicit flag > manifest > git remote > directory name."""
    if explicit:
        return explicit
    manifest = (
        config_dir.parent / "manifest.yaml"
        if config_dir.name == ".raise"
        else config_dir / "manifest.yaml"
    )
    if not manifest.is_file():
        manifest = Path(".raise") / "manifest.yaml"
    if manifest.is_file():
        try:
            import yaml  # noqa: PLC0415

            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            name = (data or {}).get("project", {}).get("name", "")
            if name:
                return _slugify(str(name))
        except Exception:  # noqa: BLE001, S110
            pass

    from raise_cli.storage.connection import get_project_id

    return get_project_id(Path.cwd())


def _read_adapter_yamls(config_dir: Path) -> dict[str, object]:
    """Read adapter YAML files and return as dict keyed by adapter type."""
    import yaml  # noqa: PLC0415

    adapters: dict[str, object] = {}

    jira_path = config_dir / "jira.yaml"
    if jira_path.is_file():
        raw = yaml.safe_load(jira_path.read_text(encoding="utf-8"))
        if raw:
            adapters["backlog"] = _filter_credentials(raw)

    docs_path = config_dir / "docs.yaml"
    if docs_path.is_file():
        raw = yaml.safe_load(docs_path.read_text(encoding="utf-8"))
        if raw:
            adapters["docs"] = _filter_credentials(raw)

    return adapters


@project_app.command("push-config")
def push_config_command(
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project slug (auto-detected if omitted)"),
    ] = "",
    config_dir: Annotated[
        str, typer.Option("--config-dir", help="Path to .raise/ directory")
    ] = "",
) -> None:
    """Push local adapter config to the RaiSE server."""
    server_url, api_key = _require_config()

    cfg_path = Path(config_dir) if config_dir else Path(".raise")
    adapters = _read_adapter_yamls(cfg_path)

    if not adapters:
        console.print(
            "[red]No adapter config found[/red] in "
            f"{cfg_path}/\n"
            "  Expected: jira.yaml and/or docs.yaml"
        )
        raise typer.Exit(1)

    slug = _resolve_project_slug(project, cfg_path)
    now = datetime.now(UTC).isoformat()

    payload = {
        "settings": {
            "config_version": 1,
            "adapters": adapters,
            "pushed_at": now,
            "pushed_by": os.environ.get("RAISE_USER_EMAIL", "unknown"),
        }
    }

    resp = httpx.post(
        f"{server_url}/api/v2/projects/{slug}/config",
        json=payload,
        headers=_auth_headers(api_key),
        timeout=10,
    )

    if resp.status_code >= 400:
        _handle_error(resp)

    adapter_names = ", ".join(
        f"{k} ({k.replace('backlog', 'jira')}.yaml)"
        if k == "backlog"
        else f"{k} ({k}.yaml)"
        for k in adapters
    )
    console.print(f"[green]✓ Config pushed[/green] to project '{slug}'")
    console.print(f"  Adapters: {adapter_names}")
    console.print("  Config version: 1")
    console.print(f"  Pushed at: {now}")


_ADAPTER_FILE_MAP: dict[str, str] = {
    "backlog": "jira.yaml",
    "docs": "docs.yaml",
}


def _content_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def _diff_adapters(
    adapters: dict[str, object],
    cfg_path: Path,
    force: bool,
) -> tuple[list[tuple[str, str, str]], list[str], list[str]]:
    """Compare server adapters against local files. Returns (to_write, skipped, blocked)."""
    import yaml  # noqa: PLC0415

    to_write: list[tuple[str, str, str]] = []
    skipped: list[str] = []
    blocked: list[str] = []

    for adapter_key, filename in _ADAPTER_FILE_MAP.items():
        adapter_data = adapters.get(adapter_key)
        if not adapter_data:
            continue

        new_content = yaml.dump(adapter_data, default_flow_style=False, sort_keys=True)
        local_path = cfg_path / filename

        if local_path.is_file():
            local_content = local_path.read_text(encoding="utf-8")
            if _content_hash(local_content) == _content_hash(new_content):
                skipped.append(filename)
                continue
            if not force:
                blocked.append(filename)
                continue

        to_write.append((filename, adapter_key, new_content))

    return to_write, skipped, blocked


@dataclass
class PullConfigResult:
    """Result of a pull-config operation — usable from CLI and init."""

    status: Literal["ok", "no_config", "error"]
    written: list[str] = field(default_factory=list)
    message: str = ""


def pull_config_core(
    server_url: str,
    api_key: str,
    project_slug: str,
    config_dir: Path,
    force: bool = False,
) -> PullConfigResult:
    """Pull adapter config from server. Returns result instead of raising typer.Exit."""
    resp = httpx.get(
        f"{server_url}/api/v2/projects/{project_slug}/config",
        headers=_auth_headers(api_key),
        timeout=10,
    )

    if resp.status_code >= 400:
        return PullConfigResult(
            status="error", message=f"Server error ({resp.status_code})"
        )

    settings: dict[str, object] = resp.json().get("settings", {})
    adapters = settings.get("adapters")
    if not adapters or not isinstance(adapters, dict):
        return PullConfigResult(
            status="no_config",
            message=f"No adapter config on server for project '{project_slug}'",
        )

    config_dir.mkdir(parents=True, exist_ok=True)
    to_write, _skipped, blocked = _diff_adapters(adapters, config_dir, force)

    if blocked:
        return PullConfigResult(
            status="error",
            message=f"Local config differs: {', '.join(blocked)}. Use --force.",
        )

    for filename, _key, content in to_write:
        (config_dir / filename).write_text(content, encoding="utf-8")

    return PullConfigResult(
        status="ok",
        written=[filename for filename, _, _ in to_write],
        message=f"Config pulled from project '{project_slug}'",
    )


@project_app.command("pull-config")
def pull_config_command(
    project: Annotated[
        str,
        typer.Option("--project", "-p", help="Project slug (auto-detected if omitted)"),
    ] = "",
    config_dir: Annotated[
        str, typer.Option("--config-dir", help="Path to .raise/ directory")
    ] = "",
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite local config even if it differs")
    ] = False,
) -> None:
    """Pull adapter config from the RaiSE server."""
    server_url, api_key = _require_config()

    cfg_path = Path(config_dir) if config_dir else Path(".raise")
    slug = _resolve_project_slug(project, cfg_path)

    resp = httpx.get(
        f"{server_url}/api/v2/projects/{slug}/config",
        headers=_auth_headers(api_key),
        timeout=10,
    )

    if resp.status_code >= 400:
        _handle_error(resp)

    from raise_cli.onboarding.manifest import persist_server_slug  # noqa: PLC0415

    project_path = cfg_path.parent if cfg_path.name == ".raise" else cfg_path
    persist_server_slug(project_path, slug)

    settings: dict[str, object] = resp.json().get("settings", {})
    adapters = settings.get("adapters")
    if not adapters or not isinstance(adapters, dict):
        console.print(f"[red]No adapter config[/red] on server for project '{slug}'")
        raise typer.Exit(1)

    cfg_path.mkdir(parents=True, exist_ok=True)
    to_write, skipped, blocked = _diff_adapters(adapters, cfg_path, force)

    if blocked:
        console.print("[yellow]Local config differs from server:[/yellow]")
        for f in blocked:
            console.print(f"  {cfg_path / f} — local modified")
        console.print("Use [bold]--force[/bold] to overwrite local config")
        raise typer.Exit(1)

    if not to_write and skipped:
        console.print("[green]✓ Already up to date[/green] — no changes from server")
        return

    for filename, _key, content in to_write:
        (cfg_path / filename).write_text(content, encoding="utf-8")

    console.print(f"[green]✓ Config pulled[/green] from project '{slug}'")
    for filename, adapter_key, _content in to_write:
        console.print(f"  Written: {cfg_path / filename} ({adapter_key})")

    console.print()
    console.print("  Set your credentials:")
    console.print("    export JIRA_API_TOKEN=<your-token>")
    console.print("    export JIRA_EMAIL=<your-email>")


def _print_reconcile_report(
    report: ProjectSlugMigrationReport,
    old_id: str,
    new_id: str,
    *,
    dry_run: bool,
) -> None:
    """Print a per-table summary of a ProjectSlugMigrationReport."""
    verb = "Would reconcile" if dry_run else "Reconciled"
    console.print(f"{verb} project_id='{old_id}' -> '{new_id}'")
    console.print(f"  Tables covered: {len(report.tables_covered)}")
    # Generic over every project_id table the migration discovered — no
    # hardcoded subset (F2). Only tables with actual movement are listed.
    for table in sorted(report.tables):
        counts = report.tables[table]
        if counts.total == 0:
            continue
        parts: list[str] = []
        if counts.migrated:
            parts.append(f"{counts.migrated} migrated")
        if counts.merged:
            parts.append(f"{counts.merged} merged/deduped")
        if counts.deleted:
            parts.append(f"{counts.deleted} deleted")
        console.print(f"  {table}: {', '.join(parts)}")
    if report.total_rows_affected == 0:
        console.print("  Nothing pending — already reconciled (idempotent no-op).")
    if not dry_run and report.backup_path is not None:
        console.print(f"  Backup: {report.backup_path}")


@project_app.command("reconcile")
def reconcile_command(
    old_id: Annotated[str, typer.Argument(help="Splinter project_id to merge away")],
    new_id: Annotated[str, typer.Argument(help="Canonical project_id to merge onto")],
    apply_: Annotated[
        bool,
        typer.Option("--apply", help="Write changes (default: dry-run report only)"),
    ] = False,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")
    ] = False,
    db_path: Annotated[
        str,
        typer.Option(
            "--db-path", help="Override raise.db path (testing/diagnostics only)"
        ),
    ] = "",
) -> None:
    """Reconcile project_id splinter rows in ~/.rai/raise.db (RAISE-13319).

    Merges every row under OLD_ID (the splinter) onto NEW_ID (the canonical
    id) across EVERY project_id-bearing table — discovered from the live
    schema, not a hardcoded subset (graph_nodes/graph_edges, patterns,
    pipeline_runs, sessions, missions, worktrees, …). Collisions are resolved
    newer-wins-wholesale, except counters (keep-max), active_sessions (dedup
    by cc_session_id) and governance_cache (drop, refetchable); see
    ``raise_cli.storage.migrate_project_slug`` for the per-table policy.

    OLD_ID and NEW_ID must differ — reconciling a project onto itself is
    rejected (it would delete every row as a self-collision).

    Dry-run by default — pass --apply to write. A backup is created before
    the first write. Idempotent: re-running after --apply finds nothing
    pending and is a no-op.

    Example (merge the 'raise' splinter back onto the canonical
    'raise-commons' — arg order is OLD NEW):
        $ rai project reconcile raise raise-commons --apply
    """
    from raise_cli.storage.connection import get_project_db_path
    from raise_cli.storage.migrate_project_slug import migrate_project_slug

    if old_id == new_id:
        console.print(
            f"[red]Error:[/red] OLD_ID and NEW_ID must differ (both '{old_id}'). "
            "Reconciling a project_id onto itself would destroy its own rows."
        )
        raise typer.Exit(1)

    resolved_db_path = Path(db_path) if db_path else get_project_db_path()

    if not apply_:
        report = migrate_project_slug(
            resolved_db_path, dry_run=True, old_id=old_id, new_id=new_id
        )
        _print_reconcile_report(report, old_id, new_id, dry_run=True)
        if report.total_rows_affected:
            console.print(
                "\n[yellow]Dry run only — no changes written.[/yellow] "
                "Re-run with --apply to write."
            )
        return

    if not yes:
        confirmed = typer.confirm(
            f"This will reconcile project_id='{old_id}' rows onto '{new_id}' "
            f"in {resolved_db_path}. A backup will be created first. Continue?"
        )
        if not confirmed:
            console.print("Aborted.")
            raise typer.Exit(0)

    report = migrate_project_slug(
        resolved_db_path, dry_run=False, old_id=old_id, new_id=new_id
    )
    _print_reconcile_report(report, old_id, new_id, dry_run=False)
