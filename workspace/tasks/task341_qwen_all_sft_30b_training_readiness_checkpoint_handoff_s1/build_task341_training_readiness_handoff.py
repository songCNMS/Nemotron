#!/usr/bin/env python3
"""Build task341 no-training training-readiness/checkpoint-handoff evidence."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TASK_ID = "task341_qwen_all_sft_30b_training_readiness_checkpoint_handoff_s1"
OUTPUT_BASE = Path("/work-agents/intern_nemotron_worker_2/outputs") / TASK_ID
CURRENT_MAIN = "f16dffdef961b1a6cdb3ae23203f9ae7495b38ab"
LEAD_DOCS = "afbae9028daf7291d07db9a95f8d841b9981825f"
REMOTE_HOST = "NemTron"
MODEL_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507")
TASK337_RUNTIME_TARGET = Path(
    "/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/"
    "run_20260604T095948Z/runtime_site"
)
TASK339_RUN_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z"
)
TASK339_REMOTE_ROOT = Path(
    "/root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z"
)
TASK339_REMOTE_TRAIN_ONLY_ROOT = (
    TASK339_REMOTE_ROOT / "input/packed_qwen_task333_train_only_contract"
)
TASK298_RUN_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z"
)
TASK298_CHECKPOINT_ROOT = Path(
    "/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/"
    "run_20260602T143838Z/qwen3_30b_bridge_import_iter0"
)
QWEN_ENTRYPOINT = "src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py"
BASE_CONFIG = "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rendered_launch_script(remote_root: Path) -> str:
    save_root = remote_root / "future_lead_gated_training_run/checkpoints"
    return f"""#!/usr/bin/env bash
set -euo pipefail

# Task341 rendered handoff only. Do not run until a later lead-gated task
# explicitly authorizes training.
export TASK341_TRAIN_ITERS=2
export TASK341_LR=5e-7
export TASK341_MIN_LR=1e-7
export TASK341_LR_WARMUP_ITERS=0
export TASK341_SAVE_INTERVAL=1
export SUPER3_M1_PRETRAINED_CHECKPOINT={TASK298_CHECKPOINT_ROOT}

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTHONPATH={TASK337_RUNTIME_TARGET}:{remote_root}/Nemotron/src
export WANDB_MODE=offline
export WANDB_DISABLED=true
export TOKENIZERS_PARALLELISM=false
export SUPER3_M1_QWEN_HF_MODEL={MODEL_PATH}
export SUPER3_M1_TOKENIZER_MODEL={MODEL_PATH}
export SUPER3_M1_TRAINING_PROFILE=qwen
export SUPER3_M1_AGENTIC_PACKED_DIR={TASK339_REMOTE_TRAIN_ONLY_ROOT}/splits
export SUPER3_M1_SFT_SAVE={save_root}

cd {remote_root}/Nemotron
torchrun --standalone --nnodes=1 --nproc_per_node=8 \\
  {QWEN_ENTRYPOINT} \\
  --config {BASE_CONFIG} \\
  dataset.super3_packed_sft_dir={TASK339_REMOTE_TRAIN_ONLY_ROOT}/splits \\
  train.train_iters=${{TASK341_TRAIN_ITERS}} \\
  train.global_batch_size=8 \\
  train.micro_batch_size=1 \\
  train.eval_interval=100000000 \\
  optimizer.lr=${{TASK341_LR}} \\
  optimizer.min_lr=${{TASK341_MIN_LR}} \\
  scheduler.lr_warmup_iters=${{TASK341_LR_WARMUP_ITERS}} \\
  scheduler.lr_decay_iters=${{TASK341_TRAIN_ITERS}} \\
  checkpoint.save_interval=${{TASK341_SAVE_INTERVAL}} \\
  checkpoint.save={save_root} \\
  checkpoint.pretrained_checkpoint=${{SUPER3_M1_PRETRAINED_CHECKPOINT}} \\
  logger.log_interval=1 \\
  convert_to_hf.enabled=false
"""


def main() -> int:
    run_root = OUTPUT_BASE / f"run_{utc_stamp()}"
    logs = run_root / "logs"
    manifests = run_root / "manifests"
    config = run_root / "config"
    for path in (logs, manifests, config):
        path.mkdir(parents=True, exist_ok=True)

    remote_root = Path(f"/root/{TASK_ID}/{run_root.name}")
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

    task339_artifact_rc = run_logged(
        f"cd {TASK339_RUN_ROOT} && sha256sum -c manifests/artifact_checksums.sha256",
        log_path=logs / "task339_artifact_checksums_check.log",
    )
    task339_shard_rc = run_logged(
        f"cd {TASK339_RUN_ROOT} && sha256sum -c manifests/train_only_shard_checksums.sha256",
        log_path=logs / "task339_train_only_shard_checksums_check.log",
    )
    source_residual_rg_rc = run_logged(
        "rg -n 'nvidia_resiliency_ext|multi_storage_client|multistorageclient' src || true",
        log_path=logs / "current_source_residual_import_rg.log",
    )
    ssh_probe_rc = run_logged(
        "ssh -o ConnectTimeout=10 NemTron "
        "'hostname; date -u +%Y-%m-%dT%H:%M:%SZ; "
        "test -d /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site; "
        "test -d /root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0; "
        "test -d /root/task339_qwen_all_sft_task337_30b_launch_preflight_rerun_s1/run_20260604T112611Z/input/packed_qwen_task333_train_only_contract; "
        "python3 - <<\"PY\"\nimport importlib.util\nfor m in [\"nvidia_resiliency_ext\", \"multi_storage_client\", \"multistorageclient\"]:\n    spec = importlib.util.find_spec(m)\n    print(m, \"FOUND\" if spec else \"MISSING\", getattr(spec, \"origin\", None) if spec else \"\")\nPY'",
        log_path=logs / "nemtron_ssh_runtime_checkpoint_probe.log",
    )

    launch_script = rendered_launch_script(remote_root)
    launch_script_path = config / "run_later_training_RENDERED_DO_NOT_RUN.sh"
    write_text(launch_script_path, launch_script)
    launch_script_path.chmod(0o755)

    task339_summary = load_json(TASK339_RUN_ROOT / "manifests/final_summary.json")
    task339_remote = load_json(TASK339_RUN_ROOT / "manifests/remote_no_training_preflight_probe.json")
    latest_iteration = (TASK298_RUN_ROOT / "manifests/bridge_import_30b_latest_iteration.txt").read_text(
        encoding="utf-8"
    ).strip()

    placeholder_manifest = {
        "TASK341_TRAIN_ITERS": 2,
        "TASK341_LR": "5e-7",
        "TASK341_MIN_LR": "1e-7",
        "TASK341_LR_WARMUP_ITERS": 0,
        "TASK341_SAVE_INTERVAL": 1,
        "SUPER3_M1_PRETRAINED_CHECKPOINT": str(TASK298_CHECKPOINT_ROOT),
        "justification": (
            "two-iteration bounded first all-SFT 30B run with checkpoint every "
            "iteration; LR/min LR match accepted prior 30B preflight values and "
            "warmup=0 avoids hiding first-step LR"
        ),
        "status": "CANDIDATE_NOT_RELEASED",
    }
    write_json(manifests / "task341_launch_placeholders.json", placeholder_manifest)

    checkpoint_manifest = {
        "candidate_checkpoint_root": str(TASK298_CHECKPOINT_ROOT),
        "candidate_source": "task298_qwen_aime_v11_30b_runtime_resource_base_load_s1",
        "candidate_latest_iteration": latest_iteration,
        "local_evidence": {
            "bridge_import_log": str(TASK298_RUN_ROOT / "logs/bridge_import_30b_iter0.log"),
            "bridge_import_log_sha256": sha256_file(TASK298_RUN_ROOT / "logs/bridge_import_30b_iter0.log"),
            "inventory": str(TASK298_RUN_ROOT / "manifests/bridge_import_30b_inventory.tsv"),
            "inventory_sha256": sha256_file(TASK298_RUN_ROOT / "manifests/bridge_import_30b_inventory.tsv"),
            "checksum_manifest": str(TASK298_RUN_ROOT / "manifests/bridge_import_30b_checksums.sha256"),
            "checksum_manifest_sha256": sha256_file(
                TASK298_RUN_ROOT / "manifests/bridge_import_30b_checksums.sha256"
            ),
        },
        "live_remote_validation_status": "BLOCKED_NEMTRON_SSH_UNAVAILABLE"
        if ssh_probe_rc != 0
        else "REMOTE_PATH_PROBED",
    }
    write_json(manifests / "checkpoint_handoff_manifest.json", checkpoint_manifest)

    readiness = {
        "task": TASK_ID,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "branch": branch,
        "head": head,
        "current_main": CURRENT_MAIN,
        "lead_docs": LEAD_DOCS,
        "local_host": socket.gethostname(),
        "platform": platform.platform(),
        "run_root": str(run_root),
        "remote_root": str(remote_root),
        "model_path": str(MODEL_PATH),
        "task339_run_root": str(TASK339_RUN_ROOT),
        "task337_runtime_target": str(TASK337_RUNTIME_TARGET),
        "candidate_checkpoint_root": str(TASK298_CHECKPOINT_ROOT),
        "task339_disposition": task339_summary.get("disposition"),
        "task339_remote_disposition": task339_remote.get("disposition"),
        "task339_key_checks": {
            "artifact_checksums_rc": task339_artifact_rc,
            "train_only_shard_checksums_rc": task339_shard_rc,
            "runtime_imports": task339_summary.get("remote_checks", {}).get("runtime_imports", {}),
            "qwen30b_bridge_config_surface": task339_summary.get("remote_checks", {}).get(
                "qwen30b_bridge_config_surface", {}
            ),
            "validation_route_fail_closed": task339_summary.get("remote_checks", {}).get(
                "validation_route_fail_closed", {}
            ),
        },
        "residual_classification": {
            "nvidia_resiliency_ext": {
                "status": "UNRESOLVED_BLOCKED_BY_NEMTRON_SSH"
                if ssh_probe_rc != 0
                else "SEE_REMOTE_PROBE_LOG",
                "static_current_source_import_check_log": str(logs / "current_source_residual_import_rg.log"),
                "note": (
                    "Task339 config import did not need this package, but actual "
                    "training-runtime waiver/remediation cannot be proven while "
                    "NemTron is unreachable."
                ),
            },
            "multi_storage_client": {
                "status": "DIAGNOSTIC_NAME_NONBLOCKING_BY_TASK339_EVIDENCE",
                "note": (
                    "Task339 proved multistorageclient imports from the task337 "
                    "runtime target; current src contains no direct underscore "
                    "module import in this local scan."
                ),
            },
        },
        "placeholder_manifest": str(manifests / "task341_launch_placeholders.json"),
        "rendered_launch_script": str(launch_script_path),
        "policies": {
            "validation": "train-only root has 0 valid/test shards; any validation phase entry is fail-closed",
            "rc": "any nonzero rc, validation phase, missing checkpoint, non-finite loss, or shared mutation blocks",
            "timeout": "retain task339 no-log timeout 900s; post-train validation timeout 0",
            "checkpoint": "inventory and checksums required for any produced checkpoint",
            "teardown": "collect process/GPU snapshots; do not signal hung run without lead clearance",
            "eval_handoff": "no benchmark/AIME/task243 eval in task341 or later training task unless separately assigned",
        },
        "commands": [
            {
                "name": "task339_artifact_checksum_check",
                "rc": task339_artifact_rc,
                "log": str(logs / "task339_artifact_checksums_check.log"),
            },
            {
                "name": "task339_train_only_shard_checksum_check",
                "rc": task339_shard_rc,
                "log": str(logs / "task339_train_only_shard_checksums_check.log"),
            },
            {
                "name": "current_source_residual_import_rg",
                "rc": source_residual_rg_rc,
                "log": str(logs / "current_source_residual_import_rg.log"),
            },
            {
                "name": "nemtron_ssh_runtime_checkpoint_probe",
                "rc": ssh_probe_rc,
                "log": str(logs / "nemtron_ssh_runtime_checkpoint_probe.log"),
            },
        ],
        "boundaries": {
            "optimizer_steps": "not run",
            "training_loop": "not run",
            "benchmark_eval": "not run",
            "aime_task243_eval": "not run",
            "export": "not run",
            "endpoint": "not run",
            "promotion": "not claimed",
            "task255_reuse": "not used",
            "aime2025_train_rows": 0,
            "shared_deletion_or_mutation": "not performed",
            "main_push_merge_self_merge": "not performed",
        },
    }

    if task339_artifact_rc == 0 and task339_shard_rc == 0 and ssh_probe_rc == 0:
        readiness["disposition"] = "PASS_TRAINING_READINESS_HANDOFF"
        readiness["recommendation"] = (
            "Ready for lead/independent review as no-training handoff evidence; "
            "a later lead-gated training task must still authorize optimizer steps."
        )
    else:
        readiness["disposition"] = "BLOCK_TRAINING_READINESS"
        readiness["blocker"] = {
            "type": "NEMTRON_SSH_UNAVAILABLE" if ssh_probe_rc != 0 else "LOCAL_EVIDENCE_CHECK_FAILED",
            "ssh_probe_rc": ssh_probe_rc,
            "reason": (
                "Required task-owned /root sync/probe and live checkpoint/runtime validation "
                "cannot be completed while SSH to NemTron fails."
            )
            if ssh_probe_rc != 0
            else "Local checksum evidence did not validate.",
        }
        readiness["recommendation"] = (
            "Do not assign training. Restore NemTron SSH/runtime access, then rerun "
            "task341 or an equivalent no-training checkpoint-handoff probe."
        )

    write_json(manifests / "training_readiness_summary.json", readiness)

    candidates = []
    for rel in ("logs", "manifests", "config"):
        candidates.extend(sorted((run_root / rel).glob("*")))
    checksum_path = manifests / "artifact_checksums.sha256"
    summary_path = manifests / "training_readiness_summary.json"
    lines = []
    for path in candidates:
        if path in {checksum_path, summary_path} or not path.is_file():
            continue
        lines.append(f"{sha256_file(path)}  {path.relative_to(run_root)}")
    write_text(checksum_path, "\n".join(lines) + "\n")
    readiness["artifact_checksums"] = str(checksum_path)
    readiness["artifact_checksums_sha256"] = sha256_file(checksum_path)
    write_json(summary_path, readiness)

    print(json.dumps(readiness, indent=2, sort_keys=True))
    return 0 if readiness["disposition"] == "PASS_TRAINING_READINESS_HANDOFF" else 2


if __name__ == "__main__":
    raise SystemExit(main())
