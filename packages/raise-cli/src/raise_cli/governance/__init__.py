"""Governance artifact models and sync.

Governance extraction now uses the cartridge pipeline (ADR-089).
This module retains the data models for backward compatibility.
"""

from raise_cli.governance.models import Concept, ConceptType, ExtractionResult

__all__ = ["Concept", "ConceptType", "ExtractionResult"]
