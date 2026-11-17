"""DDD heuristic prompt bundle for symbol classification."""

from __future__ import annotations

_HEURISTIC_BUNDLE = """\
You are a Domain-Driven Design expert. Classify each code symbol as:
- **D** (Domain): encodes business rules, domain concepts, or ubiquitous language
- **I** (Infrastructure): technical plumbing, frameworks, adapters, CLI wiring, persistence
- **?** (Ambiguous): genuinely unclear — use ONLY when heuristics split exactly 2D-2I

## Classification Procedure

For EACH symbol, follow this procedure strictly:
1. Evaluate H1 (Substitutability) — write your verdict (D or I)
2. Evaluate H2 (What-Changes-When) — write your verdict (D or I)
3. Evaluate H3 (Dependency Direction) — write your verdict (D or I)
4. Evaluate H4 (Ubiquitous Language) — write your verdict (D or I)
5. Count the votes. Derive the label from the majority.

Do NOT decide the label first and rationalize the heuristics afterward. \
The heuristics drive the label, not the other way around.

## Heuristic Tests

### H1: Substitutability
Could you replace this implementation with a different technology (different DB, \
different HTTP framework, different CLI library) WITHOUT changing business rules?
- Yes → **I** (infrastructure is substitutable)
- No → **D** (domain logic is not substitutable)

### H2: What-Changes-When
Does this code change when:
- Business rules change (new pricing model, new workflow step) → **D**
- Technology changes (library upgrade, framework migration, API version bump) → **I**

### H3: Dependency Direction
- This imports infrastructure (DB, HTTP, CLI frameworks) → **I**
- Infrastructure adapters depend on this (implement its interfaces) → **D**
- This has no infrastructure imports and is referenced by domain code → likely **D**
- Pure utility with no domain dependency → **I**

### H4: Ubiquitous Language
Would a domain expert (product owner, business analyst) recognize this name \
and understand its purpose without technical explanation?
- Yes → likely **D**
- No → likely **I**

## Tiebreaker Rules
- If H1-H4 split 2D-2I: classify as **?** (Ambiguous)
- If 3 agree and 1 disagrees: follow the majority
- If all 4 agree: high confidence classification

## Anti-Abstention Rule
Default to a definite classification (D or I). The **?** label should apply to \
fewer than 5% of symbols. Most symbols have a clear answer — genuine ambiguity \
is rare. If you classify as **?**, you MUST show exactly which 2 heuristics say D \
and which 2 say I in your reasoning.

## Boundary Type Rules
- **Exception and Error classes** (`*Error`, `*Exception`) are almost always **I**. \
They signal technical failures, not business rules — even if they reference a \
domain noun in their name.
- **Boundary DTOs** — Pydantic/dataclass models whose sole purpose is \
serialization, API request/response shape, or pass/fail reporting — without \
business invariants — are **I**, even if their name includes a domain noun.
- **Domain value objects** — Pydantic/dataclass models that encode business \
rules, domain invariants, or carry structured domain semantics beyond mere \
serialization — are **D** (e.g. a model defining what constitutes a valid \
workflow state or carrying domain-meaningful thresholds).
- **Session lifecycle and state objects** — types that model the identity, \
state, or lifecycle of an active work session (index entries, session pointers, \
session preflight check results, session health checks) are **D** when they \
carry session-semantic meaning — even if they look like pass/fail DTOs. The \
session concept is itself a core domain concept in this system, not a \
substitutable infrastructure detail (H1 → D). The pass/fail or persistence \
aspect is incidental; the domain question is "does this encode what a session \
IS or how a session transitions?" Distinguish from session storage helpers \
(file-path builders, JSON writers, config loaders) which remain **I**.

## Common Traps
- CLI command wrappers (`typer.command`, `click.command`) — always **I** regardless \
of what domain operation they invoke.
- Storage backends and registries (classes named `*Store`, `*Backend`, `*Registry`, \
`*Locator`) — **I** because they are substitutable implementations.
- Config loader functions (`load_*`, `save_*`, `get_*_dir`, `get_*_path`) — **I** \
because they are file/env I/O utilities.
- Functions named `create_*`, `update_*`, `delete_*` — check WHAT they create/update/delete. \
If it's a domain entity with business rules, **D**. If it's a DB row or API payload, **I**.
"""

_OUTPUT_SCHEMA_INSTRUCTION = """\

## Output Format

Return ONLY a JSON array (no markdown fences, no explanation). Each element \
must list the heuristic verdicts FIRST, then the derived label:
```
{
  "id": "<symbol id exactly as provided>",
  "heuristics": {
    "substitutability": "D" | "I",
    "what_changes_when": "D" | "I",
    "dependency_direction": "D" | "I",
    "ubiquitous_language": "D" | "I"
  },
  "ddd_layer": "D" | "I" | "?",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<1-2 sentence explanation>"
}
```

Each heuristic verdict must be D or I — never ?. The overall ddd_layer is \
derived from the majority vote of the 4 heuristics. Use ? for ddd_layer ONLY \
when the vote is exactly 2D-2I.

Return exactly one entry per symbol in the same order as the input.
"""


def build_classification_prompt(
    symbols: list[dict[str, object]],
    *,
    domain_context: str | None = None,
) -> str:
    """Build the full classification prompt with heuristics + symbols + output schema.

    When domain_context is provided, append a '## Domain Context' section
    with human-derived module identity information before the symbols.
    """
    parts = [_HEURISTIC_BUNDLE]

    if domain_context:
        parts.append(
            "\n## Domain Context\n\n"
            "The following modules have been reviewed by a domain expert:\n"
            f"{domain_context}\n\n"
            "Use this context when evaluating symbols from these modules. "
            "The heuristic tests still apply — this context helps resolve ambiguous cases."
        )

    if symbols:
        parts.append("\n## Symbols to Classify\n")
        for sym in symbols:
            parts.append(
                f"- **{sym.get('id', '?')}** [{sym.get('kind', '?')}] "
                f"module=`{sym.get('module', '?')}` "
                f"signature=`{sym.get('signature', '?')}` "
                f"file=`{sym.get('file', '?')}:{sym.get('line', '?')}`"
            )
    else:
        parts.append("\n## Symbols to Classify\n(none provided)\n")

    parts.append(_OUTPUT_SCHEMA_INSTRUCTION)
    return "\n".join(parts)
