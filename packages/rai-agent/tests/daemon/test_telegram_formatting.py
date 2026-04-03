"""Tests for Telegram Markdown → entity conversion (RAI-31)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from rai_agent.daemon.telegram import convert_for_telegram

if TYPE_CHECKING:
    from telegram import MessageEntity


def _find_entity(
    entities: list[MessageEntity], entity_type: str
) -> MessageEntity | None:
    """Find first entity of given type."""
    return next((e for e in entities if e.type == entity_type), None)


class TestConvertForTelegram:
    """Unit tests for convert_for_telegram() helper."""

    def test_bold_converts_to_entity(self) -> None:
        text, entities = convert_for_telegram("**bold text**")
        assert "bold text" in text
        assert entities is not None
        bold = _find_entity(entities, "bold")
        assert bold is not None

    def test_italic_converts_to_entity(self) -> None:
        text, entities = convert_for_telegram("*italic text*")
        assert "italic text" in text
        assert entities is not None
        italic = _find_entity(entities, "italic")
        assert italic is not None

    def test_code_block_converts(self) -> None:
        md = "```python\nprint('hello')\n```"
        text, entities = convert_for_telegram(md)
        assert "print" in text
        assert entities is not None
        pre = _find_entity(entities, "pre")
        assert pre is not None

    def test_inline_code_converts(self) -> None:
        text, entities = convert_for_telegram("use `foo()` here")
        assert "foo()" in text
        assert entities is not None
        code = _find_entity(entities, "code")
        assert code is not None

    def test_header_converts_to_bold(self) -> None:
        text, entities = convert_for_telegram("## Section Title")
        assert "Section Title" in text
        assert entities is not None
        bold = _find_entity(entities, "bold")
        assert bold is not None

    def test_nested_formatting(self) -> None:
        _text, entities = convert_for_telegram("**bold _and italic_**")
        assert entities is not None
        assert len(entities) >= 2
        bold = _find_entity(entities, "bold")
        italic = _find_entity(entities, "italic")
        assert bold is not None
        assert italic is not None

    def test_link_converts(self) -> None:
        text, entities = convert_for_telegram("[click](https://example.com)")
        assert "click" in text
        assert entities is not None
        link = _find_entity(entities, "text_link")
        assert link is not None
        assert link.url == "https://example.com"

    def test_returns_ptb_message_entities(self) -> None:
        """Entities must be PTB MessageEntity, not library's own type."""
        from telegram import MessageEntity  # type: ignore[import-untyped]

        _text, entities = convert_for_telegram("**bold**")
        assert entities is not None
        assert all(isinstance(e, MessageEntity) for e in entities)

    def test_plain_text_returns_no_entities(self) -> None:
        text, entities = convert_for_telegram("just plain text")
        assert text == "just plain text"
        assert entities is not None
        assert len(entities) == 0

    def test_fallback_on_conversion_error(self) -> None:
        with patch(
            "rai_agent.daemon.telegram.telegramify_markdown_convert",
            side_effect=ValueError("parse error"),
        ):
            text, entities = convert_for_telegram("**will fail**")
        assert text == "**will fail**"
        assert entities is None
