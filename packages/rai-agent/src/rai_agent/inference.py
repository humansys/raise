"""Structured inference via Claude Agent SDK.

Provides `invoke_structured()` — a synchronous function that sends a prompt
to Claude via the Agent SDK and returns a validated Pydantic model.

This is the approved inference mechanism for pipelines (see Confluence:
Inference Mechanism: Claude Agent SDK in rai-agent). The daemon uses
ClaudeRuntime (async, streaming); pipelines use this module (sync, structured).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from contextlib import contextmanager
from typing import Any, Generator, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# JSON fence pattern: ```json ... ``` or ``` ... ```
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)


@contextmanager
def _suspend_claudecode_env() -> Generator[None, None, None]:
    """Temporarily unset CLAUDECODE env var so SDK creates its own client."""
    saved = os.environ.pop("CLAUDECODE", None)
    try:
        yield
    finally:
        if saved is not None:
            os.environ["CLAUDECODE"] = saved


def invoke_structured(
    prompt: str,
    response_model: type[T],
    system_prompt: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    max_turns: int = 1,
    cwd: str | None = None,
    _client_factory: Any | None = None,
) -> T:
    """Send a prompt to Claude and parse the response as a Pydantic model.

    Uses the Claude Agent SDK (subprocess) for inference. The prompt should
    ask Claude to return JSON matching the response_model schema.

    Args:
        prompt: The user prompt (should request JSON output).
        response_model: Pydantic model class to validate the response against.
        system_prompt: Optional system prompt.
        model: Claude model ID.
        max_turns: Max agentic turns (1 for simple completion).
        cwd: Working directory for the Claude subprocess.
        _client_factory: Test injection point — returns an async generator factory.
    """
    schema_hint = json.dumps(response_model.model_json_schema(), indent=2)
    full_prompt = (
        f"{prompt}\n\n"
        f"Respond with ONLY valid JSON matching this schema:\n"
        f"```json\n{schema_hint}\n```"
    )

    text = _run_query(full_prompt, system_prompt, model, max_turns, cwd, _client_factory)

    if not text.strip():
        msg = "Empty response from Claude"
        raise ValueError(msg)

    return _parse_structured(text, response_model)


def _run_query(
    prompt: str,
    system_prompt: str | None,
    model: str,
    max_turns: int,
    cwd: str | None,
    client_factory: Any | None,
) -> str:
    """Run the Claude Agent SDK query and collect text output."""

    async def _async_query() -> str:
        if client_factory is not None:
            query_fn = client_factory()
        else:
            from claude_agent_sdk import ClaudeAgentOptions, query as sdk_query

            options = ClaudeAgentOptions(
                system_prompt=system_prompt,
                permission_mode="bypassPermissions",
                max_turns=max_turns,
                model=model,
            )
            if cwd:
                options.cwd = cwd

            async def _sdk_gen(prompt: str, options: Any) -> Any:  # noqa: ANN401
                async for msg in sdk_query(prompt=prompt, options=options):
                    yield msg

            query_fn = lambda: _sdk_gen  # noqa: E731

            # Use the SDK directly
            from claude_agent_sdk.types import AssistantMessage, TextBlock

            text_parts: list[str] = []
            async for msg in sdk_query(prompt=prompt, options=options):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            text_parts.append(block.text)
            return "".join(text_parts)

        # Mock path: use the factory
        text_parts_mock: list[str] = []
        async for msg in query_fn(prompt=prompt, options=None):
            if hasattr(msg, "content"):
                for block in msg.content:
                    if hasattr(block, "text"):
                        text_parts_mock.append(block.text)
        return "".join(text_parts_mock)

    # Bridge async → sync
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None and loop.is_running():
        msg = (
            "invoke_structured called from within a running event loop. "
            "Use 'await' or run from a sync context."
        )
        raise RuntimeError(msg)

    with _suspend_claudecode_env():
        return asyncio.run(_async_query())


def _parse_structured(text: str, model: type[T]) -> T:
    """Extract JSON from text (stripping markdown fences) and validate."""
    # Try to extract from markdown fences first
    match = _JSON_FENCE_RE.search(text)
    json_str = match.group(1) if match else text.strip()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        msg = f"Parse error: could not extract valid JSON from response: {exc}"
        raise ValueError(msg) from exc

    try:
        return model.model_validate(data)
    except ValidationError as exc:
        msg = f"Validation error: response JSON does not match {model.__name__}: {exc}"
        raise ValueError(msg) from exc
