#!/usr/bin/env python3

"""Plan a reproducible M1 Agentic SFT training run from packed local data."""

from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import stat
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_PACKED_SFT_DIR: Path | None = None
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_agentic_sft_v0/train-plans")
DEFAULT_SAVE_DIR = Path("../output/super3/m1_agentic_sft_v0/checkpoints")
DEFAULT_CONFIG_PATH = Path("src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml")
DEFAULT_SCRIPT_PATH = Path("src/nemotron/recipes/super3/stage1_sft/train.py")
DEFAULT_REPO_DIR: Path | None = None
MILESTONE = "M1"
STAGE = "Agentic SFT v0 training"

JsonDict = dict[str, Any]


@dataclass(frozen=True)
class SplitSummary:
    shards: int
    rows: int | None
    path: str


def read_json(path: Path) -> JsonDict:
    with path.open(encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def normalize_packed_sft_dir(path: Path) -> Path:
    if (path / "train").is_dir() and (path / "valid").is_dir():
        return path
    splits_dir = path / "splits"
    if (splits_dir / "train").is_dir() and (splits_dir / "valid").is_dir():
        return splits_dir
    raise FileNotFoundError(f"packed SFT directory must contain train/ and valid/ splits: {path}")


def metadata_path_for(packed_sft_dir: Path) -> Path | None:
    candidates = [
        packed_sft_dir / "metadata.json",
        packed_sft_dir.parent / "metadata.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def maybe_count_parquet_rows(paths: Sequence[Path]) -> int | None:
    try:
        import pyarrow.parquet as pq
    except Exception:
        return None

    total = 0
    for path in paths:
        try:
            total += pq.ParquetFile(path).metadata.num_rows
        except Exception:
            return None
    return total


def summarize_split(split_dir: Path) -> SplitSummary:
    if not split_dir.is_dir():
        return SplitSummary(shards=0, rows=None, path=str(split_dir))
    shards = sorted(split_dir.glob("*.parquet"))
    rows = maybe_count_parquet_rows(shards) if shards else 0
    return SplitSummary(shards=len(shards), rows=rows, path=str(split_dir))


def infer_tokenizer_model(metadata: Mapping[str, Any], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    value = metadata.get("tokenizer_uri") or metadata.get("metadata", {}).get("tokenizer_uri")
    if isinstance(value, str) and value.startswith("file://"):
        return value.removeprefix("file://")
    if isinstance(value, str) and value:
        return value
    return None


def compute_train_iters(
    *,
    explicit_train_iters: int | None,
    train_rows: int | None,
    global_batch_size: int,
    epochs: float,
    fallback: int,
) -> int:
    if explicit_train_iters is not None:
        return explicit_train_iters
    if train_rows is None:
        return fallback
    return max(1, math.ceil(train_rows * epochs / global_batch_size))


def shell_quote(value: str | os.PathLike[str] | int) -> str:
    return shlex.quote(str(value))


def build_torchrun_command(manifest: Mapping[str, Any]) -> list[str]:
    resources = manifest["resources"]
    training = manifest["training"]
    paths = manifest["paths"]
    nodes = int(resources.get("nodes", 1))
    if nodes != 1:
        # Multi-node launches need rendezvous endpoint, node_rank, and a launcher
        # (slurm srun, MPI, or torchrun's c10d backend) that this planner does
        # not have enough context to emit safely. Surface the limit explicitly
        # instead of silently downgrading to a single-node run.
        raise ValueError(
            f"plan_m1_agentic_sft_training only emits single-node launch commands, got nodes={nodes}; "
            "wrap the produced script with slurm srun or extend build_torchrun_command for multi-node"
        )
    command = [
        "python",
        "-m",
        "torch.distributed.run",
        f"--nproc_per_node={resources['gpus_per_node']}",
        str(paths["script_path"]),
        "--config",
        str(paths["config_path"]),
        f"train.train_iters={training['train_iters']}",
        f"train.eval_interval={training['eval_interval']}",
        f"train.global_batch_size={training['global_batch_size']}",
        f"train.micro_batch_size={training['micro_batch_size']}",
        f"model.seq_length={training['seq_length']}",
        f"dataset.seq_length={training['seq_length']}",
        f"dataset.packed_sequence_specs.packed_sequence_size={training['seq_length']}",
        f"checkpoint.save_interval={training['save_interval']}",
    ]
    if training.get("optimizer_lr") is not None:
        command.append(f"++optimizer.lr={training['optimizer_lr']}")
    if training.get("scheduler_min_lr") is not None:
        command.append(f"++optimizer.min_lr={training['scheduler_min_lr']}")
    if training.get("lr_warmup_iters") is not None:
        command.append(f"scheduler.lr_warmup_iters={training['lr_warmup_iters']}")
    if training.get("lr_decay_iters") is not None:
        command.append(f"++scheduler.lr_decay_iters={training['lr_decay_iters']}")
    return command


def render_run_script(manifest: Mapping[str, Any]) -> str:
    paths = manifest["paths"]
    env = manifest["env"]
    command = " ".join(shell_quote(part) for part in build_torchrun_command(manifest))
    venv = env.get("venv")
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"cd {shell_quote(paths['repo_dir'])}",
    ]
    if venv:
        lines.extend(
            [
                f"source {shell_quote(Path(str(venv)) / 'bin' / 'activate')}",
            ]
        )
    lines.extend(
        [
            f"export SUPER3_M1_AGENTIC_PACKED_DIR={shell_quote(paths['packed_sft_dir'])}",
            f"export SUPER3_M1_TOKENIZER_MODEL={shell_quote(paths['tokenizer_model'])}",
            f"export SUPER3_M1_PRETRAINED_CHECKPOINT={shell_quote(paths['pretrained_checkpoint'])}",
            f"export SUPER3_M1_SFT_SAVE={shell_quote(paths['save_dir'])}",
            "export PYTHONPATH=\"${PWD}/src${PYTHONPATH:+:${PYTHONPATH}}\"",
            "export WANDB_MODE=\"${WANDB_MODE:-offline}\"",
            "export WANDB_DISABLED=\"${WANDB_DISABLED:-true}\"",
            "",
            command,
            "",
        ]
    )
    return "\n".join(lines)


def write_run_script(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    splits = manifest["splits"]
    lines = [
        "# M1 Agentic SFT v0 Training Plan",
        "",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- Packed SFT dir: `{manifest['paths']['packed_sft_dir']}`",
        f"- Pretrained checkpoint: `{manifest['paths']['pretrained_checkpoint']}`",
        f"- Save dir: `{manifest['paths']['save_dir']}`",
        f"- Config: `{manifest['paths']['config_path']}`",
        f"- Run script: `{manifest['outputs']['run_script']}`",
        f"- Missing checkpoint allowed: `{manifest['validation']['allow_missing_checkpoint']}`",
        "",
        "## Splits",
        "",
        "| Split | Shards | Rows | Path |",
        "|---|---:|---:|---|",
    ]
    for split_name in ("train", "valid", "test"):
        split = splits[split_name]
        rows = split["rows"] if split["rows"] is not None else "unknown"
        lines.append(f"| {split_name} | {split['shards']} | {rows} | `{split['path']}` |")
    lines.extend(
        [
            "",
            "## Training",
            "",
            f"- `train_iters`: {manifest['training']['train_iters']}",
            f"- `eval_interval`: {manifest['training']['eval_interval']}",
            f"- `global_batch_size`: {manifest['training']['global_batch_size']}",
            f"- `micro_batch_size`: {manifest['training']['micro_batch_size']}",
            f"- `seq_length`: {manifest['training']['seq_length']}",
            f"- `epochs`: {manifest['training']['epochs']}",
            f"- `optimizer.lr`: {manifest['training'].get('optimizer_lr')}",
            f"- `scheduler.min_lr`: {manifest['training'].get('scheduler_min_lr')}",
            f"- `scheduler.lr_warmup_iters`: {manifest['training'].get('lr_warmup_iters')}",
            f"- `scheduler.lr_decay_iters`: {manifest['training'].get('lr_decay_iters')}",
            "",
            "## Command",
            "",
            "```bash",
            str(manifest["outputs"]["run_script"]),
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_inputs(
    *,
    packed_sft_dir: Path,
    pretrained_checkpoint: Path,
    tokenizer_model: str,
    allow_missing_checkpoint: bool,
) -> None:
    train_dir = packed_sft_dir / "train"
    valid_dir = packed_sft_dir / "valid"
    if not list(train_dir.glob("*.parquet")):
        raise FileNotFoundError(f"no train parquet shards found in {train_dir}")
    if not list(valid_dir.glob("*.parquet")):
        raise FileNotFoundError(f"no valid parquet shards found in {valid_dir}")
    if not allow_missing_checkpoint and not pretrained_checkpoint.exists():
        raise FileNotFoundError(f"pretrained checkpoint does not exist: {pretrained_checkpoint}")
    if tokenizer_model.startswith("/") and not Path(tokenizer_model).exists():
        raise FileNotFoundError(f"tokenizer model does not exist: {tokenizer_model}")


def ensure_batch_geometry(
    *,
    global_batch_size: int,
    micro_batch_size: int,
    gpus_per_node: int,
    nodes: int,
) -> None:
    """Refuse plans that would crash Megatron's GBS / DP×MBS check at setup.

    Megatron-Core requires ``global_batch_size`` to be a positive multiple of
    ``data_parallel_size * micro_batch_size``. The planner does not surface
    tensor- or pipeline-parallel flags, so DP collapses to
    ``gpus_per_node * nodes`` here — this is a necessary, not sufficient, check
    (a downstream config that adds TP/PP will only ever shrink DP further).
    """
    if global_batch_size <= 0:
        raise ValueError(f"global_batch_size must be positive, got {global_batch_size}")
    if micro_batch_size <= 0:
        raise ValueError(f"micro_batch_size must be positive, got {micro_batch_size}")
    if gpus_per_node <= 0 or nodes <= 0:
        raise ValueError(
            f"gpus_per_node and nodes must be positive, got gpus_per_node={gpus_per_node}, nodes={nodes}"
        )
    dp_size = gpus_per_node * nodes
    step_size = dp_size * micro_batch_size
    if global_batch_size % step_size != 0:
        raise ValueError(
            f"global_batch_size={global_batch_size} must be a positive multiple of "
            f"data_parallel_size * micro_batch_size = {dp_size} * {micro_batch_size} = {step_size}; "
            f"set --global-batch-size to {step_size} or another multiple of {step_size}, "
            f"or lower --gpus-per-node / --nodes"
        )


def build_plan(args: argparse.Namespace) -> JsonDict:
    if args.packed_sft_dir is None:
        raise ValueError("--packed-sft-dir is required")
    ensure_batch_geometry(
        global_batch_size=args.global_batch_size,
        micro_batch_size=args.micro_batch_size,
        gpus_per_node=args.gpus_per_node,
        nodes=args.nodes,
    )
    repo_dir = args.repo_dir if args.repo_dir is not None else Path.cwd()
    packed_sft_dir = normalize_packed_sft_dir(args.packed_sft_dir)
    metadata_path = metadata_path_for(packed_sft_dir)
    metadata = read_json(metadata_path) if metadata_path else {}
    tokenizer_model = infer_tokenizer_model(metadata, args.tokenizer_model)
    if not tokenizer_model:
        raise ValueError("tokenizer model is required when packed metadata has no tokenizer_uri")
    pretrained_checkpoint_value = args.pretrained_checkpoint or os.environ.get("SUPER3_M1_PRETRAINED_CHECKPOINT")
    if not pretrained_checkpoint_value:
        raise ValueError("--pretrained-checkpoint or SUPER3_M1_PRETRAINED_CHECKPOINT is required")
    pretrained_checkpoint = Path(pretrained_checkpoint_value)

    ensure_inputs(
        packed_sft_dir=packed_sft_dir,
        pretrained_checkpoint=pretrained_checkpoint,
        tokenizer_model=tokenizer_model,
        allow_missing_checkpoint=args.allow_missing_checkpoint,
    )

    splits = {
        "train": summarize_split(packed_sft_dir / "train"),
        "valid": summarize_split(packed_sft_dir / "valid"),
        "test": summarize_split(packed_sft_dir / "test"),
    }
    train_iters = compute_train_iters(
        explicit_train_iters=args.train_iters,
        train_rows=splits["train"].rows,
        global_batch_size=args.global_batch_size,
        epochs=args.epochs,
        fallback=args.fallback_train_iters,
    )
    optimizer_lr = getattr(args, "optimizer_lr", None)
    scheduler_min_lr = getattr(args, "scheduler_min_lr", None)
    lr_warmup_iters = getattr(args, "lr_warmup_iters", None)
    lr_decay_iters = getattr(args, "lr_decay_iters", None)
    run_name = args.run_name or f"m1-agentic-sft-v0-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    output_dir = args.output_dir / run_name
    manifest_path = output_dir / "training_manifest.json"
    run_script_path = output_dir / "run_m1_agentic_sft.sh"
    report_path = output_dir / "report.md"
    manifest: JsonDict = {
        "schema_version": 1,
        "milestone": MILESTONE,
        "stage": STAGE,
        "run_name": run_name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "paths": {
            "repo_dir": str(repo_dir),
            "script_path": str(args.script_path),
            "config_path": str(args.config_path),
            "packed_sft_dir": str(packed_sft_dir),
            "metadata_path": str(metadata_path) if metadata_path else None,
            "pretrained_checkpoint": str(pretrained_checkpoint),
            "tokenizer_model": tokenizer_model,
            "save_dir": str(args.save_dir),
        },
        "validation": {
            "allow_missing_checkpoint": args.allow_missing_checkpoint,
        },
        "resources": {
            "nodes": args.nodes,
            "gpus_per_node": args.gpus_per_node,
        },
        "training": {
            "epochs": args.epochs,
            "train_iters": train_iters,
            "eval_interval": args.eval_interval,
            "global_batch_size": args.global_batch_size,
            "micro_batch_size": args.micro_batch_size,
            "seq_length": args.seq_length,
            "save_interval": args.save_interval,
            "optimizer_lr": optimizer_lr,
            "scheduler_min_lr": scheduler_min_lr,
            "lr_warmup_iters": lr_warmup_iters,
            "lr_decay_iters": lr_decay_iters,
        },
        "splits": {
            name: {"shards": summary.shards, "rows": summary.rows, "path": summary.path}
            for name, summary in splits.items()
        },
        "packed_metadata": metadata,
        "env": {
            "venv": str(args.venv) if args.venv else None,
        },
        "outputs": {
            "manifest": str(manifest_path),
            "run_script": str(run_script_path),
            "report": str(report_path),
        },
    }
    return manifest


def write_plan(manifest: Mapping[str, Any], *, overwrite: bool) -> None:
    manifest_path = Path(str(manifest["outputs"]["manifest"]))
    run_script_path = Path(str(manifest["outputs"]["run_script"]))
    report_path = Path(str(manifest["outputs"]["report"]))
    existing = [path for path in (manifest_path, run_script_path, report_path) if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"plan outputs already exist; pass --overwrite to replace them:\n{formatted}")
    write_json(manifest_path, manifest)
    write_run_script(run_script_path, render_run_script(manifest))
    write_report(report_path, manifest)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packed-sft-dir", type=Path, default=DEFAULT_PACKED_SFT_DIR)
    parser.add_argument("--pretrained-checkpoint", type=Path, default=None)
    parser.add_argument("--tokenizer-model", default=None)
    parser.add_argument("--save-dir", type=Path, default=DEFAULT_SAVE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--repo-dir", type=Path, default=DEFAULT_REPO_DIR)
    parser.add_argument("--script-path", type=Path, default=DEFAULT_SCRIPT_PATH)
    parser.add_argument("--config-path", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--venv", type=Path, default=None)
    parser.add_argument("--nodes", type=int, default=1)
    parser.add_argument("--gpus-per-node", type=int, default=8)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--train-iters", type=int, default=None)
    parser.add_argument("--fallback-train-iters", type=int, default=1700)
    parser.add_argument("--global-batch-size", type=int, default=8)
    parser.add_argument("--micro-batch-size", type=int, default=1)
    parser.add_argument("--seq-length", type=int, default=4096)
    parser.add_argument("--eval-interval", type=int, default=100)
    parser.add_argument("--save-interval", type=int, default=20)
    parser.add_argument("--optimizer-lr", type=float, default=None)
    parser.add_argument("--scheduler-min-lr", type=float, default=None)
    parser.add_argument("--lr-warmup-iters", type=int, default=None)
    parser.add_argument("--lr-decay-iters", type=int, default=None)
    parser.add_argument("--allow-missing-checkpoint", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = build_plan(args)
        write_plan(manifest, overwrite=args.overwrite)
    except Exception as exc:  # noqa: BLE001 - CLI should render concise failures.
        print(f"plan_m1_agentic_sft_training.py: error: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "run_name": manifest["run_name"],
                "train_iters": manifest["training"]["train_iters"],
                "train_shards": manifest["splits"]["train"]["shards"],
                "train_rows": manifest["splits"]["train"]["rows"],
                "manifest": manifest["outputs"]["manifest"],
                "run_script": manifest["outputs"]["run_script"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
