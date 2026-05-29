import json
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
    validate_qwen_packed_sft_chat_contract,
    validate_sft_data_prep_target_family_config,
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
LEGACY_AGENTIC_CONFIG = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml"
)
LEGACY_TINY_CONFIG = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage1_sft/config/data_prep/tiny.yaml"
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


def _write_qwen_packed_metadata(
    tmp_path: Path,
    *,
    tokenizer_uri: str | None = "/models/Qwen/Qwen3-4B-Instruct-2507",
) -> Path:
    splits_dir = tmp_path / "splits"
    splits_dir.mkdir(parents=True)
    metadata = {
        "chat_template": QWEN_SFT_CHAT_TEMPLATE,
        "chat_template_kwargs": dict(QWEN_SFT_CHAT_TEMPLATE_KWARGS),
    }
    if tokenizer_uri is not None:
        metadata["tokenizer_uri"] = tokenizer_uri
    (splits_dir / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )
    return splits_dir


def test_qwen_data_prep_contract_accepts_qwen_profile() -> None:
    validate_qwen_data_prep_config(_valid_qwen_config())


def test_qwen_data_prep_contract_accepts_qwen_hf_id() -> None:
    config = _valid_qwen_config()
    config["tokenizer"]["model"] = "Qwen/Qwen3-4B-Instruct-2507"

    validate_qwen_data_prep_config(config)


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


def test_qwen_data_prep_contract_rejects_non_qwen_tokenizer_ref() -> None:
    config = _valid_qwen_config()
    config["tokenizer"]["model"] = "/models/Llama-3-tokenizer"

    with pytest.raises(ValueError, match="recognizably Qwen tokenizer/model"):
        validate_qwen_data_prep_config(config)


def test_qwen_agentic_config_file_is_self_guarded() -> None:
    config = yaml.safe_load(QWEN_CONFIG.read_text(encoding="utf-8"))

    validate_sft_data_prep_target_family_config(config, config_path=QWEN_CONFIG)
    validate_qwen_data_prep_config(config, config_path=QWEN_CONFIG)
    assert config["target_model_family"] == "qwen"
    assert config["config_name"] == "qwen_agentic_v0"
    assert config["chat_template"] == "tokenizer"


def test_sft_data_prep_runnable_defaults_select_qwen_profile() -> None:
    from nemotron.recipes.super3.stage1_sft.data_prep import DEFAULT_CONFIG_PATH

    source = DATA_PREP_SCRIPT.read_text(encoding="utf-8")
    assert '# default = "qwen_agentic_v0"' in source
    assert DEFAULT_CONFIG_PATH == QWEN_CONFIG
    assert DEFAULT_CONFIG_PATH.name == "qwen_agentic_v0.yaml"


def test_qwen_agentic_config_prefers_tokenizer_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    omega_conf = pytest.importorskip("omegaconf").OmegaConf
    monkeypatch.setenv("SUPER3_M1_QWEN_HF_MODEL", "/models/Qwen/Qwen3-4B-Train")
    monkeypatch.setenv("SUPER3_M1_TOKENIZER_MODEL", "/models/Qwen/Qwen3-4B-Tokenizer")

    config = omega_conf.to_container(omega_conf.load(QWEN_CONFIG), resolve=True)

    assert config["tokenizer"]["model"] == "/models/Qwen/Qwen3-4B-Tokenizer"
    validate_sft_data_prep_target_family_config(config, config_path=QWEN_CONFIG)
    validate_qwen_data_prep_config(config, config_path=QWEN_CONFIG)


def test_qwen_agentic_config_falls_back_to_qwen_hf_model_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    omega_conf = pytest.importorskip("omegaconf").OmegaConf
    monkeypatch.delenv("SUPER3_M1_TOKENIZER_MODEL", raising=False)
    monkeypatch.setenv("SUPER3_M1_QWEN_HF_MODEL", "/models/Qwen/Qwen3-4B-Instruct-2507")

    config = omega_conf.to_container(omega_conf.load(QWEN_CONFIG), resolve=True)

    assert config["tokenizer"]["model"] == "/models/Qwen/Qwen3-4B-Instruct-2507"
    validate_sft_data_prep_target_family_config(config, config_path=QWEN_CONFIG)
    validate_qwen_data_prep_config(config, config_path=QWEN_CONFIG)


@pytest.mark.parametrize(
    ("config_path", "config_name"),
    [
        (LEGACY_DEFAULT_CONFIG, "default"),
        (LEGACY_AGENTIC_CONFIG, "agentic_v0"),
        (LEGACY_TINY_CONFIG, "tiny"),
    ],
)
def test_legacy_super3_configs_are_explicit_non_qwen(
    config_path: Path,
    config_name: str,
) -> None:
    legacy = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    source = DATA_PREP_SCRIPT.read_text(encoding="utf-8")

    assert legacy["config_name"] == config_name
    assert legacy.get("target_model_family") != "qwen"
    assert legacy["tokenizer"]["model"] == NEMOTRON_SUPER_TOKENIZER_DEFAULT
    assert legacy["chat_template"] == "super3"
    validate_sft_data_prep_target_family_config(legacy, config_path=config_path)
    assert "default.yaml" not in source.split("DEFAULT_CONFIG_PATH =", 1)[1].splitlines()[0]


@pytest.mark.parametrize(
    "config_path",
    [LEGACY_DEFAULT_CONFIG, LEGACY_AGENTIC_CONFIG, LEGACY_TINY_CONFIG],
)
def test_legacy_configs_reject_qwen_tokenizer_override(config_path: Path) -> None:
    legacy = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    legacy["tokenizer"]["model"] = "/models/Qwen/Qwen3-4B-Instruct-2507"

    with pytest.raises(ValueError, match="qwen_agentic_v0.yaml.*target_model_family='qwen'"):
        validate_sft_data_prep_target_family_config(legacy, config_path=config_path)


def test_legacy_config_rejects_qwen_template_kwargs_without_qwen_family() -> None:
    legacy = yaml.safe_load(LEGACY_AGENTIC_CONFIG.read_text(encoding="utf-8"))
    legacy["chat_template"] = "tokenizer"
    legacy["chat_template_kwargs"] = dict(QWEN_SFT_CHAT_TEMPLATE_KWARGS)

    with pytest.raises(ValueError, match="Qwen thinking chat_template_kwargs"):
        validate_sft_data_prep_target_family_config(legacy, config_path=LEGACY_AGENTIC_CONFIG)


def test_qwen_packed_contract_requires_tokenizer_uri_with_training_tokenizer(
    tmp_path: Path,
) -> None:
    splits_dir = _write_qwen_packed_metadata(tmp_path, tokenizer_uri=None)

    with pytest.raises(ValueError, match="missing tokenizer_uri"):
        validate_qwen_packed_sft_chat_contract(
            splits_dir,
            tokenizer_model="/models/Qwen/Qwen3-4B-Instruct-2507",
        )


def test_qwen_packed_contract_rejects_non_qwen_tokenizer_uri_without_training_tokenizer(
    tmp_path: Path,
) -> None:
    splits_dir = _write_qwen_packed_metadata(
        tmp_path,
        tokenizer_uri="/models/Llama-3-tokenizer",
    )

    with pytest.raises(ValueError, match="tokenizer_uri must point at a Qwen"):
        validate_qwen_packed_sft_chat_contract(splits_dir)


def test_qwen_packed_contract_accepts_valid_tokenizer_uri_normalization_cases(
    tmp_path: Path,
) -> None:
    local_tokenizer = tmp_path / "Qwen3-4B-Tokenizer"
    local_tokenizer.mkdir()

    cases = [
        (str(local_tokenizer), str(local_tokenizer)),
        (f"file://{local_tokenizer}", str(local_tokenizer)),
        ("https://huggingface.co/Qwen/Qwen3-4B", "Qwen/Qwen3-4B"),
        ("hf://models/Qwen/Qwen3-4B", "Qwen/Qwen3-4B"),
    ]

    for index, (tokenizer_uri, tokenizer_model) in enumerate(cases):
        splits_dir = _write_qwen_packed_metadata(
            tmp_path / f"case_{index}",
            tokenizer_uri=tokenizer_uri,
        )

        assert (
            validate_qwen_packed_sft_chat_contract(
                splits_dir,
                tokenizer_model=tokenizer_model,
            )
            == splits_dir / "metadata.json"
        )
