from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_SCRIPT = REPO_ROOT / "src/nemotron/recipes/data/sdg/long-document/01-seed-dataset-preparation.py"
SEED_CONFIG = REPO_ROOT / "src/nemotron/recipes/data/sdg/long-document/config/01-seed.yaml"
EXPECTED_REPO = "HuggingFaceFW/finepdfs"
EXPECTED_REVISION = "220bac3acbf07789502c621d2d33952f51ac7f86"


def _module_tree() -> ast.Module:
    return ast.parse(SEED_SCRIPT.read_text(encoding="utf-8"))


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


def _field_default_name(tree: ast.Module, field_name: str) -> str:
    for node in ast.walk(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name) or node.target.id != field_name:
            continue
        assert isinstance(node.value, ast.Call)
        assert isinstance(node.value.func, ast.Name)
        assert node.value.func.id == "Field"
        for keyword in node.value.keywords:
            if keyword.arg != "default":
                continue
            assert isinstance(keyword.value, ast.Name)
            return keyword.value.id
    raise AssertionError(f"missing SeedConfig field {field_name}")


def _load_dataset_call(tree: ast.Module) -> ast.Call:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "load_dataset":
            return node
    raise AssertionError("missing load_dataset call")


def _keyword_value(call: ast.Call, name: str) -> ast.expr:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    raise AssertionError(f"missing load_dataset keyword {name}")


def test_finepdfs_seed_source_defaults_to_pinned_revision() -> None:
    tree = _module_tree()

    assert _module_string_constant(tree, "FINEPDFS_REPO") == EXPECTED_REPO
    revision = _module_string_constant(tree, "FINEPDFS_REVISION")
    assert revision == EXPECTED_REVISION
    assert re.fullmatch(r"[0-9a-f]{40}", revision)
    assert _field_default_name(tree, "finepdfs_revision") == "FINEPDFS_REVISION"


def test_finepdfs_load_dataset_threads_revision_from_config() -> None:
    call = _load_dataset_call(_module_tree())

    assert isinstance(call.args[0], ast.Name)
    assert call.args[0].id == "FINEPDFS_REPO"

    name_value = _keyword_value(call, "name")
    assert isinstance(name_value, ast.Attribute)
    assert isinstance(name_value.value, ast.Name)
    assert name_value.value.id == "cfg"
    assert name_value.attr == "subset"

    revision_value = _keyword_value(call, "revision")
    assert isinstance(revision_value, ast.Attribute)
    assert isinstance(revision_value.value, ast.Name)
    assert revision_value.value.id == "cfg"
    assert revision_value.attr == "finepdfs_revision"


def test_finepdfs_default_config_exposes_same_revision_pin() -> None:
    config = yaml.safe_load(SEED_CONFIG.read_text(encoding="utf-8"))

    assert config["finepdfs_revision"] == EXPECTED_REVISION
    assert re.fullmatch(r"[0-9a-f]{40}", config["finepdfs_revision"])
