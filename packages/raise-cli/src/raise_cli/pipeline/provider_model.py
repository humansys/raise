"""Provider model resolver — translate RaiSE capability tiers to runtime model IDs.

Loads ``.raise/provider_models.yaml`` and exposes ``resolve_provider_model()`` so
that pipeline/fleet dispatch can emit model IDs a non-Claude runtime actually
understands (e.g. ``k3-256k`` for Kimi instead of the abstract ``fable`` tier).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

from raise_cli.pipeline.skill_model import VALID_MODELS

logger = logging.getLogger(__name__)

_CONFIG_RELATIVE_PATH = Path(".raise") / "provider_models.yaml"


def resolve_provider_model(
    tier: str,
    runtime: str | None = None,
    project_root: Path | None = None,
) -> str:
    """Translate a RaiSE capability tier to a runtime-specific model ID.

    Args:
        tier: Capability tier (haiku, sonnet, fable, opus).
        runtime: Target runtime identifier (e.g. ``kimi``, ``codex``, ``claude``).
            When ``None``, resolved from ``RAISE_AGENT_RUNTIME`` env var or
            agent-session detection.
        project_root: Project root used to locate ``.raise/provider_models.yaml``.
            Defaults to the current working directory.

    Returns:
        The model ID declared for ``(runtime, tier)`` in provider_models.yaml,
        or ``tier`` itself when no mapping exists (fail-open).
    """
    tier = tier.strip().lower()
    if tier not in VALID_MODELS:
        logger.warning(
            "Provider model resolver received unknown tier %r — returning as-is",
            tier,
        )
        return tier

    runtime = _resolve_runtime(runtime)
    if runtime is None:
        return tier

    config = _load_config(project_root)
    mapping = config.get(runtime) or config.get(runtime.lower())
    if not isinstance(mapping, dict):
        logger.debug("No provider mapping for runtime %r", runtime)
        return tier

    model_id = mapping.get(tier)
    if model_id is None:
        logger.debug("No mapping for tier %r under runtime %r", tier, runtime)
        return tier

    return str(model_id).strip()


def _resolve_runtime(runtime: str | None) -> str | None:
    """Resolve runtime from explicit arg, env var, or agent session detection."""
    if runtime is not None:
        return runtime.strip().lower() or None

    explicit = os.environ.get("RAISE_AGENT_RUNTIME", "").strip()
    if explicit:
        return explicit.lower()

    # Fall back to the same discovery logic used for session/runtime correlation.
    # Imported lazily to avoid circular imports at module load time.
    try:
        from raise_cli._agent_session import discover_agent_runtime

        discovered = discover_agent_runtime()
        if discovered and discovered != "unknown":
            return discovered.lower()
    except Exception:  # noqa: BLE001
        logger.debug("Runtime discovery failed", exc_info=True)

    return None


def _load_config(project_root: Path | None) -> dict[str, Any]:
    """Best-effort load of <project_root>/.raise/provider_models.yaml."""
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / _CONFIG_RELATIVE_PATH
    if not config_path.is_file():
        return {}

    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    try:
        data: object = yaml.safe_load(content)
    except yaml.YAMLError:
        return {}

    if not isinstance(data, dict):
        return {}
    return data
