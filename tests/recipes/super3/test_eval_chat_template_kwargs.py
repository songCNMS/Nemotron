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
    data = yaml.safe_load(EVAL_DEFAULT_PATH.read_text(encoding="utf-8"))
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


def test_eval_default_values_match_super3_template_defaults() -> None:
    """The pinned values match the super3.jinja defaults, which is also
    what RLVR1 / RLHF use today. SWE1 / SWE2 explicitly override
    `truncate_history_thinking=false` for multi-turn tool loops — those
    per-task agentic configs are expected to override on top of these
    defaults. See docs/chat-template-consistency-review.md PR B / PR C
    for the cross-stage consistency follow-up."""
    kwargs = _eval_chat_template_kwargs()
    assert kwargs["enable_thinking"] is True, (
        "PR B initial value is True (matches super3.jinja default + RL "
        "stage usage); PR D may flip this to match SFT-side rendering"
    )
    assert kwargs["truncate_history_thinking"] is True, (
        "PR B initial value is True (matches super3.jinja default + "
        "RLVR1/RLHF); PR C unifies across RL stages — until then, "
        "agentic per-task configs override to False as needed"
    )
