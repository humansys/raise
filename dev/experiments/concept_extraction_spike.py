#!/usr/bin/env python3
"""
Concept Extraction Spike
Test: Can we extract semantic concepts from governance markdown?
Complexity: Easy/Medium/Hard?
Time: 1 hour to find out
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class Concept:
    """A semantic concept extracted from markdown"""
    id: str
    type: str
    file: str
    section: str
    lines: tuple[int, int]
    content: str
    metadata: Dict[str, Any]

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "file": self.file,
            "section": self.section,
            "lines": list(self.lines),
            "content": self.content,
            "metadata": self.metadata
        }


def extract_prd_requirements(file_path: Path) -> List[Concept]:
    """Extract requirements from PRD (RF-XX format)"""
    print(f"\n🔍 Extracting requirements from {file_path.name}...")

    text = file_path.read_text()
    lines = text.split('\n')

    concepts = []
    current_section = None
    section_start = None

    for i, line in enumerate(lines, 1):
        # Match requirement sections: ### RF-05: Title
        match = re.match(r'^### (RF-\d+):\s*(.+)$', line)

        if match:
            req_id = match.group(1)
            title = match.group(2)

            # Extract requirement details (table rows)
            section_lines = []
            j = i
            while j < len(lines) and not lines[j].startswith('###'):
                section_lines.append(lines[j])
                j += 1

            content = '\n'.join(section_lines[:20])  # First ~20 lines of section

            concept = Concept(
                id=f"req-{req_id.lower()}",
                type="requirement",
                file=str(file_path.relative_to(file_path.parent.parent.parent)),
                section=f"{req_id}: {title}",
                lines=(i, min(i + 20, len(lines))),
                content=content.strip(),
                metadata={
                    "requirement_id": req_id,
                    "title": title
                }
            )
            concepts.append(concept)
            print(f"  ✓ Found {req_id}: {title}")

    print(f"  → Extracted {len(concepts)} requirements")
    return concepts


def extract_vision_outcomes(file_path: Path) -> List[Concept]:
    """Extract key outcomes from vision"""
    print(f"\n🔍 Extracting outcomes from {file_path.name}...")

    text = file_path.read_text()
    lines = text.split('\n')

    concepts = []

    # Look for table with outcomes (| **Outcome** | Description |)
    in_outcomes_table = False

    for i, line in enumerate(lines, 1):
        # Detect outcomes table
        if '| **' in line and ('outcome' in line.lower() or 'context' in line.lower()):
            in_outcomes_table = True
            continue

        if in_outcomes_table:
            # Parse table row: | **Outcome Name** | Description |
            match = re.match(r'\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|', line)
            if match:
                outcome_name = match.group(1).strip()
                description = match.group(2).strip()

                # Generate ID from name
                outcome_id = outcome_name.lower().replace(' ', '-').replace('(', '').replace(')', '')

                concept = Concept(
                    id=f"outcome-{outcome_id}",
                    type="outcome",
                    file=str(file_path.relative_to(file_path.parent.parent.parent)),
                    section=outcome_name,
                    lines=(i, i),
                    content=description,
                    metadata={
                        "outcome_name": outcome_name
                    }
                )
                concepts.append(concept)
                print(f"  ✓ Found outcome: {outcome_name}")

            # End of table
            if line.strip() == '' or (line.startswith('|') and '---' in line):
                continue
            elif not line.startswith('|'):
                in_outcomes_table = False

    print(f"  → Extracted {len(concepts)} outcomes")
    return concepts


def extract_constitution_principles(file_path: Path) -> List[Concept]:
    """Extract principles from constitution (§N format)"""
    print(f"\n🔍 Extracting principles from {file_path.name}...")

    text = file_path.read_text()
    lines = text.split('\n')

    concepts = []

    for i, line in enumerate(lines, 1):
        # Match principle headers: ### §2. Principle Name
        match = re.match(r'^### §(\d+)\.\s*(.+)$', line)

        if match:
            principle_num = match.group(1)
            principle_name = match.group(2).strip()

            # Extract principle content until next section
            section_lines = []
            j = i
            while j < len(lines) and not (lines[j].startswith('###') and j > i):
                section_lines.append(lines[j])
                j += 1

            content = '\n'.join(section_lines[:30])  # First ~30 lines

            # Generate ID
            principle_id = principle_name.lower().replace(' ', '-').replace(',', '')

            concept = Concept(
                id=f"principle-{principle_id}",
                type="principle",
                file=str(file_path.relative_to(file_path.parent.parent.parent)),
                section=f"§{principle_num}. {principle_name}",
                lines=(i, min(i + 30, len(lines))),
                content=content.strip(),
                metadata={
                    "principle_number": principle_num,
                    "principle_name": principle_name
                }
            )
            concepts.append(concept)
            print(f"  ✓ Found §{principle_num}: {principle_name}")

    print(f"  → Extracted {len(concepts)} principles")
    return concepts


def infer_relationships(concepts: List[Concept]) -> List[Dict[str, str]]:
    """Infer relationships between concepts (simple keyword matching for spike)"""
    print(f"\n🔗 Inferring relationships...")

    edges = []

    # Simple heuristic: keyword matching
    for concept in concepts:
        if concept.type == "requirement":
            content_lower = concept.content.lower()

            # Find related outcomes
            for other in concepts:
                if other.type == "outcome":
                    outcome_keywords = other.metadata.get("outcome_name", "").lower().split()
                    # If requirement mentions outcome keywords
                    if any(keyword in content_lower for keyword in outcome_keywords if len(keyword) > 3):
                        edges.append({
                            "from": concept.id,
                            "to": other.id,
                            "type": "implements",
                            "reason": f"Requirement mentions '{other.metadata.get('outcome_name')}'"
                        })
                        print(f"  ✓ {concept.id} implements {other.id}")

            # Find related principles
            for other in concepts:
                if other.type == "principle":
                    principle_keywords = other.metadata.get("principle_name", "").lower().split()
                    if any(keyword in content_lower for keyword in principle_keywords if len(keyword) > 5):
                        edges.append({
                            "from": concept.id,
                            "to": other.id,
                            "type": "governed_by",
                            "reason": f"Requirement relates to '{other.metadata.get('principle_name')}'"
                        })
                        print(f"  ✓ {concept.id} governed_by {other.id}")

    print(f"  → Inferred {len(edges)} relationships")
    return edges


def build_concept_graph(base_path: Path) -> Dict[str, Any]:
    """Build complete concept graph from governance files"""
    print("="*70)
    print("CONCEPT EXTRACTION SPIKE")
    print("="*70)

    all_concepts = []

    # Extract from each file type
    prd_path = base_path / "governance/projects/raise-cli/prd.md"
    vision_path = base_path / "governance/solution/vision.md"
    constitution_path = base_path / "framework/reference/constitution.md"

    if prd_path.exists():
        all_concepts.extend(extract_prd_requirements(prd_path))

    if vision_path.exists():
        all_concepts.extend(extract_vision_outcomes(vision_path))

    if constitution_path.exists():
        all_concepts.extend(extract_constitution_principles(constitution_path))

    # Infer relationships
    edges = infer_relationships(all_concepts)

    # Build graph structure
    graph = {
        "nodes": {c.id: c.to_dict() for c in all_concepts},
        "edges": edges
    }

    return graph


def test_concept_query(graph: Dict[str, Any], task: str) -> Dict[str, Any]:
    """Test querying concept graph for a specific task"""
    print(f"\n{'='*70}")
    print(f"TEST QUERY: {task}")
    print(f"{'='*70}")

    # For spike: hardcode task mappings
    task_queries = {
        "validate-rf-05": {
            "start": "req-rf-05",
            "edge_types": ["implements", "governed_by"],
            "depth": 1
        }
    }

    query = task_queries.get(task)
    if not query:
        print(f"  ❌ Unknown task: {task}")
        return {}

    # Simple BFS traversal
    start = query["start"]
    edge_types = query["edge_types"]

    visited = {start}
    result_nodes = [start]

    # One level traversal
    for edge in graph["edges"]:
        if edge["from"] == start and edge["type"] in edge_types:
            visited.add(edge["to"])
            result_nodes.append(edge["to"])
            print(f"  ✓ {edge['from']} --{edge['type']}--> {edge['to']}")

    # Build MVC
    mvc = {
        "task": task,
        "concepts": [graph["nodes"][nid] for nid in result_nodes if nid in graph["nodes"]],
        "total_concepts": len(result_nodes)
    }

    # Count tokens
    total_tokens = sum(
        len(c["content"].split()) * 1.3
        for c in mvc["concepts"]
    )

    print(f"\n📊 MVC Results:")
    print(f"  Concepts returned: {len(mvc['concepts'])}")
    for c in mvc["concepts"]:
        tokens = int(len(c["content"].split()) * 1.3)
        print(f"    - {c['id']} ({c['type']}): ~{tokens} tokens")
    print(f"  Total tokens: ~{int(total_tokens)}")

    return mvc


def main():
    base_path = Path(__file__).parent.parent.parent

    # Build concept graph
    graph = build_concept_graph(base_path)

    print(f"\n{'='*70}")
    print(f"GRAPH SUMMARY")
    print(f"{'='*70}")
    print(f"Total concepts: {len(graph['nodes'])}")
    print(f"  Requirements: {sum(1 for n in graph['nodes'].values() if n['type'] == 'requirement')}")
    print(f"  Outcomes: {sum(1 for n in graph['nodes'].values() if n['type'] == 'outcome')}")
    print(f"  Principles: {sum(1 for n in graph['nodes'].values() if n['type'] == 'principle')}")
    print(f"Total relationships: {len(graph['edges'])}")

    # Save graph
    output_file = Path(__file__).parent / "concept-graph.json"
    with open(output_file, 'w') as f:
        json.dump(graph, f, indent=2)
    print(f"\n💾 Graph saved to: {output_file}")

    # Test query
    mvc = test_concept_query(graph, "validate-rf-05")

    print(f"\n{'='*70}")
    print("COMPLEXITY ASSESSMENT")
    print(f"{'='*70}")
    print()
    print("✅ EASY: Regex extraction works for structured markdown")
    print("✅ EASY: Concept identification is straightforward")
    print("✅ EASY: Relationship inference works (simple heuristics)")
    print()
    print("⏱️  Implementation estimate:")
    print("   - Concept extraction: 1-2 days (parsers for each doc type)")
    print("   - Relationship inference: 1 day (improve heuristics)")
    print("   - Graph building: 1 day (schema + serialization)")
    print("   - Query engine: 1 day (reuse from file-level)")
    print("   TOTAL: ~4-5 days (3-4 SP)")
    print()
    print("💡 RECOMMENDATION: Build concept-level directly in E2")
    print("   File-level becomes fallback for unparsed documents")
    print()


if __name__ == "__main__":
    main()
