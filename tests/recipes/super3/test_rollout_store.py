"""Tests for task032 Session 1 repo-local rollout store scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m1_swe2.openhands_loop import (
    RolloutResult,
    TERMINAL_SOLVED,
    TurnRecord,
)
from nemotron.recipes.super3.milestones.rollout_store import (
    LocalRolloutStore,
    RolloutKey,
    RolloutTrace,
    key_to_index_token,
    stable_rollout_id,
    trace_from_openhands_result,
)


def _trace(
    *,
    prompt_id: str = "prompt-1",
    model_version: str = "model-a@001",
    env_id: str = "terminal_workplace",
    rollout_id: str | None = "rollout-1",
    reward: float = 1.0,
) -> dict:
    payload = {
        "prompt_id": prompt_id,
        "model_version": model_version,
        "env_id": env_id,
        "reward": reward,
        "terminal_reason": "solved",
        "trace": [
            {
                "turn_index": 0,
                "tool_name": "run_shell",
                "argument_dict": {"command": "ls"},
                "observation_length_chars": 4,
                "latency_ms": 2.0,
            }
        ],
        "metrics": {"turn_count": 1},
        "metadata": {"source": "synthetic"},
    }
    if rollout_id is not None:
        payload["rollout_id"] = rollout_id
    return payload


def test_rollout_key_requires_nonempty_tuple_fields() -> None:
    with pytest.raises(ValueError, match="prompt_id"):
        RolloutKey(prompt_id="", model_version="m", env_id="e")
    key = RolloutKey(prompt_id="p", model_version="m", env_id="e")
    assert key_to_index_token(key) == '["p","m","e"]'


def test_rollout_trace_accepts_mapping_and_generates_stable_id() -> None:
    payload = _trace(rollout_id=None)
    trace = RolloutTrace.from_mapping(payload)
    assert trace.rollout_id == stable_rollout_id(payload)
    assert trace.key == RolloutKey("prompt-1", "model-a@001", "terminal_workplace")


def test_local_store_write_creates_jsonl_and_index(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    record = store.write(_trace())
    assert record.rollout_id == "rollout-1"
    assert store.rollouts_path.is_file()
    assert store.index_path.is_file()

    rows = store.rollouts_path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    assert json.loads(rows[0])["prompt_id"] == "prompt-1"

    index = json.loads(store.index_path.read_text(encoding="utf-8"))
    token = key_to_index_token(record.key)
    assert index["by_key"][token] == [0]
    assert index["by_rollout_id"]["rollout-1"] == 0
    assert index["backend"] == "local_jsonl"
    assert "production backend" in index["follow_up_blockers"]


def test_local_store_retrieves_by_prompt_model_env_key(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_trace(rollout_id="r1", prompt_id="p1", model_version="m1", env_id="env-a"))
    store.write(_trace(rollout_id="r2", prompt_id="p1", model_version="m1", env_id="env-a", reward=0.0))
    store.write(_trace(rollout_id="r3", prompt_id="p2", model_version="m1", env_id="env-a"))
    store.write(_trace(rollout_id="r4", prompt_id="p1", model_version="m2", env_id="env-a"))

    matches = store.get("p1", "m1", "env-a")
    assert [record.rollout_id for record in matches] == ["r1", "r2"]
    assert [key.prompt_id for key in store.list_keys()] == ["p1", "p1", "p2"]


def test_local_store_retrieves_by_rollout_id(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_trace(rollout_id="r1"))
    assert store.get_by_rollout_id("r1") is not None
    assert store.get_by_rollout_id("missing") is None


def test_local_store_rejects_duplicate_rollout_id(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_trace(rollout_id="r1"))
    with pytest.raises(ValueError, match="duplicate rollout_id"):
        store.write(_trace(rollout_id="r1"))


def test_local_store_rebuilds_missing_index_from_jsonl(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_trace(rollout_id="r1"))
    store.index_path.unlink()

    rebuilt = store.load_or_rebuild_index()
    assert rebuilt["record_count"] == 1
    assert rebuilt["by_rollout_id"]["r1"] == 0
    assert store.get("prompt-1", "model-a@001", "terminal_workplace")[0].rollout_id == "r1"


def test_iter_all_returns_all_records_in_write_order(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_trace(rollout_id="r1"))
    store.write(_trace(rollout_id="r2", prompt_id="p2"))
    assert [record.rollout_id for record in store.iter_all()] == ["r1", "r2"]


def test_trace_from_openhands_result_preserves_turns_and_metrics() -> None:
    result = RolloutResult(
        instance_id="demo__repo-1",
        reward=1.0,
        terminal_reason=TERMINAL_SOLVED,
        turn_count=1,
        submitted_patch="diff --git ...",
        elapsed_s=12.5,
        turns=(
            TurnRecord(
                turn_index=0,
                tool_name="view_file",
                argument_dict={"path": "a.py"},
                observation_length_chars=10,
                latency_ms=2.0,
            ),
        ),
    )

    trace = trace_from_openhands_result(
        result,
        prompt_id="demo__repo-1",
        model_version="sft-v1",
        metadata={"harness": "openhands"},
    )
    assert trace.env_id == "swe2_openhands_trace"
    assert trace.metrics == {"turn_count": 1, "elapsed_s": 12.5}
    assert trace.metadata["source"] == "openhands_loop"
    assert trace.metadata["submitted_patch_present"] is True
    assert trace.metadata["harness"] == "openhands"
    assert trace.trace[0]["tool_name"] == "view_file"
