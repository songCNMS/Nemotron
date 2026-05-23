"""Tests for task038 Session 2 reward calibration scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m2_rl_curriculum import (
    RewardCalibrationSummary,
    build_reward_calibration_summaries,
    calibrate_rollout_rewards,
    calibrate_trace_reward,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore


def _write_rollout(
    store: LocalRolloutStore,
    *,
    prompt_id: str,
    model_version: str,
    env_id: str,
    reward: float | None,
) -> None:
    store.write(
        {
            "prompt_id": prompt_id,
            "model_version": model_version,
            "env_id": env_id,
            "rollout_id": f"{model_version}:{env_id}:{prompt_id}:{reward}",
            "reward": reward,
            "trace": [
                {
                    "turn_index": 0,
                    "tool_name": "synthetic_calibration",
                    "argument_dict": {},
                    "observation_length_chars": 0,
                    "latency_ms": 1.0,
                }
            ],
            "terminal_reason": "scored" if reward is not None else "missing_reward",
            "metadata": {"source": "task038_s2"},
        }
    )


def test_reward_calibration_summaries_are_per_env_and_checkpoint(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="math-1", model_version="ckpt-a", env_id="math", reward=0.0)
    _write_rollout(store, prompt_id="math-2", model_version="ckpt-a", env_id="math", reward=1.0)
    _write_rollout(store, prompt_id="safety-1", model_version="ckpt-a", env_id="safety", reward=0.75)
    _write_rollout(store, prompt_id="math-3", model_version="ckpt-b", env_id="math", reward=0.25)
    _write_rollout(store, prompt_id="math-4", model_version="ckpt-b", env_id="math", reward=0.75)

    summaries = build_reward_calibration_summaries(
        store,
        model_versions=("ckpt-a", "ckpt-b"),
        env_ids=("math", "safety"),
    )
    by_key = {(summary.model_version, summary.env_id): summary for summary in summaries}

    assert by_key[("ckpt-a", "math")].reward_count == 2
    assert by_key[("ckpt-a", "math")].mean_reward == pytest.approx(0.5)
    assert by_key[("ckpt-a", "math")].std_reward == pytest.approx(0.5)
    assert by_key[("ckpt-b", "math")].mean_reward == pytest.approx(0.5)
    assert by_key[("ckpt-b", "math")].std_reward == pytest.approx(0.25)
    assert by_key[("ckpt-a", "safety")].zero_variance is True
    assert by_key[("ckpt-b", "safety")].missing is True
    assert by_key[("ckpt-b", "safety")].reward_count == 0


def test_calibrated_rewards_are_deterministic_and_json_serializable(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="p-low", model_version="ckpt-a", env_id="math", reward=0.0)
    _write_rollout(store, prompt_id="p-mid", model_version="ckpt-a", env_id="math", reward=0.5)
    _write_rollout(store, prompt_id="p-high", model_version="ckpt-a", env_id="math", reward=1.0)

    summaries = build_reward_calibration_summaries(
        store,
        model_versions=("ckpt-a",),
        env_ids=("math",),
    )
    calibrated = calibrate_rollout_rewards(store, summaries=summaries)
    repeat = calibrate_rollout_rewards(store, summaries=tuple(reversed(summaries)))
    by_prompt = {item.prompt_id: item for item in calibrated}

    assert [item.to_jsonable() for item in calibrated] == [
        item.to_jsonable() for item in repeat
    ]
    assert by_prompt["p-low"].normalized_reward == pytest.approx(0.0)
    assert by_prompt["p-mid"].normalized_reward == pytest.approx(0.5)
    assert by_prompt["p-high"].normalized_reward == pytest.approx(1.0)
    assert by_prompt["p-low"].z_score == pytest.approx(-1.224745, abs=1e-6)
    assert by_prompt["p-mid"].z_score == pytest.approx(0.0)
    assert by_prompt["p-high"].z_score == pytest.approx(1.224745, abs=1e-6)
    json.dumps([item.to_jsonable() for item in calibrated], sort_keys=True)


def test_zero_variance_rewards_have_stable_neutral_calibration(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="p1", model_version="ckpt-a", env_id="safety", reward=0.7)
    _write_rollout(store, prompt_id="p2", model_version="ckpt-a", env_id="safety", reward=0.7)

    summary = build_reward_calibration_summaries(
        store,
        model_versions=("ckpt-a",),
        env_ids=("safety",),
    )[0]
    calibrated = calibrate_rollout_rewards(store, summaries=(summary,))

    assert summary.zero_variance is True
    assert summary.effective_std_reward == pytest.approx(1.0)
    assert {item.z_score for item in calibrated} == {0.0}
    assert {item.normalized_reward for item in calibrated} == {0.5}


def test_missing_env_summary_is_deterministic(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)

    summary = build_reward_calibration_summaries(
        store,
        model_versions=("ckpt-a",),
        env_ids=("missing_env",),
    )[0]

    assert summary.missing is True
    assert summary.zero_variance is True
    assert summary.mean_reward is None
    assert summary.z_score(0.9) == 0.0
    assert summary.normalize(0.9) == 0.0
    assert summary.to_jsonable()["effective_std_reward"] == pytest.approx(1.0)


def test_calibrate_trace_requires_matching_summary_key(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    trace = store.write(
        {
            "prompt_id": "p1",
            "model_version": "ckpt-a",
            "env_id": "math",
            "rollout_id": "r1",
            "reward": 0.5,
            "trace": [],
        }
    )
    summary = RewardCalibrationSummary(
        env_id="safety",
        model_version="ckpt-a",
        reward_count=1,
        mean_reward=0.5,
        std_reward=1.0,
        min_reward=0.5,
        max_reward=0.5,
        zero_variance=True,
    )

    with pytest.raises(ValueError, match="keys do not match"):
        calibrate_trace_reward(trace, summary)


def test_calibration_rejects_duplicate_requested_keys(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)

    with pytest.raises(ValueError, match="model_versions"):
        build_reward_calibration_summaries(
            store,
            model_versions=("ckpt-a", "ckpt-a"),
            env_ids=("math",),
        )
    with pytest.raises(ValueError, match="env_ids"):
        build_reward_calibration_summaries(
            store,
            model_versions=("ckpt-a",),
            env_ids=("math", "math"),
        )


def test_calibration_rejects_duplicate_summary_keys(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    summary = RewardCalibrationSummary(
        env_id="math",
        model_version="ckpt-a",
        reward_count=1,
        mean_reward=0.5,
        std_reward=1.0,
        min_reward=0.5,
        max_reward=0.5,
        zero_variance=True,
    )

    with pytest.raises(ValueError, match="must be unique"):
        calibrate_rollout_rewards(store, summaries=(summary, summary))
