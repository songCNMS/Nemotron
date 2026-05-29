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

"""Revision propagation tests for generic pretrain/SFT data blends."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nemotron.data_prep.blend import DataBlend, Dataset
from nemotron.data_prep.config import FormatResult
from nemotron.data_prep.recipes import pretrain as pretrain_recipe
from nemotron.data_prep.recipes import sft as sft_recipe
from nemotron.kit.artifacts.pretrain_blends import PretrainBlendsArtifact
from nemotron.kit.artifacts.sft_data import SFTDataArtifact

REVISION_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
REVISION_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def _fake_resolve_tokenizer(_config: Any) -> dict[str, str]:
    return {
        "type": "huggingface",
        "model": "unit-test/tokenizer",
        "resolved_revision": "cccccccccccccccccccccccccccccccccccccccc",
        "tokenizer_hash": "unit-test-tokenizer",
    }


def _blend(revision: str | None) -> DataBlend:
    return DataBlend(
        datasets=[
            Dataset(
                name="hf_source",
                path="hf://unit/test-dataset",
                weight=2.0,
                split="train",
                subset="default",
                revision=revision,
                text_field="body",
            ),
            Dataset(
                name="local_source",
                path="/tmp/local-source.jsonl",
                weight=1.0,
                split=None,
                subset=None,
                revision=None,
            ),
        ]
    )


def _load_run_config(run_dir: str) -> dict[str, Any]:
    with (Path(run_dir) / "config.json").open() as f:
        return json.load(f)


def test_pretrain_setup_keeps_dataset_revision_in_config_work_items_and_plan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(pretrain_recipe, "resolve_tokenizer", _fake_resolve_tokenizer)

    items, context, _resolved_tokenizer = pretrain_recipe.setup_pretrain_run(
        _blend(REVISION_A),
        tmp_path / "pretrain",
        "unit-test/tokenizer",
        num_shards=2,
    )

    config = _load_run_config(context.run_dir)
    assert config["datasets"][0]["revision"] == REVISION_A
    assert config["datasets"][1]["revision"] is None
    assert items[0].revision == REVISION_A
    assert items[1].revision is None

    plan_request = pretrain_recipe.PretrainPlanAdapter().to_plan_request(items[0])
    assert plan_request.dataset_config.revision == REVISION_A


def test_pretrain_run_hash_changes_when_only_dataset_revision_changes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(pretrain_recipe, "resolve_tokenizer", _fake_resolve_tokenizer)

    _items_a, context_a, _tokenizer_a = pretrain_recipe.setup_pretrain_run(
        _blend(REVISION_A),
        tmp_path / "pretrain",
        "unit-test/tokenizer",
        num_shards=2,
    )
    _items_b, context_b, _tokenizer_b = pretrain_recipe.setup_pretrain_run(
        _blend(REVISION_B),
        tmp_path / "pretrain",
        "unit-test/tokenizer",
        num_shards=2,
    )

    assert context_a.run_hash != context_b.run_hash


def test_sft_setup_keeps_dataset_revision_in_config_work_items_and_plan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(sft_recipe, "resolve_tokenizer", _fake_resolve_tokenizer)

    items, context, _resolved_tokenizer = sft_recipe.setup_sft_run(
        _blend(REVISION_A),
        tmp_path / "sft",
        "unit-test/tokenizer",
        num_shards=2,
    )

    config = _load_run_config(context.run_dir)
    assert config["datasets"][0]["revision"] == REVISION_A
    assert config["datasets"][1]["revision"] is None
    assert items[0].revision == REVISION_A
    assert items[1].revision is None

    plan_request = sft_recipe.SftPlanAdapter().to_plan_request(items[0])
    assert plan_request.dataset_config.revision == REVISION_A


def test_sft_run_hash_changes_when_only_dataset_revision_changes(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(sft_recipe, "resolve_tokenizer", _fake_resolve_tokenizer)

    _items_a, context_a, _tokenizer_a = sft_recipe.setup_sft_run(
        _blend(REVISION_A),
        tmp_path / "sft",
        "unit-test/tokenizer",
        num_shards=2,
    )
    _items_b, context_b, _tokenizer_b = sft_recipe.setup_sft_run(
        _blend(REVISION_B),
        tmp_path / "sft",
        "unit-test/tokenizer",
        num_shards=2,
    )

    assert context_a.run_hash != context_b.run_hash


def _format_result(output_dir: Path) -> FormatResult:
    return FormatResult(
        run_hash="unit-run",
        run_dir=str(output_dir / "runs" / "unit-run"),
        output_dir=output_dir,
        num_shards=2,
        data_paths=[],
        dataset_stats={},
        from_cache=False,
        total_tokens=0,
        total_sequences=0,
    )


def test_pretrain_artifact_lineage_keeps_dataset_revision(tmp_path: Path) -> None:
    artifact = PretrainBlendsArtifact.from_result(
        _format_result(tmp_path / "pretrain-output"),
        _blend(REVISION_A),
        "unit-test/tokenizer",
        tmp_path / "pretrain-output" / "blend.json",
    )

    assert artifact.source_datasets[0].revision == REVISION_A
    assert artifact.source_datasets[1].revision is None


def test_sft_artifact_lineage_keeps_dataset_revision(tmp_path: Path) -> None:
    artifact = SFTDataArtifact.from_result(
        _format_result(tmp_path / "sft-output"),
        _blend(REVISION_A),
        "unit-test/tokenizer",
        tmp_path / "sft-output" / "blend.json",
        pack_size=2048,
    )

    assert artifact.source_datasets[0].revision == REVISION_A
    assert artifact.source_datasets[1].revision is None
