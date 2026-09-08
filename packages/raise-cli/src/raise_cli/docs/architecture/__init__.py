"""Layer 2 — deterministic scaffolding for architecture doc synthesis.

No module in this package calls an LLM API (AC12). Synthesis itself
happens at the skill-turn level (``rai-docs-update``); this package
provides everything that surrounds it: bundle assembly, fingerprinting,
region parsing/writing, and Mermaid dialect validation.

Architecture: ADR-146 (Machine-Owned Narrative Regions), S15884.2 design.
"""

from __future__ import annotations
