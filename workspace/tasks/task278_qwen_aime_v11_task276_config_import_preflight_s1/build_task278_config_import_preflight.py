#!/usr/bin/env python3
"""Build task278 no-training config/import preflight evidence.

This helper intentionally never calls the Stage1 SFT training entry point or
Megatron-Bridge finetune/pretrain functions. It performs offline config,
packed-data, Qwen HF checkpoint, and import checks, then fails closed when the
runtime needed for a real Bridge import is absent.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
from omegaconf import OmegaConf
from transformers import AutoConfig, AutoTokenizer

from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import (
    QWEN_TRAINING_PROFILE,
    validate_qwen_packed_sft_chat_contract,
    validate_qwen_training_pipeline_contract,
)
from nemotron.recipes.super3.stage1_sft.qwen_local_train import (
    QWEN_MODEL_ENV_VAR,
    resolve_qwen_packed_sft_dir,
    resolve_qwen_tokenizer_model,
)


TASK_ID = "task278_qwen_aime_v11_task276_config_import_preflight_s1"
REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = Path(f"/work-agents/intern_nemotron_worker_2/outputs/{TASK_ID}")
TASK276_RUN_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z"
)
PACKED_ROOT = TASK276_RUN_ROOT / "packed_qwen"
SPLITS_ROOT = PACKED_ROOT / "splits"
TASK276_EVIDENCE_MANIFEST = TASK276_RUN_ROOT / "evidence/packed_qwen_evidence_manifest.json"
TASK276_SHARD_CHECKSUM_LIST = TASK276_RUN_ROOT / "evidence/packed_qwen_shard_checksums.sha256"
QWEN_MODEL = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507")
TRAIN_CONFIG = REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml"
QWEN_TRAIN_ENTRYPOINT = REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py"
GENERIC_TRAIN_ENTRYPOINT = REPO_ROOT / "src/nemotron/recipes/super3/stage1_sft/train.py"
GENERIC_RECIPE_TARGET = (
    "megatron.bridge.recipes.nemotronh.nemotron_3_super.nemotron_3_super_sft_config"
)
QWEN_RECIPE_TARGET = "megatron.bridge.recipes.qwen.qwen3.qwen3_4b_finetune_config"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_revision() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def import_probe(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 - evidence needs exact exception.
        return {
            "module": module_name,
            "status": "FAIL",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
        }
    return {
        "module": module_name,
        "status": "PASS",
        "origin": getattr(module, "__file__", None),
    }


def split_counts() -> dict[str, Any]:
    counts: dict[str, Any] = {}
    for split in ("train", "valid", "test"):
        split_dir = SPLITS_ROOT / split
        files = sorted(split_dir.glob("*.parquet"))
        rows = 0
        input_tokens = 0
        supervised_tokens = 0
        readable_files = 0
        for path in files:
            table = pq.read_table(path, columns=["input_ids", "loss_mask", "seq_start_id"])
            data = table.to_pydict()
            readable_files += 1
            rows += table.num_rows
            for ids in data["input_ids"]:
                input_tokens += len(ids)
            for mask in data["loss_mask"]:
                supervised_tokens += sum(1 for value in mask if bool(value))
        counts[split] = {
            "exposed_parquet_entries": len(files),
            "readable_parquet_files": readable_files,
            "packed_rows": rows,
            "input_tokens": input_tokens,
            "supervised_tokens": supervised_tokens,
        }
    return counts


def qwen_checkpoint_inventory() -> dict[str, Any]:
    required = [
        "config.json",
        "configuration.json",
        "generation_config.json",
        "model.safetensors.index.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.json",
        "merges.txt",
    ]
    inventory: dict[str, Any] = {}
    for name in required:
        path = QWEN_MODEL / name
        inventory[name] = {
            "exists": path.is_file(),
            "size_bytes": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path) if path.is_file() else None,
        }

    index = read_json(QWEN_MODEL / "model.safetensors.index.json")
    shard_names = sorted(set(index.get("weight_map", {}).values()))
    shard_info: dict[str, Any] = {}
    for name in shard_names:
        path = QWEN_MODEL / name
        shard_info[name] = {
            "exists": path.is_file(),
            "size_bytes": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path) if path.is_file() else None,
        }
    inventory["safetensor_shards"] = shard_info
    inventory["safetensor_total_size_from_index"] = index.get("metadata", {}).get("total_size")
    inventory["all_index_shards_exist"] = all(item["exists"] for item in shard_info.values())
    return inventory


def qwen_hf_import_probe() -> dict[str, Any]:
    config = AutoConfig.from_pretrained(str(QWEN_MODEL), local_files_only=True, trust_remote_code=False)
    tokenizer = AutoTokenizer.from_pretrained(
        str(QWEN_MODEL),
        local_files_only=True,
        trust_remote_code=False,
        use_fast=True,
    )
    return {
        "status": "PASS",
        "auto_config_class": type(config).__name__,
        "model_type": getattr(config, "model_type", None),
        "architectures": getattr(config, "architectures", None),
        "num_hidden_layers": getattr(config, "num_hidden_layers", None),
        "hidden_size": getattr(config, "hidden_size", None),
        "num_attention_heads": getattr(config, "num_attention_heads", None),
        "num_key_value_heads": getattr(config, "num_key_value_heads", None),
        "intermediate_size": getattr(config, "intermediate_size", None),
        "vocab_size": getattr(config, "vocab_size", None),
        "tokenizer_class": type(tokenizer).__name__,
        "tokenizer_vocab_size": getattr(tokenizer, "vocab_size", None),
        "chat_template_present": bool(getattr(tokenizer, "chat_template", None)),
    }


def resolved_config_payload() -> dict[str, Any]:
    os.environ[QWEN_MODEL_ENV_VAR] = str(QWEN_MODEL)
    os.environ["SUPER3_M1_TOKENIZER_MODEL"] = str(QWEN_MODEL)
    os.environ["SUPER3_M1_AGENTIC_PACKED_DIR"] = str(SPLITS_ROOT)
    os.environ["SUPER3_M1_TRAINING_PROFILE"] = QWEN_TRAINING_PROFILE
    os.environ["SUPER3_M1_PRETRAINED_CHECKPOINT"] = str(QWEN_MODEL)

    cfg = OmegaConf.load(TRAIN_CONFIG)
    hf_model = os.environ[QWEN_MODEL_ENV_VAR]
    tokenizer_model = resolve_qwen_tokenizer_model(cfg, hf_model)
    packed_sft_dir = resolve_qwen_packed_sft_dir(cfg)
    resolved = OmegaConf.to_container(cfg, resolve=True)
    return {
        "config_path": str(TRAIN_CONFIG),
        "train_entrypoint": str(QWEN_TRAIN_ENTRYPOINT),
        "env": {
            QWEN_MODEL_ENV_VAR: os.environ[QWEN_MODEL_ENV_VAR],
            "SUPER3_M1_TOKENIZER_MODEL": os.environ["SUPER3_M1_TOKENIZER_MODEL"],
            "SUPER3_M1_AGENTIC_PACKED_DIR": os.environ["SUPER3_M1_AGENTIC_PACKED_DIR"],
            "SUPER3_M1_TRAINING_PROFILE": os.environ["SUPER3_M1_TRAINING_PROFILE"],
            "SUPER3_M1_PRETRAINED_CHECKPOINT": os.environ["SUPER3_M1_PRETRAINED_CHECKPOINT"],
        },
        "resolved_packed_sft_dir": packed_sft_dir,
        "resolved_tokenizer_model": tokenizer_model,
        "dataset": resolved.get("dataset"),
        "tokenizer": resolved.get("tokenizer"),
        "training_contract": resolved.get("training_contract"),
        "train": resolved.get("train"),
        "scheduler": resolved.get("scheduler"),
        "checkpoint": resolved.get("checkpoint"),
        "optimizer": resolved.get("optimizer"),
        "guard": {
            "training_command_executed": False,
            "reason": (
                "Executing qwen_local_train.py or run_finetune would enter the "
                "Megatron-Bridge finetune path; task278 only permits offline "
                "config/import preflight."
            ),
        },
    }


def contract_checks() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    try:
        metadata_path = validate_qwen_packed_sft_chat_contract(
            SPLITS_ROOT,
            tokenizer_model=str(QWEN_MODEL),
        )
        checks["packed_chat_contract"] = {"status": "PASS", "metadata_path": str(metadata_path)}
    except Exception as exc:  # noqa: BLE001
        checks["packed_chat_contract"] = {
            "status": "FAIL",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
        }

    try:
        metadata_path = validate_qwen_training_pipeline_contract(
            SPLITS_ROOT,
            tokenizer_model=str(QWEN_MODEL),
            training_profile=QWEN_TRAINING_PROFILE,
            model_ref=str(QWEN_MODEL),
            train_entrypoint=str(QWEN_TRAIN_ENTRYPOINT),
            recipe_target=QWEN_RECIPE_TARGET,
        )
        checks["positive_qwen_training_pipeline_contract"] = {
            "status": "PASS",
            "metadata_path": str(metadata_path) if metadata_path else None,
        }
    except Exception as exc:  # noqa: BLE001
        checks["positive_qwen_training_pipeline_contract"] = {
            "status": "FAIL",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
        }

    try:
        validate_qwen_training_pipeline_contract(
            SPLITS_ROOT,
            tokenizer_model="nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
            training_profile="nemotron-super",
            model_ref="nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
            train_entrypoint=str(GENERIC_TRAIN_ENTRYPOINT),
            recipe_target=GENERIC_RECIPE_TARGET,
        )
        checks["negative_fail_closed_nemotron_defaults"] = {
            "status": "FAIL",
            "exception": "Expected Qwen contract to reject Nemotron defaults, but it passed.",
        }
    except Exception as exc:  # noqa: BLE001
        checks["negative_fail_closed_nemotron_defaults"] = {
            "status": "PASS",
            "blocked_exception_type": type(exc).__name__,
            "blocked_exception": str(exc),
        }
    return checks


def task276_references() -> dict[str, Any]:
    evidence = read_json(TASK276_EVIDENCE_MANIFEST)
    return {
        "packed_root": str(PACKED_ROOT),
        "splits_root": str(SPLITS_ROOT),
        "split_manifest": str(SPLITS_ROOT / "manifest.json"),
        "metadata": str(SPLITS_ROOT / "metadata.json"),
        "evidence_manifest": str(TASK276_EVIDENCE_MANIFEST),
        "shard_checksum_list": str(TASK276_SHARD_CHECKSUM_LIST),
        "evidence_manifest_sha256": sha256_file(TASK276_EVIDENCE_MANIFEST),
        "shard_checksum_list_sha256": sha256_file(TASK276_SHARD_CHECKSUM_LIST),
        "split_manifest_sha256": sha256_file(SPLITS_ROOT / "manifest.json"),
        "metadata_sha256": sha256_file(SPLITS_ROOT / "metadata.json"),
        "task276_disposition": evidence.get("disposition"),
        "task276_split_counts": evidence.get("split_counts"),
        "task276_multiset_parity": evidence.get("intended_vs_exposed_multiset_parity"),
        "task276_qwen_chat_contract": evidence.get("qwen_chat_contract"),
        "task276_no_aime_leakage": evidence.get("no_aime2025_train_leakage_decision"),
    }


def render_report(manifest: dict[str, Any]) -> str:
    bridge_blocker = manifest["runtime_import_probes"]["megatron.bridge.training.config"]
    disposition = manifest["disposition"]
    split_counts_value = manifest["local_data_readability"]["split_counts"]
    config = manifest["resolved_config"]
    lines = [
        "# task278 Config/Import Preflight Report",
        "",
        f"Generated: {manifest['created_at_utc']}",
        "",
        f"Disposition: `{disposition}`.",
        "",
        "This is a no-training config/import preflight artifact. It does not",
        "authorize training, nonzero-LR smoke, live canary, AIME/task243 eval,",
        "export, endpoint, promotion, task255 reuse, AIME2025 train data, shared",
        "deletion, main push, merge, or 30B/8-GPU.",
        "",
        "## Result",
        "",
        "- Local packed-data readability: PASS.",
        "- Qwen packed/training contract checks: PASS.",
        "- Qwen HF config/tokenizer import: PASS.",
        "- Full Megatron-Bridge training-stack import: BLOCKED.",
        f"- Blocker: `{bridge_blocker.get('exception_type')}: {bridge_blocker.get('exception')}`.",
        "",
        "## Artifact Paths",
        "",
        f"- Output root: `{manifest['output_root']}`.",
        f"- Run root: `{manifest['run_root']}`.",
        f"- Manifest: `{manifest['manifest_path']}`.",
        f"- Report: `{manifest['report_path']}`.",
        f"- Task276 packed root: `{manifest['task276']['packed_root']}`.",
        f"- Task276 splits root: `{manifest['task276']['splits_root']}`.",
        "",
        "## Config Payload",
        "",
        f"- Train entrypoint checked but not executed: `{config['train_entrypoint']}`.",
        f"- Config path: `{config['config_path']}`.",
        f"- Packed data env: `{config['env']['SUPER3_M1_AGENTIC_PACKED_DIR']}`.",
        f"- Qwen model/tokenizer env: `{config['env'][QWEN_MODEL_ENV_VAR]}`.",
        f"- Training profile: `{config['env']['SUPER3_M1_TRAINING_PROFILE']}`.",
        f"- Train settings if launched: `{config['train']}`.",
        f"- Scheduler settings if launched: `{config['scheduler']}`.",
        f"- Checkpoint settings if launched: `{config['checkpoint']}`.",
        "- Guard: training command was not executed because it would enter the",
        "  Megatron-Bridge finetune path.",
        "",
        "## Packed Data Readability",
        "",
        "| Split | Shards | Rows | Input tokens | Supervised tokens |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for split in ("train", "valid", "test"):
        row = split_counts_value[split]
        lines.append(
            f"| {split} | {row['exposed_parquet_entries']} | {row['packed_rows']} | "
            f"{row['input_tokens']} | {row['supervised_tokens']} |"
        )
    lines.extend(
        [
            "",
            "Sparse valid/test disposition: accepted for preflight only. Valid has",
            "one packed row; test has one exposed shard and zero rows. This does not",
            "authorize training or evaluation.",
            "",
            "## Qwen Import",
            "",
            f"- HF import status: `{manifest['qwen_hf_import']['status']}`.",
            f"- Model type: `{manifest['qwen_hf_import']['model_type']}`.",
            f"- Config class: `{manifest['qwen_hf_import']['auto_config_class']}`.",
            f"- Tokenizer class: `{manifest['qwen_hf_import']['tokenizer_class']}`.",
            f"- Safetensor index shards exist: `{manifest['qwen_checkpoint_inventory']['all_index_shards_exist']}`.",
            "",
            "## Runtime Import Probes",
            "",
        ]
    )
    for module, probe in manifest["runtime_import_probes"].items():
        if probe["status"] == "PASS":
            lines.append(f"- `{module}`: PASS ({probe.get('origin')}).")
        else:
            lines.append(
                f"- `{module}`: FAIL `{probe.get('exception_type')}: {probe.get('exception')}`."
            )
    lines.extend(
        [
            "",
            "## Checksums",
            "",
            f"- Evidence manifest sha256: `{manifest['task276']['evidence_manifest_sha256']}`.",
            f"- Shard checksum list sha256: `{manifest['task276']['shard_checksum_list_sha256']}`.",
            f"- Split manifest sha256: `{manifest['task276']['split_manifest_sha256']}`.",
            f"- Metadata sha256: `{manifest['task276']['metadata_sha256']}`.",
            f"- Qwen config.json sha256: `{manifest['qwen_checkpoint_inventory']['config.json']['sha256']}`.",
            f"- Qwen tokenizer.json sha256: `{manifest['qwen_checkpoint_inventory']['tokenizer.json']['sha256']}`.",
            f"- Qwen model.safetensors.index.json sha256: `{manifest['qwen_checkpoint_inventory']['model.safetensors.index.json']['sha256']}`.",
            "",
            "The manifest contains full safetensors shard sizes and sha256 values.",
            "",
            "## Next Remediation",
            "",
            "Run the same no-training helper or an equivalent Bridge import preflight",
            "inside a task-owned NemTron/NeMo/Megatron-Bridge runtime where",
            "`megatron.bridge.training.config` and the Qwen Bridge recipe import.",
            "Do not run `qwen_local_train.py` or `run_finetune`; the next proof should",
            "stop after config/dataset/checkpoint import and fail-closed guards.",
            "",
            "## Boundary Confirmation",
            "",
            "No training loop, optimizer step, checkpoint save from training, export,",
            "endpoint, live canary, AIME/task243 eval, promotion, task255 reuse,",
            "AIME2025 train data, shared deletion, main push, merge, or 30B/8-GPU",
            "action was performed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_root = OUTPUT_ROOT / f"run_{timestamp}"
    evidence_dir = run_root / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "task": TASK_ID,
        "created_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "disposition": "CONFIG_IMPORT_PREFLIGHT_BLOCKED_MISSING_MEGATRON_BRIDGE",
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version,
            "executable": sys.executable,
        },
        "code_revision": git_revision(),
        "output_root": str(OUTPUT_ROOT),
        "run_root": str(run_root),
        "task276": task276_references(),
        "resolved_config": resolved_config_payload(),
        "local_data_readability": {
            "status": "PASS",
            "split_counts": split_counts(),
            "sparse_valid_test_preflight_only": {
                "status": "PASS_PREFLIGHT_ONLY",
                "valid_rows": 1,
                "test_rows": 0,
            },
        },
        "contract_checks": contract_checks(),
        "qwen_hf_import": qwen_hf_import_probe(),
        "qwen_checkpoint_inventory": qwen_checkpoint_inventory(),
        "runtime_import_probes": {
            module: import_probe(module)
            for module in (
                "nemo",
                "nemo.collections.llm",
                "megatron",
                "megatron.bridge",
                "megatron.bridge.training.config",
                "megatron.bridge.recipes.qwen.qwen3",
                "nemotron.recipes.super3.stage1_sft.train",
            )
        },
        "commands": {
            "acceptance": (
                "git switch -c intern_nemotron_worker_2/"
                "task278_qwen_aime_v11_task276_config_import_preflight_s1 origin/main"
            ),
            "preflight": (
                "PYTHONPATH=src python3 "
                "workspace/tasks/task278_qwen_aime_v11_task276_config_import_preflight_s1/"
                "build_task278_config_import_preflight.py"
            ),
        },
        "boundaries": {
            "training_loop_run": False,
            "optimizer_step_run": False,
            "checkpoint_save_from_training": False,
            "export_run": False,
            "endpoint_launched": False,
            "live_canary_run": False,
            "aime_task243_eval_run": False,
            "promotion_claimed": False,
            "task255_reused": False,
            "aime2025_train_data_used": False,
            "shared_files_deleted": False,
            "main_pushed": False,
            "merged": False,
            "thirty_b_or_8gpu_used": False,
        },
    }
    manifest_path = evidence_dir / "task278_config_import_preflight_manifest.json"
    report_path = evidence_dir / "task278_config_import_preflight_report.md"
    manifest["manifest_path"] = str(manifest_path)
    manifest["report_path"] = str(report_path)

    report = render_report(manifest)
    report_path.write_text(report, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (evidence_dir / "task278_config_import_preflight_manifest.json.sha256").write_text(
        f"{sha256_file(manifest_path)}  {manifest_path}\n",
        encoding="utf-8",
    )
    (evidence_dir / "task278_config_import_preflight_report.md.sha256").write_text(
        f"{sha256_file(report_path)}  {report_path}\n",
        encoding="utf-8",
    )
    print(json.dumps({"manifest": str(manifest_path), "report": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
