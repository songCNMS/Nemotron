from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import (  # noqa: E402
    NEMOTRON_SUPER_TOKENIZER_DEFAULT,
    QWEN_DATA_PREP_CONFIG_NAME,
    QWEN_DATA_PREP_TARGET_FAMILY,
    QWEN_SFT_CHAT_TEMPLATE,
    QWEN_SFT_CHAT_TEMPLATE_KWARGS,
    validate_qwen_data_prep_config,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
QWEN_CONFIG = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml"
)
LEGACY_DEFAULT_CONFIG = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/default.yaml"
)
DATA_PREP_SCRIPT = REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/data_prep.py"


def _valid_qwen_config() -> dict:
    return {
        "target_model_family": QWEN_DATA_PREP_TARGET_FAMILY,
        "config_name": QWEN_DATA_PREP_CONFIG_NAME,
        "tokenizer": {"model": "/models/Qwen/Qwen3-4B-Instruct-2507"},
        "chat_template": QWEN_SFT_CHAT_TEMPLATE,
        "chat_template_kwargs": dict(QWEN_SFT_CHAT_TEMPLATE_KWARGS),
    }


def test_qwen_data_prep_contract_accepts_qwen_profile() -> None:
    validate_qwen_data_prep_config(_valid_qwen_config())


def test_qwen_data_prep_contract_rejects_super3_template() -> None:
    config = _valid_qwen_config()
    config["chat_template"] = "super3"

    with pytest.raises(ValueError, match="chat_template='tokenizer'"):
        validate_qwen_data_prep_config(config)


def test_qwen_data_prep_contract_rejects_nemotron_tokenizer_default() -> None:
    config = _valid_qwen_config()
    config["tokenizer"]["model"] = NEMOTRON_SUPER_TOKENIZER_DEFAULT

    with pytest.raises(ValueError, match="Nemotron/Super3 default"):
        validate_qwen_data_prep_config(config)


def test_qwen_agentic_config_file_is_self_guarded() -> None:
    config = yaml.safe_load(QWEN_CONFIG.read_text(encoding="utf-8"))

    validate_qwen_data_prep_config(config, config_path=QWEN_CONFIG)
    assert config["target_model_family"] == "qwen"
    assert config["config_name"] == "qwen_agentic_v0"
    assert config["chat_template"] == "tokenizer"


def test_sft_data_prep_runnable_defaults_select_qwen_profile() -> None:
    source = DATA_PREP_SCRIPT.read_text(encoding="utf-8")
    assert '# default = "qwen_agentic_v0"' in source
    assert 'DEFAULT_CONFIG_PATH = STAGE_PATH / "config" / "data_prep" / "qwen_agentic_v0.yaml"' in source


def test_qwen_agentic_config_prefers_tokenizer_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    omega_conf = pytest.importorskip("omegaconf").OmegaConf
    monkeypatch.setenv("SUPER3_M1_QWEN_HF_MODEL", "/models/Qwen/Qwen3-4B-Train")
    monkeypatch.setenv("SUPER3_M1_TOKENIZER_MODEL", "/models/Qwen/Qwen3-4B-Tokenizer")

    config = omega_conf.to_container(omega_conf.load(QWEN_CONFIG), resolve=True)

    assert config["tokenizer"]["model"] == "/models/Qwen/Qwen3-4B-Tokenizer"
    validate_qwen_data_prep_config(config, config_path=QWEN_CONFIG)


def test_qwen_agentic_config_falls_back_to_qwen_hf_model_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    omega_conf = pytest.importorskip("omegaconf").OmegaConf
    monkeypatch.delenv("SUPER3_M1_TOKENIZER_MODEL", raising=False)
    monkeypatch.setenv("SUPER3_M1_QWEN_HF_MODEL", "/models/Qwen/Qwen3-4B-Instruct-2507")

    config = omega_conf.to_container(omega_conf.load(QWEN_CONFIG), resolve=True)

    assert config["tokenizer"]["model"] == "/models/Qwen/Qwen3-4B-Instruct-2507"
    validate_qwen_data_prep_config(config, config_path=QWEN_CONFIG)


def test_legacy_super3_default_config_is_explicit_only() -> None:
    legacy = yaml.safe_load(LEGACY_DEFAULT_CONFIG.read_text(encoding="utf-8"))
    source = DATA_PREP_SCRIPT.read_text(encoding="utf-8")

    assert legacy["config_name"] == "default"
    assert legacy["tokenizer"]["model"] == NEMOTRON_SUPER_TOKENIZER_DEFAULT
    assert legacy["chat_template"] == "super3"
    assert legacy["used_in_filter"] == "nano_v3"
    assert "default.yaml" not in source.split("DEFAULT_CONFIG_PATH =", 1)[1].splitlines()[0]
