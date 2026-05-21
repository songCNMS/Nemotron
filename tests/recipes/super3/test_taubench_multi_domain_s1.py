"""Tests for task023 Session 1 TauBench multi-domain scaffold.

Session 1 keeps the work sandbox-runnable: retail/telecom record
conversion, env-registry rows, and reuse of the existing
``tool_schema_and_argument_match`` verifier. The TauBench simulator /
multi-turn rollout service remains a cluster follow-up.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SYSTEM_PROMPTS,
    TAUBENCH_DEFAULT_TOOLS,
    load_yaml,
    transform_taubench_multi_domain,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec(env: str) -> dict[str, Any]:
    domain = env.removeprefix("taubench_")
    return {
        "id": f"m0_{env}",
        "environment": env,
        "domain": "taubench",
        "hf_dataset": "sierra-research/tau-bench",
        "hf_config": domain,
        "hf_split": "train",
        "hf_val_split": None,
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://github.com/sierra-research/tau-bench",
        "license": "cc-by-4.0",
        "converter": "taubench_multi_domain",
        "difficulty": f"{domain}_customer_support",
        "reward_type": "tool_schema_and_argument_match",
        "contamination": "synthetic test spec; source pin deferred",
        "contamination_against": ["TauBench retail", "TauBench telecom"],
        "milestone": "M0",
        "use_stage": ["M2 taubench multi-domain expansion"],
    }


def _retail_row() -> dict[str, Any]:
    return {
        "id": "retail-1",
        "domain": "retail",
        "user_message": "Change order O-100 to ship to 1 Main St.",
        "expected_actions": [
            {
                "tool_name": "update_order_address",
                "arguments": {"order_id": "O-100", "address": "1 Main St."},
            }
        ],
        "final_response": "I updated the shipping address.",
    }


def test_taubench_prompts_and_converter_are_registered() -> None:
    assert "taubench_retail" in SYSTEM_PROMPTS
    assert "taubench_telecom" in SYSTEM_PROMPTS
    assert CONVERTERS.get("taubench_multi_domain") is transform_taubench_multi_domain


def test_transform_taubench_retail_emits_tool_call_record() -> None:
    record = transform_taubench_multi_domain(_retail_row(), _spec("taubench_retail"))

    assert record["environment"] == "taubench_retail"
    assert record["question"] == "Change order O-100 to ship to 1 Main St."
    assert record["reward_config"]["verifier"] == "tool_schema_and_argument_match"
    assert record["reward_config"]["multi_turn_rollout"] == "deferred"
    assert record["extra_env_info"]["domain"] == "retail"
    assert record["extra_env_info"]["requires_live_rollout"] is False
    assert record["extra_env_info"]["cluster_execution"] == "deferred_to_task023_session_3"
    assert record["expected_answer"][0]["function"]["name"] == "update_order_address"
    assert record["expected_answer"][0]["function"]["arguments"]["order_id"] == "O-100"
    assert record["extra_env_info"]["expected_trajectory"][0]["tool_calls"] == record["expected_answer"]
    tool_names = {tool["function"]["name"] for tool in record["responses_create_params"]["tools"]}
    assert tool_names == {tool["function"]["name"] for tool in TAUBENCH_DEFAULT_TOOLS["retail"]}


def test_transform_taubench_telecom_accepts_json_encoded_tools_and_calls() -> None:
    tool_call = {
        "name": "update_service_plan",
        "arguments": {"account_id": "A-9", "plan": "unlimited-plus"},
    }
    tools = [
        {
            "type": "function",
            "function": {
                "name": "update_service_plan",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]
    row = {
        "task": "Move account A-9 to unlimited-plus.",
        "tools": json.dumps(tools),
        "tool_calls": json.dumps([tool_call]),
        "expected_trajectory": [{"role": "assistant", "content": "", "tool_calls": [tool_call]}],
    }

    record = transform_taubench_multi_domain(row, _spec("taubench_telecom"))

    assert record["environment"] == "taubench_telecom"
    assert record["extra_env_info"]["domain"] == "telecom"
    assert record["responses_create_params"]["tools"] == tools
    assert record["expected_answer"][0]["function"]["name"] == "update_service_plan"
    assert record["expected_answer"][0]["function"]["arguments"]["plan"] == "unlimited-plus"


def test_transform_taubench_rejects_missing_prompt_or_expected_actions() -> None:
    with pytest.raises(ValueError, match="user task prompt"):
        transform_taubench_multi_domain({"expected_actions": [{"name": "x"}]}, _spec("taubench_retail"))

    with pytest.raises(ValueError, match="expected tool calls"):
        transform_taubench_multi_domain({"user_message": "Do it"}, _spec("taubench_retail"))


def test_taubench_reuses_tool_schema_and_argument_match_verifier() -> None:
    record = transform_taubench_multi_domain(_retail_row(), _spec("taubench_retail"))

    score_ok, diagnostics_ok = score_record(record["expected_answer"], record)
    assert score_ok == 1.0
    assert diagnostics_ok["invalid_tool_call"] is False
    assert diagnostics_ok["argument_match"] is True

    bad_candidate = [
        {
            "type": "function",
            "function": {"name": "refund_order", "arguments": {"order_id": "O-100"}},
        }
    ]
    score_bad, diagnostics_bad = score_record(bad_candidate, record)
    assert score_bad == 0.0
    assert diagnostics_bad["invalid_tool_call"] is False
    assert diagnostics_bad["argument_match"] is False


def test_registry_consistency_holds_with_taubench_env_rows() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_environment_registry_carries_taubench_retail_and_telecom_rows() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    by_id = {env["id"]: env for env in env_registry["environments"]}

    assert {"taubench_retail", "taubench_telecom"} <= set(by_id)
    for env_id in ("taubench_retail", "taubench_telecom"):
        env = by_id[env_id]
        assert env["family"] == "taubench"
        assert env["reward"]["verifier"] == "tool_schema_and_argument_match"
        assert env["resources"]["sandbox"] == "none"
        assert "simulator_deferred" in env["telemetry"]


def test_data_registry_defers_taubench_rows_until_source_pin() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    ids = {dataset["id"] for dataset in data_registry["datasets"]}

    assert "m0_taubench_retail" not in ids
    assert "m0_taubench_telecom" not in ids
