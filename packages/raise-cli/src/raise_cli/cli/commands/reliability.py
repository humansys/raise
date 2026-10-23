"""CLI commands: rai reliability — Escaped-defect reliability lens (RAISE-11490).

``rai reliability`` assembles the classifier + SZZ into an honest 3-denominator
escaped-defect report. Mirrors ``rai quality defect-rate`` conventions.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

if TYPE_CHECKING:
    from raise_cli.reliability.session_condition import ConditionBreakdown

import typer

from raise_cli.reliability.deployments import DeploymentEvent, DeploymentEventStore
from raise_cli.reliability.lens import ReliabilityLens
from raise_cli.reliability.rollup import (
    PROXY_DISCLAIMER,
    PROXY_METRICS,
    ReliabilityRollup,
)

reliability_app = typer.Typer(
    help="Escaped-defect reliability lens — 3-denominator backfill report."
)

deploy_app = typer.Typer(
    help="Register and list deployment events (production boundary)."
)
reliability_app.add_typer(deploy_app, name="deploy")

rollup_app = typer.Typer(help="Accumulate reliability snapshots and show the trend.")
reliability_app.add_typer(rollup_app, name="rollup")


@rollup_app.command("append")
def rollup_append(
    since: Annotated[
        str, typer.Option("--since", help="Backfill start date (YYYY-MM-DD)")
    ] = "2025-01-01",
    repo: Annotated[
        Path,
        typer.Option("--repo", "-r", help="Repository root", resolve_path=True),
    ] = Path("."),
) -> None:
    """Run a backfill and append its headline metrics as a rollup snapshot."""
    try:
        since_date = date.fromisoformat(since)
    except ValueError as exc:
        raise typer.BadParameter(
            f"--since must be an ISO date (YYYY-MM-DD), got: {since!r}"
        ) from exc
    report = ReliabilityLens().run_backfill(repo, since=since_date)
    snap = ReliabilityRollup(repo).append_snapshot(report)
    typer.echo(f"Snapshot appended ({snap.taken_on}): per_change={snap.per_change}")


@rollup_app.command("show")
def rollup_show(
    repo: Annotated[
        Path,
        typer.Option("--repo", "-r", help="Repository root", resolve_path=True),
    ] = Path("."),
) -> None:
    """Show the trend of headline metrics vs the previous snapshot."""
    trend = ReliabilityRollup(repo).trend()
    if trend.reason is not None:
        typer.echo(f"No trend yet: {trend.reason}")
        return
    typer.echo("Reliability trend (vs the previous snapshot only):")
    for name, d in trend.metrics.items():
        arrow = {"improving": "↓", "regressing": "↑", "flat": "→"}.get(d.direction, "?")
        prev = "—" if d.previous is None else f"{d.previous:.4f}"
        cur = "—" if d.current is None else f"{d.current:.4f}"
        tag = " *proxy" if name in PROXY_METRICS else ""
        typer.echo(f"  {name:<18} {prev} → {cur}  {arrow} {d.direction}{tag}")
    typer.echo(f"\n* {PROXY_DISCLAIMER}")


@deploy_app.command("register")
def deploy_register(
    ref: Annotated[str, typer.Option("--ref", help="Deployed git ref (SHA or tag)")],
    environment: Annotated[
        str, typer.Option("--env", help="Target environment (e.g. prod)")
    ] = "prod",
    version: Annotated[
        str | None, typer.Option("--version", help="Optional version label")
    ] = None,
    source: Annotated[
        Literal["manual", "ci"],
        typer.Option("--source", help="How the deploy was registered"),
    ] = "manual",
    at: Annotated[
        str | None,
        typer.Option("--at", help="Deploy timestamp ISO (default: now)"),
    ] = None,
    repo: Annotated[
        Path,
        typer.Option("--repo", "-r", help="Repository root", resolve_path=True),
    ] = Path("."),
) -> None:
    """Record one deployment event to the JSONL store (the production boundary)."""
    try:
        deployed_at = datetime.fromisoformat(at) if at else datetime.now()
    except ValueError as exc:
        raise typer.BadParameter(f"--at must be an ISO datetime, got: {at!r}") from exc
    event = DeploymentEvent(
        deployed_at=deployed_at,
        ref=ref,
        environment=environment,
        version=version,
        source=source,
    )
    DeploymentEventStore(repo).register(event)
    typer.echo(f"Registered deploy: {ref} → {environment} @ {deployed_at.isoformat()}")


@deploy_app.command("list")
def deploy_list(
    environment: Annotated[
        str | None, typer.Option("--env", help="Filter by environment")
    ] = None,
    since: Annotated[
        str | None, typer.Option("--since", help="Only deploys since ISO date")
    ] = None,
    repo: Annotated[
        Path,
        typer.Option("--repo", "-r", help="Repository root", resolve_path=True),
    ] = Path("."),
) -> None:
    """List registered deployment events."""
    try:
        since_date = date.fromisoformat(since) if since else None
    except ValueError as exc:
        raise typer.BadParameter(
            f"--since must be an ISO date (YYYY-MM-DD), got: {since!r}"
        ) from exc
    events = DeploymentEventStore(repo).list(environment=environment, since=since_date)
    if not events:
        typer.echo("No deployment events registered.")
        return
    for e in events:
        ver = f" ({e.version})" if e.version else ""
        typer.echo(f"{e.deployed_at.isoformat()}  {e.environment:<10} {e.ref}{ver}")


@reliability_app.callback(invoke_without_command=True)
def reliability_command(
    ctx: typer.Context,
    repo: Annotated[
        Path,
        typer.Option(
            "--repo",
            "-r",
            help="Repository root (default: current directory)",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = Path("."),
    since: Annotated[
        str,
        typer.Option(
            "--since",
            help="Start date for the analysis window, ISO format (YYYY-MM-DD)",
        ),
    ] = "2025-01-01",
    format: Annotated[
        Literal["human", "json"],
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch",
            help="Integration branch (default: manifest branches.development)",
        ),
    ] = None,
    confidence_threshold: Annotated[
        float,
        typer.Option(
            "--confidence-threshold",
            help="Minimum SZZ confidence to include an attribution (default: 0.6)",
            min=0.0,
            max=1.0,
        ),
    ] = 0.6,
) -> None:
    """Build a 3-denominator escaped-defect reliability report.

    Assembles the commit-stream classifier and SZZ introducer attribution into
    an honest report with per-change, per-deployment (deferred), and per-defect
    denominators. Confidence filtering is applied to SZZ results.

    Examples:
        rai reliability --since 2025-01-01
        rai reliability --since 2025-01-01 --format json
        rai reliability --since 2025-01-01 --branch release/3.1.0 --confidence-threshold 0.7
    """
    # A subcommand (e.g. `deploy`) handles its own work — don't run the backfill.
    if ctx.invoked_subcommand is not None:
        return

    # Parse since date robustly
    try:
        since_date = date.fromisoformat(since)
    except ValueError as exc:
        raise typer.BadParameter(
            f"--since must be an ISO date (YYYY-MM-DD), got: {since!r}"
        ) from exc

    lens = ReliabilityLens()
    report = lens.run_backfill(
        repo,
        since=since_date,
        branch=branch,
        confidence_threshold=confidence_threshold,
    )

    if format == "json":
        typer.echo(report.model_dump_json(indent=2))
    else:
        typer.echo(report.to_markdown())


# ---------------------------------------------------------------------------
# condition — join commit × condición de sesión (S11637.3 / RAISE-11668)
# ---------------------------------------------------------------------------


def _render_condition_table(
    breakdowns: list[ConditionBreakdown],
    *,
    numerator_wired: bool = False,
) -> str:
    """Renderizar tabla de condiciones como texto tabulado.

    Formato: condition (type/model/fill) | defect_density | n_changes | n_defects | confidence

    B1: cuando numerator_wired=False (el deriver produjo 0 pares en la ventana), las columnas
    defect_density y n_defects muestran '—' en lugar de 0.0000.
    Esto evita presentar un 0.0 fabricado como dato real.
    """
    if not breakdowns:
        return "(sin datos en la ventana seleccionada)"

    header = f"{'condition (type/model/fill)':<30} {'defect_density':>22} {'n_changes':>10} {'n_defects':>22} {'confidence':>12}"
    sep = "-" * len(header)
    rows = [header, sep]

    for b in breakdowns:
        cond = b.condition
        model_str = cond.model or "—"
        fill_str = cond.fill_band or "—"
        label = f"{cond.session_type} / {model_str}/{fill_str}"

        if not numerator_wired:
            density_str = "—"
            n_defects_str = "—"
        elif b.defect_density is not None:
            density_str = f"{b.defect_density:.4f}"
            n_defects_str = str(b.n_defects)
        else:
            density_str = f"None (n={b.n_changes}<5)"
            n_defects_str = str(b.n_defects)

        conf_str = b.confidence or "None"
        rows.append(
            f"{label:<30} {density_str:>22} {b.n_changes:>10} {n_defects_str:>22} {conf_str:>12}"
        )

    rows.append(sep)
    return "\n".join(rows)


def _render_caveats(
    breakdowns: list[ConditionBreakdown],
    *,
    numerator_wired: bool = False,
) -> str:
    """Renderizar bloque CAVEATS con caveats de proxies, fill_band, y prevalencia ai_unknown.

    B1: cuando numerator_wired=False (deriver produjo 0 pares en la ventana) añade caveat
    explícito: 0 fix-commits atribuibles — la ventana no tiene fix-commits con clave RAISE-.
    Incluye siempre el caveat de fill_band (v1, sin fuente). Nunca colapsa silenciosamente.
    """
    caveats = [
        "- fill_band no instrumentado en v1 (sin fuente). Columna = — (follow-up).",
        "- model resoluble solo para sesiones UUID-form con log presente.",
        "- escape/cfr del lens son PROXIES (no se usan como ground-truth aquí).",
    ]

    if not numerator_wired:
        caveats.insert(
            0,
            "- 0 fix-commits atribuibles en la ventana (numerador vacío) — defect_density no computable; "
            "n_changes es el dato vivo.",
        )

    for b in breakdowns:
        if b.condition.session_type == "ai_unknown" and b.proxy_caveat:
            caveats.insert(0, f"- {b.proxy_caveat}")

    return "CAVEATS:\n" + "\n".join(caveats)


@reliability_app.command("condition")
def condition_command(
    since: Annotated[
        str,
        typer.Option(
            "--since",
            help="Inicio de ventana temporal (YYYY-MM-DD, default: 30 días atrás)",
        ),
    ] = "",
    repo: Annotated[
        Path,
        typer.Option("--repo", "-r", help="Raíz del repositorio", resolve_path=True),
    ] = Path("."),
) -> None:
    """Session-condition reliability join — defect-density por condición de sesión.

    Responde (raise-commons es 100%-IA): ¿la CONDICIÓN de generación IA
    (`interactive` vs `batch_agent` vs `ai_unknown`) → diferente defect-density?
    NO es human-vs-ai (no hay humanos que comparar); es intra-IA. Fuente: SZZ ×
    condición (JSONL-native, sin DB). Ver RAISE-11898.

    Nota: `rai reliability condition` es un sustantivo nuevo — pendiente
    ontology validation (RAISE-10923) antes de merge a main.

    Ejemplos:
        rai reliability condition --since 2026-06-01
        rai reliability condition --since 2026-06-01 --repo /path/to/repo
    """
    from datetime import timedelta

    from raise_cli.quality.classifier import resolve_branch
    from raise_cli.reliability.session_condition import (
        SessionConditionJoin,
        derive_fix_commit_bug_pairs,
    )

    try:
        if since:
            since_date = date.fromisoformat(since)
        else:
            since_date = date.today() - timedelta(days=30)
    except ValueError as exc:
        raise typer.BadParameter(
            f"--since debe ser una fecha ISO (YYYY-MM-DD), recibido: {since!r}"
        ) from exc

    # R2 (S11637.5 QR): resolver el branch UNA sola vez y pasarlo a deriver + join para
    # que numerador y denominador de defect_density sean poblaciones congruentes.
    resolved_branch, _branch_warning = resolve_branch(repo, override=None)

    # S11637.5: numerador SZZ cableado — (fix_sha, bug_key) reales del deriver
    fix_commit_bug_pairs = derive_fix_commit_bug_pairs(
        repo, since_date, branch=resolved_branch
    )
    numerator_wired = len(fix_commit_bug_pairs) > 0

    breakdowns = SessionConditionJoin().join(
        repo_path=repo,
        since_date=since_date,
        fix_commit_bug_pairs=fix_commit_bug_pairs,
        branch=resolved_branch,
        claude_projects_dir=None,
    )

    repo_name = repo.name if repo != Path(".") else "."
    typer.echo(f"\nSession-Condition Reliability ({repo_name}, since {since_date})")
    typer.echo("=" * 60)
    typer.echo(_render_condition_table(breakdowns, numerator_wired=numerator_wired))
    typer.echo("")
    typer.echo(_render_caveats(breakdowns, numerator_wired=numerator_wired))


# ---------------------------------------------------------------------------
# Multi-Carril Attribution helpers
# ---------------------------------------------------------------------------

# Fuente única del caveat GATED de Carril B (ADR-126 invariante 1 / RAISE-11962).
# Usado por el render humano Y por el contrato JSON (--format json) para que el
# marcador de degeneración NUNCA falte en la superficie máquina (AR-1, S11899.5 QR).
_CARRIL_B_GATED_CAVEAT = (
    "Carril B: resolver trailer-based degenerado — precisión 0% en muestra"
    " etiquetada (RAISE-11962); condición pendiente de RAISE-12387."
    " Usar sólo localización, no condición."
)


def _render_single_carril(
    label: str,
    carril_key: str,
    records: list[Any],
) -> str:
    """Renderiza una sección de carril individual."""
    from raise_cli.reliability.multitrack import DefectAttributionRecord

    typed: list[DefectAttributionRecord] = records  # type: ignore[assignment]
    n = len(typed)
    # Fuente única del tier por carril — evita la triple ternaria duplicada
    # entre cabecera y filas (OBS QR: legibilidad / DRY).
    tier = {"region": "medium", "commission": "high", "module": "low"}[carril_key]
    if carril_key == "region":
        header = f"[{label}] {carril_key:<12} tier=medium  {n} defectos   ⚠️  condición GATED (precisión 0%, RAISE-12387)"
    elif carril_key == "commission":
        header = f"[{label}] {carril_key:<12} tier=high    {n} defectos   procedencia: SZZ líneas borradas"
    else:
        header = f"[{label}] {carril_key:<12} tier=low     {n} defectos   correlación NO-causal (archivo tocado por fix)"

    lines = [header]
    for rec in typed:
        cond_str = (
            "gated (RAISE-12387)"
            if carril_key == "region"
            else (rec.condition or f"null | Razón: {rec.reason}")
        )
        lines.append(
            f"  [{carril_key}, tier={tier}]"
            f"  Condición: {cond_str}"
            + (
                f" | Razón: {rec.reason}"
                if rec.reason and rec.condition and carril_key != "region"
                else ""
            )
            + (f" | Commit: {rec.introducer_commit}" if rec.introducer_commit else "")
        )
    return "\n".join(lines)


def _render_carriles(records: list[Any]) -> str:
    """Agrupa records por carril y renderiza cada uno como sección separada.

    Invariante ADR-126: los carriles NUNCA se fusionan.
    """
    from raise_cli.reliability.multitrack import DefectAttributionRecord

    typed: list[DefectAttributionRecord] = records  # type: ignore[assignment]

    by_carril: dict[str, list[DefectAttributionRecord]] = {
        "commission": [],
        "region": [],
        "module": [],
    }
    for rec in typed:
        by_carril[rec.carril].append(rec)

    sections = [
        _render_single_carril("A", "commission", by_carril["commission"]),
        _render_single_carril("B", "region", by_carril["region"]),
        _render_single_carril("C", "module", by_carril["module"]),
    ]
    return "\n\n".join(sections)


def _render_carril_caveats(records: list[Any]) -> str:  # noqa: ARG001
    """Caveats fijos por carril + invariante de no-fusión (ADR-126 invariante 1)."""
    lines = [
        "CAVEATS:",
        f"- ⚠️  {_CARRIL_B_GATED_CAVEAT}",
        "- Carril C: correlación NO-causal — archivo tocado por el fix, no implica autoría.",
        "- Carriles nunca se fusionan ni se promedian en un score único (ADR-126 invariante 1).",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Subcomando: rai reliability attribution
# ---------------------------------------------------------------------------


@reliability_app.command("attribution")
def attribution_command(
    since: Annotated[
        str,
        typer.Option(
            "--since",
            help="Inicio de ventana temporal (YYYY-MM-DD, default: 30 días atrás)",
        ),
    ] = "",
    repo: Annotated[
        Path,
        typer.Option("--repo", "-r", help="Raíz del repositorio", resolve_path=True),
    ] = Path("."),
    format: Annotated[
        str,
        typer.Option("--format", help="Formato de salida: human | json"),
    ] = "human",
) -> None:
    """Multi-Carril Attribution — atribución de defectos por Carril A/B/C (ADR-126).

    Renderiza los 3 carriles de atribución por separado (nunca fusionados):
      [A] commission — SZZ + condición IA (tier=high, fuente canónica)
      [B] region     — add-only, condición GATED/pendiente RAISE-12387 (tier=medium)
      [C] module     — correlación no-causal, archivo tocado por fix (tier=low)

    Invariante honestidad: si condition=None, se muestra la razón. Carril B
    nunca presenta ai_unknown como condición resuelta — marcado explícitamente
    como GATED hasta que RAISE-12387 sustituya el resolver trailer-based.

    Nota: sustantivo `attribution` pendiente ontology validation (RAISE-10923).

    Ejemplos:
        rai reliability attribution --since 2025-01-01
        rai reliability attribution --since 2025-01-01 --format json
    """
    import json as _json
    from datetime import timedelta

    from raise_cli.quality.classifier import resolve_branch
    from raise_cli.reliability.multitrack import MultiTrackAttributor
    from raise_cli.reliability.session_condition import derive_fix_commit_bug_pairs

    try:
        if since:
            since_date = date.fromisoformat(since)
        else:
            since_date = date.today() - timedelta(days=30)
    except ValueError as exc:
        raise typer.BadParameter(
            f"--since debe ser una fecha ISO (YYYY-MM-DD), recibido: {since!r}"
        ) from exc

    resolved_branch, _branch_warning = resolve_branch(repo, override=None)
    # derive_fix_commit_bug_pairs returns (fix_sha, bug_key);
    # MultiTrackAttributor.attribute() expects (bug_key, fix_commit) — swap.
    fix_sha_bug_pairs = derive_fix_commit_bug_pairs(
        repo, since_date, branch=resolved_branch
    )
    bug_fix_pairs = [(bug_key, fix_sha) for fix_sha, bug_key in fix_sha_bug_pairs]

    records = MultiTrackAttributor().attribute(bug_fix_pairs, repo_path=repo)

    if format == "json":
        by_carril: dict[str, list[dict[str, object]]] = {
            "commission": [],
            "region": [],
            "module": [],
        }
        for rec in records:
            payload = rec.model_dump(mode="json")
            if rec.carril == "region":
                # AR-1 (QR): paridad con el render humano — Carril B es GATED.
                # El marcador de degeneración NUNCA debe faltar en la superficie
                # máquina (el consumidor JSON no ve el caveat en pantalla). Se
                # anexa junto al valor crudo de `condition` para que un futuro
                # resolver no-nulo (RAISE-12387) no emita señal sin advertencia.
                payload["gated"] = True
                payload["caveat"] = _CARRIL_B_GATED_CAVEAT
            by_carril[rec.carril].append(payload)
        typer.echo(_json.dumps(by_carril, indent=2, ensure_ascii=False))
        return

    repo_name = repo.name if repo != Path(".") else "."
    typer.echo(f"\nMulti-Carril Attribution ({repo_name}, since {since_date})")
    typer.echo("=" * 60)
    typer.echo("Resumen por carril (NUNCA fusionados):")
    typer.echo("")
    typer.echo(_render_carriles(records))
    typer.echo("")
    typer.echo(_render_carril_caveats(records))
