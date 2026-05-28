from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_qwen_scaleup_run import (
    AGENTIC_M0_DATASET_IDS,
    DEFAULT_REMOTE_ROOT,
    QWEN30B_A3B_TRAIN_ENTRYPOINT,
    QWEN_DATA_PREP_CONFIG,
    build_manifest,
    build_parser,
    qwen_data_prep_config_contract,
    render_eval_script,
    render_local_data_prep_script,
    render_remote_train_script,
    render_report,
    render_sync_script,
    write_plan,
)
from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import (
    QWEN_DATA_PREP_CONFIG_NAME,
    QWEN_DATA_PREP_TARGET_FAMILY,
    validate_qwen_data_prep_config,
)


def _args(tmp_path: Path, *extra_args: str):
    return build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--run-name",
            "unit_qwen_scaleup",
            "--qwen-hf-model",
            "/models/qwen3-4b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-4b-bridge",
            "--max-train-per-dataset",
            "12",
            "--max-val-per-dataset",
            "3",
            "--num-shards",
            "8",
            "--pack-size",
            "512",
            "--seq-length",
            "512",
            "--eval-interval",
            "7",
            "--eval-config",
            "m1_full_basket",
            "--overwrite",
            *extra_args,
        ]
    )


def test_scaleup_manifest_limits_to_agentic_sft_m0_datasets(tmp_path) -> None:
    manifest = build_manifest(_args(tmp_path))
    dataset_ids = manifest["data"]["m0_dataset_ids"]

    assert tuple(dataset_ids) == AGENTIC_M0_DATASET_IDS
    assert len(dataset_ids) == 11
    assert "m0_swe_pivot_tool_call" not in dataset_ids
    assert "m0_swe2_openhands_trace" not in dataset_ids
    assert "m0_helpsteer2_pref" not in dataset_ids


def test_scaleup_scripts_wire_data_training_and_eval(tmp_path) -> None:
    manifest = build_manifest(_args(tmp_path))

    local_script = render_local_data_prep_script(manifest)
    remote_script = render_remote_train_script(manifest)
    eval_script = render_eval_script(manifest)

    assert "prepare_m0_assets.py" in local_script
    assert "m0_status=$?" in local_script
    assert 'if [[ "$m0_status" -ne 0 && "$m0_status" -ne 2 ]]' in local_script
    assert "prepare_m1_agentic_sft.py" in local_script
    assert "stage1_sft/data_prep.py" in local_script
    assert f"--config {QWEN_DATA_PREP_CONFIG}" in local_script
    assert "config/data_prep/agentic_v0.yaml" not in local_script
    assert "plan_m1_agentic_sft_training.py" in local_script
    assert "--dataset-id m0_search_hotpotqa" in local_script
    assert "--dataset-id m0_math_numinamath" in local_script
    assert "tokenizer.model=/models/qwen3-4b" in local_script
    assert "chat_template=tokenizer" in local_script
    assert "target_model_family=qwen" in local_script
    assert "config_name=qwen_agentic_v0" in local_script
    assert "chat_template_kwargs.enable_thinking=false" in local_script
    assert "chat_template_kwargs.truncate_history_thinking=false" in local_script
    assert "validate_qwen_packed_sft_chat_contract" in local_script
    assert "chat_template=super3" not in local_script
    assert "pack_size=512" in local_script
    assert manifest["packing"]["chat_template"] == "tokenizer"
    assert manifest["packing"]["chat_template_kwargs"] == {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }
    assert manifest["packing"]["target_model_family"] == QWEN_DATA_PREP_TARGET_FAMILY
    assert manifest["packing"]["data_prep_config"] == QWEN_DATA_PREP_CONFIG
    assert manifest["packing"]["data_prep_config_name"] == QWEN_DATA_PREP_CONFIG_NAME
    assert manifest["qwen_chat_contract"]["sft_chat_template"] == "tokenizer"
    validate_qwen_data_prep_config(manifest["qwen_chat_contract"]["data_prep"])
    assert manifest["qwen_chat_contract"]["training_profile"] == "qwen"
    assert (
        manifest["qwen_chat_contract"]["eval_chat_template_kwargs"]
        == manifest["packing"]["chat_template_kwargs"]
    )

    assert "qwen_local_train.py" in remote_script
    assert "--nproc_per_node=2" in remote_script
    assert "TRAIN_ITERS=" in remote_script
    assert "export TRAIN_ITERS" in remote_script
    assert 'tmux set-environment -g TRAIN_ITERS "$TRAIN_ITERS" 2>/dev/null || true' in remote_script
    assert "intern_nemontron_code_reading" not in remote_script
    assert manifest["paths"]["remote_root"] == str(DEFAULT_REMOTE_ROOT)
    assert manifest["paths"]["remote_run_root"] == str(DEFAULT_REMOTE_ROOT / "scaleup")
    assert str(DEFAULT_REMOTE_ROOT / "scaleup") in remote_script
    assert "dataset.packed_sequence_specs.packed_sequence_size=512" in remote_script
    assert "--training-profile qwen" in local_script
    assert "training_contract.model_profile=qwen" in remote_script
    assert "training_contract.model_ref=/models/qwen3-4b" in remote_script
    assert "export SUPER3_M1_TRAINING_PROFILE=qwen" in remote_script
    assert "CUDA_VISIBLE_DEVICES=0,1" in remote_script
    assert "train.global_batch_size=2" in remote_script
    assert "train.eval_interval=7" in remote_script
    assert "--eval-interval 7" in local_script

    assert "super3 eval -c m1_full_basket --dry-run" in eval_script
    assert "run.model=sft:unit_qwen_scaleup" in eval_script
    assert "deployment.checkpoint_path=" in eval_script


def test_scaleup_planner_preserves_explicit_remote_root(tmp_path) -> None:
    explicit_remote_root = tmp_path / "operator_remote_root"
    manifest = build_manifest(_args(tmp_path, "--remote-root", str(explicit_remote_root)))
    remote_script = render_remote_train_script(manifest)
    sync_script = render_sync_script(manifest)

    assert manifest["paths"]["remote_root"] == str(explicit_remote_root)
    assert manifest["paths"]["remote_run_root"] == str(explicit_remote_root / "scaleup")
    assert str(explicit_remote_root / "scaleup") in remote_script
    assert str(explicit_remote_root) in sync_script
    assert str(DEFAULT_REMOTE_ROOT) not in remote_script
    assert str(DEFAULT_REMOTE_ROOT) not in sync_script
    assert "intern_nemontron_code_reading" not in remote_script
    assert "intern_nemontron_code_reading" not in sync_script


def test_scaleup_planner_can_use_separate_qwen_tokenizer_model(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--run-name",
            "unit_qwen_scaleup",
            "--qwen-hf-model",
            "/remote/models/Qwen3-30B-A3B-Instruct-2507",
            "--qwen-tokenizer-model",
            "/local/models/Qwen3-30B-A3B-Instruct-2507",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
        ]
    )
    manifest = build_manifest(args)

    local_script = render_local_data_prep_script(manifest)
    remote_script = render_remote_train_script(manifest)
    report = render_report(manifest)

    assert manifest["training"]["qwen_hf_model"] == "/remote/models/Qwen3-30B-A3B-Instruct-2507"
    assert manifest["packing"]["tokenizer_model"] == "/local/models/Qwen3-30B-A3B-Instruct-2507"
    assert manifest["qwen_chat_contract"]["sft_model"] == "/remote/models/Qwen3-30B-A3B-Instruct-2507"
    assert (
        manifest["qwen_chat_contract"]["sft_tokenizer_model"]
        == "/local/models/Qwen3-30B-A3B-Instruct-2507"
    )
    assert "tokenizer.model=/local/models/Qwen3-30B-A3B-Instruct-2507" in local_script
    assert "--tokenizer-model /local/models/Qwen3-30B-A3B-Instruct-2507" in local_script
    assert "export SUPER3_M1_QWEN_HF_MODEL=/remote/models/Qwen3-30B-A3B-Instruct-2507" in remote_script
    assert "export SUPER3_M1_TOKENIZER_MODEL=/local/models/Qwen3-30B-A3B-Instruct-2507" in remote_script
    assert "training_contract.model_ref=/remote/models/Qwen3-30B-A3B-Instruct-2507" in remote_script
    assert "training_contract.model_ref=/local/models/Qwen3-30B-A3B-Instruct-2507" not in remote_script
    assert "/remote/models/Qwen3-30B-A3B-Instruct-2507" in report


def test_scaleup_planner_wires_30b_entrypoint_and_strategy_overrides(tmp_path) -> None:
    train_entrypoint = "src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py"
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--train-entrypoint",
            train_entrypoint,
            "--optimizer-lr",
            "1e-6",
            "--scheduler-min-lr",
            "1e-7",
            "--lr-warmup-iters",
            "100",
            "--allow-missing-checkpoint",
        ]
    )
    manifest = build_manifest(args)

    local_script = render_local_data_prep_script(manifest)
    remote_script = render_remote_train_script(manifest)

    assert manifest["training"]["train_entrypoint"] == train_entrypoint
    assert f"--script-path {train_entrypoint}" in local_script
    assert "--optimizer-lr" in local_script
    assert "--allow-missing-checkpoint" in local_script
    assert "1e-06" in local_script
    assert "qwen3_30b_a3b_local_train.py" in remote_script
    assert "++optimizer.lr=1e-06" in remote_script
    assert "++optimizer.min_lr=1e-07" in remote_script
    assert "scheduler.lr_warmup_iters=100" in remote_script
    assert "++scheduler.lr_decay_iters=$TRAIN_ITERS" in remote_script


def test_scaleup_planner_auto_selects_30b_a3b_entrypoint(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/Qwen3-30B-A3B-Instruct-2507",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
        ]
    )
    manifest = build_manifest(args)
    remote_script = render_remote_train_script(manifest)

    assert manifest["training"]["train_entrypoint"] == QWEN30B_A3B_TRAIN_ENTRYPOINT
    assert "qwen3_30b_a3b_local_train.py" in remote_script
    assert "qwen_local_train.py" not in remote_script


def test_scaleup_planner_qwen_data_prep_contract_rejects_super3_drift() -> None:
    contract = qwen_data_prep_config_contract("/models/qwen3-4b")
    contract["chat_template"] = "super3"

    with pytest.raises(ValueError, match="chat_template='tokenizer'"):
        validate_qwen_data_prep_config(contract)


def test_scaleup_planner_normalizes_iter_checkpoint_to_root(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/Qwen3-30B-A3B-Instruct-2507",
            "--pretrained-checkpoint",
            "/runs/v8/checkpoints/iter_0000779",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)
    remote_script = render_remote_train_script(manifest)

    assert manifest["training"]["pretrained_checkpoint"] == "/runs/v8/checkpoints"
    assert "--pretrained-checkpoint /runs/v8/checkpoints" in local_script
    assert "export SUPER3_M1_PRETRAINED_CHECKPOINT=/runs/v8/checkpoints" in remote_script
    assert "iter_0000779" not in remote_script


def test_scaleup_planner_can_emit_uncapped_m0_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-4b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-4b-bridge",
            "--uncapped-data",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["uncapped"] is True
    assert manifest["data"]["max_train_per_dataset"] is None
    assert manifest["data"]["max_val_per_dataset"] is None
    assert "--uncapped" in local_script
    assert "--max-train-per-dataset" not in local_script
    assert "--max-val-per-dataset" not in local_script


def test_scaleup_planner_can_emit_math_reasoning_replay_v3_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "reasoning_replay_v3",
            "--math-v3-final-answer-aux-weight",
            "0.15",
            "--math-v3-format-repair-weight",
            "0.04",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "reasoning_replay_v3"
    assert manifest["data"]["math_v3_weights"]["final_answer_aux"] == 0.15
    assert "--math-supervision-strategy reasoning_replay_v3" in local_script
    assert "--math-v3-verified-full-solution-weight 1.0" in local_script
    assert "--math-v3-final-answer-aux-weight 0.15" in local_script
    assert "--math-v3-format-repair-weight 0.04" in local_script


def test_scaleup_planner_can_emit_hard_math_recovery_v4_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_recovery_v4",
            "--math-v4-verified-full-solution-weight",
            "0.3",
            "--math-v4-final-answer-aux-weight",
            "0.0",
            "--math-v4-format-repair-weight",
            "0.0",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "hard_math_recovery_v4"
    assert manifest["data"]["math_v4_weights"]["hard_verified_full_solution"] == 1.0
    assert manifest["data"]["math_v4_weights"]["verified_full_solution"] == 0.3
    assert "--math-supervision-strategy hard_math_recovery_v4" in local_script
    assert "--math-v4-hard-verified-full-solution-weight 1.0" in local_script
    assert "--math-v4-verified-full-solution-weight 0.3" in local_script
    assert "--math-v4-final-answer-aux-weight 0.0" in local_script
    assert "--math-v4-format-repair-weight 0.0" in local_script


def test_scaleup_planner_can_emit_hard_math_precision_v5_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_precision_v5",
            "--math-v5-hard-verified-full-solution-weight",
            "0.4",
            "--math-v5-verified-full-solution-weight",
            "0.0",
            "--math-v5-final-answer-aux-weight",
            "0.0",
            "--math-v5-format-repair-weight",
            "0.0",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "hard_math_precision_v5"
    assert manifest["data"]["math_v5_weights"]["hard_verified_full_solution"] == 0.4
    assert manifest["data"]["math_v5_weights"]["verified_full_solution"] == 0.0
    assert "--math-supervision-strategy hard_math_precision_v5" in local_script
    assert "--math-v5-hard-verified-full-solution-weight 0.4" in local_script
    assert "--math-v5-verified-full-solution-weight 0.0" in local_script
    assert "--math-v5-final-answer-aux-weight 0.0" in local_script
    assert "--math-v5-format-repair-weight 0.0" in local_script


def test_scaleup_planner_can_emit_hard_math_balanced_v6_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_balanced_v6",
            "--math-v6-hard-verified-full-solution-weight",
            "0.5",
            "--math-v6-verified-full-solution-weight",
            "0.2",
            "--math-v6-final-answer-aux-weight",
            "0.04",
            "--math-v6-format-repair-weight",
            "0.02",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "hard_math_balanced_v6"
    assert manifest["data"]["math_v6_weights"]["hard_verified_full_solution"] == 0.5
    assert manifest["data"]["math_v6_weights"]["verified_full_solution"] == 0.2
    assert manifest["data"]["math_v6_weights"]["final_answer_aux"] == 0.04
    assert manifest["data"]["math_v6_weights"]["format_repair"] == 0.02
    assert "--math-supervision-strategy hard_math_balanced_v6" in local_script
    assert "--math-v6-hard-verified-full-solution-weight 0.5" in local_script
    assert "--math-v6-verified-full-solution-weight 0.2" in local_script
    assert "--math-v6-final-answer-aux-weight 0.04" in local_script
    assert "--math-v6-format-repair-weight 0.02" in local_script


def test_scaleup_planner_can_emit_hard_math_long_reasoning_v7_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_long_reasoning_v7",
            "--math-v7-hard-verified-full-solution-weight",
            "0.8",
            "--math-v7-verified-full-solution-weight",
            "0.0",
            "--math-v7-final-answer-aux-weight",
            "0.0",
            "--math-v7-format-repair-weight",
            "0.0",
            "--math-sidecar-m0-input-dir",
            "/data/full_m0",
            "--math-sidecar-max-records-per-env",
            "50000",
            "--pack-size",
            "8192",
            "--seq-length",
            "8192",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "hard_math_long_reasoning_v7"
    assert manifest["data"]["math_v7_weights"]["hard_verified_full_solution"] == 0.8
    assert manifest["data"]["math_v7_weights"]["verified_full_solution"] == 0.0
    assert manifest["data"]["math_v7_weights"]["final_answer_aux"] == 0.0
    assert manifest["data"]["math_v7_weights"]["format_repair"] == 0.0
    assert manifest["data"]["math_sidecar_m0_input_dir"] == "/data/full_m0"
    assert manifest["data"]["math_sidecar_max_records_per_env"] == 50000
    assert manifest["packing"]["pack_size"] == 8192
    assert manifest["training"]["seq_length"] == 8192
    assert "--math-supervision-strategy hard_math_long_reasoning_v7" in local_script
    assert "--math-v7-hard-verified-full-solution-weight 0.8" in local_script
    assert "--math-v7-verified-full-solution-weight 0.0" in local_script
    assert "--math-v7-final-answer-aux-weight 0.0" in local_script
    assert "--math-v7-format-repair-weight 0.0" in local_script
    assert "--math-sidecar-m0-input-dir /data/full_m0" in local_script
    assert "--math-sidecar-max-records-per-env 50000" in local_script
    assert "pack_size=8192" in local_script


def test_scaleup_planner_can_emit_hard_math_clean_final_v8_data_prep(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_clean_final_v8",
            "--math-v8-hard-verified-full-solution-weight",
            "0.75",
            "--math-v8-verified-full-solution-weight",
            "0.0",
            "--math-v8-final-answer-aux-weight",
            "0.0",
            "--math-v8-format-repair-weight",
            "0.0",
            "--math-sidecar-m0-input-dir",
            "/data/full_m0",
            "--pack-size",
            "8192",
            "--seq-length",
            "8192",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "hard_math_clean_final_v8"
    assert manifest["data"]["math_v8_weights"]["hard_verified_full_solution"] == 0.75
    assert manifest["data"]["math_v8_weights"]["verified_full_solution"] == 0.0
    assert manifest["data"]["math_v8_weights"]["final_answer_aux"] == 0.0
    assert manifest["data"]["math_v8_weights"]["format_repair"] == 0.0
    assert "--math-supervision-strategy hard_math_clean_final_v8" in local_script
    assert "--math-v8-hard-verified-full-solution-weight 0.75" in local_script
    assert "--math-v8-verified-full-solution-weight 0.0" in local_script
    assert "--math-v8-final-answer-aux-weight 0.0" in local_script
    assert "--math-v8-format-repair-weight 0.0" in local_script
    assert "--math-sidecar-m0-input-dir /data/full_m0" in local_script
    assert "pack_size=8192" in local_script


def test_scaleup_planner_can_emit_hard_math_recurrence_v9_data_prep(tmp_path) -> None:
    corpus_path = tmp_path / "aime25_hmmt_math_corpus.jsonl"
    corpus_path.write_text("", encoding="utf-8")
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_recurrence_v9",
            "--math-v9-hard-verified-full-solution-weight",
            "0.5",
            "--math-v9-verified-full-solution-weight",
            "0.0",
            "--math-v9-final-answer-aux-weight",
            "0.0",
            "--math-v9-format-repair-weight",
            "0.0",
            "--math-sidecar-m0-input-dir",
            "/data/full_m0",
            "--math-decontaminate-against-corpus",
            str(corpus_path),
            "--pack-size",
            "8192",
            "--seq-length",
            "8192",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_supervision_strategy"] == "hard_math_recurrence_v9"
    assert manifest["data"]["math_v9_weights"]["hard_verified_full_solution"] == 0.5
    assert manifest["data"]["math_v9_weights"]["verified_full_solution"] == 0.0
    assert manifest["data"]["math_v9_weights"]["final_answer_aux"] == 0.0
    assert manifest["data"]["math_v9_weights"]["format_repair"] == 0.0
    assert manifest["data"]["math_decontaminate_against_corpus"] == str(corpus_path)
    assert "--math-supervision-strategy hard_math_recurrence_v9" in local_script
    assert "--math-v9-hard-verified-full-solution-weight 0.5" in local_script
    assert "--math-v9-verified-full-solution-weight 0.0" in local_script
    assert "--math-v9-final-answer-aux-weight 0.0" in local_script
    assert "--math-v9-format-repair-weight 0.0" in local_script
    assert f"--decontaminate-math-against-corpus {corpus_path}" in local_script
    assert "--math-sidecar-m0-input-dir /data/full_m0" in local_script
    assert "pack_size=8192" in local_script


def test_scaleup_planner_plumbs_math_decontamination_flags_through_local_script(tmp_path) -> None:
    """Regression: prepare_m1_agentic_sft.py requires
    --decontaminate-math-against-corpus for V7+ strategies (or
    --skip-math-decontamination-check). The planner must plumb both
    flags through to the local data-prep script, otherwise V7+
    scaleup bundles fail with the prepare-side guard.
    """
    corpus_path = tmp_path / "aime25_hmmt_corpus.jsonl"
    corpus_path.write_text("", encoding="utf-8")
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_long_reasoning_v7",
            "--math-decontaminate-against-corpus",
            str(corpus_path),
            "--math-decontaminate-ngram-size",
            "6",
            "--math-decontaminate-blocker-threshold",
            "0.4",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_decontaminate_against_corpus"] == str(corpus_path)
    assert manifest["data"]["math_decontaminate_ngram_size"] == 6
    assert manifest["data"]["math_decontaminate_blocker_threshold"] == 0.4
    assert manifest["data"]["math_skip_decontamination_check"] is False
    assert f"--decontaminate-math-against-corpus {corpus_path}" in local_script
    assert "--decontaminate-math-ngram-size 6" in local_script
    assert "--decontaminate-math-blocker-threshold 0.4" in local_script
    assert "--skip-math-decontamination-check" not in local_script


def test_scaleup_planner_can_emit_skip_decontamination_check(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "hard_math_clean_final_v8",
            "--math-skip-decontamination-check",
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    assert manifest["data"]["math_skip_decontamination_check"] is True
    assert manifest["data"]["math_decontaminate_against_corpus"] is None
    assert "--skip-math-decontamination-check" in local_script
    assert "--decontaminate-math-against-corpus" not in local_script


def test_scaleup_planner_omits_decontamination_flags_when_not_set(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-30b-a3b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-30b-a3b-bridge",
            "--math-supervision-strategy",
            "reasoning_replay_v3",  # V3 doesn't require decontam
        ]
    )
    manifest = build_manifest(args)
    local_script = render_local_data_prep_script(manifest)

    # V3 doesn't pass decontamination flags by default; older bundle
    # behavior is preserved.
    assert manifest["data"]["math_decontaminate_against_corpus"] is None
    assert manifest["data"]["math_skip_decontamination_check"] is False
    assert "--decontaminate-math-against-corpus" not in local_script
    assert "--skip-math-decontamination-check" not in local_script


def test_write_plan_outputs_executable_scripts(tmp_path) -> None:
    manifest = build_manifest(_args(tmp_path))
    write_plan(manifest, overwrite=True)

    for key in (
        "local_data_prep_script",
        "sync_script",
        "remote_train_script",
        "eval_dry_run_script",
    ):
        path = Path(manifest["outputs"][key])
        assert path.exists()
        assert path.stat().st_mode & 0o111

    assert Path(manifest["outputs"]["manifest"]).exists()
    assert Path(manifest["outputs"]["report"]).read_text(encoding="utf-8").startswith(
        "# Qwen M1 Agentic SFT Scale-up Plan"
    )


def test_scaleup_planner_accepts_launcher_available_eval_config(tmp_path) -> None:
    args = build_parser().parse_args(
        [
            "--output-dir",
            str(tmp_path / "scaleup"),
            "--repo-dir",
            str(tmp_path / "repo"),
            "--qwen-hf-model",
            "/models/qwen3-4b",
            "--pretrained-checkpoint",
            "/checkpoints/qwen3-4b-bridge",
            "--eval-config",
            "m1_full_basket_launcher_available",
        ]
    )
    manifest = build_manifest(args)
    assert manifest["eval"]["config"] == "m1_full_basket_launcher_available"
    assert "m1_full_basket_launcher_available" in render_eval_script(manifest)


def test_scaleup_requires_qwen_paths_when_env_absent(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("SUPER3_M1_QWEN_HF_MODEL", raising=False)
    monkeypatch.delenv("SUPER3_M1_PRETRAINED_CHECKPOINT", raising=False)
    args = build_parser().parse_args(["--output-dir", str(tmp_path / "scaleup")])

    with pytest.raises(ValueError, match="--qwen-hf-model"):
        build_manifest(args)
