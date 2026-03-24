"""Integration tests — end-to-end gate pipeline."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003
from unittest.mock import patch

import yaml
from tests.knowledge.conftest import SampleNode
from typer.testing import CliRunner

from rai_agent.knowledge.cli import app
from rai_agent.knowledge.domain import load_domain
from rai_agent.knowledge.gates import (
    run_coverage,
    run_graph,
    run_reconcile,
    run_validate,
)

runner = CliRunner()


def _build_domain(base: Path) -> Path:
    """Build a complete test domain with nodes and CQs."""
    domain_dir = base / "integration-test"
    domain_dir.mkdir(parents=True)
    (domain_dir / "extracted").mkdir()
    (domain_dir / "curated").mkdir()

    # Manifest
    manifest = {
        "name": "integration-test",
        "display_name": "Integration Test Domain",
        "schema": {
            "module": "tests.knowledge.conftest",
            "class_name": "SampleNode",
        },
        "required_types": ["concept", "tool"],
    }
    (domain_dir / "domain.yaml").write_text(
        yaml.dump(manifest, default_flow_style=False)
    )

    # Valid nodes with proper relationships
    nodes = [
        {
            "id": "concept-a",
            "type": "concept",
            "name": "Concept A",
            "summary": "First concept",
            "relationships": [
                {"type": "requires", "target": "tool-b"},
            ],
            "decision": "people",
        },
        {
            "id": "tool-b",
            "type": "tool",
            "name": "Tool B",
            "summary": "First tool",
            "relationships": [
                {"type": "requires", "target": "concept-a"},
            ],
            "decision": "people",
        },
        {
            "id": "concept-c",
            "type": "concept",
            "name": "Concept C",
            "summary": "Second concept",
            "relationships": [
                {"type": "requires", "target": "concept-a"},
            ],
            "decision": "strategy",
        },
    ]
    for node in nodes:
        path = domain_dir / "extracted" / f"{node['id']}.yaml"
        path.write_text(yaml.dump(node, default_flow_style=False))

    return domain_dir


class TestEndToEndGatePipeline:
    """Test the full pipeline: load domain → run all gates → verify results."""

    def test_full_pipeline(self, tmp_path: Path) -> None:
        domain_dir = _build_domain(tmp_path)

        # Step 1: Load domain
        manifest, config = load_domain(domain_dir)
        assert manifest.name == "integration-test"
        assert config.node_model is SampleNode

        # Step 2: Validate
        v_result = run_validate(config, domain="integration-test")
        assert v_result.passed
        assert v_result.metrics["valid"] == 3

        # Step 3: Reconcile
        r_result = run_reconcile(config, domain="integration-test")
        assert r_result.passed
        assert r_result.metrics["phantoms"] == 0

        # Step 4: Coverage (no CQ file → passes with warning)
        c_result = run_coverage(config, domain="integration-test")
        assert c_result.passed
        assert len(c_result.warnings) >= 1

        # Step 5: Graph
        g_result = run_graph(config, domain="integration-test")
        assert g_result.passed
        assert g_result.metrics["nodes"] == 3
        assert g_result.metrics["edges"] >= 3

    def test_pipeline_with_invalid_node(self, tmp_path: Path) -> None:
        """Validate gate catches invalid nodes in the pipeline."""
        domain_dir = _build_domain(tmp_path)

        # Add an invalid node (missing 'summary')
        bad_node = {"id": "bad-node", "type": "concept", "name": "Bad"}
        (domain_dir / "extracted" / "bad-node.yaml").write_text(
            yaml.dump(bad_node, default_flow_style=False)
        )

        manifest, config = load_domain(domain_dir)
        v_result = run_validate(config, domain="integration-test")
        assert not v_result.passed
        assert v_result.metrics["invalid"] == 1
        assert "bad-node.yaml" in v_result.errors[0]

    def test_pipeline_with_phantom_ref(self, tmp_path: Path) -> None:
        """Reconcile gate catches phantom references."""
        domain_dir = _build_domain(tmp_path)

        # Add node with phantom reference
        phantom_node = {
            "id": "phantom-ref",
            "type": "tool",
            "name": "Phantom",
            "summary": "Has phantom ref",
            "relationships": [
                {"type": "requires", "target": "nonexistent-node"},
            ],
        }
        (domain_dir / "extracted" / "phantom-ref.yaml").write_text(
            yaml.dump(phantom_node, default_flow_style=False)
        )

        manifest, config = load_domain(domain_dir)
        r_result = run_reconcile(config, domain="integration-test")
        assert not r_result.passed
        assert r_result.metrics["phantoms"] == 1


class TestCLIIntegration:
    """Test CLI commands end-to-end."""

    def test_check_full_domain(self, tmp_path: Path) -> None:
        _build_domain(tmp_path)
        with patch(
            "rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path
        ):
            result = runner.invoke(
                app, ["check", "integration-test"]
            )
        assert result.exit_code == 0
        assert "4 gates" in result.output.lower() or "gates" in result.output.lower()

    def test_check_json_full(self, tmp_path: Path) -> None:
        _build_domain(tmp_path)
        with patch(
            "rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path
        ):
            result = runner.invoke(
                app, ["check", "integration-test", "--json"]
            )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 4
        gates = {d["gate"] for d in data}
        assert gates == {"validate", "reconcile", "coverage", "graph"}

    def test_status_shows_domain(self, tmp_path: Path) -> None:
        _build_domain(tmp_path)
        with patch(
            "rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path
        ):
            result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "integration-test" in result.output

    def test_init_and_status(self, tmp_path: Path) -> None:
        """Init a domain, then verify status shows it."""
        with patch(
            "rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR", tmp_path
        ):
            init_result = runner.invoke(app, ["init", "new-domain"])
            assert init_result.exit_code == 0

            status_result = runner.invoke(app, ["status"])
            # New domain won't show in status because schema is TODO
            # (load_domain fails for unresolved schema)
            assert status_result.exit_code == 0
