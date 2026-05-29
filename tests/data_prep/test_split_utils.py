# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
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

from __future__ import annotations

import os
from pathlib import Path

import pytest

from nemotron.data_prep.utils.splits import realize_packed_shards_into_split_dirs


def _write_parquet_placeholder(path_without_suffix: Path) -> Path:
    parquet_path = Path(f"{path_without_suffix}.parquet")
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.write_bytes(b"placeholder")
    return parquet_path


def test_realize_packed_shards_removes_stale_parquet_entries(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    shard_path = tmp_path / "packed" / "current" / "shard_000000"
    parquet_path = _write_parquet_placeholder(shard_path)

    split_dir = output_dir / "splits" / "train"
    split_dir.mkdir(parents=True)
    stale_file = split_dir / "stale_file.parquet"
    stale_file.write_bytes(b"old")
    stale_link = split_dir / "stale_link.parquet"
    stale_link.symlink_to("missing_old_target.parquet")
    sidecar = split_dir / "notes.txt"
    sidecar.write_text("keep me", encoding="utf-8")

    result = realize_packed_shards_into_split_dirs(
        output_dir=output_dir,
        split_to_paths={"train": ["1.0", str(shard_path)]},
    )

    current_link = split_dir / "shard_000000.parquet"
    assert result["train"] == split_dir
    assert not stale_file.exists()
    assert not stale_link.exists()
    assert not stale_link.is_symlink()
    assert sidecar.read_text(encoding="utf-8") == "keep me"
    assert current_link.is_symlink()
    assert os.readlink(current_link) == os.path.relpath(parquet_path, split_dir)


def test_realize_packed_shards_rejects_stale_parquet_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    shard_path = tmp_path / "packed" / "current" / "shard_000000"
    _write_parquet_placeholder(shard_path)

    stale_dir = output_dir / "splits" / "train" / "stale_000000.parquet"
    stale_dir.mkdir(parents=True)

    with pytest.raises(RuntimeError, match="Cannot remove stale parquet split entry"):
        realize_packed_shards_into_split_dirs(
            output_dir=output_dir,
            split_to_paths={"train": ["1.0", str(shard_path)]},
        )


def test_realize_packed_shards_rejects_current_parquet_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    shard_path = tmp_path / "packed" / "current" / "shard_000000"
    _write_parquet_placeholder(shard_path)

    current_dir = output_dir / "splits" / "train" / "shard_000000.parquet"
    current_dir.mkdir(parents=True)

    with pytest.raises(RuntimeError, match="Cannot replace parquet split entry"):
        realize_packed_shards_into_split_dirs(
            output_dir=output_dir,
            split_to_paths={"train": ["1.0", str(shard_path)]},
        )


def test_realize_packed_shards_missing_train_shard_still_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No parquet files found for train split"):
        realize_packed_shards_into_split_dirs(
            output_dir=tmp_path / "output",
            split_to_paths={"train": ["1.0", str(tmp_path / "missing" / "shard_000000")]},
        )
