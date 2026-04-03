"""Tests for knowledge discovery models and diff functions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from rai_agent.knowledge.discovery import (
    DISCOVERY_PROMPT,
    NodeTypeSpec,
    SchemaSpec,
    diff_nodes,
    diff_schemas,
    discover_schema,
    reconcile_extracted,
    refine_schema,
)

# --- Model construction ---


class TestSchemaSpec:
    def test_basic_construction(self) -> None:
        spec = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="concept", fields=["name", "summary"]),
                NodeTypeSpec(name="tool", fields=["name", "steps"]),
            ],
            relationship_types=["belongs_to", "requires"],
        )
        assert len(spec.node_types) == 2
        assert len(spec.relationship_types) == 2

    def test_empty_spec(self) -> None:
        spec = SchemaSpec(node_types=[], relationship_types=[])
        assert spec.node_types == []


class TestNodeTypeSpec:
    def test_construction(self) -> None:
        nts = NodeTypeSpec(name="tool", fields=["name", "decision", "steps"])
        assert nts.name == "tool"
        assert "steps" in nts.fields


# --- diff_schemas ---


class TestDiffSchemas:
    def test_full_overlap(self) -> None:
        """All discovered types match reference model."""
        spec = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="concept", fields=["name", "summary", "tags"]),
            ],
            relationship_types=[],
        )
        # Use a simple reference model with known fields
        report = diff_schemas(spec, _FakeRefModel)
        assert "concept" in report.types_both

    def test_discovered_only_types(self) -> None:
        spec = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="principle", fields=["name"]),
            ],
            relationship_types=[],
        )
        report = diff_schemas(spec, _FakeRefModel)
        assert "principle" in report.types_only_discovered

    def test_reference_only_types(self) -> None:
        spec = SchemaSpec(node_types=[], relationship_types=[])
        report = diff_schemas(spec, _FakeRefModel)
        assert len(report.types_only_reference) > 0

    def test_field_diffs(self) -> None:
        spec = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="concept", fields=["name", "custom_field"]),
            ],
            relationship_types=[],
        )
        report = diff_schemas(spec, _FakeRefModel)
        assert "concept" in report.field_diffs
        fd = report.field_diffs["concept"]
        assert "name" in fd.common
        assert "custom_field" in fd.only_discovered

    def test_empty_spec_vs_model(self) -> None:
        spec = SchemaSpec(node_types=[], relationship_types=[])
        report = diff_schemas(spec, _FakeRefModel)
        assert report.types_both == []
        assert report.types_only_discovered == []


# --- diff_nodes ---


class TestDiffNodes:
    def test_full_overlap(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        cur_dir = tmp_path / "curated"
        ext_dir.mkdir()
        cur_dir.mkdir()

        _write_node(ext_dir / "tool-opsp.yaml", "tool-opsp", "tool")
        _write_node(cur_dir / "tool-opsp.yaml", "tool-opsp", "tool")

        report = diff_nodes(ext_dir, cur_dir)
        assert "tool-opsp" in report.nodes_both
        assert report.nodes_only_extracted == []
        assert report.nodes_only_curated == []
        assert report.overlap_pct == pytest.approx(1.0)

    def test_disjoint_sets(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        cur_dir = tmp_path / "curated"
        ext_dir.mkdir()
        cur_dir.mkdir()

        _write_node(ext_dir / "concept-bhag.yaml", "concept-bhag", "concept")
        _write_node(cur_dir / "tool-opsp.yaml", "tool-opsp", "tool")

        report = diff_nodes(ext_dir, cur_dir)
        assert report.nodes_both == []
        assert "concept-bhag" in report.nodes_only_extracted
        assert "tool-opsp" in report.nodes_only_curated
        assert report.overlap_pct == pytest.approx(0.0)

    def test_partial_overlap(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        cur_dir = tmp_path / "curated"
        ext_dir.mkdir()
        cur_dir.mkdir()

        _write_node(ext_dir / "tool-opsp.yaml", "tool-opsp", "tool")
        _write_node(ext_dir / "concept-bhag.yaml", "concept-bhag", "concept")
        _write_node(cur_dir / "tool-opsp.yaml", "tool-opsp", "tool")
        _write_node(cur_dir / "metric-sat.yaml", "metric-sat", "metric")

        report = diff_nodes(ext_dir, cur_dir)
        assert "tool-opsp" in report.nodes_both
        assert "concept-bhag" in report.nodes_only_extracted
        assert "metric-sat" in report.nodes_only_curated
        assert report.total_extracted == 2
        assert report.total_curated == 2

    def test_empty_dirs(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        cur_dir = tmp_path / "curated"
        ext_dir.mkdir()
        cur_dir.mkdir()

        report = diff_nodes(ext_dir, cur_dir)
        assert report.nodes_both == []
        assert report.total_extracted == 0
        assert report.total_curated == 0

    def test_by_decision_breakdown(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        cur_dir = tmp_path / "curated"
        ext_dir.mkdir()
        cur_dir.mkdir()

        _write_node(ext_dir / "tool-ccc.yaml", "tool-ccc", "tool", decision="cash")
        _write_node(
            ext_dir / "concept-cv.yaml", "concept-cv", "concept", decision="people"
        )
        _write_node(cur_dir / "tool-ccc.yaml", "tool-ccc", "tool", decision="cash")

        report = diff_nodes(ext_dir, cur_dir)
        assert report.by_decision is not None
        assert "cash" in report.by_decision

    def test_nested_curated_dirs(self, tmp_path: Path) -> None:
        """Eduardo's curated nodes are in nested subdirs (people/concepts/, cash/tools/)."""
        ext_dir = tmp_path / "extracted"
        cur_dir = tmp_path / "curated"
        ext_dir.mkdir()
        (cur_dir / "people" / "concepts").mkdir(parents=True)

        _write_node(ext_dir / "concept-cv.yaml", "concept-cv", "concept")
        _write_node(
            cur_dir / "people" / "concepts" / "concept-cv.yaml", "concept-cv", "concept"
        )

        report = diff_nodes(ext_dir, cur_dir)
        assert "concept-cv" in report.nodes_both


# --- Helpers ---


class _FakeRefModel:
    """Simulates a Pydantic model with known fields for diff_schemas tests."""

    # diff_schemas extracts node types from a Literal type annotation
    # We simulate OntologyNode's structure
    __annotations__: dict[str, Any] = {
        "id": str,
        "type": str,
        "name": str,
        "summary": str,
        "decision": str,
        "tags": list,
    }

    # Simulated node types (what OntologyNode.type accepts)
    _node_types: list[str] = ["concept", "tool", "decision", "worksheet"]
    _fields: dict[str, list[str]] = {
        "concept": ["id", "type", "name", "summary", "decision", "tags"],
        "tool": ["id", "type", "name", "summary", "decision", "tags"],
        "decision": ["id", "type", "name", "summary", "decision", "tags"],
        "worksheet": ["id", "type", "name", "summary", "decision", "tags"],
    }


def _write_node(
    path: Path, node_id: str, node_type: str, decision: str | None = None
) -> None:
    data: dict[str, Any] = {"id": node_id, "type": node_type, "name": node_id}
    if decision:
        data["decision"] = decision
    path.write_text(yaml.dump(data))


# --- discover_schema ---


SAMPLE_CORPUS = """\
# People
Hiring A-players with Topgrading. Core Values define culture.

# Strategy
Brand Promise and BHAG drive differentiation.

# Cash
Cash Conversion Cycle and Power of One for financial levers.
"""


class TestDiscoverSchema:
    @pytest.fixture
    def corpus_path(self, tmp_path: Path) -> Path:
        p = tmp_path / "corpus.md"
        p.write_text(SAMPLE_CORPUS)
        return p

    def test_returns_schema_spec(self, corpus_path: Path) -> None:
        """discover_schema returns a SchemaSpec with mocked LLM."""
        canned = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="concept", fields=["name", "summary"]),
                NodeTypeSpec(name="tool", fields=["name", "steps"]),
            ],
            relationship_types=["belongs_to", "requires"],
        )
        factory = _make_mock_factory(canned.model_dump_json())
        result = discover_schema(corpus_path, client=factory)
        assert isinstance(result, SchemaSpec)
        assert len(result.node_types) == 2

    def test_prompt_does_not_leak_schema(self) -> None:
        """Discovery prompt must not mention OntologyNode or Eduardo's field names."""
        prompt_lower = DISCOVERY_PROMPT.lower()
        assert "ontologynode" not in prompt_lower
        assert "name_es" not in prompt_lower
        assert "eduardo" not in prompt_lower

    def test_corpus_with_braces(self, tmp_path: Path) -> None:
        """Corpus containing {braces} must not crash the prompt formatter."""
        p = tmp_path / "braces.md"
        p.write_text("# Chapter\nUse {tool_name} for {purpose}.\n")
        canned = SchemaSpec(node_types=[], relationship_types=[])
        factory = _make_mock_factory(canned.model_dump_json())
        result = discover_schema(p, client=factory)
        assert isinstance(result, SchemaSpec)

    def test_empty_corpus_raises(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.md"
        empty.write_text("")
        factory = _make_mock_factory("{}")
        with pytest.raises(ValueError, match="[Ee]mpty"):
            discover_schema(empty, client=factory)


class TestReconcileExtracted:
    def test_creates_missing_decision_nodes(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        ext_dir.mkdir()
        # Only decision-people exists
        _write_node(
            ext_dir / "decision-people.yaml",
            "decision-people",
            "decision",
            decision="people",
        )
        _write_node(
            ext_dir / "concept-x.yaml", "concept-x", "concept", decision="strategy"
        )

        report = reconcile_extracted(ext_dir, {})
        assert "decision-strategy" in report.nodes_created
        assert "decision-execution" in report.nodes_created
        assert "decision-cash" in report.nodes_created
        assert "decision-people" not in report.nodes_created  # already existed
        assert (ext_dir / "decision-strategy.yaml").exists()

    def test_resolves_broken_refs(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        ext_dir.mkdir()
        # Node with broken ref to decision-execution
        data: dict[str, Any] = {
            "id": "concept-x",
            "type": "concept",
            "name": "X",
            "relationships": [{"type": "belongs-to", "target": "decision-execution"}],
        }
        (ext_dir / "concept-x.yaml").write_text(yaml.dump(data))

        report = reconcile_extracted(ext_dir, {})
        # decision-execution should be created, ref should resolve
        assert report.total_broken_after == 0
        assert "decision-execution" in report.nodes_created

    def test_removes_unresolvable_refs(self, tmp_path: Path) -> None:
        ext_dir = tmp_path / "extracted"
        ext_dir.mkdir()
        data: dict[str, Any] = {
            "id": "concept-x",
            "type": "concept",
            "name": "X",
            "relationships": [{"type": "requires", "target": "nonexistent-xyz"}],
        }
        (ext_dir / "concept-x.yaml").write_text(yaml.dump(data))

        report = reconcile_extracted(ext_dir, {})
        assert report.refs_removed >= 1
        # Check file was updated
        updated = yaml.safe_load((ext_dir / "concept-x.yaml").read_text())
        assert len(updated["relationships"]) == 0


class TestRefineSchema:
    @pytest.fixture
    def corpus_path(self, tmp_path: Path) -> Path:
        p = tmp_path / "corpus.md"
        p.write_text(SAMPLE_CORPUS)
        return p

    def test_adds_missing_types(self, corpus_path: Path) -> None:
        """Refinement adds types that exist in reference but not in discovered."""
        initial = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="concept", fields=["name", "summary"]),
                NodeTypeSpec(name="tool", fields=["name", "steps"]),
            ],
            relationship_types=["belongs_to"],
        )
        # LLM "finds" worksheet and stage in refinement
        refinement_response = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="worksheet", fields=["name", "purpose", "sections"]),
                NodeTypeSpec(name="stage", fields=["name", "characteristics"]),
            ],
            relationship_types=["fills_out"],
        )
        factory = _make_mock_factory(refinement_response.model_dump_json())
        missing_types = ["worksheet", "stage"]

        result = refine_schema(
            initial_schema=initial,
            missing_types=missing_types,
            corpus_path=corpus_path,
            client=factory,
        )

        type_names = {nt.name for nt in result.node_types}
        assert "concept" in type_names  # kept from initial
        assert "tool" in type_names  # kept from initial
        assert "worksheet" in type_names  # added from refinement
        assert "stage" in type_names  # added from refinement

    def test_merges_relationship_types(self, corpus_path: Path) -> None:
        """Refinement merges new relationship types without duplicates."""
        initial = SchemaSpec(
            node_types=[NodeTypeSpec(name="concept", fields=["name"])],
            relationship_types=["belongs_to", "requires"],
        )
        refinement_response = SchemaSpec(
            node_types=[
                NodeTypeSpec(name="worksheet", fields=["name"]),
            ],
            relationship_types=["requires", "fills_out"],  # "requires" is a dupe
        )
        factory = _make_mock_factory(refinement_response.model_dump_json())

        result = refine_schema(
            initial_schema=initial,
            missing_types=["worksheet"],
            corpus_path=corpus_path,
            client=factory,
        )

        assert sorted(result.relationship_types) == [
            "belongs_to",
            "fills_out",
            "requires",
        ]

    def test_no_missing_returns_initial(self, corpus_path: Path) -> None:
        """If no types are missing, returns initial schema unchanged."""
        initial = SchemaSpec(
            node_types=[NodeTypeSpec(name="concept", fields=["name"])],
            relationship_types=["belongs_to"],
        )

        result = refine_schema(
            initial_schema=initial,
            missing_types=[],
            corpus_path=corpus_path,
        )

        assert result == initial


def _make_mock_factory(response_json: str) -> Any:
    """Create a factory for invoke_structured's _client_factory that yields canned text."""
    from dataclasses import dataclass
    from dataclasses import field as dc_field

    @dataclass
    class _FakeTextBlock:
        text: str
        type: str = "text"

    @dataclass
    class _FakeAssistantMessage:
        content: list[Any] = dc_field(default_factory=list)
        type: str = "assistant"

    @dataclass
    class _FakeResultMessage:
        session_id: str = "test-session"
        type: str = "result"

    async def fake_query(prompt: str, options: Any) -> Any:  # noqa: ANN401
        msg = _FakeAssistantMessage(content=[_FakeTextBlock(text=response_json)])
        yield msg
        yield _FakeResultMessage()

    def factory() -> Any:
        return fake_query

    return factory
