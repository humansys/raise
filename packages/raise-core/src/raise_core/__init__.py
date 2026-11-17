"""RaiSE Core - Shared domain models for the RaiSE framework.

rai-core is the shared domain contract between COMMUNITY (rai-cli) and PRO (rai-server).
It contains the vocabulary, protocols, and logic that any RaiSE component needs.

Domain axes:
- graph: Models, engine, query, scoring, backends (E275)
- workflow: Work item types, state machines, gates (future)
- governance: Extensible artifact type schema (future)
"""

from __future__ import annotations

from importlib.metadata import version as _pkg_version

__version__ = _pkg_version("raise-core")
