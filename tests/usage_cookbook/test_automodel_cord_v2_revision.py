from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = (
    REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/automodel/automodel_training_cookbook.md"
)
EXPECTED_REPO = "naver-clova-ix/cord-v2"
EXPECTED_REVISION = "7f0115a4b758a71d6473b8d085751692da2fef98"
UNPINNED_CALL = 'load_dataset("naver-clova-ix/cord-v2")'


def _python_code_blocks(text: str) -> list[str]:
    return re.findall(r"```python\n(.*?)\n```", text, flags=re.DOTALL)


def _cord_v2_load_dataset_calls(text: str) -> list[ast.Call]:
    calls: list[ast.Call] = []
    for block in _python_code_blocks(text):
        tree = ast.parse(block)
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


def test_cord_v2_load_dataset_examples_are_revision_pinned() -> None:
    text = COOKBOOK.read_text(encoding="utf-8")
    calls = _cord_v2_load_dataset_calls(text)

    assert EXPECTED_REPO in text
    assert re.fullmatch(r"[0-9a-f]{40}", EXPECTED_REVISION)
    assert len(calls) == 3
    for call in calls:
        assert _keyword_string(call, "revision") == EXPECTED_REVISION
    assert UNPINNED_CALL not in text


def test_cord_v2_revision_guard_targets_expected_automodel_sections() -> None:
    text = COOKBOOK.read_text(encoding="utf-8")

    expected_sections = (
        "## Step 1 — Explore the CORD-v2 Dataset",
        "### Baseline inference — before fine-tuning",
        "### Full SFT inference",
        "### LoRA PEFT inference",
        "### Evaluation on 5 CORD-v2 Validation Samples",
    )
    for section in expected_sections:
        assert section in text
