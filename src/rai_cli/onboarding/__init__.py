"""Onboarding module for RaiSE CLI.

Handles developer profile management, project initialization, and convention detection.
"""

from __future__ import annotations

from rai_cli.onboarding.claudemd import (
    ClaudeMdGenerator,
    generate_claude_md,
)
from rai_cli.onboarding.conventions import (
    Confidence,
    ConventionResult,
    IndentationConvention,
    LineLengthConvention,
    NamingConvention,
    NamingConventions,
    QuoteConvention,
    StructureConventions,
    StyleConventions,
    detect_conventions,
)
from rai_cli.onboarding.detection import (
    CODE_EXTENSIONS,
    DetectionResult,
    ProjectType,
    count_code_files,
    detect_project_type,
)
from rai_cli.onboarding.governance import (
    GeneratedGuardrail,
    GuardrailGenerator,
    GuardrailLevel,
    generate_guardrails,
)
from rai_cli.onboarding.manifest import (
    BranchConfig,
    ProjectInfo,
    ProjectManifest,
    load_manifest,
    save_manifest,
)
from rai_cli.onboarding.migration import migrate_emilio_profile
from rai_cli.onboarding.profile import (
    CommunicationPreferences,
    CommunicationStyle,
    DeveloperProfile,
    ExperienceLevel,
    get_rai_home,
    increment_session,
    load_developer_profile,
    save_developer_profile,
)

__all__ = [
    # Conventions
    "Confidence",
    "ConventionResult",
    "IndentationConvention",
    "LineLengthConvention",
    "NamingConvention",
    "NamingConventions",
    "QuoteConvention",
    "StructureConventions",
    "StyleConventions",
    "detect_conventions",
    # ClaudeMd
    "ClaudeMdGenerator",
    "generate_claude_md",
    # Detection
    "CODE_EXTENSIONS",
    "DetectionResult",
    "ProjectType",
    "count_code_files",
    "detect_project_type",
    # Governance
    "GeneratedGuardrail",
    "GuardrailGenerator",
    "GuardrailLevel",
    "generate_guardrails",
    # Manifest
    "BranchConfig",
    "ProjectInfo",
    "ProjectManifest",
    "load_manifest",
    "save_manifest",
    # Profile
    "CommunicationPreferences",
    "CommunicationStyle",
    "DeveloperProfile",
    "ExperienceLevel",
    "get_rai_home",
    "increment_session",
    "load_developer_profile",
    "migrate_emilio_profile",
    "save_developer_profile",
]
