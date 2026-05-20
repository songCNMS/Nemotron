# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""OpenHands loop wrapper protocol + fake stub (task070 Session 1).

Lifted out of task017 Session 2 (the renamed task070 — see roadmap
note). The wrapper sits between ``stage2_rl/stage2_swe2/train.py`` (or
its NeMo-Gym agent shim) and the upstream OpenHands library, adding
Nemotron-specific concerns:

- **Sandbox watchdog enforcement** — every shell command the agent
  emits flows through ``m1_swe2.sandbox_watchdog.enforce_subprocess``
  (task017 Session 2 ✓). Blocked commands turn into a terminal
  rollout with reward 0 and ``terminal_reason='policy_violation'``.
- **Per-turn telemetry** — emit per-turn dicts matching task021
  Session 1 telemetry contract (always includes ``latency_ms``;
  per-turn fields for ``tool_name`` / ``argument_dict`` /
  ``observation_length_chars``).
- **Bounded rollout** — respect ``agent_max_turns`` (default 200 from
  stage2_swe2 config) and per-instance ``timeout_s`` (default
  3600). A run that hits the bound terminates with reward 0 and
  ``terminal_reason='turn_budget'`` / ``'timeout'``.
- **Failure modes never crash the batch** — container_crash /
  tool_schema_mismatch / timeout / policy_violation produce
  ``RolloutResult(reward=0)``, never raise. The terminal_reason field
  surfaces the why for downstream dashboards.

Session 1 is the interface + fake stub for sandbox testing. Session 2
implements ``OpenHandsLoopAdapter`` against the real upstream library;
Session 3 cluster smoke. The Session 1 fake gives the
``stage2_swe2/train.py`` wiring something to call before the real
library lands, so the integration path is testable end-to-end without
a SIF container.
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol


# Terminal reasons enumerated as constants so the dashboard can split
# rollouts by failure mode without parsing strings. Each value matches
# a possible ``RolloutResult.terminal_reason``.
TERMINAL_SOLVED = "solved"
TERMINAL_PATCH_REJECTED = "patch_rejected"
TERMINAL_TESTS_FAILED = "tests_failed"
TERMINAL_TURN_BUDGET = "turn_budget"
TERMINAL_TIMEOUT = "timeout"
TERMINAL_POLICY_VIOLATION = "policy_violation"
TERMINAL_CONTAINER_CRASH = "container_crash"
TERMINAL_TOOL_SCHEMA_MISMATCH = "tool_schema_mismatch"
TERMINAL_REASON_UNKNOWN = "unknown"


VALID_TERMINAL_REASONS: frozenset[str] = frozenset({
    TERMINAL_SOLVED,
    TERMINAL_PATCH_REJECTED,
    TERMINAL_TESTS_FAILED,
    TERMINAL_TURN_BUDGET,
    TERMINAL_TIMEOUT,
    TERMINAL_POLICY_VIOLATION,
    TERMINAL_CONTAINER_CRASH,
    TERMINAL_TOOL_SCHEMA_MISMATCH,
    TERMINAL_REASON_UNKNOWN,
})


@dataclass(frozen=True)
class Instance:
    """One SWE-Bench-style task to roll out against.

    Carries the SIF container handle (resolved via
    ``swe2_sif_registry``), the issue payload, and the per-instance
    deadline. The wrapper drives the agent loop until the agent submits
    a patch, hits the turn budget, or hits the timeout.
    """

    instance_id: str
    repo: str
    problem_statement: str
    sif_path: str  # Resolved by `swe2_sif_registry.resolve_sif_path`
    agent_max_turns: int = 200
    timeout_s: float = 3600.0


@dataclass(frozen=True)
class TurnRecord:
    """One agent turn's record for the rollout store.

    Schema lines up with task021 Session 1 telemetry contract — every
    turn carries ``latency_ms`` at minimum. ``tool_name`` /
    ``argument_dict`` / ``observation_length_chars`` are SWE2-specific
    extensions the rollout store treats as opaque payload.
    """

    turn_index: int
    tool_name: str
    argument_dict: dict[str, Any]
    observation_length_chars: int
    latency_ms: float
    blocked_by_watchdog: bool = False


@dataclass(frozen=True)
class RolloutResult:
    """Final output of one wrapper rollout against a single instance.

    ``reward`` is binary 0.0 / 1.0 per the SWE2 ``openhands_loop``
    verifier (patch applies AND tests pass). Anything that's not a
    clean solve produces reward 0 — the ``terminal_reason`` field
    surfaces the why.

    ``turns`` is the full per-turn log; the rollout store consumes
    these to compute aggregate statistics (trajectory_turns,
    sandbox_violations, mean latency) without re-parsing the rollout.
    """

    instance_id: str
    reward: float
    terminal_reason: str
    turn_count: int
    submitted_patch: str | None
    elapsed_s: float
    turns: tuple[TurnRecord, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.terminal_reason not in VALID_TERMINAL_REASONS:
            raise ValueError(
                f"terminal_reason must be one of {sorted(VALID_TERMINAL_REASONS)}, "
                f"got {self.terminal_reason!r}"
            )
        if self.reward not in (0.0, 1.0):
            raise ValueError(
                f"reward must be binary 0.0/1.0 per openhands_loop verifier; got {self.reward}"
            )


class OpenHandsLoop(Protocol):
    """Wrapper interface the SWE2 stage drives against.

    Structural protocol — no ABC inheritance needed. The production
    ``OpenHandsLoopAdapter`` (Session 2) and the
    ``FakeOpenHandsLoop`` test stub both satisfy this contract.

    Lifecycle: ``start(instance)`` → repeated ``step()`` returning an
    action → optionally ``submit_patch(patch)`` → ``close()`` releases
    container resources. The caller doesn't manage turn counting or
    the policy decision; the wrapper owns the loop.
    """

    def rollout(self, instance: Instance) -> RolloutResult:
        """Run the full agent loop against *instance*; return result.

        Implementation MUST:
        - Bound the loop by ``instance.agent_max_turns`` and
          ``instance.timeout_s``.
        - Route every shell command through
          ``sandbox_watchdog.enforce_subprocess`` against a policy.
        - Emit per-turn ``TurnRecord`` entries.
        - Return a ``RolloutResult`` with reward 0 on any failure
          (never raise).
        """
        ...


@dataclass
class _CannedScript:
    """One pre-programmed trajectory the fake plays back.

    ``turns`` is a list of ``(tool_name, arguments, observation)``
    tuples; ``terminal_reason`` is what the rollout terminates with
    after the canned turns are exhausted.
    """

    turns: list[tuple[str, dict[str, Any], str]]
    terminal_reason: str
    submitted_patch: str | None
    reward: float


class FakeOpenHandsLoop:
    """Deterministic test stub satisfying ``OpenHandsLoop``.

    Plays back a canned trajectory provided at construction; threads
    every shell command through the supplied watchdog policy so the
    blocked-command path is exercisable in tests.

    Construct via:
      ``FakeOpenHandsLoop(policy=policy, canned_trajectory=[...], reward=1.0, terminal_reason='solved')``
    """

    def __init__(
        self,
        *,
        policy: Any,  # WatchdogPolicy from sandbox_watchdog
        canned_turns: Sequence[Mapping[str, Any]] | None = None,
        reward: float = 1.0,
        terminal_reason: str = TERMINAL_SOLVED,
        submitted_patch: str | None = None,
        per_turn_latency_ms: float = 5.0,
        clock: Any = None,  # callable returning current time; default time.perf_counter
    ) -> None:
        self._policy = policy
        self._canned_turns = list(canned_turns or [])
        self._reward = reward
        self._terminal_reason = terminal_reason
        self._submitted_patch = submitted_patch
        self._per_turn_latency_ms = per_turn_latency_ms
        self._clock = clock or time.perf_counter

    def rollout(self, instance: Instance) -> RolloutResult:
        from nemotron.recipes.super3.milestones.m1_swe2.sandbox_watchdog import (
            SandboxPolicyViolation,
            is_command_blocked,
        )

        start = self._clock()
        turns: list[TurnRecord] = []
        deadline = start + instance.timeout_s

        for idx, canned in enumerate(self._canned_turns):
            if idx >= instance.agent_max_turns:
                return self._build_result(
                    instance,
                    reward=0.0,
                    terminal_reason=TERMINAL_TURN_BUDGET,
                    turns=turns,
                    submitted_patch=None,
                    elapsed_s=self._clock() - start,
                )
            if self._clock() >= deadline:
                return self._build_result(
                    instance,
                    reward=0.0,
                    terminal_reason=TERMINAL_TIMEOUT,
                    turns=turns,
                    submitted_patch=None,
                    elapsed_s=self._clock() - start,
                )

            tool_name = str(canned.get("tool_name") or "")
            argument_dict = dict(canned.get("argument_dict") or {})
            observation = str(canned.get("observation") or "")

            # Watchdog check for shell-like tool calls. The wrapper
            # treats `run_shell` / `run_tests` as the policy-gated
            # surface; other tools (view_file / search / edit_file)
            # don't invoke a fresh shell from the policy's perspective.
            blocked = False
            if tool_name in ("run_shell", "run_tests"):
                command = argument_dict.get("command") or argument_dict.get("path") or ""
                if command and is_command_blocked(self._policy, command):
                    blocked = True

            turns.append(
                TurnRecord(
                    turn_index=idx,
                    tool_name=tool_name,
                    argument_dict=argument_dict,
                    observation_length_chars=len(observation),
                    latency_ms=self._per_turn_latency_ms,
                    blocked_by_watchdog=blocked,
                )
            )

            if blocked:
                return self._build_result(
                    instance,
                    reward=0.0,
                    terminal_reason=TERMINAL_POLICY_VIOLATION,
                    turns=turns,
                    submitted_patch=None,
                    elapsed_s=self._clock() - start,
                )

        return self._build_result(
            instance,
            reward=self._reward,
            terminal_reason=self._terminal_reason,
            turns=turns,
            submitted_patch=self._submitted_patch,
            elapsed_s=self._clock() - start,
        )

    def _build_result(
        self,
        instance: Instance,
        *,
        reward: float,
        terminal_reason: str,
        turns: list[TurnRecord],
        submitted_patch: str | None,
        elapsed_s: float,
    ) -> RolloutResult:
        return RolloutResult(
            instance_id=instance.instance_id,
            reward=reward,
            terminal_reason=terminal_reason,
            turn_count=len(turns),
            submitted_patch=submitted_patch,
            elapsed_s=elapsed_s,
            turns=tuple(turns),
        )


def aggregate_turn_telemetry(turns: Sequence[TurnRecord]) -> dict[str, Any]:
    """Roll up per-turn records into an aggregate telemetry dict.

    Shape matches task021 Session 1 aggregate contract — numeric
    fields min/mean/max where multi-valued, integer counts where
    discrete. Bridges between the wrapper's per-turn log and the
    rollout store / dashboard.
    """
    if not turns:
        return {
            "trajectory_turns": 0,
            "sandbox_violations": 0,
            "tool_name_counts": {},
            "latency_ms": {"min": 0.0, "mean": 0.0, "max": 0.0},
            "observation_length_chars": {"min": 0, "mean": 0.0, "max": 0},
        }
    tool_name_counts: dict[str, int] = {}
    sandbox_violations = 0
    latencies: list[float] = []
    obs_lengths: list[int] = []
    for record in turns:
        tool_name_counts[record.tool_name] = tool_name_counts.get(record.tool_name, 0) + 1
        if record.blocked_by_watchdog:
            sandbox_violations += 1
        latencies.append(record.latency_ms)
        obs_lengths.append(record.observation_length_chars)
    return {
        "trajectory_turns": len(turns),
        "sandbox_violations": sandbox_violations,
        "tool_name_counts": tool_name_counts,
        "latency_ms": {
            "min": min(latencies),
            "mean": sum(latencies) / len(latencies),
            "max": max(latencies),
        },
        "observation_length_chars": {
            "min": min(obs_lengths),
            "mean": sum(obs_lengths) / len(obs_lengths),
            "max": max(obs_lengths),
        },
    }


__all__ = [
    "FakeOpenHandsLoop",
    "Instance",
    "OpenHandsLoop",
    "RolloutResult",
    "TERMINAL_CONTAINER_CRASH",
    "TERMINAL_PATCH_REJECTED",
    "TERMINAL_POLICY_VIOLATION",
    "TERMINAL_REASON_UNKNOWN",
    "TERMINAL_SOLVED",
    "TERMINAL_TESTS_FAILED",
    "TERMINAL_TIMEOUT",
    "TERMINAL_TOOL_SCHEMA_MISMATCH",
    "TERMINAL_TURN_BUDGET",
    "TurnRecord",
    "VALID_TERMINAL_REASONS",
    "aggregate_turn_telemetry",
]
