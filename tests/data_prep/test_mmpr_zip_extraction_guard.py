# Copyright (c) 2026, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Synthetic zip traversal guard coverage for MMPR data-prep paths."""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest

from nemotron.data_prep.stages import vlm_preference_prep
from nemotron.data_prep.utils.safe_zip import safe_extract_zip

REPO_ROOT = Path(__file__).resolve().parents[2]
TINY_SCRIPT_PATH = REPO_ROOT / "scripts" / "prepare_mmpr_tiny_for_vision_rl.py"


def _load_tiny_script_module():
    spec = importlib.util.spec_from_file_location(
        "prepare_mmpr_tiny_for_vision_rl",
        TINY_SCRIPT_PATH,
    )
    assert spec is not None and spec.loader is not None, TINY_SCRIPT_PATH
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


TINY_SCRIPT = _load_tiny_script_module()


def _write_zip(path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)


@pytest.mark.parametrize(
    "member_name_template",
    [
        "../escape.txt",
        "{absolute_escape}",
        "C:/tmp/escape.txt",
    ],
)
def test_safe_extract_zip_rejects_traversal_before_writing(
    tmp_path: Path,
    member_name_template: str,
):
    zip_path = tmp_path / "images.zip"
    output_dir = tmp_path / "extract"
    absolute_escape = tmp_path.parent / f"{tmp_path.name}_absolute_escape.txt"
    member_name = member_name_template.format(absolute_escape=absolute_escape)
    _write_zip(
        zip_path,
        {
            "images/ok.txt": "ok\n",
            member_name: "outside\n",
        },
    )

    with zipfile.ZipFile(zip_path) as zf:
        with pytest.raises(ValueError, match="Unsafe zip member path"):
            safe_extract_zip(zf, output_dir)

    assert not (output_dir / "images" / "ok.txt").exists()
    assert not (tmp_path / "escape.txt").exists()
    assert not absolute_escape.exists()


def test_safe_extract_zip_extracts_normal_nested_archive(tmp_path: Path):
    zip_path = tmp_path / "images.zip"
    output_dir = tmp_path / "extract"
    _write_zip(zip_path, {"images/nested/ok.txt": "ok\n"})

    with zipfile.ZipFile(zip_path) as zf:
        extracted = safe_extract_zip(zf, output_dir)

    assert extracted == [output_dir / "images" / "nested" / "ok.txt"]
    assert (output_dir / "images" / "nested" / "ok.txt").read_text(
        encoding="utf-8"
    ) == "ok\n"


def test_tiny_script_rejects_traversal_member_without_writing_escape(tmp_path: Path):
    zip_path = tmp_path / "images.zip"
    output_dir = tmp_path / "cache"
    _write_zip(
        zip_path,
        {
            "images/ok.txt": "ok\n",
            "../escape.txt": "outside\n",
        },
    )

    with pytest.raises(ValueError, match="Unsafe zip member path"):
        TINY_SCRIPT.extract_images_if_needed(zip_path, output_dir)

    assert not (tmp_path / "escape.txt").exists()
    assert not (output_dir / "escape.txt").exists()
    assert not (output_dir / "MMPR-Tiny" / "images").exists()


def test_vlm_stage_rejects_traversal_member_without_writing_escape(tmp_path: Path):
    zip_path = tmp_path / "images.zip"
    output_dir = tmp_path / "cache"
    _write_zip(
        zip_path,
        {
            "images/ok.txt": "ok\n",
            "../escape.txt": "outside\n",
        },
    )

    with pytest.raises(ValueError, match="Unsafe zip member path"):
        vlm_preference_prep._extract_images_if_needed(zip_path, output_dir)

    assert not (tmp_path / "escape.txt").exists()
    assert not (output_dir / "escape.txt").exists()
    assert not (output_dir / "MMPR-Tiny" / "images").exists()
