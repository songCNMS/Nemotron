import json

from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
    TOOL_CALLING_SYSTEM_PROMPT,
    USED_IN_TAG,
    build_blend,
    convert_m0_record,
    prepare,
)
from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training import (
    build_plan,
    compute_train_iters,
    render_run_script,
    write_plan,
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
    record["responses_create_params"]["input"][0]["content"] = (
        "You are a function calling AI model.\n<tools>[]</tools>\n"
        '<tool_call>{"name": "lookup", "arguments": {}}</tool_call>'
    )
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

    assert converted["messages"][0] == {"role": "system", "content": TOOL_CALLING_SYSTEM_PROMPT}
    assert "<tools>" not in converted["messages"][0]["content"]
    assert "<tool_call>" not in converted["messages"][0]["content"]
    assert converted["tools"][0]["function"]["name"] == "lookup"
    assert converted["messages"][-1]["tool_calls"][0]["function"]["arguments"] == {"query": "x"}
    assert converted["messages"][-1]["content"] == ""


def test_convert_tool_record_expands_expected_trajectory() -> None:
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
    record["extra_env_info"]["expected_trajectory"] = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"type": "function", "function": {"name": "lookup", "arguments": '{"query": "x"}'}}],
        },
        {"role": "tool", "content": '{"result": "y"}', "tool_calls": []},
        {"role": "assistant", "content": "The result is y.", "tool_calls": []},
    ]

    converted = convert_m0_record(record, split="train")

    assert [message["role"] for message in converted["messages"]] == [
        "system",
        "user",
        "assistant",
        "tool",
        "assistant",
    ]
    assert converted["messages"][2]["tool_calls"][0]["function"]["arguments"] == {"query": "x"}
    assert converted["messages"][3]["content"] == '{"result": "y"}'
    assert converted["messages"][4]["content"] == "The result is y."
    assert "warning" not in converted["metadata"]


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


def test_convert_tool_record_attaches_tool_call_ids() -> None:
    """Regression for review finding B6: chat templates need tool_call_id wiring."""
    record = _base_record("general_tool_calling")
    record["extra_env_info"]["expected_trajectory"] = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "call_0", "type": "function", "function": {"name": "lookup", "arguments": {"q": "x"}}}
            ],
        },
        {"role": "tool", "content": '{"result": "y"}', "tool_calls": []},
        {"role": "assistant", "content": "Done.", "tool_calls": []},
    ]

    converted = convert_m0_record(record, split="train")

    assistant = converted["messages"][2]
    tool = converted["messages"][3]
    assert assistant["tool_calls"][0]["id"] == "call_0"
    assert tool["tool_call_id"] == "call_0"


def test_convert_tool_record_fills_missing_ids_deterministically() -> None:
    """If upstream forgot to set ids, prepare_m1_agentic_sft must generate them."""
    record = _base_record("general_tool_calling")
    record["extra_env_info"]["expected_trajectory"] = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"type": "function", "function": {"name": "lookup", "arguments": {}}}],
        },
        {"role": "tool", "content": "{}", "tool_calls": []},
    ]

    converted = convert_m0_record(record, split="train")
    assistant_call_id = converted["messages"][2]["tool_calls"][0]["id"]
    tool_call_id = converted["messages"][3]["tool_call_id"]
    assert assistant_call_id == tool_call_id == "call_0_0"


def test_convert_tool_record_text_only_final_is_not_warned() -> None:
    """Regression for review finding S5: text-only finals are legitimate."""
    record = _base_record("general_tool_calling")
    record["extra_env_info"]["expected_trajectory"] = [
        {"role": "assistant", "content": "Just the answer.", "tool_calls": []},
    ]

    converted = convert_m0_record(record, split="train")

    assert "warning" not in converted["metadata"]


def test_prepare_requires_m0_input_dir() -> None:
    """Regression for review finding S4: hard-coded user-specific defaults removed."""
    import pytest

    class Args:
        m0_input_dir = None
        output_dir = None
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    with pytest.raises(ValueError, match="--m0-input-dir is required"):
        prepare(Args())


def test_compute_train_iters_from_rows_and_epochs() -> None:
    assert compute_train_iters(
        explicit_train_iters=None,
        train_rows=189,
        global_batch_size=16,
        epochs=2.0,
        fallback=1700,
    ) == 24
    assert compute_train_iters(
        explicit_train_iters=7,
        train_rows=189,
        global_batch_size=16,
        epochs=2.0,
        fallback=1700,
    ) == 7
    assert compute_train_iters(
        explicit_train_iters=None,
        train_rows=None,
        global_batch_size=16,
        epochs=2.0,
        fallback=1700,
    ) == 1700


def test_plan_m1_rejects_multi_node_run(tmp_path) -> None:
    """Regression for review finding B4: planner used to silently emit single-node command."""
    import pytest
    from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training import build_torchrun_command

    manifest = {
        "resources": {"nodes": 4, "gpus_per_node": 8},
        "training": {
            "train_iters": 9,
            "global_batch_size": 4,
            "micro_batch_size": 1,
            "seq_length": 4096,
            "save_interval": 3,
        },
        "paths": {
            "script_path": tmp_path / "train.py",
            "config_path": tmp_path / "config.yaml",
        },
    }
    with pytest.raises(ValueError, match="single-node launch"):
        build_torchrun_command(manifest)


def test_m1_agentic_train_yaml_tokenizer_matches_data_prep_tokenizer() -> None:
    """Regression for review finding B2: training defaults used the Nano tokenizer."""
    import yaml
    from pathlib import Path

    root = Path("src/nemotron/recipes/super3/stage1_sft/config")
    with (root / "data_prep" / "agentic_v0.yaml").open(encoding="utf-8") as f:
        data_prep = yaml.safe_load(f)
    data_prep_tokenizer = data_prep["tokenizer"]["model"]

    for config_name in ("m1_agentic_train.yaml", "m1_agentic_smoke.yaml"):
        with (root / config_name).open(encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert data_prep_tokenizer in cfg["tokenizer"]["tokenizer_model"], (
            f"{config_name} fallback tokenizer must match data prep ({data_prep_tokenizer})"
        )


def test_m1_agentic_train_yaml_pretrained_checkpoint_has_no_string_null_default() -> None:
    """Regression for review finding B3: oc.env default `null` becomes literal string."""
    from pathlib import Path

    for path in (
        Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"),
        Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_smoke.yaml"),
    ):
        text = path.read_text(encoding="utf-8")
        assert "${oc.env:SUPER3_M1_PRETRAINED_CHECKPOINT,null}" not in text, (
            f"{path} still uses ${{oc.env:VAR,null}} which OmegaConf treats as the string 'null'"
        )


def test_plan_m1_training_writes_manifest_and_run_script(tmp_path) -> None:
    packed_root = tmp_path / "packed"
    splits_dir = packed_root / "splits"
    for split in ("train", "valid", "test"):
        split_dir = splits_dir / split
        split_dir.mkdir(parents=True)
        (split_dir / "shard_000000.parquet").write_bytes(b"not-a-real-parquet")
    tokenizer_dir = tmp_path / "tokenizer"
    tokenizer_dir.mkdir()
    checkpoint_dir = tmp_path / "checkpoint"
    checkpoint_dir.mkdir()
    metadata = {
        "type": "SFTDataArtifact",
        "tokenizer_uri": f"file://{tokenizer_dir}",
        "total_sequences": 1200,
        "pack_size": 4096,
    }
    with (splits_dir / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f)

    class Args:
        packed_sft_dir = packed_root
        pretrained_checkpoint = checkpoint_dir
        tokenizer_model = None
        save_dir = tmp_path / "save"
        output_dir = tmp_path / "plans"
        run_name = "unit"
        repo_dir = tmp_path / "repo"
        script_path = "src/nemotron/recipes/super3/stage1_sft/train.py"
        config_path = "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"
        venv = tmp_path / "venv"
        nodes = 1
        gpus_per_node = 2
        epochs = 1.0
        train_iters = 9
        fallback_train_iters = 1700
        global_batch_size = 4
        micro_batch_size = 1
        seq_length = 4096
        save_interval = 3
        allow_missing_checkpoint = False

    manifest = build_plan(Args())
    write_plan(manifest, overwrite=False)
    script = render_run_script(manifest)

    assert manifest["paths"]["packed_sft_dir"] == str(splits_dir)
    assert manifest["paths"]["tokenizer_model"] == str(tokenizer_dir)
    assert manifest["training"]["train_iters"] == 9
    assert manifest["splits"]["train"]["shards"] == 1
    assert "--nproc_per_node=2" in script
    assert "SUPER3_M1_AGENTIC_PACKED_DIR" in script
    assert (Args.output_dir / "unit" / "training_manifest.json").exists()
    assert (Args.output_dir / "unit" / "run_m1_agentic_sft.sh").exists()
