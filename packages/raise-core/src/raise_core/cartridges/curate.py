"""Generic curation session — HITL review workflow for GraphNode.

Ported from scaleupagent/curation/, generalized from OntologyNode to GraphNode.
"""

from __future__ import annotations

import hashlib
import json
import logging
import tempfile
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from raise_core.graph.models import GraphNode

_log = logging.getLogger(__name__)


class CurationDecision(StrEnum):
    """Possible curation outcomes for a node."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"


class NodeDecision(BaseModel):
    """A single curation decision for one node."""

    node_id: str
    decision: CurationDecision
    reason: str | None = None
    edits: dict[str, Any] | None = None
    original_hash: str
    timestamp: datetime


class CurationSessionState(BaseModel):
    """Persisted session state for curation workflow."""

    session_id: str
    source_dir: str
    output_dir: str
    total_nodes: int
    cursor: int
    node_order: list[str]
    decisions: dict[str, NodeDecision]
    created: datetime
    updated: datetime


class CurationSummary(BaseModel):
    """Aggregate counts from a curation session."""

    total: int
    accepted: int
    rejected: int
    edited: int
    remaining: int

    @classmethod
    def from_state(cls, state: CurationSessionState) -> CurationSummary:
        """Build summary from session state."""
        accepted = sum(
            1
            for d in state.decisions.values()
            if d.decision == CurationDecision.ACCEPTED
        )
        rejected = sum(
            1
            for d in state.decisions.values()
            if d.decision == CurationDecision.REJECTED
        )
        edited = sum(
            1 for d in state.decisions.values() if d.decision == CurationDecision.EDITED
        )
        return cls(
            total=state.total_nodes,
            accepted=accepted,
            rejected=rejected,
            edited=edited,
            remaining=state.total_nodes - accepted - rejected - edited,
        )


class CurationSession:
    """Engine for HITL curation of extracted GraphNode instances."""

    def __init__(
        self,
        state: CurationSessionState,
        nodes: dict[str, tuple[GraphNode, str]],
        state_path: Path,
    ) -> None:
        self.state = state
        self._nodes = nodes
        self._state_path = state_path

    @classmethod
    def load(
        cls,
        source_dir: Path,
        output_dir: Path,
        state_path: Path,
    ) -> CurationSession:
        """Load or resume a curation session."""
        nodes = _load_nodes_from_dir(source_dir)

        if state_path.exists():
            raw = yaml.safe_load(state_path.read_text(encoding="utf-8"))
            state = CurationSessionState.model_validate(raw)
            state.source_dir = str(source_dir)
            state.output_dir = str(output_dir)
            return cls(state=state, nodes=nodes, state_path=state_path)

        now = datetime.now(tz=UTC)
        node_order = sorted(nodes.keys())
        state = CurationSessionState(
            session_id=f"curation-{now:%Y-%m-%d-%H%M%S}",
            source_dir=str(source_dir),
            output_dir=str(output_dir),
            total_nodes=len(node_order),
            cursor=0,
            node_order=node_order,
            decisions={},
            created=now,
            updated=now,
        )
        return cls(state=state, nodes=nodes, state_path=state_path)

    def current_node(self) -> GraphNode:
        """Return the node at the current cursor position."""
        if self.state.cursor >= len(self.state.node_order):
            msg = (
                f"All {self.state.total_nodes} nodes have been reviewed "
                f"(cursor={self.state.cursor})"
            )
            raise IndexError(msg)
        node_id = self.state.node_order[self.state.cursor]
        node, _ = self._nodes[node_id]
        return node

    def record_decision(
        self,
        node_id: str,
        decision: CurationDecision,
        reason: str | None = None,
        edits: dict[str, Any] | None = None,
    ) -> None:
        """Record a curation decision for *node_id* and advance cursor."""
        if node_id not in self._nodes:
            msg = f"Unknown node: {node_id}"
            raise ValueError(msg)
        expected_id = self.state.node_order[self.state.cursor]
        if node_id != expected_id:
            msg = (
                f"Expected decision for {expected_id!r} at cursor "
                f"{self.state.cursor}, got {node_id!r}"
            )
            raise ValueError(msg)
        _, file_hash = self._nodes[node_id]
        now = datetime.now(tz=UTC)
        self.state.decisions[node_id] = NodeDecision(
            node_id=node_id,
            decision=decision,
            reason=reason,
            edits=edits,
            original_hash=file_hash,
            timestamp=now,
        )
        self.state.cursor += 1
        self.state.updated = now
        self._save_state()

    def skip(self) -> None:
        """Skip the current node without recording a decision."""
        self.state.cursor += 1
        self.state.updated = datetime.now(tz=UTC)
        self._save_state()

    def summary(self) -> CurationSummary:
        """Return aggregate counts for the current session."""
        return CurationSummary.from_state(self.state)

    def write_curated(self) -> int:
        """Write accepted and edited nodes to the output directory.

        Returns the number of files written.
        """
        out = Path(self.state.output_dir)
        out.mkdir(parents=True, exist_ok=True)

        written = 0
        for node_id, nd in self.state.decisions.items():
            if nd.decision == CurationDecision.REJECTED:
                continue

            node, _ = self._nodes[node_id]

            if nd.decision == CurationDecision.EDITED and nd.edits:
                node = node.model_copy(update=nd.edits)

            data = [node.model_dump(mode="json")]
            json_text = json.dumps(data, indent=2, ensure_ascii=False)

            target = out / f"{node_id}.json"
            _atomic_write(target, json_text)
            written += 1

        return written

    def _save_state(self) -> None:
        data = self.state.model_dump(mode="json")
        yaml_text = yaml.dump(data, sort_keys=False, allow_unicode=True)
        _atomic_write(self._state_path, yaml_text)


def _load_nodes_from_dir(directory: Path) -> dict[str, tuple[GraphNode, str]]:
    """Load GraphNode instances from JSON files in *directory*."""
    nodes: dict[str, tuple[GraphNode, str]] = {}
    for json_path in sorted(directory.glob("*.json")):
        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
            items = raw if isinstance(raw, list) else [raw]
            file_hash = hashlib.sha256(json_path.read_bytes()).hexdigest()
            for item in items:
                if isinstance(item, dict) and "id" in item:
                    node = GraphNode.model_validate(item)
                    nodes[node.id] = (node, file_hash)
        except (json.JSONDecodeError, OSError) as exc:
            _log.warning("Skipped %s: %s", json_path.name, exc)
    return nodes


def _atomic_write(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(dir=target.parent, suffix=".tmp", text=True)
    tmp_path = Path(tmp_name)
    try:
        with open(tmp_fd, "w") as fh:
            fh.write(content)
        tmp_path.rename(target)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise


__all__ = [
    "CurationDecision",
    "CurationSession",
    "CurationSessionState",
    "CurationSummary",
    "NodeDecision",
]
