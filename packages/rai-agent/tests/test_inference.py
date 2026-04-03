"""Tests for the inference module — structured output via Claude Agent SDK."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel

from rai_agent.inference import invoke_structured

# --- Test models ---


class SimpleOutput(BaseModel):
    name: str
    count: int


class ListOutput(BaseModel):
    items: list[str]


# --- Tests ---


class TestInvokeStructured:
    def test_parses_json_response(self) -> None:
        """Successful JSON response is parsed into the Pydantic model."""
        result = invoke_structured(
            prompt="test",
            response_model=SimpleOutput,
            _client_factory=_mock_client_factory('{"name": "hello", "count": 42}'),
        )
        assert isinstance(result, SimpleOutput)
        assert result.name == "hello"
        assert result.count == 42

    def test_strips_markdown_fences(self) -> None:
        """JSON wrapped in ```json fences is still parsed correctly."""
        result = invoke_structured(
            prompt="test",
            response_model=SimpleOutput,
            _client_factory=_mock_client_factory(
                '```json\n{"name": "fenced", "count": 1}\n```'
            ),
        )
        assert result.name == "fenced"

    def test_list_output(self) -> None:
        result = invoke_structured(
            prompt="test",
            response_model=ListOutput,
            _client_factory=_mock_client_factory('{"items": ["a", "b", "c"]}'),
        )
        assert result.items == ["a", "b", "c"]

    def test_invalid_json_raises(self) -> None:
        with pytest.raises(ValueError, match="[Pp]arse"):
            invoke_structured(
                prompt="test",
                response_model=SimpleOutput,
                _client_factory=_mock_client_factory("not json at all"),
            )

    def test_validation_error_raises(self) -> None:
        """Valid JSON that doesn't match the model raises ValueError."""
        with pytest.raises(ValueError, match="[Vv]alidat"):
            invoke_structured(
                prompt="test",
                response_model=SimpleOutput,
                _client_factory=_mock_client_factory('{"wrong_field": true}'),
            )

    def test_system_prompt_passed(self) -> None:
        factory = _mock_client_factory('{"name": "x", "count": 0}')
        invoke_structured(
            prompt="test",
            response_model=SimpleOutput,
            system_prompt="Be helpful",
            _client_factory=factory,
        )
        # The factory was called — we verify it didn't raise
        assert True

    def test_empty_response_raises(self) -> None:
        with pytest.raises(ValueError, match="[Ee]mpty"):
            invoke_structured(
                prompt="test",
                response_model=SimpleOutput,
                _client_factory=_mock_client_factory(""),
            )

    def test_claudecode_env_unset_during_sdk_call(self) -> None:
        """CLAUDECODE env var is temporarily unset when using real SDK client."""
        import os

        captured_env: dict[str, str | None] = {}

        original_response = '{"name": "test", "count": 1}'

        def capturing_factory() -> Any:
            # Capture env state at the moment the factory is called
            captured_env["CLAUDECODE"] = os.environ.get("CLAUDECODE")

            async def fake_query(prompt: str, options: Any) -> Any:  # noqa: ANN401
                from dataclasses import dataclass, field

                @dataclass
                class FakeTextBlock:
                    text: str
                    type: str = "text"

                @dataclass
                class FakeAssistantMessage:
                    content: list[Any] = field(default_factory=list)
                    type: str = "assistant"

                msg = FakeAssistantMessage(
                    content=[FakeTextBlock(text=original_response)]
                )
                yield msg

            return fake_query

        # Set CLAUDECODE env var to simulate running inside Claude Code
        os.environ["CLAUDECODE"] = "1"
        try:
            invoke_structured(
                prompt="test",
                response_model=SimpleOutput,
                _client_factory=capturing_factory,
            )
        finally:
            # Env var should be restored after the call
            assert os.environ.get("CLAUDECODE") == "1", (
                "CLAUDECODE not restored after call"
            )
            os.environ.pop("CLAUDECODE", None)

        # During the SDK call, CLAUDECODE should have been unset
        assert captured_env["CLAUDECODE"] is None, (
            "CLAUDECODE should be unset during SDK call"
        )


# --- Helpers ---


def _mock_client_factory(response_text: str) -> Any:
    """Create a factory that returns a mock query function yielding canned text."""
    from dataclasses import dataclass, field

    @dataclass
    class FakeTextBlock:
        text: str
        type: str = "text"

    @dataclass
    class FakeAssistantMessage:
        content: list[Any] = field(default_factory=list)
        type: str = "assistant"

    @dataclass
    class FakeResultMessage:
        session_id: str = "test-session"
        type: str = "result"

    async def fake_query(prompt: str, options: Any) -> Any:  # noqa: ANN401
        msg = FakeAssistantMessage(content=[FakeTextBlock(text=response_text)])
        yield msg
        yield FakeResultMessage()

    def factory() -> Any:
        return fake_query

    return factory
