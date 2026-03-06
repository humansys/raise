"""Built-in GateBridgeHook — bridges gate system into before: events.

Subscribes to ``before:`` events and runs matching WorkflowGates via
GateRegistry discovery. Returns ``abort`` if any gate fails, preventing
the guarded operation from proceeding.

This is the bridge between the independent gate and hook systems (PAT-E-454).
Gates remain standalone (AD-5) — the bridge is the only coupling point.

Architecture: ADR-039 §5 (Built-in hooks), S248.6
"""

from __future__ import annotations

import logging
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.registry import GateRegistry
from raise_cli.hooks.events import HookEvent, HookResult

logger = logging.getLogger(__name__)


class GateBridgeHook:
    """Bridges WorkflowGates into the hook lifecycle.

    Subscribes to ``before:`` events, discovers gates registered for
    the matching workflow point, runs them all, and returns ``abort``
    if any gate fails. Priority 100 ensures gates run before other hooks.

    Registered via ``rai.hooks`` entry point in pyproject.toml.
    """

    events: ClassVar[list[str]] = [
        "before:release:publish",
        "before:session:close",
    ]
    priority: ClassVar[int] = 100

    def handle(self, event: HookEvent) -> HookResult:
        """Run matching gates and abort if any fail."""
        workflow_point = event.event_name

        registry = GateRegistry()
        registry.discover()
        gates = registry.get_gates_for_point(workflow_point)

        if not gates:
            logger.debug("GateBridgeHook: no gates for '%s'", workflow_point)
            return HookResult(status="ok")

        logger.debug(
            "GateBridgeHook: running %d gate(s) for '%s'",
            len(gates),
            workflow_point,
        )

        failures: list[GateResult] = []
        for gate in gates:
            context = GateContext(gate_id=gate.gate_id)
            try:
                result = gate.evaluate(context)
            except Exception as exc:  # noqa: BLE001
                result = GateResult(
                    passed=False,
                    gate_id=gate.gate_id,
                    message=f"{type(exc).__name__}: {exc}",
                )

            if not result.passed:
                failures.append(result)
                logger.debug(
                    "GateBridgeHook: gate '%s' failed: %s",
                    gate.gate_id,
                    result.message,
                )

        if failures:
            summary = "; ".join(f"{f.gate_id}: {f.message}" for f in failures)
            return HookResult(status="abort", message=f"Gates failed: {summary}")

        return HookResult(status="ok")
