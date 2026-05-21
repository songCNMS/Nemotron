# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Local/synthetic shadow-eval pipeline scaffold (task036 Session 1).

This module is intentionally sandbox-only. It reads local rollout traces
through the task032 ``LocalRolloutStore`` schema, evaluates canary
thresholds, then reuses the M1 promotion gate for category regression
logic. Real checkpoint promotion, cluster evaluation, W&B/lineage
publishing, and production shadow split execution remain follow-up work.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from nemotron.recipes.super3.milestones.m1_eval_basket.promotion_gate import (
    DEFAULT_CATEGORY_REGRESSION_THRESHOLD,
    DEFAULT_ROLLBACK_CATEGORIES,
    DEFAULT_WEIGHTED_PARITY_THRESHOLD,
    PromotionDecision,
    evaluate_promotion_gate,
    format_gate_report,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore, RolloutTrace


JsonDict = dict[str, Any]

SHADOW_STATUS_PROMOTE = "promote"
SHADOW_STATUS_HOLD = "hold"
SHADOW_STATUS_ROLLBACK = "rollback"

DEFAULT_CANARY_MIN_SCORE = 1.0
DEFAULT_SHADOW_EVAL_BLOCKERS = (
    "real checkpoint promotion",
    "live cluster eval",
    "W&B/lineage publishing",
    "production shadow split execution",
)


def _require_nonempty(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


@dataclass(frozen=True, order=True)
class ShadowEvalExample:
    """One held-out canary or shadow-eval prompt descriptor."""

    prompt_id: str
    env_id: str
    benchmark_id: str
    category: str
    gate_metric: str = "reward"
    split: str = "shadow"
    is_canary: bool = False
    min_score: float | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.prompt_id, "prompt_id")
        _require_nonempty(self.env_id, "env_id")
        _require_nonempty(self.benchmark_id, "benchmark_id")
        _require_nonempty(self.category, "category")
        _require_nonempty(self.gate_metric, "gate_metric")
        _require_nonempty(self.split, "split")
        if self.min_score is not None:
            float(self.min_score)

    def registry_row(self) -> JsonDict:
        return {
            "benchmark_id": self.benchmark_id,
            "category": self.category,
            "gate_metric": self.gate_metric,
        }


@dataclass(frozen=True)
class ShadowEvalPlan:
    """A local shadow-eval run plan comparing candidate vs baseline."""

    plan_id: str
    candidate_model_version: str
    baseline_model_version: str
    examples: tuple[ShadowEvalExample, ...]
    canary_min_score: float = DEFAULT_CANARY_MIN_SCORE
    weighted_parity_threshold: float = DEFAULT_WEIGHTED_PARITY_THRESHOLD
    category_regression_threshold: float = DEFAULT_CATEGORY_REGRESSION_THRESHOLD
    rollback_categories: frozenset[str] = DEFAULT_ROLLBACK_CATEGORIES

    def __post_init__(self) -> None:
        _require_nonempty(self.plan_id, "plan_id")
        _require_nonempty(self.candidate_model_version, "candidate_model_version")
        _require_nonempty(self.baseline_model_version, "baseline_model_version")
        if not self.examples:
            raise ValueError("shadow eval plan requires at least one example")

    @property
    def registry_rows(self) -> list[JsonDict]:
        return [example.registry_row() for example in self.examples]


@dataclass(frozen=True)
class ShadowTaskResult:
    """Per-example rollout scores resolved from the local rollout store."""

    example: ShadowEvalExample
    candidate_score: float | None
    baseline_score: float | None
    candidate_rollout_id: str | None = None
    baseline_rollout_id: str | None = None

    @property
    def canary_threshold(self) -> float | None:
        if not self.example.is_canary:
            return None
        if self.example.min_score is not None:
            return float(self.example.min_score)
        return DEFAULT_CANARY_MIN_SCORE

    @property
    def canary_failed(self) -> bool:
        threshold = self.canary_threshold
        if threshold is None:
            return False
        return self.candidate_score is None or self.candidate_score < threshold

    def to_jsonable(self) -> JsonDict:
        return {
            "prompt_id": self.example.prompt_id,
            "env_id": self.example.env_id,
            "benchmark_id": self.example.benchmark_id,
            "category": self.example.category,
            "split": self.example.split,
            "is_canary": self.example.is_canary,
            "candidate_score": self.candidate_score,
            "baseline_score": self.baseline_score,
            "candidate_rollout_id": self.candidate_rollout_id,
            "baseline_rollout_id": self.baseline_rollout_id,
            "canary_threshold": self.canary_threshold,
            "canary_failed": self.canary_failed,
        }


@dataclass(frozen=True)
class ShadowEvalReport:
    """Combined canary + promotion gate decision."""

    plan_id: str
    candidate_model_version: str
    baseline_model_version: str
    final_status: str
    gate_decision: PromotionDecision
    task_results: tuple[ShadowTaskResult, ...]
    missing_candidate: tuple[str, ...]
    missing_baseline: tuple[str, ...]
    canary_failures: tuple[str, ...]
    blockers: tuple[str, ...] = field(default_factory=lambda: DEFAULT_SHADOW_EVAL_BLOCKERS)

    def to_jsonable(self) -> JsonDict:
        return {
            "plan_id": self.plan_id,
            "candidate_model_version": self.candidate_model_version,
            "baseline_model_version": self.baseline_model_version,
            "final_status": self.final_status,
            "gate_decision": self.gate_decision.to_jsonable(),
            "task_results": [result.to_jsonable() for result in self.task_results],
            "missing_candidate": list(self.missing_candidate),
            "missing_baseline": list(self.missing_baseline),
            "canary_failures": list(self.canary_failures),
            "blockers": list(self.blockers),
        }


def build_synthetic_shadow_plan(
    *,
    candidate_model_version: str,
    baseline_model_version: str,
    plan_id: str = "synthetic_shadow_eval_s1",
) -> ShadowEvalPlan:
    """Return a small held-out/canary split for sandbox tests."""

    examples = (
        ShadowEvalExample(
            prompt_id="canary-terminal-001",
            env_id="terminal_workplace",
            benchmark_id="shadow_terminal_canary",
            category="tool_use_terminal",
            split="canary",
            is_canary=True,
            min_score=1.0,
        ),
        ShadowEvalExample(
            prompt_id="canary-swe-001",
            env_id="swe2_openhands_trace",
            benchmark_id="shadow_swe_canary",
            category="swe_repo_repair",
            split="canary",
            is_canary=True,
            min_score=1.0,
        ),
        ShadowEvalExample(
            prompt_id="shadow-browser-001",
            env_id="browser_qa",
            benchmark_id="shadow_browser_qa",
            category="browser_search",
            split="shadow",
        ),
        ShadowEvalExample(
            prompt_id="shadow-if-001",
            env_id="multi_turn_tool_use",
            benchmark_id="shadow_multi_turn_if",
            category="multi_turn_instruction",
            split="shadow",
        ),
    )
    return ShadowEvalPlan(
        plan_id=plan_id,
        candidate_model_version=candidate_model_version,
        baseline_model_version=baseline_model_version,
        examples=examples,
    )


def evaluate_shadow_plan(
    store: LocalRolloutStore,
    plan: ShadowEvalPlan,
) -> ShadowEvalReport:
    """Evaluate a shadow plan from local rollout traces."""

    task_results = tuple(_resolve_task_result(store, plan, example) for example in plan.examples)
    current_results = {
        result.example.benchmark_id: result.candidate_score
        for result in task_results
        if result.candidate_score is not None
    }
    baseline_results = {
        result.example.benchmark_id: result.baseline_score
        for result in task_results
        if result.baseline_score is not None
    }
    gate_decision = evaluate_promotion_gate(
        current_results,
        baseline_results,
        plan.registry_rows,
        weighted_parity_threshold=plan.weighted_parity_threshold,
        category_regression_threshold=plan.category_regression_threshold,
        rollback_categories=plan.rollback_categories,
    )
    missing_candidate = tuple(
        result.example.prompt_id for result in task_results if result.candidate_score is None
    )
    missing_baseline = tuple(
        result.example.prompt_id for result in task_results if result.baseline_score is None
    )
    canary_failures = tuple(
        result.example.prompt_id for result in task_results if result.canary_failed
    )
    final_status = _combine_status(
        gate_status=gate_decision.status,
        missing_candidate=missing_candidate,
        missing_baseline=missing_baseline,
        canary_failures=canary_failures,
    )
    return ShadowEvalReport(
        plan_id=plan.plan_id,
        candidate_model_version=plan.candidate_model_version,
        baseline_model_version=plan.baseline_model_version,
        final_status=final_status,
        gate_decision=gate_decision,
        task_results=task_results,
        missing_candidate=missing_candidate,
        missing_baseline=missing_baseline,
        canary_failures=canary_failures,
    )


def format_shadow_eval_report(report: ShadowEvalReport) -> str:
    """Render the combined shadow-eval report as markdown."""

    lines = [
        f"# Shadow eval decision: **{report.final_status.upper()}**",
        "",
        f"- Plan: `{report.plan_id}`",
        f"- Candidate: `{report.candidate_model_version}`",
        f"- Baseline: `{report.baseline_model_version}`",
        "",
    ]
    if report.canary_failures:
        lines.append("**Canary failures**:")
        for prompt_id in report.canary_failures:
            lines.append(f"- `{prompt_id}`")
        lines.append("")
    if report.missing_candidate:
        lines.append("**Missing candidate rollouts**:")
        for prompt_id in report.missing_candidate:
            lines.append(f"- `{prompt_id}`")
        lines.append("")
    if report.missing_baseline:
        lines.append("**Missing baseline rollouts**:")
        for prompt_id in report.missing_baseline:
            lines.append(f"- `{prompt_id}`")
        lines.append("")
    lines.append("## Promotion Gate")
    lines.append("")
    lines.append(format_gate_report(report.gate_decision).strip())
    lines.append("")
    lines.append("## Deferred Production Work")
    lines.append("")
    for blocker in report.blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines) + "\n"


def _resolve_task_result(
    store: LocalRolloutStore,
    plan: ShadowEvalPlan,
    example: ShadowEvalExample,
) -> ShadowTaskResult:
    candidate = _latest_trace(store, example, plan.candidate_model_version)
    baseline = _latest_trace(store, example, plan.baseline_model_version)
    return ShadowTaskResult(
        example=example,
        candidate_score=candidate.reward if candidate else None,
        baseline_score=baseline.reward if baseline else None,
        candidate_rollout_id=candidate.rollout_id if candidate else None,
        baseline_rollout_id=baseline.rollout_id if baseline else None,
    )


def _latest_trace(
    store: LocalRolloutStore,
    example: ShadowEvalExample,
    model_version: str,
) -> RolloutTrace | None:
    matches = store.get(example.prompt_id, model_version, example.env_id)
    return matches[-1] if matches else None


def _combine_status(
    *,
    gate_status: str,
    missing_candidate: Sequence[str],
    missing_baseline: Sequence[str],
    canary_failures: Sequence[str],
) -> str:
    if gate_status == SHADOW_STATUS_ROLLBACK:
        return SHADOW_STATUS_ROLLBACK
    if canary_failures or missing_candidate or missing_baseline:
        return SHADOW_STATUS_HOLD
    if gate_status == SHADOW_STATUS_HOLD:
        return SHADOW_STATUS_HOLD
    return SHADOW_STATUS_PROMOTE
