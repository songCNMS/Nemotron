# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox judge-pool interface for M2 (task034 Session 1).

The production judge pool will route to live GenRM / judge services and
cluster-hosted models. This module deliberately stays local and deterministic:
it defines versioned judge records, calibration metadata, request/response
contracts, a mock judge, deterministic ensemble aggregation, and an explicit
live-adapter boundary that remains deferred.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


JsonDict = dict[str, Any]

LABEL_PASS = "pass"
LABEL_FAIL = "fail"
DEFAULT_DECISION_THRESHOLD = 0.5

DEFAULT_JUDGE_POOL_BLOCKERS = (
    "task018 Session 3 live GenRM service deployment",
    "task018 Session 4 end-to-end RLHF",
    "live judge model hosting",
    "auth/secrets for judge services",
    "calibration corpora access",
    "reward service routing",
    "cluster inference",
)


def _require_nonempty(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


def _freeze_strings(values: Sequence[str] | None, field_name: str) -> tuple[str, ...]:
    if not values:
        return ()
    out = tuple(_require_nonempty(value, field_name) for value in values)
    if len(set(out)) != len(out):
        raise ValueError(f"{field_name} must not contain duplicates")
    return out


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot average an empty sequence")
    return sum(values) / len(values)


@dataclass(frozen=True, order=True)
class JudgeModelVersion:
    """One frozen judge model version used for reproducible scoring."""

    judge_id: str
    version: str
    provider: str = "mock"
    model_name: str = "sandbox-mock-judge"
    calibration_set_id: str | None = None
    capabilities: tuple[str, ...] = ()
    frozen: bool = True
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "judge_id", _require_nonempty(self.judge_id, "judge_id"))
        object.__setattr__(self, "version", _require_nonempty(self.version, "version"))
        object.__setattr__(self, "provider", _require_nonempty(self.provider, "provider"))
        object.__setattr__(self, "model_name", _require_nonempty(self.model_name, "model_name"))
        object.__setattr__(
            self,
            "capabilities",
            _freeze_strings(self.capabilities, "capabilities"),
        )
        if self.calibration_set_id is not None:
            object.__setattr__(
                self,
                "calibration_set_id",
                _require_nonempty(self.calibration_set_id, "calibration_set_id"),
            )
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @property
    def version_key(self) -> str:
        return f"{self.judge_id}@{self.version}"

    def to_jsonable(self) -> JsonDict:
        return {
            "judge_id": self.judge_id,
            "version": self.version,
            "version_key": self.version_key,
            "provider": self.provider,
            "model_name": self.model_name,
            "calibration_set_id": self.calibration_set_id,
            "capabilities": list(self.capabilities),
            "frozen": self.frozen,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class CalibrationSet:
    """Metadata for a frozen judge calibration set."""

    calibration_set_id: str
    env_id: str
    revision: str
    sample_count: int
    metric_name: str = "judge_score"
    score_mean: float = 0.5
    score_std: float = 0.25
    score_min: float = 0.0
    score_max: float = 1.0
    label_space: tuple[str, ...] = (LABEL_FAIL, LABEL_PASS)
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "calibration_set_id",
            _require_nonempty(self.calibration_set_id, "calibration_set_id"),
        )
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        object.__setattr__(self, "revision", _require_nonempty(self.revision, "revision"))
        object.__setattr__(self, "metric_name", _require_nonempty(self.metric_name, "metric_name"))
        if int(self.sample_count) <= 0:
            raise ValueError("sample_count must be positive")
        object.__setattr__(self, "sample_count", int(self.sample_count))
        if float(self.score_std) <= 0.0:
            raise ValueError("score_std must be positive")
        if float(self.score_min) >= float(self.score_max):
            raise ValueError("score_min must be less than score_max")
        object.__setattr__(
            self,
            "label_space",
            _freeze_strings(self.label_space, "label_space"),
        )
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def calibrate_score(self, score: float) -> float:
        """Map a raw score into the calibrated 0..1 range."""

        span = float(self.score_max) - float(self.score_min)
        return _clamp01((float(score) - float(self.score_min)) / span)

    def z_score(self, score: float) -> float:
        return (float(score) - float(self.score_mean)) / float(self.score_std)

    def to_jsonable(self) -> JsonDict:
        return {
            "calibration_set_id": self.calibration_set_id,
            "env_id": self.env_id,
            "revision": self.revision,
            "sample_count": self.sample_count,
            "metric_name": self.metric_name,
            "score_mean": float(self.score_mean),
            "score_std": float(self.score_std),
            "score_min": float(self.score_min),
            "score_max": float(self.score_max),
            "label_space": list(self.label_space),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class JudgeRequest:
    """One candidate response to score with the judge pool."""

    request_id: str
    env_id: str
    prompt: str
    candidate_response: str
    reference_response: str | None = None
    rubric: str | None = None
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _require_nonempty(self.request_id, "request_id"))
        object.__setattr__(self, "env_id", _require_nonempty(self.env_id, "env_id"))
        object.__setattr__(self, "prompt", _require_nonempty(self.prompt, "prompt"))
        object.__setattr__(
            self,
            "candidate_response",
            _require_nonempty(self.candidate_response, "candidate_response"),
        )
        if self.reference_response is not None:
            object.__setattr__(
                self,
                "reference_response",
                _require_nonempty(self.reference_response, "reference_response"),
            )
        if self.rubric is not None:
            object.__setattr__(self, "rubric", _require_nonempty(self.rubric, "rubric"))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_jsonable(self) -> JsonDict:
        return {
            "request_id": self.request_id,
            "env_id": self.env_id,
            "prompt": self.prompt,
            "candidate_response": self.candidate_response,
            "reference_response": self.reference_response,
            "rubric": self.rubric,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class JudgeResponse:
    """One judge's scored response, including frozen version metadata."""

    request_id: str
    judge_version: JudgeModelVersion
    score: float
    label: str
    confidence: float
    calibration_set_id: str | None = None
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _require_nonempty(self.request_id, "request_id"))
        object.__setattr__(self, "score", _clamp01(float(self.score)))
        object.__setattr__(self, "label", _require_nonempty(self.label, "label"))
        object.__setattr__(self, "confidence", _clamp01(float(self.confidence)))
        if self.calibration_set_id is not None:
            object.__setattr__(
                self,
                "calibration_set_id",
                _require_nonempty(self.calibration_set_id, "calibration_set_id"),
            )
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_jsonable(self) -> JsonDict:
        return {
            "request_id": self.request_id,
            "judge_version": self.judge_version.to_jsonable(),
            "score": self.score,
            "label": self.label,
            "confidence": self.confidence,
            "calibration_set_id": self.calibration_set_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EnsembleVoteResult:
    """Deterministic aggregate across multiple judge responses."""

    request_id: str
    responses: tuple[JudgeResponse, ...]
    aggregate_score: float
    aggregate_confidence: float
    label: str
    votes_by_label: dict[str, int]
    decision_threshold: float = DEFAULT_DECISION_THRESHOLD
    decision_rule: str = "majority_label_then_mean_score"

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", _require_nonempty(self.request_id, "request_id"))
        if not self.responses:
            raise ValueError("ensemble requires at least one judge response")
        object.__setattr__(self, "aggregate_score", _clamp01(float(self.aggregate_score)))
        object.__setattr__(
            self,
            "aggregate_confidence",
            _clamp01(float(self.aggregate_confidence)),
        )
        object.__setattr__(self, "label", _require_nonempty(self.label, "label"))
        object.__setattr__(self, "votes_by_label", dict(sorted(self.votes_by_label.items())))

    @property
    def judge_version_keys(self) -> tuple[str, ...]:
        return tuple(response.judge_version.version_key for response in self.responses)

    def to_jsonable(self) -> JsonDict:
        return {
            "request_id": self.request_id,
            "aggregate_score": self.aggregate_score,
            "aggregate_confidence": self.aggregate_confidence,
            "label": self.label,
            "votes_by_label": dict(self.votes_by_label),
            "decision_threshold": self.decision_threshold,
            "decision_rule": self.decision_rule,
            "judge_version_keys": list(self.judge_version_keys),
            "responses": [response.to_jsonable() for response in self.responses],
        }


class JudgeVersionRegistry:
    """Resolve frozen judge versions, calibration sets, and aliases."""

    def __init__(
        self,
        *,
        versions: Sequence[JudgeModelVersion],
        calibration_sets: Sequence[CalibrationSet] = (),
        aliases: Mapping[str, str] | None = None,
        default_ensemble: Sequence[str] = (),
    ) -> None:
        if not versions:
            raise ValueError("judge registry requires at least one version")
        self._versions = {version.version_key: version for version in versions}
        if len(self._versions) != len(versions):
            raise ValueError("judge version keys must be unique")
        self._calibration_sets = {
            calibration.calibration_set_id: calibration for calibration in calibration_sets
        }
        if len(self._calibration_sets) != len(calibration_sets):
            raise ValueError("calibration_set_id values must be unique")
        self._aliases = dict(aliases or {})
        for alias, target in self._aliases.items():
            _require_nonempty(alias, "alias")
            if target not in self._versions:
                raise ValueError(f"alias {alias!r} points to unknown judge version {target!r}")
        self.default_ensemble = _freeze_strings(default_ensemble, "default_ensemble")

    @property
    def version_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._versions))

    @property
    def aliases(self) -> dict[str, str]:
        return dict(sorted(self._aliases.items()))

    def resolve_version(self, ref: str) -> JudgeModelVersion:
        key = self._aliases.get(ref, ref)
        try:
            return self._versions[key]
        except KeyError as exc:
            known = ", ".join(self.version_keys)
            raise KeyError(f"unknown judge version {ref!r}; known versions: {known}") from exc

    def resolve_calibration(self, version: JudgeModelVersion) -> CalibrationSet | None:
        if version.calibration_set_id is None:
            return None
        try:
            return self._calibration_sets[version.calibration_set_id]
        except KeyError as exc:
            raise KeyError(
                f"judge version {version.version_key!r} references unknown calibration "
                f"set {version.calibration_set_id!r}"
            ) from exc

    def build_mock_judge(
        self,
        ref: str,
        *,
        score_overrides: Mapping[str, Any] | None = None,
    ) -> "MockJudge":
        version = self.resolve_version(ref)
        return MockJudge(
            version=version,
            calibration_set=self.resolve_calibration(version),
            score_overrides=score_overrides,
        )

    def build_default_mock_ensemble(
        self,
        *,
        score_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> tuple["MockJudge", ...]:
        refs = self.default_ensemble or self.version_keys
        overrides = score_overrides or {}
        return tuple(
            self.build_mock_judge(ref, score_overrides=overrides.get(ref))
            for ref in refs
        )

    def to_jsonable(self) -> JsonDict:
        return {
            "schema_version": 1,
            "versions": [
                self._versions[key].to_jsonable()
                for key in self.version_keys
            ],
            "calibration_sets": [
                self._calibration_sets[key].to_jsonable()
                for key in sorted(self._calibration_sets)
            ],
            "aliases": self.aliases,
            "default_ensemble": list(self.default_ensemble),
            "blockers": list(DEFAULT_JUDGE_POOL_BLOCKERS),
        }


class MockJudge:
    """Deterministic local judge implementation for sandbox tests."""

    def __init__(
        self,
        *,
        version: JudgeModelVersion,
        calibration_set: CalibrationSet | None = None,
        score_overrides: Mapping[str, Any] | None = None,
    ) -> None:
        self.version = version
        self.calibration_set = calibration_set
        self.score_overrides = dict(score_overrides or {})

    def judge(self, request: JudgeRequest) -> JudgeResponse:
        raw_score, confidence, label = self._score_request(request)
        calibrated_score = (
            self.calibration_set.calibrate_score(raw_score)
            if self.calibration_set is not None
            else raw_score
        )
        final_label = label or _label_for_score(calibrated_score)
        return JudgeResponse(
            request_id=request.request_id,
            judge_version=self.version,
            score=calibrated_score,
            label=final_label,
            confidence=confidence,
            calibration_set_id=(
                self.calibration_set.calibration_set_id
                if self.calibration_set is not None
                else self.version.calibration_set_id
            ),
            metadata={
                "adapter": "mock",
                "score_source": (
                    "override"
                    if request.request_id in self.score_overrides
                    else "deterministic_hash"
                ),
                "raw_score": raw_score,
                "raw_z_score": (
                    self.calibration_set.z_score(raw_score)
                    if self.calibration_set is not None
                    else None
                ),
            },
        )

    def _score_request(self, request: JudgeRequest) -> tuple[float, float, str | None]:
        if request.request_id in self.score_overrides:
            override = self.score_overrides[request.request_id]
            if isinstance(override, Mapping):
                score = _clamp01(float(override.get("score", 0.0)))
                confidence = _clamp01(float(override.get("confidence", _confidence_for_score(score))))
                label = override.get("label")
                return score, confidence, str(label) if label is not None else None
            score = _clamp01(float(override))
            return score, _confidence_for_score(score), None
        material = "|".join(
            [
                self.version.version_key,
                request.request_id,
                request.env_id,
                request.prompt,
                request.candidate_response,
                request.reference_response or "",
                request.rubric or "",
            ]
        )
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) / 0xFFFFFFFF
        score = round(bucket, 6)
        return score, _confidence_for_score(score), None


class DeferredLiveJudgeAdapter:
    """Boundary for future live-service adapters.

    The class is intentionally not wired to network calls in Session 1.
    """

    def __init__(self, *, endpoint_name: str, blockers: Sequence[str] | None = None) -> None:
        self.endpoint_name = _require_nonempty(endpoint_name, "endpoint_name")
        self.blockers = tuple(blockers or DEFAULT_JUDGE_POOL_BLOCKERS)

    def judge(self, request: JudgeRequest) -> JudgeResponse:
        raise NotImplementedError(
            "live judge service adapter is deferred; unresolved blockers: "
            + ", ".join(self.blockers)
        )

    def to_jsonable(self) -> JsonDict:
        return {
            "endpoint_name": self.endpoint_name,
            "status": "deferred",
            "blockers": list(self.blockers),
        }


def evaluate_ensemble(
    request: JudgeRequest,
    judges: Sequence[MockJudge],
    *,
    decision_threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> EnsembleVoteResult:
    """Run a deterministic ensemble over a judge request."""

    if not judges:
        raise ValueError("ensemble requires at least one judge")
    responses = tuple(
        sorted(
            (judge.judge(request) for judge in judges),
            key=lambda response: response.judge_version.version_key,
        )
    )
    aggregate_score = round(_mean([response.score for response in responses]), 6)
    aggregate_confidence = round(_mean([response.confidence for response in responses]), 6)
    votes = Counter(response.label for response in responses)
    label = _ensemble_label(votes, aggregate_score, decision_threshold)
    return EnsembleVoteResult(
        request_id=request.request_id,
        responses=responses,
        aggregate_score=aggregate_score,
        aggregate_confidence=aggregate_confidence,
        label=label,
        votes_by_label=dict(sorted(votes.items())),
        decision_threshold=decision_threshold,
    )


def format_ensemble_report(result: EnsembleVoteResult) -> str:
    """Render a compact Markdown report for one ensemble result."""

    lines = [
        f"# Judge ensemble result: **{result.label.upper()}**",
        "",
        f"- Request: `{result.request_id}`",
        f"- Aggregate score: `{result.aggregate_score:.6f}`",
        f"- Aggregate confidence: `{result.aggregate_confidence:.6f}`",
        f"- Decision rule: `{result.decision_rule}`",
        "",
        "| Judge version | Label | Score | Confidence | Calibration |",
        "|---|---|---:|---:|---|",
    ]
    for response in result.responses:
        lines.append(
            "| {version} | {label} | {score:.6f} | {confidence:.6f} | {calib} |".format(
                version=response.judge_version.version_key,
                label=response.label,
                score=response.score,
                confidence=response.confidence,
                calib=response.calibration_set_id or "-",
            )
        )
    lines.extend(["", "## Deferred Live Work", ""])
    for blocker in DEFAULT_JUDGE_POOL_BLOCKERS:
        lines.append(f"- {blocker}")
    return "\n".join(lines) + "\n"


def build_default_sandbox_judge_pool() -> JudgeVersionRegistry:
    """Return a small frozen mock judge registry for sandbox tests."""

    calibrations = (
        CalibrationSet(
            calibration_set_id="safety_calibration_s1",
            env_id="safety_judge",
            revision="synthetic_task029_s1",
            sample_count=12,
            metadata={"scope": "safety/jailbreak/over-refusal sandbox prompts"},
        ),
        CalibrationSet(
            calibration_set_id="if_calibration_s1",
            env_id="multilingual_ifeval",
            revision="synthetic_task027_s1",
            sample_count=8,
            metadata={"scope": "instruction-following sandbox prompts"},
        ),
        CalibrationSet(
            calibration_set_id="genrm_calibration_s1",
            env_id="genrm_compare",
            revision="synthetic_task018_bridge",
            sample_count=10,
            metadata={"scope": "preference-comparison mock records"},
        ),
    )
    versions = (
        JudgeModelVersion(
            judge_id="safety_judge",
            version="mock-s1",
            calibration_set_id="safety_calibration_s1",
            capabilities=("safety", "jailbreak", "over_refusal"),
        ),
        JudgeModelVersion(
            judge_id="instruction_judge",
            version="mock-s1",
            calibration_set_id="if_calibration_s1",
            capabilities=("instruction_following", "multilingual"),
        ),
        JudgeModelVersion(
            judge_id="genrm_compare",
            version="mock-s1",
            calibration_set_id="genrm_calibration_s1",
            capabilities=("preference_comparison", "rlhf_reward"),
        ),
    )
    return JudgeVersionRegistry(
        versions=versions,
        calibration_sets=calibrations,
        aliases={
            "safety_primary": "safety_judge@mock-s1",
            "if_primary": "instruction_judge@mock-s1",
            "genrm_primary": "genrm_compare@mock-s1",
        },
        default_ensemble=("safety_primary", "if_primary", "genrm_primary"),
    )


def _confidence_for_score(score: float) -> float:
    return round(0.5 + abs(_clamp01(score) - 0.5), 6)


def _label_for_score(score: float, *, threshold: float = DEFAULT_DECISION_THRESHOLD) -> str:
    return LABEL_PASS if float(score) >= threshold else LABEL_FAIL


def _ensemble_label(
    votes: Mapping[str, int],
    aggregate_score: float,
    decision_threshold: float,
) -> str:
    pass_votes = int(votes.get(LABEL_PASS, 0))
    fail_votes = int(votes.get(LABEL_FAIL, 0))
    if pass_votes > fail_votes:
        return LABEL_PASS
    if fail_votes > pass_votes:
        return LABEL_FAIL
    return _label_for_score(aggregate_score, threshold=decision_threshold)


__all__ = [
    "DEFAULT_JUDGE_POOL_BLOCKERS",
    "CalibrationSet",
    "DeferredLiveJudgeAdapter",
    "EnsembleVoteResult",
    "JudgeModelVersion",
    "JudgeRequest",
    "JudgeResponse",
    "JudgeVersionRegistry",
    "MockJudge",
    "build_default_sandbox_judge_pool",
    "evaluate_ensemble",
    "format_ensemble_report",
]
