# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox-only environment scheduler policy model for Super3 M2.

This module deliberately models scheduler decisions over local Python records.
It does not start Ray actors, NeMo-RL workers, vLLM servers, NeMo-Gym
environments, Kubernetes jobs, or real queues. Session 1 is the stable policy
contract: classify environments into fast/slow queues, apply per-env quotas and
backpressure signals, and choose the next runnable item deterministically.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

JsonDict = dict[str, Any]

DEFAULT_SLOW_ENV_TERMS = ("swe", "browser", "gui")
SUCCESS_TERMINAL_REASONS = frozenset({"solved", "success", "passed", "pass", "complete"})


class QueueName(StrEnum):
    """Logical queues in the sandbox scheduler plan."""

    NORMAL = "normal"
    SLOW = "slow"


def _require_nonempty_string(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


def _require_nonnegative_int(value: Any, field_name: str) -> int:
    number = int(value)
    if number < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return number


def _optional_nonnegative_float(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    number = float(value)
    if number < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return number


def _normalise_queue(value: QueueName | str | None, field_name: str = "queue") -> QueueName | None:
    if value is None:
        return None
    try:
        return value if isinstance(value, QueueName) else QueueName(str(value))
    except ValueError as exc:
        choices = ", ".join(queue.value for queue in QueueName)
        raise ValueError(f"{field_name} must be one of: {choices}") from exc


@dataclass(frozen=True)
class EnvQuota:
    """Per-environment sandbox quota inputs.

    ``max_in_flight`` models active workers for the env, while ``max_pending``
    models queued local work before the env is considered backpressured.
    """

    env_id: str
    max_in_flight: int = 1
    max_pending: int = 16
    queue: QueueName | str | None = None
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty_string(self.env_id, "env_id"))
        object.__setattr__(
            self,
            "max_in_flight",
            _require_nonnegative_int(self.max_in_flight, "max_in_flight"),
        )
        object.__setattr__(
            self,
            "max_pending",
            _require_nonnegative_int(self.max_pending, "max_pending"),
        )
        object.__setattr__(self, "queue", _normalise_queue(self.queue))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @classmethod
    def from_mapping(cls, env_id: str, data: Mapping[str, Any] | "EnvQuota") -> "EnvQuota":
        if isinstance(data, EnvQuota):
            if data.env_id != env_id:
                raise ValueError(f"quota key {env_id!r} does not match quota env_id {data.env_id!r}")
            return data
        return cls(
            env_id=env_id,
            max_in_flight=data.get("max_in_flight", 1),
            max_pending=data.get("max_pending", 16),
            queue=data.get("queue"),
            metadata=dict(data.get("metadata") or {}),
        )

    def to_jsonable(self) -> JsonDict:
        out = asdict(self)
        out["queue"] = self.queue.value if self.queue else None
        return out


@dataclass(frozen=True)
class EnvBackpressure:
    """Local backpressure signal for one environment."""

    env_id: str
    in_flight: int = 0
    pending: int = 0
    recent_failures: int = 0
    avg_latency_ms: float | None = None
    explicit_backpressure: bool = False
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "env_id", _require_nonempty_string(self.env_id, "env_id"))
        object.__setattr__(self, "in_flight", _require_nonnegative_int(self.in_flight, "in_flight"))
        object.__setattr__(self, "pending", _require_nonnegative_int(self.pending, "pending"))
        object.__setattr__(
            self,
            "recent_failures",
            _require_nonnegative_int(self.recent_failures, "recent_failures"),
        )
        object.__setattr__(
            self,
            "avg_latency_ms",
            _optional_nonnegative_float(self.avg_latency_ms, "avg_latency_ms"),
        )
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @classmethod
    def empty(cls, env_id: str) -> "EnvBackpressure":
        return cls(env_id=env_id)

    @classmethod
    def from_mapping(
        cls,
        env_id: str,
        data: Mapping[str, Any] | "EnvBackpressure",
    ) -> "EnvBackpressure":
        if isinstance(data, EnvBackpressure):
            if data.env_id != env_id:
                raise ValueError(f"signal key {env_id!r} does not match signal env_id {data.env_id!r}")
            return data
        return cls(
            env_id=env_id,
            in_flight=data.get("in_flight", 0),
            pending=data.get("pending", 0),
            recent_failures=data.get("recent_failures", 0),
            avg_latency_ms=data.get("avg_latency_ms"),
            explicit_backpressure=bool(data.get("explicit_backpressure", False)),
            metadata=dict(data.get("metadata") or {}),
        )

    def to_jsonable(self) -> JsonDict:
        return asdict(self)


@dataclass(frozen=True)
class EnvSchedulerConfig:
    """Scheduler policy thresholds and queue classification hints."""

    slow_env_ids: frozenset[str] = field(default_factory=frozenset)
    slow_env_terms: tuple[str, ...] = DEFAULT_SLOW_ENV_TERMS
    failure_backpressure_threshold: int = 3
    latency_backpressure_ms: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "slow_env_ids",
            frozenset(str(env_id).strip() for env_id in self.slow_env_ids if str(env_id).strip()),
        )
        object.__setattr__(
            self,
            "slow_env_terms",
            tuple(str(term).lower() for term in self.slow_env_terms if str(term).strip()),
        )
        object.__setattr__(
            self,
            "failure_backpressure_threshold",
            _require_nonnegative_int(
                self.failure_backpressure_threshold,
                "failure_backpressure_threshold",
            ),
        )
        object.__setattr__(
            self,
            "latency_backpressure_ms",
            _optional_nonnegative_float(self.latency_backpressure_ms, "latency_backpressure_ms"),
        )


@dataclass(frozen=True)
class SchedulerItem:
    """One pending prompt/model/env rollout request."""

    prompt_id: str
    model_version: str
    env_id: str
    priority: int = 0
    sequence: int = 0
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "prompt_id", _require_nonempty_string(self.prompt_id, "prompt_id"))
        object.__setattr__(
            self,
            "model_version",
            _require_nonempty_string(self.model_version, "model_version"),
        )
        object.__setattr__(self, "env_id", _require_nonempty_string(self.env_id, "env_id"))
        object.__setattr__(self, "priority", int(self.priority))
        object.__setattr__(self, "sequence", int(self.sequence))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | "SchedulerItem") -> "SchedulerItem":
        if isinstance(data, SchedulerItem):
            return data
        return cls(
            prompt_id=data.get("prompt_id"),
            model_version=data.get("model_version"),
            env_id=data.get("env_id"),
            priority=data.get("priority", 0),
            sequence=data.get("sequence", 0),
            metadata=dict(data.get("metadata") or {}),
        )

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.prompt_id, self.model_version, self.env_id)

    def to_jsonable(self) -> JsonDict:
        return asdict(self)


@dataclass(frozen=True)
class SchedulerEnvState:
    """Evaluated quota/backpressure state for an environment."""

    env_id: str
    queue: QueueName
    quota: EnvQuota
    signal: EnvBackpressure
    quota_remaining: int
    backpressure_reasons: tuple[str, ...] = ()

    @property
    def is_available(self) -> bool:
        return not self.backpressure_reasons

    def to_jsonable(self) -> JsonDict:
        return {
            "env_id": self.env_id,
            "queue": self.queue.value,
            "quota": self.quota.to_jsonable(),
            "signal": self.signal.to_jsonable(),
            "quota_remaining": self.quota_remaining,
            "available": self.is_available,
            "backpressure_reasons": list(self.backpressure_reasons),
        }


@dataclass(frozen=True)
class SchedulingDecision:
    """Stable JSON-friendly scheduling decision."""

    action: str
    reason: str
    item: SchedulerItem | None
    queue: QueueName | None
    env_state: SchedulerEnvState | None
    skipped: tuple[JsonDict, ...] = ()

    @property
    def should_schedule(self) -> bool:
        return self.action == "schedule" and self.item is not None

    def to_jsonable(self) -> JsonDict:
        return {
            "action": self.action,
            "reason": self.reason,
            "item": self.item.to_jsonable() if self.item else None,
            "queue": self.queue.value if self.queue else None,
            "env_state": self.env_state.to_jsonable() if self.env_state else None,
            "skipped": list(self.skipped),
        }


def classify_env_queue(
    env_id: str,
    *,
    quota: EnvQuota | None = None,
    config: EnvSchedulerConfig | None = None,
) -> QueueName:
    """Classify an environment into the normal or slow queue."""

    env_id = _require_nonempty_string(env_id, "env_id")
    if quota and quota.queue:
        return quota.queue
    policy = config or EnvSchedulerConfig()
    if env_id in policy.slow_env_ids:
        return QueueName.SLOW
    lowered = env_id.lower()
    if any(term in lowered for term in policy.slow_env_terms):
        return QueueName.SLOW
    return QueueName.NORMAL


class SandboxEnvScheduler:
    """Deterministic scheduler policy for local/synthetic rollout requests."""

    def __init__(
        self,
        quotas: Mapping[str, EnvQuota | Mapping[str, Any]] | None = None,
        signals: Mapping[str, EnvBackpressure | Mapping[str, Any]] | None = None,
        *,
        config: EnvSchedulerConfig | None = None,
    ) -> None:
        self.config = config or EnvSchedulerConfig()
        self.quotas = {
            env_id: EnvQuota.from_mapping(env_id, quota)
            for env_id, quota in (quotas or {}).items()
        }
        self.signals = {
            env_id: EnvBackpressure.from_mapping(env_id, signal)
            for env_id, signal in (signals or {}).items()
        }

    def env_state(self, env_id: str) -> SchedulerEnvState:
        """Evaluate queue, quota, and backpressure for one env."""

        env_id = _require_nonempty_string(env_id, "env_id")
        quota = self.quotas.get(env_id, EnvQuota(env_id=env_id))
        signal = self.signals.get(env_id, EnvBackpressure.empty(env_id))
        queue = classify_env_queue(env_id, quota=quota, config=self.config)
        quota_remaining = max(quota.max_in_flight - signal.in_flight, 0)
        reasons: list[str] = []
        if signal.explicit_backpressure:
            reasons.append("explicit_backpressure")
        if signal.in_flight >= quota.max_in_flight:
            reasons.append("in_flight_quota_exhausted")
        if signal.pending >= quota.max_pending:
            reasons.append("pending_quota_exhausted")
        if (
            self.config.failure_backpressure_threshold
            and signal.recent_failures >= self.config.failure_backpressure_threshold
        ):
            reasons.append("recent_failures")
        if (
            self.config.latency_backpressure_ms is not None
            and signal.avg_latency_ms is not None
            and signal.avg_latency_ms >= self.config.latency_backpressure_ms
        ):
            reasons.append("latency_backpressure")
        return SchedulerEnvState(
            env_id=env_id,
            queue=queue,
            quota=quota,
            signal=signal,
            quota_remaining=quota_remaining,
            backpressure_reasons=tuple(reasons),
        )

    def choose_next(
        self,
        items: Iterable[SchedulerItem | Mapping[str, Any]],
        *,
        target_queue: QueueName | str | None = None,
    ) -> SchedulingDecision:
        """Choose the next runnable item, skipping backpressured envs.

        Sorting is intentionally stable and deterministic: higher priority first,
        then lower sequence, then env/model/prompt ids as tie-breakers.
        """

        queue_filter = _normalise_queue(target_queue, "target_queue")
        candidates = sorted(
            (SchedulerItem.from_mapping(item) for item in items),
            key=lambda item: (
                -item.priority,
                item.sequence,
                item.env_id,
                item.model_version,
                item.prompt_id,
            ),
        )
        skipped: list[JsonDict] = []
        for item in candidates:
            state = self.env_state(item.env_id)
            if queue_filter is not None and state.queue != queue_filter:
                skipped.append(
                    {
                        "prompt_id": item.prompt_id,
                        "env_id": item.env_id,
                        "queue": state.queue.value,
                        "reason": "queue_mismatch",
                    }
                )
                continue
            if state.backpressure_reasons:
                skipped.append(
                    {
                        "prompt_id": item.prompt_id,
                        "env_id": item.env_id,
                        "queue": state.queue.value,
                        "reason": "backpressure",
                        "backpressure_reasons": list(state.backpressure_reasons),
                    }
                )
                continue
            return SchedulingDecision(
                action="schedule",
                reason="eligible",
                item=item,
                queue=state.queue,
                env_state=state,
                skipped=tuple(skipped),
            )

        return SchedulingDecision(
            action="defer",
            reason="no_eligible_candidates",
            item=None,
            queue=queue_filter,
            env_state=None,
            skipped=tuple(skipped),
        )

    def snapshot(self) -> JsonDict:
        """Return a JSON-friendly view of known env states."""

        env_ids = sorted(set(self.quotas) | set(self.signals))
        return {
            "schema_version": 1,
            "kind": "sandbox_env_scheduler",
            "queues": [queue.value for queue in QueueName],
            "environments": [self.env_state(env_id).to_jsonable() for env_id in env_ids],
            "out_of_scope": [
                "Ray/NeMo-RL/vLLM/NeMo-Gym worker startup",
                "Kubernetes or cluster resource telemetry",
                "live retry/accounting integration",
                "production scheduler deployment",
            ],
        }


def summarize_rollout_backpressure(
    records: Iterable[Any],
    *,
    in_flight_by_env: Mapping[str, int] | None = None,
    pending_by_env: Mapping[str, int] | None = None,
    explicit_backpressure_by_env: Mapping[str, bool] | None = None,
) -> dict[str, EnvBackpressure]:
    """Build env backpressure signals from local rollout-store-like records.

    The function accepts ``RolloutTrace`` instances, dict rows, or any object
    with ``env_id``, ``reward``, ``terminal_reason``, and ``metrics``
    attributes. This keeps task033 decoupled from a production rollout backend
    while still consuming task032's local JSONL contract in tests.
    """

    env_counts: dict[str, int] = defaultdict(int)
    failure_counts: dict[str, int] = defaultdict(int)
    latency_totals: dict[str, float] = defaultdict(float)
    latency_counts: dict[str, int] = defaultdict(int)

    for record in records:
        env_id = _record_value(record, "env_id")
        if env_id is None:
            raise ValueError("rollout record must include env_id")
        env_id = _require_nonempty_string(env_id, "env_id")
        env_counts[env_id] += 1

        reward = _record_value(record, "reward")
        terminal_reason = _record_value(record, "terminal_reason")
        if _is_failed_rollout(reward, terminal_reason):
            failure_counts[env_id] += 1

        latency_ms = _latency_ms_from_record(record)
        if latency_ms is not None:
            latency_totals[env_id] += latency_ms
            latency_counts[env_id] += 1

    env_ids = (
        set(env_counts)
        | set(in_flight_by_env or {})
        | set(pending_by_env or {})
        | set(explicit_backpressure_by_env or {})
    )
    signals: dict[str, EnvBackpressure] = {}
    for env_id in sorted(env_ids):
        avg_latency = None
        if latency_counts.get(env_id):
            avg_latency = latency_totals[env_id] / latency_counts[env_id]
        signals[env_id] = EnvBackpressure(
            env_id=env_id,
            in_flight=(in_flight_by_env or {}).get(env_id, 0),
            pending=(pending_by_env or {}).get(env_id, 0),
            recent_failures=failure_counts.get(env_id, 0),
            avg_latency_ms=avg_latency,
            explicit_backpressure=bool((explicit_backpressure_by_env or {}).get(env_id, False)),
            metadata={"rollout_count": env_counts.get(env_id, 0)},
        )
    return signals


def _record_value(record: Any, field_name: str) -> Any:
    if isinstance(record, Mapping):
        return record.get(field_name)
    return getattr(record, field_name, None)


def _record_metrics(record: Any) -> Mapping[str, Any]:
    metrics = _record_value(record, "metrics") or {}
    if not isinstance(metrics, Mapping):
        raise ValueError("rollout record metrics must be a mapping")
    return metrics


def _latency_ms_from_record(record: Any) -> float | None:
    metrics = _record_metrics(record)
    for key in ("latency_ms", "elapsed_ms", "runtime_ms"):
        if metrics.get(key) is not None:
            return _optional_nonnegative_float(metrics[key], key)
    if metrics.get("elapsed_s") is not None:
        return _optional_nonnegative_float(metrics["elapsed_s"], "elapsed_s") * 1000.0
    return None


def _is_failed_rollout(reward: Any, terminal_reason: Any) -> bool:
    if reward is not None:
        try:
            if float(reward) <= 0.0:
                return True
        except (TypeError, ValueError):
            pass
    if terminal_reason is None:
        return False
    return str(terminal_reason).strip().lower() not in SUCCESS_TERMINAL_REASONS
