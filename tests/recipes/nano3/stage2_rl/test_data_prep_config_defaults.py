"""Static contracts for Nano3 stage2 RL data-prep configs."""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.recipes.nano3.stage2_rl.data_prep import RLDataPrepConfig

yaml = pytest.importorskip("yaml")
OmegaConf = pytest.importorskip("omegaconf").OmegaConf


REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = REPO_ROOT / "src/nemotron/recipes/nano3/stage2_rl/config/data_prep"
CONFIGS = {
    "default": CONFIG_DIR / "default.yaml",
    "tiny": CONFIG_DIR / "tiny.yaml",
}
EXPECTED_BLEND_PATH = "src/nemotron/recipes/nano3/stage2_rl/config/data_prep/data_blend_raw.json"
EXPECTED_OUTPUT_DIRS = {
    "default": "${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage2_rl_resolved",
    "tiny": "${oc.env:NEMO_RUN_DIR,.}/output/nano3/stage2_rl_tiny",
}
EXPECTED_OUTPUT_SUFFIXES = {
    "default": Path("output/nano3/stage2_rl_resolved"),
    "tiny": Path("output/nano3/stage2_rl_tiny"),
}


def _load_config(config_name: str) -> tuple[str, dict[str, object]]:
    config_path = CONFIGS[config_name]
    text = config_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    return text, data


@pytest.mark.parametrize("config_name", sorted(CONFIGS))
def test_nano3_stage2_rl_blend_paths_are_repo_relative(config_name: str) -> None:
    text, data = _load_config(config_name)
    blend_path = data["blend_path"]

    assert blend_path == EXPECTED_BLEND_PATH
    assert "${oc.env:PWD}/src/" not in text
    assert Path(blend_path).is_relative_to("src/nemotron/recipes/nano3")


@pytest.mark.parametrize("config_name", sorted(CONFIGS))
def test_nano3_stage2_rl_output_dirs_are_nemo_run_dir_relative(config_name: str) -> None:
    text, data = _load_config(config_name)
    output_dir = data["output_dir"]

    assert output_dir == EXPECTED_OUTPUT_DIRS[config_name]
    assert "${oc.env:PWD}" not in output_dir
    assert "/../output/" not in output_dir
    assert output_dir.startswith("${oc.env:NEMO_RUN_DIR,.}/output/nano3/")
    assert "${oc.env:PWD}" not in text
    assert "/../output/" not in text


@pytest.mark.parametrize("config_name", sorted(CONFIGS))
def test_nano3_stage2_rl_output_dirs_resolve_under_run_dir(
    config_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("NEMO_RUN_DIR", str(tmp_path))

    cfg = OmegaConf.load(CONFIGS[config_name])
    output_dir = Path(cfg.output_dir)

    assert output_dir == tmp_path / EXPECTED_OUTPUT_SUFFIXES[config_name]
    assert output_dir.is_relative_to(tmp_path / "output" / "nano3")


@pytest.mark.parametrize("config_name", sorted(CONFIGS))
def test_nano3_stage2_rl_dataclass_resolves_repo_blend_from_non_repo_cwd(
    config_name: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    cfg = RLDataPrepConfig(blend_path=EXPECTED_BLEND_PATH)

    assert cfg.blend_path == REPO_ROOT / EXPECTED_BLEND_PATH
    assert cfg.blend_path.is_file()


def test_nano3_stage2_rl_dataclass_preserves_absolute_blend_override(
    tmp_path: Path,
) -> None:
    absolute_override = tmp_path / "blend.json"

    cfg = RLDataPrepConfig(blend_path=absolute_override)

    assert cfg.blend_path == absolute_override


@pytest.mark.parametrize(
    "relative_override",
    [
        Path("custom/blend.json"),
        Path("src/nemotron/recipes/super3/stage2_rl/config/data_prep/data_blend_raw.json"),
    ],
)
def test_nano3_stage2_rl_dataclass_preserves_arbitrary_relative_blend_override(
    relative_override: Path,
) -> None:
    cfg = RLDataPrepConfig(blend_path=relative_override)

    assert cfg.blend_path == relative_override
