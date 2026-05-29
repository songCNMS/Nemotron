from __future__ import annotations

import ast
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COOKBOOK = (
    REPO_ROOT
    / "usage-cookbook"
    / "Nemotron-3-Super/lora-text2sql/nemo-automodel/automodel_lora_cookbook.ipynb"
)

EXPECTED_REVISIONS = {
    "xu3kev/BIRD-SQL-data-train": "9122256f9d14752ed80fb9b7d158e21d9f9261aa",
    "meowterspace45/bird-sql-train-with-reasoning": (
        "9e351e0057819f1b0917debb83c8e12f321157a4"
    ),
}


def _notebook_text() -> str:
    return COOKBOOK.read_text(encoding="utf-8")


def _source(cell: dict[str, object]) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def _load_dataset_calls() -> list[ast.Call]:
    notebook = json.loads(_notebook_text())
    calls: list[ast.Call] = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = _source(cell)
        if not any(repo in source for repo in EXPECTED_REVISIONS):
            continue
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "load_dataset":
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


def _repo_name(call: ast.Call) -> str:
    assert call.args
    first_arg = call.args[0]
    assert isinstance(first_arg, ast.Constant)
    assert isinstance(first_arg.value, str)
    return first_arg.value


def test_automodel_bird_text2sql_load_dataset_examples_are_revision_pinned() -> None:
    calls = _load_dataset_calls()

    assert {_repo_name(call) for call in calls} == set(EXPECTED_REVISIONS)
    assert len(calls) == len(EXPECTED_REVISIONS)
    for call in calls:
        repo = _repo_name(call)
        revision = _keyword_string(call, "revision")
        assert _keyword_string(call, "split") == "train"
        assert revision == EXPECTED_REVISIONS[repo]
        assert re.fullmatch(r"[0-9a-f]{40}", revision)


def test_automodel_bird_text2sql_training_sources_have_no_unpinned_calls() -> None:
    text = _notebook_text()

    for repo in EXPECTED_REVISIONS:
        assert f'load_dataset("{repo}", split="train")' not in text


def test_automodel_bird_text2sql_cookbook_context_is_present() -> None:
    text = _notebook_text()

    expected_context = (
        "BIRD-SQL dataset is used for fine-tuning Nemotron-3-super "
        "with NeMo AutoModel",
        "BIRD_PROMPT_TEMPLATE",
        "load_bird_no_reasoning",
        "load_bird_with_reasoning",
    )
    for marker in expected_context:
        assert marker in text
