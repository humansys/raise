"""Output formatters for MVC query results.

This module provides formatters for converting ContextResult into various
output formats (markdown, JSON) for consumption by AI agents or tools.
"""

from __future__ import annotations

from raise_cli.governance.query.models import ContextResult


def format_markdown(result: ContextResult) -> str:
    """Format ContextResult as markdown for AI consumption.

    Creates a structured markdown document with:
    - Query metadata header
    - Concepts organized by type with relationship annotations
    - Relationship paths
    - Token savings estimate

    Args:
        result: MVC query result to format.

    Returns:
        Formatted markdown string.

    Examples:
        >>> markdown = format_markdown(result)
        >>> "# Minimum Viable Context" in markdown
        True
    """
    lines: list[str] = []

    # Header
    lines.append("# Minimum Viable Context (MVC)")
    lines.append("")
    lines.append(f"**Query:** `{result.metadata.query}`")
    lines.append(f"**Strategy:** {result.metadata.strategy.value}")
    lines.append(
        f"**Concepts:** {result.metadata.total_concepts} | "
        f"**Tokens:** ~{result.metadata.token_estimate} | "
        f"**Depth:** {result.metadata.traversal_depth}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # No results
    if not result.concepts:
        lines.append("*No concepts found matching the query.*")
        lines.append("")
        return "\n".join(lines)

    # Group concepts by type for better organization
    by_type: dict[str, list] = {}
    for concept in result.concepts:
        concept_type = concept.type.value
        by_type.setdefault(concept_type, []).append(concept)

    # Render each concept
    for idx, concept in enumerate(result.concepts):
        # Concept header
        lines.append(f"## {concept.section}")
        lines.append(
            f"**Type:** {concept.type.value} | **File:** {concept.file} | "
            f"**Lines:** {concept.lines[0]}-{concept.lines[1]}"
        )
        lines.append("")

        # Content (truncate if very long)
        content = concept.content
        if len(content) > 500:
            content = content[:500] + "..."

        lines.append(content)
        lines.append("")

        # Metadata annotations (if available)
        if concept.metadata:
            if "requirement_id" in concept.metadata:
                lines.append(f"*Requirement ID: {concept.metadata['requirement_id']}*")
            if "principle_number" in concept.metadata:
                lines.append(f"*Principle: §{concept.metadata['principle_number']}*")

        lines.append("")

        # Separator between concepts
        if idx < len(result.concepts) - 1:
            lines.append("---")
            lines.append("")

    # Relationship paths (if available)
    if result.metadata.paths:
        lines.append("---")
        lines.append("")
        lines.append("## Relationship Paths")
        lines.append("")

        for path in result.metadata.paths:
            if len(path) >= 2:
                path_str = " → ".join(f"`{node}`" for node in path)
                lines.append(f"- {path_str}")

        lines.append("")

    # Footer with metadata
    lines.append("---")
    lines.append("")
    lines.append("**Query Metadata:**")
    lines.append(f"- Execution time: {result.metadata.execution_time_ms:.2f}ms")
    lines.append(f"- Token estimate: ~{result.metadata.token_estimate}")

    # Token savings estimate (if we can estimate baseline)
    # Rough estimate: manual file loading would be ~6,000-10,000 tokens
    if result.metadata.total_concepts > 0:
        baseline_estimate = 6000  # Typical manual approach
        savings_pct = (
            (baseline_estimate - result.metadata.token_estimate) / baseline_estimate
        ) * 100
        if savings_pct > 0:
            lines.append(
                f"- Estimated savings: ~{savings_pct:.0f}% vs manual file loading"
            )

    lines.append("")

    return "\n".join(lines)


def format_json(result: ContextResult) -> str:
    """Format ContextResult as JSON.

    Args:
        result: MVC query result to format.

    Returns:
        JSON string representation.

    Examples:
        >>> json_str = format_json(result)
        >>> "concepts" in json_str and "metadata" in json_str
        True
    """
    return result.to_json()


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses spike-validated heuristic: word count * 1.3

    Args:
        text: Text to estimate tokens for.

    Returns:
        Estimated token count.

    Examples:
        >>> estimate_tokens("The system must validate inputs")
        7
    """
    words = len(text.split())
    return int(words * 1.3)
