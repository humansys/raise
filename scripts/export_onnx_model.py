"""Export intfloat/multilingual-e5-base to quantized ONNX for the rai binary.

Usage (run from repo root):
    pip install optimum[exporters] onnx onnxruntime
    python scripts/export_onnx_model.py [--output-dir packages/raise-cli/models/multilingual-e5-base]

Produces:
    <output-dir>/model_quant.onnx   — int8-quantized ONNX model (~90MB)
    <output-dir>/tokenizer.json     — fast tokenizer for runtime inference

This script runs once (offline or in CI) before pyinstaller. The output is
bundled into the binary via the datas entry in raise-cli.spec (RAISE-15800).
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MODEL_ID = "intfloat/multilingual-e5-base"


def export(output_dir: Path) -> None:
    from optimum.exporters.onnx import main_export  # type: ignore[import-not-found]
    from onnxruntime.quantization import quantize_dynamic, QuantType  # type: ignore[import-not-found]
    from transformers import AutoTokenizer  # type: ignore[import-not-found]

    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        print(f"Exporting {MODEL_ID} to ONNX (fp32) …")
        main_export(
            model_name_or_path=MODEL_ID,
            output=tmp_path,
            task="feature-extraction",
        )

        fp32_model = tmp_path / "model.onnx"
        quant_model = output_dir / "model_quant.onnx"

        print("Quantizing to int8 …")
        quantize_dynamic(
            model_input=fp32_model,
            model_output=quant_model,
            weight_type=QuantType.QInt8,
        )

        print("Saving tokenizer …")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        tokenizer.save_pretrained(str(tmp_path / "tok"))
        shutil.copy(tmp_path / "tok" / "tokenizer.json", output_dir / "tokenizer.json")

    size_mb = quant_model.stat().st_size / 1024 / 1024
    print(f"Done. model_quant.onnx = {size_mb:.1f} MB → {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("packages/raise-cli/models/multilingual-e5-base"),
        help="Directory to write model_quant.onnx and tokenizer.json",
    )
    args = parser.parse_args()
    export(args.output_dir)


if __name__ == "__main__":
    main()
