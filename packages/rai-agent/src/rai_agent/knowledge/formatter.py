"""Human-readable output formatting for gate and query results."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rai_agent.knowledge.models import DomainManifest, GateResult, PromptingConfig
    from rai_agent.knowledge.retrieval.models import RetrievalResult


def format_gate_result(result: GateResult) -> str:
    """Format a single gate result for human display."""
    symbol = "\u2713" if result.passed else "\u2717"
    status = "PASSED" if result.passed else "FAILED"
    line = f"  {result.gate:<12} {symbol}  {status}"

    # Add key metric summary
    summary = _metric_summary(result)
    if summary:
        line += f" \u2014 {summary}"

    line += f" ({result.duration_ms:.0f}ms)"

    # Errors
    lines = [line]
    for err in result.errors:
        lines.append(f"    ERROR: {err}")
    for warn in result.warnings:
        lines.append(f"    WARN:  {warn}")

    return "\n".join(lines)


def format_check_summary(
    results: list[GateResult],
    domain: str,
) -> str:
    """Format the summary of a check run."""
    all_passed = all(r.passed for r in results)
    lines = [f"[{domain}] Running {len(results)} gates...", ""]
    for result in results:
        lines.append(format_gate_result(result))
    lines.append("")
    if all_passed:
        lines.append("All gates passed.")
    else:
        failed = [r.gate for r in results if not r.passed]
        lines.append(f"FAILED gates: {', '.join(failed)}")
    return "\n".join(lines)


def format_status(
    domains: list[tuple[DomainManifest, int, int]],
) -> str:
    """Format domain status overview.

    Args:
        domains: list of (manifest, extracted_count, curated_count).
    """
    if not domains:
        return "No knowledge domains registered."

    lines = [f"Domains: {len(domains)} registered", ""]
    for manifest, extracted, curated in domains:
        lines.append(f"  {manifest.name:<16} {manifest.display_name}")
        types_str = (
            ", ".join(sorted(manifest.required_types))
            if manifest.required_types
            else "any"
        )
        lines.append(f"    Types:     {types_str}")
        lines.append(f"    Extracted: {extracted} nodes")
        lines.append(f"    Curated:   {curated} nodes")
    return "\n".join(lines)


def _metric_summary(result: GateResult) -> str:
    """Extract key metrics as a one-line summary."""
    m = result.metrics
    if result.gate == "validate":
        return f"{m.get('valid', 0)} valid, {m.get('invalid', 0)} invalid"
    if result.gate == "reconcile":
        return (
            f"{m.get('phantoms', 0)} phantoms, "
            f"{m.get('orphans', 0)} orphans"
        )
    if result.gate == "coverage":
        pct = m.get("coverage_pct", 0)
        total = m.get("total", 0)
        covered = m.get("covered", 0)
        return f"{covered}/{total} CQs covered \u2014 {pct:.1f}%"
    if result.gate == "graph":
        return (
            f"{m.get('nodes', 0)} nodes, "
            f"{m.get('edges', 0)} edges, "
            f"{m.get('components', 0)} components"
        )
    return ""


# ---------------------------------------------------------------------------
# Knowledge query formatters
# ---------------------------------------------------------------------------

_COMPACT_MAX = 150


def format_query_human(
    result: RetrievalResult,
    display_name: str,
    prompting: PromptingConfig | None,
) -> str:
    """Format query result as human-readable markdown."""
    lines: list[str] = []
    total = len(result.nodes)

    lines.append(f"═══ {display_name}: {result.query} ({total} results) ═══")
    lines.append("")

    # Prompting context
    if prompting and prompting.system_context:
        lines.append("## System Context")
        lines.append(prompting.system_context.strip())
        lines.append("")
        if prompting.response_format:
            lines.append("## Response Format")
            lines.append(prompting.response_format.strip())
            lines.append("")

    if not result.nodes:
        lines.append("*No relevant nodes found.*")
        return "\n".join(lines)

    lines.append("## Results")
    for i, scored in enumerate(result.nodes, 1):
        node = scored.node
        score = f"{scored.score:.2f}"
        lines.append(f"{i}. {node.id} ({score}) [{node.type}]")
        content = node.content
        if len(content) > 200:
            content = content[:200] + "..."
        lines.append(f"   {content}")
        lines.append("")

    return "\n".join(lines)


def format_query_compact(
    result: RetrievalResult,
    domain_name: str,
    prompting: PromptingConfig | None,
) -> str:
    """Format query result as compact one-liner for AI consumption."""
    total = len(result.nodes)
    lines: list[str] = []

    lines.append(f"# Knowledge: {result.query} ({total} results, {domain_name})")

    if not result.nodes:
        lines.append("*No results.*")
        return "\n".join(lines)

    if prompting and prompting.system_context:
        ctx = prompting.system_context.strip().replace("\n", " ")
        if len(ctx) > _COMPACT_MAX:
            ctx = ctx[:_COMPACT_MAX] + "..."
        lines.append(f"**ctx** {ctx}")

    for scored in result.nodes:
        node = scored.node
        content = node.content
        if len(content) > _COMPACT_MAX:
            content = content[:_COMPACT_MAX] + "..."
        lines.append(
            f"**{node.type}** {node.id} ({scored.score:.2f}): {content}"
        )

    return "\n".join(lines)


def format_query_json(
    result: RetrievalResult,
    prompting: PromptingConfig | None,
) -> str:
    """Format query result as JSON."""
    data: dict[str, object] = {
        "query": result.query,
        "domain": result.hints.domain if result.hints else None,
        "prompting": (
            {
                "system_context": prompting.system_context,
                "response_format": prompting.response_format,
            }
            if prompting
            else None
        ),
        "results": [
            {
                "id": s.node.id,
                "type": s.node.type,
                "score": s.score,
                "content": s.node.content,
                "explanation": s.explanation,
            }
            for s in result.nodes
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
