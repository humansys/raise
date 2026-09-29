"""Developer profile schema and persistence — thin re-export shim (RAISE-16419 S4).

Reclassified from foundation (T5) to services (T2) tier. Pure models and
load_developer_profile moved to developer_profile/ (T5). This shim preserves
backward compatibility for T1/T2 callers that import from onboarding.profile.
"""

from __future__ import annotations

from raise_cli.developer_profile.persistence import save_developer_profile
from raise_cli.developer_profile.profile import (
    CORRECTIONS_MAX,
    DEVELOPER_PROFILE_FILE,
    RAI_HOME_DIR,
    ActiveSession,
    CoachingContext,
    CommunicationPreferences,
    CommunicationStyle,
    Correction,
    CurrentSession,
    Deadline,
    DelegationConfig,
    DelegationLevel,
    DeveloperProfile,
    ExperienceLevel,
    RelationshipState,
    add_correction,
    add_deadline,
    end_session,
    get_rai_home,
    increment_session,
    load_developer_profile,
    resolve_delegation,
    start_session,
    update_coaching,
)

__all__ = [
    "ActiveSession",
    "CoachingContext",
    "CommunicationPreferences",
    "CommunicationStyle",
    "CORRECTIONS_MAX",
    "Correction",
    "CurrentSession",
    "Deadline",
    "DelegationConfig",
    "DelegationLevel",
    "DEVELOPER_PROFILE_FILE",
    "DeveloperProfile",
    "ExperienceLevel",
    "RAI_HOME_DIR",
    "RelationshipState",
    "add_correction",
    "add_deadline",
    "end_session",
    "get_rai_home",
    "increment_session",
    "load_developer_profile",
    "resolve_delegation",
    "save_developer_profile",
    "start_session",
    "update_coaching",
]
