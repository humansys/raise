"""Onboarding module for RaiSE CLI.

Handles developer profile management and project initialization.
"""

from __future__ import annotations

from raise_cli.onboarding.migration import migrate_emilio_profile
from raise_cli.onboarding.profile import (
    CommunicationPreferences,
    CommunicationStyle,
    DeveloperProfile,
    ExperienceLevel,
    get_rai_home,
    load_developer_profile,
    save_developer_profile,
)

__all__ = [
    "CommunicationPreferences",
    "CommunicationStyle",
    "DeveloperProfile",
    "ExperienceLevel",
    "get_rai_home",
    "load_developer_profile",
    "migrate_emilio_profile",
    "save_developer_profile",
]
