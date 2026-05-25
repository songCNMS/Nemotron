"""Tests for task038 Session 3 judge ensemble dispatcher scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m2_judge_pool import (
    build_default_sandbox_judge_pool,
)
from nemotron.recipes.super3.milestones.m2_rl_curriculum import (
    EnvGapConfig,
    EnvJudgeRoutingPolicy,
    build_default_env_judge_routing_policies,
    dispatch_judge_ensembles_for_rollouts,
    estimate_env_gaps,
    judge_ensemble_result_to_rollout_metrics,
    rollout_trace_to_judge_request,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore


MODEL = "candidate@task038-s3"


def _write_rollout(
    store: LocalRolloutStore,
    *,
    prompt_id: str,
    env_id: str,
    rollout_id: str,
    model_version: str = MODEL,
    metadata: dict[str, object] | None = None,
) -> None:
    store.write(
        {
            "prompt_id": prompt_id,
            "model_version": model_version,
            "env_id": env_id,
            "rollout_id": rollout_id,
            "trace": [
                {
                    "turn_index": 0,
                    "tool_name": "synthetic_rollout",
                    "argument_dict": {},
                    "observation": f"answer for {prompt_id}",
                    "observation_length_chars": 12,
                    "latency_ms": 1.0,
                }
            ],
            "terminal_reason": "needs_judge",
            "metadata": {
                "prompt": f"Prompt {prompt_id}",
                "candidate_response": f"Candidate {prompt_id}",
                "reference_response": f"Reference {prompt_id}",
                **(metadata or {}),
            },
        }
    )


def test_dispatch_routes_rollouts_through_per_env_mock_ensembles(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="safe-1", env_id="safety_judge", rollout_id="roll-safe")
    _write_rollout(store, prompt_id="if-1", env_id="multilingual_ifeval", rollout_id="roll-if")
    registry = build_default_sandbox_judge_pool()
    policies = build_default_env_judge_routing_policies()

    dispatched = dispatch_judge_ensembles_for_rollouts(
        store,
        registry=registry,
        routing_policies=policies,
        model_version=MODEL,
        score_overrides={
            "safety_primary": {"roll-safe": {"score": 0.9, "confidence": 0.8}},
            "genrm_primary": {
                "roll-safe": {"score": 0.7, "confidence": 0.6},
                "roll-if": {"score": 0.2, "confidence": 0.7},
            },
            "if_primary": {"roll-if": {"score": 0.4, "confidence": 0.6}},
        },
    )
    repeat = dispatch_judge_ensembles_for_rollouts(
        store,
        registry=registry,
        routing_policies=tuple(reversed(policies)),
        model_version=MODEL,
        score_overrides={
            "safety_primary": {"roll-safe": {"score": 0.9, "confidence": 0.8}},
            "genrm_primary": {
                "roll-safe": {"score": 0.7, "confidence": 0.6},
                "roll-if": {"score": 0.2, "confidence": 0.7},
            },
            "if_primary": {"roll-if": {"score": 0.4, "confidence": 0.6}},
        },
    )

    by_rollout = {record.rollout_id: record for record in dispatched}
    assert [record.to_jsonable() for record in dispatched] == [
        record.to_jsonable() for record in repeat
    ]
    assert by_rollout["roll-safe"].reward == pytest.approx(0.8)
    assert by_rollout["roll-safe"].result.label == "pass"
    assert by_rollout["roll-safe"].result.judge_version_keys == (
        "genrm_compare@mock-s1",
        "safety_judge@mock-s1",
    )
    assert by_rollout["roll-if"].reward == pytest.approx(0.3)
    assert by_rollout["roll-if"].result.label == "fail"
    assert by_rollout["roll-if"].rollout_metrics["judge_routing_refs"] == [
        "if_primary",
        "genrm_primary",
    ]
    json.dumps([record.to_jsonable() for record in dispatched], sort_keys=True)


def test_dispatch_metrics_feed_existing_gap_estimator(tmp_path: Path) -> None:
    raw_store = LocalRolloutStore(tmp_path / "raw")
    scored_store = LocalRolloutStore(tmp_path / "scored")
    _write_rollout(raw_store, prompt_id="safe-1", env_id="safety_judge", rollout_id="roll-safe")
    dispatch = dispatch_judge_ensembles_for_rollouts(
        raw_store,
        routing_policies=(
            EnvJudgeRoutingPolicy(
                env_id="safety_judge",
                judge_refs=("safety_primary", "genrm_primary"),
            ),
        ),
        score_overrides={
            "safety_primary": {"roll-safe": {"score": 0.5, "confidence": 0.6}},
            "genrm_primary": {"roll-safe": {"score": 0.7, "confidence": 0.8}},
        },
    )[0]
    scored_store.write(
        {
            "prompt_id": dispatch.prompt_id,
            "model_version": dispatch.model_version,
            "env_id": dispatch.env_id,
            "rollout_id": "scored-roll-safe",
            "reward": dispatch.reward,
            "metrics": dispatch.rollout_metrics,
            "trace": [],
        }
    )

    estimate = estimate_env_gaps(
        scored_store,
        model_version=MODEL,
        env_configs=(EnvGapConfig("safety_judge"),),
    )[0]

    assert estimate.mean_reward == pytest.approx(0.6)
    assert estimate.judge_score_mean == pytest.approx(0.6)
    assert estimate.judge_confidence_mean == pytest.approx(0.7)


def test_rollout_trace_to_judge_request_uses_metadata_and_trace_fallbacks(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(
        store,
        prompt_id="p1",
        env_id="safety_judge",
        rollout_id="roll-fallback",
        metadata={"candidate_response": ""},
    )
    trace = store.get_by_rollout_id("roll-fallback")
    assert trace is not None

    request = rollout_trace_to_judge_request(
        trace,
        routing_policy=EnvJudgeRoutingPolicy(
            env_id="safety_judge",
            judge_refs=("safety_primary",),
            rubric="Prefer safe aligned answers.",
        ),
    )

    assert request.request_id == "roll-fallback"
    assert request.env_id == "safety_judge"
    assert request.prompt == "Prompt p1"
    assert request.candidate_response == "answer for p1"
    assert request.reference_response == "Reference p1"
    assert request.rubric == "Prefer safe aligned answers."


def test_dispatch_validates_missing_and_duplicate_policies(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="safe-1", env_id="safety_judge", rollout_id="roll-safe")

    with pytest.raises(KeyError, match="no judge routing policy"):
        dispatch_judge_ensembles_for_rollouts(
            store,
            routing_policies=(
                EnvJudgeRoutingPolicy(env_id="other_env", judge_refs=("safety_primary",)),
            ),
        )
    assert (
        dispatch_judge_ensembles_for_rollouts(
            store,
            routing_policies=(
                EnvJudgeRoutingPolicy(env_id="other_env", judge_refs=("safety_primary",)),
            ),
            strict=False,
        )
        == ()
    )
    with pytest.raises(ValueError, match="unique by env_id"):
        dispatch_judge_ensembles_for_rollouts(
            store,
            routing_policies=(
                EnvJudgeRoutingPolicy(env_id="safety_judge", judge_refs=("safety_primary",)),
                EnvJudgeRoutingPolicy(env_id="safety_judge", judge_refs=("genrm_primary",)),
            ),
        )
    with pytest.raises(ValueError, match="judge_refs"):
        EnvJudgeRoutingPolicy(env_id="safety_judge", judge_refs=("safety_primary", "safety_primary"))


def test_dispatch_accepts_generator_routing_policies(tmp_path: Path) -> None:
    """Regression: `_routing_policies_by_env` previously iterated the
    sequence twice (once via dict comprehension, once via `len(tuple(...))`
    for the dedup check). If a caller passed a generator, the second
    iteration drained to empty and the dedup check incorrectly raised
    "must be unique by env_id". Fix: materialize once."""
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="safe-1", env_id="safety_judge", rollout_id="roll-safe")

    def _generator():
        yield EnvJudgeRoutingPolicy(env_id="safety_judge", judge_refs=("safety_primary",))

    # Generator (single-pass) used to trigger spurious "must be unique"
    # ValueError. With the fix it dispatches normally.
    records = dispatch_judge_ensembles_for_rollouts(
        store,
        routing_policies=_generator(),
    )
    assert len(records) == 1
    assert records[0].env_id == "safety_judge"


def test_judge_ensemble_result_to_rollout_metrics_is_jsonable(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    _write_rollout(store, prompt_id="safe-1", env_id="safety_judge", rollout_id="roll-safe")
    record = dispatch_judge_ensembles_for_rollouts(
        store,
        routing_policies=(
            EnvJudgeRoutingPolicy(env_id="safety_judge", judge_refs=("safety_primary",)),
        ),
        score_overrides={
            "safety_primary": {"roll-safe": {"score": 1.0, "confidence": 0.9}},
        },
    )[0]

    metrics = judge_ensemble_result_to_rollout_metrics(
        record.result,
        routing_policy=record.routing_policy,
    )

    assert metrics["judge_score"] == pytest.approx(1.0)
    assert metrics["judge_confidence"] == pytest.approx(0.9)
    assert metrics["judge_label"] == "pass"
    assert metrics["judge_calibration_set_ids"] == ["safety_calibration_s1"]
    json.dumps(metrics, sort_keys=True)
