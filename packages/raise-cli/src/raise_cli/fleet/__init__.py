"""No-op fleet collision stubs — intentionally inert for N<4 agents (ADR-106 §3)."""

from raise_cli.fleet.noop_collision import (
    NoopMergePreflight,
    NoopModuleScope,
    NoopTaskClaimStore,
)

__all__ = ["NoopModuleScope", "NoopTaskClaimStore", "NoopMergePreflight"]
