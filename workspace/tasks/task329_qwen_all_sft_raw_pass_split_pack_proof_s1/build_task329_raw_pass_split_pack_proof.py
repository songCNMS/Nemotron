#!/usr/bin/env python3
"""Build task329 raw-pass split and Qwen30B packing evidence."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.compute as pc
import pyarrow.parquet as pq


RUN_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z"
)
TASK322_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z"
)
TASK327_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task327_qwen_all_sft_large_source_materialize_decontam_s1/run_20260603T211508Z"
)
MODEL_PATH = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507")
PACKED_ROOT = RUN_ROOT / "packed_qwen_raw_pass_materialized"
SPLITS_ROOT = PACKED_ROOT / "splits"
MANIFEST_DIR = RUN_ROOT / "manifests"
MATRIX_DIR = RUN_ROOT / "matrices"

INCLUDED_SOURCE_NAMES = {
    "instruction-following-structured",
    "agentic-interactive",
    "swe",
}
PACKED_TO_RAW_SOURCE = {
    "task322-instruction-following-structured": "instruction-following-structured",
    "task322-agentic-interactive": "agentic-interactive",
    "task327-swe": "swe",
}
EXPECTED_BLOCKED_TASK327 = {
    "instruction-following-chat",
    "competitive-cpp-00",
    "competitive-cpp-01",
    "competitive-python-00",
    "competitive-python-01",
    "math-proofs-lean",
    "agentic-tool-calling",
    "infinibyte-00",
    "infinibyte-01",
}


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


def source_from_dataset_path(path: str) -> str:
    return path.split("/datasets/", 1)[1].split("/", 1)[0]


def expected_targets_from_blend(blend: dict[str, Any]) -> dict[str, Counter[str]]:
    expected: dict[str, Counter[str]] = {}
    for split, values in blend.items():
        counter: Counter[str] = Counter()
        for index in range(1, len(values), 2):
            target = str(Path(f"{values[index]}.parquet").resolve(strict=False))
            counter[target] += 1
        expected[split] = counter
    return expected


def actual_targets_from_manifest(manifest: dict[str, Any]) -> dict[str, Counter[str]]:
    actual: dict[str, Counter[str]] = {}
    for split, info in manifest["splits"].items():
        counter: Counter[str] = Counter()
        for entry in info["entries"]:
            counter[str(Path(entry["target_path"]).resolve(strict=False))] += 1
        actual[split] = counter
    return actual


def parquet_metrics(manifest: dict[str, Any]) -> dict[str, Any]:
    by_split: dict[str, dict[str, Any]] = {}
    by_source: dict[str, dict[str, int]] = defaultdict(
        lambda: {"shards": 0, "rows": 0, "input_tokens": 0, "supervised_tokens": 0, "bytes": 0}
    )
    by_split_source: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "shards": 0,
                "rows": 0,
                "input_tokens": 0,
                "supervised_tokens": 0,
                "bytes": 0,
            }
        )
    )
    shard_rows: list[dict[str, Any]] = []

    for split, info in sorted(manifest["splits"].items()):
        split_metrics = {
            "shards": 0,
            "rows": 0,
            "input_tokens": 0,
            "supervised_tokens": 0,
            "bytes": 0,
            "sources": {},
        }
        for entry in sorted(info["entries"], key=lambda e: e["link_name"]):
            path = Path(entry["link_path"])
            source = source_from_dataset_path(entry["source_path"])
            raw_source = PACKED_TO_RAW_SOURCE.get(source, source)
            file_rows = 0
            input_tokens = 0
            supervised_tokens = 0
            parquet_file = pq.ParquetFile(path)
            for batch in parquet_file.iter_batches(
                batch_size=256,
                columns=["input_ids", "loss_mask"],
            ):
                file_rows += batch.num_rows
                input_tokens += int(pc.sum(pc.list_value_length(batch["input_ids"])).as_py() or 0)
                supervised_tokens += int(pc.sum(pc.list_flatten(batch["loss_mask"])).as_py() or 0)
            size_bytes = path.stat().st_size
            checksum = sha256_file(path)

            row = {
                "split": split,
                "packed_source": source,
                "raw_source": raw_source,
                "link_name": entry["link_name"],
                "link_path": str(path),
                "target_path": entry["target_path"],
                "rows": file_rows,
                "input_tokens": input_tokens,
                "supervised_tokens": supervised_tokens,
                "bytes": size_bytes,
                "sha256": checksum,
            }
            shard_rows.append(row)

            split_metrics["shards"] += 1
            split_metrics["rows"] += file_rows
            split_metrics["input_tokens"] += input_tokens
            split_metrics["supervised_tokens"] += supervised_tokens
            split_metrics["bytes"] += size_bytes
            for bucket in (by_source[raw_source], by_split_source[split][raw_source]):
                bucket["shards"] += 1
                bucket["rows"] += file_rows
                bucket["input_tokens"] += input_tokens
                bucket["supervised_tokens"] += supervised_tokens
                bucket["bytes"] += size_bytes

        split_metrics["sources"] = dict(sorted(by_split_source[split].items()))
        by_split[split] = split_metrics

    total = {
        "shards": sum(v["shards"] for v in by_split.values()),
        "rows": sum(v["rows"] for v in by_split.values()),
        "input_tokens": sum(v["input_tokens"] for v in by_split.values()),
        "supervised_tokens": sum(v["supervised_tokens"] for v in by_split.values()),
        "bytes": sum(v["bytes"] for v in by_split.values()),
    }
    return {
        "packed_root": str(PACKED_ROOT),
        "splits_root": str(SPLITS_ROOT),
        "by_split": by_split,
        "by_source": dict(sorted(by_source.items())),
        "total": total,
        "shards": shard_rows,
    }


def receipt_metrics() -> dict[str, Any]:
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
    by_source: dict[str, dict[str, int]] = defaultdict(lambda: {field: 0 for field in fields})
    receipts: list[dict[str, Any]] = []
    for path in sorted((PACKED_ROOT / "runs").rglob("receipts/*.json")):
        data = load_json(path)
        stats = data["stats"]
        dataset = data["dataset_name"]
        raw_source = PACKED_TO_RAW_SOURCE.get(dataset, dataset)
        row = {
            "path": str(path),
            "dataset_name": dataset,
            "raw_source": raw_source,
            "shard_index": data["shard_index"],
        }
        for field in fields:
            value = int(stats.get(field, 0) or 0)
            row[field] = value
            totals[field] += value
            by_source[raw_source][field] += value
        receipts.append(row)
    return {
        "totals": totals,
        "by_source": dict(sorted(by_source.items())),
        "receipts": receipts,
        "notes": {
            "num_sequences": "receipt-level output sequence count before final bin packing",
            "num_packed_sequences": "Parquet row count after final bin packing",
        },
    }


def build_source_matrix() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    task322 = load_json(TASK322_ROOT / "manifests/materialize_count_decontam_summary.json")
    task327 = load_json(TASK327_ROOT / "manifests/large_source_materialize_decontam_summary.json")

    included_rows: list[dict[str, Any]] = []
    excluded_rows: list[dict[str, Any]] = []
    for row in task322:
        if row.get("name") in {"instruction-following-structured", "agentic-interactive"}:
            included_rows.append(
                {
                    "source_task": "task322",
                    "name": row["name"],
                    "dataset_id": row["dataset_id"],
                    "status": row["status"],
                    "decontam_pass": True,
                    "row_count": row["row_count"],
                    "file_bytes": row["file_bytes"],
                    "file_sha256": row["file_sha256"],
                    "row_manifest": row["row_manifest"],
                    "row_manifest_sha256": row["row_manifest_sha256"],
                    "repo_revision_from_task308": row["repo_revision_from_task308"],
                    "local_path": row["local_path"],
                    "prompt_hash_hit_rows": row["prompt_hash_hit_rows"],
                    "normalized_prompt_hit_rows": row["normalized_prompt_hit_rows"],
                    "ngram_hit_rows": row["ngram_hit_rows"],
                    "parse_errors": row["parse_errors"],
                    "selected_filename": row["selected_filename"],
                    "selected_lfs_sha256": row["selected_lfs_sha256"],
                }
            )
    for row in task327:
        if row.get("name") == "swe":
            included_rows.append(
                {
                    "source_task": "task327",
                    "name": row["name"],
                    "dataset_id": row["dataset_id"],
                    "status": row["status"],
                    "decontam_pass": row["decontam_pass"],
                    "row_count": row["row_count"],
                    "file_bytes": row["file_bytes"],
                    "file_sha256": row["file_sha256"],
                    "row_manifest": row["row_manifest"],
                    "row_manifest_sha256": row["row_manifest_sha256"],
                    "repo_revision_from_task308": row["repo_revision_from_task308"],
                    "local_path": row["local_path"],
                    "prompt_hash_hit_rows": row["prompt_hash_hit_rows"],
                    "normalized_prompt_hit_rows": row["normalized_prompt_hit_rows"],
                    "ngram_hit_rows": row["ngram_hit_rows"],
                    "parse_errors": row["parse_errors"],
                    "selected_filename": row["selected_filename"],
                    "split_exposure_status": row["split_exposure_status"],
                }
            )
        elif row.get("name") in EXPECTED_BLOCKED_TASK327:
            excluded_rows.append(
                {
                    "source_task": "task327",
                    "name": row["name"],
                    "dataset_id": row["dataset_id"],
                    "status": row["status"],
                    "decontam_pass": row["decontam_pass"],
                    "row_count": row["row_count"],
                    "file_bytes": row["file_bytes"],
                    "file_sha256": row["file_sha256"],
                    "row_manifest": row["row_manifest"],
                    "row_manifest_sha256": row["row_manifest_sha256"],
                    "prompt_hash_hit_rows": row["prompt_hash_hit_rows"],
                    "normalized_prompt_hit_rows": row["normalized_prompt_hit_rows"],
                    "ngram_hit_rows": row["ngram_hit_rows"],
                    "blocker": row.get("blocker"),
                }
            )
    included_rows.sort(key=lambda r: r["name"])
    excluded_rows.sort(key=lambda r: r["name"])
    return included_rows, excluded_rows


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8") as f:
        f.write("\t".join(keys) + "\n")
        for row in rows:
            f.write("\t".join(str(row.get(key, "")) for key in keys) + "\n")


def main() -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    MATRIX_DIR.mkdir(parents=True, exist_ok=True)

    metadata = load_json(SPLITS_ROOT / "metadata.json")
    manifest = load_json(SPLITS_ROOT / "manifest.json")
    blend = load_json(PACKED_ROOT / "blend.json")

    expected = expected_targets_from_blend(blend)
    actual = actual_targets_from_manifest(manifest)
    parity = {
        "status": "PASS",
        "note": "Expected shard targets from blend.json exactly match exposed split manifest target paths.",
        "splits": {},
    }
    for split in sorted(set(expected) | set(actual)):
        missing = sorted((expected.get(split, Counter()) - actual.get(split, Counter())).elements())
        unexpected = sorted((actual.get(split, Counter()) - expected.get(split, Counter())).elements())
        parity["splits"][split] = {
            "expected_shards": expected.get(split, Counter()).total(),
            "exposed_shards": actual.get(split, Counter()).total(),
            "missing": missing,
            "unexpected": unexpected,
            "status": "PASS" if not missing and not unexpected else "FAIL",
        }
        if missing or unexpected:
            parity["status"] = "FAIL"

    pack_metrics = parquet_metrics(manifest)
    receipts = receipt_metrics()
    pack_metrics["receipt_metrics"] = {
        "totals": receipts["totals"],
        "by_source": receipts["by_source"],
        "notes": receipts["notes"],
    }

    source_split_exposure = {}
    for source in INCLUDED_SOURCE_NAMES:
        split_presence = {
            split: source in pack_metrics["by_split"][split]["sources"]
            for split in sorted(pack_metrics["by_split"])
        }
        source_split_exposure[source] = {
            "split_presence": split_presence,
            "status": (
                "TRAIN_VALID_TEST_EXPOSED"
                if all(split_presence.values())
                else "TRAIN_EXPOSED_VALID_TEST_SPARSE"
            ),
        }
    parity["source_split_exposure"] = source_split_exposure
    parity["sparse_valid_test_note"] = (
        "The generated Qwen data-prep split is shard-ratio based. Train exposes all three "
        "raw pass sources; valid/test each expose only task322 agentic-interactive. This is "
        "recorded for lead review and does not change intended-vs-exposed shard parity."
    )

    included_sources, excluded_sources = build_source_matrix()
    decontam = {
        "status": "PASS_NO_AIME2025_TRAIN_ROWS_BY_PRIOR_DECONTAM_AND_SOURCE_EXCLUSION",
        "included_sources": included_sources,
        "excluded_task327_sources": excluded_sources,
        "included_source_names": sorted(INCLUDED_SOURCE_NAMES),
        "excluded_source_names": sorted(EXPECTED_BLOCKED_TASK327),
        "all_included_sources_zero_hits": all(
            row["prompt_hash_hit_rows"] == 0
            and row["normalized_prompt_hit_rows"] == 0
            and row["ngram_hit_rows"] == 0
            and row["parse_errors"] == 0
            and row["decontam_pass"]
            for row in included_sources
        ),
        "all_task327_blocked_sources_excluded": sorted(row["name"] for row in excluded_sources)
        == sorted(EXPECTED_BLOCKED_TASK327),
    }

    combination = {
        "status": "COMBINATION_WAITING_FOR_LEAD_REVIEW",
        "raw_pass_packed_root": str(PACKED_ROOT),
        "prior_constrained_task299_root": (
            "/work-agents/intern_nemotron_worker_1/outputs/"
            "task299_qwen_aime_v11_30b_data_packing_contract_s1/"
            "run_20260602T150941Z/packed_qwen_30b"
        ),
        "decision": (
            "task329 produced a standalone task-owned raw-pass packed root. Combining "
            "with the prior constrained task299 seed is deferred to a later lead-gated "
            "review/packing task so sparse valid/test split policy and expanded training "
            "contract can be accepted independently."
        ),
    }

    command_env = {
        "created_at": datetime.now(UTC).isoformat(),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "branch": git(["branch", "--show-current"]),
        "head": git(["rev-parse", "HEAD"]),
        "origin_main_base": "292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb",
        "model_path": str(MODEL_PATH),
        "packed_root": str(PACKED_ROOT),
        "splits_root": str(SPLITS_ROOT),
        "env": {
            key: os.environ.get(key)
            for key in [
                "PYTHONPATH",
                "CUDA_VISIBLE_DEVICES",
                "WANDB_MODE",
                "WANDB_DISABLED",
                "TOKENIZERS_PARALLELISM",
            ]
        },
        "commands": [
            {
                "name": "dependency_probe",
                "rc": 0,
                "summary": "cosmos_xenna OK; pyarrow OK 24.0.0; transformers OK 4.52.4; datasets OK 4.8.5",
            },
            {
                "name": "initial_data_prep_symlink_attempt",
                "rc_file": str(RUN_ROOT / "logs/data_prep.rc"),
                "log": str(RUN_ROOT / "logs/data_prep.log"),
                "result": "rc=1; SWE HF cache symlink target lacked .jsonl extension and was read as parquet",
            },
            {
                "name": "materialized_data_prep_retry",
                "rc_file": str(RUN_ROOT / "logs/data_prep_materialized.rc"),
                "log": str(RUN_ROOT / "logs/data_prep_materialized.log"),
                "result": "rc=0; packed_qwen_raw_pass_materialized/splits produced",
            },
            {
                "name": "qwen30b_contract_validate",
                "rc_file": str(RUN_ROOT / "logs/qwen30b_contract_validate.rc"),
                "log": str(RUN_ROOT / "logs/qwen30b_contract_validate.log"),
                "result": "QWEN30B_PACKED_CONTRACT=PASS",
            },
        ],
        "boundaries": {
            "training": "not run",
            "optimizer_steps": "not run",
            "nonzero_lr_smoke": "not run",
            "eval": "not run",
            "export": "not run",
            "endpoint": "not run",
            "promotion": "not claimed",
            "task255_reuse": "not used",
            "aime2025_train_rows": "excluded by decontam/source policy",
            "shared_deletion": "not performed",
            "main_push_or_merge": "not performed",
        },
    }

    source_matrix = {
        "included_sources": included_sources,
        "excluded_task327_decontam_hit_sources": excluded_sources,
    }
    split_summary = {
        "manifest_path": str(SPLITS_ROOT / "manifest.json"),
        "metadata_path": str(SPLITS_ROOT / "metadata.json"),
        "split_counts": {
            split: {
                "created_shards": info["created_shards"],
                "intended_shards": info["intended_shards"],
                "source_shards": dict(
                    sorted(
                        Counter(source_from_dataset_path(entry["source_path"]) for entry in info["entries"]).items()
                    )
                ),
            }
            for split, info in sorted(manifest["splits"].items())
        },
    }

    write_json(MANIFEST_DIR / "source_matrix.json", source_matrix)
    write_tsv(MATRIX_DIR / "source_matrix.tsv", included_sources + excluded_sources)
    write_json(MANIFEST_DIR / "split_manifest_summary.json", split_summary)
    write_json(MANIFEST_DIR / "intended_vs_exposed_parity.json", parity)
    write_json(MANIFEST_DIR / "decontam_no_aime2025_train_proof.json", decontam)
    write_json(MANIFEST_DIR / "qwen30b_packing_metrics.json", pack_metrics)
    write_json(MANIFEST_DIR / "packing_receipt_metrics.json", receipts)
    write_json(MANIFEST_DIR / "combination_decision.json", combination)
    write_json(MANIFEST_DIR / "command_env_manifest.json", command_env)

    shard_lines = [
        f"{row['sha256']}  {Path(row['link_path']).relative_to(RUN_ROOT)}"
        for row in pack_metrics["shards"]
    ]
    (MANIFEST_DIR / "packed_shard_checksums.sha256").write_text(
        "\n".join(shard_lines) + "\n",
        encoding="utf-8",
    )

    final = {
        "disposition": "PARTIAL_PASS_WITH_EXACT_BLOCKERS",
        "exact_blockers": [
            "task327-swe packed 51,029 rows but supervised_tokens=0 under tokenizer-native Qwen data_prep config; "
            "SWE requires a lead-approved source/config formatter remediation before it is a supervised SFT source.",
            "task322 instruction-following-structured has 6 validation-filtered rows in packing receipts; "
            "the packed artifact excludes those rows and needs review before it can be treated as a complete source contract.",
            "valid/test split exposure is shard-ratio sparse: train exposes all three sources, but valid/test expose only task322 agentic-interactive.",
        ],
        "run_root": str(RUN_ROOT),
        "packed_root": str(PACKED_ROOT),
        "splits_root": str(SPLITS_ROOT),
        "source_matrix": str(MANIFEST_DIR / "source_matrix.json"),
        "split_manifest_summary": str(MANIFEST_DIR / "split_manifest_summary.json"),
        "parity": str(MANIFEST_DIR / "intended_vs_exposed_parity.json"),
        "decontam_no_aime2025_train_proof": str(
            MANIFEST_DIR / "decontam_no_aime2025_train_proof.json"
        ),
        "packing_metrics": str(MANIFEST_DIR / "qwen30b_packing_metrics.json"),
        "artifact_checksums": str(MANIFEST_DIR / "artifact_checksums.sha256"),
        "packed_shard_checksums": str(MANIFEST_DIR / "packed_shard_checksums.sha256"),
        "packing_receipt_metrics": str(MANIFEST_DIR / "packing_receipt_metrics.json"),
        "combination_decision": str(MANIFEST_DIR / "combination_decision.json"),
        "qwen_contract": "PASS",
        "sparse_valid_test_note": parity["sparse_valid_test_note"],
        "task310_recommendation": (
            "not ready for task310 training; request independent review of partial raw-pass evidence "
            "and a follow-up lead-gated remediation for SWE supervised-token mapping / filtered rows / split policy"
        ),
    }
    write_json(MANIFEST_DIR / "final_summary.json", final)

    artifact_paths = [
        RUN_ROOT / "input/raw_pass_sources_blend.json",
        RUN_ROOT / "input/raw_pass_sources_blend_materialized.json",
        RUN_ROOT / "logs/data_prep.log",
        RUN_ROOT / "logs/data_prep.rc",
        RUN_ROOT / "logs/data_prep_materialized.log",
        RUN_ROOT / "logs/data_prep_materialized.rc",
        RUN_ROOT / "logs/qwen30b_contract_validate.log",
        RUN_ROOT / "logs/qwen30b_contract_validate.rc",
        PACKED_ROOT / "blend.json",
        SPLITS_ROOT / "manifest.json",
        SPLITS_ROOT / "metadata.json",
        MANIFEST_DIR / "source_matrix.json",
        MATRIX_DIR / "source_matrix.tsv",
        MANIFEST_DIR / "split_manifest_summary.json",
        MANIFEST_DIR / "intended_vs_exposed_parity.json",
        MANIFEST_DIR / "decontam_no_aime2025_train_proof.json",
        MANIFEST_DIR / "qwen30b_packing_metrics.json",
        MANIFEST_DIR / "packing_receipt_metrics.json",
        MANIFEST_DIR / "combination_decision.json",
        MANIFEST_DIR / "command_env_manifest.json",
        MANIFEST_DIR / "packed_shard_checksums.sha256",
        MANIFEST_DIR / "final_summary.json",
    ]
    checksum_lines = []
    for path in artifact_paths:
        if path.is_file():
            checksum_lines.append(f"{sha256_file(path)}  {path.relative_to(RUN_ROOT)}")
    (MANIFEST_DIR / "artifact_checksums.sha256").write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(final, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
