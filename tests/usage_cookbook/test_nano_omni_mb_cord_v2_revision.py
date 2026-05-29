from __future__ import annotations

import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = (
    REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/Megatron-bridge/mbridge_lora_cord_v2_cookbook.ipynb"
)

EXPECTED_REPO = "naver-clova-ix/cord-v2"
EXPECTED_REVISION = "7f0115a4b758a71d6473b8d085751692da2fef98"
UNPINNED_CALL = 'load_dataset("naver-clova-ix/cord-v2", split="train")'


def _notebook_text() -> str:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )


def _code_cells() -> list[str]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
        and "load_dataset" in "".join(cell.get("source", []))
        and EXPECTED_REPO in "".join(cell.get("source", []))
    ]


def _cord_v2_load_dataset_calls() -> list[ast.Call]:
    calls: list[ast.Call] = []
    for source in _code_cells():
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != "load_dataset":
                continue
            if not node.args or not isinstance(node.args[0], ast.Constant):
                continue
            if node.args[0].value == EXPECTED_REPO:
                calls.append(node)
    return calls


def _keyword_string(call: ast.Call, name: str) -> str:
    for keyword in call.keywords:
        if keyword.arg != name:
            continue
        assert isinstance(keyword.value, ast.Constant)
        assert isinstance(keyword.value.value, str)
        return keyword.value.value
    raise AssertionError(f"missing keyword {name}")


def test_nano_omni_megatron_bridge_cord_v2_load_dataset_is_revision_pinned() -> None:
    calls = _cord_v2_load_dataset_calls()

    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert len(calls) == 1
    call = calls[0]
    assert _keyword_string(call, "split") == "train"
    assert _keyword_string(call, "revision") == EXPECTED_REVISION


def test_nano_omni_megatron_bridge_cord_v2_has_no_unpinned_train_example() -> None:
    text = _notebook_text()

    assert UNPINNED_CALL not in text
    assert EXPECTED_REPO in text
    assert EXPECTED_REVISION in text


def test_nano_omni_megatron_bridge_cord_v2_sections_are_preserved() -> None:
    text = _notebook_text()

    expected_sections = (
        "# Nemotron-3 Omni LoRA Fine-Tuning on CORD-v2 with Megatron Bridge",
        "## Step 1 — Model Conversion (HuggingFace → Megatron)",
        "## Step 2 — Dataset",
        "## Step 4 — Launch Training",
        "## Step 7 — Merge LoRA into Base Megatron Checkpoint",
    )
    for section in expected_sections:
        assert section in text
