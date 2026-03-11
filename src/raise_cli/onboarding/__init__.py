"""Onboarding module for RaiSE CLI.

Handles developer profile management, project initialization, and convention detection.
"""

from __future__ import annotations

from raise_cli.onboarding.conventions import (
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
from raise_cli.onboarding.detection import (
    CODE_EXTENSIONS,
    DetectionResult,
    ProjectType,
    count_code_files,
    detect_project_type,
)
from raise_cli.onboarding.governance import (
    GeneratedGuardrail,
    GuardrailGenerator,
    GuardrailLevel,
    generate_guardrails,
)
from raise_cli.onboarding.instructions import (
    ClaudeMdGenerator,
    InstructionsGenerator,
    generate_claude_md,
    generate_instructions,
)
from raise_cli.onboarding.manifest import (
    BranchConfig,
    ProjectInfo,
    ProjectManifest,
    load_manifest,
    save_manifest,
)
from raise_cli.onboarding.migration import migrate_developer_profile
from raise_cli.onboarding.profile import (
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
    # Instructions
    "InstructionsGenerator",
    "generate_instructions",
    # Backward-compat
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
    "migrate_developer_profile",
    "save_developer_profile",
]
