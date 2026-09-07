"""Migration utilities for developer profiles.

Extracts profile data from existing memory artifacts.
"""

from __future__ import annotations

import contextlib
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from raise_cli.config.paths import get_memory_dir
from raise_cli.onboarding.profile import (
    CommunicationPreferences,
    CommunicationStyle,
    DeveloperProfile,
    ExperienceLevel,
)

logger = logging.getLogger(__name__)


def _parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    return date.fromisoformat(date_str)


def _extract_sessions_data(sessions_path: Path) -> tuple[int, date | None, date | None]:
    """Extract session statistics from sessions index.

    Args:
        sessions_path: Path to sessions/index.jsonl file.

    Returns:
        Tuple of (total_sessions, first_session_date, last_session_date).
    """
    if not sessions_path.exists():
        logger.warning("Sessions index not found: %s", sessions_path)
        return 0, None, None

    sessions: list[dict[str, Any]] = []
    for line in sessions_path.read_text(encoding="utf-8").strip().splitlines():
        if line:
            try:
                session: dict[str, Any] = json.loads(line)
                sessions.append(session)
            except json.JSONDecodeError:
                sanitized = line[:50].encode("unicode_escape").decode("ascii")
                logger.warning("Invalid JSON in sessions index: %s", sanitized)

    if not sessions:
        return 0, None, None

    # Extract dates
    dates: list[date] = []
    for session_data in sessions:
        if "date" in session_data:
            with contextlib.suppress(ValueError):
                dates.append(_parse_date(str(session_data["date"])))

    if not dates:
        return len(sessions), None, None

    dates.sort()
    return len(sessions), dates[0], dates[-1]


def _extract_skills_from_sessions(sessions_path: Path) -> list[str]:
    """Extract skill names mentioned in session outcomes.

    Args:
        sessions_path: Path to sessions/index.jsonl file.

    Returns:
        List of unique skill names found.
    """
    if not sessions_path.exists():
        return []

    # Skills to look for in outcomes
    known_skills = {
        "rai-session-start",
        "rai-session-close",
        "rai-story-design",
        "rai-story-plan",
        "rai-story-implement",
        "rai-story-review",
        "rai-story-start",
        "rai-story-close",
        "rai-epic-design",
        "rai-epic-plan",
        "rai-research",
        "rai-debug",
        "rai-discover-start",
        "rai-discover-scan",
        "rai-discover-validate",
        # Legacy names (pre-namespace, for backward compat with old sessions)
        "session-start",
        "session-close",
        "story-design",
        "story-plan",
        "story-implement",
        "story-review",
        "story-start",
        "story-close",
        "epic-design",
        "epic-plan",
        "research",
        "debug",
        "discover-start",
        "discover-scan",
        "discover-validate",
    }

    found_skills: set[str] = set()

    for line in sessions_path.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            session = json.loads(line)
            outcomes = session.get("outcomes", [])
            topic = session.get("topic", "")

            # Check outcomes for skill mentions
            for outcome in outcomes:
                outcome_lower = outcome.lower()
                for skill in known_skills:
                    # Match /skill-name or skill-name in text
                    if skill in outcome_lower or f"/{skill}" in outcome_lower:
                        found_skills.add(skill)

            # Check topic for skill mentions
            topic_lower = topic.lower()
            for skill in known_skills:
                if skill.replace("-", " ") in topic_lower or skill in topic_lower:
                    found_skills.add(skill)

        except json.JSONDecodeError:
            pass

    return sorted(found_skills)


def migrate_developer_profile(
    project_path: Path,
    *,
    name: str = "Developer",
    additional_skills: list[str] | None = None,
) -> DeveloperProfile:
    """Create developer profile from existing memory data.

    Extracts session history, skills used, and communication preferences
    from the project's .raise/rai/memory/ directory.

    Args:
        project_path: Path to the project root.
        name: Developer name (default: "Developer").
        additional_skills: Extra skills to add beyond those detected.

    Returns:
        DeveloperProfile populated from historical data.
    """
    memory_path = get_memory_dir(project_path)
    sessions_path = memory_path / "sessions" / "index.jsonl"

    # Extract session statistics (sessions_total now derived from index)
    _, first_session, last_session = _extract_sessions_data(sessions_path)

    # Extract skills from session history
    skills_mastered = _extract_skills_from_sessions(sessions_path)

    # Add any additional skills specified
    if additional_skills:
        skills_mastered = sorted(set(skills_mastered) | set(additional_skills))

    # Default communication preferences
    communication = CommunicationPreferences(
        style=CommunicationStyle.DIRECT,
        language="en",  # es for casual
        skip_praise=True,
        detailed_explanations=False,
        redirect_when_dispersing=True,
    )

    # Universal patterns that apply across all projects
    universal_patterns = [
        "Commit after each completed task",
        "TDD for complex stories",
        "Ask before spawning subagents",
        "Inference economy: gather with tools, think with inference",
        "Permission granted to redirect when dispersing",
        "No unnecessary praise or emotional validation",
    ]

    return DeveloperProfile(
        name=name,
        experience_level=ExperienceLevel.RI,
        communication=communication,
        skills_mastered=skills_mastered,
        universal_patterns=universal_patterns,
        first_session=first_session,
        last_session=last_session,
        projects=[str(project_path)],
    )
