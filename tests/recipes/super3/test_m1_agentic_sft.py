import json
from argparse import Namespace

from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training import (
    build_plan,
    compute_train_iters,
    render_run_script,
    write_plan,
)
from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
    DIFFICULTY_HARD,
    DIFFICULTY_TRIVIAL,
    DIFFICULTY_UNKNOWN,
    M1_USE_BY_ENV,
    MATH_BUCKET_FINAL_ANSWER_AUX,
    MATH_BUCKET_FORMAT_REPAIR,
    MATH_BUCKET_HELDOUT_EVAL,
    MATH_BUCKET_VERIFIED_FULL_SOLUTION,
    MATH_FINAL_ANSWER_EFFECTIVE_WEIGHT,
    MATH_FINAL_ANSWER_SIDECAR_NAME,
    MATH_FINAL_ANSWER_SIDECAR_WEIGHT,
    MATH_SUPERVISION_STRATEGY_V3,
    MATH_V3_FINAL_ANSWER_AUX_WEIGHT,
    MATH_V3_FORMAT_REPAIR_WEIGHT,
    MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT,
    TOOL_CALLING_SYSTEM_PROMPT,
    USED_IN_TAG,
    build_blend,
    classify_math_supervision_bucket,
    convert_m0_record,
    load_difficulty_signal,
    prepare,
)
from nemotron.recipes.super3.milestones.m1_agentic_sft.run_m1_sft_roundtrip_smoke import (
    run as run_m1_sft_roundtrip_smoke,
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


def test_convert_reasoning_record_preserves_reference_solution_without_gsm8k_marker() -> None:
    """Reasoning SFT keeps solution traces but strips GSM8K's verifier marker."""
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "Work it out.\n#### 42"

    converted = convert_m0_record(record, split="train")

    content = converted["messages"][-1]["content"]
    assert "Work it out." in content
    assert "####" not in content
    assert content.endswith(r"Final answer: \boxed{42}")
    assert USED_IN_TAG in converted["used_in"]
    assert converted["metadata"]["m0_environment"] == "math_reasoning_numeric"
    assert converted["metadata"]["m1_stage"] == "Agentic SFT v0"
    assert converted["metadata"]["final_answer_supervision"]["format"] == "boxed_final_line"
    assert converted["metadata"]["final_answer_supervision"]["effective_weight"] == MATH_FINAL_ANSWER_EFFECTIVE_WEIGHT


def test_convert_reasoning_record_strips_gsm8k_marker_when_falling_back() -> None:
    """If expected_answer is empty, reference_solution is used but `####` is stripped."""
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = ""
    record["extra_env_info"]["reference_solution"] = "Step 1: do something.\n#### 24"

    converted = convert_m0_record(record, split="train")

    content = converted["messages"][-1]["content"]
    assert "####" not in content
    # The reasoning text is preserved.
    assert "Step 1: do something." in content
    assert content.endswith("24")


def test_convert_reasoning_record_appends_missing_expected_answer() -> None:
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "Reason through the problem."

    converted = convert_m0_record(record, split="train")

    content = converted["messages"][-1]["content"]
    assert content == r"Reason through the problem." "\n\n" r"Final answer: \boxed{42}"


def test_convert_reasoning_record_boxes_answer_when_no_reference_solution() -> None:
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1]["content"] == r"Final answer: \boxed{42}"


def test_convert_reasoning_record_does_not_double_box_expected_answer() -> None:
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = r"\boxed{42}"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1]["content"] == r"Final answer: \boxed{42}"


def test_classify_math_supervision_bucket_for_v3_rows() -> None:
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "We compute 40 + 2 = 42. Therefore \\boxed{42}."
    assert classify_math_supervision_bucket(record) == MATH_BUCKET_VERIFIED_FULL_SOLUTION

    record["extra_env_info"]["reference_solution"] = "We compute 40 + 2 = 42."
    assert classify_math_supervision_bucket(record) == MATH_BUCKET_FORMAT_REPAIR

    record["extra_env_info"].pop("reference_solution")
    assert classify_math_supervision_bucket(record) == MATH_BUCKET_FINAL_ANSWER_AUX

    competition = _base_record("math_competition_numeric")
    competition["expected_answer"] = "42"
    competition["extra_env_info"].pop("reference_solution", None)
    assert classify_math_supervision_bucket(competition) == MATH_BUCKET_HELDOUT_EVAL


def test_convert_code_record_uses_reference_code() -> None:
    record = _base_record("code_execution_python")
    record["extra_env_info"]["reference_code"] = "def answer():\n    return 42"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1]["content"] == "def answer():\n    return 42"
    assert converted["metadata"]["m0_split"] == "train"


def test_convert_structured_output_record_uses_expected_json() -> None:
    record = _base_record("structured_outputs_json")
    record["expected_answer"] = '{"city":"Paris","country":"France"}'
    record["extra_env_info"]["expected_json"] = {"city": "Paris", "country": "France"}
    record["extra_env_info"]["schema"] = {"type": "object", "required": ["city", "country"]}
    record["metadata"]["domain"] = "structured_output"
    record["metadata"]["reward_type"] = "json_value_exact_match"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1] == {
        "role": "assistant",
        "content": '{"city": "Paris", "country": "France"}',
    }
    assert converted["metadata"]["m1_use"] == ["structured output"]
    assert converted["metadata"]["m0_environment"] == "structured_outputs_json"


def test_convert_terminal_record_uses_expected_command() -> None:
    record = _base_record("terminal_basic_shell")
    record["expected_answer"] = "mv ~/Desktop/x ~/Downloads/"
    record["extra_env_info"]["expected_command"] = "mv ~/Desktop/x ~/Downloads/"
    record["metadata"]["domain"] = "terminal"
    record["metadata"]["reward_type"] = "command_substring_match"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1] == {
        "role": "assistant",
        "content": "mv ~/Desktop/x ~/Downloads/",
    }
    assert converted["metadata"]["m1_use"] == ["terminal basics"]
    assert converted["metadata"]["m0_environment"] == "terminal_basic_shell"


def test_convert_swe_patch_record_uses_gold_patch() -> None:
    patch = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-old\n+new"
    record = _base_record("swe_pivot_patch_supervision")
    record["expected_answer"] = patch
    record["extra_env_info"]["gold_patch"] = patch
    record["extra_env_info"]["repo"] = "sqlfluff/sqlfluff"
    record["metadata"]["domain"] = "software_engineering"
    record["metadata"]["reward_type"] = "patch_diff_match"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1] == {"role": "assistant", "content": patch}
    assert converted["metadata"]["m1_use"] == ["short SWE traces"]
    assert converted["metadata"]["m0_environment"] == "swe_pivot_patch_supervision"


def test_convert_tool_call_repair_negative_preserves_tools_and_repair_target() -> None:
    tool_call = {
        "type": "function",
        "function": {"name": "lookup", "arguments": {"query": "weather"}},
    }
    record = _base_record("tool_call_repair_negative")
    record["responses_create_params"]["tools"] = [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up information.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
            },
        }
    ]
    record["expected_answer"] = {"repair_message": "I will repair the call.", "tool_calls": [tool_call]}
    record["extra_env_info"]["repair_target"] = [tool_call]
    record["extra_env_info"]["expected_assistant_content"] = "I will repair the call."
    record["metadata"]["domain"] = "general_tool_calling"
    record["metadata"]["reward_type"] = "negative_recognition"

    converted = convert_m0_record(record, split="train")

    assistant = converted["messages"][-1]
    assert assistant["role"] == "assistant"
    assert assistant["content"] == "I will repair the call."
    assert assistant["tool_calls"][0]["id"] == "repair_call_0"
    assert assistant["tool_calls"][0]["function"]["name"] == "lookup"
    assert converted["tools"][0]["function"]["name"] == "lookup"
    assert converted["metadata"]["m1_use"] == [
        "malformed tool call negatives",
        "hallucinated tool output negatives",
    ]


def test_m1_sft_roundtrip_smoke_writes_packed_parquet_for_new_task005_envs(tmp_path) -> None:
    records = []

    terminal = _base_record("terminal_basic_shell")
    terminal["expected_answer"] = "mv ~/Desktop/x ~/Downloads/"
    terminal["extra_env_info"]["expected_command"] = "mv ~/Desktop/x ~/Downloads/"
    records.append(convert_m0_record(terminal, split="train"))

    swe = _base_record("swe_pivot_patch_supervision")
    patch = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-old\n+new"
    swe["expected_answer"] = patch
    swe["extra_env_info"]["gold_patch"] = patch
    records.append(convert_m0_record(swe, split="train"))

    repair = _base_record("tool_call_repair_negative")
    repair["responses_create_params"]["input"][-1]["content"] = (
        "Invalid artifact:\n&lt;tool_call&gt;{\"name\":\"lookup\"}&lt;/tool_call&gt;"
    )
    repair["responses_create_params"]["tools"] = [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up information.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
            },
        }
    ]
    repair["extra_env_info"]["repair_target"] = [
        {"type": "function", "function": {"name": "lookup", "arguments": {"query": "weather"}}}
    ]
    repair["extra_env_info"]["expected_assistant_content"] = "I will repair the call."
    records.append(convert_m0_record(repair, split="train"))

    input_path = tmp_path / "agentic_sft_v0_train.jsonl"
    with input_path.open("w", encoding="utf-8") as f:
        for record in records:
            json.dump(record, f)
            f.write("\n")

    summary = run_m1_sft_roundtrip_smoke(
        Namespace(
            m1_jsonl=input_path,
            output_dir=tmp_path / "roundtrip",
            max_records=None,
            pack_size=4096,
            used_in_filter=USED_IN_TAG,
            require_environment=[
                "terminal_basic_shell",
                "swe_pivot_patch_supervision",
                "tool_call_repair_negative",
            ],
            overwrite=False,
        )
    )

    assert summary["status"] == "pass"
    assert summary["environment_counts"] == {
        "swe_pivot_patch_supervision": 1,
        "terminal_basic_shell": 1,
        "tool_call_repair_negative": 1,
    }
    assert (tmp_path / "roundtrip" / "splits" / "train" / "shard_000000.parquet").exists()
    assert summary["parquet"]["total_loss_tokens"] > 0


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
    assert len(blend["datasets"]) == 1


def test_build_blend_can_add_math_final_answer_sidecar() -> None:
    blend = build_blend(
        "/tmp/train.jsonl",
        math_final_answer_train_path="/tmp/math-final-answer.jsonl",
    )

    assert blend["datasets"][1]["name"] == MATH_FINAL_ANSWER_SIDECAR_NAME
    assert blend["datasets"][1]["path"] == "/tmp/math-final-answer.jsonl"
    assert blend["datasets"][1]["weight"] == MATH_FINAL_ANSWER_SIDECAR_WEIGHT


def test_prepare_writes_train_shadow_and_blend(tmp_path) -> None:
    m0_root = tmp_path / "m0"
    env_dir = m0_root / "math_reasoning_numeric"
    env_dir.mkdir(parents=True)
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "#### 42"
    for split in ("train", "val"):
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            json.dump(record, f)
            f.write("\n")

    class Args:
        m0_input_dir = m0_root
        output_dir = tmp_path / "out"
        m0_health_baseline = None
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert manifest["counts"]["train"] == {"math_reasoning_numeric": 1}
    assert manifest["counts"]["val_shadow"] == {"math_reasoning_numeric": 1}
    assert (Args.output_dir / "agentic_sft_v0_train.jsonl").exists()
    assert (Args.output_dir / "agentic_sft_v0_math_final_answer_train.jsonl").exists()
    assert (Args.output_dir / "agentic_sft_v0_val_shadow.jsonl").exists()
    assert (Args.output_dir / "data_blend_agentic_sft_v0.json").exists()
    math_sidecar = [
        json.loads(line)
        for line in (Args.output_dir / "agentic_sft_v0_math_final_answer_train.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(math_sidecar) == 1
    assert math_sidecar[0]["messages"][-1]["content"].endswith(r"Final answer: \boxed{42}")
    blend = json.loads((Args.output_dir / "data_blend_agentic_sft_v0.json").read_text(encoding="utf-8"))
    assert [dataset["name"] for dataset in blend["datasets"]] == [
        "m1-agentic-sft-v0-from-m0",
        MATH_FINAL_ANSWER_SIDECAR_NAME,
    ]
    assert manifest["math_final_answer_supervision"]["train_rows"] == 1
    assert manifest["math_final_answer_supervision"]["sidecar_in_blend"] is True
    # No M0 baseline supplied → every row falls into the unknown bucket.
    assert manifest["difficulty_buckets"]["train"] == {"unknown": 1}
    assert manifest["difficulty_buckets"]["val_shadow"] == {"unknown": 1}


def test_prepare_reasoning_replay_v3_writes_math_buckets_and_blend(tmp_path) -> None:
    m0_root = tmp_path / "m0"

    def write_split(environment: str, split: str, records: list[dict]) -> None:
        env_dir = m0_root / environment
        env_dir.mkdir(parents=True, exist_ok=True)
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            for record in records:
                json.dump(record, f)
                f.write("\n")

    verified = _base_record("math_reasoning_numeric")
    verified["expected_answer"] = "42"
    verified["extra_env_info"]["reference_solution"] = (
        "We compute 40 + 2 = 42. Therefore the answer is \\boxed{42}."
    )
    repaired = _base_record("math_reasoning_numeric")
    repaired["expected_answer"] = "7"
    repaired["extra_env_info"]["reference_solution"] = "Add 3 and 4 to obtain 7."
    answer_only = _base_record("math_reasoning_numeric")
    answer_only["expected_answer"] = "5"
    answer_only["extra_env_info"].pop("reference_solution", None)
    heldout = _base_record("math_competition_numeric")
    heldout["expected_answer"] = "11"
    heldout["extra_env_info"].pop("reference_solution", None)
    search = _base_record("search_grounded_qa")
    search["expected_answer"] = "Paris"

    write_split("math_reasoning_numeric", "train", [verified, repaired, answer_only])
    write_split("math_reasoning_numeric", "val", [verified])
    write_split("math_competition_numeric", "train", [heldout])
    write_split("math_competition_numeric", "val", [])
    write_split("search_grounded_qa", "train", [search])
    write_split("search_grounded_qa", "val", [])

    class Args:
        m0_input_dir = m0_root
        output_dir = tmp_path / "out"
        m0_health_baseline = None
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False
        math_supervision_strategy = MATH_SUPERVISION_STRATEGY_V3
        math_v3_verified_full_solution_weight = MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT
        math_v3_final_answer_aux_weight = MATH_V3_FINAL_ANSWER_AUX_WEIGHT
        math_v3_format_repair_weight = MATH_V3_FORMAT_REPAIR_WEIGHT

    manifest = prepare(Args())

    assert manifest["math_supervision_strategy"] == MATH_SUPERVISION_STRATEGY_V3
    assert manifest["counts"]["train"] == {
        "math_reasoning_numeric": 3,
        "search_grounded_qa": 1,
    }
    assert manifest["math_final_answer_supervision"]["sidecar_in_blend"] is False
    assert manifest["math_final_answer_supervision"]["effective_weight"] == 1.0

    bucket_info = manifest["math_reasoning_replay_v3"]["buckets"]
    assert bucket_info[MATH_BUCKET_VERIFIED_FULL_SOLUTION]["rows"] == 1
    assert bucket_info[MATH_BUCKET_FINAL_ANSWER_AUX]["rows"] == 1
    assert bucket_info[MATH_BUCKET_FORMAT_REPAIR]["rows"] == 1
    assert bucket_info[MATH_BUCKET_HELDOUT_EVAL]["rows"] == 2
    assert manifest["math_reasoning_replay_v3"]["train_rows_excluded_as_heldout"] == 1

    blend = json.loads((Args.output_dir / "data_blend_agentic_sft_v0.json").read_text(encoding="utf-8"))
    blend_by_name = {dataset["name"]: dataset for dataset in blend["datasets"]}
    assert "m1-agentic-sft-v0-math-final-answer" not in blend_by_name
    assert blend_by_name["m1-agentic-sft-v0-math-verified-full-solution"]["weight"] == 1.0
    assert blend_by_name["m1-agentic-sft-v0-math-final-answer-aux"]["weight"] == 0.2
    assert blend_by_name["m1-agentic-sft-v0-math-format-repair"]["weight"] == 0.05

    aux_rows = [
        json.loads(line)
        for line in (Args.output_dir / "agentic_sft_v0_math_final_answer_aux_train.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert aux_rows[0]["metadata"]["final_answer_supervision"]["strategy"] == MATH_SUPERVISION_STRATEGY_V3
    assert aux_rows[0]["metadata"]["final_answer_supervision"]["sidecar_blend_weight"] == 0.2

    heldout_rows = [
        json.loads(line)
        for line in (Args.output_dir / "agentic_sft_v0_math_heldout_eval.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(heldout_rows) == 2
    assert all(
        row["metadata"]["final_answer_supervision"]["sidecar_blend_weight"] == 0.0
        for row in heldout_rows
    )

    report_md = (Args.output_dir / "report.md").read_text(encoding="utf-8")
    assert "## Math reasoning replay v3 buckets" in report_md
    assert "| heldout_eval | 2 | 0.0 |" in report_md


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
            "eval_interval": 3,
            "save_interval": 3,
        },
        "paths": {
            "script_path": tmp_path / "train.py",
            "config_path": tmp_path / "config.yaml",
        },
    }
    with pytest.raises(ValueError, match="single-node launch"):
        build_torchrun_command(manifest)


def test_plan_m1_torchrun_command_includes_strategy_overrides(tmp_path) -> None:
    from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training import build_torchrun_command

    manifest = {
        "resources": {"nodes": 1, "gpus_per_node": 8},
        "training": {
            "train_iters": 9,
            "global_batch_size": 8,
            "micro_batch_size": 1,
            "seq_length": 4096,
            "eval_interval": 3,
            "save_interval": 3,
            "optimizer_lr": 1e-6,
            "scheduler_min_lr": 1e-7,
            "lr_warmup_iters": 100,
            "lr_decay_iters": 900,
        },
        "paths": {
            "script_path": tmp_path / "qwen3_30b_a3b_local_train.py",
            "config_path": tmp_path / "config.yaml",
        },
    }

    command = build_torchrun_command(manifest)

    assert "++optimizer.lr=1e-06" in command
    assert "++optimizer.min_lr=1e-07" in command
    assert "scheduler.lr_warmup_iters=100" in command
    assert "++scheduler.lr_decay_iters=900" in command


def test_ensure_batch_geometry_accepts_valid_combos() -> None:
    """Regression for review finding P0 #2: GBS must be a multiple of DP × MBS."""
    from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training import (
        ensure_batch_geometry,
    )

    # Default planner combo: GBS=8, GPUs=8, MBS=1, nodes=1 → DP=8, step=8, 8%8==0 ✓
    ensure_batch_geometry(global_batch_size=8, micro_batch_size=1, gpus_per_node=8, nodes=1)
    # Single-GPU smoke: GBS=1, GPUs=1, MBS=1 ✓
    ensure_batch_geometry(global_batch_size=1, micro_batch_size=1, gpus_per_node=1, nodes=1)
    # Multiple-of-step is fine: GBS=16 on DP=8, MBS=1 → step=8, 16%8==0 ✓
    ensure_batch_geometry(global_batch_size=16, micro_batch_size=1, gpus_per_node=8, nodes=1)
    # MBS > 1: GBS=8 on DP=2, MBS=4 → step=8, 8%8==0 ✓
    ensure_batch_geometry(global_batch_size=8, micro_batch_size=4, gpus_per_node=2, nodes=1)


def test_ensure_batch_geometry_rejects_gbs_smaller_than_dp_times_mbs() -> None:
    """Regression for review finding P0 #2: original default GBS=4, GPUs=8 used to crash at setup."""
    import pytest

    from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_m1_agentic_sft_training import (
        ensure_batch_geometry,
    )

    # Original broken default before this fix.
    with pytest.raises(ValueError, match="multiple of"):
        ensure_batch_geometry(global_batch_size=4, micro_batch_size=1, gpus_per_node=8, nodes=1)
    # GBS not a multiple of step.
    with pytest.raises(ValueError, match="multiple of"):
        ensure_batch_geometry(global_batch_size=12, micro_batch_size=1, gpus_per_node=8, nodes=1)
    # Multi-node case: GBS=8, GPUs=8, nodes=2 → DP=16, step=16, 8%16!=0 → reject.
    with pytest.raises(ValueError, match="multiple of"):
        ensure_batch_geometry(global_batch_size=8, micro_batch_size=1, gpus_per_node=8, nodes=2)


def test_build_plan_uses_batch_geometry_guard(tmp_path) -> None:
    """End-to-end: build_plan must surface the GBS×DP mismatch before writing anything."""
    import pytest

    splits_dir = tmp_path / "packed" / "splits"
    for split in ("train", "valid"):
        (splits_dir / split).mkdir(parents=True)
        (splits_dir / split / "shard_000000.parquet").write_bytes(b"x")
    (tmp_path / "checkpoint").mkdir()
    (tmp_path / "tokenizer").mkdir()

    class Args:
        packed_sft_dir = splits_dir.parent
        pretrained_checkpoint = tmp_path / "checkpoint"
        tokenizer_model = str(tmp_path / "tokenizer")
        save_dir = tmp_path / "save"
        output_dir = tmp_path / "plans"
        run_name = "unit"
        repo_dir = tmp_path / "repo"
        script_path = "src/nemotron/recipes/super3/stage1_sft/train.py"
        config_path = "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"
        venv = None
        nodes = 1
        gpus_per_node = 8
        epochs = 1.0
        train_iters = 9
        fallback_train_iters = 1700
        # Intentionally broken: GBS=4 on DP=8 → step=8, 4%8 != 0.
        global_batch_size = 4
        micro_batch_size = 1
        seq_length = 4096
        eval_interval = 3
        save_interval = 3
        allow_missing_checkpoint = False

    with pytest.raises(ValueError, match="multiple of"):
        build_plan(Args())


def test_m1_agentic_smoke_yaml_pretrained_checkpoint_resolves_without_env(monkeypatch) -> None:
    """Regression for review finding N2: smoke yaml used to raise MissingMandatoryValue."""
    from pathlib import Path

    import pytest

    # omegaconf is a megatron-bridge / nemo_runspec dep; skip gracefully when
    # the test env doesn't have it (matches the cosmos_xenna / megatron.bridge
    # skip gates elsewhere in this file).
    omega_conf = pytest.importorskip("omegaconf").OmegaConf

    monkeypatch.delenv("SUPER3_M1_PRETRAINED_CHECKPOINT", raising=False)
    cfg = omega_conf.load(Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_smoke.yaml"))
    # Resolving the field used to raise MissingMandatoryValue because the file
    # had `pretrained_checkpoint: ${oc.env:SUPER3_M1_PRETRAINED_CHECKPOINT}` (no
    # default). After the fix it is a YAML literal null.
    assert omega_conf.select(cfg, "checkpoint.pretrained_checkpoint") is None
    # And the train-side yaml *does* still require the env var — that is the
    # intentional contract for finetune=true. Sanity-check that the smoke fix
    # didn't accidentally weaken the train-side requirement.
    train_cfg = omega_conf.load(Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"))
    train_pc = omega_conf.to_yaml(train_cfg.checkpoint)
    assert "SUPER3_M1_PRETRAINED_CHECKPOINT" in train_pc


def test_qwen_local_train_requires_env_var(monkeypatch) -> None:
    """Regression for review finding N1: hardcoded lei.song default removed."""
    import pytest

    # qwen_local_train top-imports omegaconf; skip cleanly when it's absent
    # rather than failing collection.
    pytest.importorskip("omegaconf")
    from nemotron.recipes.super3.stage1_sft.qwen_local_train import (
        QWEN_MODEL_ENV_VAR,
        resolve_qwen_hf_model,
    )

    monkeypatch.delenv(QWEN_MODEL_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match=QWEN_MODEL_ENV_VAR):
        resolve_qwen_hf_model()


def test_qwen_local_train_uses_env_var_when_set(monkeypatch, tmp_path) -> None:
    import pytest

    pytest.importorskip("omegaconf")
    from nemotron.recipes.super3.stage1_sft.qwen_local_train import (
        QWEN_MODEL_ENV_VAR,
        resolve_qwen_hf_model,
    )

    target = tmp_path / "qwen3-4b"
    target.mkdir()
    monkeypatch.setenv(QWEN_MODEL_ENV_VAR, str(target))
    assert resolve_qwen_hf_model() == str(target)


def test_qwen_local_train_uses_qwen_tokenizer_when_config_has_nemotron_fallback(tmp_path) -> None:
    import pytest

    omega_conf = pytest.importorskip("omegaconf").OmegaConf
    from nemotron.recipes.super3.stage1_sft.qwen_local_train import (
        NEMOTRON_SUPER_TOKENIZER_DEFAULT,
        resolve_qwen_tokenizer_model,
    )

    qwen_model = str(tmp_path / "qwen3-4b")
    cfg = omega_conf.create({"tokenizer": {"tokenizer_model": NEMOTRON_SUPER_TOKENIZER_DEFAULT}})

    assert resolve_qwen_tokenizer_model(cfg, qwen_model) == qwen_model

    explicit_tokenizer = str(tmp_path / "explicit-tokenizer")
    cfg.tokenizer.tokenizer_model = explicit_tokenizer
    assert resolve_qwen_tokenizer_model(cfg, qwen_model) == explicit_tokenizer


def test_qwen30b_a3b_local_train_requires_env_var(monkeypatch) -> None:
    import pytest

    pytest.importorskip("omegaconf")
    from nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train import (
        QWEN_MODEL_ENV_VAR,
        resolve_qwen_hf_model,
    )

    monkeypatch.delenv(QWEN_MODEL_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match=QWEN_MODEL_ENV_VAR):
        resolve_qwen_hf_model()


def test_qwen30b_a3b_local_train_uses_env_var_when_set(monkeypatch, tmp_path) -> None:
    import pytest

    pytest.importorskip("omegaconf")
    from nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train import (
        QWEN_MODEL_ENV_VAR,
        resolve_qwen_hf_model,
    )

    target = tmp_path / "qwen3-30b-a3b"
    target.mkdir()
    monkeypatch.setenv(QWEN_MODEL_ENV_VAR, str(target))
    assert resolve_qwen_hf_model() == str(target)


def test_qwen30b_a3b_local_train_uses_qwen_tokenizer_when_config_has_nemotron_fallback(tmp_path) -> None:
    import pytest

    omega_conf = pytest.importorskip("omegaconf").OmegaConf
    from nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train import (
        NEMOTRON_SUPER_TOKENIZER_DEFAULT,
        resolve_qwen_tokenizer_model,
    )

    qwen_model = str(tmp_path / "qwen3-30b-a3b")
    cfg = omega_conf.create({"tokenizer": {"tokenizer_model": NEMOTRON_SUPER_TOKENIZER_DEFAULT}})

    assert resolve_qwen_tokenizer_model(cfg, qwen_model) == qwen_model


def test_convert_m0_record_raises_on_empty_supervision_across_all_envs() -> None:
    """Regression for review finding P1 #4: every env must reject empty assistant supervision.

    Previously only general_tool_calling carried a soft `metadata.warning`;
    reasoning / code / search rows with empty expected_answer + empty
    reference_* would silently train on `{"role":"assistant","content":""}`.
    """
    import pytest

    for environment in ("math_reasoning_numeric", "code_execution_python", "search_grounded_qa"):
        record = _base_record(environment)
        record["expected_answer"] = ""
        record["extra_env_info"]["reference_solution"] = ""
        record["extra_env_info"]["reference_code"] = ""
        with pytest.raises(ValueError, match="supervision target would be empty"):
            convert_m0_record(record, split="train")

    # general_tool_calling with neither tool_calls nor assistant content
    record = _base_record("general_tool_calling")
    record["extra_env_info"]["expected_trajectory"] = [
        {"role": "assistant", "content": "", "tool_calls": []},
    ]
    with pytest.raises(ValueError, match="supervision target would be empty"):
        convert_m0_record(record, split="train")


def test_assistant_for_search_emits_grounded_template() -> None:
    """Regression for review finding P1 #11: search target used to be a bare short answer."""
    record = _base_record("search_grounded_qa")
    record["expected_answer"] = "London"
    record["extra_env_info"]["supporting_facts"] = {
        "title": ["Ada Lovelace", "Ada Lovelace", "London"],
        "sent_id": [0, 1, 0],
    }

    converted = convert_m0_record(record, split="train")

    content = converted["messages"][-1]["content"]
    # Grounded template references supporting passages, not a bare token.
    assert content != "London"
    assert "London" in content
    assert "[1] Ada Lovelace" in content
    assert "[2] London" in content
    assert "retrieved passages" in content


def test_assistant_for_search_falls_back_without_supporting_facts() -> None:
    record = _base_record("search_grounded_qa")
    record["expected_answer"] = "Paris"
    # No supporting_facts in extra_env_info — should still produce a grounded
    # template, just without indexed citations.
    converted = convert_m0_record(record, split="train")
    content = converted["messages"][-1]["content"]
    assert content == "Based on the retrieved passages, the answer is Paris."


def test_tool_role_supervision_survives_to_chat_template_input() -> None:
    """Regression for review finding P1 #14: tool turns must reach the template intact.

    The downstream loss-mask rule in
    `src/nemotron/data_prep/core/chat_sft_shard_core.py::_tokenize_chunks_with_mask`
    assigns `mask = 1 if chunk["role"] == "assistant" else 0`. Any future
    refactor of `convert_m0_record` that renames tool turns to user/assistant
    (e.g. to "fix" a chat-template quirk) would silently flip those tokens to
    loss_mask=1 and start training the model to mimic tool outputs. This test
    pins the role identity at the conversion boundary.
    """
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

    roles = [m["role"] for m in converted["messages"]]
    assert "tool" in roles, f"tool role missing from converted messages: {roles}"
    for tool_msg in (m for m in converted["messages"] if m["role"] == "tool"):
        # tool messages must not carry tool_calls — only assistant messages do.
        assert not tool_msg.get("tool_calls"), (
            "tool message accidentally adopted assistant tool_calls payload — "
            "loss_mask logic would still treat its tokens as 0, but downstream "
            "renderers may misinterpret the schema"
        )


def test_qwen_sft_data_prep_contract_can_use_tokenizer_template() -> None:
    from nemotron.data_prep.core.chat_sft_shard_core import _apply_chat_template
    from nemotron.recipes.super3.stage1_sft.data_prep import SFTDataPrepConfig

    cfg = SFTDataPrepConfig(
        chat_template="tokenizer",
        chat_template_kwargs={
            "enable_thinking": False,
            "truncate_history_thinking": False,
        },
    )
    assert cfg.chat_template == "tokenizer"
    assert cfg.chat_template_kwargs == {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }

    class _Tokenizer:
        chat_template = "qwen tokenizer template"

    tokenizer = _Tokenizer()
    _apply_chat_template(tokenizer, "tokenizer")
    assert tokenizer.chat_template == "qwen tokenizer template"


def test_sft_data_artifact_records_chat_template_contract(tmp_path) -> None:
    from nemotron.data_prep.blend import DataBlend, Dataset
    from nemotron.data_prep.config import FormatResult
    from nemotron.kit.artifacts.sft_data import SFTDataArtifact

    output_dir = tmp_path / "packed_qwen"
    (output_dir / "splits").mkdir(parents=True)
    format_result = FormatResult(
        run_hash="abc123",
        run_dir=str(output_dir / "runs" / "abc123"),
        output_dir=output_dir,
        num_shards=1,
        data_paths=[],
        dataset_stats={},
        from_cache=False,
        total_tokens=32,
        total_sequences=4,
    )
    blend = DataBlend.from_datasets(
        Dataset(name="unit", path=str(tmp_path / "unit.jsonl"), split="train", text_field="messages")
    )

    artifact = SFTDataArtifact.from_result(
        format_result=format_result,
        blend=blend,
        tokenizer_model=str(tmp_path / "qwen-tokenizer"),
        blend_json_path=tmp_path / "blend.json",
        pack_size=4096,
        chat_template="tokenizer",
        chat_template_kwargs={
            "enable_thinking": False,
            "truncate_history_thinking": False,
        },
    )

    assert artifact.path == (output_dir / "splits").resolve()
    assert artifact.chat_template == "tokenizer"
    assert artifact.chat_template_kwargs == {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }


def test_qwen_packed_sft_chat_contract_accepts_tokenizer_template(tmp_path) -> None:
    from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract

    tokenizer_dir = tmp_path / "qwen"
    tokenizer_dir.mkdir()
    splits_dir = tmp_path / "packed_qwen" / "splits"
    splits_dir.mkdir(parents=True)
    (splits_dir / "metadata.json").write_text(
        json.dumps(
            {
                "type": "SFTDataArtifact",
                "tokenizer_uri": f"file://{tokenizer_dir}",
                "chat_template": "tokenizer",
                "chat_template_kwargs": {
                    "enable_thinking": False,
                    "truncate_history_thinking": False,
                },
            }
        ),
        encoding="utf-8",
    )

    assert validate_qwen_packed_sft_chat_contract(splits_dir, tokenizer_model=str(tokenizer_dir)) == (
        splits_dir / "metadata.json"
    )


def test_qwen_packed_sft_chat_contract_accepts_hf_tokenizer_uri(tmp_path) -> None:
    from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract

    splits_dir = tmp_path / "packed_qwen" / "splits"
    splits_dir.mkdir(parents=True)
    (splits_dir / "metadata.json").write_text(
        json.dumps(
            {
                "type": "SFTDataArtifact",
                "tokenizer_uri": "https://huggingface.co/Qwen/Qwen3-4B",
                "chat_template": "tokenizer",
                "chat_template_kwargs": {
                    "enable_thinking": False,
                    "truncate_history_thinking": False,
                },
            }
        ),
        encoding="utf-8",
    )

    validate_qwen_packed_sft_chat_contract(splits_dir, tokenizer_model="Qwen/Qwen3-4B")


def test_qwen_packed_sft_chat_contract_rejects_super3_template(tmp_path) -> None:
    import pytest

    from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract

    splits_dir = tmp_path / "packed_qwen" / "splits"
    splits_dir.mkdir(parents=True)
    (splits_dir / "metadata.json").write_text(
        json.dumps(
            {
                "type": "SFTDataArtifact",
                "tokenizer_uri": "hf://models/Qwen/Qwen3",
                "chat_template": "super3",
                "chat_template_kwargs": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="chat_template=tokenizer"):
        validate_qwen_packed_sft_chat_contract(splits_dir, tokenizer_model="Qwen/Qwen3")


def test_qwen_packed_sft_chat_contract_rejects_enabled_thinking(tmp_path) -> None:
    import pytest

    from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract

    splits_dir = tmp_path / "packed_qwen" / "splits"
    splits_dir.mkdir(parents=True)
    (splits_dir / "metadata.json").write_text(
        json.dumps(
            {
                "type": "SFTDataArtifact",
                "tokenizer_uri": "hf://models/Qwen/Qwen3",
                "chat_template": "tokenizer",
                "chat_template_kwargs": {
                    "enable_thinking": True,
                    "truncate_history_thinking": False,
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="enable_thinking"):
        validate_qwen_packed_sft_chat_contract(splits_dir, tokenizer_model="Qwen/Qwen3")


def test_qwen_packed_sft_chat_contract_rejects_tokenizer_mismatch(tmp_path) -> None:
    import pytest

    from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import validate_qwen_packed_sft_chat_contract

    packed_tokenizer = tmp_path / "qwen-packed"
    train_tokenizer = tmp_path / "qwen-train"
    packed_tokenizer.mkdir()
    train_tokenizer.mkdir()
    splits_dir = tmp_path / "packed_qwen" / "splits"
    splits_dir.mkdir(parents=True)
    (splits_dir / "metadata.json").write_text(
        json.dumps(
            {
                "type": "SFTDataArtifact",
                "tokenizer_uri": f"file://{packed_tokenizer}",
                "chat_template": "tokenizer",
                "chat_template_kwargs": {
                    "enable_thinking": False,
                    "truncate_history_thinking": False,
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="tokenizer mismatch"):
        validate_qwen_packed_sft_chat_contract(splits_dir, tokenizer_model=str(train_tokenizer))


def test_tokenize_chunks_with_mask_pins_tool_role_to_zero() -> None:
    """Regression for review finding P1 #14: the role-based mask contract.

    Runs the actual `_tokenize_chunks_with_mask` from
    `src.nemotron.data_prep.core.chat_sft_shard_core` and asserts that only
    assistant chunks contribute to the SFT loss. Skipped locally when the
    `cosmos_xenna` runtime helpers used by the surrounding data-prep package
    aren't installed; CI environments that ship the full data-prep stack will
    run this end-to-end.
    """
    import pytest

    pytest.importorskip("cosmos_xenna")
    from nemotron.data_prep.core.chat_sft_shard_core import _tokenize_chunks_with_mask

    class _StubTokenizer:
        def encode(self, text, add_special_tokens=False):  # noqa: ARG002
            # One pseudo-token per whitespace-delimited word; deterministic.
            words = text.split()
            return list(range(len(words))) if words else []

    chunks = [
        {"role": "system", "content": "sys prompt one two"},
        {"role": "user", "content": "the question"},
        {"role": "assistant", "content": "answer one two three"},
        {"role": "tool", "content": "tool observation result"},
        {"role": "assistant", "content": "final answer"},
    ]

    _input_ids, loss_mask = _tokenize_chunks_with_mask(_StubTokenizer(), chunks)

    cursor = 0
    for chunk in chunks:
        n_tokens = len(chunk["content"].split())
        expected = 1 if chunk["role"] == "assistant" else 0
        chunk_mask = loss_mask[cursor : cursor + n_tokens]
        assert all(m == expected for m in chunk_mask), (
            f"role={chunk['role']!r} expected loss_mask {expected} got {chunk_mask}"
        )
        cursor += n_tokens
    assert cursor == len(loss_mask)


def test_m1_agentic_train_yaml_tokenizer_matches_data_prep_tokenizer() -> None:
    """Regression for review finding B2: training defaults used the Nano tokenizer."""
    from pathlib import Path

    import yaml

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
        eval_interval = 3
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


def test_build_plan_derives_train_iters_from_packed_rows(tmp_path, monkeypatch) -> None:
    """Regression for review finding #21: derived-rows path through summarize_split was uncovered.

    The existing happy-path test fixes ``train_iters`` explicitly, so the
    ``packed_train_rows × epochs / global_batch_size`` derivation in
    ``compute_train_iters`` never executes from ``build_plan``. Monkeypatch
    ``maybe_count_parquet_rows`` to return a known row count so the chain
    ``summarize_split → compute_train_iters → manifest.training.train_iters``
    is exercised end-to-end.
    """
    from nemotron.recipes.super3.milestones.m1_agentic_sft import plan_m1_agentic_sft_training as planner

    packed_root = tmp_path / "packed"
    splits_dir = packed_root / "splits"
    for split in ("train", "valid", "test"):
        split_dir = splits_dir / split
        split_dir.mkdir(parents=True)
        (split_dir / "shard_000000.parquet").write_bytes(b"placeholder")
    tokenizer_dir = tmp_path / "tokenizer"
    tokenizer_dir.mkdir()
    checkpoint_dir = tmp_path / "checkpoint"
    checkpoint_dir.mkdir()
    metadata = {"type": "SFTDataArtifact", "tokenizer_uri": f"file://{tokenizer_dir}"}
    with (splits_dir / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f)

    # 240 rows × 2 epochs / GBS 16 = ceil(30) = 30
    monkeypatch.setattr(planner, "maybe_count_parquet_rows", lambda paths: 240)

    class Args:
        packed_sft_dir = packed_root
        pretrained_checkpoint = checkpoint_dir
        tokenizer_model = None
        save_dir = tmp_path / "save"
        output_dir = tmp_path / "plans"
        run_name = "derived"
        repo_dir = tmp_path / "repo"
        script_path = "src/nemotron/recipes/super3/stage1_sft/train.py"
        config_path = "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"
        venv = None
        nodes = 1
        gpus_per_node = 8
        epochs = 2.0
        train_iters = None  # <-- the path under test
        fallback_train_iters = 999
        global_batch_size = 16
        micro_batch_size = 1
        seq_length = 4096
        eval_interval = 5
        save_interval = 5
        allow_missing_checkpoint = False

    manifest = planner.build_plan(Args())

    assert manifest["splits"]["train"]["rows"] == 240
    # ceil(240 * 2.0 / 16) = 30 (not the 999 fallback)
    assert manifest["training"]["train_iters"] == 30


def test_load_difficulty_signal_warns_on_corrupt_report(tmp_path, caplog) -> None:
    """Silent failure on a bad report used to leave every row tagged 'unknown'
    with no operator-visible signal. Surface the parse error via a warning."""
    bad_path = tmp_path / "health_baseline_report.json"
    bad_path.write_text("{not valid json", encoding="utf-8")

    with caplog.at_level("WARNING"):
        signal = load_difficulty_signal(bad_path)

    assert signal == {}
    warnings = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("could not be parsed" in m and "JSONDecodeError" in m for m in warnings)


def test_load_difficulty_signal_warns_when_report_missing_environments_mapping(tmp_path, caplog) -> None:
    """A health-baseline file with the wrong shape used to silently return {}."""
    weird = tmp_path / "health_baseline_report.json"
    weird.write_text(json.dumps({"baselines": {"environments": "not a dict"}}), encoding="utf-8")

    with caplog.at_level("WARNING"):
        signal = load_difficulty_signal(weird)

    assert signal == {}
    warnings = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("no `baselines.environments` mapping" in m for m in warnings)


def test_prepare_report_md_lists_difficulty_buckets(tmp_path) -> None:
    """The report.md used to only render counts; difficulty_buckets stayed in
    manifest.json. Surface it so operators don't have to spelunk JSON."""
    m0_root = tmp_path / "m0"
    env_dir = m0_root / "math_reasoning_numeric"
    env_dir.mkdir(parents=True)
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "Solve.\n#### 42"
    for split in ("train", "val"):
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            json.dump(record, f)
            f.write("\n")
    # Provide a minimal health baseline so at least one row gets tagged trivial.
    health_dir = m0_root / "health_baseline"
    health_dir.mkdir()
    report = {
        "baselines": {
            "environments": {
                "math_reasoning_numeric": {
                    "splits": {
                        "train": {
                            "oracle": {
                                "rows": 1,
                                "scored_rows": 1,
                                "failure_count": 0,
                                "failures": [],
                            }
                        },
                        "val": {
                            "oracle": {
                                "rows": 1,
                                "scored_rows": 1,
                                "failure_count": 0,
                                "failures": [],
                            }
                        },
                    }
                }
            }
        }
    }
    with (health_dir / "health_baseline_report.json").open("w", encoding="utf-8") as f:
        json.dump(report, f)

    class Args:
        m0_input_dir = m0_root
        output_dir = tmp_path / "out"
        m0_health_baseline = None  # exercise the auto-resolve path
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert manifest["difficulty_buckets"]["train"] == {"trivial": 1}
    report_md = (Args.output_dir / "report.md").read_text(encoding="utf-8")
    assert "## Difficulty buckets" in report_md
    assert "| train | trivial | 1 |" in report_md
    assert "M0 health baseline" in report_md


def test_m1_use_is_scoped_per_environment() -> None:
    """Regression for review finding P2 #10: m1_use was a hardcoded 4-string list per row."""
    for env_id, expected in M1_USE_BY_ENV.items():
        record = _base_record(env_id)
        if env_id == "math_reasoning_numeric":
            record["extra_env_info"]["reference_solution"] = "42"
        elif env_id == "code_execution_python":
            record["extra_env_info"]["reference_code"] = "def f():\n    return 1"
        elif env_id in {"general_tool_calling", "multi_turn_tool_use"}:
            record["extra_env_info"]["expected_trajectory"] = [
                {"role": "assistant", "content": "ok", "tool_calls": []},
            ]
        elif env_id == "tool_call_repair_negative":
            record["extra_env_info"]["repair_target"] = [
                {"type": "function", "function": {"name": "repair", "arguments": {"x": 1}}},
            ]
            record["extra_env_info"]["expected_assistant_content"] = "Repairing the invalid call."
        # search_grounded_qa: _base_record's expected_answer="Answer" suffices
        converted = convert_m0_record(record, split="train")
        assert converted["metadata"]["m1_use"] == expected, (
            f"env={env_id!r} expected m1_use={expected} got {converted['metadata']['m1_use']}"
        )


def test_load_difficulty_signal_maps_oracle_failures_to_hard(tmp_path) -> None:
    """Regression for review finding P2 #7: M0 oracle pass/fail must surface as difficulty."""
    report = {
        "baselines": {
            "environments": {
                "math_reasoning_numeric": {
                    "splits": {
                        "train": {
                            "oracle": {
                                "rows": 4,
                                "scored_rows": 4,
                                "failure_count": 2,
                                "failures": [{"row_index": 1}, {"row_index": 3}],
                            }
                        }
                    }
                }
            }
        }
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    signal = load_difficulty_signal(report_path)

    assert signal[("math_reasoning_numeric", "train", 0)] == DIFFICULTY_TRIVIAL
    assert signal[("math_reasoning_numeric", "train", 1)] == DIFFICULTY_HARD
    assert signal[("math_reasoning_numeric", "train", 2)] == DIFFICULTY_TRIVIAL
    assert signal[("math_reasoning_numeric", "train", 3)] == DIFFICULTY_HARD


def test_load_difficulty_signal_skips_truncated_failure_lists(tmp_path) -> None:
    """evaluate_policy caps failures at 20; unlisted rows must stay unknown, not trivial."""
    report = {
        "baselines": {
            "environments": {
                "math_reasoning_numeric": {
                    "splits": {
                        "train": {
                            "oracle": {
                                "rows": 30,
                                "scored_rows": 30,
                                "failure_count": 25,  # higher than the 1 listed
                                "failures": [{"row_index": 5}],
                            }
                        }
                    }
                }
            }
        }
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    signal = load_difficulty_signal(report_path)

    # row 5 still gets marked hard because it appears in the (truncated) failures
    assert signal[("math_reasoning_numeric", "train", 5)] == DIFFICULTY_HARD
    # but row 0 must NOT be trivial — we don't know whether it's one of the 24
    # unlisted failures
    assert ("math_reasoning_numeric", "train", 0) not in signal


def test_load_difficulty_signal_returns_empty_for_missing_report() -> None:
    from pathlib import Path

    assert load_difficulty_signal(None) == {}
    assert load_difficulty_signal(Path("/nonexistent/report.json")) == {}


def test_prepare_propagates_difficulty_bucket_per_row(tmp_path) -> None:
    """End-to-end: difficulty_signal flows through prepare into per-record metadata + manifest counts."""
    m0_root = tmp_path / "m0"
    env_dir = m0_root / "math_reasoning_numeric"
    env_dir.mkdir(parents=True)
    record = _base_record("math_reasoning_numeric")
    record["extra_env_info"]["reference_solution"] = "42"
    for split in ("train", "val"):
        # Write three identical math rows per split so we can address row_index 0/1/2.
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            for _ in range(3):
                json.dump(record, f)
                f.write("\n")

    # Mark row 1 in train as hard; row 0 in val as hard; the rest are oracle-pass.
    health = m0_root / "health_baseline" / "health_baseline_report.json"
    health.parent.mkdir()
    health.write_text(
        json.dumps(
            {
                "baselines": {
                    "environments": {
                        "math_reasoning_numeric": {
                            "splits": {
                                "train": {
                                    "oracle": {
                                        "rows": 3,
                                        "scored_rows": 3,
                                        "failure_count": 1,
                                        "failures": [{"row_index": 1}],
                                    }
                                },
                                "val": {
                                    "oracle": {
                                        "rows": 3,
                                        "scored_rows": 3,
                                        "failure_count": 1,
                                        "failures": [{"row_index": 0}],
                                    }
                                },
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    class Args:
        m0_input_dir = m0_root
        output_dir = tmp_path / "out"
        m0_health_baseline = None  # rely on the default discovery
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert manifest["m0_health_baseline"] == str(health)
    assert manifest["difficulty_buckets"]["train"] == {DIFFICULTY_HARD: 1, DIFFICULTY_TRIVIAL: 2}
    assert manifest["difficulty_buckets"]["val_shadow"] == {DIFFICULTY_HARD: 1, DIFFICULTY_TRIVIAL: 2}

    # Spot-check the metadata on the produced JSONL.
    train_jsonl = (Args.output_dir / "agentic_sft_v0_train.jsonl").read_text(encoding="utf-8").splitlines()
    train_records = [json.loads(line) for line in train_jsonl]
    assert train_records[0]["metadata"]["difficulty_bucket"] == DIFFICULTY_TRIVIAL
    assert train_records[1]["metadata"]["difficulty_bucket"] == DIFFICULTY_HARD
    assert train_records[2]["metadata"]["difficulty_bucket"] == DIFFICULTY_TRIVIAL


def test_prepare_marks_difficulty_unknown_without_baseline(tmp_path) -> None:
    m0_root = tmp_path / "m0"
    env_dir = m0_root / "math_reasoning_numeric"
    env_dir.mkdir(parents=True)
    record = _base_record("math_reasoning_numeric")
    record["extra_env_info"]["reference_solution"] = "42"
    for split in ("train", "val"):
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            json.dump(record, f)
            f.write("\n")

    class Args:
        m0_input_dir = m0_root
        output_dir = tmp_path / "out"
        m0_health_baseline = None
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert manifest["m0_health_baseline"] is None
    assert manifest["difficulty_buckets"]["train"] == {DIFFICULTY_UNKNOWN: 1}
    assert manifest["difficulty_buckets"]["val_shadow"] == {DIFFICULTY_UNKNOWN: 1}


def test_m0_use_stage_lineage_is_preserved_in_metadata() -> None:
    """Regression for review finding P3 #12: M0 used_in stage tags were dropped."""
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["used_in"] = ["M0 data_env_foundation", "M1 RLVR math/reasoning smoke"]

    converted = convert_m0_record(record, split="train")

    assert converted["used_in"] == ["super3", USED_IN_TAG, "m1_agentic_sft_v0"]
    assert converted["metadata"]["m0_use_stage"] == [
        "M0 data_env_foundation",
        "M1 RLVR math/reasoning smoke",
    ]


def test_m0_use_stage_lineage_defaults_to_empty_when_m0_missing_used_in() -> None:
    """Records that lack the M0 used_in field still get a deterministic m0_use_stage value."""
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record.pop("used_in", None)

    converted = convert_m0_record(record, split="train")
    assert converted["metadata"]["m0_use_stage"] == []


def test_m0_use_stage_lineage_reads_real_m0_use_stage_field() -> None:
    """Real M0 JSONL rows carry `use_stage`, not `used_in`."""
    record = _base_record("structured_outputs_json")
    record["expected_answer"] = '{"city":"Paris"}'
    record["extra_env_info"]["expected_json"] = {"city": "Paris"}
    record.pop("used_in", None)
    record["use_stage"] = ["M0 data_env_foundation", "M1 Agentic SFT v0 structured output"]

    converted = convert_m0_record(record, split="train")

    assert converted["metadata"]["m0_use_stage"] == [
        "M0 data_env_foundation",
        "M1 Agentic SFT v0 structured output",
    ]


def test_prompt_messages_scrubs_demo_tool_call_xml_from_user_content() -> None:
    """Regression for review finding P3 #20: Hermes demo `<tool_call>` blocks leaked into user content."""
    record = _base_record("general_tool_calling")
    record["responses_create_params"]["input"] = [
        {"role": "system", "content": "<tools>[]</tools>"},
        {
            "role": "user",
            "content": (
                "What is the weather?\n"
                '<tool_call>{"name": "lookup", "arguments": {"q": "weather"}}</tool_call>\n'
                "<tools>[{\"function\":{\"name\":\"lookup\"}}]</tools>"
            ),
        },
    ]
    record["extra_env_info"]["expected_trajectory"] = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "call_0", "type": "function", "function": {"name": "lookup", "arguments": {"q": "weather"}}}
            ],
        },
    ]

    converted = convert_m0_record(record, split="train")
    user_message = next(m for m in converted["messages"] if m["role"] == "user")

    assert "<tool_call>" not in user_message["content"]
    assert "<tools>" not in user_message["content"]
    assert "What is the weather?" in user_message["content"]


def test_smoke_runtime_patch_logs_warning_when_helpers_missing(monkeypatch, caplog) -> None:
    """Regression for review finding P3 #18: silent no-op masked missing helpers_cpp."""
    import logging
    import sys

    monkeypatch.setitem(sys.modules, "megatron.core.datasets.helpers_cpp", None)
    from nemotron.recipes.super3 import smoke_runtime

    with caplog.at_level(logging.WARNING, logger=smoke_runtime.logger.name):
        smoke_runtime.patch_dataset_helper_compile_if_prebuilt()

    assert any("Skipping dataset-helper compile patch" in r.message for r in caplog.records)


def test_tiny_model_surfaces_super_provider_availability_flag() -> None:
    """Regression for review finding P3 #19: silent Super3->Nano fallback.

    The module-level `_SUPER_PROVIDER_AVAILABLE` boolean is the new contract;
    when Super3 is missing the import emits a warning, when present it is True.
    Skip when megatron-bridge isn't installed in the test environment (the
    module raises ImportError before exposing the flag).
    """
    import pytest

    pytest.importorskip("megatron.bridge.models.nemotronh")
    import nemotron.recipes.super3.tiny_model as tiny_model_module

    assert isinstance(tiny_model_module._SUPER_PROVIDER_AVAILABLE, bool)


def test_convert_multihop_search_uses_grounded_template_with_musique_titles() -> None:
    """task056: MuSiQue's `supporting_titles` flat list feeds the grounded SFT
    template — same builder, different lineage shape than HotpotQA."""
    record = _base_record("search_multihop_qa")
    record["expected_answer"] = "Dearborn"
    record["extra_env_info"]["supporting_titles"] = ["Henry Ford", "Assembly Line"]

    converted = convert_m0_record(record, split="train")

    assistant = converted["messages"][-1]
    assert assistant["role"] == "assistant"
    assert "Based on the retrieved passages" in assistant["content"]
    assert "[1] Henry Ford" in assistant["content"]
    assert "[2] Assembly Line" in assistant["content"]
    assert assistant["content"].endswith("the answer is Dearborn.")
    # M1 use tag reflects the multi-hop env, not the single-hop search env.
    assert converted["metadata"]["m1_use"] == ["search pattern", "multi-hop reasoning"]


def test_convert_competition_math_routes_through_reasoning_builder() -> None:
    """task056: NuminaMath competition math reuses `assistant_for_reasoning`;
    reference_solution carries the full competition-math solution trace."""
    record = _base_record("math_competition_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "Steps... \\boxed{42}"
    record["extra_env_info"]["source"] = "amc_aime"

    converted = convert_m0_record(record, split="train")

    assert converted["messages"][-1] == {"role": "assistant", "content": "Steps... \\boxed{42}"}
    assert converted["metadata"]["m1_use"] == ["reasoning answer format", "competition math"]
    assert (
        converted["metadata"]["final_answer_supervision"]["sidecar_blend_weight"]
        == MATH_FINAL_ANSWER_SIDECAR_WEIGHT
    )


def test_convert_multi_turn_tool_use_routes_through_trajectory_builder() -> None:
    """task056: `multi_turn_tool_use` env shares the trajectory builder with
    `general_tool_calling` (both in `_TOOL_CALLING_ENVIRONMENTS`); system
    prompt is rewritten and the trajectory is expanded with tool_call_id pairing."""
    record = _base_record("multi_turn_tool_use")
    record["responses_create_params"]["input"][0]["content"] = (
        "You are a function calling AI model.\n<tools>[]</tools>"
    )
    record["responses_create_params"]["tools"] = [
        {"type": "function", "function": {"name": "lookup", "description": "L", "parameters": {"type": "object"}}}
    ]
    record["extra_env_info"]["expected_trajectory"] = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "call_0", "type": "function", "function": {"name": "lookup", "arguments": {"q": "x"}}}
            ],
        },
        {"role": "tool", "content": '{"result":"y"}', "tool_calls": []},
        {"role": "assistant", "content": "Done.", "tool_calls": []},
    ]

    converted = convert_m0_record(record, split="train")
    roles = [message["role"] for message in converted["messages"]]

    # system (rewritten) + user + 3-step assistant/tool/assistant trajectory
    assert roles == ["system", "user", "assistant", "tool", "assistant"]
    assert converted["messages"][0] == {"role": "system", "content": TOOL_CALLING_SYSTEM_PROMPT}
    assert converted["messages"][3]["tool_call_id"] == "call_0"
    assert converted["metadata"]["m1_use"] == ["tool call syntax", "multi-turn tool trace"]
