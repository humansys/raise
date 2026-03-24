"""Tests for ExpressionEvaluator.

TDD RED phase — all tests should fail until implementation.
AC refs: s337.1-story.md scenarios 1-7.
"""

from __future__ import annotations

import json

import pytest

from raise_cli.adapters.declarative.expressions import ExpressionEvaluator


@pytest.fixture
def evaluator() -> ExpressionEvaluator:
    return ExpressionEvaluator()


# --- AC Scenario 1: Simple variable substitution ---


class TestSimpleSubstitution:
    def test_simple_var(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ name }}", {"name": "hello"})
        assert result == "hello"

    def test_var_with_spaces(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{name}}", {"name": "hello"})
        assert result == "hello"

    def test_missing_var_raises(self, evaluator: ExpressionEvaluator) -> None:
        with pytest.raises(KeyError, match="unknown"):
            evaluator.evaluate("{{ unknown }}", {"name": "hello"})

    def test_none_value_returns_none(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ val }}", {"val": None})
        assert result is None


# --- AC Scenario 2: Dot-access ---


class TestDotAccess:
    def test_single_level(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate(
            "{{ issue.summary }}", {"issue": {"summary": "Fix bug"}}
        )
        assert result == "Fix bug"

    def test_nested_levels(self, evaluator: ExpressionEvaluator) -> None:
        ctx = {"a": {"b": {"c": "deep"}}}
        result = evaluator.evaluate("{{ a.b.c }}", ctx)
        assert result == "deep"

    def test_missing_nested_key_raises(self, evaluator: ExpressionEvaluator) -> None:
        with pytest.raises(KeyError):
            evaluator.evaluate("{{ a.b.missing }}", {"a": {"b": {"c": 1}}})

    def test_dot_access_on_non_dict_raises(
        self, evaluator: ExpressionEvaluator
    ) -> None:
        with pytest.raises((KeyError, TypeError)):
            evaluator.evaluate("{{ a.b }}", {"a": "string"})


# --- AC Scenario 3: Filter — str ---


class TestFilterStr:
    def test_int_to_str(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ value | str }}", {"value": 42})
        assert result == "42"

    def test_none_to_str(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ value | str }}", {"value": None})
        assert result == "None"

    def test_already_str(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ value | str }}", {"value": "hello"})
        assert result == "hello"


# --- AC Scenario 4: Filter — default ---


class TestFilterDefault:
    def test_missing_key_uses_default(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ missing | default('fallback') }}", {})
        assert result == "fallback"

    def test_none_value_uses_default(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ val | default('fallback') }}", {"val": None})
        assert result == "fallback"

    def test_present_value_ignores_default(
        self, evaluator: ExpressionEvaluator
    ) -> None:
        result = evaluator.evaluate(
            "{{ val | default('fallback') }}", {"val": "actual"}
        )
        assert result == "actual"

    def test_empty_string_is_not_none(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ val | default('fallback') }}", {"val": ""})
        assert result == ""


# --- AC Scenario 5: Filter — pluck ---


class TestFilterPluck:
    def test_pluck_field(self, evaluator: ExpressionEvaluator) -> None:
        ctx = {"items": [{"name": "a"}, {"name": "b"}]}
        result = evaluator.evaluate("{{ items | pluck('name') }}", ctx)
        assert result == ["a", "b"]

    def test_pluck_empty_list(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ items | pluck('name') }}", {"items": []})
        assert result == []

    def test_pluck_missing_field_raises(self, evaluator: ExpressionEvaluator) -> None:
        ctx = {"items": [{"name": "a"}, {"other": "b"}]}
        with pytest.raises(KeyError):
            evaluator.evaluate("{{ items | pluck('name') }}", ctx)


# --- AC Scenario 6: Filter — json ---


class TestFilterJson:
    def test_dict_to_json(self, evaluator: ExpressionEvaluator) -> None:
        ctx = {"data": {"key": "value"}}
        result = evaluator.evaluate("{{ data | json }}", ctx)
        assert json.loads(result) == {"key": "value"}

    def test_list_to_json(self, evaluator: ExpressionEvaluator) -> None:
        ctx = {"data": [1, 2, 3]}
        result = evaluator.evaluate("{{ data | json }}", ctx)
        assert json.loads(result) == [1, 2, 3]


# --- AC Scenario 7: Literal passthrough ---


class TestLiteralPassthrough:
    def test_plain_string(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("hello world", {})
        assert result == "hello world"

    def test_empty_string(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("", {})
        assert result == ""

    def test_string_with_no_template(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("just text", {"name": "ignored"})
        assert result == "just text"


# --- evaluate_args ---


class TestEvaluateArgs:
    def test_evaluates_all_keys(self, evaluator: ExpressionEvaluator) -> None:
        args = {"title": "{{ issue.summary }}", "count": "{{ limit }}"}
        ctx = {"issue": {"summary": "Fix bug"}, "limit": 10}
        result = evaluator.evaluate_args(args, ctx)
        assert result == {"title": "Fix bug", "count": 10}

    def test_literal_values_pass_through(self, evaluator: ExpressionEvaluator) -> None:
        args = {"type": "Bug", "project": "{{ key }}"}
        result = evaluator.evaluate_args(args, {"key": "PROJ"})
        assert result == {"type": "Bug", "project": "PROJ"}

    def test_empty_args(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate_args({}, {"key": "val"})
        assert result == {}


# --- Filter chaining (dot-access + filter) ---


class TestCombined:
    def test_dot_access_with_str_filter(self, evaluator: ExpressionEvaluator) -> None:
        result = evaluator.evaluate("{{ data.number | str }}", {"data": {"number": 42}})
        assert result == "42"

    def test_dot_access_with_default_filter(
        self, evaluator: ExpressionEvaluator
    ) -> None:
        result = evaluator.evaluate("{{ data.missing | default('n/a') }}", {"data": {}})
        assert result == "n/a"
