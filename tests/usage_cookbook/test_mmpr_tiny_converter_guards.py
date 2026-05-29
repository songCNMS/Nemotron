from __future__ import annotations

import ast
import importlib.util
import re
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONVERTER = (
    REPO_ROOT
    / "usage-cookbook/Nemotron-3-Nano-Omni/grpo_nemo_gym/convert_mmpr_tiny_to_gym_jsonl.py"
)
EXPECTED_REPO = "OpenGVLab/MMPR-Tiny"
EXPECTED_REVISION = "eb493212c9614b69ca49cd6e66719413c514459b"


def _load_converter_module():
    spec = importlib.util.spec_from_file_location("mmpr_tiny_converter", CONVERTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _module_tree() -> ast.Module:
    return ast.parse(CONVERTER.read_text(encoding="utf-8"))


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


def _hf_hub_download_calls(tree: ast.Module) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "hf_hub_download"
    ]


def _keyword_value(call: ast.Call, name: str) -> ast.expr:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    raise AssertionError(f"missing keyword {name}")


def _write_zip(path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)


def test_mmpr_tiny_downloads_are_revision_pinned_and_safe_zip_static() -> None:
    source = CONVERTER.read_text(encoding="utf-8")
    tree = _module_tree()

    assert ".extractall(" not in source
    assert "safe_extract_zip(" in source
    assert _module_string_constant(tree, "MMPR_TINY_REPO") == EXPECTED_REPO
    revision = _module_string_constant(tree, "MMPR_TINY_REVISION")
    assert revision == EXPECTED_REVISION
    assert re.fullmatch(r"[0-9a-f]{40}", revision)

    calls = _hf_hub_download_calls(tree)
    assert len(calls) == 2
    filenames = []
    for call in calls:
        assert isinstance(call.args[0], ast.Name)
        assert call.args[0].id == "MMPR_TINY_REPO"
        assert isinstance(call.args[1], ast.Name)
        filenames.append(call.args[1].id)

        repo_type = _keyword_value(call, "repo_type")
        assert isinstance(repo_type, ast.Constant)
        assert repo_type.value == "dataset"

        revision_arg = _keyword_value(call, "revision")
        assert isinstance(revision_arg, ast.Name)
        assert revision_arg.id == "MMPR_TINY_REVISION"

    assert filenames == ["MMPR_TINY_IMAGES_FILENAME", "MMPR_TINY_PARQUET_FILENAME"]


def test_mmpr_tiny_converter_rejects_zip_traversal_before_ready_marker(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    converter = _load_converter_module()
    zip_path = tmp_path / "images.zip"
    parquet_path = tmp_path / "mmpr_tiny.parquet"
    cache_dir = tmp_path / "cache"
    escape_path = tmp_path / "escape.txt"
    _write_zip(zip_path, {"images/ok.txt": "ok\n", "../escape.txt": "escape\n"})
    parquet_path.write_text("fake parquet\n", encoding="utf-8")

    calls = []

    def fake_hf_hub_download(repo_id, filename, *, repo_type, revision):
        calls.append(
            {
                "repo_id": repo_id,
                "filename": filename,
                "repo_type": repo_type,
                "revision": revision,
            }
        )
        return str(zip_path if filename == "images.zip" else parquet_path)

    monkeypatch.setattr(converter, "hf_hub_download", fake_hf_hub_download)

    with pytest.raises(ValueError, match="Unsafe zip member path"):
        converter._ensure_downloaded(str(cache_dir))

    assert calls == [
        {
            "repo_id": EXPECTED_REPO,
            "filename": "images.zip",
            "repo_type": "dataset",
            "revision": EXPECTED_REVISION,
        }
    ]
    assert not escape_path.exists()
    assert not (cache_dir / ".mmpr_ready").exists()
    assert not (cache_dir / "MMPR-Tiny" / "images" / "ok.txt").exists()


def test_mmpr_tiny_converter_extracts_normal_zip_with_pinned_downloads(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    converter = _load_converter_module()
    zip_path = tmp_path / "images.zip"
    parquet_path = tmp_path / "mmpr_tiny.parquet"
    cache_dir = tmp_path / "cache"
    _write_zip(zip_path, {"images/nested/ok.txt": "ok\n"})
    parquet_path.write_text("fake parquet\n", encoding="utf-8")

    calls = []

    def fake_hf_hub_download(repo_id, filename, *, repo_type, revision):
        calls.append(
            {
                "repo_id": repo_id,
                "filename": filename,
                "repo_type": repo_type,
                "revision": revision,
            }
        )
        return str(zip_path if filename == "images.zip" else parquet_path)

    monkeypatch.setattr(converter, "hf_hub_download", fake_hf_hub_download)

    converter._ensure_downloaded(str(cache_dir))

    assert calls == [
        {
            "repo_id": EXPECTED_REPO,
            "filename": "images.zip",
            "repo_type": "dataset",
            "revision": EXPECTED_REVISION,
        },
        {
            "repo_id": EXPECTED_REPO,
            "filename": "mmpr_tiny.parquet",
            "repo_type": "dataset",
            "revision": EXPECTED_REVISION,
        },
    ]
    assert (cache_dir / "MMPR-Tiny" / "images" / "nested" / "ok.txt").read_text(
        encoding="utf-8"
    ) == "ok\n"
    assert (cache_dir / "mmpr_tiny.parquet").read_text(encoding="utf-8") == "fake parquet\n"
    assert (cache_dir / ".mmpr_ready").read_text(encoding="utf-8") == "ready\n"
    assert not (cache_dir / "_tmp_extract").exists()
