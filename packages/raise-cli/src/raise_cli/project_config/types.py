"""Project type enum for project configuration (core tier).

Moved from onboarding/detection.py in RAISE-16419 S4 to break
the circular dependency: project_config/manifest.py needs ProjectType
but must stay in Tier 5 (foundation), while detection.py must stay in
Tier 2 (services) after onboarding is reclassified.
"""

from __future__ import annotations

from enum import StrEnum


class ProjectType(StrEnum):
    """Type of project based on existing code.

    Values:
        GREENFIELD: No existing code files (new project)
        BROWNFIELD: Has existing code files
    """

    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"
