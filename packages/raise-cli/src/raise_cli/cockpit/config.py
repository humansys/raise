"""Agent launch configuration persistence for the cockpit (RAISE-15063).

Stores per-agent launch preferences (model, effort, permissions) in
`.raise/cockpit.yaml` under the worktree root.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

_CLAUDE_MODELS: list[str] = [
    "claude-sonnet-5",
    "claude-opus-4-8",
    "claude-haiku-4-5-20251001",
]

_CODEX_MODELS: list[str] = [
    "o3",
    "o4-mini",
]

_EFFORT_LEVELS: list[str] = ["low", "medium", "high"]

_AGENT_MODELS: dict[str, list[str]] = {
    "claude": _CLAUDE_MODELS,
    "codex": _CODEX_MODELS,
}


class AgentLaunchConfig(BaseModel):
    """Launch configuration for a single agent."""

    model: str | None = None
    effort: str | None = None
    permissions: str = Field(default="default")

    def to_args(self, models: list[str] | None = None) -> list[str]:
        """Convert config to CLI args for the agent command.

        Args:
            models: Available models for the agent. When provided and model is
                None (default), the first element is passed explicitly so the
                launched agent uses a known model instead of its own default.
        """
        args: list[str] = []
        resolved_model = self.model
        if resolved_model is None and models:
            resolved_model = models[0]
        if resolved_model is not None:
            args.extend(["--model", resolved_model])
        if self.permissions == "full":
            args.append("--dangerously-skip-permissions")
        return args


class CockpitConfigStore:
    """Read/write `.raise/cockpit.yaml` for per-agent launch config."""

    def __init__(self, worktree_path: Path) -> None:
        self._path = worktree_path / ".raise" / "cockpit.yaml"
        self._configs: dict[str, AgentLaunchConfig] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return
        if not isinstance(data, dict):
            return
        agent_config: Any = data.get("agent_config", {})
        if not isinstance(agent_config, dict):
            return
        for agent_key, cfg_dict in agent_config.items():
            if isinstance(cfg_dict, dict):
                self._configs[agent_key] = AgentLaunchConfig(**cfg_dict)

    def get(self, agent_cmd: str) -> AgentLaunchConfig:
        """Return config for agent, or defaults if not set."""
        return self._configs.get(agent_cmd, AgentLaunchConfig())

    def set(self, agent_cmd: str, config: AgentLaunchConfig) -> None:
        """Update config for agent (in memory — call save() to persist)."""
        self._configs[agent_cmd] = config

    def save(self) -> None:
        """Write current config to `.raise/cockpit.yaml`."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {
            "agent_config": {
                k: v.model_dump(exclude_defaults=False)
                for k, v in self._configs.items()
            }
        }
        self._path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )

    def available_models(self, agent_cmd: str) -> list[str]:
        """Return available models for the given agent command."""
        return _AGENT_MODELS.get(agent_cmd, [])

    def cycle_model(self, agent_cmd: str) -> AgentLaunchConfig:
        """Cycle to the next model for the agent. Wraps around to None."""
        cfg = self.get(agent_cmd)
        models = self.available_models(agent_cmd)
        if not models:
            return cfg
        if cfg.model is None:
            new_model = models[0]
        elif cfg.model in models:
            idx = models.index(cfg.model)
            new_model = None if idx + 1 >= len(models) else models[idx + 1]
        else:
            new_model = models[0]
        new_cfg = cfg.model_copy(update={"model": new_model})
        self._configs[agent_cmd] = new_cfg
        return new_cfg

    def cycle_effort(self, agent_cmd: str) -> AgentLaunchConfig:
        """Cycle to the next effort level. Wraps around to None."""
        cfg = self.get(agent_cmd)
        if cfg.effort is None:
            new_effort = _EFFORT_LEVELS[0]
        elif cfg.effort in _EFFORT_LEVELS:
            idx = _EFFORT_LEVELS.index(cfg.effort)
            new_effort = (
                None if idx + 1 >= len(_EFFORT_LEVELS) else _EFFORT_LEVELS[idx + 1]
            )
        else:
            new_effort = _EFFORT_LEVELS[0]
        new_cfg = cfg.model_copy(update={"effort": new_effort})
        self._configs[agent_cmd] = new_cfg
        return new_cfg

    def toggle_permissions(self, agent_cmd: str) -> AgentLaunchConfig:
        """Toggle permissions between 'default' and 'full'."""
        cfg = self.get(agent_cmd)
        new_perm = "full" if cfg.permissions == "default" else "default"
        new_cfg = cfg.model_copy(update={"permissions": new_perm})
        self._configs[agent_cmd] = new_cfg
        return new_cfg
