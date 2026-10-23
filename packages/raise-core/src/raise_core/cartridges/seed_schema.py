"""Seed schema generator — convert CorpusAnalysis to cartridge config artifacts.

Takes the output of corpus_analyzer and produces the YAML-serializable
dicts for extractors/config.yaml, extractors/schemas/relationships.yaml,
and CARTRIDGE.yaml updates.
"""

from __future__ import annotations

from raise_core.cartridges.corpus_analyzer import CorpusAnalysis


def generate_extractor_config(
    analysis: CorpusAnalysis,
    *,
    corpus_glob: str = "corpus/*.md",
) -> dict[str, list[dict[str, str | list[str]]]]:
    """Generate extractors/config.yaml content from corpus analysis.

    One LLM extractor spec per proposed node type.
    """
    if not analysis.proposed_node_types:
        return {"extractors": []}

    type_names = [nt.name for nt in analysis.proposed_node_types]
    domain_ctx = f"Knowledge domain covering {', '.join(type_names)} entities"

    specs: list[dict[str, str | list[str]]] = []
    for nt in analysis.proposed_node_types:
        specs.append(
            {
                "name": nt.name,
                "type": "llm",
                "sources": [corpus_glob],
                "node_type": nt.name,
                "schema_ref": "extractors/schemas/relationships.yaml",
                "relationship_mode": "guided",
                "domain_context": domain_ctx,
            }
        )

    return {"extractors": specs}


def generate_relationship_schema(
    analysis: CorpusAnalysis,
) -> dict[str, list[dict[str, str]]]:
    """Generate extractors/schemas/relationships.yaml from corpus analysis."""
    if not analysis.proposed_relationship_types:
        return {"relationship_types": []}

    types: list[dict[str, str]] = []
    for rt in analysis.proposed_relationship_types:
        types.append(
            {
                "type": rt.name,
                "description": rt.description,
            }
        )

    return {"relationship_types": types}


def generate_manifest_updates(analysis: CorpusAnalysis) -> dict[str, str]:
    """Generate CARTRIDGE.yaml field updates from corpus analysis.

    Returns a dict with domain_context and competency_questions strings.
    """
    if not analysis.proposed_node_types:
        return {"domain_context": "", "competency_questions": ""}

    type_names = [nt.name for nt in analysis.proposed_node_types]
    domain_context = f"Knowledge domain covering {', '.join(type_names)} entities"

    cq_lines: list[str] = []
    for q in analysis.proposed_competency_questions:
        cq_lines.append(f"- {q}")
    competency_questions = "\n".join(cq_lines) if cq_lines else ""

    return {
        "domain_context": domain_context,
        "competency_questions": competency_questions,
    }
