"""Tests for GovernanceParser wrapper classes.

Validates that each wrapper conforms to the GovernanceParser Protocol
and produces GraphNode results from ArtifactLocator inputs.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.adapters.protocols import GovernanceParser
from raise_core.graph.models import GraphNode

# --- Fixtures ---


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a project root with governance files for testing."""
    # PRD
    prd = tmp_path / "governance" / "prd.md"
    prd.parent.mkdir(parents=True, exist_ok=True)
    prd.write_text(
        dedent("""\
        # PRD

        ## Requirements

        ### RF-01: Test Requirement
        The system MUST do X.
    """)
    )

    # Vision — parser detects table when row has | ** AND "context" or "outcome"
    vision = tmp_path / "governance" / "vision.md"
    vision.write_text(
        dedent("""\
        # Vision

        ## Outcomes

        | **Outcome** | Descripción |
        |---------|-------------|
        | **Extensibility** | Plugins can extend the system |
        | **Observability** | System shows its work |
    """)
    )

    # Constitution
    const = tmp_path / "framework" / "reference" / "constitution.md"
    const.parent.mkdir(parents=True, exist_ok=True)
    const.write_text(
        dedent("""\
        # Constitution

        ## Principles

        ### §1. Honesty
        Tell the truth.
    """)
    )

    # Roadmap
    roadmap = tmp_path / "governance" / "roadmap.md"
    roadmap.write_text(
        dedent("""\
        # Roadmap

        ## Releases

        | ID | Release | Target | Status | Epics |
        |----|---------|--------|--------|-------|
        | REL-1 | **v2.0** | 2026-02-15 | ✅ Released | E14, E7 |
    """)
    )

    # Backlog
    backlog = tmp_path / "governance" / "backlog.md"
    backlog.write_text(
        dedent("""\
        # Backlog

        ## Project
        - **Name:** TestProject
        - **Version:** 1.0

        ## Epics

        | ID | Epic | Status |
        |----|------|--------|
        | E1 | First Epic | ✅ Complete |
    """)
    )

    # Epic scope — dir name must match e(\d+) pattern
    epic_dir = tmp_path / "work" / "epics" / "e1-test"
    epic_dir.mkdir(parents=True, exist_ok=True)
    scope = epic_dir / "scope.md"
    scope.write_text(
        dedent("""\
        ---
        epic_id: "RAISE-1"
        title: "Test Epic"
        status: "complete"
        stories_count: 1
        ---

        # Epic Scope: Test Epic

        > **Status:** COMPLETE

        ## Stories

        | ID | Story | Size | Status |
        |----|-------|------|--------|
        | S1.1 | Test Story | S | Done ✓ |
    """)
    )

    # ADR
    adr_dir = tmp_path / "governance" / "adrs"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr = adr_dir / "adr-026-filtered-github-mirror.md"
    adr.write_text(
        dedent("""\
        ---
        id: ADR-026
        title: Test Decision
        status: accepted
        date: 2026-01-01
        ---

        # ADR-026: Test Decision

        ## Decision
        We decided to test.
    """)
    )

    # Guardrails
    guardrails = tmp_path / "governance" / "guardrails.md"
    guardrails.write_text(
        dedent("""\
        # Guardrails

        ### Code Quality

        | ID | Level | Guardrail | Verificación | Derived From |
        |----|-------|-----------|--------------|--------------|
        | `MUST-CODE-001` | MUST | Type hints | `pyright` | §1 |
    """)
    )

    # Glossary
    glossary = tmp_path / "framework" / "reference" / "glossary.md"
    glossary.write_text(
        dedent("""\
        # Glossary

        ## Términos Core de RaiSE

        ### Agent (Agente)
        A software entity that acts autonomously.
    """)
    )

    return tmp_path


def _make_locator(artifact_type: str, path: str, project_root: Path) -> ArtifactLocator:
    """Helper to create an ArtifactLocator with project_root in metadata."""
    return ArtifactLocator(
        path=path,
        artifact_type=artifact_type,
        metadata={"project_root": str(project_root)},
    )


# --- Protocol conformance ---


class TestProtocolConformance:
    """All parser wrappers satisfy the GovernanceParser Protocol."""

    @pytest.mark.parametrize(
        "parser_class_path",
        [
            "raise_cli.governance.parsers.prd:PrdParser",
            "raise_cli.governance.parsers.vision:VisionParser",
            "raise_cli.governance.parsers.constitution:ConstitutionParser",
            "raise_cli.governance.parsers.roadmap:RoadmapParser",
            "raise_cli.governance.parsers.backlog:BacklogParser",
            "raise_cli.governance.parsers.epic:EpicScopeParser",
            "raise_cli.governance.parsers.adr:AdrParser",
            "raise_cli.governance.parsers.guardrails:GuardrailsParser",
            "raise_cli.governance.parsers.glossary:GlossaryParser",
        ],
    )
    def test_conforms_to_protocol(self, parser_class_path: str) -> None:
        """Each wrapper is a runtime-checkable GovernanceParser."""
        module_path, class_name = parser_class_path.rsplit(":", 1)
        import importlib

        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        instance = cls()
        assert isinstance(instance, GovernanceParser)


# --- can_parse ---


class TestCanParse:
    """Wrappers correctly match their artifact type."""

    @pytest.mark.parametrize(
        ("parser_import", "matching_type", "non_matching_type"),
        [
            (
                "raise_cli.governance.parsers.prd:PrdParser",
                CoreArtifactType.PRD,
                CoreArtifactType.VISION,
            ),
            (
                "raise_cli.governance.parsers.vision:VisionParser",
                CoreArtifactType.VISION,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.constitution:ConstitutionParser",
                CoreArtifactType.CONSTITUTION,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.roadmap:RoadmapParser",
                CoreArtifactType.ROADMAP,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.backlog:BacklogParser",
                CoreArtifactType.BACKLOG,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.epic:EpicScopeParser",
                CoreArtifactType.EPIC_SCOPE,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.adr:AdrParser",
                CoreArtifactType.ADR,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.guardrails:GuardrailsParser",
                CoreArtifactType.GUARDRAILS,
                CoreArtifactType.PRD,
            ),
            (
                "raise_cli.governance.parsers.glossary:GlossaryParser",
                CoreArtifactType.GLOSSARY,
                CoreArtifactType.PRD,
            ),
        ],
    )
    def test_matches_own_type_rejects_other(
        self,
        parser_import: str,
        matching_type: str,
        non_matching_type: str,
    ) -> None:
        """Parser accepts its own type and rejects others."""
        import importlib

        module_path, class_name = parser_import.rsplit(":", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        parser = cls()

        matching = ArtifactLocator(path="test.md", artifact_type=matching_type)
        non_matching = ArtifactLocator(path="test.md", artifact_type=non_matching_type)

        assert parser.can_parse(matching) is True
        assert parser.can_parse(non_matching) is False


# --- parse() produces GraphNode ---


class TestParse:
    """Each wrapper produces list[GraphNode] from valid input."""

    def test_prd_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.prd import PrdParser

        parser = PrdParser()
        locator = _make_locator(CoreArtifactType.PRD, "governance/prd.md", project_root)
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        assert nodes[0].type == "requirement"

    def test_vision_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.vision import VisionParser

        parser = VisionParser()
        locator = _make_locator(
            CoreArtifactType.VISION, "governance/vision.md", project_root
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        assert nodes[0].type == "outcome"

    def test_constitution_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.constitution import ConstitutionParser

        parser = ConstitutionParser()
        locator = _make_locator(
            CoreArtifactType.CONSTITUTION,
            "framework/reference/constitution.md",
            project_root,
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        assert nodes[0].type == "principle"

    def test_roadmap_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.roadmap import RoadmapParser

        parser = RoadmapParser()
        locator = _make_locator(
            CoreArtifactType.ROADMAP, "governance/roadmap.md", project_root
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        assert nodes[0].type == "release"

    def test_backlog_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.backlog import BacklogParser

        parser = BacklogParser()
        locator = _make_locator(
            CoreArtifactType.BACKLOG, "governance/backlog.md", project_root
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        # Backlog produces project and/or epic nodes
        node_types = {n.type for n in nodes}
        assert node_types & {"project", "epic"}

    def test_epic_scope_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.epic import EpicScopeParser

        parser = EpicScopeParser()
        locator = _make_locator(
            CoreArtifactType.EPIC_SCOPE,
            "work/epics/e1-test/scope.md",
            project_root,
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        node_types = {n.type for n in nodes}
        assert node_types & {"epic", "story"}

    def test_adr_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.adr import AdrParser

        parser = AdrParser()
        locator = _make_locator(
            CoreArtifactType.ADR,
            "governance/adrs/adr-026-filtered-github-mirror.md",
            project_root,
        )
        nodes = parser.parse(locator)

        assert len(nodes) == 1
        assert nodes[0].type == "decision"
        assert nodes[0].metadata["adr_id"] == "ADR-026"

    def test_guardrails_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.guardrails import GuardrailsParser

        parser = GuardrailsParser()
        locator = _make_locator(
            CoreArtifactType.GUARDRAILS,
            "governance/guardrails.md",
            project_root,
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        assert nodes[0].type == "guardrail"

    def test_glossary_parser(self, project_root: Path) -> None:
        from raise_cli.governance.parsers.glossary import GlossaryParser

        parser = GlossaryParser()
        locator = _make_locator(
            CoreArtifactType.GLOSSARY,
            "framework/reference/glossary.md",
            project_root,
        )
        nodes = parser.parse(locator)

        assert len(nodes) >= 1
        assert all(isinstance(n, GraphNode) for n in nodes)
        assert nodes[0].type == "term"

    def test_parse_nonexistent_file_returns_empty(self, tmp_path: Path) -> None:
        """Parser returns empty list for missing file, not an exception."""
        from raise_cli.governance.parsers.prd import PrdParser

        parser = PrdParser()
        locator = _make_locator(CoreArtifactType.PRD, "nonexistent.md", tmp_path)
        nodes = parser.parse(locator)

        assert nodes == []
