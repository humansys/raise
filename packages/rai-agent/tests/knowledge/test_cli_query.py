"""Tests for `rai knowledge query` CLI command.

Requires rai_agent.scaleup (private module, not in monorepo).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
import yaml
from typer.testing import CliRunner

from rai_agent.knowledge.cli import app

if TYPE_CHECKING:
    from pathlib import Path

runner = CliRunner()


def _scaleup_available() -> bool:
    try:
        import rai_agent.scaleup  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


# All tests in this module depend on scaleup fixtures
pytestmark = pytest.mark.skipif(
    not _scaleup_available(),
    reason="rai_agent.scaleup not available (private module)",
)


def _setup_domain(tmp_path: Path, *, with_retrieval: bool = True) -> Path:
    """Create a domain dir with domain.yaml and a few YAML nodes."""
    domain_dir = tmp_path / "scaleup"
    domain_dir.mkdir()
    (domain_dir / "extracted").mkdir()
    (domain_dir / "curated").mkdir()

    manifest: dict[str, object] = {
        "name": "scaleup",
        "display_name": "Scaling Up",
        "schema": {
            "module": "rai_agent.scaleup.validation.models",
            "class_name": "OntologyNode",
        },
    }
    if with_retrieval:
        manifest["retrieval"] = {
            "adapter": {
                "module": "rai_agent.scaleup.retrieval.adapter",
                "class_name": "ScaleUpAdapter",
            },
            "builder": {
                "module": "rai_agent.scaleup.graph.builder",
                "class_name": "ScaleUpGraphBuilder",
            },
        }
        manifest["prompting"] = {
            "system_context": "You are a test expert.",
            "response_format": "1. Answer",
        }

    (domain_dir / "domain.yaml").write_text(
        yaml.dump(manifest, default_flow_style=False, allow_unicode=True)
    )

    # Minimal valid nodes
    for i, decision in enumerate(["people", "cash"]):
        node = {
            "id": f"decision-{decision}",
            "type": "decision",
            "name": decision.title(),
            "name_es": decision.title(),
            "decision": decision,
            "summary": f"The {decision} decision area",
            "relationships": [],
            "source": {"book_chapter": "CH1", "book_line": i + 1},
            "tags": [decision],
        }
        (domain_dir / "extracted" / f"decision-{decision}.yaml").write_text(
            yaml.dump(node, default_flow_style=False, allow_unicode=True)
        )

    tool_node = {
        "id": "tool-cash-accel",
        "type": "tool",
        "name": "Cash Acceleration",
        "name_es": "Aceleración de Efectivo",
        "decision": "cash",
        "summary": "Power of One: 5 cash levers",
        "relationships": [
            {"type": "belongs-to", "target": "decision-cash"},
        ],
        "source": {"book_chapter": "CASH", "book_line": 100},
        "tags": ["cash", "tool"],
    }
    (domain_dir / "extracted" / "tool-cash-accel.yaml").write_text(
        yaml.dump(tool_node, default_flow_style=False, allow_unicode=True)
    )

    return tmp_path


class TestQueryCommand:
    @patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR")
    def test_query_with_explicit_domain(
        self, mock_dir: MagicMock, tmp_path: Path
    ) -> None:
        knowledge_dir = _setup_domain(tmp_path)
        mock_dir.__truediv__ = lambda self, x: knowledge_dir / x  # type: ignore[assignment]
        mock_dir.exists.return_value = True
        mock_dir.iterdir.return_value = list(knowledge_dir.iterdir())

        result = runner.invoke(app, ["query", "scaleup", "cash"])
        assert result.exit_code == 0, result.output
        assert "cash" in result.output.lower()

    @patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR")
    def test_query_json_format(self, mock_dir: MagicMock, tmp_path: Path) -> None:
        import json

        knowledge_dir = _setup_domain(tmp_path)
        mock_dir.__truediv__ = lambda self, x: knowledge_dir / x  # type: ignore[assignment]
        mock_dir.exists.return_value = True
        mock_dir.iterdir.return_value = list(knowledge_dir.iterdir())

        result = runner.invoke(app, ["query", "scaleup", "cash", "--format", "json"])
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        assert "results" in parsed
        assert "prompting" in parsed

    @patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR")
    def test_query_limit(self, mock_dir: MagicMock, tmp_path: Path) -> None:
        import json

        knowledge_dir = _setup_domain(tmp_path)
        mock_dir.__truediv__ = lambda self, x: knowledge_dir / x  # type: ignore[assignment]
        mock_dir.exists.return_value = True
        mock_dir.iterdir.return_value = list(knowledge_dir.iterdir())

        result = runner.invoke(
            app, ["query", "scaleup", "cash", "--format", "json", "--limit", "1"]
        )
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        assert len(parsed["results"]) <= 1

    @patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR")
    def test_query_unknown_domain(self, mock_dir: MagicMock, tmp_path: Path) -> None:
        knowledge_dir = _setup_domain(tmp_path)
        mock_dir.__truediv__ = lambda self, x: knowledge_dir / x  # type: ignore[assignment]

        result = runner.invoke(app, ["query", "nonexistent", "test"])
        assert result.exit_code != 0

    @patch("rai_agent.knowledge.cli._DEFAULT_KNOWLEDGE_DIR")
    def test_query_auto_detect_domain(
        self, mock_dir: MagicMock, tmp_path: Path
    ) -> None:
        knowledge_dir = _setup_domain(tmp_path)
        mock_dir.__truediv__ = lambda self, x: knowledge_dir / x  # type: ignore[assignment]
        mock_dir.exists.return_value = True
        mock_dir.iterdir.return_value = list(knowledge_dir.iterdir())

        result = runner.invoke(app, ["query", "cash tools"])
        assert result.exit_code == 0, result.output
