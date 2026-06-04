#!/usr/bin/env python3
"""Build task328 post-task327 packed-contract preflight evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK322_SUMMARY = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task322_qwen_all_sft_raw_materialize_count_decontam_s1/"
    "run_20260603T203100Z/manifests/materialize_count_decontam_summary.json"
)
TASK327_SUMMARY = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task327_qwen_all_sft_large_source_materialize_decontam_s1/"
    "run_20260603T211508Z/manifests/large_source_materialize_decontam_summary.json"
)
TASK327_FINAL = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task327_qwen_all_sft_large_source_materialize_decontam_s1/"
    "run_20260603T211508Z/manifests/final_disposition.json"
)
TASK276_EVIDENCE = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task276_qwen_aime_v11_rematerialize_packed_qwen_s1/"
    "run_20260602T034648Z/evidence/packed_qwen_evidence_manifest.json"
)
TASK299_ROOT = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task299_qwen_aime_v11_30b_data_packing_contract_s1/"
    "run_20260602T150941Z"
)
TASK299_PACKED_ROOT = TASK299_ROOT / "packed_qwen_30b"
QWEN30B_MODEL = Path("/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507")
TASK327_PR_HEAD = "49c5d748c8c9ecc95d21c69a1bd16af0118cba3d"
ORIGIN_MAIN = "292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb"
PRODUCT_CODE_BASELINE = "ecb14173a820df377270273b9f7d9d92cb5076d2"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_capture(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def source_decision_for_raw_pass(source: dict[str, Any], upstream: str) -> dict[str, Any]:
    split_status = source.get("split_exposure_status") or "NO_ACCEPTED_SPLIT_EXPOSURE_PROOF"
    qwen_status = "NO_QWEN30B_PACKED_SUPERVISED_TOKEN_PROOF_FOR_RAW_SOURCE"
    return {
        "source": source["name"],
        "evidence": upstream,
        "upstream_status": source.get("status", ""),
        "decision": "EXCLUDE_FROM_TASK328_PACKED_CONTRACT",
        "blocker": "accepted raw decontam pass, but split exposure/parity and Qwen30B supervised-token packing proof are missing",
        "rows": source.get("row_count", ""),
        "parse_errors": source.get("parse_errors", ""),
        "file_sha256": source.get("file_sha256", source.get("selected_lfs_sha256", "")),
        "row_manifest_sha256": source.get("row_manifest_sha256", ""),
        "prompt_hash_hit_rows": source.get("prompt_hash_hit_rows", 0),
        "normalized_prompt_hit_rows": source.get("normalized_prompt_hit_rows", 0),
        "ngram_hit_rows": source.get("ngram_hit_rows", 0),
        "split_exposure_status": split_status,
        "qwen_pack_status": qwen_status,
        "path": source.get("local_path", ""),
    }


def source_decision_for_blocked(source: dict[str, Any], upstream: str) -> dict[str, Any]:
    return {
        "source": source["name"],
        "evidence": upstream,
        "upstream_status": source.get("status", ""),
        "decision": "EXCLUDE_DECONTAM_FAIL_CLOSED",
        "blocker": source.get("blocker", "heldout decontam hit"),
        "rows": source.get("row_count", ""),
        "parse_errors": source.get("parse_errors", ""),
        "file_sha256": source.get("file_sha256", source.get("selected_lfs_sha256", "")),
        "row_manifest_sha256": source.get("row_manifest_sha256", ""),
        "prompt_hash_hit_rows": source.get("prompt_hash_hit_rows", 0),
        "normalized_prompt_hit_rows": source.get("normalized_prompt_hit_rows", 0),
        "ngram_hit_rows": source.get("ngram_hit_rows", 0),
        "split_exposure_status": source.get("split_exposure_status", ""),
        "qwen_pack_status": "NOT_EVALUATED_DECONTAM_BLOCKED",
        "path": source.get("local_path", ""),
    }


def task299_seed_row() -> dict[str, Any]:
    evidence = read_json(TASK276_EVIDENCE)
    split_counts = evidence["split_counts"]
    return {
        "source": "constrained-v11-task299-packed-seed",
        "evidence": "task299/task276/task309 accepted packed evidence",
        "upstream_status": "PASS_30B_DATA_PACKING_CONTRACT",
        "decision": "CARRY_FORWARD_SAFE_CONSTRAINED_PACKED_SEED_ONLY",
        "blocker": "none for constrained seed; not a post-task327 raw-source expansion",
        "rows": split_counts["train"]["rows"] + split_counts["valid"]["rows"] + split_counts["test"]["rows"],
        "parse_errors": 0,
        "file_sha256": sha256_path(TASK299_ROOT / "manifest.json"),
        "row_manifest_sha256": sha256_path(TASK299_ROOT / "packed_qwen_30b_shard_checksums.json"),
        "prompt_hash_hit_rows": 0,
        "normalized_prompt_hit_rows": 0,
        "ngram_hit_rows": 0,
        "split_exposure_status": "PASS_INTENDED_VS_EXPOSED_PARITY",
        "qwen_pack_status": "PASS_QWEN30B_PACKED_CONTRACT",
        "path": str(TASK299_PACKED_ROOT),
    }


def write_matrix(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "source",
        "evidence",
        "upstream_status",
        "decision",
        "blocker",
        "rows",
        "parse_errors",
        "file_sha256",
        "row_manifest_sha256",
        "prompt_hash_hit_rows",
        "normalized_prompt_hit_rows",
        "ngram_hit_rows",
        "split_exposure_status",
        "qwen_pack_status",
        "path",
    ]
    lines = ["\t".join(fields)]
    for row in rows:
        lines.append("\t".join(str(row.get(field, "")) for field in fields))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()

    output_root = Path(args.output_root)
    manifests = output_root / "manifests"
    matrices = output_root / "matrices"
    logs = output_root / "logs"
    for directory in [manifests, matrices, logs]:
        directory.mkdir(parents=True, exist_ok=True)

    command_env = {
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "env": {
            key: os.environ.get(key, "")
            for key in ["CUDA_VISIBLE_DEVICES", "HF_HOME", "HF_HUB_CACHE", "PYTHONPATH"]
        },
        "host": run_capture(["hostname"]),
        "started_at": utc_now(),
        "origin_main": ORIGIN_MAIN,
        "product_code_baseline": PRODUCT_CODE_BASELINE,
        "qwen30b_model": str(QWEN30B_MODEL),
        "task322_summary": str(TASK322_SUMMARY),
        "task327_summary": str(TASK327_SUMMARY),
        "task327_pr_head": TASK327_PR_HEAD,
        "task327_pr_view": run_capture([
            "gh",
            "pr",
            "view",
            "390",
            "--json",
            "number,state,headRefOid,mergeable,isDraft,url,baseRefName",
        ]),
    }
    write_json(logs / "command_env.json", command_env)

    rows: list[dict[str, Any]] = [task299_seed_row()]
    task322 = read_json(TASK322_SUMMARY)
    task327 = read_json(TASK327_SUMMARY)
    task327_final = read_json(TASK327_FINAL)

    for source in task322:
        if source.get("status") == "INCLUDED_PASS":
            rows.append(source_decision_for_raw_pass(source, "task322/#388"))

    for source in task327:
        if source.get("status") == "INCLUDED_PASS":
            rows.append(source_decision_for_raw_pass(source, "task327/#390"))
        elif source.get("status") == "BLOCKED_DECONTAM_HIT":
            rows.append(source_decision_for_blocked(source, "task327/#390"))

    matrix_path = matrices / "source_inclusion_matrix.tsv"
    write_matrix(matrix_path, rows)

    task276_evidence = read_json(TASK276_EVIDENCE)
    final = {
        "disposition": "PARTIAL_PASS_WITH_EXACT_BLOCKERS",
        "return_code": 2,
        "created_at": utc_now(),
        "packed_root_produced_by_task328": None,
        "carried_forward_safe_packed_root": str(TASK299_PACKED_ROOT),
        "target_model": str(QWEN30B_MODEL),
        "safe_constrained_seed": {
            "train_rows": task276_evidence["split_counts"]["train"]["rows"],
            "valid_rows": task276_evidence["split_counts"]["valid"]["rows"],
            "test_rows": task276_evidence["split_counts"]["test"]["rows"],
            "train_shards": task276_evidence["split_counts"]["train"]["exposed_shards"],
            "valid_shards": task276_evidence["split_counts"]["valid"]["exposed_shards"],
            "test_shards": task276_evidence["split_counts"]["test"]["exposed_shards"],
            "train_input_tokens": task276_evidence["split_counts"]["train"]["input_tokens"],
            "train_supervised_tokens": task276_evidence["split_counts"]["train"]["supervised_tokens"],
            "qwen_contract": task276_evidence["qwen_chat_contract"]["status"],
            "no_aime2025_train_leakage": task276_evidence["no_aime2025_train_leakage_decision"]["status"],
        },
        "raw_pass_sources_blocked_before_packing": [
            row["source"]
            for row in rows
            if row["decision"] == "EXCLUDE_FROM_TASK328_PACKED_CONTRACT"
        ],
        "decontam_blocked_sources_excluded": [
            row["source"] for row in rows if row["decision"] == "EXCLUDE_DECONTAM_FAIL_CLOSED"
        ],
        "task327_final_disposition": task327_final,
        "blocker": (
            "post-task327 all-eligible packed contract cannot safely include the "
            "new raw pass sources because accepted split exposure/parity and "
            "Qwen30B supervised-token packing proof are missing; nine task327 "
            "sources are decontam-blocked and excluded"
        ),
        "task310_recommendation": (
            "NO_GO_FOR_EXPANDED_POST_TASK327_ALL_SFT; only the prior constrained "
            "task299 seed remains carry-forward evidence pending lead decision"
        ),
        "boundaries": {
            "packed_by_task328": False,
            "training": False,
            "optimizer_steps": False,
            "benchmark_eval": False,
            "export": False,
            "endpoint": False,
            "promotion": False,
            "task255_reuse": False,
            "aime2025_train_rows": False,
            "shared_deletion_or_mutation": False,
            "main_push_or_merge": False,
        },
    }
    write_json(manifests / "final_disposition.json", final)

    preflight = {
        "schema_version": 1,
        "task": "task328_qwen_all_sft_post_task327_packed_contract_s1",
        "source_matrix": str(matrix_path),
        "source_count": len(rows),
        "raw_pass_blocked_before_packing_count": len(final["raw_pass_sources_blocked_before_packing"]),
        "decontam_blocked_count": len(final["decontam_blocked_sources_excluded"]),
        "safe_constrained_seed_count": 1,
        "final_disposition": final,
        "task299_artifact_hashes": {
            "manifest.json": sha256_path(TASK299_ROOT / "manifest.json"),
            "contract_validation.json": sha256_path(TASK299_ROOT / "contract_validation.json"),
            "split_counts_parity.json": sha256_path(TASK299_ROOT / "split_counts_parity.json"),
            "decontam_proof.json": sha256_path(TASK299_ROOT / "decontam_proof.json"),
            "tokenizer_chat_template_equivalence_probe.json": sha256_path(
                TASK299_ROOT / "tokenizer_chat_template_equivalence_probe.json"
            ),
            "packed_qwen_30b_shard_checksums.json": sha256_path(
                TASK299_ROOT / "packed_qwen_30b_shard_checksums.json"
            ),
        },
        "input_hashes": {
            "task322_summary": sha256_path(TASK322_SUMMARY),
            "task327_summary": sha256_path(TASK327_SUMMARY),
            "task327_final": sha256_path(TASK327_FINAL),
            "task276_evidence": sha256_path(TASK276_EVIDENCE),
        },
    }
    write_json(manifests / "post_task327_packed_contract_preflight.json", preflight)

    checksum_files: list[Path] = []
    for pattern in ["logs/*.json", "manifests/*.json", "matrices/*.tsv"]:
        checksum_files.extend(sorted(output_root.glob(pattern)))
    checksum_path = manifests / "artifact_checksums.sha256"
    with checksum_path.open("w") as f:
        for path in checksum_files:
            if path == checksum_path:
                continue
            f.write(f"{sha256_path(path)}  {path}\n")

    print(json.dumps(final, indent=2, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
