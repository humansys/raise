"""Corpus analyzer — propose a seed schema from document corpus.

Samples chunks uniformly from each document, sends them to an LLM,
and returns proposed node types, relationship types, and competency
questions as a structured CorpusAnalysis.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from raise_core.cartridges.chunker import Chunk, GenericChunker

logger = logging.getLogger(__name__)

_MAX_SAMPLES_PER_DOC = 5
_MIN_SAMPLES_PER_DOC = 3


class ProposedNodeType(BaseModel):
    """A node type proposed by the corpus analyzer."""

    name: str
    description: str
    examples: list[str] = Field(default_factory=list)


class ProposedRelationshipType(BaseModel):
    """A relationship type proposed by the corpus analyzer."""

    name: str
    description: str
    source_type: str
    target_type: str


class CorpusStats(BaseModel):
    """Basic statistics about the analyzed corpus."""

    file_count: int = 0
    total_chars: int = 0


class CorpusAnalysis(BaseModel):
    """Result of corpus analysis — seed schema proposal."""

    proposed_node_types: list[ProposedNodeType] = Field(default_factory=list)
    proposed_relationship_types: list[ProposedRelationshipType] = Field(
        default_factory=list
    )
    proposed_competency_questions: list[str] = Field(default_factory=list)
    corpus_stats: CorpusStats = Field(default_factory=CorpusStats)


def _sample_chunks(paths: list[Path], chunker: GenericChunker) -> list[Chunk]:
    """Sample 3-5 chunks uniformly from each document."""
    samples: list[Chunk] = []
    for path in paths:
        chunks = chunker.split(path)
        if not chunks:
            continue
        n = min(max(_MIN_SAMPLES_PER_DOC, len(chunks)), _MAX_SAMPLES_PER_DOC)
        if len(chunks) <= n:
            samples.extend(chunks)
        else:
            step = len(chunks) / n
            indices = [int(i * step) for i in range(n)]
            samples.extend(chunks[i] for i in indices)
    return samples


def _compute_stats(paths: list[Path]) -> CorpusStats:
    """Compute basic corpus statistics."""
    total_chars = 0
    for path in paths:
        try:
            total_chars += len(path.read_text(encoding="utf-8"))
        except Exception:
            logger.warning("Could not read %s for stats", path)
    return CorpusStats(file_count=len(paths), total_chars=total_chars)


_ANALYSIS_PROMPT = """\
You are a knowledge ontology analyst. Analyze the following document samples \
and propose a schema for structuring the knowledge they contain.

## Task
Based on the samples below, propose:
1. **Node types** — the kinds of entities/concepts in this domain (3-8 types)
2. **Relationship types** — how these entities relate to each other (2-5 types)
3. **Competency questions** — questions this knowledge base should answer (3-5 questions)

## Output format
Return a JSON object:
```json
{{
  "proposed_node_types": [
    {{"name": "kebab-case", "description": "What this type represents", "examples": ["example1"]}}
  ],
  "proposed_relationship_types": [
    {{"name": "kebab-case", "description": "What this relationship means", \
"source_type": "type-a", "target_type": "type-b"}}
  ],
  "proposed_competency_questions": [
    "What are the key X in this domain?"
  ]
}}
```

## Guidelines
- Use kebab-case for names
- Be specific to the domain — avoid generic types like "concept" or "item"
- Each node type should represent a distinct kind of entity
- Relationship types should connect the proposed node types
- Competency questions should be answerable by querying the knowledge graph

## Document Samples

{samples}"""


def _format_samples(chunks: list[Chunk]) -> str:
    """Format sampled chunks for the LLM prompt."""
    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        heading = f" ({chunk.heading})" if chunk.heading else ""
        text = chunk.text[:500] if len(chunk.text) > 500 else chunk.text
        parts.append(f"--- Sample {i}{heading} ---\n{text}")
    return "\n\n".join(parts)


def analyze_corpus(paths: list[Path], llm_client: Any) -> CorpusAnalysis:
    """Analyze a corpus and propose a seed schema.

    Args:
        paths: List of markdown file paths to analyze.
        llm_client: OpenAI-compatible client for LLM calls.

    Returns:
        CorpusAnalysis with proposed schema and corpus stats.
    """
    if not paths:
        return CorpusAnalysis()

    stats = _compute_stats(paths)
    chunker = GenericChunker(heading_level=2)
    samples = _sample_chunks(paths, chunker)

    if not samples:
        return CorpusAnalysis(corpus_stats=stats)

    prompt = _ANALYSIS_PROMPT.format(samples=_format_samples(samples))

    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash-lite",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or ""
    except Exception:
        logger.warning("LLM call failed during corpus analysis")
        return CorpusAnalysis(corpus_stats=stats)

    if not raw_text.strip():
        return CorpusAnalysis(corpus_stats=stats)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON from LLM in corpus analysis")
        return CorpusAnalysis(corpus_stats=stats)

    try:
        analysis = CorpusAnalysis.model_validate(data)
    except ValidationError:
        logger.warning("LLM response did not match CorpusAnalysis schema")
        return CorpusAnalysis(corpus_stats=stats)

    analysis.corpus_stats = stats
    return analysis
