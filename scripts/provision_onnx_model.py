"""Provisiona el model dir canonico de la variante `server-int8` (ADR-139 C5).

Idempotente: si el directorio ya esta completo NO toca la red. Es el unico punto
de provision de esta variante -- lo usan el job de CI `build:onnx-model` (que lo
publica como artifact) y el `RUN` del target `server` del Dockerfile (que asi cae
al download solo cuando nadie lo stageo).

INV-1 (epic e15852 design C-1): el modelo Y su tokenizer deben estar en la imagen
al terminar el build; cero red en el arranque del contenedor. NO citar como
ADR-139 C1 -- esa constraint es "Protocolo como unica interfaz publica".

ADR-139 C2: este archivo NO importa onnxruntime.

Uso:
    python scripts/provision_onnx_model.py --dest /app/models/multilingual-e5-base-int8
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

WEIGHTS_REPO = "Xenova/multilingual-e5-base"
WEIGHTS_HF_FILE = "onnx/model_int8.onnx"
WEIGHTS_NAME = "model.onnx"  # C5: nombre local de la variante server-int8
TOKENIZER_REPO = "intfloat/multilingual-e5-base"
_MIN_WEIGHTS_BYTES = (
    200_000_000  # el INT8 real pesa ~266 MB; atrapa 404-HTML y truncados
)


def is_complete(dest: Path) -> bool:
    """True si el model dir ya satisface C5 (pesos plausibles + tokenizer round-trippable)."""
    weights = dest / WEIGHTS_NAME
    if not weights.is_file() or weights.stat().st_size < _MIN_WEIGHTS_BYTES:
        return False
    return all(
        (dest / f).is_file() for f in ("tokenizer.json", "tokenizer_config.json")
    )


def verify(dest: Path) -> None:
    """Falla RUIDOSAMENTE en build time si el artefacto esta incompleto (D3)."""
    from transformers import AutoTokenizer  # lazy: no es dep de los tests unitarios

    weights = dest / WEIGHTS_NAME
    size = weights.stat().st_size if weights.is_file() else 0
    if size < _MIN_WEIGHTS_BYTES:
        raise SystemExit(
            f"ONNX invalido en {dest}: {WEIGHTS_NAME} pesa {size} B "
            f"(< {_MIN_WEIGHTS_BYTES}). Artefacto truncado o 404-HTML."
        )
    AutoTokenizer.from_pretrained(str(dest))  # path LOCAL, nunca repo-id (INV-1)


def provision(dest: Path) -> str:
    """Devuelve 'staged' si no hubo red, 'downloaded' si hubo que bajarlo."""
    dest.mkdir(parents=True, exist_ok=True)
    if is_complete(dest):
        print(f"ONNX model dir ya staged en {dest} -- sin descarga (ADR-139 C5)")
        verify(dest)
        return "staged"

    print(
        f"ONNX model dir incompleto en {dest} -- fallback: descargando de HuggingFace"
    )
    from huggingface_hub import hf_hub_download
    from transformers import AutoTokenizer

    src = hf_hub_download(repo_id=WEIGHTS_REPO, filename=WEIGHTS_HF_FILE)
    shutil.copy(src, dest / WEIGHTS_NAME)
    AutoTokenizer.from_pretrained(TOKENIZER_REPO).save_pretrained(str(dest))
    shutil.rmtree(Path.home() / ".cache" / "huggingface", ignore_errors=True)
    verify(dest)
    return "downloaded"


def main() -> None:
    """CLI entrypoint: `python scripts/provision_onnx_model.py --dest <dir>`."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True)
    print(provision(parser.parse_args().dest))


if __name__ == "__main__":
    main()
