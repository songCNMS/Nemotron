# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox M2 RL curriculum scaffold (task038 Sessions 1-3).

This module is local-only. It reads synthetic/local rollout traces from
``LocalRolloutStore``, estimates per-environment gaps, and turns those gaps
into deterministic sampling quotas. Session 2 adds per-environment,
per-checkpoint reward calibration summaries and deterministic calibrated reward
outputs. Session 3 adds a sandbox judge-ensemble dispatcher over the task034
judge-pool mock interfaces. Cluster RL runs, live judge dispatch, reward
service routing, production rollout backends, and W&B/lineage streams remain
follow-up work.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from nemotron.recipes.super3.milestones.m2_judge_pool import (
    EnsembleVoteResult,
    JudgeRequest,
    JudgeResponse,
    JudgeVersionRegistry,
    build_default_sandbox_judge_pool,
    evaluate_ensemble,
)
from nemotron.recipes.super3.milestones.rollout_store import (
    LocalRolloutStore,
    RolloutTrace,
)


JsonDict = dict[str, Any]

DEFAULT_TARGET_REWARD = 1.0
DEFAULT_PASS_THRESHOLD = 1.0
DEFAULT_MIN_WEIGHT = 0.05
DEFAULT_COVERAGE_GAP_WEIGHT = 0.25
ZERO_VARIANCE_STD_FALLBACK = 1.0
DEFAULT_JUDGE_DECISION_THRESHOLD = 0.5
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
DEFAULT_JUDGE_DISPATCH_BLOCKERS = (
    "live GenRM/judge service deployment",
    "reward-service routing",
    "auth/secrets for live judge endpoints",
    "calibration corpora access",
    "cluster inference",
    "RL training launch",
    "W&B/lineage publication",
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


@dataclass(frozen=True, order=True)
class RewardCalibrationSummary:
    """Per-environment reward statistics for one model checkpoint."""

    env_id: str
    model_version: str
    reward_count: int
    mean_reward: float | None
    std_reward: float | None
    min_reward: float | None
    max_reward: float | None
    zero_variance: bool
    missing: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        object.__setattr__(
            self,
            "model_version",
            _require_nonempty(self.model_version, "model_version"),
        )
        if int(self.reward_count) < 0:
            raise ValueError("reward_count must be non-negative")
        object.__setattr__(self, "reward_count", int(self.reward_count))
        if self.reward_count == 0:
            object.__setattr__(self, "missing", True)
            object.__setattr__(self, "zero_variance", True)
        if self.mean_reward is None and self.reward_count > 0:
            raise ValueError("mean_reward is required when reward_count is positive")

    @property
    def normalization_range(self) -> float:
        if self.min_reward is None or self.max_reward is None:
            return 0.0
        return max(0.0, float(self.max_reward) - float(self.min_reward))

    @property
    def effective_std_reward(self) -> float:
        if self.std_reward is None or self.std_reward <= 0.0:
            return ZERO_VARIANCE_STD_FALLBACK
        return float(self.std_reward)

    def z_score(self, reward: float | None) -> float:
        if reward is None or self.mean_reward is None or self.zero_variance:
            return 0.0
        return round(
            (float(reward) - float(self.mean_reward)) / self.effective_std_reward,
            6,
        )

    def normalize(self, reward: float | None) -> float:
        if reward is None:
            return 0.0
        if self.missing:
            return 0.0
        if self.normalization_range <= 0.0:
            return 0.5
        return round(
            _clamp01((float(reward) - float(self.min_reward)) / self.normalization_range),
            6,
        )

    def to_jsonable(self) -> JsonDict:
        return {
            "env_id": self.env_id,
            "model_version": self.model_version,
            "reward_count": self.reward_count,
            "mean_reward": self.mean_reward,
            "std_reward": self.std_reward,
            "effective_std_reward": self.effective_std_reward,
            "min_reward": self.min_reward,
            "max_reward": self.max_reward,
            "normalization_range": self.normalization_range,
            "zero_variance": self.zero_variance,
            "missing": self.missing,
        }


@dataclass(frozen=True, order=True)
class CalibratedReward:
    """One rollout reward projected through an env/checkpoint calibration."""

    rollout_id: str
    prompt_id: str
    env_id: str
    model_version: str
    raw_reward: float | None
    z_score: float
    normalized_reward: float
    calibration: RewardCalibrationSummary

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rollout_id",
            _require_nonempty(self.rollout_id, "rollout_id"),
        )
        object.__setattr__(
            self,
            "prompt_id",
            _require_nonempty(self.prompt_id, "prompt_id"),
        )
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        object.__setattr__(
            self,
            "model_version",
            _require_nonempty(self.model_version, "model_version"),
        )
        object.__setattr__(self, "normalized_reward", _clamp01(float(self.normalized_reward)))

    def to_jsonable(self) -> JsonDict:
        return {
            "rollout_id": self.rollout_id,
            "prompt_id": self.prompt_id,
            "env_id": self.env_id,
            "model_version": self.model_version,
            "raw_reward": self.raw_reward,
            "z_score": self.z_score,
            "normalized_reward": self.normalized_reward,
            "calibration": self.calibration.to_jsonable(),
        }


@dataclass(frozen=True)
class EnvJudgeRoutingPolicy:
    """Per-environment judge refs and decision policy for sandbox dispatch."""

    env_id: str
    judge_refs: tuple[str, ...]
    decision_threshold: float = DEFAULT_JUDGE_DECISION_THRESHOLD
    rubric: str | None = None
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        judge_refs = _freeze_unique_strings(self.judge_refs, "judge_refs")
        if not judge_refs:
            raise ValueError("judge_refs must contain at least one judge ref")
        object.__setattr__(self, "judge_refs", judge_refs)
        threshold = float(self.decision_threshold)
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("decision_threshold must be in [0, 1]")
        object.__setattr__(self, "decision_threshold", threshold)
        if self.rubric is not None:
            object.__setattr__(self, "rubric", _require_nonempty(self.rubric, "rubric"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_jsonable(self) -> JsonDict:
        return {
            "env_id": self.env_id,
            "judge_refs": list(self.judge_refs),
            "decision_threshold": self.decision_threshold,
            "rubric": self.rubric,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class JudgeDispatchRecord:
    """One rollout judged through an environment-specific mock ensemble."""

    rollout_id: str
    prompt_id: str
    env_id: str
    model_version: str
    request: JudgeRequest
    routing_policy: EnvJudgeRoutingPolicy
    result: EnsembleVoteResult
    rollout_metrics: JsonDict
    blockers: tuple[str, ...] = DEFAULT_JUDGE_DISPATCH_BLOCKERS

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rollout_id",
            _require_nonempty(self.rollout_id, "rollout_id"),
        )
        object.__setattr__(
            self,
            "prompt_id",
            _require_nonempty(self.prompt_id, "prompt_id"),
        )
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        object.__setattr__(
            self,
            "model_version",
            _require_nonempty(self.model_version, "model_version"),
        )
        if self.request.request_id != self.rollout_id:
            raise ValueError("judge request_id must match rollout_id")
        if self.request.env_id != self.env_id:
            raise ValueError("judge request env_id must match rollout env_id")
        if self.result.request_id != self.request.request_id:
            raise ValueError("ensemble result request_id must match judge request_id")
        object.__setattr__(self, "rollout_metrics", dict(self.rollout_metrics or {}))
        object.__setattr__(self, "blockers", tuple(self.blockers))

    @property
    def reward(self) -> float:
        return self.result.aggregate_score

    def to_jsonable(self) -> JsonDict:
        return {
            "schema_version": 1,
            "kind": "m2_rl_curriculum_judge_dispatch_record",
            "rollout_id": self.rollout_id,
            "prompt_id": self.prompt_id,
            "env_id": self.env_id,
            "model_version": self.model_version,
            "reward": self.reward,
            "request": self.request.to_jsonable(),
            "routing_policy": self.routing_policy.to_jsonable(),
            "result": self.result.to_jsonable(),
            "rollout_metrics": dict(self.rollout_metrics),
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


def build_reward_calibration_summaries(
    store: LocalRolloutStore,
    *,
    model_versions: Sequence[str] | None = None,
    env_ids: Sequence[str] | None = None,
) -> tuple[RewardCalibrationSummary, ...]:
    """Build per-env/per-checkpoint reward calibration summaries.

    When ``model_versions`` and ``env_ids`` include combinations missing from
    the local rollout store, this function emits deterministic empty summaries
    with ``missing=True`` and ``zero_variance=True``.
    """

    traces = list(store.iter_all())
    requested_models = (
        _freeze_requested_values(model_versions, "model_versions")
        if model_versions is not None
        else tuple(sorted({trace.model_version for trace in traces}))
    )
    requested_envs = (
        _freeze_requested_values(env_ids, "env_ids")
        if env_ids is not None
        else tuple(sorted({trace.env_id for trace in traces}))
    )
    if not requested_models:
        raise ValueError("model_versions must contain at least one model")
    if not requested_envs:
        raise ValueError("env_ids must contain at least one environment")

    rewards_by_key: dict[tuple[str, str], list[float]] = {
        (model_version, env_id): []
        for model_version in requested_models
        for env_id in requested_envs
    }
    requested_model_set = set(requested_models)
    requested_env_set = set(requested_envs)
    for trace in traces:
        if (
            trace.model_version not in requested_model_set
            or trace.env_id not in requested_env_set
        ):
            continue
        if trace.reward is None:
            continue
        rewards_by_key.setdefault((trace.model_version, trace.env_id), []).append(
            float(trace.reward)
        )

    summaries = []
    for model_version in requested_models:
        for env_id in requested_envs:
            rewards = tuple(rewards_by_key.get((model_version, env_id), ()))
            summaries.append(_summary_from_rewards(env_id, model_version, rewards))
    return tuple(summaries)


def calibrate_rollout_rewards(
    store: LocalRolloutStore,
    *,
    summaries: Sequence[RewardCalibrationSummary],
) -> tuple[CalibratedReward, ...]:
    """Apply calibration summaries to matching local rollout traces."""

    by_key = {
        (summary.model_version, summary.env_id): summary
        for summary in summaries
    }
    if len(by_key) != len(tuple(summaries)):
        raise ValueError("calibration summaries must be unique by (model_version, env_id)")
    calibrated = []
    for trace in sorted(
        store.iter_all(),
        key=lambda item: (item.model_version, item.env_id, item.prompt_id, item.rollout_id),
    ):
        summary = by_key.get((trace.model_version, trace.env_id))
        if summary is None:
            continue
        calibrated.append(calibrate_trace_reward(trace, summary))
    return tuple(calibrated)


def calibrate_trace_reward(
    trace: RolloutTrace,
    summary: RewardCalibrationSummary,
) -> CalibratedReward:
    """Calibrate one rollout reward against its env/checkpoint summary."""

    if trace.model_version != summary.model_version or trace.env_id != summary.env_id:
        raise ValueError("trace and calibration summary keys do not match")
    reward = float(trace.reward) if trace.reward is not None else None
    return CalibratedReward(
        rollout_id=trace.rollout_id,
        prompt_id=trace.prompt_id,
        env_id=trace.env_id,
        model_version=trace.model_version,
        raw_reward=reward,
        z_score=summary.z_score(reward),
        normalized_reward=summary.normalize(reward),
        calibration=summary,
    )


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


def build_default_env_judge_routing_policies() -> tuple[EnvJudgeRoutingPolicy, ...]:
    """Return sandbox per-env judge-routing policies compatible with task034."""

    return (
        EnvJudgeRoutingPolicy(
            env_id="genrm_compare",
            judge_refs=("genrm_primary", "if_primary"),
            rubric="Score preference-comparison quality for local RL curriculum shaping.",
            metadata={"source": "task038_s3_default"},
        ),
        EnvJudgeRoutingPolicy(
            env_id="multilingual_ifeval",
            judge_refs=("if_primary", "genrm_primary"),
            rubric="Score multilingual instruction-following quality for local curriculum shaping.",
            metadata={"source": "task038_s3_default"},
        ),
        EnvJudgeRoutingPolicy(
            env_id="safety_judge",
            judge_refs=("safety_primary", "genrm_primary"),
            rubric="Score safety and alignment quality for local curriculum shaping.",
            metadata={"source": "task038_s3_default"},
        ),
    )


def rollout_trace_to_judge_request(
    trace: RolloutTrace,
    *,
    routing_policy: EnvJudgeRoutingPolicy | None = None,
) -> JudgeRequest:
    """Convert a local rollout trace into a task034 judge-pool request."""

    prompt = _first_text(
        trace.metadata,
        ("prompt", "instruction", "input"),
        default=f"prompt_id={trace.prompt_id}",
    )
    candidate_response = (
        _first_text(
            trace.metadata,
            ("candidate_response", "response", "answer", "completion"),
            default=None,
        )
        or _candidate_response_from_trace(trace)
        or trace.terminal_reason
        or f"rollout_id={trace.rollout_id}"
    )
    reference_response = _first_text(
        trace.metadata,
        ("reference_response", "reference", "expected_response"),
        default=None,
    )
    rubric = (
        (routing_policy.rubric if routing_policy is not None else None)
        or _first_text(trace.metadata, ("rubric",), default=None)
    )
    return JudgeRequest(
        request_id=trace.rollout_id,
        env_id=trace.env_id,
        prompt=prompt,
        candidate_response=candidate_response,
        reference_response=reference_response,
        rubric=rubric,
        metadata={
            "prompt_id": trace.prompt_id,
            "model_version": trace.model_version,
            "source": "task038_s3_rollout_dispatch",
        },
    )


def judge_ensemble_result_to_rollout_metrics(
    result: EnsembleVoteResult,
    *,
    routing_policy: EnvJudgeRoutingPolicy,
) -> JsonDict:
    """Convert a task034 ensemble result into rollout-store metrics."""

    calibration_set_ids = sorted(
        {
            response.calibration_set_id
            for response in result.responses
            if response.calibration_set_id is not None
        }
    )
    return {
        "judge_score": result.aggregate_score,
        "judge_confidence": result.aggregate_confidence,
        "judge_label": result.label,
        "judge_votes_by_label": dict(result.votes_by_label),
        "judge_version_keys": list(result.judge_version_keys),
        "judge_response_count": len(result.responses),
        "judge_decision_threshold": result.decision_threshold,
        "judge_decision_rule": result.decision_rule,
        "judge_routing_env_id": routing_policy.env_id,
        "judge_routing_refs": list(routing_policy.judge_refs),
        "judge_calibration_set_ids": calibration_set_ids,
    }


def dispatch_judge_ensembles_for_rollouts(
    store: LocalRolloutStore,
    *,
    registry: JudgeVersionRegistry | None = None,
    routing_policies: Sequence[EnvJudgeRoutingPolicy] | None = None,
    model_version: str | None = None,
    score_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    strict: bool = True,
) -> tuple[JudgeDispatchRecord, ...]:
    """Dispatch local rollout traces through per-env sandbox judge ensembles."""

    registry = registry or build_default_sandbox_judge_pool()
    policies_by_env = _routing_policies_by_env(
        routing_policies or build_default_env_judge_routing_policies()
    )
    requested_model_version = (
        _require_nonempty(model_version, "model_version")
        if model_version is not None
        else None
    )
    overrides = dict(score_overrides or {})
    dispatched: list[JudgeDispatchRecord] = []
    for trace in sorted(
        store.iter_all(),
        key=lambda item: (item.model_version, item.env_id, item.prompt_id, item.rollout_id),
    ):
        if requested_model_version is not None and trace.model_version != requested_model_version:
            continue
        policy = policies_by_env.get(trace.env_id)
        if policy is None:
            if strict:
                raise KeyError(f"no judge routing policy for env_id {trace.env_id!r}")
            continue
        request = rollout_trace_to_judge_request(trace, routing_policy=policy)
        judges = tuple(
            registry.build_mock_judge(ref, score_overrides=overrides.get(ref))
            for ref in policy.judge_refs
        )
        result = evaluate_ensemble(
            request,
            judges,
            decision_threshold=policy.decision_threshold,
        )
        metrics = judge_ensemble_result_to_rollout_metrics(result, routing_policy=policy)
        dispatched.append(
            JudgeDispatchRecord(
                rollout_id=trace.rollout_id,
                prompt_id=trace.prompt_id,
                env_id=trace.env_id,
                model_version=trace.model_version,
                request=request,
                routing_policy=policy,
                result=result,
                rollout_metrics=metrics,
            )
        )
    return tuple(dispatched)


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


def _freeze_requested_values(values: Sequence[str], field_name: str) -> tuple[str, ...]:
    out = tuple(_require_nonempty(value, field_name) for value in values)
    if len(set(out)) != len(out):
        raise ValueError(f"{field_name} must not contain duplicates")
    return tuple(sorted(out))


def _freeze_unique_strings(values: Sequence[str], field_name: str) -> tuple[str, ...]:
    out = tuple(_require_nonempty(value, field_name) for value in values)
    if len(set(out)) != len(out):
        raise ValueError(f"{field_name} must not contain duplicates")
    return out


def _routing_policies_by_env(
    policies: Sequence[EnvJudgeRoutingPolicy],
) -> dict[str, EnvJudgeRoutingPolicy]:
    if not policies:
        raise ValueError("routing_policies must contain at least one policy")
    by_env = {policy.env_id: policy for policy in policies}
    if len(by_env) != len(tuple(policies)):
        raise ValueError("routing_policies must be unique by env_id")
    return by_env


def _first_text(
    values: Mapping[str, Any],
    keys: Sequence[str],
    *,
    default: str | None,
) -> str | None:
    for key in keys:
        value = values.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _candidate_response_from_trace(trace: RolloutTrace) -> str | None:
    for turn in reversed(trace.trace):
        candidate = _first_text(
            turn,
            ("candidate_response", "response", "answer", "output", "observation", "content"),
            default=None,
        )
        if candidate is not None:
            return candidate
    return None


def _summary_from_rewards(
    env_id: str,
    model_version: str,
    rewards: Sequence[float],
) -> RewardCalibrationSummary:
    if not rewards:
        return RewardCalibrationSummary(
            env_id=env_id,
            model_version=model_version,
            reward_count=0,
            mean_reward=None,
            std_reward=None,
            min_reward=None,
            max_reward=None,
            zero_variance=True,
            missing=True,
        )
    mean_reward = float(_mean(rewards))
    variance = sum((reward - mean_reward) ** 2 for reward in rewards) / len(rewards)
    std_reward = math.sqrt(variance)
    return RewardCalibrationSummary(
        env_id=env_id,
        model_version=model_version,
        reward_count=len(rewards),
        mean_reward=round(mean_reward, 6),
        std_reward=round(std_reward, 6),
        min_reward=min(rewards),
        max_reward=max(rewards),
        zero_variance=std_reward <= 0.0,
        missing=False,
    )


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
    "CalibratedReward",
    "DEFAULT_JUDGE_DECISION_THRESHOLD",
    "DEFAULT_RL_CURRICULUM_BLOCKERS",
    "DEFAULT_JUDGE_DISPATCH_BLOCKERS",
    "CurriculumSamplingPlan",
    "EnvGapConfig",
    "EnvGapEstimate",
    "EnvJudgeRoutingPolicy",
    "JudgeDispatchRecord",
    "RewardCalibrationSummary",
    "SamplingAllocation",
    "build_dynamic_sampling_plan",
    "build_default_env_judge_routing_policies",
    "build_reward_calibration_summaries",
    "calibrate_rollout_rewards",
    "calibrate_trace_reward",
    "dispatch_judge_ensembles_for_rollouts",
    "estimate_env_gaps",
    "format_curriculum_plan",
    "judge_ensemble_result_to_rollout_metrics",
    "judge_response_to_rollout_metrics",
    "rollout_trace_to_judge_request",
]
