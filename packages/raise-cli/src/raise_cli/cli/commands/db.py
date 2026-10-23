"""rai db — SQLite database diagnostics and export."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.config.paths import get_global_rai_dir
from raise_cli.storage.connection import get_project_db, get_project_db_path
from raise_cli.storage.migrate import migrate_if_needed
from raise_cli.storage.schema import create_all, validate_current_schema

db_app = typer.Typer(
    name="db",
    help="SQLite personal database diagnostics and backup.",
    no_args_is_help=True,
)


def _get_project_root() -> Path:
    return Path.cwd()


def _db_exists(project: Path) -> bool:
    return get_project_db_path(project).exists()


def _get_tables(project: Path) -> dict[str, int]:
    conn = get_project_db(project)
    create_all(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    counts: dict[str, int] = {}
    for row in rows:
        name: str = row["name"]
        count: int = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]  # noqa: S608  # nosec B608
        counts[name] = count
    conn.close()
    return counts


@db_app.command()
def check() -> None:
    """Check database integrity, foreign keys, and current schema invariants."""
    project = _get_project_root()
    out = Console()

    if not _db_exists(project):
        out.print("No database found. Run a rai command first to create it.")
        return

    conn = get_project_db(project)
    try:
        create_all(conn)
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        fk_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
        schema_problems = validate_current_schema(conn, require_tables=True)
        version: int = conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()

    problems: list[str] = []
    if integrity != "ok":
        problems.append(f"integrity_check: {integrity}")
    if fk_rows:
        problems.append(f"foreign_key_check: {len(fk_rows)} violation(s)")
    problems.extend(schema_problems)

    if problems:
        out.print(f"[red]DB check failed[/red] (schema v{version})")
        for problem in problems:
            out.print(f"  - {problem}")
        raise typer.Exit(1)

    out.print(f"DB OK: schema v{version}, integrity ok, foreign keys ok")


@db_app.command()
def status(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="JSON output"),
    ] = False,
) -> None:
    """Show database stats: tables, row counts, size, schema version."""
    project = _get_project_root()
    out = Console()

    if not _db_exists(project):
        if json_output:
            out.print_json(json.dumps({"error": "no database found"}))
        else:
            out.print("No database found. Run a rai command first to create it.")
        return

    db_path = get_project_db_path(project)
    size_bytes = db_path.stat().st_size
    tables = _get_tables(project)

    conn = get_project_db(project)
    version: int = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()

    if json_output:
        data = {
            "db_path": str(db_path),
            "size_bytes": size_bytes,
            "schema_version": version,
            "tables": tables,
        }
        out.print_json(json.dumps(data))
        return

    size_kb = size_bytes / 1024
    out.print(f"\nRaiSE DB: {db_path} ({size_kb:,.0f} KB)")
    out.print(f"Schema version: {version}")

    table = Table(show_header=True)
    table.add_column("Table", style="cyan")
    table.add_column("Rows", justify="right")
    for name, count in tables.items():
        table.add_row(name, f"{count:,}")
    out.print(table)


@db_app.command()
def consolidate(  # noqa: C901 — intentional fan-out: dry-run/backup/per-source/lock error paths
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Report what would happen without writing."),
    ] = False,
) -> None:
    """Merge orphaned per-project DBs into the global ~/.rai/raise.db.

    Scans legacy ~/.rai/projects partitions, project-local DBs, and
    worktree copies. Verifies row counts per table; sources are renamed
    to *.consolidated only after a verified merge — never deleted.
    """
    from raise_cli.storage.consolidate import consolidate_all, discover_sources
    from raise_cli.storage.maintenance_lock import MaintenanceLockHeldError

    project = _get_project_root()
    out = Console()

    sources = discover_sources(project)
    if not sources:
        out.print("No orphaned per-project DBs found — nothing to consolidate.")
        return

    out.print(f"Scan: {len(sources)} fuente(s)")
    for src in sources:
        out.print(f"  [{src.kind}] {src.path} (project_id={src.project_id})")

    try:
        result = consolidate_all(sources=sources, dry_run=dry_run)
    except MaintenanceLockHeldError as exc:
        out.print(
            f"[red]Lock contention:[/red] db_consolidation held by PID "
            f"{exc.holder.pid} (expires {exc.holder.expires_at})"
        )
        out.print(
            f"Action: wait for expiry, or verify PID {exc.holder.pid} is alive "
            f"(kill -0 {exc.holder.pid})."
        )
        out.print("If the process is dead, the lock auto-recovers on next attempt.")
        raise typer.Exit(1) from exc

    if result.tables_skipped:
        skipped = ", ".join(sorted(result.tables_skipped))
        out.print(f"Tablas desconocidas (skipped): {skipped}")

    if dry_run:
        total = sum(result.rows_migrated.values())
        for table_name, count in sorted(result.rows_migrated.items()):
            out.print(f"  {table_name}: {count} filas candidatas")
        out.print(
            f"Dry-run: nada modificado. {result.sources_found} DB(s) "
            f"consolidables, {total} filas candidatas."
        )
        return

    if result.backup_path is not None:
        out.print(f"Backup: {result.backup_path}")

    total_new = 0
    total_dup = 0
    for table_name in sorted(result.rows_migrated):
        src_rows = result.rows_migrated[table_name]
        inserted = result.rows_inserted.get(table_name, 0)
        total_new += inserted
        total_dup += src_rows - inserted
        out.print(
            f"  {table_name}: {src_rows} filas ({inserted} nuevas, "
            f"{src_rows - inserted} duplicadas)"
        )

    if result.errors:
        out.print(f"[red]{len(result.errors)} fuente(s) fallaron:[/red]")
        for err in result.errors:
            out.print(f"  - {err}")
        out.print("Las fuentes con error NO fueron marcadas como consolidadas.")
        raise typer.Exit(1)

    out.print(
        f"Total: {result.sources_migrated} DB(s), {total_new} filas nuevas, "
        f"{total_dup} ignoradas, 0 perdidas"
    )


def _run_import_legacy(project: Path, out: Console) -> None:
    """Core logic for the import-legacy operation (shared by import-legacy and migrate)."""
    result = migrate_if_needed(project)

    if not result.success:
        out.print(f"[red]Import failed:[/red] {', '.join(result.errors)}")
        raise typer.Exit(1)

    out.print(result.message)


@db_app.command("import-legacy")
def import_legacy() -> None:
    """Import legacy JSONL/YAML personal data into SQLite (one-time).

    Scans legacy file locations (.raise/rai/personal/...) and imports
    sessions, journal entries, signals, and pipeline runs into the SQLite
    database. Original files are renamed to .migrated — never deleted.
    Idempotent: already-migrated sources are skipped.
    """
    project = _get_project_root()
    out = Console()
    _run_import_legacy(project, out)


@db_app.command("migrate")
def migrate() -> None:
    """[Deprecated] Use 'rai db import-legacy' instead.

    This command imports legacy JSONL/YAML personal data into SQLite.
    The name 'migrate' is misleading because the actual schema migration
    (DDL: CREATE TABLE / ALTER TABLE) happens automatically on every DB open.
    Use 'rai db import-legacy' for the same one-time data-import operation.
    """
    out = Console()
    out.print(
        "[yellow]Warning:[/yellow] 'rai db migrate' is deprecated. "
        "Use 'rai db import-legacy' instead."
    )
    project = _get_project_root()
    _run_import_legacy(project, out)


@db_app.command()
def export(
    output: Annotated[
        Path | None,
        typer.Option(
            "--out",
            help=(
                "Parent directory for the timestamped export folder. "
                "Defaults to $RAI_HOME/exports/ to keep backups outside the project tree."
            ),
        ),
    ] = None,
) -> None:
    """Export all tables to JSONL files for backup.

    By default exports to $RAI_HOME/exports/<timestamp>/ so the backup files
    stay outside the project repository and are never accidentally committed.
    Use --out to override the destination.
    """
    project = _get_project_root()
    out = Console()

    if not _db_exists(project):
        out.print("No database found. Nothing to export.")
        return

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S")
    export_parent = output if output is not None else get_global_rai_dir() / "exports"
    export_dir = export_parent / timestamp
    export_dir.mkdir(parents=True, exist_ok=True)

    tables = _get_tables(project)
    conn = get_project_db(project)
    create_all(conn)

    total_rows = 0
    for table_name, count in tables.items():
        rows = conn.execute(f"SELECT * FROM [{table_name}]").fetchall()  # noqa: S608  # nosec B608
        file_path = export_dir / f"{table_name}.jsonl"
        with file_path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(dict(row)) + "\n")
        total_rows += count
        out.print(f"  {table_name}.jsonl ({count} rows)")

    conn.close()

    out.print(f"\nExported {len(tables)} tables ({total_rows:,} rows) to {export_dir}/")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read a JSONL file into a list of dicts."""
    rows: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _import_table(
    conn: sqlite3.Connection,
    table_name: str,
    rows: list[dict[str, object]],
    *,
    merge: bool,
) -> tuple[int, int]:
    """Import rows into a single table. Returns (imported, skipped)."""
    if not merge:
        conn.execute(f"DELETE FROM [{table_name}]")  # noqa: S608  # nosec B608

    columns = list(rows[0].keys())
    table_cols = {
        row[1] for row in conn.execute(f"PRAGMA table_info([{table_name}])").fetchall()
    }
    columns = [c for c in columns if c in table_cols]

    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(f"[{c}]" for c in columns)
    conflict = " OR IGNORE" if merge else ""
    sql = f"INSERT{conflict} INTO [{table_name}] ({col_names}) VALUES ({placeholders})"  # nosec B608

    imported = 0
    skipped = 0
    for row in rows:
        values = [
            json.dumps(v) if isinstance(v, (dict, list)) else v
            for v in (row.get(c) for c in columns)
        ]
        try:
            result = conn.execute(sql, values)
            imported += 1 if result.rowcount > 0 else 0
            skipped += 0 if result.rowcount > 0 else 1
        except Exception:  # noqa: BLE001
            skipped += 1

    conn.commit()
    return imported, skipped


@db_app.command("import")
def import_db(
    path: Annotated[
        Path,
        typer.Argument(help="Directory containing JSONL files from 'rai db export'"),
    ],
    merge: Annotated[
        bool,
        typer.Option("--merge", help="Merge into existing data (skip conflicts)"),
    ] = False,
) -> None:
    """Import JSONL backup into the local database.

    Without --merge, replaces all data (destructive).
    With --merge, inserts rows skipping primary key conflicts.
    """
    project = _get_project_root()
    out = Console()

    if not path.is_dir():
        out.print(f"[red]Not a directory:[/red] {path}")
        raise typer.Exit(1)

    jsonl_files = sorted(path.glob("*.jsonl"))
    if not jsonl_files:
        out.print(f"[red]No JSONL files found in[/red] {path}")
        raise typer.Exit(1)

    conn = get_project_db(project)
    create_all(conn)
    existing_tables = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
    }

    if not merge and not typer.confirm(
        f"This will REPLACE all data in {len(existing_tables)} tables. Continue?"
    ):
        conn.close()
        raise typer.Abort()

    total_imported = 0
    total_skipped = 0

    for jsonl_file in jsonl_files:
        table_name = jsonl_file.stem
        if table_name not in existing_tables:
            out.print(f"  [yellow]skip[/yellow] {table_name} (table not in schema)")
            continue

        rows = _read_jsonl(jsonl_file)
        if not rows:
            continue

        imported, skipped = _import_table(conn, table_name, rows, merge=merge)
        total_imported += imported
        total_skipped += skipped
        status = f"{imported} imported"
        if skipped:
            status += f", {skipped} skipped"
        out.print(f"  {table_name}: {status}")

    conn.close()
    out.print(
        f"\nImported {total_imported:,} rows ({total_skipped:,} skipped) from {path}"
    )
