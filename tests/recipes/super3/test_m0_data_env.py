import json

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    convert_hermes_conversations,
    load_yaml,
    normalize_numeric_answer,
    parse_tool_calls,
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
