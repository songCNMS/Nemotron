"""Regression: super3 eval `default.yaml` must pin chat-template kwargs.

Before PR B (chat-template consistency review follow-up), the super3
eval baskets (`stage3_eval/config/m1_basket.yaml`,
`m1_full_basket.yaml`) only listed ``tasks: [...]`` with no
``chat_template_kwargs``. The eval pipeline then silently relied on
whatever ``tokenizer.chat_template`` was saved into the checkpoint,
risking drift between training-time rendering and eval-time rendering.

The fix pins ``chat_template_kwargs`` in
``stage3_eval/config/default.yaml`` so every basket inheriting that
default gets explicit kwargs. This test locks the contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]
EVAL_DEFAULT_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage3_eval/config/default.yaml"
)


def _eval_chat_template_kwargs() -> dict:
    data = _eval_default_data()
    evaluation = data.get("evaluation")
    assert isinstance(evaluation, dict), "missing evaluation block"
    nemo_cfg = evaluation.get("nemo_evaluator_config")
    assert isinstance(nemo_cfg, dict), "missing nemo_evaluator_config"
    inner = nemo_cfg.get("config")
    assert isinstance(inner, dict), "missing nemo_evaluator_config.config"
    params = inner.get("params")
    assert isinstance(params, dict), "missing nemo_evaluator_config.config.params"
    extra = params.get("extra")
    assert isinstance(extra, dict), (
        "missing nemo_evaluator_config.config.params.extra"
    )
    kwargs = extra.get("chat_template_kwargs")
    assert isinstance(kwargs, dict), (
        "chat_template_kwargs must be a mapping under "
        "evaluation.nemo_evaluator_config.config.params.extra "
        "(PR B: pinned so eval doesn't silently inherit from the "
        "checkpoint's saved tokenizer config)"
    )
    return kwargs


def _eval_default_data() -> dict:
    data = yaml.safe_load(EVAL_DEFAULT_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "eval default must load as a mapping"
    return data


def _qwen_chat_contract() -> dict:
    contract = _eval_default_data().get("qwen_chat_contract")
    assert isinstance(contract, dict), "missing qwen_chat_contract audit block"
    return contract


def _eval_default_endpoints() -> dict:
    deployment = _eval_default_data().get("deployment")
    assert isinstance(deployment, dict), "missing deployment block"
    endpoints = deployment.get("endpoints")
    assert isinstance(endpoints, dict), "missing deployment.endpoints block"
    return endpoints


def test_eval_default_pins_enable_thinking() -> None:
    kwargs = _eval_chat_template_kwargs()
    assert "enable_thinking" in kwargs, (
        "eval default must pin enable_thinking (PR B)"
    )
    assert isinstance(kwargs["enable_thinking"], bool), (
        "enable_thinking must be a bool"
    )


def test_eval_default_pins_truncate_history_thinking() -> None:
    kwargs = _eval_chat_template_kwargs()
    assert "truncate_history_thinking" in kwargs, (
        "eval default must pin truncate_history_thinking (PR B)"
    )
    assert isinstance(kwargs["truncate_history_thinking"], bool), (
        "truncate_history_thinking must be a bool"
    )


def test_eval_default_values_match_unified_rl_contract() -> None:
    """After PR D, every super3 RL stage AND the eval default share
    the same contract: {enable_thinking: false,
    truncate_history_thinking: false}. enable_thinking=false matches
    SFT-time rendering — no M0/M1 converter sets `reasoning_content`
    today, and `assistant_for_reasoning` puts the CoT in content body
    (not inside `<think>...</think>` blocks), so the SFT-trained model
    only ever sees `<|im_start|>assistant\\n<think></think>` (closed
    empty) as the assistant turn start. truncate_history_thinking=false
    matches SWE1/SWE2's multi-turn agentic choice; no-op for single-
    turn evals. Revisit if a follow-up PR carries `reasoning_content`
    through M0/M1 supervision builders. See
    docs/chat-template-consistency-review.md PR D."""
    kwargs = _eval_chat_template_kwargs()
    assert kwargs["enable_thinking"] is False, (
        "PR D: every RL stage uses enable_thinking=false to match SFT; "
        "eval mirrors. Was True under PR B+C; flipped to False in PR D."
    )
    assert kwargs["truncate_history_thinking"] is False, (
        "PR C: every RL stage uses truncate_history_thinking=false; "
        "eval mirrors."
    )


def test_eval_qwen_contract_matches_eval_extra_kwargs() -> None:
    kwargs = _eval_chat_template_kwargs()
    contract = _qwen_chat_contract()

    assert contract["target_family"] == "qwen"
    assert contract["sft"]["chat_template"] == "tokenizer"
    assert contract["sft"]["chat_template_kwargs"] == kwargs
    assert contract["eval"]["extra_chat_template_kwargs"] == kwargs


def test_eval_default_uses_slashless_openai_routes() -> None:
    endpoints = _eval_default_endpoints()

    assert endpoints["chat"] == "/v1/chat/completions"
    assert endpoints["completions"] == "/v1/completions"
    assert not endpoints["chat"].endswith("/")
    assert not endpoints["completions"].endswith("/")


def test_eval_qwen_contract_calls_out_non_chat_and_parser_sensitive_tasks() -> None:
    task_audit = _qwen_chat_contract()["task_audit"]

    assert "ifbench.ifbench" in task_audit["valid_qwen_chat_tasks"]
    assert (
        "livecodebench.codegeneration_release_latest"
        in task_audit["completion_or_non_chat_prompt_tasks"]
    )
    assert (
        "simple_evals.AIME_2025"
        in task_audit["short_generation_cap_or_parser_sensitive_tasks"]
    )
