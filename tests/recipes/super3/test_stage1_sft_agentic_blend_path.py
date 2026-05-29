"""Static guards for M1 Agentic Stage1 SFT blend-path portability."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from nemotron.recipes.super3.milestones.m1_agentic_sft import prepare_m1_agentic_sft

yaml = pytest.importorskip("yaml")
OmegaConf = pytest.importorskip("omegaconf").OmegaConf


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PREP_CONFIG_DIR = REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/config/data_prep"
AGENTIC_BLEND_PATH = (
    "${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_agentic_sft_v0/"
    "data_blend_agentic_sft_v0.json"
)
BLEND_SUFFIX = Path("output/super3/m1_agentic_sft_v0/data_blend_agentic_sft_v0.json")
PROFILE_CONFIGS = {
    "agentic_v0": DATA_PREP_CONFIG_DIR / "agentic_v0.yaml",
    "qwen_agentic_v0": DATA_PREP_CONFIG_DIR / "qwen_agentic_v0.yaml",
}


def _load_profile(profile: str) -> tuple[str, dict[str, Any]]:
    text = PROFILE_CONFIGS[profile].read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict), f"{profile} config must be a mapping"
    return text, data


@pytest.mark.parametrize("profile", sorted(PROFILE_CONFIGS))
def test_agentic_stage1_sft_blend_path_uses_nemo_run_dir(profile: str) -> None:
    text, data = _load_profile(profile)

    assert data["blend_path"] == AGENTIC_BLEND_PATH
    assert "${oc.env:NEMO_RUN_DIR,.}" in data["blend_path"]
    assert "${oc.env:PWD}" not in data["blend_path"]
    assert "/../output/" not in data["blend_path"]
    assert "${oc.env:PWD}/../output/super3/m1_agentic_sft_v0" not in text


@pytest.mark.parametrize("profile", sorted(PROFILE_CONFIGS))
def test_agentic_stage1_sft_blend_path_resolves_to_producer_output(
    profile: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "nemo_run"
    monkeypatch.setenv("NEMO_RUN_DIR", str(run_dir))

    cfg = OmegaConf.load(PROFILE_CONFIGS[profile])
    expected = run_dir / BLEND_SUFFIX

    assert Path(cfg.blend_path) == expected
    producer_blend_path = (
        prepare_m1_agentic_sft._default_output_dir()
        / "data_blend_agentic_sft_v0.json"
    )
    assert producer_blend_path == expected


def test_agentic_stage1_sft_profiles_preserve_non_blend_semantics() -> None:
    _, agentic = _load_profile("agentic_v0")
    _, qwen = _load_profile("qwen_agentic_v0")

    assert (
        agentic["output_dir"]
        == "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage1_sft_agentic_v0"
    )
    assert (
        agentic["tokenizer"]["model"]
        == "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"
    )
    assert agentic["chat_template"] == "super3"
    assert agentic["chat_template_kwargs"] == {}
    assert agentic["used_in_filter"] == "super3_agentic_sft_v0"
    assert agentic["config_name"] == "agentic_v0"
    assert "target_model_family" not in agentic

    assert (
        qwen["output_dir"]
        == "${oc.env:NEMO_RUN_DIR,.}/output/super3/stage1_sft_agentic_v0_qwen"
    )
    assert (
        qwen["tokenizer"]["model"]
        == "${oc.env:SUPER3_M1_TOKENIZER_MODEL,${oc.env:SUPER3_M1_QWEN_HF_MODEL}}"
    )
    assert qwen["chat_template"] == "tokenizer"
    assert qwen["chat_template_kwargs"] == {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }
    assert qwen["used_in_filter"] == "super3_agentic_sft_v0"
    assert qwen["config_name"] == "qwen_agentic_v0"
    assert qwen["target_model_family"] == "qwen"


def test_agentic_stage1_sft_profiles_do_not_use_pwd_output_comment() -> None:
    offenders = []
    for profile, path in PROFILE_CONFIGS.items():
        text = path.read_text(encoding="utf-8")
        if "${PWD}/../output/" in text or "${oc.env:PWD}/../output/" in text:
            offenders.append(profile)

    assert offenders == []
