#!/usr/bin/env python3
"""Build task335 no-training Qwen3-30B launch preflight evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TASK_ID = "task335_qwen_all_sft_task333_30b_launch_preflight_s1"
OUTPUT_BASE = Path("/work-agents/intern_nemotron_worker_2/outputs") / TASK_ID
CURRENT_MAIN = "76b9ebf98e623cb85075378ca9980ba6ee11c8ed"
LEAD_DOCS = "5c55be6227a01897adfec12231931ebe2eed7dbc"
MODEL_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507")
TASK333_RUN_ROOT = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z"
)
TASK333_PACKED_ROOT = TASK333_RUN_ROOT / "packed_qwen_combined_contract"
TASK333_SPLITS_ROOT = TASK333_PACKED_ROOT / "splits"
REMOTE_HOST = "NemTron"
REMOTE_TASK_BASE = Path(f"/root/{TASK_ID}")
QWEN_ENTRYPOINT = "src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py"
BASE_CONFIG = "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_logged(cmd: str, *, log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"$ {cmd}\n")
        log.flush()
        proc = subprocess.run(
            cmd,
            cwd=Path.cwd(),
            shell=True,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
            executable="/bin/bash",
        )
    return int(proc.returncode)


def copy_or_link(src: Path, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_resolved = src.resolve(strict=True)
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(dest)
    try:
        os.link(src_resolved, dest)
        return "hardlink"
    except OSError:
        shutil.copy2(src_resolved, dest)
        return "copy"


def local_train_metrics() -> dict[str, Any]:
    manifest = load_json(TASK333_RUN_ROOT / "manifest.json")
    return manifest["metrics"]["by_split"]["train"]


def build_train_only_view(run_root: Path, *, remote_data_root: Path) -> dict[str, Any]:
    """Create local and remote-staged train-only packed roots.

    The full task333 root intentionally exposes valid/test. The later launch
    route uses a task-owned train-only root so the checked-in training data
    builder sees no valid parquet directory and sets do_validation=False.
    """
    full_blend = load_json(TASK333_PACKED_ROOT / "blend.json")
    full_metadata = load_json(TASK333_SPLITS_ROOT / "metadata.json")
    metrics = local_train_metrics()

    local_root = run_root / "packed_qwen_task333_train_only_contract"
    local_splits = local_root / "splits"
    local_train = local_splits / "train"
    remote_stage_root = run_root / "remote_stage" / "packed_qwen_task333_train_only_contract"
    remote_stage_splits = remote_stage_root / "splits"
    remote_stage_train = remote_stage_splits / "train"

    train_entries: list[dict[str, Any]] = []
    train_blend: list[str] = []
    materialization_counts: dict[str, int] = {"hardlink": 0, "copy": 0}

    source_train = TASK333_SPLITS_ROOT / "train"
    for index, src_link in enumerate(sorted(source_train.glob("*.parquet"))):
        local_dest = local_train / src_link.name
        method = copy_or_link(src_link, local_dest)
        materialization_counts[method] += 1

        remote_stage_dest = remote_stage_train / src_link.name
        method_remote_stage = copy_or_link(local_dest, remote_stage_dest)
        materialization_counts[method_remote_stage] += 1

        local_without_suffix = str(local_dest.with_suffix(""))
        remote_without_suffix = str((remote_data_root / "splits" / "train" / src_link.name).with_suffix(""))
        train_blend.extend(["1.0", local_without_suffix])
        train_entries.append(
            {
                "index": index,
                "name": src_link.name,
                "source_link": str(src_link),
                "source_target": os.readlink(src_link) if src_link.is_symlink() else str(src_link),
                "local_path": str(local_dest),
                "remote_path": str(remote_data_root / "splits" / "train" / src_link.name),
                "local_sha256": sha256_file(local_dest),
                "bytes": local_dest.stat().st_size,
                "remote_blend_without_suffix": remote_without_suffix,
            }
        )

    local_blend = {"train": train_blend, "valid": [], "test": []}
    write_json(local_root / "blend.json", local_blend)

    remote_blend_values: list[str] = []
    for entry in train_entries:
        remote_blend_values.extend(["1.0", entry["remote_blend_without_suffix"]])
    remote_blend = {"train": remote_blend_values, "valid": [], "test": []}
    write_json(remote_stage_root / "blend.json", remote_blend)

    def patched_metadata(*, root: Path, blend_path: Path, remote: bool) -> dict[str, Any]:
        data = json.loads(json.dumps(full_metadata))
        data["blend_path"] = str(blend_path)
        data["path"] = str(root / "splits")
        data["num_shards"] = len(train_entries)
        data["total_sequences"] = metrics["rows"]
        data["total_tokens"] = metrics["input_tokens"]
        data["training_path"] = str(root / "splits" / "train")
        data["validation_path"] = None
        data["test_path"] = None
        data["producer"] = "task335_train_only_launch_preflight"
        data["task335_train_only_view"] = {
            "source_packed_root": str(TASK333_PACKED_ROOT),
            "remote_view": remote,
            "validation_route": "valid/test omitted to force do_validation=False",
        }
        nested = data.setdefault("metadata", {})
        if isinstance(nested, dict):
            nested["blend_path"] = str(blend_path)
            nested["num_shards"] = len(train_entries)
            nested["total_sequences"] = metrics["rows"]
            nested["total_tokens"] = metrics["input_tokens"]
        return data

    local_metadata = patched_metadata(root=local_root, blend_path=local_root / "blend.json", remote=False)
    remote_metadata = patched_metadata(root=remote_data_root, blend_path=remote_data_root / "blend.json", remote=True)
    write_json(local_splits / "metadata.json", local_metadata)
    write_json(remote_stage_splits / "metadata.json", remote_metadata)

    write_json(
        local_splits / "manifest.json",
        {
            "source_packed_root": str(TASK333_PACKED_ROOT),
            "train_only_root": str(local_root),
            "remote_data_root": str(remote_data_root),
            "splits": {
                "train": {"entries": train_entries, "count": len(train_entries)},
                "valid": {"entries": [], "count": 0},
                "test": {"entries": [], "count": 0},
            },
        },
    )
    write_json(
        run_root / "manifests/train_only_view_manifest.json",
        {
            "local_root": str(local_root),
            "remote_stage_root": str(remote_stage_root),
            "remote_data_root": str(remote_data_root),
            "source_full_root": str(TASK333_PACKED_ROOT),
            "materialization_counts": materialization_counts,
            "train_shards": len(train_entries),
            "valid_shards": 0,
            "test_shards": 0,
            "train_metrics": metrics,
            "entries": train_entries,
        },
    )

    checksum_lines = [
        f"{entry['local_sha256']}  {Path(entry['local_path']).relative_to(run_root)}"
        for entry in train_entries
    ]
    (run_root / "manifests/train_only_shard_checksums.sha256").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
    )
    return {
        "local_root": local_root,
        "local_splits": local_splits,
        "remote_stage_root": remote_stage_root,
        "remote_data_root": remote_data_root,
        "train_entries": train_entries,
        "train_metrics": metrics,
    }


def write_launch_contract(run_root: Path, *, remote_root: Path, remote_repo: Path, remote_data_root: Path) -> dict[str, Any]:
    future_run_root = REMOTE_TASK_BASE / "future_lead_gated_training_run"
    contract = {
        "disposition": "NO_TRAINING_PREFLIGHT_CONTRACT",
        "model_path": str(MODEL_PATH),
        "tokenizer_model": str(MODEL_PATH),
        "packed_train_only_root": str(remote_data_root),
        "packed_train_splits": str(remote_data_root / "splits"),
        "validation_disposition": "disabled_by_train_only_view_no_valid_parquet_do_validation_false",
        "entrypoint": QWEN_ENTRYPOINT,
        "base_config": BASE_CONFIG,
        "launcher": "torchrun --standalone --nnodes=1 --nproc_per_node=8",
        "host": "NemTron",
        "gpu_contract": {
            "required_gpus": 8,
            "observed_gpu_type": "NVIDIA H200",
            "cuda_visible_devices": "0,1,2,3,4,5,6,7",
        },
        "parallelism": {
            "tensor_model_parallel_size": 4,
            "pipeline_model_parallel_size": 2,
            "context_parallel_size": 1,
            "data_parallel_size": 1,
            "expert_model_parallel_size": 4,
            "expert_tensor_parallel_size": 1,
            "sequence_parallel": True,
        },
        "batch_sequence_precision": {
            "seq_length": 4096,
            "global_batch_size": 8,
            "micro_batch_size": 1,
            "precision": "recipe/container default bf16 mixed precision",
        },
        "lead_required_placeholders": {
            "TASK335_TRAIN_ITERS": "required positive integer set by later lead-gated training task",
            "TASK335_LR": "required positive learning rate set by later lead-gated training task",
            "TASK335_MIN_LR": "required non-negative min lr; suggested 1e-7 if lead does not change",
            "TASK335_LR_WARMUP_ITERS": "required warmup iters; suggested 4 if lead does not change",
            "TASK335_SAVE_INTERVAL": "required checkpoint interval; suggested 5 if lead does not change",
        },
        "checkpoint_policy": {
            "save_root": str(future_run_root / "checkpoints"),
            "pretrained_checkpoint": "requires later lead-approved imported Bridge checkpoint path",
            "finetune": True,
            "save_interval": "$TASK335_SAVE_INTERVAL",
            "inventory_required": True,
            "checksum_required": True,
        },
        "timeout_policy": {
            "training_wrapper_timeout_sec": 0,
            "no_log_progress_timeout_sec": 900,
            "post_train_validation_timeout_sec": 0,
            "reason": "validation route is disabled; any validation entry is a fail-closed condition",
        },
        "rc_policy": {
            "pass": "wrapper rc=0 with finite-loss logs, no validation phase, checkpoint inventory/checksums",
            "block": "any nonzero rc, any validation phase entry, missing checkpoint, non-finite loss, or shared mutation",
            "salvage": "not allowed without explicit lead clearance",
        },
        "teardown_policy": {
            "normal": "collect process/GPU snapshots after rc=0",
            "hung": "do not signal without explicit lead clearance; report exact process/GPU/log state",
        },
        "same_harness_eval_handoff": "no eval in task335; any checkpoint needs later independent review and same-harness eval assignment",
        "boundaries": {
            "training": "not authorized in task335",
            "optimizer_steps": "not authorized in task335",
            "eval": "not authorized in task335",
            "export": "not authorized in task335",
            "endpoint": "not authorized in task335",
            "promotion": "not authorized in task335",
            "task310_release": "not claimed",
            "task255_reuse": "not used",
            "aime2025_train_rows": 0,
            "shared_deletion_or_mutation": "not performed",
        },
    }
    write_json(run_root / "manifests/later_launch_contract.json", contract)

    script = f"""#!/usr/bin/env bash
set -euo pipefail

# Task335 no-training preflight artifact only. Do not run this script until a
# later lead-gated training task explicitly releases it.
: "${{TASK335_TRAIN_ITERS:?lead-approved train iters required}}"
: "${{TASK335_LR:?lead-approved lr required}}"
: "${{TASK335_MIN_LR:?lead-approved min lr required}}"
: "${{TASK335_LR_WARMUP_ITERS:?lead-approved warmup iters required}}"
: "${{TASK335_SAVE_INTERVAL:?lead-approved save interval required}}"
: "${{SUPER3_M1_PRETRAINED_CHECKPOINT:?lead-approved Bridge checkpoint path required}}"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTHONPATH={remote_repo}/src
export WANDB_MODE=offline
export WANDB_DISABLED=true
export TOKENIZERS_PARALLELISM=false
export SUPER3_M1_QWEN_HF_MODEL={MODEL_PATH}
export SUPER3_M1_TOKENIZER_MODEL={MODEL_PATH}
export SUPER3_M1_TRAINING_PROFILE=qwen
export SUPER3_M1_AGENTIC_PACKED_DIR={remote_data_root}/splits
export SUPER3_M1_SFT_SAVE={future_run_root}/checkpoints

cd {remote_repo}
torchrun --standalone --nnodes=1 --nproc_per_node=8 \\
  {QWEN_ENTRYPOINT} \\
  --config {BASE_CONFIG} \\
  dataset.super3_packed_sft_dir={remote_data_root}/splits \\
  train.train_iters=${{TASK335_TRAIN_ITERS}} \\
  train.global_batch_size=8 \\
  train.micro_batch_size=1 \\
  train.eval_interval=100000000 \\
  optimizer.lr=${{TASK335_LR}} \\
  optimizer.min_lr=${{TASK335_MIN_LR}} \\
  scheduler.lr_warmup_iters=${{TASK335_LR_WARMUP_ITERS}} \\
  scheduler.lr_decay_iters=${{TASK335_TRAIN_ITERS}} \\
  checkpoint.save_interval=${{TASK335_SAVE_INTERVAL}} \\
  checkpoint.save={future_run_root}/checkpoints \\
  checkpoint.pretrained_checkpoint=${{SUPER3_M1_PRETRAINED_CHECKPOINT}} \\
  logger.log_interval=1 \\
  convert_to_hf.enabled=false
"""
    path = run_root / "config/run_later_training_TEMPLATE_DO_NOT_RUN.sh"
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return contract


def write_remote_probe_script(run_root: Path, *, remote_root: Path, remote_repo: Path, remote_data_root: Path) -> Path:
    script_path = run_root / "config/remote_no_training_preflight_probe.py"
    script = f"""#!/usr/bin/env python3
from __future__ import annotations

import importlib
import inspect
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

repo = Path({str(remote_repo)!r})
remote_root = Path({str(remote_root)!r})
model = Path({str(MODEL_PATH)!r})
packed_root = Path({str(remote_data_root)!r})
splits = packed_root / "splits"
sys.path.insert(0, str(repo / "src"))

result = {{
    "host": socket.gethostname(),
    "cwd": str(Path.cwd()),
    "repo": str(repo),
    "model_path": str(model),
    "packed_root": str(packed_root),
    "splits": str(splits),
    "checks": {{}},
    "boundaries": {{
        "training": "not run",
        "optimizer_steps": "not run",
        "eval": "not run",
        "export": "not run",
        "endpoint": "not run",
    }},
}}

def record(name, status, **extra):
    result["checks"][name] = {{"status": status, **extra}}

mods = [
    "omegaconf",
    "torch",
    "megatron",
    "megatron.bridge",
    "megatron.bridge.training.config",
    "nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train",
    "nemotron.recipes.super3.stage1_sft.qwen_chat_contract",
]
import_results = {{}}
for mod in mods:
    try:
        importlib.import_module(mod)
    except Exception as exc:
        import_results[mod] = {{"status": "FAIL", "error": repr(exc)}}
    else:
        import_results[mod] = {{"status": "PASS"}}

try:
    importlib.import_module("megatron.bridge.recipes.qwen.qwen3_moe")
except Exception as exc:
    import_results["megatron.bridge.recipes.qwen.qwen3_moe"] = {{"status": "FAIL", "error": repr(exc)}}
else:
    import_results["megatron.bridge.recipes.qwen.qwen3_moe"] = {{"status": "PASS"}}

required_imports_pass = all(value["status"] == "PASS" for value in import_results.values())
record(
    "runtime_imports",
    "PASS" if required_imports_pass else "BLOCK",
    modules=import_results,
)

if not model.is_dir():
    raise FileNotFoundError(model)
required_model_files = ["config.json", "tokenizer_config.json"]
missing_model_files = [name for name in required_model_files if not (model / name).is_file()]
if missing_model_files:
    raise FileNotFoundError(missing_model_files)
tokenizer_config = json.loads((model / "tokenizer_config.json").read_text())
model_config = json.loads((model / "config.json").read_text())
record(
    "model_path",
    "PASS",
    architecture=model_config.get("architectures"),
    model_type=model_config.get("model_type"),
    tokenizer_chat_template_present=bool(tokenizer_config.get("chat_template")),
)

if not splits.is_dir():
    raise FileNotFoundError(splits)
train_count = len(list((splits / "train").glob("*.parquet"))) if (splits / "train").is_dir() else 0
valid_count = len(list((splits / "valid").glob("*.parquet"))) if (splits / "valid").is_dir() else 0
test_count = len(list((splits / "test").glob("*.parquet"))) if (splits / "test").is_dir() else 0
if train_count <= 0:
    raise RuntimeError("train-only view has no train parquet shards")
record("remote_train_only_view", "PASS", train_shards=train_count, valid_shards=valid_count, test_shards=test_count)

from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import (
    validate_qwen_packed_sft_chat_contract,
    validate_qwen_training_pipeline_contract,
)

metadata_path = validate_qwen_packed_sft_chat_contract(splits, tokenizer_model=str(model))
pipeline_metadata_path = validate_qwen_training_pipeline_contract(
    splits,
    tokenizer_model=str(model),
    training_profile="qwen",
    model_ref=str(model),
    train_entrypoint="{QWEN_ENTRYPOINT}",
)
record(
    "qwen_contract",
    "PASS",
    metadata_path=str(metadata_path),
    pipeline_metadata_path=str(pipeline_metadata_path),
)

train_source_path = repo / "src/nemotron/recipes/super3/stage1_sft/train.py"
source = train_source_path.read_text(encoding="utf-8")
has_validation = valid_count > 0
route_pass = (
    not has_validation
    and "has_validation_data = False" in source
    and "do_validation=has_validation_data" in source
)
if not route_pass:
    raise RuntimeError("validation route did not prove do_validation=False")
record(
    "validation_route_fail_closed",
    "PASS",
    valid_parquet_count=valid_count,
    do_validation_expected=False,
    train_source_path=str(train_source_path),
    source_contains_false_assignment="has_validation_data = False" in source,
    source_returns_do_validation="do_validation=has_validation_data" in source,
)

gpu_cmd = [
    "nvidia-smi",
    "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
    "--format=csv,noheader,nounits",
]
gpu_proc = subprocess.run(gpu_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
gpu_lines = [line.strip() for line in gpu_proc.stdout.splitlines() if line.strip()]
record("gpu_resource_probe", "PASS" if gpu_proc.returncode == 0 and len(gpu_lines) >= 8 else "BLOCK", rc=gpu_proc.returncode, lines=gpu_lines)

if not required_imports_pass:
    result["disposition"] = "BLOCK_RUNTIME_MISSING_IMPORT"
    result["blocker"] = import_results
else:
    result["disposition"] = "PASS_NO_TRAINING_PREFLIGHT"

out = remote_root / "manifests" / "remote_no_training_preflight_probe.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n")
print(json.dumps(result, indent=2, sort_keys=True))
print("TASK335_REMOTE_PREFLIGHT=" + ("PASS" if required_imports_pass else "BLOCK"))
if not required_imports_pass:
    raise SystemExit(2)
"""
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o755)
    return script_path


def write_local_probes(run_root: Path, train_only: dict[str, Any]) -> None:
    model_config = load_json(MODEL_PATH / "config.json")
    tokenizer_config = load_json(MODEL_PATH / "tokenizer_config.json")
    manifest = load_json(TASK333_RUN_ROOT / "manifest.json")
    split_manifest = load_json(TASK333_SPLITS_ROOT / "manifest.json")
    full_split_counts = {
        split: len(list((TASK333_SPLITS_ROOT / split).glob("*.parquet")))
        for split in ("train", "valid", "test")
    }
    write_json(
        run_root / "manifests/local_model_and_data_probe.json",
        {
            "model_path": str(MODEL_PATH),
            "model_path_exists": MODEL_PATH.is_dir(),
            "model_architectures": model_config.get("architectures"),
            "model_type": model_config.get("model_type"),
            "tokenizer_chat_template_present": bool(tokenizer_config.get("chat_template")),
            "tokenizer_trust_remote_code": False,
            "task333_run_root": str(TASK333_RUN_ROOT),
            "task333_packed_root": str(TASK333_PACKED_ROOT),
            "task333_packed_root_exists_local": TASK333_PACKED_ROOT.is_dir(),
            "task333_full_split_counts": full_split_counts,
            "task333_contract_validation_pass": manifest["checks"]["contract_validation_pass"],
            "task333_artifact_sha256sum_rc": manifest["checks"]["artifact_sha256sum_check"]["rc"],
            "task333_packed_shard_sha256sum_rc": manifest["checks"]["packed_shard_sha256sum_check"]["rc"],
            "task333_metrics_total": manifest["metrics"]["total"],
            "task333_train_metrics": manifest["metrics"]["by_split"]["train"],
            "task333_split_manifest_keys": sorted(split_manifest["splits"].keys()),
            "train_only_local_root": str(train_only["local_root"]),
            "train_only_remote_root": str(train_only["remote_data_root"]),
        },
    )


def write_checksums(run_root: Path) -> str:
    candidates: list[Path] = []
    for rel in ("manifests", "logs", "config"):
        candidates.extend(sorted((run_root / rel).glob("*")))
    candidates.extend(
        [
            run_root / "packed_qwen_task333_train_only_contract/blend.json",
            run_root / "packed_qwen_task333_train_only_contract/splits/metadata.json",
            run_root / "packed_qwen_task333_train_only_contract/splits/manifest.json",
        ]
    )
    checksum_path = run_root / "manifests/artifact_checksums.sha256"
    excluded = {checksum_path, run_root / "manifests/final_summary.json"}
    lines = []
    seen: set[Path] = set()
    for path in candidates:
        if path in excluded or path in seen or not path.is_file():
            continue
        seen.add(path)
        lines.append(f"{sha256_file(path)}  {path.relative_to(run_root)}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sha256_file(checksum_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = args.run_root or (OUTPUT_BASE / f"run_{utc_stamp()}")
    run_root.mkdir(parents=True, exist_ok=True)
    for rel in ("logs", "manifests", "config"):
        (run_root / rel).mkdir(exist_ok=True)

    remote_root = REMOTE_TASK_BASE / run_root.name
    remote_repo = remote_root / "Nemotron"
    remote_data_root = remote_root / "input/packed_qwen_task333_train_only_contract"

    train_only = build_train_only_view(run_root, remote_data_root=remote_data_root)
    write_local_probes(run_root, train_only)
    launch_contract = write_launch_contract(
        run_root,
        remote_root=remote_root,
        remote_repo=remote_repo,
        remote_data_root=remote_data_root,
    )
    remote_probe_script = write_remote_probe_script(
        run_root,
        remote_root=remote_root,
        remote_repo=remote_repo,
        remote_data_root=remote_data_root,
    )

    sync_repo_cmd = (
        f"ssh {REMOTE_HOST} 'mkdir -p {remote_repo}' && "
        f"git archive --format=tar {CURRENT_MAIN} | "
        f"ssh {REMOTE_HOST} 'tar -xf - -C {remote_repo} && "
        f"printf {CURRENT_MAIN!r} > {remote_root}/synced_head.txt'"
    )
    sync_repo_rc = run_logged(sync_repo_cmd, log_path=run_root / "logs/remote_repo_sync.log")

    sync_data_cmd = (
        f"ssh {REMOTE_HOST} 'mkdir -p {remote_data_root}' && "
        f"tar -C {train_only['remote_stage_root']} -cf - . | "
        f"ssh {REMOTE_HOST} 'tar -xf - -C {remote_data_root}'"
    )
    sync_data_rc = run_logged(sync_data_cmd, log_path=run_root / "logs/remote_train_only_data_sync.log")

    sync_probe_cmd = (
        f"scp {remote_probe_script} {REMOTE_HOST}:{remote_root}/remote_no_training_preflight_probe.py && "
        f"scp {run_root / 'config/run_later_training_TEMPLATE_DO_NOT_RUN.sh'} "
        f"{REMOTE_HOST}:{remote_root}/run_later_training_TEMPLATE_DO_NOT_RUN.sh && "
        f"scp {run_root / 'manifests/later_launch_contract.json'} "
        f"{REMOTE_HOST}:{remote_root}/later_launch_contract.json"
    )
    sync_probe_rc = run_logged(sync_probe_cmd, log_path=run_root / "logs/remote_probe_artifact_sync.log")

    remote_probe_cmd = (
        f"ssh {REMOTE_HOST} 'cd {remote_repo} && "
        f"PYTHONPATH={remote_repo}/src "
        f"WANDB_MODE=offline WANDB_DISABLED=true TOKENIZERS_PARALLELISM=false "
        f"SUPER3_M1_QWEN_HF_MODEL={MODEL_PATH} "
        f"SUPER3_M1_TOKENIZER_MODEL={MODEL_PATH} "
        f"SUPER3_M1_TRAINING_PROFILE=qwen "
        f"SUPER3_M1_AGENTIC_PACKED_DIR={remote_data_root}/splits "
        f"python {remote_root}/remote_no_training_preflight_probe.py'"
    )
    remote_probe_rc = run_logged(remote_probe_cmd, log_path=run_root / "logs/remote_no_training_preflight_probe.log")

    fetch_remote_manifest_cmd = (
        f"scp {REMOTE_HOST}:{remote_root}/manifests/remote_no_training_preflight_probe.json "
        f"{run_root / 'manifests/remote_no_training_preflight_probe.json'}"
    )
    fetch_remote_manifest_rc = run_logged(
        fetch_remote_manifest_cmd,
        log_path=run_root / "logs/fetch_remote_preflight_manifest.log",
    )

    command_manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "local_host": socket.gethostname(),
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "branch": subprocess.check_output(["git", "branch", "--show-current"], text=True).strip(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "current_main_synced": CURRENT_MAIN,
        "lead_docs": LEAD_DOCS,
        "remote_host": REMOTE_HOST,
        "remote_root": str(remote_root),
        "remote_repo": str(remote_repo),
        "remote_data_root": str(remote_data_root),
        "commands": [
            {"name": "sync_current_main_to_root", "rc": sync_repo_rc, "log": str(run_root / "logs/remote_repo_sync.log")},
            {"name": "sync_train_only_data_to_root", "rc": sync_data_rc, "log": str(run_root / "logs/remote_train_only_data_sync.log")},
            {"name": "sync_remote_probe_artifacts", "rc": sync_probe_rc, "log": str(run_root / "logs/remote_probe_artifact_sync.log")},
            {"name": "remote_no_training_preflight_probe", "rc": remote_probe_rc, "log": str(run_root / "logs/remote_no_training_preflight_probe.log")},
            {"name": "fetch_remote_preflight_manifest", "rc": fetch_remote_manifest_rc, "log": str(run_root / "logs/fetch_remote_preflight_manifest.log")},
        ],
        "env": {
            "PYTHONPATH": f"{remote_repo}/src",
            "SUPER3_M1_QWEN_HF_MODEL": str(MODEL_PATH),
            "SUPER3_M1_TOKENIZER_MODEL": str(MODEL_PATH),
            "SUPER3_M1_TRAINING_PROFILE": "qwen",
            "SUPER3_M1_AGENTIC_PACKED_DIR": f"{remote_data_root}/splits",
            "WANDB_MODE": "offline",
            "WANDB_DISABLED": "true",
            "TOKENIZERS_PARALLELISM": "false",
        },
    }
    write_json(run_root / "manifests/command_env_manifest.json", command_manifest)

    remote_probe = {}
    remote_probe_path = run_root / "manifests/remote_no_training_preflight_probe.json"
    if remote_probe_path.is_file():
        remote_probe = load_json(remote_probe_path)

    required_rcs = [sync_repo_rc, sync_data_rc, sync_probe_rc, remote_probe_rc, fetch_remote_manifest_rc]
    remote_checks = remote_probe.get("checks", {})
    remote_pass = all(
        remote_checks.get(name, {}).get("status") == "PASS"
        for name in (
            "runtime_imports",
            "model_path",
            "remote_train_only_view",
            "qwen_contract",
            "validation_route_fail_closed",
            "gpu_resource_probe",
        )
    )
    disposition = "PASS_LAUNCH_PREFLIGHT" if all(rc == 0 for rc in required_rcs) and remote_pass else "BLOCK_LAUNCH_PREFLIGHT"
    recommendation = (
        "Later lead-gated training task may use the task-owned remote train-only mirror and launch contract; "
        "task335 itself does not release training."
        if disposition == "PASS_LAUNCH_PREFLIGHT"
        else "Do not launch training; use exact rc/log/check failures in this run root."
    )

    artifact_checksums_sha = write_checksums(run_root)
    final = {
        "disposition": disposition,
        "recommendation": recommendation,
        "run_root": str(run_root),
        "remote_root": str(remote_root),
        "remote_repo": str(remote_repo),
        "remote_data_root": str(remote_data_root),
        "current_main_synced": CURRENT_MAIN,
        "model_path": str(MODEL_PATH),
        "task333_packed_root": str(TASK333_PACKED_ROOT),
        "local_train_only_root": str(train_only["local_root"]),
        "train_only_shards": len(train_only["train_entries"]),
        "train_only_metrics": train_only["train_metrics"],
        "later_launch_contract": str(run_root / "manifests/later_launch_contract.json"),
        "command_env_manifest": str(run_root / "manifests/command_env_manifest.json"),
        "remote_preflight_manifest": str(remote_probe_path),
        "artifact_checksums": str(run_root / "manifests/artifact_checksums.sha256"),
        "artifact_checksums_sha256": artifact_checksums_sha,
        "train_only_shard_checksums": str(run_root / "manifests/train_only_shard_checksums.sha256"),
        "remote_checks": remote_checks,
        "boundaries": launch_contract["boundaries"],
    }
    write_json(run_root / "manifests/final_summary.json", final)
    artifact_checksums_sha = write_checksums(run_root)
    final["artifact_checksums_sha256"] = artifact_checksums_sha
    write_json(run_root / "manifests/final_summary.json", final)
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0 if disposition == "PASS_LAUNCH_PREFLIGHT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
