import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

# Optional heavy deps — skip collection on sandboxes that don't have
# numpy / omegaconf / pyarrow / megatron-bridge installed. PR #176
# originally added this pattern; the V8 commit (`0db5490`) reverted the
# importorskip back to bare imports, breaking sandbox collection a
# second time. Restored here so the full super3 test suite stays
# collectable on a clean checkout.
np = pytest.importorskip("numpy")
OmegaConf = pytest.importorskip("omegaconf").OmegaConf
pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")
pytest.importorskip("megatron.bridge.training.config")
train_module = pytest.importorskip("nemotron.recipes.super3.stage1_sft.train")
_build_dataset_config = train_module._build_dataset_config


def _write_packed_parquet(path: Path, rows: list[dict[str, list[int] | list[bool]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)


def test_super3_bridge_rebuilds_corrupt_npy_and_writes_metadata_atomically(tmp_path: Path) -> None:
    splits = tmp_path / "splits"
    train_rows = [
        {"input_ids": [1, 2, 3, 4], "loss_mask": [False, True, True, False], "seq_start_id": [0]},
        {"input_ids": [5, 6, 7, 8, 9], "loss_mask": [False, True, True, True, False], "seq_start_id": [0, 3]},
    ]
    valid_rows = [
        {"input_ids": [10, 11, 12], "loss_mask": [False, True, False], "seq_start_id": [0]},
    ]
    _write_packed_parquet(splits / "train" / "shard_000000.parquet", train_rows)
    _write_packed_parquet(splits / "valid" / "shard_000000.parquet", valid_rows)

    corrupt_npy = splits / "train_8_train.npy"
    corrupt_npy.write_bytes(b"truncated")
    newer_than_parquet = max(
        (splits / "train" / "shard_000000.parquet").stat().st_mtime,
        (splits / "valid" / "shard_000000.parquet").stat().st_mtime,
    ) + 10
    os.utime(corrupt_npy, (newer_than_parquet, newer_than_parquet))

    cfg = OmegaConf.create(
        {
            "super3_packed_sft_dir": str(splits),
            "packed_sequence_specs": {"packed_sequence_size": 8},
        }
    )
    current_dataset = SimpleNamespace(dataset_root=None, seq_length=8, dataloader_type="batch")

    dataset_cfg = _build_dataset_config(cfg, current_dataset)

    specs = dataset_cfg.packed_sequence_specs
    train_npy = Path(specs.packed_train_data_path)
    valid_npy = Path(specs.packed_val_data_path)
    metadata_path = Path(specs.packed_metadata_path)

    loaded_train = np.load(train_npy, allow_pickle=True)
    loaded_valid = np.load(valid_npy, allow_pickle=True)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert len(loaded_train) == 2
    assert len(loaded_valid) == 1
    assert metadata[0]["pack_size"] == 8
    assert metadata_path.with_name(f"{metadata_path.name}.lock").exists() is False
    assert train_npy.with_name(f"{train_npy.name}.lock").exists() is False
