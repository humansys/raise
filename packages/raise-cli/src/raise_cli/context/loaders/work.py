"""Work-item loaders for the context graph.

Projects session and story rows from raise.db into SessionNode and StoryNode
graph nodes, enabling `learned_from` edge resolution (RAISE-15988).

The session_id and story_id from the database are run through
`normalize_learned_from_ref` so graph node ids match exactly what
`_infer_pattern_learned_from` looks up: a pattern referencing ``S5.3``
normalises to ``story-s5-3``, and a session UUID like
``d841432e-4ff1-4d57-9b08-594f61c783b9`` normalises to itself. Without
this projection, 100% of ``learned_from`` refs are discarded because their
targets never exist in the graph.
"""

from __future__ import annotations

import logging
from pathlib import Path

from raise_cli.context.extractors.relationships import normalize_learned_from_ref
from raise_core.graph.models import GraphNode, SessionNode, StoryNode

logger = logging.getLogger(__name__)


def load_sessions(project_root: Path) -> list[GraphNode]:
    """Load SessionNode instances from the sessions table in raise.db.

    Queries all sessions for the current project and emits one ``SessionNode``
    per row whose session_id normalises to a ``session`` type under
    :func:`normalize_learned_from_ref`.  Rows with opaque ids that the
    normaliser cannot classify are skipped with a DEBUG log (they would never
    be reachable via ``learned_from`` anyway).

    Args:
        project_root: Root directory of the project (used to locate raise.db
            and to derive the project_id for row filtering).

    Returns:
        List of :class:`SessionNode` instances, one per qualifying session row.
    """
    try:
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        conn = get_project_db(project_root)
        create_all(conn)
        pid = get_project_id(project_root)
        rows = conn.execute(
            "SELECT session_id, name, started FROM sessions WHERE project_id = ?",
            (pid,),
        ).fetchall()
    except Exception:  # noqa: BLE001
        logger.debug("load_sessions: could not query raise.db", exc_info=True)
        return []

    nodes: list[GraphNode] = []
    for row in rows:
        session_id: str = row[0]
        canonical_id, target_type = normalize_learned_from_ref(session_id)
        if target_type != "session":
            logger.debug("load_sessions: skipping non-session id %r", session_id)
            continue
        nodes.append(
            SessionNode(
                id=canonical_id,
                content=row[1] or session_id,
                source_file="raise.db:sessions",
                created=str(row[2] or ""),
                metadata={"raw_id": session_id},
            )
        )
    return nodes


def load_stories(project_root: Path) -> list[GraphNode]:
    """Load StoryNode instances from the story_stats table in raise.db.

    Queries all story rows for the current project and emits one ``StoryNode``
    per row whose story_id normalises to a ``story`` type (S/F prefix format).
    Jira-key story_ids like ``RAISE-15988`` normalise to the ``epic`` type and
    are intentionally skipped — they would collide with existing EpicNode ids
    and their ``learned_from`` references are handled via the epic extractor.

    Args:
        project_root: Root directory of the project.

    Returns:
        List of :class:`StoryNode` instances, one per qualifying story row.
    """
    try:
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        conn = get_project_db(project_root)
        create_all(conn)
        pid = get_project_id(project_root)
        rows = conn.execute(
            "SELECT story_id, updated_at FROM story_stats WHERE project_id = ?",
            (pid,),
        ).fetchall()
    except Exception:  # noqa: BLE001
        logger.debug("load_stories: could not query raise.db", exc_info=True)
        return []

    nodes: list[GraphNode] = []
    for row in rows:
        story_id: str = row[0]
        canonical_id, target_type = normalize_learned_from_ref(story_id)
        if target_type != "story":
            logger.debug("load_stories: skipping non-story id %r", story_id)
            continue
        nodes.append(
            StoryNode(
                id=canonical_id,
                content=story_id,
                source_file="raise.db:story_stats",
                created=str(row[1] or ""),
                metadata={"raw_id": story_id},
            )
        )
    return nodes
