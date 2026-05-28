"""Regression: Super3 GenRM vLLM servers use the Nano3 reasoning parser.

The rollout policy already pins the Qwen/Nemotron serving contract to
``nano_v3`` plus the Nano3 parser plugin. GenRM/reward model servers that ask
Nemo Gym to parse reasoning must use that same contract instead of drifting
back to vLLM's built-in ``deepseek_r1`` parser.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]

CONFIGS = {
    "stage1_rlvr": REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/default.yaml",
    "stage3_rlhf": REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml",
}

EXPECTED_REASONING_PARSER = "nano_v3"
EXPECTED_REASONING_PARSER_PLUGIN = "nemo_rl/utils/nano_v3_reasoning_parser.py"
EXPECTED_SERVER_ARGS_FIELDS = {
    "reasoning_parser": EXPECTED_REASONING_PARSER,
    "reasoning_parser_plugin": EXPECTED_REASONING_PARSER_PLUGIN,
}


def _config_data(config_path: Path) -> dict[str, Any]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config_path}: top-level config must be a mapping"
    return data


def _policy_http_serving_kwargs(config_path: Path) -> dict[str, Any]:
    data = _config_data(config_path)
    policy = data.get("policy")
    assert isinstance(policy, dict), f"{config_path}: missing policy block"
    generation = policy.get("generation")
    assert isinstance(generation, dict), f"{config_path}: missing policy.generation"
    vllm_cfg = generation.get("vllm_cfg")
    assert isinstance(vllm_cfg, dict), f"{config_path}: missing generation.vllm_cfg"
    http_chat = vllm_cfg.get("http_server_serving_chat_kwargs")
    assert isinstance(http_chat, dict), (
        f"{config_path}: missing http_server_serving_chat_kwargs"
    )
    return http_chat


def _nemo_gym_config(config_path: Path) -> dict[str, Any]:
    data = _config_data(config_path)
    env = data.get("env")
    assert isinstance(env, dict), f"{config_path}: missing env block"
    nemo_gym = env.get("nemo_gym")
    assert isinstance(nemo_gym, dict), f"{config_path}: missing env.nemo_gym block"
    return nemo_gym


def _iter_vllm_models(
    node: Any, path: tuple[str, ...] = ()
) -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        responses_api_models = node.get("responses_api_models")
        if isinstance(responses_api_models, dict):
            vllm_model = responses_api_models.get("vllm_model")
            if isinstance(vllm_model, dict):
                yield (
                    ".".join((*path, "responses_api_models", "vllm_model")),
                    vllm_model,
                )

        for key, value in node.items():
            yield from _iter_vllm_models(value, (*path, str(key)))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _iter_vllm_models(value, (*path, str(index)))


@pytest.mark.parametrize(("config_name", "config_path"), CONFIGS.items())
def test_reasoning_parser_servers_match_policy_rollout_contract(
    config_name: str, config_path: Path
) -> None:
    http_chat = _policy_http_serving_kwargs(config_path)
    for key, expected in EXPECTED_SERVER_ARGS_FIELDS.items():
        assert http_chat.get(key) == expected, (
            f"{config_name}: policy rollout {key} must stay pinned to {expected!r}"
        )

    reasoning_servers = []
    for model_path, vllm_model in _iter_vllm_models(_nemo_gym_config(config_path)):
        if vllm_model.get("uses_reasoning_parser") is True:
            reasoning_servers.append(model_path)
            server_args = vllm_model.get("server_args")
            assert isinstance(server_args, dict), (
                f"{config_name}:{model_path}: missing server_args mapping"
            )
            for key, expected in EXPECTED_SERVER_ARGS_FIELDS.items():
                assert server_args.get(key) == expected, (
                    f"{config_name}:{model_path}: server_args.{key}="
                    f"{server_args.get(key)!r} diverges from policy rollout "
                    f"{key}={expected!r}"
                )

    assert reasoning_servers, (
        f"{config_name}: expected at least one GenRM/reward vLLM server with "
        "uses_reasoning_parser: true"
    )
