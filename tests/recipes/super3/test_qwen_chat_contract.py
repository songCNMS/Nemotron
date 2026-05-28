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
