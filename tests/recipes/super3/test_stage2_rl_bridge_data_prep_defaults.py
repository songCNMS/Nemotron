"""Stage2 RL data-prep defaults must consume bridge combined JSONL outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.data_prep.recipes.rl_local import split_local_jsonl

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE2_RL_ROOT = REPO_ROOT / "src/nemotron/recipes/super3/stage2_rl"

DEFAULTS = {
    "swe1": STAGE2_RL_ROOT / "stage2_swe1/config/data_prep/default.yaml",
    "swe2": STAGE2_RL_ROOT / "stage2_swe2/config/data_prep/default.yaml",
    "rlhf": STAGE2_RL_ROOT / "stage3_rlhf/config/data_prep/default.yaml",
}


@pytest.mark.parametrize(("mix", "config_path"), DEFAULTS.items())
def test_stage2_rl_default_input_path_uses_bridge_combined_jsonl(
    mix: str, config_path: Path
) -> None:
    text = config_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    assert "/lustre/" not in text
    assert "yifuw" not in text
    assert "combined.jsonl" in data["input_path"]
    assert "${oc.env:NEMO_RUN_DIR" in data["input_path"]
    assert f"m1_{mix}/combined.jsonl" in data["input_path"]


@pytest.mark.parametrize(("mix", "config_path"), DEFAULTS.items())
def test_stage2_rl_default_preserves_data_prep_config_fields(
    mix: str, config_path: Path
) -> None:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    for field in ("input_path", "output_dir", "val_holdout", "sample", "force"):
        assert field in data, f"{mix} data_prep default missing field {field}"

    assert data["val_holdout"] == "auto"


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_split_local_jsonl_infers_bridge_holdout_from_manifest_counts(tmp_path: Path) -> None:
    bridge_dir = tmp_path / "m1_swe1"
    bridge_dir.mkdir()
    combined_path = bridge_dir / "combined.jsonl"
    train_rows = [{"id": f"train-{i}", "split": "train"} for i in range(7)]
    val_rows = [{"id": f"val-{i}", "split": "val"} for i in range(3)]
    _write_jsonl(combined_path, [*train_rows, *val_rows])
    (bridge_dir / "manifest.json").write_text(
        json.dumps(
            {
                "counts": {
                    "train": {"swe_pivot_demo": len(train_rows)},
                    "val": {"swe_pivot_demo": len(val_rows)},
                }
            }
        ),
        encoding="utf-8",
    )

    result = split_local_jsonl(
        input_path=combined_path,
        output_dir=tmp_path / "stage2_out",
        val_holdout="auto",
        force=True,
    )

    assert result.train_rows == len(train_rows)
    assert result.val_rows == len(val_rows)
    assert _read_jsonl(Path(result.train_path)) == train_rows
    assert result.val_path is not None
    assert _read_jsonl(Path(result.val_path)) == val_rows

    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["val_holdout"] == len(val_rows)
    assert manifest["val_holdout_source"] == "bridge_manifest"
    assert manifest["bridge_manifest"]["val_rows"] == len(val_rows)


def test_split_local_jsonl_explicit_holdout_still_works_for_plain_jsonl(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "plain.jsonl"
    rows = [{"id": i} for i in range(8)]
    _write_jsonl(input_path, rows)

    result = split_local_jsonl(
        input_path=input_path,
        output_dir=tmp_path / "plain_out",
        val_holdout=2,
        force=True,
    )

    assert result.train_rows == 6
    assert result.val_rows == 2
    assert _read_jsonl(Path(result.train_path)) == rows[:6]
    assert result.val_path is not None
    assert _read_jsonl(Path(result.val_path)) == rows[-2:]


def test_split_local_jsonl_auto_holdout_requires_bridge_manifest(tmp_path: Path) -> None:
    combined_path = tmp_path / "combined.jsonl"
    _write_jsonl(combined_path, [{"id": i} for i in range(5)])

    with pytest.raises(FileNotFoundError, match="val_holdout=auto requires a bridge manifest"):
        split_local_jsonl(
            input_path=combined_path,
            output_dir=tmp_path / "out",
            val_holdout="auto",
            force=True,
        )


def test_split_local_jsonl_auto_holdout_rejects_bad_bridge_manifest_counts(
    tmp_path: Path,
) -> None:
    bridge_dir = tmp_path / "m1_rlhf"
    bridge_dir.mkdir()
    combined_path = bridge_dir / "combined.jsonl"
    _write_jsonl(combined_path, [{"id": i} for i in range(5)])
    (bridge_dir / "manifest.json").write_text(
        json.dumps({"counts": {"train": {"rlhf": 4}, "val": {"rlhf": 4}}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Bridge manifest row count does not match combined JSONL"):
        split_local_jsonl(
            input_path=combined_path,
            output_dir=tmp_path / "out",
            val_holdout="auto",
            force=True,
        )
