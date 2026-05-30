from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_REVISION = "3d75a20d56ba4931457ca91d0fd8fdfe79b37c21"
README = REPO_ROOT / "usage-cookbook/Nemotron-3-Super/lora-text2sql/README.md"
NOTEBOOK = (
    REPO_ROOT
    / "usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/mbridge_lora_cookbook.ipynb"
)

PINNED_LINKS = (
    "https://github.com/NVIDIA-NeMo/Nemotron/blob/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge/README.md",
    "https://github.com/NVIDIA-NeMo/Nemotron/blob/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-automodel/README.md",
    "https://github.com/NVIDIA-NeMo/Nemotron/tree/"
    f"{EXPECTED_REVISION}/usage-cookbook/Nemotron-3-Super/vllm_cookbook.ipynb",
)

MUTABLE_SCOPED_LINK_RE = re.compile(
    r"https://github\.com/NVIDIA-NeMo/Nemotron/(?:blob|tree)/main/"
    r"usage-cookbook/Nemotron-3-Super/"
    r"(?:lora-text2sql/(?:nemo-megatron-bridge|nemo-automodel)/README\.md|vllm_cookbook\.ipynb)"
)
PINNED_SCOPED_LINK_RE = re.compile(
    rf"https://github\.com/NVIDIA-NeMo/Nemotron/(?:blob|tree)/{EXPECTED_REVISION}/"
    r"usage-cookbook/Nemotron-3-Super/"
    r"(?:lora-text2sql/(?:nemo-megatron-bridge|nemo-automodel)/README\.md|vllm_cookbook\.ipynb)"
)


def _source(cell: dict[str, object]) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def _notebook() -> dict[str, object]:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _combined_source() -> str:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    notebook_source = "\n".join(
        _source(cell) for cell in cells if isinstance(cell, dict)
    )
    return README.read_text(encoding="utf-8") + "\n" + notebook_source


def test_super3_lora_text2sql_self_repo_links_are_revision_pinned() -> None:
    combined = _combined_source()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    for pinned_link in PINNED_LINKS:
        assert pinned_link in combined

    assert not MUTABLE_SCOPED_LINK_RE.findall(combined)
    assert len(PINNED_SCOPED_LINK_RE.findall(combined)) == len(PINNED_LINKS)


def test_super3_lora_text2sql_doc_link_context_is_preserved() -> None:
    combined = _combined_source()

    expected_context = (
        "Nemotron-3-Super Text2SQL Fine-tuning",
        "nemo-megatron-bridge",
        "nemo-automodel",
        "NeMo Megatron-Bridge",
        "NeMo AutoModel",
        "Nemotron Super v3 Text2SQL LoRA Fine-Tuning using Megatron Bridge",
        "Step 6: Deploying the Trained Model for Inference",
        "usage-cookbook/Nemotron-3-Super/vllm_cookbook.ipynb",
    )
    for marker in expected_context:
        assert marker in combined


def test_super3_lora_text2sql_notebook_doc_link_cell_is_clear() -> None:
    notebook = _notebook()
    cells = notebook["cells"]
    assert isinstance(cells, list)
    notebook_link = PINNED_LINKS[2]
    matching_cells = [
        cell
        for cell in cells
        if isinstance(cell, dict) and notebook_link in _source(cell)
    ]

    assert len(matching_cells) == 1
    cell = matching_cells[0]
    assert cell["cell_type"] == "markdown"
    assert cell.get("execution_count") is None
    assert cell.get("outputs", []) == []
