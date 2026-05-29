"""Static checks for stage0 pretrain data-prep config portability."""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.kit.train_script import resolve_repo_relative_source_path
from nemotron.recipes.super3.stage0_pretrain.data_prep import PreTrainDataPrepConfig

yaml = pytest.importorskip("yaml")
omegaconf = pytest.importorskip("omegaconf")
OmegaConf = omegaconf.OmegaConf


REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep"
)

EXPECTED_OUTPUT_DIRS = {
    "default": "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage0_pretrain/phase1",
    "phase1": "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage0_pretrain/phase1",
    "phase2": "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage0_pretrain/phase2",
    "long_context": "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage0_pretrain/long_context",
    "tiny": "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage0_pretrain_tiny",
}

EXPECTED_OUTPUT_SUFFIXES = {
    "default": Path("output/super3/stage0_pretrain/phase1"),
    "phase1": Path("output/super3/stage0_pretrain/phase1"),
    "phase2": Path("output/super3/stage0_pretrain/phase2"),
    "long_context": Path("output/super3/stage0_pretrain/long_context"),
    "tiny": Path("output/super3/stage0_pretrain_tiny"),
}

EXPECTED_BLEND_PATHS = {
    "default": "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/data_blend_raw_phase1.json",
    "phase1": "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/data_blend_raw_phase1.json",
    "phase2": "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/data_blend_raw_phase2.json",
    "long_context": (
        "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/"
        "data_blend_raw_long_context.json"
    ),
    "tiny": "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/data_blend_raw_small.json",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "blend_path",
    "output_dir",
    "num_shards",
    "valid_shards",
    "test_shards",
    "tokenizer",
    "text_field",
    "min_doc_chars",
    "max_doc_tokens",
    "sample",
    "force",
    "config_name",
    "plan",
    "download",
    "tokenization",
    "observability",
}


def _read_config(config_name: str) -> tuple[str, dict]:
    path = CONFIG_DIR / f"{config_name}.yaml"
    text = path.read_text(encoding="utf-8")
    return text, yaml.safe_load(text)


@pytest.mark.parametrize("config_name", sorted(EXPECTED_BLEND_PATHS))
def test_stage0_pretrain_data_prep_blend_paths_are_repo_local(
    config_name: str,
) -> None:
    text, data = _read_config(config_name)

    assert data["blend_path"] == EXPECTED_BLEND_PATHS[config_name]
    assert "${oc.env:PWD}/src/" not in text
    assert "/nano3/" not in data["blend_path"]


@pytest.mark.parametrize("config_name", sorted(EXPECTED_BLEND_PATHS))
def test_stage0_pretrain_data_prep_blend_paths_resolve_from_non_repo_cwd(
    config_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    _, data = _read_config(config_name)

    blend_path = resolve_repo_relative_source_path(
        data["blend_path"],
        anchor_file=CONFIG_DIR / f"{config_name}.yaml",
    )

    assert blend_path == REPO_ROOT / EXPECTED_BLEND_PATHS[config_name]
    assert blend_path.is_file()


def test_stage0_pretrain_config_dataclass_resolves_repo_local_blend_path() -> None:
    cfg = PreTrainDataPrepConfig(blend_path=EXPECTED_BLEND_PATHS["phase1"])

    assert cfg.blend_path == REPO_ROOT / EXPECTED_BLEND_PATHS["phase1"]


def test_stage0_pretrain_config_dataclass_preserves_relative_override() -> None:
    cfg = PreTrainDataPrepConfig(blend_path="custom/blend.json")

    assert cfg.blend_path == Path("custom/blend.json")


def test_stage0_pretrain_config_dataclass_preserves_absolute_override(
    tmp_path: Path,
) -> None:
    blend_path = tmp_path / "blend.json"

    cfg = PreTrainDataPrepConfig(blend_path=blend_path)

    assert cfg.blend_path == blend_path


def test_stage0_pretrain_tiny_blend_is_super3_owned_and_non_empty() -> None:
    _, tiny_data = _read_config("tiny")
    blend_path = REPO_ROOT / tiny_data["blend_path"]
    blend = yaml.safe_load(blend_path.read_text(encoding="utf-8"))
    datasets = blend["datasets"]

    assert tiny_data["blend_path"] == EXPECTED_BLEND_PATHS["tiny"]
    assert "src/nemotron/recipes/super3/stage0_pretrain" in tiny_data["blend_path"]
    assert "src/nemotron/recipes/nano3/" not in tiny_data["blend_path"]
    assert datasets
    assert len(datasets) <= 5
    assert {row["path"] for row in datasets} <= {
        "hf://nvidia/Nemotron-CC-v2",
        "hf://nvidia/Nemotron-CC-v2.1",
        "hf://nvidia/Nemotron-CC-Math-v1",
    }
    for row in datasets:
        assert {"name", "path", "subset", "text_field", "weight"} <= set(row)
        assert row["text_field"] == "text"


@pytest.mark.parametrize("config_name", sorted(EXPECTED_OUTPUT_DIRS))
def test_stage0_pretrain_data_prep_output_dirs_are_portable(
    config_name: str,
) -> None:
    text, data = _read_config(config_name)

    assert "/lustre/" not in text
    assert "users/mromeijn" not in text
    assert data["output_dir"] == EXPECTED_OUTPUT_DIRS[config_name]
    assert "${oc.env:PWD}" not in data["output_dir"]
    assert data["output_dir"].startswith("${oc.env:NEMO_RUN_DIR,.}/output/super3/")


@pytest.mark.parametrize("config_name", sorted(EXPECTED_OUTPUT_DIRS))
def test_stage0_pretrain_data_prep_output_dirs_resolve_under_run_dir(
    config_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("NEMO_RUN_DIR", str(tmp_path))

    cfg = OmegaConf.load(CONFIG_DIR / f"{config_name}.yaml")
    output_dir = Path(OmegaConf.to_container(cfg, resolve=True)["output_dir"])

    assert output_dir == tmp_path / EXPECTED_OUTPUT_SUFFIXES[config_name]
    assert output_dir.is_relative_to(tmp_path / "output" / "super3")


@pytest.mark.parametrize("config_name", sorted(EXPECTED_OUTPUT_DIRS))
def test_stage0_pretrain_data_prep_configs_preserve_required_fields(
    config_name: str,
) -> None:
    _, data = _read_config(config_name)

    assert REQUIRED_TOP_LEVEL_FIELDS <= set(data)
    assert {"model", "add_bos", "add_eos"} <= set(data["tokenizer"])
    assert "planner_cpus" in data["plan"]
    assert {"batch_size", "stage_cpus", "max_retries", "timeout_sec"} <= set(
        data["download"]
    )
    assert "cpus_per_worker" in data["tokenization"]
    assert {"pipeline_logging_interval_s", "wandb_log_pipeline_stats"} <= set(
        data["observability"]
    )
