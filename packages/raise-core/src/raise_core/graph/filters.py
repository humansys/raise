"""Structured filter models for graph queries.

Defines the Pydantic contract (`Condition`, `GraphFilter`) that CLI/MCP
callers compile user input into, plus the pure evaluator (`evaluate_condition`)
that `QueryEngine` runs against node metadata (RAISE-16889, S2).

AC1: this module contains no query-language statement strings — filters
are evaluated in plain Python against in-memory metadata dicts, never
translated to a database query syntax. A future translator to such a
syntax, if ever built, would consume `Condition` as its input contract
(epic D1/D3 — rejected for this story).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

FilterOp = Literal[
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

FilterScalar = str | int | float | bool
FilterValue = FilterScalar | list[FilterScalar] | None


def _is_ordering_value(value: Any) -> bool:
    """True if value is a valid operand for lt/lte/gt/gte.

    Numeric (int/float, bool excluded) or an ISO date/datetime string.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
        except ValueError:
            return False
        return True
    return False


def _validate_eq_neq(value: Any) -> str | None:
    if (
        value is None
        or isinstance(value, list)
        or not isinstance(value, (str, int, float, bool))
    ):
        return "eq/neq require a scalar value (str/int/float/bool)"
    return None


def _validate_in_nin(value: Any) -> str | None:
    if not isinstance(value, list):
        return "in/nin require a list value"
    return None


def _validate_ordering(value: Any) -> str | None:
    if not _is_ordering_value(value):
        return "ordering ops require a number or ISO date/datetime string"
    return None


def _validate_contains(value: Any) -> str | None:
    if (
        value is None
        or isinstance(value, (list, bool))
        or not isinstance(value, (str, int, float))
    ):
        return "contains requires a scalar value (str/int/float)"
    return None


def _validate_startswith(value: Any) -> str | None:
    if not isinstance(value, str):
        return "startswith requires a string value"
    return None


def _validate_exists(value: Any) -> str | None:
    if value is not None:
        return "exists takes no value (presence check only)"
    return None


_OP_VALUE_VALIDATORS: dict[FilterOp, Any] = {
    "eq": _validate_eq_neq,
    "neq": _validate_eq_neq,
    "in": _validate_in_nin,
    "nin": _validate_in_nin,
    "lt": _validate_ordering,
    "lte": _validate_ordering,
    "gt": _validate_ordering,
    "gte": _validate_ordering,
    "contains": _validate_contains,
    "startswith": _validate_startswith,
    "exists": _validate_exists,
}


class Condition(BaseModel):
    """Single filter predicate on a metadata field.

    Op/value compatibility is validated at construction time (AC5) — a
    malformed condition (e.g. ``gt`` with a non-numeric, non-date string)
    fails loud here, not silently during evaluation.
    """

    field: str = Field(..., min_length=1, description="Metadata field name")
    op: FilterOp
    value: FilterValue = None

    @model_validator(mode="after")
    def _validate_op_value(self) -> Condition:
        validator = _OP_VALUE_VALIDATORS[self.op]
        error = validator(self.value)
        if error is not None:
            raise ValueError(error)
        return self


class GraphFilter(BaseModel):
    """Collection of conditions applied as an AND-implicit conjunction.

    An empty condition list is rejected at construction: a filter that
    filters nothing is always a caller bug, not a valid "match everything"
    query (fail loud, D-S2.1).
    """

    conditions: list[Condition] = Field(..., min_length=1)

    def matches(self, metadata: dict[str, Any]) -> bool:
        """True if `metadata` satisfies every condition (AND semantics)."""
        return all(evaluate_condition(metadata, c) for c in self.conditions)


def _lookup_field(metadata: dict[str, Any], field: str) -> Any:
    """Resolve `field` in `metadata`, falling back one hop into `custom_fields`.

    Absent key and an explicit ``None`` value deliberately collapse: Jira's
    "unset" is stored as `None` (e.g. `assignee`), so distinguishing "key
    absent" from "key present but None" would create two spellings of "no
    value" for callers to reason about.

    A top-level key shadows a `custom_fields` key of the same name — only
    one hop is attempted, not a generic dotted-path/JSONPath walk (S1
    produces exactly one nested container; a path grammar is complexity
    without a driver).
    """
    actual = metadata.get(field)
    if actual is None:
        custom_fields = metadata.get("custom_fields")
        if isinstance(custom_fields, dict):
            actual = custom_fields.get(field)
    return actual


def _eval_eq(actual: Any, value: Any) -> bool:
    # No str<->number coercion: silent coercion in equality invites false
    # positives ("5" would equal 5). Ordering ops coerce; eq does not.
    return actual == value


def _eval_neq(actual: Any, value: Any) -> bool:
    # THE FOOTGUN: neq does NOT match an absent/None field. An absent field
    # is not "not equal to X" in this model — it is "no opinion". Matching
    # it would make `neq` a stealth existence filter, diverging from JQL
    # (the mental model of anyone filtering Jira-sourced data). `is empty`
    # sugar is Phase 2; use `exists` to test presence explicitly.
    return actual is not None and actual != value


def _eval_in(actual: Any, value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return actual in value


def _eval_nin(actual: Any, value: Any) -> bool:
    # Same absent-semantics as neq, for consistency: absent → False, not True.
    if actual is None:
        return False
    if not isinstance(value, list):
        return False
    return actual not in value


def _coerce_numeric_pair(actual: Any, value: Any) -> tuple[float, float] | None:
    """Coerce (actual, value) into comparable floats, or None if impossible."""
    if isinstance(actual, bool) or isinstance(value, bool):
        return None
    try:
        return float(actual), float(value)
    except (TypeError, ValueError):
        return None


def _coerce_datetime_pair(actual: Any, value: str) -> tuple[datetime, datetime] | None:
    """Coerce (actual, value) into comparable datetimes, or None if impossible."""
    if not isinstance(actual, str):
        return None
    try:
        return datetime.fromisoformat(actual), datetime.fromisoformat(value)
    except ValueError:
        return None


def _compare(left: float, right: float, op: Literal["lt", "lte", "gt", "gte"]) -> bool:
    if op == "lt":
        return left < right
    if op == "lte":
        return left <= right
    if op == "gt":
        return left > right
    return left >= right  # gte


def _eval_ordering(
    actual: Any, value: Any, op: Literal["lt", "lte", "gt", "gte"]
) -> bool:
    if actual is None:
        return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        numeric_pair = _coerce_numeric_pair(actual, value)
        if numeric_pair is None:
            return False
        return _compare(numeric_pair[0], numeric_pair[1], op)
    if isinstance(value, str):
        datetime_pair = _coerce_datetime_pair(actual, value)
        if datetime_pair is None:
            return False
        left, right = datetime_pair
        try:
            if op == "lt":
                return left < right
            if op == "lte":
                return left <= right
            if op == "gt":
                return left > right
            return left >= right  # gte
        except TypeError:
            # aware vs naive datetime comparison
            return False
    return False


def _eval_contains(actual: Any, value: Any) -> bool:
    if isinstance(actual, list):
        return value in actual
    if isinstance(actual, str):
        return str(value) in actual
    return False


def _eval_startswith(actual: Any, value: Any) -> bool:
    if not isinstance(actual, str) or not isinstance(value, str):
        return False
    return actual.startswith(value)


def _eval_exists(actual: Any) -> bool:
    # A key explicitly set to None does NOT exist — one rule, documented.
    return actual is not None


def evaluate_condition(metadata: dict[str, Any], cond: Condition) -> bool:
    """Evaluate a single `Condition` against a metadata dict.

    Total: never raises, regardless of metadata shape (str, None, list,
    nested dict, int, float, bool). Runtime type mismatches resolve to
    `False` — validation errors belong at `Condition` construction (AC5),
    not here; this function runs over thousands of heterogeneous nodes per
    query and one malformed node must not fail the whole query.
    """
    actual = _lookup_field(metadata, cond.field)
    op = cond.op
    value = cond.value

    if op == "eq":
        return _eval_eq(actual, value)
    if op == "neq":
        return _eval_neq(actual, value)
    if op == "in":
        return _eval_in(actual, value)
    if op == "nin":
        return _eval_nin(actual, value)
    if op in ("lt", "lte", "gt", "gte"):
        return _eval_ordering(actual, value, op)
    if op == "contains":
        return _eval_contains(actual, value)
    if op == "startswith":
        return _eval_startswith(actual, value)
    if op == "exists":
        return _eval_exists(actual)
    return False
