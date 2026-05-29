import re
from pathlib import Path

import numpy as np
import pytest
import xxhash

pa = pytest.importorskip("pyarrow")
pytest.importorskip("pyarrow.parquet")

from nemotron.data_prep.core.chat_sft_shard_core import process_chat_sft_parquet_from_spool_core  # noqa: E402
from nemotron.data_prep.core.work_items import SftShardWorkItem  # noqa: E402
from nemotron.data_prep.packing.spool import (  # noqa: E402
    SequenceSpoolPaths,
    SequenceSpoolWriter,
)
from nemotron.data_prep.packing.writers import ParquetShardWriter  # noqa: E402
from nemotron.data_prep.stages.packed_sft_parquet import (  # noqa: E402
    PackedSftParquetStage,
    _fallback_parquet_file_metadata,
)
from nemotron.data_prep.utils.filesystem import get_filesystem  # noqa: E402

XXH64_RE = re.compile(r"^xxh64:[0-9a-f]{16}$")


def _xxh64_file(path: Path) -> str:
    hasher = xxhash.xxh64()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return f"xxh64:{hasher.hexdigest()}"


def _write_spool(root: Path, sequences: list[list[int]]) -> None:
    fs, _ = get_filesystem(str(root))
    paths = SequenceSpoolPaths.for_root(str(root))
    writer = SequenceSpoolWriter(fs=fs, paths=paths)
    for sequence in sequences:
        input_ids = np.asarray(sequence, dtype=np.int32)
        loss_mask = np.ones((len(sequence),), dtype=np.uint8)
        writer.append(input_ids, loss_mask)
    writer.finalize(
        extra_manifest={
            "input_files": ["fixture.jsonl"],
            "tokenization_stats": {
                "num_input_rows": len(sequences),
                "num_output_sequences": len(sequences),
            },
        }
    )


def _assert_real_checksum(checksum: str) -> None:
    assert XXH64_RE.match(checksum), checksum
    invalid_checksums = {"xxh64:" + "unknown", "xxh64:missing", "xxh64:empty"}
    assert checksum not in invalid_checksums


def test_parquet_shard_writer_finalizes_real_checksum_and_changes(tmp_path: Path) -> None:
    first_path = tmp_path / "first.parquet"
    first_writer = ParquetShardWriter(
        output_path=str(first_path),
        row_group_size=1,
        compression="none",
    )
    first_writer.write_bin(
        bin_id=0,
        input_ids=np.asarray([1, 2, 3], dtype=np.int32),
        loss_mask=np.asarray([1, 1, 0], dtype=np.uint8),
        seq_start_id=np.asarray([0], dtype=np.int32),
    )
    first_result = first_writer.finalize()

    second_path = tmp_path / "second.parquet"
    second_writer = ParquetShardWriter(
        output_path=str(second_path),
        row_group_size=1,
        compression="none",
    )
    second_writer.write_bin(
        bin_id=0,
        input_ids=np.asarray([4, 5, 6, 7], dtype=np.int32),
        loss_mask=np.asarray([1, 0, 1, 0], dtype=np.uint8),
        seq_start_id=np.asarray([0], dtype=np.int32),
    )
    second_result = second_writer.finalize()

    _assert_real_checksum(first_result["checksum"])
    _assert_real_checksum(second_result["checksum"])
    assert first_result["bytes"] == first_path.stat().st_size
    assert second_result["bytes"] == second_path.stat().st_size
    assert first_result["checksum"] == _xxh64_file(first_path)
    assert second_result["checksum"] == _xxh64_file(second_path)
    assert first_result["checksum"] != second_result["checksum"]

    fs_path = tmp_path / "pyarrow_fs.parquet"
    fs_writer = ParquetShardWriter(
        output_path=str(fs_path),
        row_group_size=1,
        compression="none",
        filesystem=pa.fs.LocalFileSystem(),
    )
    fs_writer.write_bin(
        bin_id=0,
        input_ids=np.asarray([8, 9], dtype=np.int32),
        loss_mask=np.asarray([1, 1], dtype=np.uint8),
        seq_start_id=np.asarray([0], dtype=np.int32),
    )
    fs_result = fs_writer.finalize()

    _assert_real_checksum(fs_result["checksum"])
    assert fs_result["bytes"] == fs_path.stat().st_size
    assert fs_result["checksum"] == _xxh64_file(fs_path)


def test_packed_sft_parquet_core_returns_real_parquet_checksum(tmp_path: Path) -> None:
    spool_dir = tmp_path / "spool" / "shard_000000"
    output_dir = tmp_path / "out"
    _write_spool(spool_dir, [[1, 2, 3], [4, 5]])
    fs, _ = get_filesystem(str(output_dir))

    stats, files = process_chat_sft_parquet_from_spool_core(
        shard_index=0,
        output_dir=str(output_dir),
        spool_dir=str(spool_dir),
        output_fs=fs,
        pack_size=8,
        algorithm="first_fit_decreasing",
        dtype=np.dtype("int32"),
        seed=None,
        parquet_row_group_size=1,
        parquet_compression="none",
    )

    parquet = files["parquet"]
    parquet_path = output_dir / parquet["path"]
    _assert_real_checksum(parquet["checksum"])
    assert parquet["bytes"] == parquet_path.stat().st_size
    assert parquet["checksum"] == _xxh64_file(parquet_path)
    assert stats["packing"]["writer"]["checksum"] == parquet["checksum"]


def test_packed_sft_parquet_stage_receipt_payload_uses_core_checksum(
    tmp_path: Path,
) -> None:
    spool_dir = tmp_path / "spool" / "shard_000000"
    output_dir = tmp_path / "out"
    _write_spool(spool_dir, [[1, 2, 3], [4, 5]])
    fs, _ = get_filesystem(str(output_dir))

    stage = object.__new__(PackedSftParquetStage)
    stage._fs = fs
    task = SftShardWorkItem(
        dataset_name="fixture",
        plan_hash="plan",
        shard_index=0,
        assignment={"files": []},
        output_dir=str(output_dir),
        receipts_dir=str(tmp_path / "receipts"),
        spool_dir=str(spool_dir),
        pack_size=8,
        algorithm="first_fit_decreasing",
        parquet_row_group_size=1,
        parquet_compression="none",
    )

    _stats, files = stage._build_completed_payload(task)

    parquet = files["parquet"]
    parquet_path = output_dir / parquet["path"]
    _assert_real_checksum(parquet["checksum"])
    assert parquet["bytes"] == parquet_path.stat().st_size
    assert parquet["checksum"] == _xxh64_file(parquet_path)
    assert _fallback_parquet_file_metadata("missing.parquet", 0)["checksum"] == "xxh64:empty"
    assert _fallback_parquet_file_metadata("missing.parquet", 12)["checksum"] == "xxh64:missing"
