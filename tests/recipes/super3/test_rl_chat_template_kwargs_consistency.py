"""Regression: all 4 super3 RL stage configs must declare the same
super3 chat-template rendering contract.

Before PR C (chat-template consistency review follow-up), only SWE1
and SWE2 explicitly set ``chat_template_kwargs`` inside
``http_server_serving_chat_kwargs``. RLVR1 and RLHF inherited the
super3.jinja defaults silently, so the multi-turn history-truncation
behavior diverged across stages (SWE1/SWE2: preserve prior thinking;
RLVR1/RLHF: truncate to ``<think></think>``). This was a real
cross-stage inconsistency on the very kwargs the model is trained on.

PR C unifies all 4 stages on
``{enable_thinking: true, truncate_history_thinking: false}`` —
matching SWE1/SWE2's original multi-turn agentic choice. Single-turn
flows (RLVR1 math/code, RLHF preference comparison) see the kwarg as
a no-op because no prior assistant turn carries ``<think>`` content
today.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[3]

RL_STAGE_CONFIGS = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/default.yaml",
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage2_swe1/config/default.yaml",
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage2_swe2/config/default.yaml",
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml",
)

EXPECTED_KWARGS = {
    "enable_thinking": True,
    "truncate_history_thinking": False,
}


def _http_chat_template_kwargs(config_path: Path) -> dict:
    """Return the chat_template_kwargs from a stage RL config's vLLM
    http_server_serving_chat_kwargs block.
    """
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config_path}: top-level must be a mapping"
    policy = data.get("policy")
    assert isinstance(policy, dict), f"{config_path}: missing policy block"
    generation = policy.get("generation")
    assert isinstance(generation, dict), (
        f"{config_path}: missing policy.generation block"
    )
    vllm_cfg = generation.get("vllm_cfg")
    assert isinstance(vllm_cfg, dict), (
        f"{config_path}: missing policy.generation.vllm_cfg block"
    )
    http_chat = vllm_cfg.get("http_server_serving_chat_kwargs")
    assert isinstance(http_chat, dict), (
        f"{config_path}: missing policy.generation.vllm_cfg."
        "http_server_serving_chat_kwargs block"
    )
    kwargs = http_chat.get("chat_template_kwargs")
    assert isinstance(kwargs, dict), (
        f"{config_path}: chat_template_kwargs must be a mapping inside "
        "http_server_serving_chat_kwargs (PR C: pinned so RL stages "
        "don't silently inherit different super3.jinja defaults)"
    )
    return kwargs


@pytest.mark.parametrize(
    "config_path", RL_STAGE_CONFIGS, ids=lambda p: p.parent.parent.name
)
def test_rl_stage_pins_unified_chat_template_kwargs(config_path: Path) -> None:
    kwargs = _http_chat_template_kwargs(config_path)
    for key, expected in EXPECTED_KWARGS.items():
        assert key in kwargs, f"{config_path}: missing chat_template_kwargs.{key}"
        assert kwargs[key] is expected, (
            f"{config_path}: chat_template_kwargs.{key}={kwargs[key]!r} "
            f"diverges from the unified PR C contract ({key}={expected!r})"
        )


def test_all_four_rl_stages_agree_on_chat_template_kwargs() -> None:
    """Cross-stage consistency: every RL stage uses the same kwargs.
    Drift here is the bug, not the values."""
    per_stage_kwargs = {
        config_path.parent.parent.name: tuple(
            sorted(_http_chat_template_kwargs(config_path).items())
        )
        for config_path in RL_STAGE_CONFIGS
    }
    distinct = set(per_stage_kwargs.values())
    assert len(distinct) == 1, (
        "RL stages disagree on chat_template_kwargs: "
        + "; ".join(
            f"{name}={dict(items)}" for name, items in per_stage_kwargs.items()
        )
    )
