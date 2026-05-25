"""Regression: all 4 super3 RL stage configs must terminate generation
at the super3 chat-template assistant-turn delimiter.

Before PR A (chat-template consistency review follow-up), each of
``stage1_rlvr/default.yaml``, ``stage2_swe1/default.yaml``,
``stage2_swe2/default.yaml``, and ``stage3_rlhf/default.yaml`` shipped
``stop_strings: null``, so vLLM had nothing to terminate generation on
beyond ``eos_token_id``. task071 math-eval audit session 36 confirmed
this was already biting: 234/300 AIME generations hit the 2048-token
cap without ever emitting ``\\boxed{...}``.

The fix pins ``stop_strings: ["<|im_end|>"]`` in all 4 configs so
generation stops at the super3 chat-template assistant turn delimiter.
This test locks the policy across the 4 stages.
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

CHAT_TEMPLATE_ASSISTANT_END = "<|im_end|>"


def _generation_block(config_path: Path) -> dict:
    """Return the ``policy.generation`` block from a stage RL config."""
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{config_path}: top-level must be a mapping"
    policy = data.get("policy")
    assert isinstance(policy, dict), f"{config_path}: missing policy block"
    generation = policy.get("generation")
    assert isinstance(generation, dict), (
        f"{config_path}: missing policy.generation block"
    )
    return generation


@pytest.mark.parametrize("config_path", RL_STAGE_CONFIGS, ids=lambda p: p.parent.parent.name)
def test_rl_stage_config_terminates_at_chat_template_assistant_end(
    config_path: Path,
) -> None:
    generation = _generation_block(config_path)
    stop_strings = generation.get("stop_strings")
    assert isinstance(stop_strings, list) and stop_strings, (
        f"{config_path}: stop_strings must be a non-empty list "
        "(PR A: pinned to ['<|im_end|>'] to terminate at the super3 "
        "chat-template assistant turn delimiter)"
    )
    assert CHAT_TEMPLATE_ASSISTANT_END in stop_strings, (
        f"{config_path}: stop_strings must include {CHAT_TEMPLATE_ASSISTANT_END!r} "
        "so vLLM does not over-run the assistant turn boundary"
    )


def test_all_four_rl_stage_configs_agree_on_assistant_turn_stop() -> None:
    """Cross-stage consistency: every RL stage stops on the same delimiter
    so the model's effective generation contract is identical across RLVR,
    SWE1, SWE2, and RLHF. Drift here is the bug, not the value."""
    per_stage_stops = {
        config_path.parent.parent.name: tuple(
            _generation_block(config_path).get("stop_strings") or ()
        )
        for config_path in RL_STAGE_CONFIGS
    }
    assert len(set(per_stage_stops.values())) == 1, (
        "RL stages disagree on stop_strings: "
        + "; ".join(f"{name}={stops}" for name, stops in per_stage_stops.items())
    )
