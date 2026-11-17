"""PM discipline gates — opt-in via project.pm_gates.enabled in manifest.yaml."""

from raise_cli.gates.pm._config import pm_gates_enabled, pm_gates_strictness

__all__ = ["pm_gates_enabled", "pm_gates_strictness"]
