"""Mini expression evaluator for declarative adapter templates.

Supports: ``{{ var }}``, ``{{ obj.field }}``, ``{{ value | filter }}``.
Filters: ``str``, ``default('fallback')``, ``pluck('field')``, ``json``.

~100 LOC, zero external dependencies.

Architecture: ADR-041 (D2 — mini evaluator, not Jinja2)
"""

from __future__ import annotations

import json
import re
from typing import Any, cast

# Matches {{ expression }} with optional whitespace
_TEMPLATE_RE = re.compile(r"\{\{\s*(.+?)\s*\}\}")

# Matches filter with optional quoted argument: filter_name('arg')
_FILTER_RE = re.compile(r"(\w+)\s*(?:\(\s*'([^']*)'\s*\))?")


class ExpressionEvaluator:
    """Evaluate template expressions against a context dict.

    Designed for declarative MCP adapter YAML configs. Intentionally
    minimal — covers dot-access and 4 filters. Not a general-purpose
    template engine.
    """

    def evaluate(self, template: str, context: dict[str, Any]) -> Any:
        """Evaluate a single template string against context.

        Args:
            template: Template string, e.g. ``"{{ issue.summary | str }}"``.
            context: Variable context dict.

        Returns:
            Resolved value. Type depends on expression — may be str, int,
            list, dict, None, etc.

        Raises:
            KeyError: If a referenced variable is not in context.
        """
        match = _TEMPLATE_RE.fullmatch(template.strip()) if template else None
        if match is None:
            # Literal passthrough — no {{ }} found
            return template

        expr = match.group(1).strip()
        return self._eval_expr(expr, context)

    def evaluate_args(
        self, args: dict[str, str], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate all values in an args dict.

        Args:
            args: Mapping of param name → template string.
            context: Variable context dict.

        Returns:
            New dict with all values resolved.
        """
        return {key: self.evaluate(tmpl, context) for key, tmpl in args.items()}

    def _eval_expr(self, expr: str, context: dict[str, Any]) -> Any:
        """Evaluate an expression, optionally with a pipe filter."""
        # Split on pipe: "value | filter('arg')"
        parts = expr.split("|", maxsplit=1)
        var_path = parts[0].strip()

        try:
            value = self._resolve_path(var_path, context)
        except KeyError:
            # If there's a default filter, use it; otherwise re-raise
            if len(parts) > 1 and "default" in parts[1]:
                value = None
            else:
                raise

        if len(parts) > 1:
            filter_expr = parts[1].strip()
            value = self._apply_filter(filter_expr, value, context)

        return value

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dot-separated path against context.

        ``"issue.summary"`` → ``context["issue"]["summary"]``
        """
        parts = path.split(".")
        current: Any = context

        for part in parts:
            if isinstance(current, dict):
                if part not in current:
                    raise KeyError(part)
                current = cast("Any", current[part])
            else:
                raise KeyError(part)

        return current

    def _apply_filter(
        self, filter_expr: str, value: Any, context: dict[str, Any]
    ) -> Any:
        """Apply a filter to a value."""
        match = _FILTER_RE.fullmatch(filter_expr)
        if not match:
            msg = f"Invalid filter expression: {filter_expr}"
            raise ValueError(msg)

        filter_name = match.group(1)
        filter_arg = match.group(2)  # None if no arg

        if filter_name == "str":
            return str(value)
        if filter_name == "json":
            return json.dumps(value)
        if filter_name == "default":
            if value is None:
                return filter_arg
            # Also handle KeyError case — caller catches and retries with default
            return value
        if filter_name == "pluck":
            if not isinstance(value, list):
                msg = f"pluck requires a list, got {type(value).__name__}"
                raise TypeError(msg)
            if filter_arg is None:
                msg = "pluck requires a field argument"
                raise ValueError(msg)
            return [
                self._pluck_item(item, filter_arg) for item in cast("list[Any]", value)
            ]

        msg = f"Unknown filter: {filter_name}"
        raise ValueError(msg)

    @staticmethod
    def _pluck_item(item: Any, field: str) -> Any:
        """Extract a field from a dict item, raising KeyError if missing."""
        if isinstance(item, dict):
            if field not in item:
                raise KeyError(field)
            return cast("Any", item[field])
        msg = f"pluck expects dict items, got {type(item).__name__}"
        raise TypeError(msg)
