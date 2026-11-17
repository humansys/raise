"""Canonical MCP response serializer (S6003.7).

Rules R1-R10 that call sites are expected to follow:
  R1  Success minimum: {"status":"ok"} + only fields with new information
  R2  No echo-back: never repeat caller parameters
  R3  No narrative strings: structured fields instead of output/message
  R4  Relative paths to cwd/project root; resolve ../
  R5  Context constants out (scope, repo_id in local queries)
  R6  Heavy metadata opt-in: verbose: bool = False parameter
  R7  Floats to 3 significant figures
  R8  Homogeneous lists >=5 identical items → aggregation {count, sample}
  R9  No indent= in json.dumps; compact separators (",",":")
  R10 Errors keep their rich shape — NEVER apply compact_response to errors

This module is import-safe: no @mcp.tool() decorators, no FastMCP instance.
"""

from __future__ import annotations

import json
from typing import Any


def compact_response(payload: Any) -> str:
    """Serialize an MCP success payload compactly (R9).

    Accepts dict or list. Call sites are responsible for applying R1-R8.
    R10: never call this function on error payloads.
    """
    return json.dumps(payload, separators=(",", ":"))
