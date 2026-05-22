"""Tests for task038 Session 1 M2 RL curriculum scaffold."""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m2_judge_pool import (
    JudgeRequest,
    build_default_sandbox_judge_pool,
)
from nemotron.recipes.super3.milestones.m2_rl_curriculum import (
    DEFAULT_RL_CURRICULUM_BLOCKERS,
    EnvGapConfig,
    build_dynamic_sampling_plan,
    estimate_env_gaps,
    format_curriculum_plan,
    judge_response_to_rollout_metrics,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore


MODEL = "candidate@task038"


def _write_rollout(
    store: LocalRolloutStore,
    *,
    env_id: str,
    prompt_id: str,
    reward: float,
    metrics: dict[str, object] | None = None,
) -> None:
    store.write(
        {
            "prompt_id": prompt_id,
            "model_version": MODEL,
            "env_id": env_id,
            "rollout_id": f"{env_id}:{prompt_id}:{reward}",
            "reward": reward,
            "trace": [
                {
                    "turn_index": 0,
                    "tool_name": "synthetic_curriculum",
                    "argument_dict": {},
                    "observation_length_chars": 0,
                    "latency_ms": 1.0,
                }
            ],
            "metrics": metrics or {},
            "terminal_reason": "solved" if reward >= 1.0 else "unsolved",
            "metadata": {"source": "task038_synthetic"},
        }
    )


def test_estimate_env_gaps_reads_local_rollout_store(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, env_id="easy_env", prompt_id="easy-1", reward=1.0)
    _write_rollout(store, env_id="easy_env", prompt_id="easy-2", reward=0.8)
    _write_rollout(store, env_id="hard_env", prompt_id="hard-1", reward=0.0)
    _write_rollout(store, env_id="hard_env", prompt_id="hard-2", reward=0.25)

    estimates = estimate_env_gaps(
        store,
        model_version=MODEL,
        env_configs=(
            EnvGapConfig("easy_env", min_rollouts=2),
            EnvGapConfig("hard_env", min_rollouts=2),
        ),
        pass_threshold=1.0,
    )

    by_env = {estimate.env_id: estimate for estimate in estimates}
    assert by_env["easy_env"].rollout_count == 2
    assert by_env["easy_env"].mean_reward == pytest.approx(0.9)
    assert by_env["easy_env"].pass_rate == pytest.approx(0.5)
    assert by_env["easy_env"].reward_gap == pytest.approx(0.1)
    assert by_env["hard_env"].mean_reward == pytest.approx(0.125)
    assert by_env["hard_env"].reward_gap == pytest.approx(0.875)
    assert by_env["hard_env"].sampling_weight > by_env["easy_env"].sampling_weight


def test_missing_env_gets_coverage_gap_signal(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)

    estimate = estimate_env_gaps(
        store,
        model_version=MODEL,
        env_configs=(EnvGapConfig("new_env", min_rollouts=4),),
    )[0]

    assert estimate.rollout_count == 0
    assert estimate.mean_reward is None
    assert estimate.pass_rate is None
    assert estimate.reward_gap == 1.0
    assert estimate.coverage_gap == 1.0
    assert estimate.sampling_weight == pytest.approx(1.25)


def test_judge_pool_response_can_feed_rollout_metrics(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    registry = build_default_sandbox_judge_pool()
    judge = registry.build_mock_judge(
        "safety_primary",
        score_overrides={"judge-1": {"score": 0.75, "confidence": 0.8}},
    )
    response = judge.judge(
        request=JudgeRequest(
            request_id="judge-1",
            env_id="safety_judge",
            prompt="Classify",
            candidate_response="ALLOW",
        )
    )
    _write_rollout(
        store,
        env_id="safety_judge",
        prompt_id="judge-1",
        reward=response.score,
        metrics=judge_response_to_rollout_metrics(response),
    )

    estimate = estimate_env_gaps(
        store,
        model_version=MODEL,
        env_configs=(EnvGapConfig("safety_judge"),),
    )[0]

    assert estimate.judge_score_mean == pytest.approx(0.75)
    assert estimate.judge_confidence_mean == pytest.approx(0.8)
    assert estimate.to_jsonable()["judge_score_mean"] == pytest.approx(0.75)


def test_dynamic_sampler_allocates_more_budget_to_larger_gap(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, env_id="easy_env", prompt_id="easy-1", reward=1.0)
    _write_rollout(store, env_id="hard_env", prompt_id="hard-1", reward=0.0)

    estimates = estimate_env_gaps(
        store,
        model_version=MODEL,
        env_configs=(
            EnvGapConfig("easy_env"),
            EnvGapConfig("hard_env"),
        ),
    )
    plan = build_dynamic_sampling_plan(
        estimates,
        total_budget=10,
        min_quota_per_env=1,
    )
    repeat = build_dynamic_sampling_plan(
        tuple(reversed(estimates)),
        total_budget=10,
        min_quota_per_env=1,
    )

    allocations = {item.env_id: item for item in plan.allocations}
    assert plan.to_jsonable() == repeat.to_jsonable()
    assert sum(item.quota for item in plan.allocations) == 10
    assert allocations["hard_env"].quota > allocations["easy_env"].quota
    assert plan.env_sequence.count("hard_env") == allocations["hard_env"].quota


def test_dynamic_sampler_validates_budget_and_versions(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    estimates = estimate_env_gaps(
        store,
        model_version=MODEL,
        env_configs=(EnvGapConfig("env_a"), EnvGapConfig("env_b")),
    )

    with pytest.raises(ValueError, match="min_quota_per_env"):
        build_dynamic_sampling_plan(estimates, total_budget=1, min_quota_per_env=1)

    mismatched = (
        estimates[0],
        type(estimates[1])(
            **{
                **estimates[1].to_jsonable(),
                "model_version": "other@model",
            }
        ),
    )
    with pytest.raises(ValueError, match="same model_version"):
        build_dynamic_sampling_plan(mismatched, total_budget=4)


def test_format_curriculum_plan_includes_blockers(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    estimates = estimate_env_gaps(
        store,
        model_version=MODEL,
        env_configs=(EnvGapConfig("safety_judge"),),
    )
    plan = build_dynamic_sampling_plan(estimates, total_budget=3)

    text = format_curriculum_plan(plan)

    assert "# M2 RL curriculum sampling plan" in text
    assert "safety_judge" in text
    for blocker in DEFAULT_RL_CURRICULUM_BLOCKERS:
        assert blocker in text
