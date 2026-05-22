# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox M2 RL curriculum scaffold (task038 Session 1).

This module is local-only. It reads synthetic/local rollout traces from
``LocalRolloutStore``, estimates per-environment gaps, and turns those gaps
into deterministic sampling quotas. Cluster RL runs, live judge dispatch,
reward service routing, production rollout backends, and W&B/lineage streams
remain follow-up work.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from nemotron.recipes.super3.milestones.m2_judge_pool import JudgeResponse
from nemotron.recipes.super3.milestones.rollout_store import (
    LocalRolloutStore,
    RolloutTrace,
)


JsonDict = dict[str, Any]

DEFAULT_TARGET_REWARD = 1.0
DEFAULT_PASS_THRESHOLD = 1.0
DEFAULT_MIN_WEIGHT = 0.05
DEFAULT_COVERAGE_GAP_WEIGHT = 0.25
DEFAULT_RL_CURRICULUM_BLOCKERS = (
    "task014 real RLVR cluster smoke",
    "task021 launch path / scheduler integration",
    "task034 Session 2+ live judge model/service deployment",
    "task040 numeric pass-rate production signal beyond synthetic traces",
    "cluster smoke/full M2 RL run",
    "W&B/lineage publication",
    "production rollout store backend",
    "live reward calibration",
)


def _require_nonempty(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


@dataclass(frozen=True, order=True)
class EnvGapConfig:
    """Per-environment target and weighting policy."""

    env_id: str
    target_reward: float = DEFAULT_TARGET_REWARD
    min_rollouts: int = 1
    min_weight: float = DEFAULT_MIN_WEIGHT
    max_weight: float = 4.0
    coverage_gap_weight: float = DEFAULT_COVERAGE_GAP_WEIGHT

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        if not 0.0 <= float(self.target_reward) <= 1.0:
            raise ValueError("target_reward must be in [0, 1]")
        if int(self.min_rollouts) <= 0:
            raise ValueError("min_rollouts must be positive")
        if float(self.min_weight) < 0.0:
            raise ValueError("min_weight must be non-negative")
        if float(self.max_weight) <= 0.0:
            raise ValueError("max_weight must be positive")
        if float(self.min_weight) > float(self.max_weight):
            raise ValueError("min_weight must not exceed max_weight")
        if float(self.coverage_gap_weight) < 0.0:
            raise ValueError("coverage_gap_weight must be non-negative")

    def to_jsonable(self) -> JsonDict:
        return {
            "env_id": self.env_id,
            "target_reward": float(self.target_reward),
            "min_rollouts": int(self.min_rollouts),
            "min_weight": float(self.min_weight),
            "max_weight": float(self.max_weight),
            "coverage_gap_weight": float(self.coverage_gap_weight),
        }


@dataclass(frozen=True, order=True)
class EnvGapEstimate:
    """Per-environment gap signal used by the dynamic sampler."""

    env_id: str
    model_version: str
    rollout_count: int
    target_reward: float
    mean_reward: float | None
    pass_rate: float | None
    reward_gap: float
    coverage_gap: float
    sampling_weight: float
    judge_score_mean: float | None = None
    judge_confidence_mean: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        object.__setattr__(
            self,
            "model_version",
            _require_nonempty(self.model_version, "model_version"),
        )
        if int(self.rollout_count) < 0:
            raise ValueError("rollout_count must be non-negative")
        object.__setattr__(self, "rollout_count", int(self.rollout_count))
        object.__setattr__(self, "reward_gap", _clamp01(float(self.reward_gap)))
        object.__setattr__(self, "coverage_gap", _clamp01(float(self.coverage_gap)))
        if float(self.sampling_weight) < 0.0:
            raise ValueError("sampling_weight must be non-negative")

    def to_jsonable(self) -> JsonDict:
        return {
            "env_id": self.env_id,
            "model_version": self.model_version,
            "rollout_count": self.rollout_count,
            "target_reward": float(self.target_reward),
            "mean_reward": self.mean_reward,
            "pass_rate": self.pass_rate,
            "reward_gap": self.reward_gap,
            "coverage_gap": self.coverage_gap,
            "sampling_weight": self.sampling_weight,
            "judge_score_mean": self.judge_score_mean,
            "judge_confidence_mean": self.judge_confidence_mean,
        }


@dataclass(frozen=True, order=True)
class SamplingAllocation:
    """One deterministic sampling quota for an environment."""

    env_id: str
    quota: int
    normalized_weight: float
    sampling_weight: float
    reward_gap: float
    rollout_count: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        if int(self.quota) < 0:
            raise ValueError("quota must be non-negative")
        object.__setattr__(self, "quota", int(self.quota))

    def to_jsonable(self) -> JsonDict:
        return {
            "env_id": self.env_id,
            "quota": self.quota,
            "normalized_weight": self.normalized_weight,
            "sampling_weight": self.sampling_weight,
            "reward_gap": self.reward_gap,
            "rollout_count": self.rollout_count,
        }


@dataclass(frozen=True)
class CurriculumSamplingPlan:
    """Deterministic dynamic-sampling plan for one rollout snapshot."""

    model_version: str
    total_budget: int
    estimates: tuple[EnvGapEstimate, ...]
    allocations: tuple[SamplingAllocation, ...]
    blockers: tuple[str, ...] = field(default_factory=lambda: DEFAULT_RL_CURRICULUM_BLOCKERS)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "model_version",
            _require_nonempty(self.model_version, "model_version"),
        )
        if int(self.total_budget) <= 0:
            raise ValueError("total_budget must be positive")
        object.__setattr__(self, "total_budget", int(self.total_budget))
        if sum(allocation.quota for allocation in self.allocations) != self.total_budget:
            raise ValueError("allocation quotas must sum to total_budget")

    @property
    def env_sequence(self) -> tuple[str, ...]:
        """Expanded deterministic env schedule from the quota allocation."""

        return tuple(
            env_id
            for allocation in self.allocations
            for env_id in [allocation.env_id] * allocation.quota
        )

    def to_jsonable(self) -> JsonDict:
        return {
            "schema_version": 1,
            "kind": "m2_rl_curriculum_sampling_plan",
            "model_version": self.model_version,
            "total_budget": self.total_budget,
            "estimates": [estimate.to_jsonable() for estimate in self.estimates],
            "allocations": [allocation.to_jsonable() for allocation in self.allocations],
            "env_sequence": list(self.env_sequence),
            "blockers": list(self.blockers),
        }


def estimate_env_gaps(
    store: LocalRolloutStore,
    *,
    model_version: str,
    env_configs: Sequence[EnvGapConfig],
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
) -> tuple[EnvGapEstimate, ...]:
    """Estimate per-env reward gaps from local rollout traces."""

    model_version = _require_nonempty(model_version, "model_version")
    if not env_configs:
        raise ValueError("env_configs must contain at least one environment")
    traces_by_env = _rollouts_by_env(store, model_version=model_version)
    estimates: list[EnvGapEstimate] = []
    for config in sorted(env_configs):
        traces = traces_by_env.get(config.env_id, ())
        rewards = [float(trace.reward) for trace in traces if trace.reward is not None]
        mean_reward = _mean(rewards)
        pass_rate = (
            sum(1 for reward in rewards if reward >= pass_threshold) / len(rewards)
            if rewards
            else None
        )
        reward_gap = _clamp01(float(config.target_reward) - (mean_reward or 0.0))
        coverage_gap = _clamp01(
            (int(config.min_rollouts) - len(rewards)) / int(config.min_rollouts)
        )
        judge_scores = [_metric_float(trace, "judge_score") for trace in traces]
        judge_confidences = [_metric_float(trace, "judge_confidence") for trace in traces]
        judge_score_mean = _mean([value for value in judge_scores if value is not None])
        judge_confidence_mean = _mean(
            [value for value in judge_confidences if value is not None]
        )
        sampling_weight = min(
            float(config.max_weight),
            max(
                float(config.min_weight),
                reward_gap + coverage_gap * float(config.coverage_gap_weight),
            ),
        )
        estimates.append(
            EnvGapEstimate(
                env_id=config.env_id,
                model_version=model_version,
                rollout_count=len(rewards),
                target_reward=float(config.target_reward),
                mean_reward=mean_reward,
                pass_rate=pass_rate,
                reward_gap=reward_gap,
                coverage_gap=coverage_gap,
                sampling_weight=round(sampling_weight, 6),
                judge_score_mean=judge_score_mean,
                judge_confidence_mean=judge_confidence_mean,
            )
        )
    return tuple(estimates)


def build_dynamic_sampling_plan(
    estimates: Sequence[EnvGapEstimate],
    *,
    total_budget: int,
    min_quota_per_env: int = 0,
) -> CurriculumSamplingPlan:
    """Allocate deterministic per-env sample quotas from gap weights."""

    if not estimates:
        raise ValueError("estimates must contain at least one environment")
    if int(total_budget) <= 0:
        raise ValueError("total_budget must be positive")
    if int(min_quota_per_env) < 0:
        raise ValueError("min_quota_per_env must be non-negative")
    estimates_tuple = tuple(sorted(estimates, key=lambda estimate: estimate.env_id))
    model_versions = {estimate.model_version for estimate in estimates_tuple}
    if len(model_versions) != 1:
        raise ValueError("all estimates must use the same model_version")
    minimum_total = int(min_quota_per_env) * len(estimates_tuple)
    if minimum_total > int(total_budget):
        raise ValueError("min_quota_per_env exceeds total_budget")

    remaining = int(total_budget) - minimum_total
    weights = [max(0.0, float(estimate.sampling_weight)) for estimate in estimates_tuple]
    if sum(weights) <= 0.0:
        weights = [1.0 for _estimate in estimates_tuple]
    total_weight = sum(weights)

    exact_shares = [remaining * weight / total_weight for weight in weights]
    base_quotas = [int(share) + int(min_quota_per_env) for share in exact_shares]
    leftover = int(total_budget) - sum(base_quotas)
    remainder_order = sorted(
        range(len(estimates_tuple)),
        key=lambda idx: (
            -(exact_shares[idx] - int(exact_shares[idx])),
            -estimates_tuple[idx].reward_gap,
            estimates_tuple[idx].env_id,
        ),
    )
    for idx in remainder_order[:leftover]:
        base_quotas[idx] += 1

    allocations = []
    for estimate, weight, quota in zip(estimates_tuple, weights, base_quotas):
        allocations.append(
            SamplingAllocation(
                env_id=estimate.env_id,
                quota=quota,
                normalized_weight=round(weight / total_weight, 6),
                sampling_weight=estimate.sampling_weight,
                reward_gap=estimate.reward_gap,
                rollout_count=estimate.rollout_count,
            )
        )

    return CurriculumSamplingPlan(
        model_version=estimates_tuple[0].model_version,
        total_budget=int(total_budget),
        estimates=estimates_tuple,
        allocations=tuple(allocations),
    )


def judge_response_to_rollout_metrics(response: JudgeResponse) -> JsonDict:
    """Convert a local judge-pool response into rollout-store metrics."""

    return {
        "judge_score": response.score,
        "judge_confidence": response.confidence,
        "judge_label": response.label,
        "judge_version_key": response.judge_version.version_key,
        "judge_calibration_set_id": response.calibration_set_id,
    }


def format_curriculum_plan(plan: CurriculumSamplingPlan) -> str:
    """Render a compact Markdown report for a sampling plan."""

    lines = [
        "# M2 RL curriculum sampling plan",
        "",
        f"- Model: `{plan.model_version}`",
        f"- Total budget: `{plan.total_budget}`",
        "",
        "| Environment | Quota | Weight | Gap | Rollouts |",
        "|---|---:|---:|---:|---:|",
    ]
    estimates_by_env = {estimate.env_id: estimate for estimate in plan.estimates}
    for allocation in plan.allocations:
        estimate = estimates_by_env[allocation.env_id]
        lines.append(
            "| {env} | {quota} | {weight:.6f} | {gap:.6f} | {rollouts} |".format(
                env=allocation.env_id,
                quota=allocation.quota,
                weight=allocation.normalized_weight,
                gap=estimate.reward_gap,
                rollouts=estimate.rollout_count,
            )
        )
    lines.extend(["", "## Deferred Production Work", ""])
    for blocker in plan.blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines) + "\n"


def _rollouts_by_env(
    store: LocalRolloutStore,
    *,
    model_version: str,
) -> dict[str, tuple[RolloutTrace, ...]]:
    grouped: dict[str, list[RolloutTrace]] = {}
    for trace in store.iter_all():
        if trace.model_version != model_version:
            continue
        grouped.setdefault(trace.env_id, []).append(trace)
    return {env_id: tuple(traces) for env_id, traces in grouped.items()}


def _metric_float(trace: RolloutTrace, key: str) -> float | None:
    value = trace.metrics.get(key)
    if value is None:
        judge_response = trace.metrics.get("judge_response")
        if isinstance(judge_response, Mapping):
            nested_key = key.removeprefix("judge_")
            value = judge_response.get(nested_key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "DEFAULT_RL_CURRICULUM_BLOCKERS",
    "CurriculumSamplingPlan",
    "EnvGapConfig",
    "EnvGapEstimate",
    "SamplingAllocation",
    "build_dynamic_sampling_plan",
    "estimate_env_gaps",
    "format_curriculum_plan",
    "judge_response_to_rollout_metrics",
]
