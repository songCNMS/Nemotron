from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

QUANTIZATION_DOC = REPO_ROOT / "docs/nemotron/super3/quantization.md"
MODEL_OPTIMIZER_SHA = "40a4dd326d8eed63d3153611201341a32bfab329"
MUTABLE_MODEL_OPTIMIZER_PTQ_LINK = (
    "https://github.com/NVIDIA/Model-Optimizer/tree/main/examples/llm_ptq"
)
PINNED_MODEL_OPTIMIZER_PTQ_LINK = (
    "https://github.com/NVIDIA/Model-Optimizer/tree/"
    f"{MODEL_OPTIMIZER_SHA}/examples/llm_ptq"
)


def _read_quantization_doc() -> str:
    return QUANTIZATION_DOC.read_text(encoding="utf-8")


def test_super3_quantization_model_optimizer_ptq_link_is_revision_pinned() -> None:
    text = _read_quantization_doc()

    assert re.fullmatch(r"[0-9a-f]{40}", MODEL_OPTIMIZER_SHA)
    assert PINNED_MODEL_OPTIMIZER_PTQ_LINK in text
    assert MUTABLE_MODEL_OPTIMIZER_PTQ_LINK not in text


def test_super3_quantization_model_optimizer_context_is_preserved() -> None:
    text = _read_quantization_doc()

    expected_context = (
        "# Stage 3: Quantization",
        "post-training quantization (PTQ)",
        "[Model Optimizer]",
        "PTQ with [Megatron-Bridge]",
        "FP8",
        "NVFP4",
    )
    for marker in expected_context:
        assert marker in text
