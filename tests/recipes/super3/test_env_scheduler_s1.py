"""Tests for task033 Session 1 sandbox env scheduler scaffold."""

from __future__ import annotations

from pathlib import Path

from nemotron.recipes.super3.milestones.m2_env_scheduler import (
    EnvBackpressure,
    EnvQuota,
    EnvSchedulerConfig,
    QueueName,
    SandboxEnvScheduler,
    SchedulerItem,
    classify_env_queue,
    summarize_rollout_backpressure,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore


def test_slow_envs_route_to_slow_queue_and_fast_envs_stay_normal() -> None:
    assert classify_env_queue("swe2_openhands_trace") == QueueName.SLOW
    assert classify_env_queue("browser_qa") == QueueName.SLOW
    assert classify_env_queue("gui_desktop_control") == QueueName.SLOW
    assert classify_env_queue("math_reasoning_numeric") == QueueName.NORMAL

    scheduler = SandboxEnvScheduler(
        quotas={
            "browser_qa": EnvQuota("browser_qa", max_in_flight=1),
            "math_reasoning_numeric": EnvQuota("math_reasoning_numeric", max_in_flight=4),
        }
    )

    slow_decision = scheduler.choose_next(
        [
            SchedulerItem(
                prompt_id="browse-1",
                model_version="model-a",
                env_id="browser_qa",
            )
        ]
    )
    assert slow_decision.should_schedule
    assert slow_decision.queue == QueueName.SLOW

    fast_decision = scheduler.choose_next(
        [
            SchedulerItem(
                prompt_id="math-1",
                model_version="model-a",
                env_id="math_reasoning_numeric",
            )
        ]
    )
    assert fast_decision.should_schedule
    assert fast_decision.queue == QueueName.NORMAL


def test_quota_exhaustion_changes_next_scheduling_decision() -> None:
    items = [
        SchedulerItem(
            prompt_id="math-high-priority",
            model_version="model-a",
            env_id="math_reasoning_numeric",
            priority=10,
        ),
        SchedulerItem(
            prompt_id="swe-lower-priority",
            model_version="model-a",
            env_id="swe2_openhands_trace",
            priority=1,
        ),
    ]
    quotas = {
        "math_reasoning_numeric": EnvQuota("math_reasoning_numeric", max_in_flight=1),
        "swe2_openhands_trace": EnvQuota("swe2_openhands_trace", max_in_flight=1),
    }

    unconstrained = SandboxEnvScheduler(quotas=quotas).choose_next(items)
    assert unconstrained.item is not None
    assert unconstrained.item.prompt_id == "math-high-priority"

    constrained = SandboxEnvScheduler(
        quotas=quotas,
        signals={
            "math_reasoning_numeric": EnvBackpressure(
                env_id="math_reasoning_numeric",
                in_flight=1,
            )
        },
    ).choose_next(items)

    assert constrained.should_schedule
    assert constrained.item is not None
    assert constrained.item.prompt_id == "swe-lower-priority"
    assert constrained.queue == QueueName.SLOW
    assert constrained.skipped == (
        {
            "prompt_id": "math-high-priority",
            "env_id": "math_reasoning_numeric",
            "queue": "normal",
            "reason": "backpressure",
            "backpressure_reasons": ["in_flight_quota_exhausted"],
        },
    )


def test_pending_backpressure_defers_when_no_candidate_is_eligible() -> None:
    scheduler = SandboxEnvScheduler(
        quotas={"browser_qa": EnvQuota("browser_qa", max_in_flight=2, max_pending=3)},
        signals={"browser_qa": EnvBackpressure("browser_qa", pending=3)},
    )

    decision = scheduler.choose_next(
        [
            {
                "prompt_id": "browse-1",
                "model_version": "model-a",
                "env_id": "browser_qa",
                "priority": 5,
            }
        ],
        target_queue="slow",
    )

    assert not decision.should_schedule
    assert decision.reason == "no_eligible_candidates"
    assert decision.queue == QueueName.SLOW
    assert decision.skipped[0]["backpressure_reasons"] == ["pending_quota_exhausted"]


def test_deterministic_tiebreaking_uses_priority_sequence_and_ids() -> None:
    scheduler = SandboxEnvScheduler()
    items = [
        SchedulerItem("prompt-b", "model-a", "math_reasoning_numeric", priority=2, sequence=1),
        SchedulerItem("prompt-a", "model-a", "math_reasoning_numeric", priority=2, sequence=1),
        SchedulerItem("prompt-c", "model-a", "terminal_workplace", priority=2, sequence=0),
        SchedulerItem("prompt-d", "model-a", "math_reasoning_numeric", priority=1, sequence=0),
    ]

    decision = scheduler.choose_next(items, target_queue=QueueName.NORMAL)

    assert decision.should_schedule
    assert decision.item is not None
    assert decision.item.prompt_id == "prompt-c"


def test_rollout_store_records_seed_backpressure_signals(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(
        {
            "prompt_id": "browse-1",
            "model_version": "model-a",
            "env_id": "browser_qa",
            "rollout_id": "r1",
            "reward": 0.0,
            "terminal_reason": "timeout",
            "trace": [],
            "metrics": {"latency_ms": 5000.0},
            "metadata": {"source": "synthetic"},
        }
    )
    store.write(
        {
            "prompt_id": "browse-2",
            "model_version": "model-a",
            "env_id": "browser_qa",
            "rollout_id": "r2",
            "reward": 1.0,
            "terminal_reason": "solved",
            "trace": [],
            "metrics": {"latency_ms": 3000.0},
            "metadata": {"source": "synthetic"},
        }
    )

    signals = summarize_rollout_backpressure(
        store.iter_all(),
        in_flight_by_env={"browser_qa": 1},
        pending_by_env={"browser_qa": 2},
    )

    assert signals["browser_qa"].recent_failures == 1
    assert signals["browser_qa"].avg_latency_ms == 4000.0
    assert signals["browser_qa"].metadata["rollout_count"] == 2

    scheduler = SandboxEnvScheduler(
        quotas={"browser_qa": EnvQuota("browser_qa", max_in_flight=4, max_pending=8)},
        signals=signals,
        config=EnvSchedulerConfig(failure_backpressure_threshold=1),
    )
    state = scheduler.env_state("browser_qa")

    assert state.queue == QueueName.SLOW
    assert state.backpressure_reasons == ("recent_failures",)
    assert not state.is_available


def test_snapshot_keeps_cluster_runtime_out_of_scope() -> None:
    scheduler = SandboxEnvScheduler(
        quotas={"math_reasoning_numeric": EnvQuota("math_reasoning_numeric", max_in_flight=2)}
    )
    snapshot = scheduler.snapshot()

    assert snapshot["kind"] == "sandbox_env_scheduler"
    assert snapshot["environments"][0]["env_id"] == "math_reasoning_numeric"
    assert "Ray/NeMo-RL/vLLM/NeMo-Gym worker startup" in snapshot["out_of_scope"]
