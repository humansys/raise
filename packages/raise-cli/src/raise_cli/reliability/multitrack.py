"""Emisor multi-carril de atribución de defectos — S11899.1, E11899.

Arquitectura de carriles (nunca fusionados):
  Carril A — "commission" (SZZ + condición de autoría): tier=high
  Carril B — "region" (add-only, pendiente S2): tier=medium
  Carril C — "module" (análisis por módulo, pendiente S3): tier=low

Invariante honestidad: si `condition is None` (condición irrecuperable),
`reason` DEBE contener la explicación. Validator Pydantic garantiza esto.
"""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, model_validator

from raise_cli.telemetry.defect_attribution import resolve_authoring_condition
from raise_cli.telemetry.region_szz import Condition, RegionAttributor
from raise_cli.telemetry.szz import SzzAttributor

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------

Carril = Literal["commission", "region", "module"]
Tier = Literal["high", "medium", "low"]
# Condition imported from telemetry.region_szz (D3 — fuente canónica)


# ---------------------------------------------------------------------------
# Modelo de datos
# ---------------------------------------------------------------------------


class DefectAttributionRecord(BaseModel):
    """Record de atribución de defecto por carril.

    Un record por (fix_commit, introducer_commit, carril).
    Carriles nunca se fusionan — cada uno es un registro independiente.

    tier = procedencia del carril (provenance), NO confidence-band de SZZ.
    condition = autoría IA resuelta (3-valor); None si irrecuperable.
    """

    bug_key: str
    """Jira/tracker key del bug atribuido."""

    fix_commit: str
    """SHA del commit que corrigió el bug."""

    carril: Carril
    """Carril de atribución: commission (A) | region (B) | module (C)."""

    tier: Tier
    """Provenance del carril: high=A, medium=B, low=C."""

    condition: Condition | None
    """Condición de autoría resuelta (3-valor).
    None si irrecuperable — REQUIERE reason no-vacío (invariante honestidad).
    """

    reason: str | None
    """Explicación de por qué condition=None. Obligatorio cuando condition is None."""

    introducer_commit: str | None
    """SHA del commit introductor (None para registros add-only)."""

    confidence: float | None
    """Score SZZ en [0.0, 1.0]. None para add-only."""

    resolved_at: datetime
    """Timestamp de resolución del record."""

    @model_validator(mode="after")
    def _honesty_invariant(self) -> DefectAttributionRecord:
        """condition=None requiere reason no-vacío (invariante honestidad)."""
        if self.condition is None and not (self.reason and self.reason.strip()):
            raise ValueError(
                "condition is None requires a non-empty reason "
                "(honesty invariant: irrecoverable conditions must be explained)"
            )
        return self


# ---------------------------------------------------------------------------
# Carril C — modelo interno y atribuidor por módulo
# ---------------------------------------------------------------------------

_CAVEAT_MODULE = (
    "Atribución por módulo (correlación NO-causal): "
    "archivo tocado por el fix. No implica autoría del defecto."
)


class ModuleAttribution(BaseModel):
    """Resultado interno de Carril C: un archivo tocado por el fix.

    No lleva campo `condition`: Carril C carece de introductor causal, por lo que el
    `DefectAttributionRecord` derivado fija `condition=None` (AC5/D2).
    file_path y caveat obligatorios y no-vacíos: señalizan explícitamente
    correlación no-causal (AC2) — honestidad por construcción.
    """

    file_path: str
    """Ruta del archivo tocado por el fix commit."""

    condition_mix: dict[str, int] = {}
    """Degenerado en fallback per-fix (sin catálogo de defectos)."""

    defect_count: int = 1
    """Conteo de defectos asociados (1 por defecto en fallback per-fix)."""

    tier: Literal["low"] = "low"
    """Provenance de Carril C: siempre low (correlación no-causal)."""

    caveat: str
    """Explicación obligatoria de correlación no-causal (AC2)."""

    @model_validator(mode="after")
    def _caveat_no_vacio(self) -> ModuleAttribution:
        """Caveat obligatorio y no-vacío: Carril C es correlación no-causal."""
        if not (self.caveat and self.caveat.strip()):
            raise ValueError("caveat obligatorio: Carril C es correlacion no-causal")
        return self

    @model_validator(mode="after")
    def _file_path_no_vacio(self) -> ModuleAttribution:
        """file_path obligatorio y no-vacío.

        Un file_path vacío produciría el sentinel ambiguo 'module:' en
        introducer_commit — honestidad por construcción.
        """
        if not (self.file_path and self.file_path.strip()):
            raise ValueError(
                "file_path obligatorio: Carril C atribuye un archivo tocado"
            )
        return self


class ModuleAttributor:
    """Carril C: atribuye archivos (módulos) tocados por el fix commit.

    Retorna un ModuleAttribution por archivo (git show --name-only).
    condition=None siempre — no hay introductor causal (AC5/D2/ADR-126 R2).
    """

    def attribute_module(
        self,
        bug_key: str,
        fix_commit: str,
        repo_path: Path,
    ) -> list[ModuleAttribution]:
        """Lista archivos tocados por fix_commit y emite un ModuleAttribution por archivo.

        Args:
            bug_key: Jira key del bug (informativo, no usado en git).
            fix_commit: SHA del commit que corrige el bug.
            repo_path: Raíz del repositorio git.

        Returns:
            Lista de ModuleAttribution, uno por archivo tocado.
            Vacía si git falla o el commit no toca archivos.
        """
        try:
            result = subprocess.run(
                ["git", "show", "--name-only", "--format=", fix_commit],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            return []
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return [ModuleAttribution(file_path=f, caveat=_CAVEAT_MODULE) for f in files]


# ---------------------------------------------------------------------------
# Mapeo condición 5→3+None
# ---------------------------------------------------------------------------

_CONDITION_MAP: dict[str, Condition] = {
    "interactive": "interactive",
    "batch_agent": "batch_agent",
    "ai_unknown": "ai_unknown",
}

_CONDITION_REASONS: dict[str, str] = {
    "unknown": "trailer presente pero JSONL de sesión no recuperable (irrecoverable)",
    "human": "autoría humana — fuera de scope intra-IA",
}


# ---------------------------------------------------------------------------
# MultiTrackAttributor
# ---------------------------------------------------------------------------


class MultiTrackAttributor:
    """Orquestador de atribución multi-carril (S11899.1-S11899.3).

    Carril A — commission (SZZ + condición de autoría): tier=high.
    Carril B — region (add-only, bloque encapsulante blameable): tier=medium.
    Carril C — module (archivos tocados por el fix, correlación no-causal): tier=low.
    Los carriles son mutuamente excluyentes: A antes que B, B antes que C.
    """

    def attribute(
        self,
        pairs: list[tuple[str, str]],
        repo_path: Path,
        since_date: datetime | None = None,  # noqa: ARG002
    ) -> list[DefectAttributionRecord]:
        """Atribuye una lista de pares (bug_key, fix_commit) por carril.

        Cascada: Carril A (SZZ) → Carril B (RegionAttributor) → Carril C (ModuleAttributor).
        Un fix cubierto por A o B nunca alcanza C (mutuamente excluyente por construcción).

        Args:
            pairs: Lista de (bug_key, fix_commit).
            repo_path: Raíz del repositorio git.
            since_date: Filtro de fecha (reservado, no usado aún).

        Returns:
            Lista de DefectAttributionRecord, uno por (par × introductor/archivo).
            Carril C emite condition=None + caveat (correlación no-causal) por archivo.
        """
        szz = SzzAttributor()
        records: list[DefectAttributionRecord] = []
        now = datetime.now(tz=UTC)

        for bug_key, fix_commit in pairs:
            intro_results = szz.attribute_introducer(fix_commit, repo_path)

            if not intro_results:
                # add-only: SZZ sin introductor → Carril B (RegionAttributor)
                region_results = RegionAttributor().attribute_region(
                    fix_commit, repo_path
                )

                if region_results:
                    for rr in region_results:
                        cond = rr.dominant_condition
                        region_reason: str | None = None
                        if cond is None:
                            region_reason = str(
                                rr.evidence.get("dominant_reason")
                                or "Carril B: condición irrecuperable"
                            )
                            if not region_reason.strip():
                                region_reason = "Carril B: sin blamed lines"
                        records.append(
                            DefectAttributionRecord(
                                bug_key=bug_key,
                                fix_commit=fix_commit,
                                carril="region",
                                tier="medium",  # Carril B fijo — nunca "high"
                                condition=cond,
                                reason=region_reason,
                                introducer_commit=rr.introducer_commit,
                                confidence=None,
                                resolved_at=now,
                            )
                        )
                else:
                    # A y B vacíos → Carril C (ModuleAttributor): correlación por módulo
                    for ma in ModuleAttributor().attribute_module(
                        bug_key, fix_commit, repo_path
                    ):
                        records.append(
                            DefectAttributionRecord(
                                bug_key=bug_key,
                                fix_commit=fix_commit,
                                carril="module",
                                tier="low",
                                condition=None,
                                reason=ma.caveat,
                                introducer_commit=f"module:{ma.file_path}",
                                confidence=None,
                                resolved_at=now,
                            )
                        )
                continue

            for intro in intro_results:
                attr_rec = resolve_authoring_condition(intro, repo_path=repo_path)
                raw = attr_rec.authoring_condition
                condition = _CONDITION_MAP.get(raw)
                reason: str | None = (
                    _CONDITION_REASONS.get(raw) if condition is None else None
                )
                if condition is None and reason is None:
                    # Fallback para condición no reconocida
                    reason = f"condición no reconocida: {raw!r}"
                records.append(
                    DefectAttributionRecord(
                        bug_key=bug_key,
                        fix_commit=fix_commit,
                        carril="commission",
                        tier="high",
                        condition=condition,
                        reason=reason,
                        introducer_commit=intro.introducer_commit,
                        confidence=intro.confidence,
                        resolved_at=now,
                    )
                )

        return records
