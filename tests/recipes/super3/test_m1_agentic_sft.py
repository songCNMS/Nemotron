import json

from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
    DIFFICULTY_HARD,
    DIFFICULTY_TRIVIAL,
    DIFFICULTY_UNKNOWN,
    M1_USE_BY_ENV,
    TOOL_CALLING_SYSTEM_PROMPT,
    USED_IN_TAG,
    build_blend,
    convert_m0_record,
    load_difficulty_signal,
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


def test_convert_reasoning_record_prefers_expected_answer_over_reference_solution() -> None:
    """Regression for review finding P1 #3: GSM8K `####` marker used to leak into SFT target."""
    record = _base_record("math_reasoning_numeric")
    record["expected_answer"] = "42"
    record["extra_env_info"]["reference_solution"] = "Work it out.\n#### 42"

    converted = convert_m0_record(record, split="train")

    # SFT target should be the normalized answer, never the verifier marker.
    assert converted["messages"][-1] == {"role": "assistant", "content": "42"}
    assert "####" not in converted["messages"][-1]["content"]
    assert USED_IN_TAG in converted["used_in"]
    assert converted["metadata"]["m0_environment"] == "math_reasoning_numeric"
    assert converted["metadata"]["m1_stage"] == "Agentic SFT v0"


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
        m0_health_baseline = None
        max_records_per_env = None
        max_val_shadow_per_env = None
        overwrite = False

    manifest = prepare(Args())

    assert manifest["counts"]["train"] == {"math_reasoning_numeric": 1}
    assert manifest["counts"]["val_shadow"] == {"math_reasoning_numeric": 1}
    assert (Args.output_dir / "agentic_sft_v0_train.jsonl").exists()
    assert (Args.output_dir / "agentic_sft_v0_val_shadow.jsonl").exists()
    assert (Args.output_dir / "data_blend_agentic_sft_v0.json").exists()
    # No M0 baseline supplied → every row falls into the unknown bucket.
    assert manifest["difficulty_buckets"]["train"] == {"unknown": 1}
    assert manifest["difficulty_buckets"]["val_shadow"] == {"unknown": 1}


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
        save_interval = 3
        allow_missing_checkpoint = False

    with pytest.raises(ValueError, match="multiple of"):
        build_plan(Args())


def test_m1_agentic_smoke_yaml_pretrained_checkpoint_resolves_without_env(monkeypatch) -> None:
    """Regression for review finding N2: smoke yaml used to raise MissingMandatoryValue."""
    from pathlib import Path

    from omegaconf import OmegaConf

    monkeypatch.delenv("SUPER3_M1_PRETRAINED_CHECKPOINT", raising=False)
    cfg = OmegaConf.load(Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_smoke.yaml"))
    # Resolving the field used to raise MissingMandatoryValue because the file
    # had `pretrained_checkpoint: ${oc.env:SUPER3_M1_PRETRAINED_CHECKPOINT}` (no
    # default). After the fix it is a YAML literal null.
    assert OmegaConf.select(cfg, "checkpoint.pretrained_checkpoint") is None
    # And the train-side yaml *does* still require the env var — that is the
    # intentional contract for finetune=true. Sanity-check that the smoke fix
    # didn't accidentally weaken the train-side requirement.
    train_cfg = OmegaConf.load(Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"))
    train_pc = OmegaConf.to_yaml(train_cfg.checkpoint)
    assert "SUPER3_M1_PRETRAINED_CHECKPOINT" in train_pc


def test_qwen_local_train_requires_env_var(monkeypatch) -> None:
    """Regression for review finding N1: hardcoded lei.song default removed."""
    import pytest
    from nemotron.recipes.super3.stage1_sft.qwen_local_train import (
        QWEN_MODEL_ENV_VAR,
        resolve_qwen_hf_model,
    )

    monkeypatch.delenv(QWEN_MODEL_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match=QWEN_MODEL_ENV_VAR):
        resolve_qwen_hf_model()


def test_qwen_local_train_uses_env_var_when_set(monkeypatch, tmp_path) -> None:
    from nemotron.recipes.super3.stage1_sft.qwen_local_train import (
        QWEN_MODEL_ENV_VAR,
        resolve_qwen_hf_model,
    )

    target = tmp_path / "qwen3-4b"
    target.mkdir()
    monkeypatch.setenv(QWEN_MODEL_ENV_VAR, str(target))
    assert resolve_qwen_hf_model() == str(target)


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


def test_m1_use_is_scoped_per_environment() -> None:
    """Regression for review finding P2 #10: m1_use was a hardcoded 4-string list per row."""
    for env_id, expected in M1_USE_BY_ENV.items():
        record = _base_record(env_id)
        if env_id == "math_reasoning_numeric":
            record["extra_env_info"]["reference_solution"] = "42"
        elif env_id == "code_execution_python":
            record["extra_env_info"]["reference_code"] = "def f():\n    return 1"
        elif env_id == "general_tool_calling":
            record["extra_env_info"]["expected_trajectory"] = [
                {"role": "assistant", "content": "ok", "tool_calls": []},
            ]
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
