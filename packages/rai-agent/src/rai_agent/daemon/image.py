"""Provider-agnostic image processing for multimodal content blocks.

Converts raw image bytes into Claude-compatible content blocks.
Provider-specific download logic lives in each provider module
(e.g., telegram.py). This module handles: validation, base64
encoding, and content block construction.

Design: S7.5 (RAI-37), Decisions D3/D5.
"""

from __future__ import annotations

import base64
from typing import Any

SUPPORTED_MIMES: frozenset[str] = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }
)
"""MIME types supported by Claude's vision API."""

MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5 MB
"""Maximum image size accepted by Claude API."""

DEFAULT_IMAGE_PROMPT: str = "Describe this image."
"""Default text prompt when no caption is provided."""


def validate_image(data: bytes, mime_type: str) -> None:
    """Validate image size and MIME type.

    Raises:
        ValueError: If image exceeds size limit or MIME type is unsupported.
    """
    if mime_type not in SUPPORTED_MIMES:
        supported = ", ".join(sorted(SUPPORTED_MIMES))
        msg = f"El formato {mime_type} no está soportado. Formatos válidos: {supported}"
        raise ValueError(msg)
    if len(data) > MAX_IMAGE_SIZE:
        size_mb = len(data) / (1024 * 1024)
        max_mb = MAX_IMAGE_SIZE // (1024 * 1024)
        msg = (
            f"La imagen es muy grande ({size_mb:.1f} MB). "
            f"Máximo: {max_mb} MB. "
            "Intenta enviarla como foto en vez de archivo."
        )
        raise ValueError(msg)


def build_image_content_blocks(
    images: list[tuple[bytes, str]],
    caption: str | None = None,
) -> list[dict[str, Any]]:
    """Build Claude-compatible multimodal content blocks.

    Images are placed before text (BASE-055: U-shaped attention).

    Args:
        images: List of (raw_bytes, mime_type) tuples.
        caption: User's text question. Falls back to DEFAULT_IMAGE_PROMPT.

    Returns:
        List of content block dicts ready for Claude Messages API.

    Raises:
        ValueError: If any image fails validation.
    """
    blocks: list[dict[str, Any]] = []

    for data, mime_type in images:
        validate_image(data, mime_type)
        encoded = base64.standard_b64encode(data).decode("utf-8")
        blocks.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": encoded,
                },
            }
        )

    text = caption.strip() if caption else ""
    if not text:
        text = DEFAULT_IMAGE_PROMPT

    blocks.append({"type": "text", "text": text})

    return blocks
