"""Project manifest schema and persistence — thin re-export shim (RAISE-16419 S4).

Reclassified from foundation (T5) to services (T2) tier. Models and
load/save functions moved to project_config/ (T5). This shim preserves
backward compatibility for T1/T2 callers that import from onboarding.manifest.
"""

from __future__ import annotations

from raise_cli.project_config.manifest import (
    AgentsManifest,
    AppInfo,
    BacklogConfig,
    BranchConfig,
    GraphConfig,
    GraphStalenessConfig,
    IdeManifest,
    ManifestModel,
    OrgBinding,
    ProjectCodeConfig,
    ProjectDocsConfig,
    ProjectDocsDeveloperConfig,
    ProjectDocsProductConfig,
    ProjectGovernanceConfig,
    ProjectInfo,
    ProjectManifest,
    ProjectPortfolioConfig,
    ProjectSchemaConfig,
    ProtocolComplianceEntry,
    TierConfig,
    load_manifest,
    persist_server_slug,
    save_manifest,
)

__all__ = [
    "AgentsManifest",
    "AppInfo",
    "BacklogConfig",
    "BranchConfig",
    "GraphConfig",
    "GraphStalenessConfig",
    "IdeManifest",
    "ManifestModel",
    "OrgBinding",
    "ProjectCodeConfig",
    "ProjectDocsConfig",
    "ProjectDocsDeveloperConfig",
    "ProjectDocsProductConfig",
    "ProjectGovernanceConfig",
    "ProjectInfo",
    "ProjectManifest",
    "ProjectPortfolioConfig",
    "ProjectSchemaConfig",
    "ProtocolComplianceEntry",
    "TierConfig",
    "load_manifest",
    "persist_server_slug",
    "save_manifest",
]
