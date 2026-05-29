from __future__ import annotations

import ast
import re
from pathlib import Path

from nemotron.recipes.omni3.stage0_sft.data_prep import (
    VALOR32K_QA_ZIP_URL,
    Omni3SFTDataPrepConfig,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PREP = REPO_ROOT / "src/nemotron/recipes/omni3/stage0_sft/data_prep.py"
EXPECTED_REVISION = "a1eeb58e16fbe84f43a3886fd72fe61fd208b7b2"
EXPECTED_URL = (
    "https://github.com/inesriahi/valor32k-avqa-2/raw/"
    f"{EXPECTED_REVISION}/data.zip"
)
FLOATING_REF_FRAGMENTS = (
    "refs/heads/main",
    "/main/",
    "refs/heads/master",
    "/master/",
)


def _module_tree() -> ast.Module:
    return ast.parse(DATA_PREP.read_text(encoding="utf-8"))


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


def _has_manifest_qa_zip_url_entry(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values, strict=True):
            if not (isinstance(key, ast.Constant) and key.value == "qa_zip_url"):
                continue
            if isinstance(value, ast.Attribute) and value.attr == "qa_zip_url":
                return True
    return False


def test_valor32k_qa_zip_default_is_pinned_to_exact_revision() -> None:
    source = DATA_PREP.read_text(encoding="utf-8")
    tree = _module_tree()

    revision = _module_string_constant(tree, "VALOR32K_QA_ZIP_REVISION")
    assert revision == EXPECTED_REVISION
    assert re.fullmatch(r"[0-9a-f]{40}", revision)
    assert VALOR32K_QA_ZIP_URL == EXPECTED_URL
    for fragment in FLOATING_REF_FRAGMENTS:
        assert fragment not in VALOR32K_QA_ZIP_URL
    assert "refs/heads/main/data.zip" not in source


def test_valor32k_config_uses_pinned_qa_zip_default_without_download() -> None:
    assert Omni3SFTDataPrepConfig().qa_zip_url == EXPECTED_URL


def test_valor32k_lineage_records_effective_qa_zip_url() -> None:
    source = DATA_PREP.read_text(encoding="utf-8")
    tree = _module_tree()

    assert "source_uri_parts = [cfg.qa_zip_url]" in source
    assert _has_manifest_qa_zip_url_entry(tree)
