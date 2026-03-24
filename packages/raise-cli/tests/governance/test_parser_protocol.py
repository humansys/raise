"""Tests for GovernanceParser Protocol conformance.

Verifies that all 9 parser classes structurally satisfy the GovernanceParser Protocol.
"""

from __future__ import annotations

import pytest

from raise_cli.governance.parsers import GovernanceParser

# All 9 parser classes that should conform to the Protocol
PARSER_CLASSES = [
    "raise_cli.governance.parsers.adr.AdrParser",
    "raise_cli.governance.parsers.backlog.BacklogParser",
    "raise_cli.governance.parsers.constitution.ConstitutionParser",
    "raise_cli.governance.parsers.epic.EpicScopeParser",
    "raise_cli.governance.parsers.glossary.GlossaryParser",
    "raise_cli.governance.parsers.guardrails.GuardrailsParser",
    "raise_cli.governance.parsers.prd.PrdParser",
    "raise_cli.governance.parsers.roadmap.RoadmapParser",
    "raise_cli.governance.parsers.vision.VisionParser",
]


def _import_class(dotted_path: str) -> type:
    """Import a class by its dotted path."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)  # type: ignore[no-any-return]


@pytest.mark.parametrize("class_path", PARSER_CLASSES)
def test_parser_satisfies_governance_parser_protocol(class_path: str) -> None:
    """Each parser class must be a structural subtype of GovernanceParser."""
    cls = _import_class(class_path)
    instance = cls()
    assert isinstance(instance, GovernanceParser), (
        f"{cls.__name__} does not satisfy GovernanceParser Protocol"
    )
