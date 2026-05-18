"""Plan §5.6 acceptance gate for the RLHF KL configuration.

Roadmap §1.6 task018 names three knobs that must hold at acceptance:

  - ``reference_policy_kl_penalty == 1.0e-4``
  - ``reference_policy_kl_type == "k3"`` (Schulman k3 estimator)
  - ``use_kl_in_reward == false`` (KL applied as loss, not folded into reward)

The values currently live in ``stage2_rl/stage3_rlhf/config/default.yaml``.
This test reads that YAML directly and asserts the trio. It catches the
regression where someone edits a single knob (e.g., switches KL into the
reward) — Session 1 wants the gate to fire before a cluster run wastes a
slot.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


CONFIG_PATH = (
    Path(__file__).resolve().parents[3]
    / "src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml"
)


def _load_config() -> dict:
    assert CONFIG_PATH.is_file(), f"missing prod config: {CONFIG_PATH}"
    with CONFIG_PATH.open(encoding="utf-8") as f:
        # OmegaConf-flavored YAML; basic safe_load handles the scalar
        # values this test reads.
        return yaml.safe_load(f)


def test_rlhf_kl_penalty_is_plan_5_6_value() -> None:
    cfg = _load_config()
    # Walk the nested structure: the knob lives near the top of the file
    # (around line 98 today). We grep through everything in case rows
    # shift; the value is unique enough that the search is unambiguous.
    found = _find_scalar(cfg, "reference_policy_kl_penalty")
    assert found == pytest.approx(1.0e-4), (
        f"plan §5.6 / roadmap §1.6 acceptance expects "
        f"reference_policy_kl_penalty == 1.0e-4; got {found!r}. "
        "If this is intentional, update roadmap §1.6 + plan §5.6 first."
    )


def test_rlhf_kl_type_is_k3_schulman_estimator() -> None:
    cfg = _load_config()
    found = _find_scalar(cfg, "reference_policy_kl_type")
    assert found == "k3", (
        f"plan §5.6 calls for Schulman k3 KL estimator; got {found!r}."
    )


def test_rlhf_use_kl_in_reward_is_false() -> None:
    """KL applies as a *loss penalty*, not folded into the reward signal —
    folding it into reward would compete with the GenRM signal."""
    cfg = _load_config()
    found = _find_scalar(cfg, "use_kl_in_reward")
    assert found is False, (
        f"plan §5.6 wants KL as loss penalty, not in reward; got "
        f"use_kl_in_reward={found!r}."
    )


_MISSING = object()


def _find_scalar(node, key):
    """Walk a nested dict/list looking for the *first* matching key.

    Returns the value found, or ``_MISSING`` if absent. Sentinel approach
    so ``False`` / ``None`` / ``0`` stay distinguishable from "not found".
    """
    if isinstance(node, dict):
        if key in node:
            return node[key]
        for value in node.values():
            hit = _find_scalar(value, key)
            if hit is not _MISSING:
                return hit
    elif isinstance(node, list):
        for item in node:
            hit = _find_scalar(item, key)
            if hit is not _MISSING:
                return hit
    return _MISSING
