"""Session-Condition Join — join commit × condición de sesión sobre sustrato SZZ.

Construye denominador (n_changes por condición) y numerador (defectos SZZ) para
producir defect_density por condición de sesión. Opción A: fuente SZZ, eje
session_type, model/fill_band = None+razón donde dato no disponible.

Diseño (S11637.3, Opción A):
- JSONL-native, SIN persistencia SQLite (honra RAISE-8204 / E8204).
- Reusa helpers de defect_attribution (lógica, no persistencia).
- model/fill_band = None+razón cuando irrecuperables (nunca se fabrican).
- Prevalencia ai_unknown reportada cuando >= UNKNOWN_CAVEAT_THRESHOLD.

Módulos consumidos en read-only (NO modificados):
  telemetry/szz.py, telemetry/defect_attribution.py,
  telemetry/session_tokens.py, reliability/lens.py,
  reliability/rollup.py, reliability/models.py.
"""

from __future__ import annotations

import logging
import subprocess
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

# Reuso sin reimplementar (anti-clon AG2, M2): parse_commits, classify, resolve_branch
from raise_cli.quality.classifier import classify, parse_commits, resolve_branch

# R3 + M2: fuentes canónicas de trailer regex y regex de clave de bug (szz)
from raise_cli.telemetry.szz import (
    _TRAILER_RE,  # pyright: ignore[reportPrivateUsage]
)

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes exportadas
# ---------------------------------------------------------------------------

N_THRESHOLD: int = 5
"""Mínimo de cambios para calcular defect_density. n < N_THRESHOLD → None+razón."""

UNKNOWN_CAVEAT_THRESHOLD: float = 0.30
"""Proporción de ai_unknown que dispara el caveat de prevalencia."""


# ---------------------------------------------------------------------------
# Modelos de datos (Pydantic, inmutables como clave de dict)
# ---------------------------------------------------------------------------


class ConditionKey(BaseModel, frozen=True):
    """Clave que identifica una condición de sesión para agrupar cambios.

    Frozen=True: hashable, usable como clave de dict/set.
    fill_band: SIEMPRE None en v1 (context-fill no instrumentado).
    model: None+razón si trailer URL-form o JSONL purgado (irrecuperable).
    """

    model: str | None
    """Modelo Claude extraído del JSONL (most-common). None si irrecuperable."""

    fill_band: str | None
    """Banda de context-fill. SIEMPRE None en v1 — sin fuente instrumentada."""

    session_type: Literal["human", "interactive", "batch_agent", "ai_unknown"]
    """Condición de generación del commit.

    En raise-commons (100%-IA) los valores producidos son intra-IA:
    - interactive: trailer + JSONL, sin markers de batch
    - batch_agent: trailer + JSONL + markers de batch
    - ai_unknown: IA con condición irrecuperable (sin trailer / URL-form / JSONL purgado)
    'human' se conserva en el enum pero NUNCA se enruta sin evidencia POSITIVA de
    autoría humana (no instrumentada). Ver RAISE-11898 (corrección de categoría)."""


class ConditionBreakdown(BaseModel):
    """Métricas de confiabilidad para una condición de sesión.

    Semántica del numerador (R2, S11637.3 AR):
    - n_defects = número de bugs DISTINTOS (fix_sha, bug_key) cuyo commit-introducer
      pertenece a esta condición. Un bug con N introducers solo suma 1.
    - defect_density = n_defects / n_changes, clampeado a [0.0, 1.0].
      Puede exceder 1.0 sin clamp si introducers caen fuera de la ventana (denominador
      chico); en ese caso se clampea y se documenta en `reason`.
    - Solo introducers con confidence >= confidence_threshold (default 0.6) se cuentan
      (alineado con el lens, que filtra al mismo umbral).

    n_changes siempre visible (denominador explícito, lección S11487.2).
    """

    condition: ConditionKey
    """Condición de sesión a la que pertenece este breakdown."""

    defect_density: float | None
    """Densidad de defectos en [0.0, 1.0]. None si n_changes < N_THRESHOLD."""

    n_changes: int
    """Denominador: total de commits (sin merge-commits) en la ventana para esta condición."""

    n_defects: int
    """Numerador: bugs distintos (fix_sha, bug_key) atribuidos a esta condición por SZZ."""

    confidence: Literal["high", "medium", "low"] | None
    """Banda de confianza. None cuando n < N_THRESHOLD."""

    reason: str | None
    """Razón honesta: sample too small, density clamped, u otras condiciones excepcionales."""

    proxy_caveat: str | None
    """Caveat de prevalencia ai_unknown cuando >= UNKNOWN_CAVEAT_THRESHOLD."""


# ---------------------------------------------------------------------------
# Resolución de condición (commit → ConditionKey)
# ---------------------------------------------------------------------------


def _get_commit_body(commit_sha: str, repo_path: Path) -> str:
    """Obtener el cuerpo completo del commit (formato %B)."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%B", commit_sha],
            capture_output=True,
            text=True,
            cwd=str(repo_path),
            timeout=15,
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, OSError):
        pass
    return ""


def resolve_condition(
    commit_sha: str,
    repo_path: Path,
    claude_projects_dir: Path | None = None,
    *,
    _session_cache: dict[str, Path | None] | None = None,
) -> ConditionKey:
    """Clasificar un commit SHA en su ConditionKey.

    Rutas de resolución:
    - Sin trailer → ai_unknown, model/fill=None (repo 100%-IA: ausencia de
      trailer = IA pre-instrumentación, NO humano — RAISE-11898)
    - Trailer presente + JSONL encontrado + markers batch → batch_agent
    - Trailer presente + JSONL encontrado + sin markers → interactive, model extraído
    - Trailer presente + JSONL no encontrado (URL-form / purgado) → ai_unknown, model=None

    fill_band: SIEMPRE None en v1 (sin fuente instrumentada).

    Args:
        commit_sha: SHA del commit a clasificar.
        repo_path: Raíz del repositorio git.
        claude_projects_dir: Directorio de proyectos CC (default: ~/.claude/projects).

    Returns:
        ConditionKey con session_type, model (o None+razón), fill_band=None.
    """
    from raise_cli.telemetry.defect_attribution import (
        _find_session_jsonl,  # pyright: ignore[reportPrivateUsage]
        _is_batch_agent_session,  # pyright: ignore[reportPrivateUsage]
    )
    from raise_cli.telemetry.session_tokens import parse_totals

    if claude_projects_dir is None:
        claude_projects_dir = Path.home() / ".claude" / "projects"

    body = _get_commit_body(commit_sha, repo_path)
    match = _TRAILER_RE.search(body)

    if not match:
        # Ruta (a): sin trailer → ai_unknown (NO human).
        # Corrección RAISE-11898 (4ª falsación gemba): raise-commons es 100%-IA.
        # La ausencia de trailer NO implica autoría humana — implica código IA
        # que precede la estandarización del trailer (o sesión purgada). El
        # default honesto es ai_unknown (IA, condición irrecuperable). 'human'
        # nunca se enruta sin evidencia POSITIVA de autoría humana (no instrumentada).
        return ConditionKey(
            model=None,
            fill_band=None,
            session_type="ai_unknown",
        )

    session_id = match.group(1).strip()

    # H-1: evitar re-escanear JSONL para el mismo session_id (incluido None para
    # URL-form irresolubles — no re-escanear los 4274 archivos por commit).
    if _session_cache is not None and session_id in _session_cache:
        jsonl_path = _session_cache[session_id]
    else:
        jsonl_path = _find_session_jsonl(session_id, claude_projects_dir)
        if _session_cache is not None:
            _session_cache[session_id] = jsonl_path

    if jsonl_path is None:
        # Ruta (d): trailer presente pero JSONL irrecuperable
        # URL-form (session_01…) no mapea a JSONL UUID — irrecuperable
        return ConditionKey(
            model=None,
            fill_band=None,
            session_type="ai_unknown",
        )

    # Rutas (b)/(c): JSONL encontrado
    model: str | None = None
    totals = parse_totals(jsonl_path)
    if totals is not None and totals.model and totals.model != "unknown":
        model = totals.model

    if _is_batch_agent_session(jsonl_path):
        return ConditionKey(
            model=model,
            fill_band=None,
            session_type="batch_agent",
        )

    return ConditionKey(
        model=model,
        fill_band=None,
        session_type="interactive",
    )


# ---------------------------------------------------------------------------
# SessionConditionJoin — denominador + numerador
# ---------------------------------------------------------------------------


def _build_breakdown(
    key: ConditionKey,
    n_changes: int,
    n_defects: int,
) -> ConditionBreakdown:
    """Construir un ConditionBreakdown puro (sin git, testeable unitariamente).

    n < N_THRESHOLD → defect_density=None + reason con el n real.
    n >= N_THRESHOLD → defect_density = min(1.0, n_defects / n_changes).

    R2: density clampeada a [0.0, 1.0]; si n_defects > n_changes el clamp se
    documenta en reason (introducer fuera de la ventana temporal del denominador).
    """
    if n_changes < N_THRESHOLD:
        return ConditionBreakdown(
            condition=key,
            defect_density=None,
            n_changes=n_changes,
            n_defects=n_defects,
            confidence=None,
            reason=f"sample too small (n={n_changes})",
            proxy_caveat=None,
        )

    raw_density = n_defects / n_changes if n_changes > 0 else 0.0
    density = min(1.0, raw_density)
    clamped = n_defects > n_changes

    confidence: Literal["high", "medium", "low"]
    if n_changes >= 50:
        confidence = "high"
    elif n_changes >= 10:
        confidence = "medium"
    else:
        confidence = "low"

    reason = (
        (
            f"density clamped to 1.0 (n_defects={n_defects} > n_changes={n_changes}; "
            "introducers may fall outside the observation window)"
        )
        if clamped
        else None
    )

    return ConditionBreakdown(
        condition=key,
        defect_density=density,
        n_changes=n_changes,
        n_defects=n_defects,
        confidence=confidence,
        reason=reason,
        proxy_caveat=None,
    )


def _apply_caveats(
    breakdowns: list[ConditionBreakdown],
    unknown_threshold: float = UNKNOWN_CAVEAT_THRESHOLD,
) -> list[ConditionBreakdown]:
    """Aplicar caveats de prevalencia ai_unknown (función pura).

    Si n_changes(ai_unknown) / total_n_changes >= unknown_threshold, el breakdown
    ai_unknown recibe un proxy_caveat con el porcentaje.

    Args:
        breakdowns: Lista de ConditionBreakdown (pre-caveat).
        unknown_threshold: Umbral de prevalencia para disparar el caveat.

    Returns:
        Nueva lista con proxy_caveat aplicado donde corresponde.
    """
    total_n = sum(b.n_changes for b in breakdowns)
    if total_n == 0:
        return breakdowns

    result: list[ConditionBreakdown] = []
    for b in breakdowns:
        if b.condition.session_type == "ai_unknown":
            fraction = b.n_changes / total_n
            if fraction >= unknown_threshold:
                pct = round(fraction * 100)
                caveat = (
                    f"{pct}% de los cambios son ai_unknown: trailer URL-form no mapea a "
                    f"log JSONL → model/tipo-fino irrecuperable. "
                    f"Credibilidad limitada para conjeturas finas."
                )
                result.append(b.model_copy(update={"proxy_caveat": caveat}))
            else:
                result.append(b)
        else:
            result.append(b)

    return result


def _resolve_with_cache(
    sha: str,
    *,
    repo_path: Path,
    claude_projects_dir: Path | None,
    sha_cache: dict[str, ConditionKey],
    session_cache: dict[str, Path | None],
) -> ConditionKey:
    """Resolver commit_sha con sha_cache y session_cache (H-1 memoización).

    Módulo-nivel (no closure) para no incrementar la complejidad ciclomática
    de SessionConditionJoin.join.
    """
    if sha not in sha_cache:
        sha_cache[sha] = resolve_condition(
            sha,
            repo_path=repo_path,
            claude_projects_dir=claude_projects_dir,
            _session_cache=session_cache,
        )
    return sha_cache[sha]


# ---------------------------------------------------------------------------
# Deriver del numerador (S11637.5 — RAISE-11670)
# ---------------------------------------------------------------------------


def derive_fix_commit_bug_pairs(
    repo_path: Path,
    since_date: date,
    *,
    branch: str | None = None,
    escaped_only: bool = True,
    key_prefix: str = "RAISE-",
) -> list[tuple[str, str]]:
    """Derivar (fix_sha, bug_key) reales para alimentar SessionConditionJoin.join.

    Reusa parse_commits + classify (quality/classifier) para obtener candidatos.

    - Incluye commits con type in {fix, bug}.
    - escaped_only=True → solo defect_class == "escaped" (excluye rework in-process:
      AR/QR/CI/lint churn NO son defectos escapados). Alinea con el lens.
    - bug_key desde ticket_refs filtrado por key_prefix; sin match → omitido
      (no se fabrica clave) + skipped++ emitido en logging.debug.
    - Un fix con múltiples claves del prefix → se toma la primera (lexicográfica
      por construcción — ticket_refs está sorted).

    Args:
        repo_path: Raíz del repositorio git.
        since_date: Inicio de la ventana temporal.
        branch: Override del branch de integración (None → manifest o current branch).
        escaped_only: Si True (default), excluye rework_in_process.
        key_prefix: Prefijo de clave rastreable (default "RAISE-").

    Returns:
        Lista de tuplas (fix_sha, bug_key) para consumir en SessionConditionJoin.join.
    """
    days_since = (date.today() - since_date).days
    resolved_branch, branch_warning = resolve_branch(repo_path, override=branch)
    if branch_warning:
        _log.debug("derive_fix_commit_bug_pairs branch fallback: %s", branch_warning)

    commits = parse_commits(repo_path, days_since, resolved_branch)

    pairs: list[tuple[str, str]] = []
    skipped = 0

    for commit in commits:
        # Filtrar por tipo (solo fix y bug — los candidatos a defecto)
        if commit.type not in {"fix", "bug"}:
            continue

        # Filtrar por clase de defecto cuando escaped_only=True
        verdict = classify(commit)
        if escaped_only and verdict.defect_class != "escaped":
            continue

        # Extraer clave rastreable desde ticket_refs (populado por _TICKET_RE en classifier).
        # _TICKET_RE captura RAISE-N en cualquier posición del subject (incluidos paréntesis)
        # → ticket_refs ya contiene todas las claves del prefijo por defecto.
        bug_keys = [r for r in commit.ticket_refs if r.startswith(key_prefix)]

        if not bug_keys:
            # Fix sin clave rastreable → omitido (honestidad por construcción, no se fabrica)
            skipped += 1
            continue

        # Un fix puede referenciar múltiples claves — se toma la primera del prefix
        pairs.append((commit.sha, bug_keys[0]))

    if skipped:
        _log.debug(
            "derive: %d fix-commit(s) sin clave %r omitidos (honestidad: no se fabrica clave)",
            skipped,
            key_prefix,
        )

    return pairs


class SessionConditionJoin:
    """Join commit × condición sobre sustrato SZZ (JSONL-native, sin DB).

    Denominador: recorre git log de la ventana → count por ConditionKey.
    Numerador: SzzAttributor.attribute_introducer sobre fix-commits → count por ConditionKey.
    """

    def join(
        self,
        *,
        repo_path: Path,
        since_date: date,
        fix_commit_bug_pairs: list[tuple[str, str]],
        branch: str | None = None,
        claude_projects_dir: Path | None = None,
        confidence_threshold: float = 0.6,
    ) -> list[ConditionBreakdown]:
        """Calcular defect_density por condición de sesión.

        Semántica del numerador (R1 + R2, S11637.3 AR):
        - Solo introducers con ir.confidence >= confidence_threshold se cuentan
          (alineado con el lens que filtra al mismo umbral por defecto 0.6).
        - n_defects = bugs DISTINTOS por (fix_sha, bug_key): un bug con N introducers
          cuenta como 1 en la condición (no N). Evita sesgo por blame-scatter.
        - defect_density clampeada a [0.0, 1.0]; si n_defects > n_changes se
          documenta en reason (R2: introducer fuera de la ventana de observación).

        Semántica de branch (R2, S11637.5 QR):
        - El denominador (git log) y el numerador (pares del deriver) deben mirar
          el MISMO branch para que defect_density sea semánticamente bien formada.
        - El caller (CLI) debe resolver el branch una sola vez (resolve_branch) y
          pasarlo tanto al deriver como aquí. branch=None preserva el comportamiento
          previo (HEAD del worktree).

        Args:
            repo_path: Raíz del repositorio git.
            since_date: Inicio de la ventana temporal (git log --since, --no-merges).
            fix_commit_bug_pairs: Lista de (fix_sha, bug_key) para SZZ.
            branch: Branch explícito para el denominador (None → HEAD del worktree).
                    Debe coincidir con el branch usado en derive_fix_commit_bug_pairs.
            claude_projects_dir: Override del directorio de proyectos CC.
            confidence_threshold: Umbral de confianza SZZ (default 0.6, alineado con lens).

        Returns:
            Lista de ConditionBreakdown (una entrada por condición presente).
            n_changes siempre poblado; defect_density=None cuando n<N_THRESHOLD.
        """
        from raise_cli.telemetry.szz import SzzAttributor

        denominator: dict[ConditionKey, int] = {}
        # R2: set de (fix_sha, bug_key) por condición para contar bugs distintos
        numerator_bugs: dict[ConditionKey, set[tuple[str, str]]] = {}

        # H-1: caches de corrida para eliminar escaneos JSONL redundantes.
        #   _session_cache: session_id → Path|None (incluye None para URL-form,
        #     que nunca mapean a JSONL — resultado cacheado para no re-escanear).
        #   _sha_cache: commit_sha → ConditionKey (evita re-resolver commits que
        #     aparecen tanto en el denominador como en el numerador como introducers).
        _session_cache: dict[str, Path | None] = {}
        _sha_cache: dict[str, ConditionKey] = {}

        # 1. Denominador: recorrer commits de la ventana (R4: --no-merges excluye
        #    merge-commits que contaminarían el bucket ai_unknown con metadatos de merge).
        #    Se usa el mismo branch que el deriver para que numerador y denominador
        #    sean poblaciones congruentes (R2, S11637.5 QR).
        since_str = since_date.isoformat()
        git_log_cmd = [
            "git",
            "log",
            "--format=%H",
            f"--since={since_str}",
            "--no-merges",
        ]
        if branch:
            git_log_cmd.append(branch)
        try:
            result = subprocess.run(
                git_log_cmd,
                capture_output=True,
                text=True,
                cwd=str(repo_path),
                timeout=60,
                check=True,
            )
            all_shas = [s.strip() for s in result.stdout.splitlines() if s.strip()]
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            all_shas = []

        for sha in all_shas:
            key = _resolve_with_cache(
                sha,
                repo_path=repo_path,
                claude_projects_dir=claude_projects_dir,
                sha_cache=_sha_cache,
                session_cache=_session_cache,
            )
            denominator[key] = denominator.get(key, 0) + 1

        # 2. Numerador: SZZ sobre fix-commits
        szz = SzzAttributor()
        for fix_sha, bug_key in fix_commit_bug_pairs:
            try:
                introducer_results = szz.attribute_introducer(
                    fix_commit=fix_sha, repo_path=repo_path
                )
            except (ValueError, subprocess.CalledProcessError):
                continue

            for ir in introducer_results:
                # R1: filtrar por confianza (alineado con el lens)
                if ir.confidence < confidence_threshold:
                    continue
                intro_sha = ir.introducer_commit
                intro_key = _resolve_with_cache(
                    intro_sha,
                    repo_path=repo_path,
                    claude_projects_dir=claude_projects_dir,
                    sha_cache=_sha_cache,
                    session_cache=_session_cache,
                )
                # R2: añadir par (fix_sha, bug_key) al set del introducer para contar distintos
                if intro_key not in numerator_bugs:
                    numerator_bugs[intro_key] = set()
                numerator_bugs[intro_key].add((fix_sha, bug_key))

        # Convertir set a conteo de bugs distintos
        numerator = {k: len(v) for k, v in numerator_bugs.items()}

        # 3. Merge → ConditionBreakdown
        all_keys = set(denominator.keys()) | set(numerator.keys())
        if not all_keys:
            return []

        breakdowns = [
            _build_breakdown(
                key=k,
                n_changes=denominator.get(k, 0),
                n_defects=numerator.get(k, 0),
            )
            for k in all_keys
        ]

        # 4. Aplicar caveats de prevalencia
        return _apply_caveats(breakdowns)
