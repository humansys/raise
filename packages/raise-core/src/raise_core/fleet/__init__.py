"""Fleet dispatch contracts — ADR-106.

Public surface: import from here, not from submodules.
"""

from raise_core.fleet.collision import (
    MergePreflight,
    MergePreview,
    ModuleScope,
    TaskClaimStore,
    serialize_overlapping,
)
from raise_core.fleet.contracts import (
    DependencyResolver,
    DispatchCandidate,
    DispatchPlan,
)

__all__ = [
    "DispatchCandidate",
    "DispatchPlan",
    "DependencyResolver",
    "TaskClaimStore",
    "ModuleScope",
    "MergePreflight",
    "MergePreview",
    "serialize_overlapping",
]
