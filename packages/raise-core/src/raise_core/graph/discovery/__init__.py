"""Schema discovery diff and reconcile tools.

Pure data comparison functions — no LLM dependencies.
LLM-based discovery (discover_schema, refine_schema) remains in rai-agent.

Migrated from rai-agent in S2674.6.
"""

from raise_core.graph.discovery.diff import (
    diff_nodes,
    diff_schemas,
    reconcile_extracted,
)
from raise_core.graph.discovery.models import (
    DecisionDiff,
    FieldDiff,
    NodeDiffReport,
    NodeTypeSpec,
    ReconcileReport,
    SchemaDiffReport,
    SchemaSpec,
)

__all__ = [
    "DecisionDiff",
    "FieldDiff",
    "NodeDiffReport",
    "NodeTypeSpec",
    "ReconcileReport",
    "SchemaDiffReport",
    "SchemaSpec",
    "diff_nodes",
    "diff_schemas",
    "reconcile_extracted",
]
