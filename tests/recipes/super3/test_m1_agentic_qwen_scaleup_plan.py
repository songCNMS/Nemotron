from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m1_agentic_sft.plan_qwen_scaleup_run import (
    AGENTIC_M0_DATASET_IDS,
    build_manifest,
    build_parser,
    render_eval_script,
    render_local_data_prep_script,
    render_remote_train_script,
    write_plan,
)


def _args(tmp_path: Path):
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
    assert "plan_m1_agentic_sft_training.py" in local_script
    assert "--dataset-id m0_search_hotpotqa" in local_script
    assert "--dataset-id m0_math_numinamath" in local_script
    assert "tokenizer.model=/models/qwen3-4b" in local_script
    assert "pack_size=512" in local_script

    assert "qwen_local_train.py" in remote_script
    assert "--nproc_per_node=2" in remote_script
    assert "TRAIN_ITERS=" in remote_script
    assert "export TRAIN_ITERS" in remote_script
    assert 'tmux set-environment -g TRAIN_ITERS "$TRAIN_ITERS" 2>/dev/null || true' in remote_script
    assert 'Path("/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup' in remote_script
    assert "dataset.packed_sequence_specs.packed_sequence_size=512" in remote_script
    assert "CUDA_VISIBLE_DEVICES=0,1" in remote_script
    assert "train.global_batch_size=2" in remote_script
    assert "train.eval_interval=7" in remote_script
    assert "--eval-interval 7" in local_script

    assert "super3 eval -c m1_full_basket --dry-run" in eval_script
    assert "run.model=sft:unit_qwen_scaleup" in eval_script
    assert "deployment.checkpoint_path=" in eval_script


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
