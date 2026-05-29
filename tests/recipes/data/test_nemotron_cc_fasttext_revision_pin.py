from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
QUALITY_CLASSIFICATION = (
    REPO_ROOT
    / "src/nemotron/recipes/data/curation/nemotron-cc/step_3-quality_classification.py"
)
EXPECTED_REPO = "mlfoundations/fasttext-oh-eli5"
EXPECTED_FILENAME = "openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin"
EXPECTED_REVISION = "cd8b714a90f2dbcd3b02cf5fc972e5d7c7f4f107"


def _module_tree() -> ast.Module:
    return ast.parse(QUALITY_CLASSIFICATION.read_text(encoding="utf-8"))


def _module_constant(tree: ast.Module, name: str) -> str:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        assert isinstance(node.value, ast.Constant)
        assert isinstance(node.value.value, str)
        return node.value.value
    raise AssertionError(f"missing module constant {name}")


def _fasttext_download_call(tree: ast.Module) -> ast.Call:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "hf_hub_download":
            return node
    raise AssertionError("missing hf_hub_download call")


def _keyword_name(call: ast.Call, keyword: str) -> str:
    for node in call.keywords:
        if node.arg != keyword:
            continue
        assert isinstance(node.value, ast.Name)
        return node.value.id
    raise AssertionError(f"missing hf_hub_download keyword {keyword}")


def test_nemotron_cc_fasttext_hf_download_pins_revision() -> None:
    tree = _module_tree()

    assert _module_constant(tree, "FASTTEXT_HQ_MODEL_REPO") == EXPECTED_REPO
    assert _module_constant(tree, "FASTTEXT_HQ_MODEL_FILENAME") == EXPECTED_FILENAME
    revision = _module_constant(tree, "FASTTEXT_HQ_MODEL_REVISION")
    assert revision == EXPECTED_REVISION
    assert re.fullmatch(r"[0-9a-f]{40}", revision)

    download_call = _fasttext_download_call(tree)
    assert _keyword_name(download_call, "repo_id") == "FASTTEXT_HQ_MODEL_REPO"
    assert _keyword_name(download_call, "filename") == "FASTTEXT_HQ_MODEL_FILENAME"
    assert _keyword_name(download_call, "revision") == "FASTTEXT_HQ_MODEL_REVISION"
