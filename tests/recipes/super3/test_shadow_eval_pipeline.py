"""Tests for task036 Session 1 shadow-eval pipeline scaffold."""

from __future__ import annotations

from pathlib import Path

from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore
from nemotron.recipes.super3.milestones.shadow_eval import (
    DEFAULT_SHADOW_EVAL_BLOCKERS,
    ShadowEvalExample,
    ShadowEvalPlan,
    build_synthetic_shadow_plan,
    evaluate_shadow_plan,
    format_shadow_eval_report,
)


def _write_rollout(
    store: LocalRolloutStore,
    *,
    prompt_id: str,
    model_version: str,
    env_id: str,
    reward: float,
) -> None:
    rollout_id = f"{prompt_id}:{model_version}:{env_id}:{reward}"
    store.write(
        {
            "prompt_id": prompt_id,
            "model_version": model_version,
            "env_id": env_id,
            "rollout_id": rollout_id,
            "reward": reward,
            "terminal_reason": "solved" if reward >= 1.0 else "tests_failed",
            "trace": [
                {
                    "turn_index": 0,
                    "tool_name": "synthetic_eval",
                    "argument_dict": {},
                    "observation_length_chars": 0,
                    "latency_ms": 1.0,
                }
            ],
            "metadata": {"source": "synthetic_shadow_eval"},
        }
    )


def _populate(
    store: LocalRolloutStore,
    plan: ShadowEvalPlan,
    *,
    candidate_rewards: dict[str, float] | None = None,
    baseline_rewards: dict[str, float] | None = None,
) -> None:
    candidate_rewards = candidate_rewards or {}
    baseline_rewards = baseline_rewards or {}
    for example in plan.examples:
        _write_rollout(
            store,
            prompt_id=example.prompt_id,
            model_version=plan.candidate_model_version,
            env_id=example.env_id,
            reward=candidate_rewards.get(example.prompt_id, 1.0),
        )
        _write_rollout(
            store,
            prompt_id=example.prompt_id,
            model_version=plan.baseline_model_version,
            env_id=example.env_id,
            reward=baseline_rewards.get(example.prompt_id, 1.0),
        )


def test_synthetic_shadow_plan_has_canary_and_shadow_examples() -> None:
    plan = build_synthetic_shadow_plan(
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
    )
    assert {example.split for example in plan.examples} == {"canary", "shadow"}
    assert sum(example.is_canary for example in plan.examples) == 2
    assert len({(e.prompt_id, e.env_id, e.benchmark_id) for e in plan.examples}) == len(plan.examples)
    assert all(row["gate_metric"] == "reward" for row in plan.registry_rows)


def test_shadow_eval_promotes_when_candidate_matches_baseline_and_canaries_pass(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    plan = build_synthetic_shadow_plan(
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
    )
    _populate(store, plan)

    report = evaluate_shadow_plan(store, plan)
    assert report.final_status == "promote"
    assert report.gate_decision.status == "promote"
    assert report.canary_failures == ()
    assert report.missing_candidate == ()
    assert report.missing_baseline == ()


def test_shadow_eval_holds_when_canary_threshold_fails_without_regression(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    plan = build_synthetic_shadow_plan(
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
    )
    _populate(
        store,
        plan,
        candidate_rewards={"canary-terminal-001": 0.5},
        baseline_rewards={"canary-terminal-001": 0.5},
    )

    report = evaluate_shadow_plan(store, plan)
    assert report.final_status == "hold"
    assert report.gate_decision.status == "promote"
    assert report.canary_failures == ("canary-terminal-001",)


def test_shadow_eval_rolls_back_on_critical_category_regression(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    plan = build_synthetic_shadow_plan(
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
    )
    _populate(store, plan, candidate_rewards={"canary-swe-001": 0.0})

    report = evaluate_shadow_plan(store, plan)
    assert report.final_status == "rollback"
    assert report.gate_decision.status == "rollback"
    assert "swe_repo_repair" in report.gate_decision.rollback_triggers


def test_shadow_eval_holds_on_missing_candidate_rollout(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    plan = build_synthetic_shadow_plan(
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
    )
    for example in plan.examples:
        if example.prompt_id != "shadow-browser-001":
            _write_rollout(
                store,
                prompt_id=example.prompt_id,
                model_version=plan.candidate_model_version,
                env_id=example.env_id,
                reward=1.0,
            )
        _write_rollout(
            store,
            prompt_id=example.prompt_id,
            model_version=plan.baseline_model_version,
            env_id=example.env_id,
            reward=1.0,
        )

    report = evaluate_shadow_plan(store, plan)
    assert report.final_status == "hold"
    assert report.missing_candidate == ("shadow-browser-001",)


def test_shadow_eval_can_use_custom_local_heldout_split(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    example = ShadowEvalExample(
        prompt_id="custom-heldout-001",
        env_id="browser_qa",
        benchmark_id="custom_browser",
        category="browser_search",
        split="shadow",
    )
    plan = ShadowEvalPlan(
        plan_id="custom",
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
        examples=(example,),
    )
    _populate(store, plan)

    report = evaluate_shadow_plan(store, plan)
    assert report.final_status == "promote"
    assert report.task_results[0].example.prompt_id == "custom-heldout-001"


def test_format_shadow_eval_report_includes_gate_and_deferred_blockers(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    plan = build_synthetic_shadow_plan(
        candidate_model_version="candidate@1",
        baseline_model_version="baseline@1",
    )
    _populate(store, plan)
    report = evaluate_shadow_plan(store, plan)

    text = format_shadow_eval_report(report)
    assert text.startswith("# Shadow eval decision: **PROMOTE**")
    assert "## Promotion Gate" in text
    for blocker in DEFAULT_SHADOW_EVAL_BLOCKERS:
        assert blocker in text
