"""Reliability lens — escaped-defect reporting over git history (RAISE-11490)."""

from raise_cli.reliability.cfr import ReleaseBoundary, compute_cfr
from raise_cli.reliability.classification_models import (
    BugRecord,
    ClassifierConfig,
    CostEstimate,
    TargetClassification,
)
from raise_cli.reliability.cohort import build_cohorts
from raise_cli.reliability.deployments import DeploymentEvent, DeploymentEventStore
from raise_cli.reliability.gate_escape import (
    DefectWindow,
    GateEscapeTracker,
)
from raise_cli.reliability.models import (
    ChangeFailureRate,
    Cohort,
    CohortBreakdown,
    CohortMaturity,
    ConfidenceSummary,
    Denominator,
    DenominatorValue,
    GateEscapeBreakdown,
    GateStage,
    ReliabilityReport,
    Target,
    TargetTally,
)
from raise_cli.reliability.recommendations import (
    RankedHotspot,
    Recommendation,
    RecommendationEngine,
    RuleConfig,
    Severity,
    band_hotspots,
)
from raise_cli.reliability.rollup import (
    MetricDelta,
    ReliabilityRollup,
    ReliabilitySnapshot,
    RollupTrend,
)
from raise_cli.reliability.target_classifier import LlmProvider, TargetClassifier

__all__ = [
    "BugRecord",
    "ChangeFailureRate",
    "ClassifierConfig",
    "Cohort",
    "CohortBreakdown",
    "CohortMaturity",
    "ConfidenceSummary",
    "CostEstimate",
    "DefectWindow",
    "DenominatorValue",
    "Denominator",
    "DeploymentEvent",
    "DeploymentEventStore",
    "GateEscapeBreakdown",
    "GateEscapeTracker",
    "GateStage",
    "LlmProvider",
    "MetricDelta",
    "RankedHotspot",
    "Recommendation",
    "RecommendationEngine",
    "ReleaseBoundary",
    "ReliabilityReport",
    "ReliabilityRollup",
    "ReliabilitySnapshot",
    "RollupTrend",
    "RuleConfig",
    "Severity",
    "Target",
    "TargetClassification",
    "TargetClassifier",
    "TargetTally",
    "band_hotspots",
    "build_cohorts",
    "compute_cfr",
]
