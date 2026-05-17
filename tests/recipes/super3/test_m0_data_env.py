import json

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    cleanup_stale_split_files,
    convert_hermes_conversations,
    load_yaml,
    normalize_numeric_answer,
    parse_tool_calls,
    stale_split_files,
    target_files,
    transform_gsm8k_numeric_reasoning,
    transform_hermes_function_calling,
    transform_hotpotqa_search,
    transform_mbpp_code_execution,
    validate_registries,
)


def _spec(dataset_id: str) -> dict:
    registry = load_yaml(DATA_REGISTRY_PATH)
    for dataset in registry["datasets"]:
        if dataset["id"] == dataset_id:
            spec = dict(dataset)
            spec["milestone"] = registry["milestone"]
            return spec
    raise AssertionError(f"missing dataset {dataset_id}")


def test_registries_are_consistent() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)

    validate_registries(data_registry, env_registry)

    assert {dataset["domain"] for dataset in data_registry["datasets"]} == {
        "search",
        "coding",
        "general_tool_calling",
        "reasoning",
    }
    for dataset in data_registry["datasets"]:
        assert dataset["license"]
        assert dataset["hf_revision"]
        assert dataset["use_stage"][0] == "M0 data_env_foundation"


def test_gsm8k_transform_normalizes_final_answer() -> None:
    row = {
        "question": "Natalia sold clips. How many did she sell?",
        "answer": "Natalia sold 48/2 = 24 clips in May.\n#### 24",
    }

    record = transform_gsm8k_numeric_reasoning(row, _spec("m0_reasoning_gsm8k"))

    assert normalize_numeric_answer("#### 1,234 ") == "1234"
    assert record["expected_answer"] == "24"
    assert record["environment"] == "math_reasoning_numeric"
    assert record["responses_create_params"]["input"][0]["role"] == "system"
    assert record["metadata"]["data_stage"] == "M0"


def test_hotpotqa_transform_keeps_context_documents() -> None:
    row = {
        "id": "hp-1",
        "question": "Where was Ada born?",
        "answer": "London",
        "type": "bridge",
        "level": "easy",
        "supporting_facts": {"title": ["Ada"], "sent_id": [0]},
        "context": {
            "title": ["Ada", "London"],
            "sentences": [["Ada was born in London."], ["London is a city."]],
        },
    }

    record = transform_hotpotqa_search(row, _spec("m0_search_hotpotqa"))

    assert record["environment"] == "search_grounded_qa"
    assert record["expected_answer"] == "London"
    assert record["extra_env_info"]["context_documents"][0]["title"] == "Ada"
    assert "Retrieved passages" in record["responses_create_params"]["input"][1]["content"]


def test_mbpp_transform_keeps_tests_for_reward_environment() -> None:
    row = {
        "task_id": 11,
        "prompt": "Write a function that returns the square of a number.",
        "code": "def square(x):\n    return x * x",
        "test_imports": [],
        "test_list": ["assert square(3) == 9"],
    }

    record = transform_mbpp_code_execution(row, _spec("m0_coding_mbpp"))

    assert record["environment"] == "code_execution_python"
    assert record["reward_config"]["verifier"] == "python_unit_tests"
    assert record["extra_env_info"]["test_list"] == ["assert square(3) == 9"]
    assert record["metadata"]["source_id"] == "11"


def test_hermes_parser_and_transform_extract_expected_tool_call() -> None:
    tool_call = '<tool_call>{"name":"lookup","arguments":{"query":"weather"}}</tool_call>'
    tools = [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up information.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
            },
        }
    ]
    row = {
        "id": "tool-1",
        "conversations": [
            {"from": "system", "value": "Use tools when useful."},
            {"from": "human", "value": "What is the weather?"},
            {"from": "gpt", "value": tool_call},
        ],
        "tools": json.dumps(tools),
        "category": "search",
        "subcategory": "lookup",
        "task": "call lookup",
    }

    input_messages, expected = convert_hermes_conversations(row["conversations"])
    record = transform_hermes_function_calling(row, _spec("m0_tool_calling_hermes"))

    assert parse_tool_calls(tool_call)[0]["function"]["name"] == "lookup"
    assert input_messages[-1]["role"] == "user"
    assert expected["expected_tool_calls"][0]["function"]["arguments"] == {"query": "weather"}
    assert record["responses_create_params"]["tools"][0]["function"]["name"] == "lookup"
    assert record["extra_env_info"]["expected_tool_calls"][0]["function"]["name"] == "lookup"


def test_hermes_rejects_row_with_neither_tool_call_nor_assistant_content() -> None:
    """Regression for review finding #1: empty expected used to score 1.0 in oracle baseline."""
    import pytest

    row = {
        "id": "tool-empty",
        "conversations": [
            {"from": "system", "value": "Use tools when useful."},
            {"from": "human", "value": "What is the weather?"},
            {"from": "gpt", "value": "   "},
        ],
        "tools": "[]",
    }

    with pytest.raises(ValueError, match="hermes row has neither"):
        transform_hermes_function_calling(row, _spec("m0_tool_calling_hermes"))


def test_data_registry_specifies_hf_val_split_for_holdout_capable_datasets() -> None:
    """Regression for review finding #4: val rows must come from a real holdout split when available."""
    registry = load_yaml(DATA_REGISTRY_PATH)
    by_id = {dataset["id"]: dataset for dataset in registry["datasets"]}

    assert by_id["m0_reasoning_gsm8k"]["hf_val_split"] == "test"
    assert by_id["m0_coding_mbpp"]["hf_val_split"] == "validation"
    assert by_id["m0_search_hotpotqa"]["hf_val_split"] == "validation"


def test_data_registry_pins_explicit_hf_config_for_hermes() -> None:
    """Regression for review finding #8: hermes hf_config: null is ambiguous on multi-config datasets."""
    registry = load_yaml(DATA_REGISTRY_PATH)
    hermes = next(dataset for dataset in registry["datasets"] if dataset["id"] == "m0_tool_calling_hermes")

    assert hermes["hf_config"] == "func_calling_singleturn"
    assert hermes["hf_config"] is not None


def test_hermes_converter_captures_multi_turn_trajectory() -> None:
    """Regression for review finding #7: convert_hermes_conversations used to drop tool turns and the final answer."""
    first_tool_call = '<tool_call>{"name":"lookup","arguments":{"query":"weather"}}</tool_call>'
    final_answer = "The weather in Paris is sunny."
    conversations = [
        {"from": "system", "value": "Use tools when useful."},
        {"from": "human", "value": "What is the weather in Paris?"},
        {"from": "gpt", "value": first_tool_call},
        {"from": "tool", "value": '{"city":"Paris","weather":"sunny"}'},
        {"from": "gpt", "value": final_answer},
    ]

    input_messages, expected = convert_hermes_conversations(conversations)

    # Input still stops at the first assistant turn — that's what the policy sees.
    assert [message["role"] for message in input_messages] == ["system", "user"]

    # Trajectory keeps every assistant + tool turn after the first user message.
    trajectory = expected["expected_trajectory"]
    assert [turn["role"] for turn in trajectory] == ["assistant", "tool", "assistant"]
    assert trajectory[0]["tool_calls"][0]["function"]["name"] == "lookup"
    assert "Paris" in trajectory[1]["content"]
    assert trajectory[2]["content"] == final_answer
    assert trajectory[2]["tool_calls"] == []

    # First-turn fields stay backward-compatible.
    assert expected["expected_tool_calls"][0]["function"]["name"] == "lookup"
    assert expected["expected_assistant_content"] == ""

    # Final content surfaces the last assistant turn that wasn't a tool call.
    assert expected["expected_final_content"] == final_answer
    assert expected["expected_turn_count"] == 3


def test_cleanup_stale_split_files_removes_unselected_dataset_outputs(tmp_path) -> None:
    full_specs = [{"environment": "search_grounded_qa"}, {"environment": "code_execution_python"}]
    active_specs = [{"environment": "search_grounded_qa"}]
    full_paths = target_files(tmp_path, full_specs)
    active_paths = target_files(tmp_path, active_specs)
    for path in full_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.name.endswith("-split.jsonl"):
            path.write_text("old\n", encoding="utf-8")

    stale_before = stale_split_files(tmp_path, active_paths)
    removed = cleanup_stale_split_files(tmp_path, active_paths)

    assert sorted(removed) == stale_before
    assert not (tmp_path / "code_execution_python" / "train-split.jsonl").exists()
    assert (tmp_path / "search_grounded_qa" / "train-split.jsonl").exists()
