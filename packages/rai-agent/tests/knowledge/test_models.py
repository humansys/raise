"""Tests for knowledge domain models."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003

from pydantic import BaseModel

from rai_agent.knowledge.models import (
    DomainManifest,
    GateConfig,
    GateResult,
    SchemaRef,
)


class TestGateResult:
    def test_create_passing(self) -> None:
        result = GateResult(
            gate="validate",
            domain="test",
            passed=True,
            metrics={"valid": 10, "invalid": 0},
            errors=[],
            warnings=[],
            duration_ms=42.0,
        )
        assert result.passed
        assert result.gate == "validate"
        assert result.metrics["valid"] == 10

    def test_create_failing(self) -> None:
        result = GateResult(
            gate="validate",
            domain="test",
            passed=False,
            metrics={"valid": 8, "invalid": 2},
            errors=["node-x.yaml: missing 'type'"],
            warnings=[],
            duration_ms=15.0,
        )
        assert not result.passed
        assert len(result.errors) == 1

    def test_json_serialization(self) -> None:
        result = GateResult(
            gate="reconcile",
            domain="test",
            passed=True,
            metrics={"phantoms": 0},
            errors=[],
            warnings=["2 orphan nodes"],
            duration_ms=8.3,
        )
        data = result.model_dump()
        assert data["gate"] == "reconcile"
        assert data["warnings"] == ["2 orphan nodes"]

        json_str = result.model_dump_json()
        assert '"gate":"reconcile"' in json_str or '"gate": "reconcile"' in json_str


class TestSchemaRef:
    def test_create(self) -> None:
        ref = SchemaRef(
            module="rai_agent.scaleup.validation.models",
            class_name="OntologyNode",
        )
        assert ref.module == "rai_agent.scaleup.validation.models"
        assert ref.class_name == "OntologyNode"


class TestDomainManifest:
    def test_create_minimal(self) -> None:
        manifest = DomainManifest(
            name="test",
            display_name="Test",
            node_schema=SchemaRef(module="some.module", class_name="SomeModel"),
        )
        assert manifest.name == "test"
        assert manifest.thresholds == {"cq_coverage": 80.0}
        assert manifest.required_types == set()

    def test_create_full(self) -> None:
        manifest = DomainManifest(
            name="scaleup",
            display_name="Scaling Up",
            node_schema=SchemaRef(
                module="rai_agent.scaleup.validation.models",
                class_name="OntologyNode",
            ),
            corpus=["book.md", "workbooks/"],
            competency_questions="cqs.yaml",
            thresholds={"cq_coverage": 90.0},
            required_types={"decision", "concept", "tool"},
        )
        assert manifest.competency_questions == "cqs.yaml"
        assert manifest.thresholds["cq_coverage"] == 90.0
        assert "tool" in manifest.required_types

    def test_create_from_yaml_alias(self) -> None:
        """domain.yaml uses 'schema' key, which maps to node_schema."""
        data = {
            "name": "test",
            "display_name": "Test",
            "schema": {"module": "some.mod", "class_name": "Cls"},
        }
        manifest = DomainManifest.model_validate(data)
        assert manifest.node_schema.module == "some.mod"


class TestGateConfig:
    def test_create_with_model(self) -> None:
        class FakeModel(BaseModel):
            id: str

        config = GateConfig(
            node_model=FakeModel,
            node_dir=Path("/tmp/nodes"),
        )
        assert config.node_model is FakeModel
        assert config.cq_threshold == 80.0

    def test_create_full(self) -> None:
        class FakeModel(BaseModel):
            id: str

        config = GateConfig(
            node_model=FakeModel,
            cq_file=Path("cqs.yaml"),
            cq_threshold=90.0,
            required_types={"concept", "tool"},
            node_dir=Path("/tmp/nodes"),
        )
        assert config.cq_threshold == 90.0
        assert "concept" in config.required_types
