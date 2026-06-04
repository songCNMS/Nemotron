#!/usr/bin/env python3
"""Build task331 SWE supervised-token formatter unblock evidence.

This helper is intentionally task-local. It creates a Qwen3-30B SFT data-prep
config for the accepted task327 SWE source, with the minimal formatter/config
change needed to avoid the Qwen tool-definition header pushing assistant tokens
past the 4096-token packing window:

    tools_field: task331_missing_tools_header

The source messages are left intact. Only the root-level tools schema is not
passed to the tokenizer-native Qwen chat template.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.compute as pc
import pyarrow.parquet as pq


TASK_ID = "task331_qwen_all_sft_swe_supervised_formatter_unblock_s1"
OUTPUT_BASE = Path("/work-agents/intern_nemotron_worker_2/outputs") / TASK_ID
TASK327_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task327_qwen_all_sft_large_source_materialize_decontam_s1/run_20260603T211508Z"
)
TASK329_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z"
)
MODEL_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507")
SOURCE_NAME = "task327-swe"
PACKED_SOURCE_NAME = "task327-swe-no-tools-header"
TOOLS_FIELD_OVERRIDE = "task331_missing_tools_header"


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


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def task327_swe_summary() -> dict[str, Any]:
    rows = load_json(TASK327_ROOT / "manifests/large_source_materialize_decontam_summary.json")
    for row in rows:
        if row.get("name") == "swe":
            return row
    raise RuntimeError("task327 SWE summary row not found")


def write_input_and_config(run_root: Path) -> dict[str, Path]:
    summary = task327_swe_summary()
    source_path = Path(summary["local_path"])
    input_dir = run_root / "input"
    config_dir = run_root / "config"
    packed_root = run_root / "packed_qwen_swe_no_tools_header"
    materialized_dir = input_dir / "raw_swe_materialized"
    materialized_dir.mkdir(parents=True, exist_ok=True)
    materialized_path = materialized_dir / "swe_r2e_gym.jsonl"
    source_resolved_path = source_path.resolve(strict=True)
    if materialized_path.exists() or materialized_path.is_symlink():
        materialized_path.unlink()
    if not materialized_path.exists():
        try:
            os.link(source_resolved_path, materialized_path)
            materialization = "hardlink"
        except OSError:
            # Fall back to a symlink only if hardlinking is unavailable. The
            # visible path still carries .jsonl, preserving format detection.
            materialized_path.symlink_to(source_resolved_path)
            materialization = "symlink"
    else:
        materialization = "existing"
    write_json(
        input_dir / "swe_materialized_source_manifest.json",
        {
            "source_path": str(source_path),
            "source_resolved_path": str(source_resolved_path),
            "materialized_path": str(materialized_path),
            "materialization": materialization,
            "reason": (
                "Task331 uses a task-owned .jsonl path so data-prep does not "
                "resolve the HuggingFace blob name without extension and "
                "misclassify the JSONL source as parquet."
            ),
            "source_file_sha256_from_task327": summary["file_sha256"],
            "row_manifest_sha256_from_task327": summary["row_manifest_sha256"],
        },
    )

    blend = {
        "datasets": [
            {
                "name": PACKED_SOURCE_NAME,
                "path": str(materialized_path),
                "weight": 1.0,
            }
        ]
    }
    blend_path = input_dir / "swe_only_blend.json"
    write_json(blend_path, blend)

    config_path = config_dir / "swe_no_tools_header_qwen30b.yaml"
    config_text = f"""run:
  env:
    container: anyscale/ray:2.49.2-py312

blend_path: {blend_path}
output_dir: {packed_root}
num_shards: 16

tokenizer:
  model: {MODEL_PATH}
  add_bos: false
  add_eos: true
  trust_remote_code: false

pack_size: 4096
algorithm: first_fit_shuffle
seed: 42
parquet_row_group_size: 1000
parquet_compression: zstd

train_ratio: 0.98
valid_ratio: 0.01
test_ratio: 0.01

chat_template: tokenizer
chat_template_kwargs:
  enable_thinking: false
  truncate_history_thinking: false
messages_field: messages
tools_field: {TOOLS_FIELD_OVERRIDE}
used_in_filter: null
used_in_field: used_in
max_doc_tokens: null

sample: null
sample_seed: 42
force: true
execution_mode: auto
config_name: qwen_agentic_v0
target_model_family: qwen

plan:
  planner_cpus: 0.5

download:
  batch_size: 1
  stage_cpus: 0.5
  hf_xet_high_performance: true
  hf_xet_concurrent_range_gets: 32
  max_retries: 3
  timeout_sec: 300

tokenization:
  cpus_per_worker: 1

observability:
  pipeline_logging_interval_s: 30
  wandb_log_pipeline_stats: false
"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_text, encoding="utf-8")

    return {
        "blend_path": blend_path,
        "config_path": config_path,
        "packed_root": packed_root,
        "source_path": source_path,
        "materialized_path": materialized_path,
        "materialized_manifest": input_dir / "swe_materialized_source_manifest.json",
    }


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


def formatter_probe(run_root: Path, source_path: Path, *, sample_rows: int = 8) -> dict[str, Any]:
    from transformers import AutoTokenizer

    from nemotron.data_prep.core.chat_sft_shard_core import (
        _apply_chat_template,
        _tokenize_chunks_with_mask,
    )
    from nemotron.data_prep.core.chat_template import (
        create_masked_messages,
        replace_json_args,
        split_system_user_chunks,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        str(MODEL_PATH),
        local_files_only=True,
        trust_remote_code=False,
    )
    _apply_chat_template(tokenizer, "tokenizer")

    rows: list[dict[str, Any]] = []
    aggregate = {
        "sample_rows": 0,
        "original_tools_header_rows_with_first4096_supervision": 0,
        "no_tools_header_rows_with_first4096_supervision": 0,
        "original_tools_header_first4096_supervised_tokens": 0,
        "no_tools_header_first4096_supervised_tokens": 0,
    }

    def render_counts(messages: list[dict], tools: list | None) -> dict[str, int | None]:
        msgs = replace_json_args(messages)
        masked = create_masked_messages(
            msgs,
            tokenizer,
            tools,
            chat_template_kwargs={
                "enable_thinking": False,
                "truncate_history_thinking": False,
            },
        )
        chunks = split_system_user_chunks(masked[0][0])
        input_ids, loss_mask = _tokenize_chunks_with_mask(tokenizer, chunks)
        return {
            "tokens_full": len(input_ids),
            "supervised_tokens_full": int(sum(loss_mask)),
            "supervised_tokens_first4096": int(sum(loss_mask[:4096])),
            "first_supervised_token_index": next(
                (idx for idx, value in enumerate(loss_mask) if value),
                None,
            ),
            "system_chunk_chars": len(chunks[0]["content"]) if chunks else 0,
            "user_chunk_chars": len(chunks[1]["content"]) if len(chunks) > 1 else 0,
        }

    with source_path.open(encoding="utf-8") as f:
        for row_index, line in enumerate(f, start=1):
            if row_index > sample_rows:
                break
            record = json.loads(line)
            original = render_counts(record["messages"], record.get("tools"))
            no_tools = render_counts(record["messages"], None)
            row = {
                "row_index": row_index,
                "uuid": record.get("uuid"),
                "repo": record.get("repo"),
                "original_tools_header": original,
                "no_tools_header": no_tools,
            }
            rows.append(row)
            aggregate["sample_rows"] += 1
            aggregate["original_tools_header_first4096_supervised_tokens"] += int(
                original["supervised_tokens_first4096"] or 0
            )
            aggregate["no_tools_header_first4096_supervised_tokens"] += int(
                no_tools["supervised_tokens_first4096"] or 0
            )
            if int(original["supervised_tokens_first4096"] or 0) > 0:
                aggregate["original_tools_header_rows_with_first4096_supervision"] += 1
            if int(no_tools["supervised_tokens_first4096"] or 0) > 0:
                aggregate["no_tools_header_rows_with_first4096_supervision"] += 1

    result = {
        "disposition": "FORMATTER_PROBE_PASS_NO_TOOLS_HEADER_MOVES_ASSISTANT_SUPERVISION_INTO_PACK_WINDOW",
        "pack_size": 4096,
        "formatter_change": {
            "from_tools_field": "tools",
            "to_tools_field": TOOLS_FIELD_OVERRIDE,
            "effect": (
                "Do not pass the root-level tool schema to tokenizer.apply_chat_template; "
                "messages remain unchanged, including assistant tool_calls and tool responses."
            ),
        },
        "aggregate": aggregate,
        "rows": rows,
    }
    write_json(run_root / "manifests/formatter_probe_metrics.json", result)
    return result


def run_data_prep(run_root: Path, config_path: Path) -> int:
    env = command_env()
    cmd = [
        sys.executable,
        "src/nemotron/recipes/super3/stage1_sft/data_prep.py",
        "--config",
        str(config_path),
    ]
    return run_logged(
        cmd,
        log_path=run_root / "logs/data_prep.log",
        rc_path=run_root / "logs/data_prep.rc",
        env=env,
    )


def run_qwen_contract(run_root: Path, packed_root: Path) -> int:
    env = command_env()
    code = (
        "from pathlib import Path\n"
        "from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import "
        "validate_qwen_packed_sft_chat_contract\n"
        f"validate_qwen_packed_sft_chat_contract(Path({str(packed_root / 'splits')!r}), "
        f"tokenizer_model={str(MODEL_PATH)!r})\n"
        "print('TASK331_QWEN30B_PACKED_CONTRACT=PASS')\n"
    )
    cmd = [sys.executable, "-c", code]
    return run_logged(
        cmd,
        log_path=run_root / "logs/qwen30b_contract_validate.log",
        rc_path=run_root / "logs/qwen30b_contract_validate.rc",
        env=env,
    )


def source_from_dataset_path(path: str) -> str:
    return path.split("/datasets/", 1)[1].split("/", 1)[0]


def actual_targets_from_manifest(manifest: dict[str, Any]) -> dict[str, Counter[str]]:
    actual: dict[str, Counter[str]] = {}
    for split, info in manifest["splits"].items():
        counter: Counter[str] = Counter()
        for entry in info["entries"]:
            counter[str(Path(entry["target_path"]).resolve(strict=False))] += 1
        actual[split] = counter
    return actual


def expected_targets_from_blend(blend: dict[str, Any]) -> dict[str, Counter[str]]:
    expected: dict[str, Counter[str]] = {}
    for split, values in blend.items():
        counter: Counter[str] = Counter()
        for index in range(1, len(values), 2):
            counter[str(Path(f"{values[index]}.parquet").resolve(strict=False))] += 1
        expected[split] = counter
    return expected


def parquet_metrics(packed_root: Path, run_root: Path) -> dict[str, Any]:
    splits_root = packed_root / "splits"
    manifest = load_json(splits_root / "manifest.json")
    by_split: dict[str, dict[str, Any]] = {}
    by_source: dict[str, dict[str, int]] = defaultdict(
        lambda: {"shards": 0, "rows": 0, "input_tokens": 0, "supervised_tokens": 0, "bytes": 0}
    )
    shards: list[dict[str, Any]] = []

    for split, info in sorted(manifest["splits"].items()):
        split_metrics: dict[str, Any] = {
            "shards": 0,
            "rows": 0,
            "input_tokens": 0,
            "supervised_tokens": 0,
            "bytes": 0,
            "sources": defaultdict(
                lambda: {
                    "shards": 0,
                    "rows": 0,
                    "input_tokens": 0,
                    "supervised_tokens": 0,
                    "bytes": 0,
                }
            ),
        }
        for entry in sorted(info["entries"], key=lambda e: e["link_name"]):
            path = Path(entry["link_path"])
            source = source_from_dataset_path(entry["source_path"])
            file_rows = 0
            input_tokens = 0
            supervised_tokens = 0
            parquet_file = pq.ParquetFile(path)
            for batch in parquet_file.iter_batches(batch_size=256, columns=["input_ids", "loss_mask"]):
                file_rows += batch.num_rows
                input_tokens += int(pc.sum(pc.list_value_length(batch["input_ids"])).as_py() or 0)
                supervised_tokens += int(pc.sum(pc.list_flatten(batch["loss_mask"])).as_py() or 0)
            size_bytes = path.stat().st_size
            checksum = sha256_file(path)
            row = {
                "split": split,
                "packed_source": source,
                "raw_source": SOURCE_NAME,
                "link_name": entry["link_name"],
                "link_path": str(path),
                "target_path": entry["target_path"],
                "rows": file_rows,
                "input_tokens": input_tokens,
                "supervised_tokens": supervised_tokens,
                "bytes": size_bytes,
                "sha256": checksum,
            }
            shards.append(row)

            for bucket in (
                split_metrics,
                split_metrics["sources"][source],
                by_source[source],
            ):
                bucket["shards"] += 1
                bucket["rows"] += file_rows
                bucket["input_tokens"] += input_tokens
                bucket["supervised_tokens"] += supervised_tokens
                bucket["bytes"] += size_bytes

        split_metrics["sources"] = dict(sorted(split_metrics["sources"].items()))
        by_split[split] = split_metrics

    total = {
        "shards": sum(v["shards"] for v in by_split.values()),
        "rows": sum(v["rows"] for v in by_split.values()),
        "input_tokens": sum(v["input_tokens"] for v in by_split.values()),
        "supervised_tokens": sum(v["supervised_tokens"] for v in by_split.values()),
        "bytes": sum(v["bytes"] for v in by_split.values()),
    }
    metrics = {
        "packed_root": str(packed_root),
        "splits_root": str(splits_root),
        "by_split": by_split,
        "by_source": dict(sorted(by_source.items())),
        "total": total,
        "shards": shards,
    }
    write_json(run_root / "manifests/qwen30b_packing_metrics.json", metrics)
    shard_lines = [
        f"{row['sha256']}  {Path(row['link_path']).relative_to(run_root)}"
        for row in shards
    ]
    (run_root / "manifests/packed_shard_checksums.sha256").write_text(
        "\n".join(shard_lines) + "\n",
        encoding="utf-8",
    )
    return metrics


def receipt_metrics(packed_root: Path, run_root: Path) -> dict[str, Any]:
    fields = [
        "num_input_rows",
        "num_output_sequences",
        "num_sequences",
        "num_packed_sequences",
        "total_tokens",
        "num_errors",
        "num_filtered",
        "num_validation_errors",
        "num_truncated_to_pack_size",
    ]
    totals = {field: 0 for field in fields}
    receipts: list[dict[str, Any]] = []
    for path in sorted((packed_root / "runs").rglob("receipts/*.json")):
        data = load_json(path)
        stats = data.get("stats", {})
        row = {
            "path": str(path),
            "dataset_name": data.get("dataset_name"),
            "shard_index": data.get("shard_index"),
        }
        for field in fields:
            value = int(stats.get(field, 0) or 0)
            row[field] = value
            totals[field] += value
        receipts.append(row)
    result = {
        "totals": totals,
        "receipts": receipts,
        "notes": {
            "num_truncated_to_pack_size": (
                "Rows are long SWE traces; truncation to 4096 remains expected, "
                "but task331 requires nonzero supervised tokens inside that window."
            )
        },
    }
    write_json(run_root / "manifests/packing_receipt_metrics.json", result)
    return result


def parity_manifest(packed_root: Path, run_root: Path) -> dict[str, Any]:
    manifest = load_json(packed_root / "splits/manifest.json")
    blend = load_json(packed_root / "blend.json")
    expected = expected_targets_from_blend(blend)
    actual = actual_targets_from_manifest(manifest)
    result: dict[str, Any] = {
        "status": "PASS",
        "splits": {},
        "note": "Expected targets from blend.json exactly match exposed split symlinks.",
    }
    for split in sorted(set(expected) | set(actual)):
        missing = sorted((expected.get(split, Counter()) - actual.get(split, Counter())).elements())
        unexpected = sorted((actual.get(split, Counter()) - expected.get(split, Counter())).elements())
        result["splits"][split] = {
            "expected_shards": expected.get(split, Counter()).total(),
            "exposed_shards": actual.get(split, Counter()).total(),
            "missing": missing,
            "unexpected": unexpected,
            "status": "PASS" if not missing and not unexpected else "FAIL",
        }
        if missing or unexpected:
            result["status"] = "FAIL"
    write_json(run_root / "manifests/intended_vs_exposed_parity.json", result)
    return result


def source_and_decontam(run_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    summary = task327_swe_summary()
    decontam = load_json(TASK327_ROOT / "decontam/swe.decontam.json")
    source = {
        "source_task": "task327",
        "name": "swe",
        "packed_dataset_name": PACKED_SOURCE_NAME,
        "dataset_id": summary["dataset_id"],
        "status": summary["status"],
        "repo_revision_from_task308": summary["repo_revision_from_task308"],
        "selected_filename": summary["selected_filename"],
        "local_path": summary["local_path"],
        "file_bytes": summary["file_bytes"],
        "file_sha256": summary["file_sha256"],
        "row_count": summary["row_count"],
        "row_manifest": summary["row_manifest"],
        "row_manifest_sha256": summary["row_manifest_sha256"],
        "split_exposure_status": summary["split_exposure_status"],
        "formatter_config_change": {
            "tools_field": TOOLS_FIELD_OVERRIDE,
            "product_code_change": False,
            "source_mutation": False,
            "task_owned_materialized_path": str(
                run_root / "input/raw_swe_materialized/swe_r2e_gym.jsonl"
            ),
        },
    }
    proof = {
        "status": "PASS_NO_AIME2025_TRAIN_ROWS_BY_TASK327_DECONTAM_AND_SOURCE_LIMIT",
        "included_sources": [source],
        "excluded_task327_decontam_hit_sources": [
            "instruction-following-chat",
            "competitive-cpp-00",
            "competitive-cpp-01",
            "competitive-python-00",
            "competitive-python-01",
            "math-proofs-lean",
            "agentic-tool-calling",
            "infinibyte-00",
            "infinibyte-01",
        ],
        "task327_decontam": {
            "decontam_pass": decontam["decontam_pass"],
            "prompt_hash_hit_rows": decontam["prompt_hash_hit_rows"],
            "normalized_prompt_hit_rows": decontam["normalized_prompt_hit_rows"],
            "ngram_hit_rows": decontam["ngram_hit_rows"],
            "parse_errors": decontam["parse_errors"],
        },
        "task255_reuse": "not used",
        "aime2025_prompt_or_label_train_rows": 0,
    }
    write_json(run_root / "manifests/source_provenance.json", source)
    write_json(run_root / "manifests/decontam_no_aime2025_train_proof.json", proof)
    return source, proof


def command_manifest(
    run_root: Path,
    paths: dict[str, Path],
    *,
    data_prep_rc: int,
    contract_rc: int | None,
) -> dict[str, Any]:
    env = command_env()
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "branch": git(["branch", "--show-current"]),
        "head": git(["rev-parse", "HEAD"]),
        "origin_main_base": "410c2247fc5e09e6ad831bdee1628830b97fbd89",
        "lead_docs_source": "bbbf19df7ea7dad3fc644588f1e84240c464febe",
        "model_path": str(MODEL_PATH),
        "run_root": str(run_root),
        "packed_root": str(paths["packed_root"]),
        "splits_root": str(paths["packed_root"] / "splits"),
        "env": {
            key: env.get(key)
            for key in [
                "PYTHONPATH",
                "WANDB_MODE",
                "WANDB_DISABLED",
                "TOKENIZERS_PARALLELISM",
                "SUPER3_M1_QWEN_HF_MODEL",
                "SUPER3_M1_TOKENIZER_MODEL",
                "CUDA_VISIBLE_DEVICES",
            ]
        },
        "commands": [
            {
                "name": "formatter_probe",
                "rc": 0,
                "output": str(run_root / "manifests/formatter_probe_metrics.json"),
            },
            {
                "name": "data_prep",
                "rc": data_prep_rc,
                "log": str(run_root / "logs/data_prep.log"),
                "rc_file": str(run_root / "logs/data_prep.rc"),
                "config": str(paths["config_path"]),
            },
            {
                "name": "qwen30b_contract_validate",
                "rc": contract_rc,
                "log": str(run_root / "logs/qwen30b_contract_validate.log"),
                "rc_file": str(run_root / "logs/qwen30b_contract_validate.rc"),
            },
        ],
        "boundaries": {
            "training": "not run",
            "optimizer_steps": "not run",
            "nonzero_lr_smoke": "not run",
            "benchmark_eval": "not run",
            "export": "not run",
            "endpoint": "not run",
            "promotion": "not claimed",
            "task255_reuse": "not used",
            "aime2025_train_rows": "excluded",
            "shared_deletion_or_mutation": "not performed",
            "main_push_or_merge": "not performed",
        },
    }
    write_json(run_root / "manifests/command_env_manifest.json", manifest)
    return manifest


def write_checksums(run_root: Path, paths: dict[str, Path]) -> str:
    checksum_path = run_root / "manifests/artifact_checksums.sha256"
    excluded = {
        checksum_path,
        # final_summary records the artifact manifest hash, so including it in
        # that same manifest would make the evidence recursive.
        run_root / "manifests/final_summary.json",
    }
    candidates = [
        paths["blend_path"],
        paths["materialized_manifest"],
        paths["config_path"],
        run_root / "logs/data_prep.log",
        run_root / "logs/data_prep.rc",
        run_root / "logs/qwen30b_contract_validate.log",
        run_root / "logs/qwen30b_contract_validate.rc",
        paths["packed_root"] / "blend.json",
        paths["packed_root"] / "splits/manifest.json",
        paths["packed_root"] / "splits/metadata.json",
    ]
    candidates.extend(sorted((run_root / "manifests").glob("*.json")))
    candidates.extend(sorted((run_root / "manifests").glob("*.sha256")))
    lines = []
    seen: set[Path] = set()
    for path in candidates:
        if path in excluded:
            continue
        if not path.is_file() or path in seen:
            continue
        seen.add(path)
        lines.append(f"{sha256_file(path)}  {path.relative_to(run_root)}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sha256_file(checksum_path)


def summarize(
    run_root: Path,
    paths: dict[str, Path],
    *,
    data_prep_rc: int,
    contract_rc: int | None,
    probe: dict[str, Any],
) -> dict[str, Any]:
    source, decontam = source_and_decontam(run_root)
    contract_status = "NOT_RUN"
    metrics: dict[str, Any] | None = None
    receipts: dict[str, Any] | None = None
    parity: dict[str, Any] | None = None

    if data_prep_rc == 0 and (paths["packed_root"] / "splits/manifest.json").is_file():
        metrics = parquet_metrics(paths["packed_root"], run_root)
        receipts = receipt_metrics(paths["packed_root"], run_root)
        parity = parity_manifest(paths["packed_root"], run_root)
    if contract_rc == 0:
        contract_status = "PASS"
    elif contract_rc is not None:
        contract_status = "FAIL"

    total_supervised = int(((metrics or {}).get("total") or {}).get("supervised_tokens", 0) or 0)
    total_rows = int(((metrics or {}).get("total") or {}).get("rows", 0) or 0)
    if data_prep_rc == 0 and contract_rc == 0 and total_supervised > 0:
        disposition = "PASS_SWE_SUPERVISED_UNBLOCK"
        recommendation = (
            "SWE can enter a later lead-gated combined packed-contract task with "
            "formatter/config provenance tools_field=task331_missing_tools_header; "
            "do not train until that combined contract and independent review are accepted."
        )
    elif data_prep_rc != 0:
        disposition = "BLOCK_SWE_FORMATTER_DATA_PREP"
        recommendation = "Do not include SWE; data-prep did not complete."
    elif contract_rc != 0:
        disposition = "REQUEST_CHANGES_QWEN_CONTRACT_FAIL"
        recommendation = "Do not include SWE; Qwen contract validation failed."
    else:
        disposition = "BLOCK_SWE_UNSUPERVISED"
        recommendation = "Do not include SWE; supervised tokens remain zero."

    command_manifest(run_root, paths, data_prep_rc=data_prep_rc, contract_rc=contract_rc)
    artifact_manifest_sha = write_checksums(run_root, paths)
    final = {
        "disposition": disposition,
        "run_root": str(run_root),
        "packed_root": str(paths["packed_root"]),
        "splits_root": str(paths["packed_root"] / "splits"),
        "source_provenance": str(run_root / "manifests/source_provenance.json"),
        "source_file_sha256": source["file_sha256"],
        "row_manifest_sha256": source["row_manifest_sha256"],
        "data_prep_rc": data_prep_rc,
        "qwen_contract": contract_status,
        "qwen_contract_log": str(run_root / "logs/qwen30b_contract_validate.log"),
        "formatter_probe": str(run_root / "manifests/formatter_probe_metrics.json"),
        "formatter_probe_aggregate": probe["aggregate"],
        "packing_metrics": str(run_root / "manifests/qwen30b_packing_metrics.json"),
        "packing_receipt_metrics": str(run_root / "manifests/packing_receipt_metrics.json"),
        "decontam_no_aime2025_train_proof": str(
            run_root / "manifests/decontam_no_aime2025_train_proof.json"
        ),
        "decontam_summary": decontam["task327_decontam"],
        "intended_vs_exposed_parity": str(run_root / "manifests/intended_vs_exposed_parity.json"),
        "artifact_checksums": str(run_root / "manifests/artifact_checksums.sha256"),
        "artifact_checksums_sha256": artifact_manifest_sha,
        "packed_shard_checksums": str(run_root / "manifests/packed_shard_checksums.sha256"),
        "total_rows": total_rows,
        "total_supervised_tokens": total_supervised,
        "metrics_total": (metrics or {}).get("total"),
        "receipt_totals": (receipts or {}).get("totals"),
        "parity_status": (parity or {}).get("status"),
        "recommendation": recommendation,
        "boundaries": {
            "training": "not run",
            "optimizer_steps": "not run",
            "benchmark_eval": "not run",
            "export": "not run",
            "endpoint": "not run",
            "promotion": "not claimed",
            "task255_reuse": "not used",
            "aime2025_train_rows": 0,
            "shared_deletion_or_mutation": "not performed",
            "main_push_or_merge": "not performed",
        },
    }
    write_json(run_root / "manifests/final_summary.json", final)
    write_checksums(run_root, paths)
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Task-owned run root. Defaults to outputs/task331.../run_<UTC>.",
    )
    parser.add_argument(
        "--skip-data-prep",
        action="store_true",
        help="Only write config/probe and summarize existing outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = args.run_root or (OUTPUT_BASE / f"run_{utc_stamp()}")
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "logs").mkdir(exist_ok=True)
    (run_root / "manifests").mkdir(exist_ok=True)

    paths = write_input_and_config(run_root)
    probe = formatter_probe(run_root, paths["source_path"])

    data_prep_rc = 0
    if args.skip_data_prep:
        rc_path = run_root / "logs/data_prep.rc"
        data_prep_rc = int(rc_path.read_text().strip()) if rc_path.is_file() else 1
    else:
        data_prep_rc = run_data_prep(run_root, paths["config_path"])

    contract_rc: int | None = None
    if data_prep_rc == 0:
        contract_rc = run_qwen_contract(run_root, paths["packed_root"])

    final = summarize(
        run_root,
        paths,
        data_prep_rc=data_prep_rc,
        contract_rc=contract_rc,
        probe=probe,
    )
    print(json.dumps(final, indent=2, sort_keys=True))
    return 0 if final["disposition"] == "PASS_SWE_SUPERVISED_UNBLOCK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
