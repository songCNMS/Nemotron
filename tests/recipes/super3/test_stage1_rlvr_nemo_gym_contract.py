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

"""Stage1 RLVR NeMo-Gym datum conversion contract tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TRAIN_PATH = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/train.py"
)


def _load_train_module():
    spec = importlib.util.spec_from_file_location("stage1_rlvr_train", TRAIN_PATH)
    assert spec is not None and spec.loader is not None, TRAIN_PATH
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


TRAIN = _load_train_module()


class _FakeAllTaskProcessedDataset:
    def __init__(
        self,
        examples: list[Any],
        tokenizer: Any,
        _unused: Any,
        task_processor: Any,
    ) -> None:
        self.examples = examples
        self.tokenizer = tokenizer
        self.task_processor = task_processor


class _FakeDatumSpec(dict):
    pass


def _install_fake_nemo_rl_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    nemo_rl = ModuleType("nemo_rl")
    nemo_rl.__path__ = []
    data = ModuleType("nemo_rl.data")
    data.__path__ = []
    datasets = ModuleType("nemo_rl.data.datasets")
    interfaces = ModuleType("nemo_rl.data.interfaces")
    environments = ModuleType("nemo_rl.environments")
    environments.__path__ = []

    datasets.AllTaskProcessedDataset = _FakeAllTaskProcessedDataset
    interfaces.DatumSpec = _FakeDatumSpec
    nemo_rl.data = data
    data.datasets = datasets
    data.interfaces = interfaces
    nemo_rl.environments = environments

    torch = ModuleType("torch")
    torch.tensor = lambda value: ("tensor", value)

    for name, module in {
        "nemo_rl": nemo_rl,
        "nemo_rl.data": data,
        "nemo_rl.data.datasets": datasets,
        "nemo_rl.data.interfaces": interfaces,
        "nemo_rl.environments": environments,
        "torch": torch,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.delitem(sys.modules, "nemo_rl.environments.nemo_gym", raising=False)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_setup_single_nemo_gym_dataset_fails_fast_when_converter_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_nemo_rl_modules(monkeypatch)
    jsonl_path = tmp_path / "train.jsonl"
    _write_jsonl(
        jsonl_path,
        [
            {
                "responses_create_params": {
                    "input": [{"role": "user", "content": "keep this payload"}],
                },
                "extra_env_info": {"env": "stub"},
            }
        ],
    )

    with pytest.raises(ImportError, match="nemo_rl.environments.nemo_gym"):
        TRAIN.setup_single_nemo_gym_dataset(str(jsonl_path), tokenizer=object())


def test_setup_single_nemo_gym_dataset_delegates_to_nemo_gym_converter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_nemo_rl_modules(monkeypatch)
    calls: list[tuple[dict[str, Any], int]] = []

    def convert(example: dict[str, Any], idx: int) -> _FakeDatumSpec:
        calls.append((example, idx))
        return _FakeDatumSpec(
            {
                "message_log": example["responses_create_params"]["input"],
                "extra_env_info": example["extra_env_info"],
                "idx": idx,
                "stop_strings": ["<|im_end|>"],
            }
        )

    nemo_gym = ModuleType("nemo_rl.environments.nemo_gym")
    nemo_gym.nemo_gym_example_to_nemo_rl_datum_spec = convert
    monkeypatch.setitem(sys.modules, "nemo_rl.environments.nemo_gym", nemo_gym)

    row = {
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "question"},
            ],
        },
        "extra_env_info": {"environment": "math"},
    }
    jsonl_path = tmp_path / "train.jsonl"
    _write_jsonl(jsonl_path, [row])
    tokenizer = object()

    dataset = TRAIN.setup_single_nemo_gym_dataset(str(jsonl_path), tokenizer=tokenizer)

    assert calls == [(row, 0)]
    assert dataset.tokenizer is tokenizer
    assert dataset.examples == [
        {
            "message_log": row["responses_create_params"]["input"],
            "extra_env_info": row["extra_env_info"],
            "idx": 0,
            "stop_strings": ["<|im_end|>"],
        }
    ]


def test_stage1_rlvr_train_has_no_local_stop_strings_none_fallback() -> None:
    text = TRAIN_PATH.read_text(encoding="utf-8")
    assert "stop_strings=None" not in text
    assert "except ImportError" not in text
