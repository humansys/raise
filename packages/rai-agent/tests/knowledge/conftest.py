"""Fixtures for knowledge domain tests."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Any

import pytest
import yaml
from pydantic import BaseModel


class SampleNode(BaseModel):
    """Minimal node model for testing — mimics OntologyNode structure."""

    id: str
    type: str
    name: str
    summary: str
    relationships: list[dict[str, str]] = []
    decision: str | None = None
    tags: list[str] = []


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))


@pytest.fixture
def sample_domain_dir(tmp_path: Path) -> Path:
    """Create a sample domain directory with domain.yaml and a few nodes."""
    domain_dir = tmp_path / "test-domain"
    domain_dir.mkdir()

    # domain.yaml
    manifest = {
        "name": "test",
        "display_name": "Test Domain",
        "schema": {
            "module": "tests.knowledge.conftest",
            "class_name": "SampleNode",
        },
        "corpus": ["corpus.md"],
        "competency_questions": "cqs.yaml",
        "thresholds": {"cq_coverage": 80.0},
        "required_types": ["concept", "tool"],
    }
    _write_yaml(domain_dir / "domain.yaml", manifest)

    # Sample nodes in extracted/
    extracted = domain_dir / "extracted"
    extracted.mkdir()
    _write_yaml(
        extracted / "concept-foo.yaml",
        {
            "id": "concept-foo",
            "type": "concept",
            "name": "Foo Concept",
            "summary": "A test concept",
            "relationships": [{"type": "belongs-to", "target": "decision-test"}],
            "decision": "people",
        },
    )
    _write_yaml(
        extracted / "tool-bar.yaml",
        {
            "id": "tool-bar",
            "type": "tool",
            "name": "Bar Tool",
            "summary": "A test tool",
            "relationships": [
                {"type": "belongs-to", "target": "decision-test"},
                {"type": "requires", "target": "concept-foo"},
            ],
            "decision": "people",
        },
    )

    # Empty curated/
    (domain_dir / "curated").mkdir()

    return domain_dir


@pytest.fixture
def sample_cqs_file(sample_domain_dir: Path) -> Path:
    """Create a sample competency questions file."""
    cqs = [
        {
            "id": "CQ-001",
            "question": "What tools exist?",
            "decision": "people",
            "expected_path": "decision(people) <- belongs-to <- tool[*]",
            "expected_min_results": 1,
        },
    ]
    cq_path = sample_domain_dir / "cqs.yaml"
    cq_path.write_text(yaml.dump(cqs, default_flow_style=False))
    return cq_path
