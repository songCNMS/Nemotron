import json

from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
    USED_IN_TAG,
    build_blend,
    convert_m0_record,
    prepare,
)


def _base_record(environment: str) -> dict:
    return {
        "environment": environment,
        "question": "Question?",
        "expected_answer": "Answer",
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "System"},
                {"role": "user", "content": "Question?"},
            ],
            "tools": [],
        },
        "reward_config": {"verifier": "normalized_exact_or_contains"},
        "extra_env_info": {},
        "metadata": {
            "source_dataset": "source",
            "source_config": "config",
            "source_revision": "rev",
            "source_id": "id",
            "source_row_index": 3,
            "license": "mit",
            "domain": "reasoning",
            "reward_type": "exact",
            "contamination": "notes",
        },
    }


def test_convert_reasoning_record_uses_reference_solution() -> None:
    record = _base_record("math_reasoning_numeric")
    record["extra_env_info"]["reference_solution"] = "Work it out.\n#### 42"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1] == {"role": "assistant", "content": "Work it out.\n#### 42"}
    assert USED_IN_TAG in converted["used_in"]
    assert converted["metadata"]["m0_environment"] == "math_reasoning_numeric"
    assert converted["metadata"]["m1_stage"] == "Agentic SFT v0"


def test_convert_code_record_uses_reference_code() -> None:
    record = _base_record("code_execution_python")
    record["extra_env_info"]["reference_code"] = "def answer():\n    return 42"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1]["content"] == "def answer():\n    return 42"
    assert converted["metadata"]["m0_split"] == "train"


def test_convert_tool_record_preserves_tools_and_tool_calls() -> None:
    record = _base_record("general_tool_calling")
    record["responses_create_params"]["tools"] = [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Lookup.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
            },
        }
    ]
    record["expected_answer"] = [{"type": "function", "function": {"name": "lookup", "arguments": {"query": "x"}}}]
    record["extra_env_info"]["expected_tool_calls"] = record["expected_answer"]

    converted = convert_m0_record(record, split="train")

    assert converted["tools"][0]["function"]["name"] == "lookup"
    assert converted["messages"][-1]["tool_calls"][0]["function"]["arguments"] == {"query": "x"}
    assert converted["messages"][-1]["content"] == ""


def test_build_blend_points_to_train_jsonl() -> None:
    blend = build_blend("/tmp/train.jsonl")

    assert blend["datasets"][0]["name"] == "m1-agentic-sft-v0-from-m0"
    assert blend["datasets"][0]["path"] == "/tmp/train.jsonl"


def test_prepare_writes_train_shadow_and_blend(tmp_path) -> None:
    m0_root = tmp_path / "m0"
    env_dir = m0_root / "math_reasoning_numeric"
    env_dir.mkdir(parents=True)
    record = _base_record("math_reasoning_numeric")
    record["extra_env_info"]["reference_solution"] = "#### 42"
    for split in ("train", "val"):
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            json.dump(record, f)
            f.write("\n")

    class Args:
        m0_input_dir = m0_root
        output_dir = tmp_path / "out"
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert manifest["counts"]["train"] == {"math_reasoning_numeric": 1}
    assert manifest["counts"]["val_shadow"] == {"math_reasoning_numeric": 1}
    assert (Args.output_dir / "agentic_sft_v0_train.jsonl").exists()
    assert (Args.output_dir / "agentic_sft_v0_val_shadow.jsonl").exists()
    assert (Args.output_dir / "data_blend_agentic_sft_v0.json").exists()
