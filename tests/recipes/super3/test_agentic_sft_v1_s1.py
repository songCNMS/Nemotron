"""Tests for task031 Session 1 Agentic SFT v1 builder contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m1_agentic_sft.agentic_sft_v1 import (
    USED_IN_TAG_V1,
    build_failure_repair_example,
    build_failure_repair_examples_from_store,
    describe_agentic_sft_v1_schema,
    failure_candidate_from_rollout,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore


def _failed_rollout() -> dict:
    return {
        "prompt_id": "swe-prompt-1",
        "model_version": "model-a@0001",
        "env_id": "swe2_openhands_trace",
        "rollout_id": "rollout-fail-1",
        "reward": 0.0,
        "terminal_reason": "timeout",
        "trace": [
            {
                "tool_name": "view_file",
                "argument_dict": {"path": "bug.py"},
                "observation": "def broken(): return 1 / 0",
                "latency_ms": 10.0,
            },
            {
                "tool_name": "edit_file",
                "argument_dict": {"path": "bug.py", "old": "1 / 0", "new": "0"},
                "observation_length_chars": 42,
                "latency_ms": 15.0,
            },
        ],
        "metrics": {"turn_count": 2, "elapsed_s": 1.25},
        "metadata": {
            "prompt": "Fix the division-by-zero bug.",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "view_file",
                        "parameters": {"type": "object"},
                    },
                }
            ],
            "repair_target": "The bug is fixed by guarding the zero denominator.",
        },
    }


def test_schema_contract_documents_v1_fields_and_blockers() -> None:
    schema = describe_agentic_sft_v1_schema()

    assert schema["kind"] == "agentic_sft_v1_supervision_contract"
    metadata = schema["record_shape"]["metadata"]
    assert metadata["supervision_family"] == "failure_rollout_repair"
    assert metadata["compact_reasoning_mode"] == "standard | low_effort | compact"
    assert "OpenHands/OpenCode/Codex production trace mining" in schema["out_of_scope"]


def test_failure_candidate_skips_success_and_captures_failed_rollout() -> None:
    failed = failure_candidate_from_rollout(_failed_rollout())
    assert failed is not None
    assert failed.failure_kind == "terminal:timeout"
    assert failed.trace_turn_count == 2
    assert failed.observation_turn_count == 2

    success = dict(_failed_rollout(), reward=1.0, terminal_reason="solved", rollout_id="ok")
    assert failure_candidate_from_rollout(success) is None


def test_builder_preserves_multiturn_tool_observations_and_repair_metadata() -> None:
    example = build_failure_repair_example(_failed_rollout(), compact_reasoning_mode="low_effort")
    payload = example.to_jsonable()

    assert USED_IN_TAG_V1 in payload["used_in"]
    assert payload["metadata"]["m1_stage"] == "Agentic SFT v1"
    assert payload["metadata"]["supervision_family"] == "failure_rollout_repair"
    assert payload["metadata"]["self_correction"] is True
    assert payload["metadata"]["compact_reasoning_mode"] == "low_effort"
    assert payload["metadata"]["source_rollout_id"] == "rollout-fail-1"
    assert payload["metadata"]["cluster_execution_required"] is False

    roles = [message["role"] for message in payload["messages"]]
    assert roles == ["system", "user", "assistant", "tool", "assistant", "tool", "assistant"]
    assert "concise reasoning" in payload["messages"][0]["content"]
    assert payload["messages"][2]["tool_calls"][0]["function"]["name"] == "view_file"
    assert payload["messages"][3]["tool_call_id"] == payload["messages"][2]["tool_calls"][0]["id"]
    assert payload["messages"][5]["content"] == "[observation omitted; length_chars=42]"
    assert payload["messages"][-1]["content"] == "The bug is fixed by guarding the zero denominator."
    assert payload["tools"][0]["function"]["name"] == "view_file"


def test_local_rollout_store_failure_records_convert_to_repair_examples(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_failed_rollout())
    store.write(
        dict(
            _failed_rollout(),
            prompt_id="swe-prompt-2",
            rollout_id="rollout-success-1",
            reward=1.0,
            terminal_reason="solved",
        )
    )

    examples = build_failure_repair_examples_from_store(
        store.iter_all(),
        repair_targets={"rollout-fail-1": "Apply a targeted fix and rerun the failing check."},
        compact_reasoning_mode="compact",
    )

    assert len(examples) == 1
    payload = examples[0].to_jsonable()
    assert payload["metadata"]["source_rollout_id"] == "rollout-fail-1"
    assert payload["metadata"]["compact_reasoning_mode"] == "compact"
    assert payload["messages"][-1]["content"] == "Apply a targeted fix and rerun the failing check."


def test_builder_rejects_non_failed_rollout_and_invalid_compact_mode() -> None:
    success = dict(_failed_rollout(), reward=1.0, terminal_reason="solved")
    with pytest.raises(ValueError, match="not a failed rollout"):
        build_failure_repair_example(success)
    with pytest.raises(ValueError, match="compact_reasoning_mode"):
        build_failure_repair_example(_failed_rollout(), compact_reasoning_mode="verbose")
