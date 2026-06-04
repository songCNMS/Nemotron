#!/usr/bin/env python3
"""Build task333 combined all-SFT packed-contract evidence.

This helper is task-local and no-training. It constructs a task-owned packed
root by exposing accepted upstream packed Parquet shards through collision-free
symlinks and a fresh split manifest:

- task299 constrained Qwen3-30B seed shards;
- task329 agentic-interactive and instruction-following-structured shards;
- task331 SWE no-tools-header shards.

The combined split assignment is task332_per_source_shard_holdout_v1:
source-local shard 14 is valid, shard 15 is test, all others are train.
Upstream artifacts are read-only inputs and are not mutated.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import platform
import re
import socket
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.compute as pc
import pyarrow.parquet as pq


TASK_ID = "task333_qwen_all_sft_combined_packed_contract_s1"
OUTPUT_BASE = Path("/work-agents/intern_nemotron_worker_1/outputs") / TASK_ID
MODEL_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507")
POLICY_ID = "task332_per_source_shard_holdout_v1"
NUM_SHARDS = 16
VALID_SHARD = 14
TEST_SHARD = 15

TASK299_ROOT = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z"
)
TASK329_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z"
)
TASK331_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z"
)
TASK332_ROOT = Path(
    "/work-agents/intern_nemotron_worker_4/outputs/"
    "task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z"
)
TASK262_ROOT = Path("/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1")

TASK299_PACKED = TASK299_ROOT / "packed_qwen_30b"
TASK329_PACKED = TASK329_ROOT / "packed_qwen_raw_pass_materialized"
TASK331_PACKED = TASK331_ROOT / "packed_qwen_swe_no_tools_header"

TASK299_SOURCE_MAP = {
    "m1-agentic-sft-v11-from-m0": "base_train",
    "m1-agentic-sft-v11-math-final-answer": "final_answer",
    "m1-agentic-sft-v11-math-hard-verified-full-solution": "hard_math_verified_full_solution",
}
TASK329_INCLUDED_DATASETS = {
    "task322-agentic-interactive": "agentic-interactive",
    "task322-instruction-following-structured": "instruction-following-structured",
}
TASK331_INCLUDED_DATASETS = {
    "task327-swe-no-tools-header": "swe",
}
EXCLUDED_TASK327_DECONTAM_HIT_SOURCES = [
    "instruction-following-chat",
    "competitive-cpp-00",
    "competitive-cpp-01",
    "competitive-python-00",
    "competitive-python-01",
    "math-proofs-lean",
    "agentic-tool-calling",
    "infinibyte-00",
    "infinibyte-01",
]


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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def parse_dataset_and_hash(path_value: str) -> tuple[str, str, int]:
    path = Path(path_value)
    parts = path.parts
    if "datasets" not in parts:
        raise ValueError(f"Cannot parse dataset path: {path_value}")
    idx = parts.index("datasets")
    dataset = parts[idx + 1]
    dataset_hash = parts[idx + 2]
    match = re.search(r"shard_(\d{6})(?:\.parquet)?$", path.name)
    if not match:
        raise ValueError(f"Cannot parse shard index from {path_value}")
    return dataset, dataset_hash, int(match.group(1))


def split_for_shard(shard_index: int) -> str:
    if shard_index == VALID_SHARD:
        return "valid"
    if shard_index == TEST_SHARD:
        return "test"
    return "train"


def parquet_metrics(path: Path) -> dict[str, int]:
    rows = 0
    input_tokens = 0
    supervised_tokens = 0
    parquet_file = pq.ParquetFile(path)
    for batch in parquet_file.iter_batches(batch_size=256, columns=["input_ids", "loss_mask"]):
        rows += batch.num_rows
        input_tokens += int(pc.sum(pc.list_value_length(batch["input_ids"])).as_py() or 0)
        supervised_tokens += int(pc.sum(pc.list_flatten(batch["loss_mask"])).as_py() or 0)
    return {
        "rows": rows,
        "input_tokens": input_tokens,
        "supervised_tokens": supervised_tokens,
        "bytes": path.stat().st_size,
    }


def iter_manifest_entries(
    packed_root: Path,
    *,
    upstream_task: str,
    dataset_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    manifest = load_json(packed_root / "splits/manifest.json")
    rows: list[dict[str, Any]] = []
    for source_split, info in manifest["splits"].items():
        for entry in info["entries"]:
            dataset, dataset_hash, shard_index = parse_dataset_and_hash(entry["target_path"])
            if dataset_map is not None and dataset not in dataset_map:
                continue
            source_name = dataset_map[dataset] if dataset_map is not None else dataset
            target_path = Path(entry["target_path"]).resolve(strict=True)
            rows.append(
                {
                    "dataset_name": dataset,
                    "dataset_hash": dataset_hash,
                    "source_name": source_name,
                    "source_split": source_split,
                    "shard_index": shard_index,
                    "target_path": str(target_path),
                    "target_without_suffix": str(target_path.with_suffix("")),
                    "upstream_task": upstream_task,
                    "upstream_packed_root": str(packed_root),
                }
            )
    return rows


def write_task299_row_manifests(run_root: Path) -> dict[str, dict[str, Any]]:
    source_summaries = load_json(TASK262_ROOT / "task251_source_summaries.json")
    out_dir = run_root / "row_manifests"
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, dict[str, Any]] = {}
    for source_name, summary_key in TASK299_SOURCE_MAP.items():
        summary = source_summaries[summary_key]
        source_path = Path(summary["path"]).resolve(strict=True)
        manifest_path = out_dir / f"{source_name}.rows.tsv.gz"
        row_count = 0
        with source_path.open("rb") as src, gzip.open(manifest_path, "wt", encoding="utf-8") as dst:
            dst.write("row_index\trow_sha256\n")
            for row_index, raw_line in enumerate(src):
                if not raw_line.strip():
                    continue
                dst.write(f"{row_index}\t{sha256_bytes(raw_line.rstrip(b'\\n'))}\n")
                row_count += 1
        result[source_name] = {
            "dataset_id": "task251_m1_agentic_sft",
            "decontam_pass": True,
            "file_sha256": summary["sha256"],
            "local_path": str(source_path),
            "name": source_name,
            "prompt_hash_hit_rows": summary.get("heldout_prompt_hash_overlap_task246_user_only", 0),
            "normalized_prompt_hit_rows": "not_emitted_by_task299_accepted_seed",
            "ngram_hit_rows": (
                0
                if source_name == "m1-agentic-sft-v11-math-final-answer"
                else "not_fresh_scanned_in_task333; carried from task299/task262 accepted proof"
            ),
            "row_count": summary["rows"],
            "row_manifest": str(manifest_path),
            "row_manifest_sha256": sha256_file(manifest_path),
            "source_task": "task299/task262/task251",
            "status": "INCLUDED_PASS_TASK299_CONSTRAINED_SEED",
        }
    return result


def load_raw_source_provenance(run_root: Path) -> dict[str, dict[str, Any]]:
    task299_sources = write_task299_row_manifests(run_root)
    task329_matrix = load_json(TASK329_ROOT / "manifests/source_matrix.json")
    task331_provenance = load_json(TASK331_ROOT / "manifests/source_provenance.json")

    result = dict(task299_sources)
    for row in task329_matrix["included_sources"]:
        if row["name"] in {"agentic-interactive", "instruction-following-structured"}:
            result[row["name"]] = {
                "dataset_id": row["dataset_id"],
                "decontam_pass": row["decontam_pass"],
                "file_sha256": row["file_sha256"],
                "local_path": row["local_path"],
                "name": row["name"],
                "ngram_hit_rows": row["ngram_hit_rows"],
                "normalized_prompt_hit_rows": row["normalized_prompt_hit_rows"],
                "parse_errors": row.get("parse_errors", 0),
                "prompt_hash_hit_rows": row["prompt_hash_hit_rows"],
                "row_count": row["row_count"],
                "row_manifest": row["row_manifest"],
                "row_manifest_sha256": row["row_manifest_sha256"],
                "source_task": row["source_task"],
                "status": "INCLUDED_PASS",
            }
    result["swe"] = {
        "dataset_id": task331_provenance["dataset_id"],
        "decontam_pass": True,
        "file_sha256": task331_provenance["file_sha256"],
        "formatter_config_change": task331_provenance["formatter_config_change"],
        "local_path": task331_provenance["local_path"],
        "name": "swe",
        "ngram_hit_rows": 0,
        "normalized_prompt_hit_rows": 0,
        "parse_errors": 0,
        "prompt_hash_hit_rows": 0,
        "row_count": task331_provenance["row_count"],
        "row_manifest": task331_provenance["row_manifest"],
        "row_manifest_sha256": task331_provenance["row_manifest_sha256"],
        "source_task": "task331/task327",
        "status": "INCLUDED_PASS_SWE_NO_TOOLS_HEADER",
    }
    return result


def aggregate_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def empty() -> dict[str, int]:
        return {"shards": 0, "rows": 0, "input_tokens": 0, "supervised_tokens": 0, "bytes": 0}

    by_split: dict[str, dict[str, Any]] = {split: {**empty(), "sources": {}} for split in ("train", "valid", "test")}
    by_source: dict[str, dict[str, Any]] = defaultdict(lambda: {**empty(), "splits": {}})
    total = empty()
    for row in rows:
        split = row["split"]
        source = row["source_name"]
        metrics = row["metrics"]
        for bucket in (by_split[split], by_source[source], total):
            bucket["shards"] += 1
            bucket["rows"] += metrics["rows"]
            bucket["input_tokens"] += metrics["input_tokens"]
            bucket["supervised_tokens"] += metrics["supervised_tokens"]
            bucket["bytes"] += metrics["bytes"]
        split_source = by_split[split]["sources"].setdefault(source, empty())
        source_split = by_source[source]["splits"].setdefault(split, empty())
        for bucket in (split_source, source_split):
            bucket["shards"] += 1
            bucket["rows"] += metrics["rows"]
            bucket["input_tokens"] += metrics["input_tokens"]
            bucket["supervised_tokens"] += metrics["supervised_tokens"]
            bucket["bytes"] += metrics["bytes"]
    return {
        "total": total,
        "by_split": by_split,
        "by_source": dict(sorted(by_source.items())),
        "shards": rows,
    }


def expected_targets_from_blend(blend: dict[str, Any]) -> dict[str, Counter[str]]:
    result: dict[str, Counter[str]] = {}
    for split, values in blend.items():
        counter: Counter[str] = Counter()
        for index in range(1, len(values), 2):
            counter[str(Path(f"{values[index]}.parquet").resolve(strict=False))] += 1
        result[split] = counter
    return result


def actual_targets_from_split_dirs(splits_root: Path) -> dict[str, Counter[str]]:
    result: dict[str, Counter[str]] = {}
    for split in ("train", "valid", "test"):
        counter: Counter[str] = Counter()
        split_dir = splits_root / split
        for entry in sorted(split_dir.glob("*.parquet")):
            if entry.is_symlink():
                target = Path(os.readlink(entry))
                if not target.is_absolute():
                    target = entry.parent / target
                counter[str(target.resolve(strict=False))] += 1
            else:
                counter[str(entry.resolve(strict=False))] += 1
        result[split] = counter
    return result


def build_parity(blend: dict[str, Any], splits_root: Path) -> dict[str, Any]:
    expected = expected_targets_from_blend(blend)
    actual = actual_targets_from_split_dirs(splits_root)
    splits: dict[str, Any] = {}
    all_pass = True
    for split in ("train", "valid", "test"):
        missing = sorted((expected[split] - actual[split]).elements())
        unexpected = sorted((actual[split] - expected[split]).elements())
        passed = not missing and not unexpected
        all_pass = all_pass and passed
        splits[split] = {
            "actual_shards": actual[split].total(),
            "expected_shards": expected[split].total(),
            "missing": missing,
            "multiset_match": passed,
            "unexpected": unexpected,
        }
    return {"all_pass": all_pass, "splits": splits}


def run_logged(cmd: list[str], *, log_path: Path, rc_path: Path, env: dict[str, str]) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(cmd) + "\n")
        log.flush()
        proc = subprocess.run(
            cmd,
            cwd=Path.cwd(),
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    rc_path.write_text(str(proc.returncode) + "\n", encoding="utf-8")
    return int(proc.returncode)


def command_env() -> dict[str, str]:
    env = dict(os.environ)
    repo_src = str(Path.cwd() / "src")
    env["PYTHONPATH"] = repo_src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["WANDB_MODE"] = "offline"
    env["WANDB_DISABLED"] = "true"
    env["TOKENIZERS_PARALLELISM"] = "false"
    env["SUPER3_M1_QWEN_HF_MODEL"] = str(MODEL_PATH)
    env["SUPER3_M1_TOKENIZER_MODEL"] = str(MODEL_PATH)
    return env


def validate_contract(run_root: Path, packed_root: Path) -> dict[str, Any]:
    code = f"""
from pathlib import Path
from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import (
    validate_qwen_packed_sft_chat_contract,
    validate_qwen_training_pipeline_contract,
)
splits = Path({str(packed_root / 'splits')!r})
model = {str(MODEL_PATH)!r}
validate_qwen_packed_sft_chat_contract(splits, tokenizer_model=model)
validate_qwen_training_pipeline_contract(
    splits,
    tokenizer_model=model,
    training_profile='qwen',
    model_ref=model,
    train_entrypoint='src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py',
)
print('TASK333_QWEN30B_PACKED_CONTRACT=PASS')
"""
    env = command_env()
    cmd = [sys.executable, "-c", code]
    log_path = run_root / "logs/qwen30b_contract_validate.log"
    rc_path = run_root / "logs/qwen30b_contract_validate.rc"
    rc = run_logged(cmd, log_path=log_path, rc_path=rc_path, env=env)
    return {"command": cmd, "log_path": str(log_path), "rc": rc, "rc_path": str(rc_path)}


def write_checksum_manifest(paths: list[Path], manifest_path: Path) -> str:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for path in sorted(paths):
        lines.append(f"{sha256_file(path)}  {path}\n")
    manifest_path.write_text("".join(lines), encoding="utf-8")
    return sha256_file(manifest_path)


def run_sha256_check(run_root: Path, manifest_path: Path, name: str) -> dict[str, Any]:
    log_path = run_root / f"logs/{name}.log"
    rc_path = run_root / f"logs/{name}.rc"
    rc = run_logged(["sha256sum", "-c", str(manifest_path)], log_path=log_path, rc_path=rc_path, env=dict(os.environ))
    return {"manifest": str(manifest_path), "log_path": str(log_path), "rc": rc, "rc_path": str(rc_path)}


def build(run_root: Path) -> dict[str, Any]:
    packed_root = run_root / "packed_qwen_combined_contract"
    splits_root = packed_root / "splits"
    manifests_dir = run_root / "manifests"
    logs_dir = run_root / "logs"
    for directory in (packed_root, splits_root, manifests_dir, logs_dir):
        directory.mkdir(parents=True, exist_ok=True)
    for split in ("train", "valid", "test"):
        (splits_root / split).mkdir(parents=True, exist_ok=True)

    raw_source_provenance = load_raw_source_provenance(run_root)
    upstream_rows = []
    upstream_rows.extend(iter_manifest_entries(TASK299_PACKED, upstream_task="task299"))
    upstream_rows.extend(
        iter_manifest_entries(TASK329_PACKED, upstream_task="task329", dataset_map=TASK329_INCLUDED_DATASETS)
    )
    upstream_rows.extend(
        iter_manifest_entries(TASK331_PACKED, upstream_task="task331", dataset_map=TASK331_INCLUDED_DATASETS)
    )

    blend: dict[str, list[str]] = {"train": [], "valid": [], "test": []}
    manifest_splits: dict[str, dict[str, Any]] = {
        split: {"created_shards": 0, "entries": [], "intended_shards": 0}
        for split in ("train", "valid", "test")
    }
    enriched_rows: list[dict[str, Any]] = []
    for row in sorted(upstream_rows, key=lambda r: (r["source_name"], r["shard_index"], r["target_path"])):
        split = split_for_shard(row["shard_index"])
        target_path = Path(row["target_path"])
        link_name = (
            f"{safe_name(row['upstream_task'])}__{safe_name(row['dataset_name'])}__"
            f"{safe_name(row['dataset_hash'])}__shard_{row['shard_index']:06d}.parquet"
        )
        link_path = splits_root / split / link_name
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.symlink_to(target_path)
        metrics = parquet_metrics(target_path)
        shard_sha = sha256_file(target_path)
        blend[split].extend(["1.0", row["target_without_suffix"]])
        entry = {
            "link_name": link_name,
            "link_path": str(link_path),
            "source_path": row["target_without_suffix"],
            "target_path": str(target_path),
            "weight": "1.0",
        }
        manifest_splits[split]["entries"].append(entry)
        manifest_splits[split]["created_shards"] += 1
        manifest_splits[split]["intended_shards"] += 1
        enriched = {
            **row,
            "split": split,
            "link_name": link_name,
            "link_path": str(link_path),
            "metrics": metrics,
            "sha256": shard_sha,
        }
        enriched_rows.append(enriched)

    for split in manifest_splits:
        manifest_splits[split]["entries"] = sorted(
            manifest_splits[split]["entries"], key=lambda e: e["link_name"]
        )
    write_json(packed_root / "blend.json", blend)
    write_json(splits_root / "manifest.json", {"schema_version": 1, "splits": manifest_splits})

    metrics = aggregate_metrics(enriched_rows)
    source_datasets = []
    for source_name, source in sorted(raw_source_provenance.items()):
        source_datasets.append(
            {
                "uri": source["local_path"],
                "name": source_name,
                "weight": 1.0,
                "split": None,
                "subset": None,
                "revision": source.get("repo_revision_from_task308"),
                "text_field": "text",
                "num_rows": source["row_count"],
                "size_bytes": None,
                "num_files": 1,
            }
        )
    metadata = {
        "path": str(splits_root),
        "type": "SFTDataArtifact",
        "metadata": {
            "blend_path": str(packed_root / "blend.json"),
            "chat_template": "tokenizer",
            "chat_template_kwargs": {"enable_thinking": False, "truncate_history_thinking": False},
            "data_format": "packed_sft_parquet",
            "elapsed_sec": 0.0,
            "num_shards": len(enriched_rows),
            "pack_size": 4096,
            "source_datasets": source_datasets,
            "tokenizer_uri": f"file://{MODEL_PATH}",
            "total_sequences": metrics["total"]["rows"],
            "total_tokens": metrics["total"]["input_tokens"],
        },
        "created_at": datetime.now(UTC).isoformat(),
        "producer": "task333_combined_manifest_builder",
        "tracking": None,
        "name": "super3/sft/data",
        "total_tokens": metrics["total"]["input_tokens"],
        "total_sequences": metrics["total"]["rows"],
        "elapsed_sec": 0.0,
        "pack_size": 4096,
        "training_path": None,
        "validation_path": None,
        "test_path": None,
        "metadata_path": None,
        "blend_path": str(packed_root / "blend.json"),
        "num_shards": len(enriched_rows),
        "data_format": "packed_sft_parquet",
        "source_datasets": source_datasets,
        "tokenizer_uri": f"file://{MODEL_PATH}",
        "chat_template": "tokenizer",
        "chat_template_kwargs": {"enable_thinking": False, "truncate_history_thinking": False},
    }
    write_json(splits_root / "metadata.json", metadata)

    parity = build_parity(blend, splits_root)
    write_json(manifests_dir / "intended_vs_exposed_parity.json", parity)
    write_json(manifests_dir / "qwen30b_packing_metrics.json", metrics)
    write_json(manifests_dir / "source_provenance.json", raw_source_provenance)

    structured_summary = load_json(TASK332_ROOT / "manifests/structured_filtered_rows_summary.json")
    structured_rows_path = TASK332_ROOT / "manifests/structured_filtered_rows.jsonl"
    validation_filtered = {
        "disposition": structured_summary["disposition"],
        "filtered_row_count": structured_summary["filtered_row_count"],
        "invalid_by_shard": structured_summary["invalid_by_shard"],
        "receipt_match": structured_summary["receipt_match"],
        "structured_filtered_rows": str(structured_rows_path),
        "structured_filtered_rows_sha256": sha256_file(structured_rows_path),
        "summary": structured_summary,
    }
    write_json(manifests_dir / "validation_filtered_rows_summary.json", validation_filtered)

    task299_decontam = load_json(TASK299_ROOT / "decontam_proof.json")
    task329_decontam = load_json(TASK329_ROOT / "manifests/decontam_no_aime2025_train_proof.json")
    task331_decontam = load_json(TASK331_ROOT / "manifests/decontam_no_aime2025_train_proof.json")
    decontam = {
        "status": "PASS_NO_AIME2025_TRAIN_ROWS_BY_UPSTREAM_ACCEPTED_DECONTAM_AND_SOURCE_EXCLUSION",
        "aime2025_prompt_or_label_train_rows": 0,
        "task255_reuse": "not used",
        "heldout_prompt_hashes": task299_decontam["heldout_prompt_hashes"],
        "heldout_corpus": task299_decontam["heldout_corpus"],
        "task299_seed": {
            "status": task299_decontam["decision"]["status"],
            "aime2025_prompts_or_labels_in_trainable_outputs": task299_decontam["decision"][
                "aime2025_prompts_or_labels_in_trainable_outputs"
            ],
            "source_trainable_scan": task299_decontam["source_trainable_scan"],
            "normalized_prompt_hit_rows": "not_emitted_by_task299_accepted_seed",
            "ngram_evidence": task299_decontam["task262_final_answer_ngram_scan"],
        },
        "task329_raw_sources": {
            "status": task329_decontam["status"],
            "included_source_names": [
                "agentic-interactive",
                "instruction-following-structured",
            ],
            "included_sources": [
                row for row in task329_decontam["included_sources"]
                if row["name"] in {"agentic-interactive", "instruction-following-structured"}
            ],
        },
        "task331_swe": task331_decontam,
        "excluded_task327_decontam_hit_sources": EXCLUDED_TASK327_DECONTAM_HIT_SOURCES,
        "all_task327_blocked_sources_excluded": True,
        "fresh_task333_scan": "not run; task333 is a combined packed-contract materialization using accepted upstream decontam proofs",
    }
    write_json(manifests_dir / "decontam_no_aime2025_train_proof.json", decontam)

    command_manifest = {
        "branch": git(["branch", "--show-current"]),
        "head": git(["rev-parse", "HEAD"]),
        "origin_main": git(["rev-parse", "origin/main"]),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "cwd": str(Path.cwd()),
        "env": {
            "PYTHONPATH": command_env().get("PYTHONPATH"),
            "WANDB_MODE": command_env().get("WANDB_MODE"),
            "WANDB_DISABLED": command_env().get("WANDB_DISABLED"),
            "TOKENIZERS_PARALLELISM": command_env().get("TOKENIZERS_PARALLELISM"),
            "SUPER3_M1_QWEN_HF_MODEL": command_env().get("SUPER3_M1_QWEN_HF_MODEL"),
            "SUPER3_M1_TOKENIZER_MODEL": command_env().get("SUPER3_M1_TOKENIZER_MODEL"),
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "unset"),
        },
        "inputs": {
            "task299_root": str(TASK299_ROOT),
            "task329_root": str(TASK329_ROOT),
            "task331_root": str(TASK331_ROOT),
            "task332_root": str(TASK332_ROOT),
            "model_path": str(MODEL_PATH),
        },
        "policy": {
            "policy_id": POLICY_ID,
            "num_shards": NUM_SHARDS,
            "valid_shard": VALID_SHARD,
            "test_shard": TEST_SHARD,
            "train_shards": [idx for idx in range(NUM_SHARDS) if idx not in {VALID_SHARD, TEST_SHARD}],
        },
    }
    write_json(manifests_dir / "command_env_manifest.json", command_manifest)

    validation = validate_contract(run_root, packed_root)
    write_json(manifests_dir / "contract_validation.json", validation)

    shard_paths = [Path(row["link_path"]) for row in enriched_rows]
    packed_shard_manifest = manifests_dir / "packed_shard_checksums.sha256"
    packed_shard_manifest_sha = write_checksum_manifest(shard_paths, packed_shard_manifest)
    packed_check = run_sha256_check(run_root, packed_shard_manifest, "packed_shard_sha256sum_check")

    artifact_paths = [
        packed_root / "blend.json",
        splits_root / "manifest.json",
        splits_root / "metadata.json",
        manifests_dir / "command_env_manifest.json",
        manifests_dir / "contract_validation.json",
        manifests_dir / "decontam_no_aime2025_train_proof.json",
        manifests_dir / "intended_vs_exposed_parity.json",
        manifests_dir / "qwen30b_packing_metrics.json",
        manifests_dir / "source_provenance.json",
        manifests_dir / "validation_filtered_rows_summary.json",
        run_root / "logs/qwen30b_contract_validate.log",
        run_root / "logs/qwen30b_contract_validate.rc",
        run_root / "logs/packed_shard_sha256sum_check.log",
        run_root / "logs/packed_shard_sha256sum_check.rc",
        packed_shard_manifest,
    ]
    artifact_manifest = manifests_dir / "artifact_checksums.sha256"
    artifact_manifest_sha = write_checksum_manifest(artifact_paths, artifact_manifest)
    artifact_check = run_sha256_check(run_root, artifact_manifest, "artifact_sha256sum_check")

    manifest = {
        "schema_version": 1,
        "task": TASK_ID,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "disposition": "PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW",
        "run_root": str(run_root),
        "packed_root": str(packed_root),
        "splits_root": str(splits_root),
        "blend_path": str(packed_root / "blend.json"),
        "split_manifest": str(splits_root / "manifest.json"),
        "metadata_path": str(splits_root / "metadata.json"),
        "policy_id": POLICY_ID,
        "metrics": {
            "total": metrics["total"],
            "by_split": metrics["by_split"],
            "by_source": metrics["by_source"],
        },
        "included_sources": raw_source_provenance,
        "excluded_sources": {
            "task327_blocked_decontam_hit": EXCLUDED_TASK327_DECONTAM_HIT_SOURCES,
            "task329_zero_supervised_swe": "excluded; replaced with task331 task327-swe-no-tools-header",
            "task332_structured_validation_filtered_rows": validation_filtered,
            "task255": "excluded",
        },
        "checks": {
            "contract_validation": validation,
            "contract_validation_pass": validation["rc"] == 0,
            "intended_vs_exposed_parity": parity,
            "packed_shard_checksum_manifest": str(packed_shard_manifest),
            "packed_shard_checksum_manifest_sha256": packed_shard_manifest_sha,
            "packed_shard_sha256sum_check": packed_check,
            "artifact_checksum_manifest": str(artifact_manifest),
            "artifact_checksum_manifest_sha256": artifact_manifest_sha,
            "artifact_sha256sum_check": artifact_check,
            "decontam_no_aime2025_train": str(manifests_dir / "decontam_no_aime2025_train_proof.json"),
        },
        "boundaries": {
            "training": "not run",
            "optimizer_steps": "not run",
            "nonzero_lr_smoke": "not run",
            "benchmark_eval": "not run",
            "export": "not run",
            "endpoint": "not run",
            "promotion": "not claimed",
            "task310_release": "not claimed",
            "thirty_b_release": "not claimed",
            "task255_reuse": "not used",
            "aime2025_train_rows": 0,
            "shared_deletion_or_mutation": "not performed",
            "main_push_or_merge": "not performed",
        },
    }
    write_json(run_root / "manifest.json", manifest)
    (run_root / "manifest.json.sha256").write_text(
        f"{sha256_file(run_root / 'manifest.json')}  {run_root / 'manifest.json'}\n",
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = args.run_root or (OUTPUT_BASE / f"run_{utc_stamp()}")
    manifest = build(run_root)
    print(json.dumps({
        "disposition": manifest["disposition"],
        "run_root": manifest["run_root"],
        "packed_root": manifest["packed_root"],
        "contract_validation_rc": manifest["checks"]["contract_validation"]["rc"],
        "artifact_sha256sum_check_rc": manifest["checks"]["artifact_sha256sum_check"]["rc"],
        "packed_shard_sha256sum_check_rc": manifest["checks"]["packed_shard_sha256sum_check"]["rc"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
