# pyright: reportPrivateUsage=false
"""Tests for Telegram image handling (S7.5)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from rai_agent.daemon.image import (
    DEFAULT_IMAGE_PROMPT,
    MAX_IMAGE_SIZE,
)
from rai_agent.daemon.telegram import download_telegram_image

if TYPE_CHECKING:
    from rai_agent.daemon.middleware import MessageContext


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_photo_message(
    *,
    photo_data: bytes = b"\xff\xd8\xff" + b"\x00" * 100,
    caption: str | None = None,
    has_document: bool = False,
    doc_mime: str = "image/png",
    doc_data: bytes | None = None,
) -> Any:
    """Create a mock Telegram Message with photo or document."""
    msg = MagicMock()
    msg.chat_id = 123
    msg.caption = caption
    msg.reply_text = AsyncMock()

    if has_document:
        msg.photo = None
        msg.document = MagicMock()
        msg.document.mime_type = doc_mime
        file_mock = AsyncMock()
        file_mock.download_as_bytearray = AsyncMock(
            return_value=bytearray(doc_data or photo_data),
        )
        msg.document.get_file = AsyncMock(return_value=file_mock)
    else:
        # photo is an array of PhotoSize, [-1] is highest res
        # Use separate MagicMock instances with their own get_file
        low_res = MagicMock()
        low_res.get_file = AsyncMock()
        mid_res = MagicMock()
        mid_res.get_file = AsyncMock()
        high_res = MagicMock()
        file_mock = AsyncMock()
        file_mock.download_as_bytearray = AsyncMock(
            return_value=bytearray(photo_data),
        )
        high_res.get_file = AsyncMock(return_value=file_mock)
        msg.photo = [low_res, mid_res, high_res]
        msg.document = None

    return msg


# ── download_telegram_image ─────────────────────────────────────────────────


class TestDownloadTelegramImage:
    """Tests for download_telegram_image()."""

    @pytest.mark.asyncio
    async def test_photo_returns_jpeg(self) -> None:
        msg = _make_photo_message()
        data, mime = await download_telegram_image(msg)
        assert mime == "image/jpeg"
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_photo_uses_highest_resolution(self) -> None:
        """Should use photo[-1] (last = highest res)."""
        msg = _make_photo_message()
        await download_telegram_image(msg)
        # Only the last PhotoSize should have get_file called
        msg.photo[-1].get_file.assert_awaited_once()
        msg.photo[0].get_file.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_document_image_returns_original_mime(self) -> None:
        msg = _make_photo_message(
            has_document=True, doc_mime="image/png",
        )
        data, mime = await download_telegram_image(msg)
        assert mime == "image/png"

    @pytest.mark.asyncio
    async def test_document_unsupported_mime_raises(self) -> None:
        msg = _make_photo_message(
            has_document=True, doc_mime="image/tiff",
        )
        with pytest.raises(ValueError, match="no está soportado"):
            await download_telegram_image(msg)

    @pytest.mark.asyncio
    async def test_no_photo_no_document_raises(self) -> None:
        msg = MagicMock()
        msg.photo = None
        msg.document = None
        with pytest.raises(ValueError, match="no image"):
            await download_telegram_image(msg)

    @pytest.mark.asyncio
    async def test_document_non_image_mime_raises(self) -> None:
        msg = MagicMock()
        msg.photo = None
        msg.document = MagicMock()
        msg.document.mime_type = "application/pdf"
        with pytest.raises(ValueError, match="no image"):
            await download_telegram_image(msg)

    @pytest.mark.asyncio
    async def test_photo_data_matches(self) -> None:
        raw = b"\xff\xd8\xff\xe0" + b"\xab" * 50
        msg = _make_photo_message(photo_data=raw)
        data, _ = await download_telegram_image(msg)
        assert data == raw


# ── Integration: image handler on TelegramTrigger ────────────────────────────


class TestTelegramImageHandler:
    """Tests for _handle_image_message on TelegramTrigger."""

    def _make_trigger(self) -> Any:
        """Create a TelegramTrigger with mocked pipeline."""
        from rai_agent.daemon.telegram import TelegramTrigger

        trigger = TelegramTrigger.__new__(TelegramTrigger)
        trigger._pipeline = []
        trigger._allowed_users = {42}
        return trigger

    def _make_update(
        self,
        *,
        photo_data: bytes = b"\xff\xd8\xff" + b"\x00" * 100,
        caption: str | None = None,
        user_id: int = 42,
        has_document: bool = False,
        doc_mime: str = "image/png",
    ) -> Any:
        update = MagicMock()
        update.effective_user = MagicMock()
        update.effective_user.id = user_id

        msg = _make_photo_message(
            photo_data=photo_data,
            caption=caption,
            has_document=has_document,
            doc_mime=doc_mime,
        )
        update.message = msg
        return update

    @pytest.mark.asyncio
    async def test_photo_with_caption_builds_content_blocks(
        self,
    ) -> None:
        trigger = self._make_trigger()
        captured: list[MessageContext] = []

        async def capture_mw(ctx: Any, next_fn: Any) -> None:
            captured.append(ctx)

        trigger._pipeline = [capture_mw]

        update = self._make_update(caption="¿Qué ves?")
        await trigger._handle_image_message(update, MagicMock())

        assert len(captured) == 1
        ctx = captured[0]
        assert ctx.content_blocks is not None
        assert len(ctx.content_blocks) == 2
        assert ctx.content_blocks[0]["type"] == "image"
        assert ctx.content_blocks[1]["type"] == "text"
        assert ctx.content_blocks[1]["text"] == "¿Qué ves?"
        assert ctx.prompt == "¿Qué ves?"

    @pytest.mark.asyncio
    async def test_photo_without_caption_uses_default(self) -> None:
        trigger = self._make_trigger()
        captured: list[Any] = []

        async def capture_mw(ctx: Any, next_fn: Any) -> None:
            captured.append(ctx)

        trigger._pipeline = [capture_mw]

        update = self._make_update(caption=None)
        await trigger._handle_image_message(update, MagicMock())

        ctx = captured[0]
        assert ctx.content_blocks is not None
        text_block = ctx.content_blocks[-1]
        assert text_block["text"] == DEFAULT_IMAGE_PROMPT

    @pytest.mark.asyncio
    async def test_oversized_image_rejected(self) -> None:
        trigger = self._make_trigger()
        big_data = b"\x00" * (MAX_IMAGE_SIZE + 1)
        update = self._make_update(photo_data=big_data)

        await trigger._handle_image_message(update, MagicMock())
        # Should have replied with error
        update.message.reply_text.assert_awaited()
        call_args = update.message.reply_text.call_args
        assert "muy grande" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_no_user_returns_silently(self) -> None:
        trigger = self._make_trigger()
        update = MagicMock()
        update.effective_user = None
        update.message = MagicMock()
        # Should not raise
        await trigger._handle_image_message(update, MagicMock())
