"""Static checks for stage0 pretrain data-prep config portability."""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage0_pretrain/config/data_prep"
)

EXPECTED_OUTPUT_DIRS = {
    "default": "${oc.env:PWD}/../output/super3/stage0_pretrain/phase1",
    "phase1": "${oc.env:PWD}/../output/super3/stage0_pretrain/phase1",
    "phase2": "${oc.env:PWD}/../output/super3/stage0_pretrain/phase2",
    "long_context": "${oc.env:PWD}/../output/super3/stage0_pretrain/long_context",
    "tiny": "${oc.env:PWD}/../output/super3/stage0_pretrain_tiny",
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


@pytest.mark.parametrize("config_name", sorted(EXPECTED_OUTPUT_DIRS))
def test_stage0_pretrain_data_prep_output_dirs_are_portable(
    config_name: str,
) -> None:
    text, data = _read_config(config_name)

    assert "/lustre/" not in text
    assert "users/mromeijn" not in text
    assert data["output_dir"] == EXPECTED_OUTPUT_DIRS[config_name]
    assert data["output_dir"].startswith("${oc.env:PWD}/../output/super3/")


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
