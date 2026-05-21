# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Repo-local rollout store scaffold (task032 Session 1).

The production rollout store will likely stream to W&B / object storage
and enforce retention policy. This Session 1 module deliberately stays
stdlib-only and local: append JSONL records, maintain a small materialized
index, and retrieve traces by the central rollout key
``(prompt_id, model_version, env_id)``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]

ROLLOUT_STORE_SCHEMA_VERSION = 1
DEFAULT_ROLLOUTS_FILENAME = "rollouts.jsonl"
DEFAULT_INDEX_FILENAME = "rollout_index.json"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _require_nonempty_string(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


@dataclass(frozen=True, order=True)
class RolloutKey:
    """Central rollout-store key: prompt, model, environment."""

    prompt_id: str
    model_version: str
    env_id: str

    def __post_init__(self) -> None:
        _require_nonempty_string(self.prompt_id, "prompt_id")
        _require_nonempty_string(self.model_version, "model_version")
        _require_nonempty_string(self.env_id, "env_id")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RolloutKey":
        return cls(
            prompt_id=_require_nonempty_string(data.get("prompt_id"), "prompt_id"),
            model_version=_require_nonempty_string(data.get("model_version"), "model_version"),
            env_id=_require_nonempty_string(data.get("env_id"), "env_id"),
        )

    def to_jsonable(self) -> JsonDict:
        return asdict(self)


def key_to_index_token(key: RolloutKey) -> str:
    """Stable JSON token for the tuple key used in the on-disk index."""

    return json.dumps(
        [key.prompt_id, key.model_version, key.env_id],
        ensure_ascii=False,
        separators=(",", ":"),
    )


def stable_rollout_id(payload: Mapping[str, Any]) -> str:
    """Deterministic rollout id for synthetic/local traces."""

    key = RolloutKey.from_mapping(payload)
    material = {
        "key": key.to_jsonable(),
        "reward": payload.get("reward"),
        "terminal_reason": payload.get("terminal_reason"),
        "trace": payload.get("trace") or [],
        "metrics": payload.get("metrics") or {},
        "metadata": payload.get("metadata") or {},
    }
    encoded = json.dumps(material, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class RolloutTrace:
    """One rollout record stored as one JSONL row."""

    prompt_id: str
    model_version: str
    env_id: str
    rollout_id: str
    trace: tuple[JsonDict, ...] = field(default_factory=tuple)
    reward: float | None = None
    terminal_reason: str | None = None
    metrics: JsonDict = field(default_factory=dict)
    metadata: JsonDict = field(default_factory=dict)
    created_at_utc: str = field(default_factory=now_utc_iso)
    schema_version: int = ROLLOUT_STORE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        RolloutKey(self.prompt_id, self.model_version, self.env_id)
        _require_nonempty_string(self.rollout_id, "rollout_id")
        if self.schema_version != ROLLOUT_STORE_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported rollout schema_version {self.schema_version}; "
                f"expected {ROLLOUT_STORE_SCHEMA_VERSION}"
            )
        if self.reward is not None:
            float(self.reward)
        if not isinstance(self.metrics, dict):
            raise ValueError("metrics must be a mapping")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a mapping")

    @property
    def key(self) -> RolloutKey:
        return RolloutKey(
            prompt_id=self.prompt_id,
            model_version=self.model_version,
            env_id=self.env_id,
        )

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RolloutTrace":
        payload = dict(data)
        key = RolloutKey.from_mapping(payload)
        raw_trace = payload.get("trace") or []
        if not isinstance(raw_trace, Sequence) or isinstance(raw_trace, (str, bytes, bytearray)):
            raise ValueError("trace must be a list of mapping turns")
        trace: list[JsonDict] = []
        for index, turn in enumerate(raw_trace):
            if not isinstance(turn, Mapping):
                raise ValueError(f"trace[{index}] must be a mapping")
            trace.append(dict(turn))
        rollout_id = str(payload.get("rollout_id") or stable_rollout_id(payload))
        reward = payload.get("reward")
        return cls(
            prompt_id=key.prompt_id,
            model_version=key.model_version,
            env_id=key.env_id,
            rollout_id=rollout_id,
            trace=tuple(trace),
            reward=float(reward) if reward is not None else None,
            terminal_reason=(
                str(payload["terminal_reason"])
                if payload.get("terminal_reason") is not None
                else None
            ),
            metrics=dict(payload.get("metrics") or {}),
            metadata=dict(payload.get("metadata") or {}),
            created_at_utc=str(payload.get("created_at_utc") or now_utc_iso()),
            schema_version=int(payload.get("schema_version") or ROLLOUT_STORE_SCHEMA_VERSION),
        )

    def to_jsonable(self) -> JsonDict:
        out = {
            "schema_version": self.schema_version,
            "prompt_id": self.prompt_id,
            "model_version": self.model_version,
            "env_id": self.env_id,
            "rollout_id": self.rollout_id,
            "created_at_utc": self.created_at_utc,
            "trace": list(self.trace),
            "metrics": dict(self.metrics),
            "metadata": dict(self.metadata),
        }
        if self.reward is not None:
            out["reward"] = self.reward
        if self.terminal_reason is not None:
            out["terminal_reason"] = self.terminal_reason
        return out


class LocalRolloutStore:
    """Append-only local JSONL store with a materialized key index."""

    def __init__(
        self,
        root: Path | str,
        *,
        rollouts_filename: str = DEFAULT_ROLLOUTS_FILENAME,
        index_filename: str = DEFAULT_INDEX_FILENAME,
    ) -> None:
        self.root = Path(root)
        self.rollouts_path = self.root / rollouts_filename
        self.index_path = self.root / index_filename

    def write(self, trace: Mapping[str, Any] | RolloutTrace) -> RolloutTrace:
        """Append one trace and update the on-disk index."""

        record = trace if isinstance(trace, RolloutTrace) else RolloutTrace.from_mapping(trace)
        self.root.mkdir(parents=True, exist_ok=True)
        index = self.load_or_rebuild_index()
        by_rollout_id = index["by_rollout_id"]
        if record.rollout_id in by_rollout_id:
            raise ValueError(f"duplicate rollout_id {record.rollout_id!r}")
        line_number = int(index["record_count"])
        with self.rollouts_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_jsonable(), sort_keys=True, ensure_ascii=False) + "\n")

        token = key_to_index_token(record.key)
        index["record_count"] = line_number + 1
        index["by_rollout_id"][record.rollout_id] = line_number
        index["by_key"].setdefault(token, []).append(line_number)
        self._write_index(index)
        return record

    def get(self, prompt_id: str, model_version: str, env_id: str) -> list[RolloutTrace]:
        """Return traces matching the central tuple key."""

        key = RolloutKey(prompt_id=prompt_id, model_version=model_version, env_id=env_id)
        index = self.load_or_rebuild_index()
        line_numbers = index["by_key"].get(key_to_index_token(key), [])
        return [self._read_line_number(line_number) for line_number in line_numbers]

    def get_by_rollout_id(self, rollout_id: str) -> RolloutTrace | None:
        index = self.load_or_rebuild_index()
        line_number = index["by_rollout_id"].get(rollout_id)
        if line_number is None:
            return None
        return self._read_line_number(int(line_number))

    def list_keys(self) -> list[RolloutKey]:
        index = self.load_or_rebuild_index()
        keys = []
        for token in index["by_key"]:
            prompt_id, model_version, env_id = json.loads(token)
            keys.append(
                RolloutKey(
                    prompt_id=prompt_id,
                    model_version=model_version,
                    env_id=env_id,
                )
            )
        return sorted(keys)

    def load_or_rebuild_index(self) -> JsonDict:
        if not self.rollouts_path.exists():
            return self._empty_index()
        if not self.index_path.exists():
            return self.rebuild_index()
        with self.index_path.open(encoding="utf-8") as f:
            try:
                index = json.load(f)
            except json.JSONDecodeError:
                return self.rebuild_index()
        if not self._index_matches_rollouts(index):
            return self.rebuild_index()
        return index

    def rebuild_index(self) -> JsonDict:
        index = self._empty_index()
        if not self.rollouts_path.exists():
            self.root.mkdir(parents=True, exist_ok=True)
            self._write_index(index)
            return index

        seen_rollout_ids: set[str] = set()
        with self.rollouts_path.open(encoding="utf-8") as f:
            for line_number, line in enumerate(f):
                if not line.strip():
                    continue
                record = RolloutTrace.from_mapping(json.loads(line))
                if record.rollout_id in seen_rollout_ids:
                    raise ValueError(f"duplicate rollout_id {record.rollout_id!r} in {self.rollouts_path}")
                seen_rollout_ids.add(record.rollout_id)
                token = key_to_index_token(record.key)
                index["by_key"].setdefault(token, []).append(line_number)
                index["by_rollout_id"][record.rollout_id] = line_number
                index["record_count"] = line_number + 1
        self._write_index(index)
        return index

    def iter_all(self) -> Iterable[RolloutTrace]:
        if not self.rollouts_path.exists():
            return
        with self.rollouts_path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield RolloutTrace.from_mapping(json.loads(line))

    def _empty_index(self) -> JsonDict:
        return {
            "schema_version": ROLLOUT_STORE_SCHEMA_VERSION,
            "rollouts_path": self.rollouts_path.name,
            "record_count": 0,
            "by_key": {},
            "by_rollout_id": {},
            "backend": "local_jsonl",
            "follow_up_blockers": [
                "production backend",
                "W&B/lineage stream integration",
                "cluster deployment",
                "retention policy enforcement",
            ],
        }

    def _index_matches_rollouts(self, index: Mapping[str, Any]) -> bool:
        if index.get("schema_version") != ROLLOUT_STORE_SCHEMA_VERSION:
            return False
        if index.get("rollouts_path") != self.rollouts_path.name:
            return False
        line_count = 0
        with self.rollouts_path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    line_count += 1
        return int(index.get("record_count") or -1) == line_count

    def _write_index(self, index: Mapping[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("w", encoding="utf-8") as f:
            json.dump(index, f, sort_keys=True, indent=2, ensure_ascii=False)
            f.write("\n")

    def _read_line_number(self, line_number: int) -> RolloutTrace:
        with self.rollouts_path.open(encoding="utf-8") as f:
            for current, line in enumerate(f):
                if current == line_number:
                    return RolloutTrace.from_mapping(json.loads(line))
        raise IndexError(f"line {line_number} not found in {self.rollouts_path}")


def trace_from_openhands_result(
    result: Any,
    *,
    prompt_id: str,
    model_version: str,
    env_id: str = "swe2_openhands_trace",
    metadata: Mapping[str, Any] | None = None,
) -> RolloutTrace:
    """Convert an OpenHands ``RolloutResult``-like object to store schema."""

    turns = []
    for turn in getattr(result, "turns", ()):
        if hasattr(turn, "__dict__"):
            payload = dict(turn.__dict__)
        elif isinstance(turn, Mapping):
            payload = dict(turn)
        else:
            raise ValueError("OpenHands turn must be dataclass-like or mapping")
        turns.append(payload)
    metrics = {
        "turn_count": int(getattr(result, "turn_count")),
        "elapsed_s": float(getattr(result, "elapsed_s")),
    }
    payload = {
        "prompt_id": prompt_id,
        "model_version": model_version,
        "env_id": env_id,
        "reward": float(getattr(result, "reward")),
        "terminal_reason": str(getattr(result, "terminal_reason")),
        "trace": turns,
        "metrics": metrics,
        "metadata": {
            "source": "openhands_loop",
            "instance_id": getattr(result, "instance_id"),
            "submitted_patch_present": bool(getattr(result, "submitted_patch")),
            **dict(metadata or {}),
        },
    }
    return RolloutTrace.from_mapping(payload)
