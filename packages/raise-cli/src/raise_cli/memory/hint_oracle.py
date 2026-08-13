"""Neuro-symbolic hint oracle for per-prompt context injection.

Provides two public functions:
    triviality_gate(prompt) -> bool
        Pure-text gate, <1µs, no I/O.  Returns True when prompt is a
        no-op (acknowledgment, slash command, symbol-only, <25 chars).

    get_hints(prompt, top_k, project_root) -> str
        Queries RetrievalGraphBackend and returns data-only markdown hints
        (<= 10K chars) for injection via CC UserPromptSubmit additionalContext.
        Returns "" on any failure (fail-open, DD-5).

Design decisions:
    DD-1: Compose RetrievalGraphBackend — do NOT re-wire graph-load / scorer /
          adapter manually.  Backend __init__ already does that.
    DD-2: triviality_gate defaults to retrieve; only filters obvious no-ops.
    DD-3: Hints are data-only — no imperatives to avoid CC #17804 detector.
    DD-5: All exceptions return "" — a broken oracle must never block a prompt.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Triviality Gate
# ---------------------------------------------------------------------------

ACK_SET: frozenset[str] = frozenset(
    {
        "ok",
        "sí",
        "si",
        "no",
        "yes",
        "gracias",
        "thanks",
        "listo",
        "adelante",
        "continúa",
        "continue",
        "proceed",
        "done",
        "perfect",
        "sounds good",
        "entendido",
        "understood",
        "👍",
        "✓",
    }
)

_IMPERATIVE_PREFIXES: frozenset[str] = frozenset(
    {"must", "should", "always", "never", "do ", "don't", "ensure", "make sure"}
)


def triviality_gate(prompt: str) -> bool:
    """Return True when prompt is trivial — skip retrieval.

    Runs in <1µs: pure string operations, no I/O, no ML.
    Default = retrieve (False).  Only explicit no-ops return True.
    """
    s = prompt.strip()
    if len(s) < 10:  # truly trivial input not covered by ACK_SET
        return True
    if s.lower() in ACK_SET:  # explicit acknowledgment
        return True
    # CC slash command or pure symbols/code snippet
    return s.startswith("/") or not any(c.isalpha() for c in s)


# ---------------------------------------------------------------------------
# Hint Retrieval
# ---------------------------------------------------------------------------

# Module-level singleton — warm path ≤20ms for CLI usage.
# Each hook invocation is a fresh subprocess so "warm" is irrelevant there,
# but the CLI subcommand and tests benefit from lazy singleton caching.
_backend: Any = None


def _get_backend() -> Any:
    """Return the module-level RetrievalGraphBackend singleton (lazy init)."""
    global _backend  # noqa: PLW0603
    if _backend is None:
        from raise_cli.graph.query_backend import RetrievalGraphBackend

        _backend = RetrievalGraphBackend()
    return _backend


def _retrieve_sync(prompt: str, top_k: int) -> list[dict[str, Any]]:
    """Synchronous wrapper around the async backend.query()."""
    backend = _get_backend()

    async def _run() -> dict[str, Any]:
        return await backend.query(prompt, top_k)

    result = asyncio.run(_run())
    return result.get("results", [])


def get_hints(
    prompt: str,
    top_k: int = 5,
    project_root: Path | None = None,  # reserved for future local-index override
) -> str:
    """Return data-only markdown hints from the neuro-symbolic graph.

    Returns "" on any failure (fail-open, DD-5).
    Max 10_000 chars; truncates by dropping lowest-ranked items (DD-3, AC-8).
    """
    _ = project_root  # reserved; retrieval is currently CWD-bound
    try:
        nodes = _retrieve_sync(prompt, top_k)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("hint_oracle: retrieval failed", exc_info=True)
        return ""

    if not nodes:
        return ""

    return _format_hints(nodes)


def _format_hints(nodes: list[dict[str, Any]]) -> str:
    """Format retrieved nodes as data-only markdown.

    Separates patterns from decisions/ADRs.  Filters leading imperatives
    to avoid CC #17804 false-positive injection detector.  Truncates at 10K.
    """
    _pat_types = frozenset({"pattern", "PAT"})
    _dec_types = frozenset({"adr", "decision", "ADR"})
    _mem_types = frozenset({"memory"})

    patterns = [n for n in nodes if n.get("node_type", "") in _pat_types]
    decisions = [n for n in nodes if n.get("node_type", "") in _dec_types]
    memory = [n for n in nodes if n.get("node_type", "") in _mem_types]
    other = [
        n for n in nodes if n not in patterns and n not in decisions and n not in memory
    ]

    lines: list[str] = ["## Hints del grafo RaiSE"]
    _append_section(lines, "**Patterns relevantes:**", patterns[:5])
    _append_section(lines, "**Decisiones:**", decisions[:3])
    _append_section(lines, "**Memoria:**", memory[:3])
    _append_section(lines, "**Contexto:**", other[:3])

    output = "\n".join(lines)

    # Enforce 10K char limit — drop lowest-ranked (already ordered by rank desc)
    if len(output) > 10_000:
        output = output[:9_990] + "\n...[truncated]"

    return output


def _append_section(lines: list[str], header: str, nodes: list[dict[str, Any]]) -> None:
    """Append a markdown section with bullet nodes (mutates lines in place)."""
    if not nodes:
        return
    lines.append(header)
    for node in nodes:
        bullet = _node_bullet(node)
        if bullet:
            lines.append(bullet)


def _node_bullet(node: dict[str, Any]) -> str:
    """Format a single node as a data-only bullet.

    Drops nodes whose content leads with an imperative verb (DD-3 / CC #17804).
    Dropping is safer than rewriting — rewriting can invert meaning (MAJOR-1 QR).
    """
    node_id = node.get("node_id", node.get("id", ""))
    content = node.get("content", node.get("summary", ""))[:200]

    if not content:
        return ""

    # Drop (not rewrite) nodes that lead with imperative verbs — prevents
    # meaning inversion and avoids CC #17804 prompt-injection false positives.
    content_lower = content.lower().lstrip()
    for prefix in _IMPERATIVE_PREFIXES:
        if content_lower.startswith(prefix):
            return ""

    # RAISE-9757: federated (multi-cartridge) results carry provenance so a
    # reader can judge whether a mixed-layer result set makes sense for the
    # query. Absent for non-federated/single-cartridge callers — format is
    # unchanged there (backward compatible).
    source_cartridge = node.get("source_cartridge")
    if source_cartridge:
        return f"- [{source_cartridge}] [{node_id}] {content}"

    return f"- [{node_id}] {content}"
