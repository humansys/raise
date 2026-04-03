"""Data models and fetching for context bundle assembly.

Contains data models (LiveBacklogStatus, SectionManifest), path constants,
and functions that load data from disk or external services.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic import BaseModel

from raise_cli.graph.backends import get_active_backend
from raise_cli.schemas.session_state import SessionState
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)


class LiveBacklogStatus(BaseModel):
    """Live status fetched from backlog adapter during session-start."""

    epic_status: str = ""
    epic_summary: str = ""
    story_status: str = ""
    story_summary: str = ""
    warning: str = ""


class SectionManifest(BaseModel):
    """Manifest entry for a queryable context section."""

    name: str
    count: int
    token_estimate: int


# Graph path relative to project root
GRAPH_REL_PATH = Path(".raise") / "rai" / "memory" / "index.json"
# Sessions index path relative to project root (personal = developer-specific)
SESSIONS_INDEX_REL_PATH = (
    Path(".raise") / "rai" / "personal" / "sessions" / "index.jsonl"
)


def fetch_live_status(
    state: SessionState | None,
    timeout: float = 5.0,
) -> LiveBacklogStatus:
    """Query backlog adapter for live epic/story status.

    Returns LiveBacklogStatus with warning on any failure.
    Never raises — all errors are caught and surfaced as warnings.
    """
    if state is None:
        return LiveBacklogStatus()

    epic_key = state.current_work.epic
    story_key = state.current_work.story

    if not epic_key and not story_key:
        return LiveBacklogStatus()

    return _query_adapter(epic_key, story_key, timeout)


def _query_adapter(
    epic_key: str,
    story_key: str,
    timeout: float,
) -> LiveBacklogStatus:
    """Resolve adapter and run queries with timeout. Never raises.

    The entire operation (adapter resolution + issue fetches) runs inside
    the ThreadPoolExecutor so that the timeout covers everything, including
    slow adapter startup (e.g., MCP bridge initialization).
    """
    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import TimeoutError as FuturesTimeoutError

    from raise_cli.adapters.models import IssueDetail
    from raise_cli.adapters.protocols import ProjectManagementAdapter
    from raise_cli.cli.commands._resolve import resolve_adapter

    def _do_fetch() -> LiveBacklogStatus:
        adapter: ProjectManagementAdapter = resolve_adapter(None)
        result = LiveBacklogStatus()
        if epic_key:
            detail: IssueDetail = adapter.get_issue(epic_key)
            result.epic_status = detail.status
            result.epic_summary = detail.summary
        if story_key:
            detail = adapter.get_issue(story_key)
            result.story_status = detail.status
            result.story_summary = detail.summary
        return result

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_do_fetch)
            return future.result(timeout=timeout)
    except FuturesTimeoutError:
        logger.debug("Live status fetch timed out after %.1fs", timeout)
        return LiveBacklogStatus(
            warning=f"Backlog query timeout ({timeout:.0f}s) — showing cached state"
        )
    except SystemExit:
        # resolve_adapter() uses sys.exit() on failure; SystemExit is
        # BaseException, not Exception, so we catch it explicitly.
        logger.debug("Adapter unavailable (SystemExit)")
        return LiveBacklogStatus(
            warning="Backlog adapter unavailable — showing cached state"
        )
    except Exception as exc:
        logger.debug("Live status fetch failed: %s", exc)
        return LiveBacklogStatus(
            warning=f"Backlog query error: {exc} — showing cached state"
        )


def get_foundational_patterns(project_path: Path) -> list[GraphNode]:
    """Query memory graph for foundational patterns.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of pattern GraphNodes with foundational=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        logger.debug("Graph not found: %s", graph_path)
        return []

    try:
        graph = get_active_backend(graph_path).load()
    except Exception:
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node
        for node in graph.iter_concepts()
        if node.type == "pattern" and node.metadata.get("foundational") is True
    ]


def get_always_on_primes(project_path: Path) -> list[GraphNode]:
    """Query memory graph for all always_on nodes (governance + identity).

    Args:
        project_path: Absolute path to the project root.

    Returns:
        List of GraphNodes with always_on=true metadata.
    """
    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        logger.debug("Graph not found: %s", graph_path)
        return []

    try:
        graph = get_active_backend(graph_path).load()
    except Exception:
        logger.warning("Failed to load graph: %s", graph_path)
        return []

    return [
        node for node in graph.iter_concepts() if node.metadata.get("always_on") is True
    ]


def find_release_for_current_epic(project_path: Path, epic_id: str) -> GraphNode | None:
    """Find release node for the current epic from the memory graph.

    Args:
        project_path: Absolute path to the project root.
        epic_id: Epic identifier (e.g., "E19").

    Returns:
        The release GraphNode, or None if not found or graph unavailable.
    """
    if not epic_id:
        return None

    graph_path = project_path / GRAPH_REL_PATH
    if not graph_path.exists():
        return None

    try:
        from raise_cli.graph.backends import get_active_backend
        from raise_core.graph.query import QueryEngine

        graph = get_active_backend(graph_path).load()
        engine = QueryEngine(graph)
        return engine.find_release_for(f"epic-{epic_id.lower()}")
    except Exception:
        logger.debug("Failed to query release for epic %s", epic_id)
        return None
