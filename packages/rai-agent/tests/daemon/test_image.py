"""Tests for provider-agnostic image processing (S7.5)."""

from __future__ import annotations

import base64

import pytest

from rai_agent.daemon.image import (
    DEFAULT_IMAGE_PROMPT,
    MAX_IMAGE_SIZE,
    SUPPORTED_MIMES,
    build_image_content_blocks,
    validate_image,
)


class TestValidateImage:
    """Unit tests for validate_image()."""

    def test_valid_jpeg(self) -> None:
        data = b"\xff\xd8\xff" + b"\x00" * 100
        validate_image(data, "image/jpeg")  # should not raise

    def test_valid_png(self) -> None:
        data = b"\x89PNG" + b"\x00" * 100
        validate_image(data, "image/png")

    def test_valid_gif(self) -> None:
        data = b"GIF89a" + b"\x00" * 100
        validate_image(data, "image/gif")

    def test_valid_webp(self) -> None:
        data = b"RIFF" + b"\x00" * 100
        validate_image(data, "image/webp")

    def test_unsupported_mime_raises(self) -> None:
        with pytest.raises(ValueError, match="no está soportado"):
            validate_image(b"\x00" * 10, "image/tiff")

    def test_too_large_raises(self) -> None:
        big_data = b"\x00" * (MAX_IMAGE_SIZE + 1)
        with pytest.raises(ValueError, match="muy grande"):
            validate_image(big_data, "image/jpeg")

    def test_exactly_max_size_ok(self) -> None:
        data = b"\x00" * MAX_IMAGE_SIZE
        validate_image(data, "image/jpeg")  # should not raise


class TestBuildImageContentBlocks:
    """Unit tests for build_image_content_blocks()."""

    def test_single_image_with_caption(self) -> None:
        data = b"\xff\xd8\xff" + b"\x00" * 10
        blocks = build_image_content_blocks(
            images=[(data, "image/jpeg")],
            caption="¿Qué patrones ves?",
        )
        assert len(blocks) == 2
        # Image block first (D4/BASE-055)
        assert blocks[0]["type"] == "image"
        assert blocks[0]["source"]["type"] == "base64"
        assert blocks[0]["source"]["media_type"] == "image/jpeg"
        expected = base64.standard_b64encode(data).decode("utf-8")
        assert blocks[0]["source"]["data"] == expected
        # Text block second
        assert blocks[1]["type"] == "text"
        assert blocks[1]["text"] == "¿Qué patrones ves?"

    def test_single_image_no_caption_uses_default(self) -> None:
        data = b"\xff\xd8\xff" + b"\x00" * 10
        blocks = build_image_content_blocks(
            images=[(data, "image/jpeg")],
            caption=None,
        )
        assert len(blocks) == 2
        assert blocks[1]["type"] == "text"
        assert blocks[1]["text"] == DEFAULT_IMAGE_PROMPT

    def test_single_image_empty_caption_uses_default(self) -> None:
        data = b"\xff\xd8\xff" + b"\x00" * 10
        blocks = build_image_content_blocks(
            images=[(data, "image/jpeg")],
            caption="",
        )
        assert len(blocks) == 2
        assert blocks[1]["text"] == DEFAULT_IMAGE_PROMPT

    def test_multiple_images(self) -> None:
        img1 = b"\xff\xd8\xff" + b"\x00" * 10
        img2 = b"\x89PNG" + b"\x00" * 10
        blocks = build_image_content_blocks(
            images=[(img1, "image/jpeg"), (img2, "image/png")],
            caption="Compare these.",
        )
        # 2 image blocks + 1 text block
        assert len(blocks) == 3
        assert blocks[0]["type"] == "image"
        assert blocks[0]["source"]["media_type"] == "image/jpeg"
        assert blocks[1]["type"] == "image"
        assert blocks[1]["source"]["media_type"] == "image/png"
        assert blocks[2]["type"] == "text"
        assert blocks[2]["text"] == "Compare these."

    def test_validates_before_building(self) -> None:
        big_data = b"\x00" * (MAX_IMAGE_SIZE + 1)
        with pytest.raises(ValueError, match="muy grande"):
            build_image_content_blocks(
                images=[(big_data, "image/jpeg")],
                caption="test",
            )

    def test_unsupported_mime_in_build(self) -> None:
        with pytest.raises(ValueError, match="no está soportado"):
            build_image_content_blocks(
                images=[(b"\x00" * 10, "image/tiff")],
                caption="test",
            )


class TestConstants:
    """Verify constants are correctly defined."""

    def test_supported_mimes(self) -> None:
        expected = frozenset(
            {
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
            }
        )
        assert expected == SUPPORTED_MIMES

    def test_max_image_size(self) -> None:
        assert MAX_IMAGE_SIZE == 5 * 1024 * 1024

    def test_default_prompt(self) -> None:
        assert isinstance(DEFAULT_IMAGE_PROMPT, str)
        assert len(DEFAULT_IMAGE_PROMPT) > 0
