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

from collections.abc import Mapping, Sequence
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
CANARY_POLICY_GROUPS = frozenset({"category", "env_id", "prompt_id"})


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
class CanaryPolicy:
    """Sandbox canary thresholds keyed by stable fixture metadata.

    ``default_min_score`` is ``None`` when the policy doesn't override
    the module default. Callers passing ``fallback_min_score`` to
    :meth:`threshold_for` only see their fallback when the policy
    has *neither* a per-key threshold nor an explicit
    ``default_min_score`` — so an explicit policy default (even one
    that happens to equal the module constant) is always respected.
    """

    default_min_score: float | None = None
    min_score_by_category: Mapping[str, float] = field(default_factory=dict)
    min_score_by_env: Mapping[str, float] = field(default_factory=dict)
    min_score_by_prompt: Mapping[str, float] = field(default_factory=dict)

    def threshold_for(
        self,
        example: ShadowEvalExample,
        *,
        fallback_min_score: float | None = None,
    ) -> float | None:
        """Resolve the canary threshold for one example.

        Precedence (highest first):
          1. ``min_score_by_prompt[example.prompt_id]``
          2. ``min_score_by_env[example.env_id]``
          3. ``min_score_by_category[example.category]``
          4. ``example.min_score`` (per-example override on the
             :class:`ShadowEvalExample`)
          5. ``self.default_min_score`` if the policy set one
          6. ``fallback_min_score`` if the caller passed one
          7. ``DEFAULT_CANARY_MIN_SCORE`` (module default)
        """

        if not example.is_canary:
            return None

        if example.prompt_id in self.min_score_by_prompt:
            return _validate_score_threshold(
                self.min_score_by_prompt[example.prompt_id],
                f"prompt threshold for {example.prompt_id}",
            )
        if example.env_id in self.min_score_by_env:
            return _validate_score_threshold(
                self.min_score_by_env[example.env_id],
                f"env threshold for {example.env_id}",
            )
        if example.category in self.min_score_by_category:
            return _validate_score_threshold(
                self.min_score_by_category[example.category],
                f"category threshold for {example.category}",
            )
        if example.min_score is not None:
            return _validate_score_threshold(
                example.min_score,
                f"example threshold for {example.prompt_id}",
            )
        if self.default_min_score is not None:
            return _validate_score_threshold(
                self.default_min_score, "default canary threshold"
            )
        if fallback_min_score is not None:
            return _validate_score_threshold(
                fallback_min_score, "fallback canary threshold"
            )
        return _validate_score_threshold(
            DEFAULT_CANARY_MIN_SCORE, "module default canary threshold"
        )

    def to_jsonable(self) -> JsonDict:
        return {
            "default_min_score": self.default_min_score,
            "min_score_by_category": dict(self.min_score_by_category),
            "min_score_by_env": dict(self.min_score_by_env),
            "min_score_by_prompt": dict(self.min_score_by_prompt),
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
    canary_policy: CanaryPolicy = field(default_factory=CanaryPolicy)

    def __post_init__(self) -> None:
        _require_nonempty(self.plan_id, "plan_id")
        _require_nonempty(self.candidate_model_version, "candidate_model_version")
        _require_nonempty(self.baseline_model_version, "baseline_model_version")
        if not self.examples:
            raise ValueError("shadow eval plan requires at least one example")

    @property
    def registry_rows(self) -> list[JsonDict]:
        return [example.registry_row() for example in self.examples]

    def canary_threshold_for(self, example: ShadowEvalExample) -> float | None:
        return self.canary_policy.threshold_for(
            example,
            fallback_min_score=self.canary_min_score,
        )


@dataclass(frozen=True)
class ShadowTaskResult:
    """Per-example rollout scores resolved from the local rollout store."""

    example: ShadowEvalExample
    candidate_score: float | None
    baseline_score: float | None
    candidate_rollout_id: str | None = None
    baseline_rollout_id: str | None = None
    canary_threshold: float | None = None

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
            "resolved_canary_thresholds": {
                result.example.prompt_id: result.canary_threshold
                for result in self.task_results
                if result.example.is_canary
            },
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


def tune_canary_policy(
    samples: Sequence[Mapping[str, object] | ShadowTaskResult],
    *,
    group_by: str = "category",
    margin: float = 0.0,
    default_min_score: float | None = DEFAULT_CANARY_MIN_SCORE,
) -> CanaryPolicy:
    """Build a deterministic sandbox canary policy from local calibration scores.

    ``default_min_score`` defaults to ``DEFAULT_CANARY_MIN_SCORE`` so the
    tuned policy carries an explicit floor that the caller's
    ``fallback_min_score`` cannot override. Pass ``None`` to leave the
    policy's default unset (so callers' fallbacks can layer underneath).
    """

    if group_by not in CANARY_POLICY_GROUPS:
        raise ValueError(f"group_by must be one of {sorted(CANARY_POLICY_GROUPS)}")
    if margin < 0:
        raise ValueError("margin must be non-negative")

    grouped: dict[str, list[float]] = {}
    for sample in samples:
        group_key = _sample_group_key(sample, group_by)
        score = _sample_score(sample)
        grouped.setdefault(group_key, []).append(score)

    tuned = {
        group_key: _clamp_score_threshold(min(scores) - margin)
        for group_key, scores in sorted(grouped.items())
    }

    kwargs: dict[str, object] = {
        "default_min_score": (
            _validate_score_threshold(default_min_score, "default_min_score")
            if default_min_score is not None
            else None
        )
    }
    if group_by == "category":
        kwargs["min_score_by_category"] = tuned
    elif group_by == "env_id":
        kwargs["min_score_by_env"] = tuned
    else:
        kwargs["min_score_by_prompt"] = tuned
    return CanaryPolicy(**kwargs)


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
    canary_results = [result for result in report.task_results if result.example.is_canary]
    if canary_results:
        lines.append("**Canary thresholds**:")
        for result in canary_results:
            lines.append(
                f"- `{result.example.prompt_id}`: "
                f"score={result.candidate_score}, threshold={result.canary_threshold}"
            )
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
        canary_threshold=plan.canary_threshold_for(example),
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


def _sample_group_key(sample: Mapping[str, object] | ShadowTaskResult, group_by: str) -> str:
    if isinstance(sample, ShadowTaskResult):
        if group_by == "category":
            return sample.example.category
        if group_by == "env_id":
            return sample.example.env_id
        return sample.example.prompt_id

    value = sample.get(group_by)
    if value is None:
        raise ValueError(f"calibration sample is missing {group_by}")
    return str(value)


def _sample_score(sample: Mapping[str, object] | ShadowTaskResult) -> float:
    if isinstance(sample, ShadowTaskResult):
        if sample.candidate_score is None:
            raise ValueError(f"calibration sample {sample.example.prompt_id} is missing candidate_score")
        return _validate_score_threshold(sample.candidate_score, f"score for {sample.example.prompt_id}")

    for key in ("score", "candidate_score", "reward"):
        if key in sample:
            return _validate_score_threshold(sample[key], f"sample {key}")
    raise ValueError("calibration sample must include score, candidate_score, or reward")


def _validate_score_threshold(value: object, label: str) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if score < 0.0 or score > 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0")
    return score


def _clamp_score_threshold(value: float) -> float:
    return max(0.0, min(1.0, value))
