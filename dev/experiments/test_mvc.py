#!/usr/bin/env python3
"""
Graph-based MVC Validation Experiment

Purpose: Test if graph-based Minimum Viable Context provides tangible benefits
         over manual file selection for common tasks.

Hypothesis: Graph traversal can reduce token usage by 20%+ while maintaining
            or improving context accuracy (no missing dependencies).

Test cases:
1. Validate PRD - Check if PRD meets quality standards
2. Design Review - Validate design against requirements
3. Plan Sprint - Select features from backlog

Success criteria:
- >20% token savings: Graph is valuable, build it
- 10-20% savings: Marginal benefit, consider deferring
- <10% savings: Not worth the complexity, skip it

Duration: 2 hours
"""

import yaml
from pathlib import Path
from collections import deque


def load_graph(graph_file: Path) -> dict:
    """Load graph from YAML"""
    with open(graph_file) as f:
        return yaml.safe_load(f)


def traverse(graph: dict, start: str, edge_types: list[str], depth: int = 1) -> list[str]:
    """
    BFS traversal following specified edge types.

    Args:
        graph: Graph structure from YAML
        start: Starting node ID
        edge_types: List of edge types to follow (e.g., ['depends_on', 'governed_by'])
        depth: Maximum traversal depth (default: 1)

    Returns:
        List of node IDs reachable from start
    """
    visited = set()
    queue = deque([(start, 0)])  # (node_id, current_depth)
    result = []

    while queue:
        node, d = queue.popleft()

        if node in visited or d > depth:
            continue

        visited.add(node)
        result.append(node)

        # Find outgoing edges from this node
        for edge in graph.get("edges", []):
            if edge["from"] == node and edge["type"] in edge_types:
                queue.append((edge["to"], d + 1))

    return result


def get_files(graph: dict, node_ids: list[str]) -> list[str]:
    """Convert node IDs to file paths"""
    nodes = graph.get("nodes", {})
    return [nodes[nid]["file"] for nid in node_ids if nid in nodes]


def count_tokens(file_path: Path) -> int:
    """
    Rough token count estimation.

    Uses simple heuristic: words * 1.3 (accounts for punctuation, formatting)
    Good enough for comparison purposes.
    """
    if not file_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return 0

    text = file_path.read_text()
    words = len(text.split())
    return int(words * 1.3)


def test_task(
    task_name: str,
    start: str,
    edge_types: list[str],
    manual_files: list[str]
) -> float:
    """
    Test a specific task comparing manual vs graph-based approaches.

    Args:
        task_name: Human-readable task name
        start: Starting node for graph traversal
        edge_types: Edge types to follow
        manual_files: Files we'd read without graph (baseline)

    Returns:
        Token savings percentage
    """
    print(f"\n{'='*70}")
    print(f"Task: {task_name}")
    print(f"{'='*70}")

    # Load graph
    graph_file = Path(__file__).parent / "graph-spike.yaml"
    graph = load_graph(graph_file)

    # MVC approach - graph traversal
    mvc_nodes = traverse(graph, start, edge_types, depth=1)
    mvc_files = get_files(graph, mvc_nodes)

    # Count tokens
    base_path = Path(__file__).parent.parent.parent
    mvc_tokens = sum(count_tokens(base_path / f) for f in mvc_files)
    manual_tokens = sum(count_tokens(base_path / f) for f in manual_files)

    # Results
    print(f"\n📋 Manual Approach (current):")
    print(f"  Files: {len(manual_files)}")
    for f in manual_files:
        tokens = count_tokens(base_path / f)
        print(f"    - {f} (~{tokens} tokens)")
    print(f"  Total tokens: ~{manual_tokens}")

    print(f"\n🔍 MVC Approach (graph-based):")
    print(f"  Query: start={start}, edges={edge_types}, depth=1")
    print(f"  Files: {len(mvc_files)}")
    for f in mvc_files:
        tokens = count_tokens(base_path / f)
        node_id = [nid for nid, n in graph["nodes"].items() if n["file"] == f][0]
        print(f"    - {f} (~{tokens} tokens) [{node_id}]")
    print(f"  Total tokens: ~{mvc_tokens}")

    # Analysis
    savings = manual_tokens - mvc_tokens
    savings_pct = (savings / manual_tokens * 100) if manual_tokens > 0 else 0

    excluded = set(manual_files) - set(mvc_files)
    missing = set(mvc_files) - set(manual_files)

    print(f"\n📊 Results:")
    print(f"  Token savings: {savings} ({savings_pct:.1f}%)")

    if excluded:
        print(f"  ✓ Excluded (not needed for this task):")
        for f in excluded:
            print(f"      - {f}")

    if missing:
        print(f"  ⚠ Found via graph (would have missed manually):")
        for f in missing:
            print(f"      - {f}")

    # Decision guidance
    if savings_pct > 20:
        print(f"\n  ✅ SIGNIFICANT savings - graph provides clear value")
    elif savings_pct > 10:
        print(f"\n  🤔 MODERATE savings - marginal benefit, consider cost/complexity")
    else:
        print(f"\n  ❌ MINIMAL savings - graph overhead likely not worth it")

    return savings_pct


def main():
    """Run all test cases and summarize results"""

    print("="*70)
    print("Graph-based MVC Validation Experiment")
    print("="*70)
    print()
    print("Testing hypothesis: Graph traversal reduces token usage by 20%+")
    print("while maintaining context accuracy.")
    print()

    results = []

    # Test Case 1: Validate PRD
    savings_1 = test_task(
        task_name="Validate PRD",
        start="prd",
        edge_types=["depends_on", "governed_by"],
        manual_files=[
            "governance/projects/raise-cli/prd.md",
            "governance/solution/vision.md",
            "framework/reference/constitution.md",
            "governance/projects/raise-cli/design.md",  # Might not need
            "governance/solution/guardrails.md",  # Might not need
        ]
    )
    results.append(("Validate PRD", savings_1))

    # Test Case 2: Design Review
    savings_2 = test_task(
        task_name="Design Review",
        start="design",
        edge_types=["implements", "governed_by"],
        manual_files=[
            "governance/projects/raise-cli/design.md",
            "governance/projects/raise-cli/prd.md",
            "governance/solution/guardrails.md",
            "framework/reference/constitution.md",  # Might not need
        ]
    )
    results.append(("Design Review", savings_2))

    # Test Case 3: Plan Sprint
    savings_3 = test_task(
        task_name="Plan Sprint from Backlog",
        start="backlog",
        edge_types=["implements", "references"],
        manual_files=[
            "governance/projects/raise-cli/backlog.md",
            "governance/projects/raise-cli/prd.md",
            "governance/projects/raise-cli/design.md",
            "governance/solution/vision.md",  # Might not need
        ]
    )
    results.append(("Plan Sprint", savings_3))

    # Summary
    print(f"\n{'='*70}")
    print("EXPERIMENT SUMMARY")
    print(f"{'='*70}")
    print()

    avg_savings = sum(s for _, s in results) / len(results)

    print("Results by test case:")
    for task, savings in results:
        status = "✅" if savings > 20 else "🤔" if savings > 10 else "❌"
        print(f"  {status} {task}: {savings:.1f}% savings")

    print(f"\nAverage savings: {avg_savings:.1f}%")
    print()

    # Final recommendation
    if avg_savings > 20:
        print("🎯 RECOMMENDATION: Build graph-based MVC")
        print("   - Clear value demonstrated")
        print("   - Proceed with full E2 implementation")
        print("   - Expected ROI: High")
    elif avg_savings > 10:
        print("🤔 RECOMMENDATION: Marginal benefit")
        print("   - Consider deferring to E2.5")
        print("   - Focus on simpler features first")
        print("   - Expected ROI: Medium")
    else:
        print("🛑 RECOMMENDATION: Skip graph in E2")
        print("   - Complexity not justified by savings")
        print("   - Use simpler approaches (skills read files directly)")
        print("   - Expected ROI: Low")

    print()


if __name__ == "__main__":
    main()
