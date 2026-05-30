"""Static checks for Embed recipe upstream documentation/source link pins."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

EXPORT_RECIPE = REPO_ROOT / "src/nemotron/recipes/embed/stage4_export/export.py"
BIENCODER_CONFIG = REPO_ROOT / "src/nemotron/recipes/embed/stage2_finetune/biencoder_base.yaml"

EXPORT_DEPLOY_REVISION = "e025bcd888d92ae226cccd4556f0a790bf714ec7"
AUTOMODEL_REVISION = "7dc827ca9108b2e45eb3beaba8a3cd148bfc658f"

MUTABLE_EXPORT_DEPLOY_LINK = (
    "https://github.com/NVIDIA-NeMo/Export-Deploy/blob/main/"
    "tutorials/onnx_tensorrt/embedding/llama_embedding.ipynb"
)
PINNED_EXPORT_DEPLOY_LINK = (
    "https://github.com/NVIDIA-NeMo/Export-Deploy/blob/"
    f"{EXPORT_DEPLOY_REVISION}/tutorials/onnx_tensorrt/embedding/llama_embedding.ipynb"
)

MUTABLE_AUTOMODEL_LINK = (
    "https://github.com/NVIDIA-NeMo/Automodel/blob/main/"
    "examples/biencoder/llama3_2_1b_biencoder.yaml"
)
PINNED_AUTOMODEL_LINK = (
    "https://github.com/NVIDIA-NeMo/Automodel/blob/"
    f"{AUTOMODEL_REVISION}/examples/biencoder/llama3_2_1b_biencoder.yaml"
)


def test_embed_export_deploy_tutorial_link_is_revision_pinned() -> None:
    text = EXPORT_RECIPE.read_text(encoding="utf-8")

    assert MUTABLE_EXPORT_DEPLOY_LINK not in text
    assert text.count(PINNED_EXPORT_DEPLOY_LINK) == 1
    assert "Based on the NeMo Export-Deploy tutorial:" in text
    assert "Export script for embedding models to ONNX and TensorRT." in text


def test_embed_biencoder_source_link_is_revision_pinned() -> None:
    text = BIENCODER_CONFIG.read_text(encoding="utf-8")

    assert MUTABLE_AUTOMODEL_LINK not in text
    assert text.count(PINNED_AUTOMODEL_LINK) == 1
    assert "# Base configuration for biencoder fine-tuning using nemo-automodel" in text
    assert "# Source: " + PINNED_AUTOMODEL_LINK in text
