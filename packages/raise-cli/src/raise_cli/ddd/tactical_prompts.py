"""DDD tactical classification prompt bundle.

Mirrors heuristics.py structure: private bundle constant + output schema constant
+ public builder function. Used by the Pass 3 tactical classification runner
(out of scope for this story — this module provides the prompt only).
"""

from __future__ import annotations

_TACTICAL_HEURISTIC_BUNDLE = """\
You are a Domain-Driven Design expert. You will receive symbols that have \
already been classified as Domain (D) layer. Your task is to identify which \
tactical DDD pattern each symbol represents.

## Tactical Patterns

### entity
Definition: Mutable domain object with a distinct identity.
- Positive: has an ID field (`id`, `uuid`, `pk`, `*_id`); has lifecycle methods \
(`create`, `activate`, `close`, `deactivate`); has mutating methods \
(`set_status`, `update_*`, `assign_*`); Pydantic model without `frozen=True`.
- Negative: frozen dataclass, NamedTuple, Protocol, ABC.

### value_object
Definition: Immutable domain concept with equality by value, not identity.
- Positive: no ID field; `frozen=True` on Pydantic model, or `NamedTuple`; \
equality by field content (`__eq__` compares all fields); carries domain \
semantics (e.g., Money, DateRange, Confidence).
- Negative: has an ID field; has mutating methods; has lifecycle transitions.

### domain_service
Definition: Stateless operation on domain objects that does not naturally \
belong to any entity or value object.
- Positive: module-level function or class with no mutable `__init__` state; \
takes domain objects as arguments; coordinates across multiple entities; \
no identity, no persistence.
- Negative: stores instance state; creates or owns entities; has infrastructure \
imports.

### domain_event
Definition: Immutable record of something that happened in the domain.
- Positive: name ends in past-tense suffix (`Occurred`, `Completed`, `Failed`, \
`Requested`, `Approved`, `Detected`, `Resolved`, `Event`); carries a context \
snapshot of relevant state at the moment of occurrence; immutable (frozen or \
NamedTuple).
- Negative: mutable fields; has behavior methods beyond property access; \
command-style name (imperative verb).

### aggregate_root
Definition: Entity that controls a consistency boundary and is the single \
entry point to its cluster.
- Positive: entity that holds references to other entities (child lists/dicts); \
enforces invariants across the cluster (validation on mutation); other entities \
in the cluster are accessible only through this root; has `id` field.
- Negative: references no child entities; is referenced BY another entity as \
a child.

### factory
Definition: Creates complex domain objects, hiding construction logic and \
assembly from callers.
- Positive: function or class that returns an entity or aggregate; name includes \
`create_`, `build_`, `make_`, `*Factory`, `*Builder`; validates and assembles \
all required parts before returning; hides the constructor.
- Negative: takes an already-constructed object and transforms it; modifies \
existing entities; is a repository (returns from persistence, not construction).

### repository_interface
Definition: Domain-side port for persistence — an abstract contract that \
infrastructure implements.
- Positive: `Protocol`, `ABC`, or abstract class; methods are domain operations \
(`get`, `find`, `save`, `add`, `remove`, `list`); no infrastructure imports \
(no SQLite, HTTP, file I/O); name ends in `*Repository`, `*Store`, `*Port`, \
`*Backend` (domain side only).
- Negative: concrete implementation; has infrastructure imports; extends a \
framework ORM base class.

## Common Traps

- `*Error` / `*Exception` classes are never tactical domain types (they are \
infrastructure signals).
- Pydantic models that only shape API requests/responses are NOT value objects \
unless they carry business invariants.
- A `*Store` concrete class (e.g., `SQLiteGraphBackend`) is infrastructure, \
not a repository_interface — even if it implements one.
- `build_*` / `create_*` functions that build CLI payloads (not domain objects) \
are NOT factories.

## Anti-Abstention Rule

Every symbol must receive a definite classification. Unlike D/I classification, \
there is no `?` escape hatch here — a symbol has already been confirmed as Domain \
layer before reaching tactical classification. You MUST assign one of the seven \
tactical types. Choose the best fit based on the heuristics above.\
"""

_TACTICAL_OUTPUT_SCHEMA = """\

## Output Format

Return ONLY a JSON array (no markdown fences, no explanation). Each element:
{
  "id": "<symbol id as provided>",
  "tactical_type": "entity" | "value_object" | "domain_service" | \
"domain_event" | "aggregate_root" | "factory" | "repository_interface",
  "confidence": <float 0.0-1.0>,
  "rationale": "<1-2 sentence explanation citing the specific indicators>"
}

Return exactly one entry per symbol in the same order as the input.\
"""


def build_tactical_classification_prompt(
    symbols: list[dict[str, object]],
    *,
    domain_context: str | None = None,
) -> str:
    """Build the full tactical classification prompt.

    Mirrors build_classification_prompt() signature for caller-side symmetry.
    Symbols use the same dict schema: id, module, kind, signature, file, line.
    The optional domain_context parameter works identically to heuristics.py.
    """
    parts = [_TACTICAL_HEURISTIC_BUNDLE]

    if domain_context:
        parts.append(
            "\n## Domain Context\n\n"
            "The following modules have been reviewed by a domain expert:\n"
            f"{domain_context}\n\n"
            "Use this context when evaluating symbols from these modules. "
            "The heuristic tests still apply — this context helps resolve "
            "ambiguous cases."
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

    parts.append(_TACTICAL_OUTPUT_SCHEMA)
    return "\n".join(parts)
