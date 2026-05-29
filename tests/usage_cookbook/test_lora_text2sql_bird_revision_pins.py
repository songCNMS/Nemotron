from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEXT2SQL_DIR = (
    REPO_ROOT / "usage-cookbook/Nemotron-3-Super/lora-text2sql/nemo-megatron-bridge"
)

LOADERS = {
    TEXT2SQL_DIR / "dataset_bird.py": {
        "repo_constant": "BIRD_SQL_DATASET_REPO",
        "revision_constant": "BIRD_SQL_DATASET_REVISION",
        "repo": "xu3kev/BIRD-SQL-data-train",
        "revision": "9122256f9d14752ed80fb9b7d158e21d9f9261aa",
    },
    TEXT2SQL_DIR / "dataset_bird_reasoning.py": {
        "repo_constant": "BIRD_REASONING_DATASET_REPO",
        "revision_constant": "BIRD_REASONING_DATASET_REVISION",
        "repo": "meowterspace45/bird-sql-train-with-reasoning",
        "revision": "9e351e0057819f1b0917debb83c8e12f321157a4",
    },
}


def _module_tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _module_string_constant(tree: ast.Module, name: str) -> str:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        assert isinstance(node.value, ast.Constant)
        assert isinstance(node.value.value, str)
        return node.value.value
    raise AssertionError(f"missing module constant {name}")


def _load_dataset_calls(tree: ast.Module) -> list[ast.Call]:
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "load_dataset":
            calls.append(node)
    return calls


def _keyword(call: ast.Call, name: str) -> ast.expr:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    raise AssertionError(f"missing load_dataset keyword {name}")


def _assert_name(value: ast.expr, name: str) -> None:
    assert isinstance(value, ast.Name)
    assert value.id == name


def test_bird_text2sql_dataset_loaders_define_expected_revision_pins() -> None:
    for path, expected in LOADERS.items():
        tree = _module_tree(path)

        assert _module_string_constant(tree, expected["repo_constant"]) == expected["repo"]
        revision = _module_string_constant(tree, expected["revision_constant"])
        assert revision == expected["revision"]
        assert re.fullmatch(r"[0-9a-f]{40}", revision)


def test_bird_text2sql_load_dataset_calls_use_matching_revision_constants() -> None:
    for path, expected in LOADERS.items():
        calls = _load_dataset_calls(_module_tree(path))
        assert len(calls) == 1
        call = calls[0]

        assert len(call.args) == 1
        _assert_name(call.args[0], expected["repo_constant"])

        split = _keyword(call, "split")
        assert isinstance(split, ast.Constant)
        assert split.value == "train"

        _assert_name(_keyword(call, "revision"), expected["revision_constant"])


def test_bird_text2sql_load_dataset_calls_have_no_unpinned_training_sources() -> None:
    for path in LOADERS:
        for call in _load_dataset_calls(_module_tree(path)):
            has_train_split = any(
                keyword.arg == "split"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value == "train"
                for keyword in call.keywords
            )
            if has_train_split:
                assert any(keyword.arg == "revision" for keyword in call.keywords)
