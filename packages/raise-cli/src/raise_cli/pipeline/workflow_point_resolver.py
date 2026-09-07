"""Workflow-point resolver for standalone skill transitions (RAISE-16990, B4).

Translates a lifecycle position string such as ``after:story:implement`` into
the ``target_status`` declared in the matching pipeline YAML, then passes that
status to ``apply_phase_transition``.  Skills never see or hardcode a status
name — they name a position, the engine resolves the status.

Notation:
    ``after:<pipeline>:<phase>``  — target_status OF <phase> in <pipeline>
    ``before:<pipeline>:<phase>`` — target_status of the phase immediately
                                    preceding <phase> in <pipeline> that has
                                    a non-None target_status
"""

from __future__ import annotations

from raise_cli.pipeline.loader import PipelineLoader
from raise_core.workflow.models import PhaseDefinition


class WorkflowPointError(ValueError):
    """Raised when a workflow point cannot be resolved to a target_status.

    Always includes a human-readable message naming the invalid token and,
    when possible, listing the valid alternatives.
    """


def resolve_target_status_from_point(point: str, loader: PipelineLoader) -> str:
    """Resolve a workflow point string to a ``target_status`` slug.

    Args:
        point: Lifecycle position in ``{direction}:{pipeline}:{phase}`` form.
               Direction must be ``after`` or ``before``.
        loader: Configured PipelineLoader used to load the pipeline definition.

    Returns:
        The ``target_status`` slug declared in the pipeline YAML.

    Raises:
        WorkflowPointError: When the point is malformed, the pipeline does not
            exist, the named phase is absent, or the phase has no target_status.
    """
    direction, pipeline_name, phase_id = _parse_point(point)
    phases = _load_phases(pipeline_name, loader, point)

    if direction == "after":
        return _resolve_after(phase_id, phases, pipeline_name, point)
    return _resolve_before(phase_id, phases, pipeline_name, point)


# ── private helpers ──────────────────────────────────────────────────────────


def _parse_point(point: str) -> tuple[str, str, str]:
    """Parse and validate the three-part workflow point string."""
    parts = point.split(":")
    if len(parts) != 3:
        raise WorkflowPointError(
            f"Invalid workflow point {point!r}: expected "
            f"'{{direction}}:{{pipeline}}:{{phase}}' (e.g. 'after:story:implement')"
        )
    direction, pipeline_name, phase_id = parts
    if direction not in ("after", "before"):
        raise WorkflowPointError(
            f"Invalid direction {direction!r} in workflow point {point!r}: "
            f"must be 'after' or 'before'"
        )
    return direction, pipeline_name, phase_id


def _load_phases(
    pipeline_name: str, loader: PipelineLoader, point: str
) -> list[PhaseDefinition]:
    """Load and return phases from the named pipeline."""
    try:
        return list(loader.load(pipeline_name).phases)
    except Exception as exc:  # noqa: BLE001
        raise WorkflowPointError(
            f"Pipeline {pipeline_name!r} not found while resolving workflow point "
            f"{point!r}: {exc}"
        ) from exc


def _valid_phase_ids(phases: list[PhaseDefinition]) -> str:
    return ", ".join(p.id for p in phases)


def _resolve_after(
    phase_id: str,
    phases: list[PhaseDefinition],
    pipeline_name: str,
    point: str,
) -> str:
    for phase in phases:
        if phase.id == phase_id:
            if phase.target_status is None:
                raise WorkflowPointError(
                    f"Phase {phase_id!r} in pipeline {pipeline_name!r} has no "
                    f"target_status — cannot resolve workflow point {point!r}"
                )
            return phase.target_status
    raise WorkflowPointError(
        f"Phase {phase_id!r} not found in pipeline {pipeline_name!r} while "
        f"resolving {point!r}. Valid phases: {_valid_phase_ids(phases)}"
    )


def _resolve_before(
    phase_id: str,
    phases: list[PhaseDefinition],
    pipeline_name: str,
    point: str,
) -> str:
    target_idx = next((i for i, p in enumerate(phases) if p.id == phase_id), None)
    if target_idx is None:
        raise WorkflowPointError(
            f"Phase {phase_id!r} not found in pipeline {pipeline_name!r} while "
            f"resolving {point!r}. Valid phases: {_valid_phase_ids(phases)}"
        )
    if target_idx == 0:
        raise WorkflowPointError(
            f"No phase before {phase_id!r} in pipeline {pipeline_name!r} — "
            f"cannot resolve 'before' point {point!r}"
        )
    for i in range(target_idx - 1, -1, -1):
        ts = phases[i].target_status
        if ts is not None:
            return ts
    raise WorkflowPointError(
        f"No phase before {phase_id!r} in pipeline {pipeline_name!r} has a "
        f"target_status — cannot resolve workflow point {point!r}"
    )
