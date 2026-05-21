#!/usr/bin/env python3

"""Plan a scaled Qwen3 4B M1 Agentic SFT run.

The task066 smoke proved the full path works:

M0 public data -> M1 Agentic SFT JSONL -> Qwen-tokenizer packed Parquet
-> planner-derived train_iters -> NemTron Qwen3 4B SFT.

This planner writes the scripts needed to repeat that path at a larger scale
without hand-copying shell commands between workspaces.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[5]

DEFAULT_OUTPUT_DIR = REPO_ROOT.parent / "outputs" / "task067_qwen_scaleup"
DEFAULT_LOCAL_VENV = Path("/work-agents/.venv")
DEFAULT_NEMTRON_VENV = Path("/root/nemotron_session5_venv")
DEFAULT_REMOTE_ROOT = Path("/work-agents/intern_nemontron_code_reading/task067_qwen_scaleup")
DEFAULT_RUN_NAME = "qwen_m1_agentic_sft_scaleup"

QWEN_MODEL_ENV_VAR = "SUPER3_M1_QWEN_HF_MODEL"
QWEN_CHECKPOINT_ENV_VAR = "SUPER3_M1_PRETRAINED_CHECKPOINT"

AGENTIC_M0_DATASET_IDS: tuple[str, ...] = (
    "m0_search_hotpotqa",
    "m0_search_musique",
    "m0_coding_mbpp",
    "m0_terminal_bash_commands",
    "m0_swe_patch_lite",
    "m0_tool_calling_hermes",
    "m0_tool_calling_hermes_multi",
    "m0_tool_call_repair_negative_hermes",
    "m0_structured_outputs_hermes_json",
    "m0_reasoning_gsm8k",
    "m0_math_numinamath",
)


JsonDict = dict[str, Any]


def _q(value: str | Path) -> str:
    return shlex.quote(str(value))


def _env_or_arg(value: str | None, env_var: str, flag: str) -> str:
    resolved = value or os.environ.get(env_var)
    if not resolved:
        raise ValueError(f"{flag} is required, or set {env_var}")
    return resolved


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@dataclass(frozen=True)
class ScaleupPaths:
    output_dir: Path
    m0_dir: Path
    m1_dir: Path
    packed_dir: Path
    plan_dir: Path
    checkpoint_dir: Path
    report_path: Path
    manifest_path: Path
    local_script_path: Path
    sync_script_path: Path
    remote_train_script_path: Path
    eval_script_path: Path
    remote_run_root: Path


def build_paths(output_dir: Path, remote_root: Path) -> ScaleupPaths:
    output_dir = output_dir.resolve()
    remote_run_root = remote_root / output_dir.name
    return ScaleupPaths(
        output_dir=output_dir,
        m0_dir=output_dir / "m0_agentic",
        m1_dir=output_dir / "m1_agentic_sft",
        packed_dir=output_dir / "packed_qwen",
        plan_dir=output_dir / "training_plan",
        checkpoint_dir=output_dir / "checkpoints",
        report_path=output_dir / "report.md",
        manifest_path=output_dir / "scaleup_manifest.json",
        local_script_path=output_dir / "run_local_data_prep.sh",
        sync_script_path=output_dir / "sync_to_nemtron.sh",
        remote_train_script_path=output_dir / "run_nemtron_train.sh",
        eval_script_path=output_dir / "run_eval_basket_dry_run.sh",
        remote_run_root=remote_run_root,
    )


def build_manifest(args: argparse.Namespace) -> JsonDict:
    qwen_hf_model = _env_or_arg(args.qwen_hf_model, QWEN_MODEL_ENV_VAR, "--qwen-hf-model")
    pretrained_checkpoint = _env_or_arg(
        args.pretrained_checkpoint,
        QWEN_CHECKPOINT_ENV_VAR,
        "--pretrained-checkpoint",
    )
    paths = build_paths(args.output_dir, args.remote_root)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "task": "task067_m1_agentic_qwen_scaleup",
        "stage": "M1 Agentic SFT scale-up",
        "run_name": args.run_name,
        "repo_dir": str(args.repo_dir.resolve()),
        "paths": {
            "output_dir": str(paths.output_dir),
            "m0_dir": str(paths.m0_dir),
            "m1_dir": str(paths.m1_dir),
            "packed_dir": str(paths.packed_dir),
            "plan_dir": str(paths.plan_dir),
            "checkpoint_dir": str(paths.checkpoint_dir),
            "remote_root": str(args.remote_root),
            "remote_run_root": str(paths.remote_run_root),
        },
        "data": {
            "m0_dataset_ids": list(AGENTIC_M0_DATASET_IDS),
            "uncapped": args.uncapped_data,
            "max_train_per_dataset": None if args.uncapped_data else args.max_train_per_dataset,
            "max_val_per_dataset": None if args.uncapped_data else args.max_val_per_dataset,
            "expected_agentic_environments": 11,
        },
        "packing": {
            "tokenizer_model": qwen_hf_model,
            "num_shards": args.num_shards,
            "pack_size": args.pack_size,
            "train_ratio": args.train_ratio,
            "valid_ratio": args.valid_ratio,
            "test_ratio": args.test_ratio,
        },
        "training": {
            "pretrained_checkpoint": pretrained_checkpoint,
            "epochs": args.epochs,
            "global_batch_size": args.global_batch_size,
            "micro_batch_size": args.micro_batch_size,
            "seq_length": args.seq_length,
            "eval_interval": args.eval_interval,
            "save_interval": args.save_interval,
            "nemtron_host": args.nemtron_host,
            "nemtron_venv": str(args.nemtron_venv),
            "cuda_visible_devices": args.cuda_visible_devices,
            "nproc_per_node": args.nproc_per_node,
            "master_port": args.master_port,
        },
        "eval": {
            "config": args.eval_config,
            "tasks": "configured by stage3_eval config",
            "dry_run_only": True,
        },
        "outputs": {
            "manifest": str(paths.manifest_path),
            "report": str(paths.report_path),
            "local_data_prep_script": str(paths.local_script_path),
            "sync_script": str(paths.sync_script_path),
            "remote_train_script": str(paths.remote_train_script_path),
            "eval_dry_run_script": str(paths.eval_script_path),
        },
    }


def render_local_data_prep_script(manifest: JsonDict) -> str:
    repo_dir = Path(manifest["repo_dir"])
    paths = manifest["paths"]
    data = manifest["data"]
    packing = manifest["packing"]
    training = manifest["training"]
    dataset_flags = " ".join(
        f"--dataset-id {_q(dataset_id)}" for dataset_id in data["m0_dataset_ids"]
    )
    m0_row_flags = (
        "--uncapped"
        if data.get("uncapped")
        else (
            f"--max-train-per-dataset {int(data['max_train_per_dataset'])} \\\n"
            f"  --max-val-per-dataset {int(data['max_val_per_dataset'])}"
        )
    )
    return f"""#!/usr/bin/env bash
set -euo pipefail

cd {_q(repo_dir)}
source {_q(DEFAULT_LOCAL_VENV / "bin" / "activate")}
export PYTHONPATH="${{PWD}}/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"
export WANDB_MODE="${{WANDB_MODE:-disabled}}"
export WANDB_DISABLED="${{WANDB_DISABLED:-true}}"

python src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py \\
  --output-dir {_q(paths["m0_dir"])} \\
  {dataset_flags} \\
  {m0_row_flags} \\
  --overwrite

python src/nemotron/recipes/super3/milestones/m1_agentic_sft/prepare_m1_agentic_sft.py \\
  --m0-input-dir {_q(paths["m0_dir"])} \\
  --output-dir {_q(paths["m1_dir"])} \\
  --overwrite

python src/nemotron/recipes/super3/stage1_sft/data_prep.py \\
  --config src/nemotron/recipes/super3/stage1_sft/config/data_prep/agentic_v0.yaml \\
  blend_path={_q(Path(paths["m1_dir"]) / "data_blend_agentic_sft_v0.json")} \\
  output_dir={_q(paths["packed_dir"])} \\
  tokenizer.model={_q(packing["tokenizer_model"])} \\
  num_shards={int(packing["num_shards"])} \\
  pack_size={int(packing["pack_size"])} \\
  train_ratio={packing["train_ratio"]} \\
  valid_ratio={packing["valid_ratio"]} \\
  test_ratio={packing["test_ratio"]} \\
  force=true \\
  execution_mode=batch \\
  observability.wandb_log_pipeline_stats=false

python src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py \\
  --packed-sft-dir {_q(Path(paths["packed_dir"]) / "splits")} \\
  --pretrained-checkpoint {_q(training["pretrained_checkpoint"])} \\
  --tokenizer-model {_q(packing["tokenizer_model"])} \\
  --save-dir {_q(paths["checkpoint_dir"])} \\
  --output-dir {_q(paths["plan_dir"])} \\
  --run-name {_q(manifest["run_name"])} \\
  --repo-dir {_q(repo_dir)} \\
  --venv {_q(training["nemtron_venv"])} \\
  --gpus-per-node {int(training["nproc_per_node"])} \\
  --global-batch-size {int(training["global_batch_size"])} \\
  --micro-batch-size {int(training["micro_batch_size"])} \\
  --epochs {training["epochs"]} \\
  --eval-interval {int(training["eval_interval"])} \\
  --seq-length {int(training["seq_length"])} \\
  --save-interval {int(training["save_interval"])} \\
  --overwrite
"""


def render_sync_script(manifest: JsonDict) -> str:
    repo_dir = Path(manifest["repo_dir"])
    output_dir = Path(manifest["paths"]["output_dir"])
    remote_host = manifest["training"]["nemtron_host"]
    remote_root = manifest["paths"]["remote_root"]
    cleanup_cmd = (
        f"rm -rf {_q(Path(remote_root) / 'Nemotron')} {_q(manifest['paths']['remote_run_root'])} "
        f"&& mkdir -p {_q(remote_root)}"
    )
    extract_cmd = f"tar -xzf - -C {_q(remote_root)}"
    return f"""#!/usr/bin/env bash
set -euo pipefail

ssh {_q(remote_host)} {_q(cleanup_cmd)}
tar --exclude='.git' \\
  --exclude='.pytest_cache' \\
  --exclude='__pycache__' \\
  -czf - -C {_q(repo_dir.parent)} {_q(repo_dir.name)} | \\
  ssh {_q(remote_host)} {_q(extract_cmd)}
tar -czf - -C {_q(output_dir.parent)} {_q(output_dir.name)} | \\
  ssh {_q(remote_host)} {_q(extract_cmd)}
"""


def render_remote_train_script(manifest: JsonDict) -> str:
    training = manifest["training"]
    packing = manifest["packing"]
    remote_host = training["nemtron_host"]
    remote_root = manifest["paths"]["remote_root"]
    remote_repo = Path(remote_root) / "Nemotron"
    remote_run_root = Path(manifest["paths"]["remote_run_root"])
    remote_plan = remote_run_root / "training_plan" / manifest["run_name"] / "training_manifest.json"
    remote_ckpt = remote_run_root / "checkpoints"
    log_dir = remote_run_root / "logs"
    session = f"task067_{manifest['run_name']}"
    torchrun_args = [
        "python",
        "-m",
        "torch.distributed.run",
        f"--nproc_per_node={int(training['nproc_per_node'])}",
        "src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py",
        "--config",
        "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml",
        f"dataset.seq_length={int(training['seq_length'])}",
        f"dataset.packed_sequence_specs.packed_sequence_size={int(training['seq_length'])}",
        f"model.seq_length={int(training['seq_length'])}",
        "train.train_iters=$TRAIN_ITERS",
        f"train.eval_interval={int(training['eval_interval'])}",
        f"train.global_batch_size={int(training['global_batch_size'])}",
        f"train.micro_batch_size={int(training['micro_batch_size'])}",
        "scheduler.lr_decay_iters=$TRAIN_ITERS",
        "scheduler.lr_warmup_iters=0",
        f"checkpoint.save_interval={int(training['save_interval'])}",
        "logger.log_interval=10",
    ]
    train_cmd_parts = [
        f"cd {_q(remote_repo)}",
        f"source {_q(Path(training['nemtron_venv']) / 'bin' / 'activate')}",
        "export PYTHONPATH=$PWD/src",
        f"export SUPER3_M1_QWEN_HF_MODEL={_q(packing['tokenizer_model'])}",
        f"export SUPER3_M1_AGENTIC_PACKED_DIR={_q(remote_run_root / 'packed_qwen' / 'splits')}",
        f"export SUPER3_M1_TOKENIZER_MODEL={_q(packing['tokenizer_model'])}",
        f"export SUPER3_M1_PRETRAINED_CHECKPOINT={_q(training['pretrained_checkpoint'])}",
        f"export SUPER3_M1_SFT_SAVE={_q(remote_ckpt)}",
        f"export CUDA_VISIBLE_DEVICES={_q(training['cuda_visible_devices'])}",
        "export CUDA_DEVICE_MAX_CONNECTIONS=1",
        f"export MASTER_PORT={int(training['master_port'])}",
        "export WANDB_MODE=disabled",
        "export WANDB_DISABLED=true",
        "export TOKENIZERS_PARALLELISM=false",
        f"{' '.join(torchrun_args)} 2>&1 | tee {_q(log_dir / 'train.log')}",
    ]
    train_cmd = " && ".join(train_cmd_parts)
    remote_cmd = f"""set -euo pipefail
mkdir -p {_q(log_dir)}
TRAIN_ITERS="$(python - <<'PY'
import json
from pathlib import Path
manifest = json.loads(Path({json.dumps(str(remote_plan))}).read_text())
print(manifest["training"]["train_iters"])
PY
)"
export TRAIN_ITERS
tmux set-environment -g TRAIN_ITERS "$TRAIN_ITERS"
tmux kill-session -t {_q(session)} 2>/dev/null || true
tmux new-session -d -s {_q(session)} {_q(train_cmd)}
tmux ls | grep {_q(session)}
"""
    return f"""#!/usr/bin/env bash
set -euo pipefail

ssh {_q(remote_host)} {_q(remote_cmd)}
"""


def render_eval_script(manifest: JsonDict) -> str:
    repo_dir = Path(manifest["repo_dir"])
    eval_config = manifest["eval"]["config"]
    model_ref = f"sft:{manifest['run_name']}"
    remote_ckpt = Path(manifest["paths"]["remote_run_root"]) / "checkpoints"
    return f"""#!/usr/bin/env bash
set -euo pipefail

cd {_q(repo_dir)}
source {_q(DEFAULT_LOCAL_VENV / "bin" / "activate")}
export PYTHONPATH="${{PWD}}/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"

# Dry-run first: this validates the selected M1 eval basket config without
# launching NeMo Evaluator. Replace deployment/checkpoint overrides as needed
# once the checkpoint has been exported or registered as a model artifact.
python -m nemotron super3 eval -c {_q(eval_config)} --dry-run \\
  run.model={_q(model_ref)} \\
  deployment.checkpoint_path={_q(remote_ckpt)}
"""


def render_report(manifest: JsonDict) -> str:
    data = manifest["data"]
    training = manifest["training"]
    row_scope = (
        "uncapped"
        if data.get("uncapped")
        else f"train={data['max_train_per_dataset']}, val={data['max_val_per_dataset']}"
    )
    return "\n".join(
        [
            "# Qwen M1 Agentic SFT Scale-up Plan",
            "",
            f"- Run name: `{manifest['run_name']}`",
            f"- M0 datasets: {len(data['m0_dataset_ids'])} agentic SFT slices",
            f"- Rows per dataset: {row_scope}",
            f"- Pack size / seq length: {manifest['packing']['pack_size']} / {training['seq_length']}",
            f"- Eval / save interval: {training['eval_interval']} / {training['save_interval']}",
            (
                f"- NemTron launch: host `{training['nemtron_host']}`, "
                f"GPUs `{training['cuda_visible_devices']}`, nproc={training['nproc_per_node']}"
            ),
            f"- Eval basket: `{manifest['eval']['config']}` dry-run script emitted",
            "",
            "## Scripts",
            "",
            f"- Local data prep: `{manifest['outputs']['local_data_prep_script']}`",
            f"- Sync to NemTron: `{manifest['outputs']['sync_script']}`",
            f"- Remote train: `{manifest['outputs']['remote_train_script']}`",
            f"- Eval dry-run: `{manifest['outputs']['eval_dry_run_script']}`",
            "",
        ]
    )


def write_plan(manifest: JsonDict, *, overwrite: bool) -> None:
    output_dir = Path(manifest["paths"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = [Path(path) for path in manifest["outputs"].values()]
    existing = [path for path in outputs if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"plan outputs already exist; pass --overwrite to replace them:\n{formatted}")

    Path(manifest["outputs"]["manifest"]).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(manifest["outputs"]["report"]).write_text(render_report(manifest), encoding="utf-8")
    _write_executable(Path(manifest["outputs"]["local_data_prep_script"]), render_local_data_prep_script(manifest))
    _write_executable(Path(manifest["outputs"]["sync_script"]), render_sync_script(manifest))
    _write_executable(Path(manifest["outputs"]["remote_train_script"]), render_remote_train_script(manifest))
    _write_executable(Path(manifest["outputs"]["eval_dry_run_script"]), render_eval_script(manifest))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--repo-dir", type=Path, default=REPO_ROOT)
    parser.add_argument("--run-name", default=DEFAULT_RUN_NAME)
    parser.add_argument("--qwen-hf-model", default=None)
    parser.add_argument("--pretrained-checkpoint", default=None)
    parser.add_argument("--max-train-per-dataset", type=int, default=100)
    parser.add_argument("--max-val-per-dataset", type=int, default=25)
    parser.add_argument(
        "--uncapped-data",
        action="store_true",
        help="Generate M0 data with prepare_m0_assets.py --uncapped instead of per-dataset row caps.",
    )
    parser.add_argument("--num-shards", type=int, default=32)
    parser.add_argument("--pack-size", type=int, default=4096)
    parser.add_argument("--seq-length", type=int, default=4096)
    parser.add_argument("--train-ratio", type=float, default=0.98)
    parser.add_argument("--valid-ratio", type=float, default=0.02)
    parser.add_argument("--test-ratio", type=float, default=0.0)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--global-batch-size", type=int, default=2)
    parser.add_argument("--micro-batch-size", type=int, default=1)
    parser.add_argument("--eval-interval", type=int, default=100)
    parser.add_argument("--save-interval", type=int, default=20)
    parser.add_argument("--remote-root", type=Path, default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--nemtron-host", default="NemTron")
    parser.add_argument("--nemtron-venv", type=Path, default=DEFAULT_NEMTRON_VENV)
    parser.add_argument("--cuda-visible-devices", default="0,1")
    parser.add_argument("--nproc-per-node", type=int, default=2)
    parser.add_argument("--master-port", type=int, default=29693)
    parser.add_argument(
        "--eval-config",
        choices=(
            "m1_basket",
            "m1_full_basket",
            "m1_full_basket_launcher_available",
        ),
        default="m1_basket",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = build_manifest(args)
        write_plan(manifest, overwrite=args.overwrite)
    except Exception as exc:  # noqa: BLE001
        print(f"plan_qwen_scaleup_run.py: error: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "manifest": manifest["outputs"]["manifest"],
                "local_data_prep_script": manifest["outputs"]["local_data_prep_script"],
                "remote_train_script": manifest["outputs"]["remote_train_script"],
                "eval_dry_run_script": manifest["outputs"]["eval_dry_run_script"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
