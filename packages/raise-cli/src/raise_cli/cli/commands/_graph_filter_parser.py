"""CLI --filter token parser for graph query (S3, RAISE-16890).

Parses ``--filter campo:valor`` tokens into Condition/GraphFilter models.
Design decision D6: ``:`` as default separator (not bare ``=``).

Operator precedence: multi-char sigils (``!=``, ``>=``, ``<=``) are tried
before single-char (``>``, ``<``, ``=``, ``:``, ``~``) to avoid misparse.
A comma in the value promotes the op from ``eq`` to ``in``.
"""

from __future__ import annotations

from typing import Any, Literal

from raise_core.graph.filters import Condition, GraphFilter

ConditionOp = Literal[
    "eq",
    "neq",
    "in",
    "nin",
    "lt",
    "lte",
    "gt",
    "gte",
    "contains",
    "exists",
    "startswith",
]

_MULTI_CHAR_OPS: list[tuple[str, ConditionOp]] = [
    ("!=", "neq"),
    (">=", "gte"),
    ("<=", "lte"),
]

_SINGLE_CHAR_OPS: list[tuple[str, ConditionOp]] = [
    (">", "gt"),
    ("<", "lt"),
    ("~", "contains"),
    ("=", "eq"),
    (":", "eq"),
]

_ORDERING_OPS: frozenset[str] = frozenset({"lt", "lte", "gt", "gte"})


def _coerce_value(raw: str, op: ConditionOp) -> str | int | float:
    """Coerce a raw string value for ordering ops (gt/gte/lt/lte) to numeric."""
    if op not in _ORDERING_OPS:
        return raw
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def parse_filter_token(token: str) -> Condition:
    """Parse a single ``--filter`` token into a Condition.

    Split on the first recognized operator by position. Multi-char sigils
    at a given position win over single-char (``!=`` before ``!``).

    Raises:
        ValueError: When no recognized operator is found in the token.
    """
    all_ops: list[tuple[str, ConditionOp]] = _MULTI_CHAR_OPS + _SINGLE_CHAR_OPS
    best_idx = len(token)
    best_sigil: str = ""
    best_op: ConditionOp = "eq"
    for sigil, op in all_ops:
        idx = token.find(sigil)
        if idx > 0 and (
            idx < best_idx or (idx == best_idx and len(sigil) > len(best_sigil))
        ):
            best_idx = idx
            best_sigil = sigil
            best_op = op
    if best_idx < len(token):
        field = token[:best_idx]
        raw_value = token[best_idx + len(best_sigil) :]
        value: Any
        if best_op == "eq" and "," in raw_value:
            parts: Any = raw_value.split(",")
            return Condition(field=field, op="in", value=parts)
        value = _coerce_value(raw_value, best_op)
        return Condition(field=field, op=best_op, value=value)

    raise ValueError(
        f"Cannot parse filter token: {token!r}. "
        "Expected format: field:value or field<op>value "
        "(operators: :, =, !=, >=, <=, >, <, ~)"
    )


def parse_filter_tokens(tokens: list[str]) -> GraphFilter | None:
    """Parse multiple ``--filter`` tokens into a GraphFilter.

    Returns None when the token list is empty.
    """
    if not tokens:
        return None
    return GraphFilter(conditions=[parse_filter_token(t) for t in tokens])
