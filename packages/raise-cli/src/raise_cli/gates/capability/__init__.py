"""ADR-132 capability registry + capability-overlap fitness function package."""

from raise_cli.gates.capability.capability_overlap import CapabilityOverlapGate
from raise_cli.gates.capability.registry import CapabilityCard, load_registry

__all__ = ["CapabilityCard", "CapabilityOverlapGate", "load_registry"]
