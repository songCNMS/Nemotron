"""Static contracts for Nano3 stage0 pretrain data-prep configs."""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = (
    REPO_ROOT / "src/nemotron/recipes/nano3/stage0_pretrain/config/data_prep"
)
CONFIGS = {
    "default": CONFIG_DIR / "default.yaml",
    "tiny": CONFIG_DIR / "tiny.yaml",
}
REQUIRED_FIELDS = (
    "blend_path",
    "output_dir",
    "num_shards",
    "valid_shards",
    "test_shards",
    "tokenizer",
    "text_field",
    "sample",
    "force",
    "config_name",
    "plan",
    "download",
    "tokenization",
    "observability",
)


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_stage0_pretrain_configs_keep_required_fields(
    config_name: str, config_path: Path
) -> None:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    for field in REQUIRED_FIELDS:
        assert field in data, f"{config_name}.yaml missing field {field}"
    assert data["config_name"] == config_name
    assert data["blend_path"]
    assert data["output_dir"]
    assert data["num_shards"] >= data["valid_shards"] + data["test_shards"]
    assert {"model", "add_bos", "add_eos"}.issubset(data["tokenizer"])
    assert data["text_field"] == "text"
    assert "planner_cpus" in data["plan"]
    assert {
        "batch_size",
        "stage_cpus",
        "hf_xet_high_performance",
        "hf_xet_concurrent_range_gets",
        "max_retries",
        "timeout_sec",
    }.issubset(data["download"])
    assert "cpus_per_worker" in data["tokenization"]
    assert {
        "pipeline_logging_interval_s",
        "wandb_log_pipeline_stats",
    }.issubset(data["observability"])


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_stage0_pretrain_output_dirs_are_portable(
    config_name: str, config_path: Path
) -> None:
    text = config_path.read_text(encoding="utf-8")
    output_dir = yaml.safe_load(text)["output_dir"]

    assert "/lustre" not in output_dir
    assert "users/mromeijn" not in output_dir
    assert "/lustre" not in text
    assert "users/mromeijn" not in text


def test_nano3_stage0_default_output_dir_matches_dataclass_default_contract() -> None:
    data = yaml.safe_load(CONFIGS["default"].read_text(encoding="utf-8"))

    assert data["output_dir"] == (
        "${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain"
    )
