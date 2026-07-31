"""Reaper de containers docker raise-runner huérfanos — S10841.2 (RAISE-10965).

Patrón: fuente de verdad externa (daemon docker) → reap lazy → devuelve ids reapeados.
Calca el patrón mental de worker_budget.acquire() (PAT-E-9366): sin ledger propio.

Contrato compartido con pipeline/executor.py: label ``raise-runner=1``
(_build_docker_args:347-350). El reaper lo consume solo — NUNCA modifica executor.py.
"""

from __future__ import annotations

import logging
import re
import subprocess
from datetime import UTC, datetime, timedelta

log = logging.getLogger(__name__)

_LABEL_FILTER = "label=raise-runner=1"
_NANO_RE = re.compile(r"(\.\d{6})\d+")  # truncar nano → micro (6 dígitos)


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------


def _list_runner_containers() -> list[str]:
    """Enumera ids de containers con label raise-runner=1.

    Devuelve lista vacía si docker ausente/no-permiso. Nunca lanza.
    """
    try:
        result = subprocess.run(  # noqa: S603, S607
            ["docker", "ps", "--filter", _LABEL_FILTER, "-q"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, PermissionError) as exc:
        log.warning("docker no disponible o sin acceso al daemon: %s", exc)
        raise  # re-raise para que reap_idle lo capture en su try/except

    if result.returncode != 0:
        log.warning("docker ps code %d: %s", result.returncode, result.stderr)
        return []

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines


def _inspect_started_at(container_id: str) -> datetime | None:
    """Lee .State.StartedAt de un container. Devuelve None si no parseable.

    Docker 29.x emite RFC3339Nano (9 dígitos fraccionarios). Python fromisoformat
    solo acepta hasta 6 → truncamos con _NANO_RE y sustituimos 'Z' por '+00:00'.
    """
    try:
        result = subprocess.run(  # noqa: S603, S607
            [
                "docker",
                "inspect",
                container_id,
                "--format",
                "{{.State.StartedAt}}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except (FileNotFoundError, PermissionError) as exc:
        log.warning("docker inspect falló para %s: %s", container_id, exc)
        return None

    if result.returncode != 0 or not result.stdout.strip():
        log.debug("docker inspect sin salida para %s", container_id)
        return None

    raw_ts = result.stdout.strip()
    # Truncar nanosegundos a microsegundos (6 dígitos fraccionarios)
    normalized = _NANO_RE.sub(r"\1", raw_ts)
    # Python fromisoformat entiende +00:00 pero no 'Z'
    normalized = normalized.replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        log.debug("StartedAt no parseable para %s: %r", container_id, raw_ts)
        return None


def _force_remove(container_id: str) -> bool:
    """Ejecuta docker rm -f. Retorna True si el container fue removido (o ya no existía).

    Race tolerado: si el container desapareció entre inspect y rm (CalledProcessError
    con "No such container" en stderr), se cuenta como reapeado (ya no existe = éxito).
    Otros fallos: retorna False — el container podría seguir vivo, no se cuenta.
    """
    try:
        subprocess.run(  # noqa: S603, S607
            ["docker", "rm", "-f", container_id],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr or ""
        if "No such container" in stderr:
            log.debug("_force_remove: %s ya no existe (race tolerado)", container_id)
            return True
        log.debug("_force_remove: rm falló para %s: %s", container_id, exc)
        return False
    except (FileNotFoundError, PermissionError) as exc:
        log.debug("_force_remove ignoró error para %s: %s", container_id, exc)
        return False


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def reap_idle(
    max_age: timedelta = timedelta(minutes=30),
    *,
    now: datetime | None = None,
) -> list[str]:
    """Force-remove orphan raise-runner containers older than max_age.

    Returns short ids reaped. Never raises: docker absent/EACCES → [] + warning.
    Source of truth: docker daemon (.State.StartedAt), not a local ledger.

    Args:
        max_age: Antigüedad máxima permitida. Default 30 min (≫ timeout 300s del
                 executor → nunca mata un job en vuelo).
        now: Momento de referencia para calcular antigüedad. Inyectable para tests.
             Defaults to datetime.now(UTC).
    """
    if now is None:
        now = datetime.now(UTC)

    try:
        container_ids = _list_runner_containers()
    except (FileNotFoundError, PermissionError, subprocess.CalledProcessError) as exc:
        log.warning("reap_idle: no se pudo enumerar containers: %s", exc)
        return []

    reaped: list[str] = []
    for cid in container_ids:
        started_at = _inspect_started_at(cid)
        if started_at is None:
            log.debug("reap_idle: skip %s — StartedAt no disponible/parseable", cid)
            continue

        # Asegurar que now y started_at son comparables (ambos aware)
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=UTC)

        age = now - started_at
        if age > max_age:
            log.info("reap_idle: remove %s (age=%s > max_age=%s)", cid, age, max_age)
            if _force_remove(cid):
                reaped.append(cid)
        else:
            log.debug("reap_idle: skip %s (age=%s ≤ max_age=%s)", cid, age, max_age)

    return reaped
