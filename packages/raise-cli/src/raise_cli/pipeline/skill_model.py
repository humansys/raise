"""Layered model routing resolver for skills (RAISE-13920).

Precedence, highest to lowest:
    1. Per-skill env var: ``RAISE_SKILL_MODEL_<SKILL>`` (skill name upper,
       ``-`` -> ``_``, e.g. ``epic-design`` -> ``RAISE_SKILL_MODEL_EPIC_DESIGN``).
    2. Global env var: ``RAISE_PIPELINE_MODEL``.
    3. Repo config phase-path key, e.g. ``skills[epic.design.adversarial]``.
    4. Repo config skill key ``skills[<skill_name>]``. ``project_root`` is derived as
       ``skill_base.parent.parent`` (``skill_base`` is ``<root>/.claude/skills``).
    5. Pipeline phase YAML ``model:`` field.
    6. ``SKILL.md`` frontmatter ``model:`` field (the original behavior).
    7. Repo config ``default:`` key in the same yaml file, if present —
       final catch-all only.
    8. ``None``.

Every candidate is validated against ``VALID_MODELS``. An invalid value at
any layer is logged (``logger.warning``) and treated as absent, falling
through to the next layer — it does NOT abort resolution to ``None``.

This lets developers change a skill's pipeline model without an MR or a
skill-sync: set an env var, or add an entry to
``.raise/skill_models.yaml``.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

VALID_MODELS: frozenset[str] = frozenset({"haiku", "sonnet", "opus", "fable"})

_CONFIG_RELATIVE_PATH = Path(".raise") / "skill_models.yaml"


def parse_skill_model(
    skill_name: str,
    skill_base: Path,
    phase_path: str | None = None,
    phase_model: str | None = None,
) -> str | None:
    """Resolve a skill's routed model via layered precedence.

    Returns a validated model name or None (nothing configured anywhere,
    or every configured value was invalid/unreadable).
    """
    model = _env_model(skill_name)
    if model is not None:
        return model

    config = _load_config(skill_base)

    if phase_path is not None:
        model = _config_skill_model(phase_path, config)
        if model is not None:
            return model

    model = _config_skill_model(skill_name, config)
    if model is not None:
        return model

    if phase_model is not None:
        model = _validate(phase_model, skill_name, "phase YAML")
        if model is not None:
            return model

    model = _frontmatter_model(skill_name, skill_base)
    if model is not None:
        return model

    model = _config_default_model(skill_name, config)
    if model is not None:
        return model

    return None


def _validate(value: str, skill_name: str, source: str) -> str | None:
    """Normalize + validate a candidate model; log and return None if bad."""
    model = value.strip().lower()
    if not model:
        return None
    if model not in VALID_MODELS:
        logger.warning(
            "Skill '%s' %s declares unknown model '%s' — ignoring",
            skill_name,
            source,
            model,
        )
        return None
    return model


def _env_model(skill_name: str) -> str | None:
    """Layers 1-2: per-skill env var, then global env var."""
    per_skill_var = f"RAISE_SKILL_MODEL_{skill_name.upper().replace('-', '_')}"
    per_skill_value = os.environ.get(per_skill_var, "")
    if per_skill_value.strip():
        model = _validate(per_skill_value, skill_name, f"env {per_skill_var}")
        if model is not None:
            return model

    global_value = os.environ.get("RAISE_PIPELINE_MODEL", "")
    if global_value.strip():
        model = _validate(global_value, skill_name, "env RAISE_PIPELINE_MODEL")
        if model is not None:
            return model

    return None


def _load_config(skill_base: Path) -> dict[str, Any]:
    """Best-effort load of <project_root>/.raise/skill_models.yaml.

    Missing file, unreadable file, or parse error all resolve to {} —
    this layer is never allowed to raise.
    """
    project_root = skill_base.parent.parent
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


def _config_skill_model(skill_name: str, config: dict[str, Any]) -> str | None:
    """Layer 3: config['skills'][skill_name]."""
    skills = config.get("skills")
    if not isinstance(skills, dict):
        return None
    value = skills.get(skill_name)
    if value is None:
        return None
    return _validate(str(value), skill_name, "config skills")


def _frontmatter_model(skill_name: str, skill_base: Path) -> str | None:
    """Layer 4: SKILL.md frontmatter `model:` field (original logic)."""
    skill_path = skill_base / skill_name / "SKILL.md"
    if not skill_path.is_file():
        return None

    try:
        content = skill_path.read_text(encoding="utf-8")
    except OSError:
        return None

    from raise_cli.skills.parser import ParseError, parse_frontmatter

    try:
        raw, _ = parse_frontmatter(content)
    except ParseError:
        return None

    model = raw.get("model")
    if model is None:
        return None

    return _validate(str(model), skill_name, "frontmatter")


def _config_default_model(skill_name: str, config: dict[str, Any]) -> str | None:
    """Layer 5: config['default'], the final catch-all (if present)."""
    default = config.get("default")
    if default is None:
        return None
    return _validate(str(default), skill_name, "config default")
