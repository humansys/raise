"""Pipeline `when` expression grammar — parsing, validation and evaluation.

Extracted from ``engine.py`` (RAISE-18252) so ``loader.py`` can validate
``when`` expressions at load time without importing ``engine.py`` — which
already imports ``loader.py`` for ``PipelineLoader``/``PipelineError``, so the
reverse import would cycle. ``engine.py`` re-exports :func:`evaluate_when` for
existing callers (``mcp_tools_pipeline.py``).

Story: S1065.3 — Story Pipeline YAML (RAISE-1081)
Bug: RAISE-18252 — fail-open on unsupported `when` (evaluate_when returned
True and nothing validated the expression at load time). Fixed here:
fail-loud at both load time (``is_supported_when`` / ``validate_when``, used
by ``PipelineLoader``) and evaluation time (``evaluate_when`` raises instead
of defaulting to True). NOT fail-closed (``return False``) — silently
skipping a phase is equally silent and violates ADR-116's "fail-safe toward
MORE ceremony".
"""

import re

from raise_cli.exceptions import RaiError

_WHEN_RE_EQ = re.compile(r"^(\w+)\s*==\s*'([^']*)'$")
_WHEN_RE_NEQ = re.compile(r"^(\w+)\s*!=\s*'([^']*)'$")
# Proportionality aspect (ADR-116): ordinal `size >= X` / `size > X`.
_WHEN_RE_SIZE = re.compile(r"^size\s*(>=|>)\s*([A-Za-z]+)$")

# Fixed ordinal size scale. Unknown/missing size resolves to the largest tier so
# nothing is ever silently skipped on ambiguity (fail-safe toward MORE ceremony).
_SIZE_ORDER: tuple[str, ...] = ("XS", "S", "M", "L")


class UnsupportedWhenExpressionError(RaiError):
    """Raised when a ``when`` expression is outside the supported grammar.

    Covers both defense-in-depth evaluation-time rejection
    (:func:`evaluate_when`) and is the error `PipelineLoader` wraps into a
    `PipelineError` naming the pipeline/phase at load time (RAISE-18252).
    Fail-loud, never fail-open (``return True``) or fail-closed
    (``return False``).
    """

    exit_code: int = 7
    error_code: str = "E016"


def _size_rank(value: str) -> int:
    """Rank a size on the fixed scale; unknown/missing → largest (fail-safe)."""
    try:
        return _SIZE_ORDER.index(value.strip().upper())
    except ValueError:
        return len(_SIZE_ORDER) - 1


def is_supported_when(expr: str) -> bool:
    """Return True if ``expr`` matches the supported ``when`` grammar."""
    expr = expr.strip()
    return bool(
        _WHEN_RE_EQ.match(expr) or _WHEN_RE_NEQ.match(expr) or _WHEN_RE_SIZE.match(expr)
    )


def validate_when(expr: str, *, phase_id: str, pipeline_name: str) -> None:
    """Raise ``UnsupportedWhenExpressionError`` if ``expr`` is outside the grammar.

    Intended for load-time use (``PipelineLoader``) so a malformed guard
    fails loud before any phase can silently run or skip.
    """
    if not is_supported_when(expr):
        msg = (
            f"pipeline '{pipeline_name}' phase '{phase_id}' has unsupported "
            f"when expression: {expr!r}"
        )
        raise UnsupportedWhenExpressionError(msg)


def evaluate_when(expr: str, context: dict[str, str]) -> bool:
    """Evaluate a simple when expression against a context dict.

    Supports ``key == 'value'``, ``key != 'value'``, and the ordinal size
    predicate ``size >= X`` / ``size > X`` over the scale XS < S < M < L
    (ADR-116). Missing ``size`` resolves to the largest tier (fail-safe).
    Other missing keys resolve to empty string.

    Raises:
        UnsupportedWhenExpressionError: ``expr`` is outside the grammar.
            Loading a pipeline already rejects this via
            :func:`validate_when` / ``PipelineLoader``; this is defense in
            depth for run snapshots persisted before that validation existed
            (RAISE-18252). Never fail-open (``return True``).
    """
    expr = expr.strip()

    match = _WHEN_RE_EQ.match(expr)
    if match:
        key, value = match.group(1), match.group(2)
        return context.get(key, "") == value

    match = _WHEN_RE_NEQ.match(expr)
    if match:
        key, value = match.group(1), match.group(2)
        return context.get(key, "") != value

    match = _WHEN_RE_SIZE.match(expr)
    if match:
        op, threshold = match.group(1), match.group(2)
        actual = _size_rank(context.get("size", ""))
        wanted = _size_rank(threshold)
        return actual >= wanted if op == ">=" else actual > wanted

    msg = f"unsupported when expression: {expr!r}"
    raise UnsupportedWhenExpressionError(msg)
