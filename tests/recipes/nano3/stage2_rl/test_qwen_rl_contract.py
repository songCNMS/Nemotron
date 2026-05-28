"""Static Qwen RL contract checks for Nano3 stage2 configs."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIGS = {
    "default": REPO_ROOT / "src/nemotron/recipes/nano3/stage2_rl/config/default.yaml",
    "tiny": REPO_ROOT / "src/nemotron/recipes/nano3/stage2_rl/config/tiny.yaml",
}
EXPECTED_CHAT_TEMPLATE_KWARGS = {
    "enable_thinking": False,
    "truncate_history_thinking": False,
}
EXPECTED_HTTP_SERVING_FIELDS = {
    "tool_parser": "qwen3_coder",
    "reasoning_parser": "nano_v3",
    "reasoning_parser_plugin": "nemo_rl/utils/nano_v3_reasoning_parser.py",
}
ARTIFACT_SPLIT_PATTERN = re.compile(r"^\$\{art:data,([^}]+)\}$")


def _config_data(config_path: Path) -> dict:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config_path}: top-level config must be a mapping"
    return data


def _policy(config_path: Path) -> dict:
    data = _config_data(config_path)
    policy = data.get("policy")
    assert isinstance(policy, dict), f"{config_path}: missing policy block"
    return policy


def _generation(config_path: Path) -> dict:
    generation = _policy(config_path).get("generation")
    assert isinstance(generation, dict), f"{config_path}: missing policy.generation"
    return generation


def _http_chat_kwargs(config_path: Path) -> dict:
    generation = _generation(config_path)
    vllm_cfg = generation.get("vllm_cfg")
    assert isinstance(vllm_cfg, dict), f"{config_path}: missing generation.vllm_cfg"
    http_chat = vllm_cfg.get("http_server_serving_chat_kwargs")
    assert isinstance(http_chat, dict), (
        f"{config_path}: missing http_server_serving_chat_kwargs"
    )
    return http_chat


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_rl_configs_pin_tokenizer_chat_template_kwargs(
    config_name: str, config_path: Path
) -> None:
    tokenizer = _policy(config_path).get("tokenizer")
    assert isinstance(tokenizer, dict), f"{config_name}: missing tokenizer block"

    assert tokenizer.get("chat_template_kwargs") == EXPECTED_CHAT_TEMPLATE_KWARGS


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_rl_configs_pin_vllm_serving_chat_template_kwargs(
    config_name: str, config_path: Path
) -> None:
    http_chat = _http_chat_kwargs(config_path)

    assert http_chat.get("chat_template_kwargs") == EXPECTED_CHAT_TEMPLATE_KWARGS
    assert (
        _policy(config_path)["tokenizer"]["chat_template_kwargs"]
        == http_chat["chat_template_kwargs"]
    ), f"{config_name}: tokenizer and vLLM serving chat kwargs must match"


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_nano3_rl_configs_pin_qwen_stop_and_parser_contract(
    config_name: str, config_path: Path
) -> None:
    generation = _generation(config_path)
    http_chat = _http_chat_kwargs(config_path)

    assert generation.get("stop_strings") == ["<|im_end|>"]
    for key, expected in EXPECTED_HTTP_SERVING_FIELDS.items():
        assert http_chat.get(key) == expected, (
            f"{config_name}: {key} must be {expected!r}, got {http_chat.get(key)!r}"
        )


def test_nano3_tiny_and_default_share_the_qwen_rl_contract() -> None:
    default_generation = _generation(CONFIGS["default"])
    tiny_generation = _generation(CONFIGS["tiny"])
    default_http_chat = _http_chat_kwargs(CONFIGS["default"])
    tiny_http_chat = _http_chat_kwargs(CONFIGS["tiny"])

    assert (
        _policy(CONFIGS["default"])["tokenizer"]["chat_template_kwargs"]
        == _policy(CONFIGS["tiny"])["tokenizer"]["chat_template_kwargs"]
        == EXPECTED_CHAT_TEMPLATE_KWARGS
    )
    assert default_generation["stop_strings"] == tiny_generation["stop_strings"]
    for key in (*EXPECTED_HTTP_SERVING_FIELDS, "chat_template_kwargs"):
        assert default_http_chat.get(key) == tiny_http_chat.get(key), (
            f"tiny.yaml drifted from default.yaml for {key}"
        )


def test_nano3_tiny_train_and_validation_use_distinct_artifact_splits() -> None:
    data = _config_data(CONFIGS["tiny"]).get("data")
    assert isinstance(data, dict), "tiny.yaml: missing data block"

    train_path = data.get("train_jsonl_fpath")
    validation_path = data.get("validation_jsonl_fpath")
    train_match = ARTIFACT_SPLIT_PATTERN.match(train_path or "")
    validation_match = ARTIFACT_SPLIT_PATTERN.match(validation_path or "")

    assert train_match, f"tiny.yaml: unexpected train artifact path {train_path!r}"
    assert validation_match, (
        f"tiny.yaml: unexpected validation artifact path {validation_path!r}"
    )
    assert train_match.group(1) == "train"
    assert validation_match.group(1) == "val"
    assert train_match.group(1) != validation_match.group(1)
