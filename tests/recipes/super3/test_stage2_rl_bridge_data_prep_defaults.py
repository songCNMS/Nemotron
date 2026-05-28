"""Stage2 RL data-prep defaults must consume bridge combined JSONL outputs."""

from __future__ import annotations

from pathlib import Path

import pytest

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
