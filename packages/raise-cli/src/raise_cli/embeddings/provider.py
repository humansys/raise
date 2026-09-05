"""OnnxEmbeddingProvider — ONNX-based embedding provider (no torch required).

Requires onnxruntime and tokenizers.
Lives in raise_cli.embeddings (foundation tier T5) to satisfy ADR-139 C2:
raise_core must not import onnxruntime (pyproject.toml:348 lint-imports forbidden
contract). Relocated from raise_cli.cartridges (RAISE-16457) — this module has
zero raise_cli-internal dependencies and belongs in the foundation tier alongside
graph, mcp, and config. Mirrors raise_server.embeddings.onnx_provider naming.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from raise_core.cartridges.embedding import (
    PASSAGE_PREFIX,
    QUERY_PREFIX,
    EmbeddingProvider,
)

_BATCH_SIZE = 32
_MAX_LEN = 512


class ModelNotConfiguredError(RuntimeError):
    """Raised when ONNX is available but no model location was configured."""


class OnnxEmbeddingProvider:
    """Embedding provider using ONNX runtime — no torch required.

    Designed for frozen PyInstaller binaries. Inject _session and _tokenizer
    to test without downloading the real model.
    Both seams must be provided together or neither (ValueError otherwise).
    """

    def __init__(
        self,
        model_dir: Path | None = None,
        *,
        query_prefix: str = QUERY_PREFIX,
        passage_prefix: str = PASSAGE_PREFIX,
        _session: object | None = None,
        _tokenizer: object | None = None,
    ) -> None:
        if (_session is None) != (_tokenizer is None):
            raise ValueError("Provide both _session and _tokenizer, or neither")
        if _session is not None and _tokenizer is not None:
            self._session = _session
            self._tokenizer = _tokenizer
        else:
            if model_dir is None:
                raise ModelNotConfiguredError(
                    "model_dir is required when _session/_tokenizer are not injected"
                )

            import onnxruntime as ort  # type: ignore[import-not-found]
            from tokenizers import Tokenizer  # type: ignore[import-not-found]

            model_quant = model_dir / "model_quant.onnx"
            if not model_quant.exists():
                raise RuntimeError(
                    f"ONNX model not found at {model_quant}. "
                    "Run scripts/export_onnx_model.py before building the binary."
                )
            opts = ort.SessionOptions()
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self._session = ort.InferenceSession(str(model_quant), sess_options=opts)
            tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
            tokenizer.enable_truncation(max_length=_MAX_LEN)
            self._tokenizer = tokenizer

        self._query_prefix = query_prefix
        self._passage_prefix = passage_prefix

    def _encode_batch(self, texts: list[str], prefix: str) -> list[list[float]]:
        import numpy as np

        prefixed = [prefix + t for t in texts]
        encodings = self._tokenizer.encode_batch(prefixed)  # type: ignore[attr-defined]

        max_len = max(len(e.ids) for e in encodings)
        batch = len(encodings)
        input_ids = np.zeros((batch, max_len), dtype=np.int64)
        attention_mask = np.zeros((batch, max_len), dtype=np.int64)

        for i, enc in enumerate(encodings):
            n = len(enc.ids)
            input_ids[i, :n] = enc.ids
            attention_mask[i, :n] = enc.attention_mask

        input_names = {inp.name for inp in self._session.get_inputs()}  # type: ignore[attr-defined]
        feed: dict[str, Any] = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        if "token_type_ids" in input_names:
            feed["token_type_ids"] = np.zeros((batch, max_len), dtype=np.int64)

        outputs = self._session.run(None, feed)  # type: ignore[attr-defined]
        token_emb = np.array(outputs[0], dtype=np.float32)

        mask = attention_mask[:, :, np.newaxis].astype(np.float32)
        pooled = (token_emb * mask).sum(axis=1) / mask.sum(axis=1).clip(min=1e-9)
        norms = np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
        return (pooled / norms).tolist()

    def _encode(self, texts: list[str], prefix: str) -> list[list[float]]:
        if not texts:
            return []
        results: list[list[float]] = []
        for i in range(0, len(texts), _BATCH_SIZE):
            results.extend(self._encode_batch(texts[i : i + _BATCH_SIZE], prefix))
        return results

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Encode documents/passages (ingest side)."""
        return self._encode(texts, self._passage_prefix)

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        """Encode queries (retrieval side)."""
        return self._encode(texts, self._query_prefix)


def get_default_provider(model_dir: Path | None = None) -> EmbeddingProvider:
    """Return OnnxEmbeddingProvider for the current environment.

    Resolution order for model_dir (first match wins):
    1. Explicit ``model_dir`` argument.
    2. ``sys._MEIPASS/models/multilingual-e5-base`` in frozen PyInstaller binaries.
    3. ``$RAISE_ONNX_MODEL_DIR`` environment variable (CI / dev override).
    """
    if model_dir is None:
        if getattr(sys, "frozen", False):
            model_dir = (
                Path(getattr(sys, "_MEIPASS", "")) / "models" / "multilingual-e5-base"
            )
        elif env_dir := os.environ.get("RAISE_ONNX_MODEL_DIR"):
            model_dir = Path(env_dir)
    return OnnxEmbeddingProvider(model_dir=model_dir)
