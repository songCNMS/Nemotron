"""Tests for the OpenHands loop wrapper (task070 Session 1).

Covers:

- ``Instance`` / ``TurnRecord`` / ``RolloutResult`` dataclass surface +
  invariants (reward must be 0/1; terminal_reason from validated set)
- ``OpenHandsLoop`` Protocol — ``FakeOpenHandsLoop`` satisfies it
- ``FakeOpenHandsLoop.rollout`` happy path → reward 1, terminal=solved
- Bounded rollout: turn budget exceeded → reward 0, terminal=turn_budget
- Bounded rollout: timeout exceeded → reward 0, terminal=timeout
- Watchdog integration: blocked shell command → reward 0,
  terminal=policy_violation, turn record marks blocked
- Per-turn telemetry: tool_name / argument_dict /
  observation_length_chars / latency_ms captured
- ``aggregate_turn_telemetry`` matches task021 Session 1 aggregate
  contract shape
"""

from __future__ import annotations

import pytest


from nemotron.recipes.super3.milestones.m1_swe2.openhands_loop import (  # noqa: E402
    TERMINAL_CONTAINER_CRASH,
    TERMINAL_POLICY_VIOLATION,
    TERMINAL_SOLVED,
    TERMINAL_TIMEOUT,
    TERMINAL_TURN_BUDGET,
    VALID_TERMINAL_REASONS,
    FakeOpenHandsLoop,
    Instance,
    OpenHandsLoop,
    RolloutResult,
    TurnRecord,
    aggregate_turn_telemetry,
)
from nemotron.recipes.super3.milestones.m1_swe2.sandbox_watchdog import (  # noqa: E402
    WatchdogPolicy,
)


def _permissive_policy() -> WatchdogPolicy:
    """Watchdog that allows everything — for happy-path tests."""
    return WatchdogPolicy(command_blocklist=(), network_policy="allow")


def _restrictive_policy() -> WatchdogPolicy:
    """Watchdog that blocks `rm -rf /` — for policy-violation tests."""
    return WatchdogPolicy(
        command_blocklist=(("rm", "-rf", "/"),),
        network_policy="deny",
    )


def _instance(
    *,
    instance_id: str = "owner__repo-1",
    agent_max_turns: int = 200,
    timeout_s: float = 3600.0,
) -> Instance:
    return Instance(
        instance_id=instance_id,
        repo="owner/repo",
        problem_statement="Fix the bug.",
        sif_path="/fake/path.sif",
        agent_max_turns=agent_max_turns,
        timeout_s=timeout_s,
    )


# ---------- Dataclass surface ----------


def test_valid_terminal_reasons_cover_expected_outcomes() -> None:
    """Lock the enum so dashboards can split rollouts by terminal_reason
    without parsing strings. Adding a new reason needs an explicit
    test update."""
    assert "solved" in VALID_TERMINAL_REASONS
    assert "patch_rejected" in VALID_TERMINAL_REASONS
    assert "tests_failed" in VALID_TERMINAL_REASONS
    assert "turn_budget" in VALID_TERMINAL_REASONS
    assert "timeout" in VALID_TERMINAL_REASONS
    assert "policy_violation" in VALID_TERMINAL_REASONS
    assert "container_crash" in VALID_TERMINAL_REASONS
    assert "tool_schema_mismatch" in VALID_TERMINAL_REASONS


def test_rollout_result_rejects_non_binary_reward() -> None:
    """openhands_loop is a BINARY verifier per task017 swe2 spec. A
    fractional reward indicates the wrapper / verifier mis-implemented
    the contract."""
    with pytest.raises(ValueError, match="binary"):
        RolloutResult(
            instance_id="x",
            reward=0.5,  # invalid
            terminal_reason=TERMINAL_SOLVED,
            turn_count=1,
            submitted_patch=None,
            elapsed_s=1.0,
        )


def test_rollout_result_rejects_unknown_terminal_reason() -> None:
    with pytest.raises(ValueError, match="terminal_reason"):
        RolloutResult(
            instance_id="x",
            reward=0.0,
            terminal_reason="ate_my_homework",  # invalid
            turn_count=1,
            submitted_patch=None,
            elapsed_s=1.0,
        )


def test_rollout_result_accepts_valid_binary_outcomes() -> None:
    win = RolloutResult(
        instance_id="x",
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
        turn_count=3,
        submitted_patch="diff --git ...",
        elapsed_s=1.0,
    )
    assert win.reward == 1.0
    lose = RolloutResult(
        instance_id="x",
        reward=0.0,
        terminal_reason=TERMINAL_TIMEOUT,
        turn_count=200,
        submitted_patch=None,
        elapsed_s=3600.0,
    )
    assert lose.reward == 0.0


# ---------- Protocol satisfaction ----------


def test_fake_openhands_loop_satisfies_protocol() -> None:
    """Structural Protocol — FakeOpenHandsLoop satisfies it by
    duck-typing without an explicit base class."""
    fake: OpenHandsLoop = FakeOpenHandsLoop(policy=_permissive_policy())
    assert hasattr(fake, "rollout")
    assert callable(fake.rollout)


# ---------- Happy path ----------


def test_rollout_happy_path_returns_reward_1_and_terminal_solved() -> None:
    fake = FakeOpenHandsLoop(
        policy=_permissive_policy(),
        canned_turns=[
            {"tool_name": "view_file", "argument_dict": {"path": "src/main.py"}, "observation": "...code..."},
            {"tool_name": "edit_file", "argument_dict": {"path": "src/main.py", "old_text": "a", "new_text": "b"}, "observation": "ok"},
            {"tool_name": "run_tests", "argument_dict": {"path": "tests/"}, "observation": "passed"},
        ],
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
        submitted_patch="diff --git a/src/main.py b/src/main.py\n...",
    )
    result = fake.rollout(_instance())
    assert result.reward == 1.0
    assert result.terminal_reason == TERMINAL_SOLVED
    assert result.turn_count == 3
    assert result.submitted_patch and "diff --git" in result.submitted_patch


def test_rollout_captures_per_turn_telemetry() -> None:
    """Each turn produces a TurnRecord with tool_name / argument_dict /
    observation_length_chars / latency_ms — matches task021 Session 1
    telemetry contract."""
    fake = FakeOpenHandsLoop(
        policy=_permissive_policy(),
        canned_turns=[
            {"tool_name": "view_file", "argument_dict": {"path": "a.py"}, "observation": "abc"},
            {"tool_name": "edit_file", "argument_dict": {"path": "a.py", "old_text": "x", "new_text": "y"}, "observation": "ok"},
        ],
    )
    result = fake.rollout(_instance())
    assert len(result.turns) == 2
    assert result.turns[0].tool_name == "view_file"
    assert result.turns[0].argument_dict == {"path": "a.py"}
    assert result.turns[0].observation_length_chars == 3  # "abc"
    assert result.turns[0].latency_ms > 0
    assert result.turns[0].turn_index == 0
    assert result.turns[1].turn_index == 1


# ---------- Bounded rollout ----------


def test_rollout_terminates_with_turn_budget_when_exceeded() -> None:
    """200-turn budget; supply 5 canned turns — but cap the instance at
    3. Rollout terminates at turn 3 with reward 0 + turn_budget."""
    fake = FakeOpenHandsLoop(
        policy=_permissive_policy(),
        canned_turns=[
            {"tool_name": "view_file", "argument_dict": {"path": f"{i}.py"}, "observation": "x"}
            for i in range(5)
        ],
        reward=1.0,  # would be solved if it ran to completion
        terminal_reason=TERMINAL_SOLVED,
    )
    result = fake.rollout(_instance(agent_max_turns=3))
    assert result.reward == 0.0
    assert result.terminal_reason == TERMINAL_TURN_BUDGET
    assert result.turn_count == 3


def test_rollout_terminates_with_timeout_when_clock_exceeds_budget() -> None:
    """Inject a clock that jumps past the deadline on the 2nd turn —
    rollout terminates with reward 0 + timeout."""
    clock_values = iter([0.0, 100.0, 200.0, 5000.0, 5001.0])  # 4th call past 3600

    def fake_clock() -> float:
        return next(clock_values)

    fake = FakeOpenHandsLoop(
        policy=_permissive_policy(),
        canned_turns=[
            {"tool_name": "view_file", "argument_dict": {"path": "a.py"}, "observation": "ok"}
            for _ in range(5)
        ],
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
        clock=fake_clock,
    )
    result = fake.rollout(_instance(timeout_s=3600.0))
    assert result.reward == 0.0
    assert result.terminal_reason == TERMINAL_TIMEOUT


# ---------- Watchdog integration ----------


def test_rollout_terminates_with_policy_violation_when_shell_blocked() -> None:
    """Blocked command turns into reward 0 + terminal=policy_violation;
    the turn record marks the command as blocked so the dashboard can
    split policy_violation rollouts from real test failures."""
    fake = FakeOpenHandsLoop(
        policy=_restrictive_policy(),
        canned_turns=[
            {"tool_name": "view_file", "argument_dict": {"path": "a.py"}, "observation": "x"},
            {"tool_name": "run_shell", "argument_dict": {"command": "rm -rf /"}, "observation": ""},
            {"tool_name": "run_tests", "argument_dict": {"path": "tests/"}, "observation": "would pass"},
        ],
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
    )
    result = fake.rollout(_instance())
    assert result.reward == 0.0
    assert result.terminal_reason == TERMINAL_POLICY_VIOLATION
    # The blocked turn IS in the log — operator can audit
    assert result.turn_count == 2
    assert result.turns[-1].tool_name == "run_shell"
    assert result.turns[-1].blocked_by_watchdog is True


def test_rollout_does_not_block_safe_shell_commands() -> None:
    """`ls` against the restrictive policy is fine; only `rm -rf /` is
    blocked. Make sure the watchdog gate isn't false-positive on
    everything."""
    fake = FakeOpenHandsLoop(
        policy=_restrictive_policy(),
        canned_turns=[
            {"tool_name": "run_shell", "argument_dict": {"command": "ls -la"}, "observation": "files"},
            {"tool_name": "run_tests", "argument_dict": {"path": "tests/test_x.py"}, "observation": "ok"},
        ],
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
    )
    result = fake.rollout(_instance())
    assert result.reward == 1.0
    assert result.turns[0].blocked_by_watchdog is False
    assert result.turns[1].blocked_by_watchdog is False


def test_rollout_does_not_send_view_or_search_through_watchdog() -> None:
    """`view_file` / `search` / `edit_file` don't invoke a shell from
    the policy's perspective — they go through the sandboxed Python
    runtime, not a fresh subprocess. Confirm those tools never trigger
    a blocked_by_watchdog flag even under a restrictive policy."""
    fake = FakeOpenHandsLoop(
        policy=_restrictive_policy(),
        canned_turns=[
            {"tool_name": "view_file", "argument_dict": {"path": "rm.py"}, "observation": "file contents"},
            {"tool_name": "search", "argument_dict": {"query": "rm -rf /"}, "observation": "no hits"},
            {"tool_name": "edit_file", "argument_dict": {"path": "a.py", "old_text": "x", "new_text": "y"}, "observation": "ok"},
        ],
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
    )
    result = fake.rollout(_instance())
    assert result.reward == 1.0
    assert all(not t.blocked_by_watchdog for t in result.turns)


# ---------- Failure modes don't crash the batch ----------


def test_rollout_can_terminate_with_container_crash_via_canned_terminal_reason() -> None:
    """The fake supports any terminal_reason at construction; verify
    container_crash flows through (the contract: wrapper produces
    RolloutResult, never raises)."""
    fake = FakeOpenHandsLoop(
        policy=_permissive_policy(),
        canned_turns=[
            {"tool_name": "run_shell", "argument_dict": {"command": "make build"}, "observation": "crash"},
        ],
        reward=0.0,
        terminal_reason=TERMINAL_CONTAINER_CRASH,
    )
    result = fake.rollout(_instance())
    assert result.reward == 0.0
    assert result.terminal_reason == TERMINAL_CONTAINER_CRASH


# ---------- aggregate_turn_telemetry ----------


def test_aggregate_telemetry_empty_turns_returns_zero_baseline() -> None:
    out = aggregate_turn_telemetry([])
    assert out["trajectory_turns"] == 0
    assert out["sandbox_violations"] == 0
    assert out["tool_name_counts"] == {}
    assert out["latency_ms"] == {"min": 0.0, "mean": 0.0, "max": 0.0}


def test_aggregate_telemetry_counts_tool_names_and_violations() -> None:
    turns = [
        TurnRecord(turn_index=0, tool_name="view_file", argument_dict={}, observation_length_chars=10, latency_ms=2.0),
        TurnRecord(turn_index=1, tool_name="view_file", argument_dict={}, observation_length_chars=20, latency_ms=4.0),
        TurnRecord(turn_index=2, tool_name="edit_file", argument_dict={}, observation_length_chars=5, latency_ms=6.0),
        TurnRecord(turn_index=3, tool_name="run_shell", argument_dict={}, observation_length_chars=0, latency_ms=8.0, blocked_by_watchdog=True),
    ]
    out = aggregate_turn_telemetry(turns)
    assert out["trajectory_turns"] == 4
    assert out["sandbox_violations"] == 1
    assert out["tool_name_counts"] == {"view_file": 2, "edit_file": 1, "run_shell": 1}
    assert out["latency_ms"]["min"] == 2.0
    assert out["latency_ms"]["max"] == 8.0
    assert out["latency_ms"]["mean"] == pytest.approx(5.0)
    assert out["observation_length_chars"]["max"] == 20
    assert out["observation_length_chars"]["min"] == 0


def test_aggregate_telemetry_shape_matches_task021_contract() -> None:
    """task021 Session 1 telemetry contract: numeric fields as
    min/mean/max dicts; discrete counts as integers; tool_name_counts
    as a tool_name → int dict. Lock the SHAPE so the dashboard rendering
    doesn't break."""
    turns = [
        TurnRecord(turn_index=0, tool_name="view_file", argument_dict={}, observation_length_chars=10, latency_ms=2.0),
    ]
    out = aggregate_turn_telemetry(turns)
    assert isinstance(out["trajectory_turns"], int)
    assert isinstance(out["sandbox_violations"], int)
    assert isinstance(out["tool_name_counts"], dict)
    assert set(out["latency_ms"].keys()) == {"min", "mean", "max"}
    assert set(out["observation_length_chars"].keys()) == {"min", "mean", "max"}
