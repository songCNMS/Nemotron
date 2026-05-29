"""Static contracts for Nano3 stage0 pretrain data-prep configs."""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.recipes.nano3.stage0_pretrain.data_prep import PreTrainDataPrepConfig

yaml = pytest.importorskip("yaml")
OmegaConf = pytest.importorskip("omegaconf").OmegaConf


REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = (
    REPO_ROOT / "src/nemotron/recipes/nano3/stage0_pretrain/config/data_prep"
)
CONFIGS = {
    "default": CONFIG_DIR / "default.yaml",
    "tiny": CONFIG_DIR / "tiny.yaml",
}
EXPECTED_BLEND_PATHS = {
    "default": "src/nemotron/recipes/nano3/stage0_pretrain/config/data_prep/data_blend_raw.json",
    "tiny": "src/nemotron/recipes/nano3/stage0_pretrain/config/data_prep/data_blend_raw_small.json",
}
EXPECTED_OUTPUT_DIRS = {
    "default": "${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain",
    "tiny": "${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage0_pretrain_tiny",
}
EXPECTED_OUTPUT_SUFFIXES = {
    "default": Path("output/nano3/stage0_pretrain"),
    "tiny": Path("output/nano3/stage0_pretrain_tiny"),
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
def test_nano3_stage0_pretrain_blend_paths_are_repo_relative(
    config_name: str, config_path: Path
) -> None:
    text = config_path.read_text(encoding="utf-8")
    blend_path = yaml.safe_load(text)["blend_path"]

    assert blend_path == EXPECTED_BLEND_PATHS[config_name]
    assert "${oc.env:PWD}/src/" not in text
    assert Path(blend_path).is_relative_to("src/nemotron/recipes/nano3")


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_stage0_pretrain_output_dirs_are_nemo_run_dir_relative(
    config_name: str, config_path: Path
) -> None:
    text = config_path.read_text(encoding="utf-8")
    output_dir = yaml.safe_load(text)["output_dir"]

    assert "/lustre" not in output_dir
    assert "users/mromeijn" not in output_dir
    assert output_dir == EXPECTED_OUTPUT_DIRS[config_name]
    assert "${oc.env:PWD}" not in output_dir
    assert "/../output/" not in output_dir
    assert output_dir.startswith("${oc.env:NEMO_RUN_DIR,.}/output/nano3/")
    assert "/lustre" not in text
    assert "users/mromeijn" not in text


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_stage0_pretrain_output_dirs_resolve_under_run_dir(
    config_name: str,
    config_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("NEMO_RUN_DIR", str(tmp_path))

    cfg = OmegaConf.load(config_path)
    output_dir = Path(cfg.output_dir)

    assert output_dir == tmp_path / EXPECTED_OUTPUT_SUFFIXES[config_name]
    assert output_dir.is_relative_to(tmp_path / "output" / "nano3")


@pytest.mark.parametrize("config_name", sorted(CONFIGS))
def test_nano3_stage0_pretrain_dataclass_resolves_repo_blend_from_non_repo_cwd(
    config_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    cfg = PreTrainDataPrepConfig(blend_path=EXPECTED_BLEND_PATHS[config_name])

    assert cfg.blend_path == REPO_ROOT / EXPECTED_BLEND_PATHS[config_name]
    assert cfg.blend_path.is_file()


def test_nano3_stage0_pretrain_dataclass_preserves_absolute_blend_override(
    tmp_path: Path,
) -> None:
    absolute_override = tmp_path / "blend.json"

    cfg = PreTrainDataPrepConfig(blend_path=absolute_override)

    assert cfg.blend_path == absolute_override


@pytest.mark.parametrize(
    "relative_override",
    [
        Path("custom/blend.json"),
        Path("src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/data_blend_raw.json"),
    ],
)
def test_nano3_stage0_pretrain_dataclass_preserves_arbitrary_relative_blend_override(
    relative_override: Path,
) -> None:
    cfg = PreTrainDataPrepConfig(blend_path=relative_override)

    assert cfg.blend_path == relative_override
