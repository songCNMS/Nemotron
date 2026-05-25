# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox Agentic SFT v1 supervision-builder contract.

Session 1 deliberately stays local and schema-focused. It accepts synthetic or
repo-local ``LocalRolloutStore`` records, identifies failed rollouts, preserves
multi-turn tool/observation structure, and emits repair-supervision examples for
future packed SFT generation. It does not mine production traces, publish W&B
lineage, or launch cluster training.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

JsonDict = dict[str, Any]

AGENTIC_SFT_V1_SCHEMA_VERSION = 1
USED_IN_TAG_V1 = "super3_agentic_sft_v1"
AGENTIC_SFT_V1_STAGE = "Agentic SFT v1"
DEFAULT_SYSTEM_PROMPT = (
    "You are an agentic assistant. Use tools when useful, read observations, "
    "and correct failed attempts before giving the final answer."
)
COMPACT_SYSTEM_PROMPT = (
    "Use concise reasoning. Keep internal deliberation compact while preserving "
    "the tool calls, observations, and final repair action needed to solve the task."
)
SUCCESS_TERMINAL_REASONS = frozenset({"solved", "success", "passed", "pass", "complete"})
DEFAULT_ROUTE_NAME = "generic_agentic_repair"
DEFAULT_ROUTE_ORDER = (
    "swe_openhands_repair",
    "swe_opencode_repair",
    "swe_codex_repair",
    "browser_repair",
    "terminal_repair",
    DEFAULT_ROUTE_NAME,
)

_ROUTE_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "route_name": "swe_openhands_repair",
        "harness": "openhands",
        "family": "swe",
        "aliases": ("openhands", "open_hands", "swe2_openhands"),
        "route_tags": ("cross-harness", "swe", "openhands"),
    },
    {
        "route_name": "swe_opencode_repair",
        "harness": "opencode",
        "family": "swe",
        "aliases": ("opencode", "open_code"),
        "route_tags": ("cross-harness", "swe", "opencode"),
    },
    {
        "route_name": "swe_codex_repair",
        "harness": "codex",
        "family": "swe",
        "aliases": ("codex", "codex_cli"),
        "route_tags": ("cross-harness", "swe", "codex"),
    },
    {
        "route_name": "browser_repair",
        "harness": "browser",
        "family": "browser",
        "aliases": ("browser", "browse", "playwright", "chromium"),
        "route_tags": ("cross-harness", "browser"),
    },
    {
        "route_name": "terminal_repair",
        "harness": "terminal",
        "family": "terminal",
        "aliases": ("terminal", "shell", "bash", "console"),
        "route_tags": ("cross-harness", "terminal"),
    },
)


@dataclass(frozen=True)
class HarnessRoute:
    """Deterministic route for a local multi-turn trace source."""

    route_name: str
    harness: str
    source: str
    family: str
    route_tags: tuple[str, ...] = ()
    reason: str = "default"

    def to_jsonable(self) -> JsonDict:
        return {
            "route_name": self.route_name,
            "harness": self.harness,
            "source": self.source,
            "family": self.family,
            "route_tags": list(self.route_tags),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class FailureRolloutCandidate:
    """One failed rollout selected for repair-supervision construction."""

    prompt_id: str
    model_version: str
    env_id: str
    rollout_id: str
    failure_kind: str
    reward: float | None = None
    terminal_reason: str | None = None
    trace_turn_count: int = 0
    observation_turn_count: int = 0
    metrics: JsonDict = field(default_factory=dict)
    metadata: JsonDict = field(default_factory=dict)

    def to_jsonable(self) -> JsonDict:
        return asdict(self)


@dataclass(frozen=True)
class AgenticSFTV1Example:
    """JSON-friendly chat example produced by the v1 builder contract."""

    messages: tuple[JsonDict, ...]
    metadata: JsonDict
    tools: tuple[JsonDict, ...] = ()
    used_in: tuple[str, ...] = ("super3", USED_IN_TAG_V1, "m1_agentic_sft_v1")
    schema_version: int = AGENTIC_SFT_V1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != AGENTIC_SFT_V1_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported Agentic SFT v1 schema_version {self.schema_version}; "
                f"expected {AGENTIC_SFT_V1_SCHEMA_VERSION}"
            )
        if not self.messages:
            raise ValueError("Agentic SFT v1 example requires messages")
        if not any(message.get("role") == "assistant" for message in self.messages):
            raise ValueError("Agentic SFT v1 example requires assistant supervision")
        object.__setattr__(self, "messages", tuple(dict(message) for message in self.messages))
        object.__setattr__(self, "tools", tuple(dict(tool) for tool in self.tools))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def to_jsonable(self) -> JsonDict:
        return {
            "schema_version": self.schema_version,
            "messages": [dict(message) for message in self.messages],
            "tools": [dict(tool) for tool in self.tools],
            "used_in": list(self.used_in),
            "metadata": dict(self.metadata),
        }


def describe_agentic_sft_v1_schema() -> JsonDict:
    """Return the stable Session 1 schema contract for docs/tests."""

    return {
        "schema_version": AGENTIC_SFT_V1_SCHEMA_VERSION,
        "kind": "agentic_sft_v1_supervision_contract",
        "record_shape": {
            "messages": [
                "system prompt",
                "user task prompt",
                "assistant tool call and/or self-correction turns",
                "tool observation turns",
                "assistant repair target",
            ],
            "metadata": {
                "source_rollout_id": "LocalRolloutStore rollout_id",
                "m0_environment": "rollout env_id",
                "trace_harness": "openhands | opencode | codex | browser | terminal | generic",
                "trace_source": "explicit local source hint or inferred harness",
                "routing_family": "swe | browser | terminal | generic",
                "cross_harness_route": "deterministic route contract",
                "failure_kind": "reward_zero | terminal:<reason> | explicit_failure",
                "supervision_family": "failure_rollout_repair",
                "self_correction": "boolean marker for repair trajectory rows",
                "compact_reasoning_mode": "standard | low_effort | compact",
            },
        },
        "supported_inputs": [
            "LocalRolloutStore.iter_all() records",
            "synthetic RolloutTrace mappings",
        ],
        "out_of_scope": [
            "task013 cluster SFT loss/run verification",
            "task070 and task026 live cross-harness runtime/data collection",
            "OpenHands/OpenCode/Codex production trace mining",
            "packed SFT generation at scale",
            "cluster training run",
            "W&B/lineage publication",
            "eval gate against live M1/M2 checkpoints",
        ],
    }


def infer_harness_route(record: Any) -> HarnessRoute:
    """Infer a stable local route for synthetic multi-turn trace records.

    Routing is intentionally deterministic and sandbox-only. Explicit metadata
    hints such as ``harness`` or ``trace_source`` win over env/tool heuristics;
    no production trace discovery or filesystem mining is performed.
    """

    metadata = _record_metadata(record)
    env_id = _required_text(_record_value(record, "env_id"), "env_id")
    source = _explicit_source(metadata)
    for key in ("harness", "trace_harness", "source_harness", "trace_source", "source"):
        value = metadata.get(key)
        if isinstance(value, str):
            match = _match_route(value)
            if match is not None:
                return _route_from_definition(
                    match,
                    source=source or _clean_source(value),
                    reason=f"metadata:{key}",
                )

    env_match = _match_route(env_id)
    if env_match is not None:
        return _route_from_definition(
            env_match,
            source=source or env_match["harness"],
            reason="env_id",
        )

    for turn in _record_trace(record):
        tool_name = _turn_tool_name(turn, fallback="")
        tool_match = _match_route(tool_name)
        if tool_match is not None:
            return _route_from_definition(
                tool_match,
                source=source or tool_match["harness"],
                reason="trace_tool",
            )

    return HarnessRoute(
        route_name=DEFAULT_ROUTE_NAME,
        harness="generic",
        source=source or "local_synthetic",
        family="generic",
        route_tags=("cross-harness", "generic"),
        reason="default",
    )


def failure_candidate_from_rollout(record: Any) -> FailureRolloutCandidate | None:
    """Return a failure candidate for a failed rollout, otherwise ``None``."""

    reward = _record_value(record, "reward")
    terminal_reason = _optional_text(_record_value(record, "terminal_reason"))
    if not _is_failed_rollout(reward, terminal_reason, _record_metadata(record)):
        return None
    trace = _record_trace(record)
    env_id = _required_text(_record_value(record, "env_id"), "env_id")
    prompt_id = _required_text(_record_value(record, "prompt_id"), "prompt_id")
    model_version = _required_text(_record_value(record, "model_version"), "model_version")
    rollout_id = _required_text(_record_value(record, "rollout_id"), "rollout_id")
    return FailureRolloutCandidate(
        prompt_id=prompt_id,
        model_version=model_version,
        env_id=env_id,
        rollout_id=rollout_id,
        failure_kind=_failure_kind(reward, terminal_reason, _record_metadata(record)),
        reward=float(reward) if reward is not None else None,
        terminal_reason=terminal_reason,
        trace_turn_count=len(trace),
        observation_turn_count=sum(1 for turn in trace if _turn_observation_text(turn)),
        metrics=dict(_record_metrics(record)),
        metadata=dict(_record_metadata(record)),
    )


def build_failure_repair_example(
    record: Any,
    *,
    repair_target: str | Mapping[str, Any] | None = None,
    compact_reasoning_mode: str = "standard",
    include_system_prompt: bool = True,
) -> AgenticSFTV1Example:
    """Convert one failed local rollout into a repair-supervision example."""

    candidate = failure_candidate_from_rollout(record)
    if candidate is None:
        raise ValueError("rollout is not a failed rollout candidate")
    mode = _normalise_compact_mode(compact_reasoning_mode)
    route = infer_harness_route(record)
    messages: list[JsonDict] = []
    if include_system_prompt:
        prompt = DEFAULT_SYSTEM_PROMPT if mode == "standard" else f"{DEFAULT_SYSTEM_PROMPT} {COMPACT_SYSTEM_PROMPT}"
        messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": _prompt_text_from_record(record)})
    messages.extend(_messages_from_trace(_record_trace(record)))
    messages.append(_repair_assistant_message(record, repair_target=repair_target))
    metadata = {
        "m1_stage": AGENTIC_SFT_V1_STAGE,
        "m1_milestone": "M1",
        "m1_use": [
            "multi-turn supervision",
            "failure rollout repair",
            "self-correction trajectory",
            f"{route.family} harness repair",
        ],
        "source_rollout_id": candidate.rollout_id,
        "source_prompt_id": candidate.prompt_id,
        "source_model_version": candidate.model_version,
        "m0_environment": candidate.env_id,
        "trace_harness": route.harness,
        "trace_source": route.source,
        "routing_family": route.family,
        "route_name": route.route_name,
        "route_tags": list(route.route_tags),
        "cross_harness_route": route.to_jsonable(),
        "failure_kind": candidate.failure_kind,
        "reward": candidate.reward,
        "terminal_reason": candidate.terminal_reason,
        "trace_turn_count": candidate.trace_turn_count,
        "observation_turn_count": candidate.observation_turn_count,
        "supervision_family": "failure_rollout_repair",
        "self_correction": True,
        "compact_reasoning_mode": mode,
        "source_metrics": candidate.metrics,
        "source_metadata": candidate.metadata,
        "cluster_execution_required": False,
    }
    return AgenticSFTV1Example(
        messages=tuple(messages),
        tools=tuple(_tools_from_record(record)),
        metadata=metadata,
    )


def build_failure_repair_examples_from_store(
    records: Iterable[Any],
    *,
    repair_targets: Mapping[str, str | Mapping[str, Any]] | None = None,
    compact_reasoning_mode: str = "standard",
    limit: int | None = None,
) -> list[AgenticSFTV1Example]:
    """Build repair examples from ``LocalRolloutStore.iter_all()``-style records."""

    examples: list[AgenticSFTV1Example] = []
    targets = repair_targets or {}
    for record in records:
        candidate = failure_candidate_from_rollout(record)
        if candidate is None:
            continue
        examples.append(
            build_failure_repair_example(
                record,
                repair_target=targets.get(candidate.rollout_id),
                compact_reasoning_mode=compact_reasoning_mode,
            )
        )
        if limit is not None and len(examples) >= limit:
            break
    return examples


def build_routed_failure_repair_examples(
    records: Iterable[Any],
    *,
    repair_targets: Mapping[str, str | Mapping[str, Any]] | None = None,
    compact_reasoning_mode: str = "standard",
    route_order: tuple[str, ...] = DEFAULT_ROUTE_ORDER,
    route_filter: str | None = None,
    limit: int | None = None,
) -> list[AgenticSFTV1Example]:
    """Build failed-rollout examples in deterministic cross-harness route order."""

    targets = repair_targets or {}
    prepared: list[tuple[int, str, str, str, Any, FailureRolloutCandidate, HarnessRoute]] = []
    rank_by_route = {route: index for index, route in enumerate(route_order)}
    for record in records:
        candidate = failure_candidate_from_rollout(record)
        if candidate is None:
            continue
        route = infer_harness_route(record)
        if route_filter is not None and route.route_name != route_filter and route.harness != route_filter:
            continue
        prepared.append(
            (
                rank_by_route.get(route.route_name, len(rank_by_route)),
                candidate.env_id,
                candidate.prompt_id,
                candidate.rollout_id,
                record,
                candidate,
                route,
            )
        )

    examples: list[AgenticSFTV1Example] = []
    # Sort by the first 4 elements only. Tuple element 5+ holds the raw
    # record / candidate / route objects which don't define comparison;
    # rollout_id at position 3 is unique in a well-formed LocalRolloutStore
    # so the fallback never matters today, but an explicit slice avoids
    # a confusing TypeError if a caller ever passes duplicate-id records.
    for _, _, _, _, record, candidate, _ in sorted(prepared, key=lambda item: item[:4]):
        examples.append(
            build_failure_repair_example(
                record,
                repair_target=targets.get(candidate.rollout_id),
                compact_reasoning_mode=compact_reasoning_mode,
            )
        )
        if limit is not None and len(examples) >= limit:
            break
    return examples


def _messages_from_trace(trace: Iterable[Mapping[str, Any]]) -> list[JsonDict]:
    messages: list[JsonDict] = []
    for index, turn in enumerate(trace):
        tool_name = _turn_tool_name(turn, fallback=f"tool_{index}")
        call_id = _turn_call_id(turn, fallback=f"rollout_call_{index}")
        arguments = _turn_arguments(turn)
        messages.append(
            {
                "role": "assistant",
                "content": _turn_assistant_content(turn, tool_name=tool_name),
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {"name": tool_name, "arguments": arguments},
                    }
                ],
            }
        )
        observation = _turn_observation_text(turn)
        if observation:
            messages.append({"role": "tool", "tool_call_id": call_id, "content": observation})
    return messages


def _repair_assistant_message(
    record: Any,
    *,
    repair_target: str | Mapping[str, Any] | None,
) -> JsonDict:
    if repair_target is None:
        metadata = _record_metadata(record)
        repair_target = (
            metadata.get("repair_target")
            or metadata.get("expected_repair")
            or metadata.get("gold_repair")
            or "Revise the failed attempt using the observations above and produce the corrected final answer."
        )
    if isinstance(repair_target, Mapping):
        content = str(repair_target.get("content") or repair_target.get("final_answer") or "").strip()
        out: JsonDict = {"role": "assistant", "content": content}
        tool_calls = repair_target.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            out["tool_calls"] = [dict(call) for call in tool_calls if isinstance(call, Mapping)]
        return out
    return {"role": "assistant", "content": str(repair_target).strip()}


def _record_value(record: Any, field_name: str) -> Any:
    if isinstance(record, Mapping):
        return record.get(field_name)
    return getattr(record, field_name, None)


def _explicit_source(metadata: Mapping[str, Any]) -> str | None:
    for key in ("trace_source", "source", "harness", "trace_harness", "collector"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return _clean_source(value)
    return None


def _clean_source(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _match_route(value: str) -> Mapping[str, Any] | None:
    text = _clean_source(value)
    for definition in _ROUTE_DEFINITIONS:
        for alias in definition["aliases"]:
            if alias in text:
                return definition
    return None


def _route_from_definition(
    definition: Mapping[str, Any],
    *,
    source: str,
    reason: str,
) -> HarnessRoute:
    return HarnessRoute(
        route_name=str(definition["route_name"]),
        harness=str(definition["harness"]),
        source=source,
        family=str(definition["family"]),
        route_tags=tuple(str(tag) for tag in definition["route_tags"]),
        reason=reason,
    )


def _record_trace(record: Any) -> tuple[JsonDict, ...]:
    trace = _record_value(record, "trace") or ()
    if not isinstance(trace, Iterable) or isinstance(trace, (str, bytes, bytearray)):
        raise ValueError("rollout trace must be an iterable of mapping turns")
    out: list[JsonDict] = []
    for index, turn in enumerate(trace):
        if not isinstance(turn, Mapping):
            raise ValueError(f"rollout trace[{index}] must be a mapping")
        out.append(dict(turn))
    return tuple(out)


def _record_metrics(record: Any) -> Mapping[str, Any]:
    metrics = _record_value(record, "metrics") or {}
    if not isinstance(metrics, Mapping):
        raise ValueError("rollout metrics must be a mapping")
    return metrics


def _record_metadata(record: Any) -> Mapping[str, Any]:
    metadata = _record_value(record, "metadata") or {}
    if not isinstance(metadata, Mapping):
        raise ValueError("rollout metadata must be a mapping")
    return metadata


def _tools_from_record(record: Any) -> tuple[JsonDict, ...]:
    metadata = _record_metadata(record)
    tools = metadata.get("tools") or metadata.get("tool_schema") or []
    if not isinstance(tools, list):
        return ()
    return tuple(dict(tool) for tool in tools if isinstance(tool, Mapping))


def _prompt_text_from_record(record: Any) -> str:
    metadata = _record_metadata(record)
    for key in ("prompt", "user_prompt", "task_prompt", "question", "instruction"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Repair failed rollout {rollout_id} for prompt {prompt_id} in env {env_id}.".format(
        rollout_id=_required_text(_record_value(record, "rollout_id"), "rollout_id"),
        prompt_id=_required_text(_record_value(record, "prompt_id"), "prompt_id"),
        env_id=_required_text(_record_value(record, "env_id"), "env_id"),
    )


def _turn_tool_name(turn: Mapping[str, Any], *, fallback: str) -> str:
    for key in ("tool_name", "name"):
        value = turn.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    function = turn.get("function")
    if isinstance(function, Mapping):
        value = function.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _turn_call_id(turn: Mapping[str, Any], *, fallback: str) -> str:
    value = turn.get("tool_call_id") or turn.get("id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _turn_arguments(turn: Mapping[str, Any]) -> JsonDict:
    arguments = turn.get("argument_dict")
    if arguments is None:
        arguments = turn.get("arguments")
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return {}
        return dict(parsed) if isinstance(parsed, Mapping) else {}
    return dict(arguments) if isinstance(arguments, Mapping) else {}


def _turn_assistant_content(turn: Mapping[str, Any], *, tool_name: str) -> str:
    value = turn.get("assistant_content") or turn.get("content")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return f"Call `{tool_name}` and inspect the observation."


def _turn_observation_text(turn: Mapping[str, Any]) -> str:
    for key in ("observation", "observation_text", "result", "output"):
        value = turn.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, Mapping):
            return json.dumps(value, sort_keys=True, ensure_ascii=False)
    length = turn.get("observation_length_chars")
    if length is not None:
        return f"[observation omitted; length_chars={int(length)}]"
    return ""


def _is_failed_rollout(
    reward: Any,
    terminal_reason: str | None,
    metadata: Mapping[str, Any],
) -> bool:
    if bool(metadata.get("explicit_failure")):
        return True
    if reward is not None:
        try:
            if float(reward) <= 0.0:
                return True
        except (TypeError, ValueError):
            pass
    if terminal_reason is None:
        return False
    return terminal_reason.strip().lower() not in SUCCESS_TERMINAL_REASONS


def _failure_kind(reward: Any, terminal_reason: str | None, metadata: Mapping[str, Any]) -> str:
    if bool(metadata.get("explicit_failure")):
        return "explicit_failure"
    if terminal_reason and terminal_reason.strip().lower() not in SUCCESS_TERMINAL_REASONS:
        return f"terminal:{terminal_reason.strip().lower()}"
    if reward is not None:
        try:
            if float(reward) <= 0.0:
                return "reward_zero"
        except (TypeError, ValueError):
            pass
    return "unknown_failure"


def _normalise_compact_mode(mode: str) -> str:
    value = str(mode or "standard").strip().lower()
    if value not in {"standard", "low_effort", "compact"}:
        raise ValueError("compact_reasoning_mode must be standard, low_effort, or compact")
    return value


def _required_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
