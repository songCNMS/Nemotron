"""Static guards for generic Super3 stage1 SFT data-prep defaults."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.data_prep.core.chat_sft_shard_core import _matches_used_in_filter

yaml = pytest.importorskip("yaml")
OmegaConf = pytest.importorskip("omegaconf").OmegaConf


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PREP_CONFIG_DIR = REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/config/data_prep"
DEFAULT_CONFIG = DATA_PREP_CONFIG_DIR / "default.yaml"
DATA_PREP_CONFIGS = {
    "default": (DEFAULT_CONFIG, "stage1_sft"),
    "tiny": (DATA_PREP_CONFIG_DIR / "tiny.yaml", "stage1_sft_tiny"),
    "agentic_v0": (DATA_PREP_CONFIG_DIR / "agentic_v0.yaml", "stage1_sft_agentic_v0"),
    "qwen_agentic_v0": (
        DATA_PREP_CONFIG_DIR / "qwen_agentic_v0.yaml",
        "stage1_sft_agentic_v0_qwen",
    ),
}
SUPER3_BLEND = (
    DATA_PREP_CONFIG_DIR / "data_blend_raw.json"
)


def test_super3_stage1_sft_default_uses_super3_blend() -> None:
    config = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    blend_path = config["blend_path"]

    assert "/super3/stage1_sft/config/data_prep/data_blend_raw.json" in blend_path
    assert "/nano3/" not in blend_path


def test_super3_stage1_sft_default_has_no_nano_used_in_filter() -> None:
    config = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))

    assert config["used_in_filter"] is None


def test_super3_stage1_sft_blend_has_datasets() -> None:
    blend = json.loads(SUPER3_BLEND.read_text(encoding="utf-8"))

    assert isinstance(blend.get("datasets"), list)
    assert blend["datasets"], "Super3 stage1 SFT blend must not be empty"


@pytest.mark.parametrize(("profile", "config_path_suffix"), DATA_PREP_CONFIGS.items())
def test_stage1_sft_data_prep_output_dir_uses_nemo_run_dir(
    profile: str,
    config_path_suffix: tuple[Path, str],
) -> None:
    config_path, suffix = config_path_suffix
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    assert config["output_dir"] == f"${{oc.env:NEMO_RUN_DIR,.}}/output/super3/{suffix}", profile
    assert "${oc.env:PWD}" not in config["output_dir"]
    assert "/../output/" not in config["output_dir"]


@pytest.mark.parametrize(("profile", "config_path_suffix"), DATA_PREP_CONFIGS.items())
def test_stage1_sft_data_prep_output_dir_resolves_under_run_dir(
    profile: str,
    config_path_suffix: tuple[Path, str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path, suffix = config_path_suffix
    run_dir = tmp_path / "nemo_run"
    monkeypatch.setenv("NEMO_RUN_DIR", str(run_dir))

    cfg = OmegaConf.load(config_path)

    assert Path(cfg.output_dir) == run_dir / "output" / "super3" / suffix, profile


def test_used_in_filter_rejects_missing_used_in_when_configured() -> None:
    assert _matches_used_in_filter(None, "nano_v3") is False
    assert _matches_used_in_filter(["super3"], "nano_v3") is False
    assert _matches_used_in_filter(["nano_v3"], "nano_v3") is True
