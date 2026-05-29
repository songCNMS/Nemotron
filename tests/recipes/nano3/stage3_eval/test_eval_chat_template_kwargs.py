"""Static chat-template contract checks for Nano3 stage3 eval."""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[4]
EVAL_DEFAULT_PATH = (
    REPO_ROOT / "src/nemotron/recipes/nano3/stage3_eval/config/default.yaml"
)
EXPECTED_CHAT_TEMPLATE_KWARGS = {
    "enable_thinking": False,
    "truncate_history_thinking": False,
}


def _eval_default_data() -> dict:
    data = yaml.safe_load(EVAL_DEFAULT_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Nano3 eval default must load as a mapping"
    return data


def _eval_extra() -> dict:
    evaluation = _eval_default_data().get("evaluation")
    assert isinstance(evaluation, dict), "missing evaluation block"
    nemo_cfg = evaluation.get("nemo_evaluator_config")
    assert isinstance(nemo_cfg, dict), "missing nemo_evaluator_config block"
    config = nemo_cfg.get("config")
    assert isinstance(config, dict), "missing nemo_evaluator_config.config"
    params = config.get("params")
    assert isinstance(params, dict), "missing nemo_evaluator_config.config.params"
    extra = params.get("extra")
    assert isinstance(extra, dict), "missing params.extra block"
    return extra


def _eval_default_endpoints() -> dict:
    deployment = _eval_default_data().get("deployment")
    assert isinstance(deployment, dict), "missing deployment block"
    endpoints = deployment.get("endpoints")
    assert isinstance(endpoints, dict), "missing deployment.endpoints block"
    return endpoints


def test_nano3_eval_default_pins_chat_template_kwargs() -> None:
    kwargs = _eval_extra().get("chat_template_kwargs")

    assert isinstance(kwargs, dict)
    assert kwargs == EXPECTED_CHAT_TEMPLATE_KWARGS
    assert all(isinstance(value, bool) for value in kwargs.values())


def test_nano3_eval_default_keeps_tokenizer_fields_intact() -> None:
    extra = _eval_extra()

    assert extra["tokenizer"] == "${deployment.checkpoint_path}/tokenizer"
    assert extra["tokenizer_backend"] == "huggingface"


def test_nano3_eval_default_uses_slashless_openai_routes() -> None:
    endpoints = _eval_default_endpoints()

    assert endpoints["chat"] == "/v1/chat/completions"
    assert endpoints["completions"] == "/v1/completions"
    assert not endpoints["chat"].endswith("/")
    assert not endpoints["completions"].endswith("/")


def test_nano3_eval_task_list_is_unchanged_by_chat_contract_pin() -> None:
    tasks = _eval_default_data()["evaluation"]["tasks"]

    assert [task["name"] for task in tasks] == [
        "adlr_mmlu",
        "adlr_arc_challenge_llama_25_shot",
        "adlr_winogrande_5_shot",
        "hellaswag",
        "openbookqa",
    ]
