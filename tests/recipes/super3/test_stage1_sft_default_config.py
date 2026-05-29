"""Static guards for generic Super3 stage1 SFT data-prep defaults."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.data_prep.core.chat_sft_shard_core import _matches_used_in_filter
from nemotron.kit.train_script import resolve_repo_relative_source_path
from nemotron.recipes.super3.stage1_sft.data_prep import SFTDataPrepConfig

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
CORE_BLEND_CONFIGS = {
    "default": (
        DEFAULT_CONFIG,
        "src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json",
    ),
    "tiny": (
        DATA_PREP_CONFIG_DIR / "tiny.yaml",
        "src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_tiny.json",
    ),
}
SUPER3_BLEND = DATA_PREP_CONFIG_DIR / "data_blend_raw.json"
SUPER3_TINY_BLEND = DATA_PREP_CONFIG_DIR / "data_blend_tiny.json"


def test_super3_stage1_sft_default_uses_super3_blend() -> None:
    config = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    blend_path = config["blend_path"]

    assert "/super3/stage1_sft/config/data_prep/data_blend_raw.json" in blend_path
    assert "/nano3/" not in blend_path


@pytest.mark.parametrize(("profile", "config_path_expected"), CORE_BLEND_CONFIGS.items())
def test_stage1_sft_core_blend_paths_are_repo_local(
    profile: str,
    config_path_expected: tuple[Path, str],
) -> None:
    config_path, expected = config_path_expected
    text = config_path.read_text(encoding="utf-8")
    config = yaml.safe_load(text)

    assert config["blend_path"] == expected, profile
    assert "/nano3/" not in config["blend_path"], profile
    assert "${oc.env:PWD}/src/" not in text


@pytest.mark.parametrize(("profile", "config_path_expected"), CORE_BLEND_CONFIGS.items())
def test_stage1_sft_core_blend_paths_resolve_from_non_repo_cwd(
    profile: str,
    config_path_expected: tuple[Path, str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path, expected = config_path_expected
    monkeypatch.chdir(tmp_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    blend_path = resolve_repo_relative_source_path(
        config["blend_path"],
        anchor_file=config_path,
    )

    assert blend_path == REPO_ROOT / expected, profile
    assert blend_path.is_file()


def test_stage1_sft_config_dataclass_resolves_repo_local_blend_path() -> None:
    _, expected = CORE_BLEND_CONFIGS["default"]
    cfg = SFTDataPrepConfig(blend_path=expected)

    assert cfg.blend_path == REPO_ROOT / expected


def test_stage1_sft_config_dataclass_preserves_relative_override() -> None:
    cfg = SFTDataPrepConfig(blend_path="custom/blend.json")

    assert cfg.blend_path == Path("custom/blend.json")


def test_stage1_sft_config_dataclass_preserves_absolute_override(tmp_path: Path) -> None:
    override = tmp_path / "custom" / "blend.json"
    cfg = SFTDataPrepConfig(blend_path=override)

    assert cfg.blend_path == override


@pytest.mark.parametrize("profile", sorted(CORE_BLEND_CONFIGS))
def test_super3_stage1_sft_core_profiles_have_no_nano_used_in_filter(
    profile: str,
) -> None:
    config_path, _expected = CORE_BLEND_CONFIGS[profile]
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    assert config["used_in_filter"] is None, profile


def test_super3_stage1_sft_blend_has_datasets() -> None:
    blend = json.loads(SUPER3_BLEND.read_text(encoding="utf-8"))

    assert isinstance(blend.get("datasets"), list)
    assert blend["datasets"], "Super3 stage1 SFT blend must not be empty"


def test_super3_stage1_sft_tiny_blend_has_datasets() -> None:
    blend = json.loads(SUPER3_TINY_BLEND.read_text(encoding="utf-8"))

    assert isinstance(blend.get("datasets"), list)
    assert blend["datasets"], "Super3 stage1 SFT tiny blend must not be empty"
    assert all("/nano3/" not in json.dumps(dataset) for dataset in blend["datasets"])


def test_super3_stage1_sft_tiny_preserves_non_blend_semantics() -> None:
    config = yaml.safe_load((DATA_PREP_CONFIG_DIR / "tiny.yaml").read_text(encoding="utf-8"))

    assert config["output_dir"] == "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage1_sft_tiny"
    assert config["num_shards"] == 4
    assert config["tokenizer"] == {
        "model": "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
        "add_bos": False,
        "add_eos": True,
    }
    assert config["pack_size"] == 4096
    assert config["algorithm"] == "first_fit_shuffle"
    assert config["chat_template"] == "super3"
    assert config["sample"] == 1000
    assert config["config_name"] == "tiny"


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
