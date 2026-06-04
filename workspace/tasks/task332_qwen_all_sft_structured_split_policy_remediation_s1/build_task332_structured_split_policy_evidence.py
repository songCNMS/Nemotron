#!/usr/bin/env python3
"""Build task332 no-training structured-row and split-policy evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nemotron.data_prep.core.chat_template import validate_conversation


TASK_NAME = "task332_qwen_all_sft_structured_split_policy_remediation_s1"
TASK329_RUN_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task329_qwen_all_sft_raw_pass_split_pack_proof_s1/run_20260604T053349Z"
)
DEFAULT_OUTPUT_BASE = Path("/work-agents/intern_nemotron_worker_4/outputs") / TASK_NAME
POLICY_ID = "task332_per_source_shard_holdout_v1"
NUM_SHARDS = 16
VALID_SHARD = 14
TEST_SHARD = 15
TASK331_BRANCH = "origin/intern_nemotron_worker_2/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1"

RAW_SOURCES = {
    "agentic-interactive": TASK329_RUN_ROOT
    / "input/raw_pass_materialized/agentic_interactive.jsonl",
    "instruction-following-structured": TASK329_RUN_ROOT
    / "input/raw_pass_materialized/instruction_following_structured.jsonl",
    "swe": TASK329_RUN_ROOT / "input/raw_pass_materialized/swe_r2e_gym.jsonl",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def run_git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        return f"ERROR rc={proc.returncode}: {proc.stderr.strip()}"
    return proc.stdout.strip()


def run_gh_pr_search() -> Any:
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "all",
            "--search",
            "task331_qwen_all_sft_swe_supervised_formatter_unblock_s1",
            "--json",
            "number,state,headRefName,headRefOid,title,url",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        return {"rc": proc.returncode, "stderr": proc.stderr.strip(), "stdout": proc.stdout.strip()}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"rc": proc.returncode, "stdout": proc.stdout.strip()}


def count_marker_occurrences(messages: list[dict[str, Any]]) -> dict[str, int | bool | list[str]]:
    tool_call_occurrences = 0
    tools_header_occurrences = 0
    roles: list[str] = []
    char_count = 0
    for message in messages:
        role = message.get("role")
        if isinstance(role, str):
            roles.append(role)
        for field in ("content", "reasoning_content"):
            value = message.get(field)
            if isinstance(value, str):
                char_count += len(value)
                tool_call_occurrences += value.count("<tool_call>")
                tools_header_occurrences += value.count("# Tools")
    return {
        "content_char_count": char_count,
        "roles": roles,
        "tool_call_occurrences": tool_call_occurrences,
        "tools_header_occurrences": tools_header_occurrences,
        "has_tools_header": tools_header_occurrences > 0,
    }


def scan_source_rows(path: Path, *, validate_rows: bool) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    row_count = 0
    shard_row_counts: Counter[int] = Counter()
    invalid_rows: list[dict[str, Any]] = []
    with path.open("rb") as f:
        for row_index, raw_line in enumerate(f):
            if not raw_line.strip():
                continue
            row_count += 1
            shard_index = row_index % NUM_SHARDS
            shard_row_counts[shard_index] += 1
            if not validate_rows:
                continue
            record = json.loads(raw_line)
            messages = record.get("messages") or []
            tools = record.get("tools")
            is_valid, error_message = validate_conversation(messages, tools)
            if is_valid:
                continue
            markers = count_marker_occurrences(messages)
            invalid_rows.append(
                {
                    "disposition": "EXCLUDE_FAIL_CLOSED_FROM_SFT_UNLESS_SOURCE_FIXED_AND_REVALIDATED",
                    "error_message": error_message,
                    "row_index": row_index,
                    "row_line_sha256": sha256_bytes(raw_line.rstrip(b"\n")),
                    "shard_index": shard_index,
                    "source": "instruction-following-structured",
                    "uuid": record.get("uuid"),
                    "message_count": len(messages),
                    "tools_field_present": "tools" in record,
                    "tools_count": len(tools) if isinstance(tools, list) else 0,
                    **markers,
                }
            )
    summary = {
        "path": str(path),
        "sha256": sha256_file(path),
        "row_count": row_count,
        "row_modulus": NUM_SHARDS,
        "shard_row_counts": {f"shard_{k:06d}": shard_row_counts[k] for k in range(NUM_SHARDS)},
    }
    return summary, invalid_rows


def load_receipt_metrics() -> dict[str, Any]:
    receipt_metrics = load_json(TASK329_RUN_ROOT / "manifests/packing_receipt_metrics.json")
    by_source_shard: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for receipt in receipt_metrics["receipts"]:
        by_source_shard[receipt["raw_source"]][int(receipt["shard_index"])] = {
            "dataset_name": receipt["dataset_name"],
            "num_errors": receipt["num_errors"],
            "num_filtered": receipt["num_filtered"],
            "num_input_rows": receipt["num_input_rows"],
            "num_output_sequences": receipt["num_output_sequences"],
            "num_packed_sequences": receipt["num_packed_sequences"],
            "num_truncated_to_pack_size": receipt["num_truncated_to_pack_size"],
            "num_validation_errors": receipt["num_validation_errors"],
            "path": receipt["path"],
            "total_tokens": receipt["total_tokens"],
        }
    return {
        "by_source": receipt_metrics["by_source"],
        "totals": receipt_metrics["totals"],
        "by_source_shard": {
            source: {f"shard_{idx:06d}": value for idx, value in sorted(shards.items())}
            for source, shards in sorted(by_source_shard.items())
        },
    }


def parse_shard_index(path_value: str) -> int:
    match = re.search(r"shard_(\d{6})(?:\.parquet)?$", path_value)
    if not match:
        raise ValueError(f"Cannot parse shard index from {path_value}")
    return int(match.group(1))


def policy_split_for_shard(shard_index: int) -> str:
    if shard_index == VALID_SHARD:
        return "valid"
    if shard_index == TEST_SHARD:
        return "test"
    return "train"


def aggregate_policy_metrics(
    qwen_metrics: dict[str, Any],
    raw_summaries: dict[str, dict[str, Any]],
    invalid_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    invalid_by_source_shard: dict[str, Counter[int]] = defaultdict(Counter)
    for row in invalid_rows:
        invalid_by_source_shard[row["source"]][int(row["shard_index"])] += 1

    split_totals: dict[str, Any] = {
        split: {
            "bytes": 0,
            "input_tokens": 0,
            "packed_rows": 0,
            "raw_eligible_rows": 0,
            "raw_input_rows": 0,
            "raw_validation_excluded_rows": 0,
            "shards": 0,
            "supervised_tokens": 0,
            "sources": {},
        }
        for split in ("train", "valid", "test")
    }
    source_presence: dict[str, dict[str, bool]] = {
        source: {"train": False, "valid": False, "test": False} for source in RAW_SOURCES
    }

    for shard in qwen_metrics["shards"]:
        raw_source = shard["raw_source"]
        shard_index = parse_shard_index(shard["target_path"])
        split = policy_split_for_shard(shard_index)
        source_presence[raw_source][split] = True

        source_entry = split_totals[split]["sources"].setdefault(
            raw_source,
            {
                "bytes": 0,
                "input_tokens": 0,
                "packed_rows": 0,
                "raw_eligible_rows": 0,
                "raw_input_rows": 0,
                "raw_validation_excluded_rows": 0,
                "shards": 0,
                "supervised_tokens": 0,
            },
        )

        raw_rows = raw_summaries[raw_source]["shard_row_counts"][f"shard_{shard_index:06d}"]
        invalid_count = invalid_by_source_shard[raw_source][shard_index]
        values = {
            "bytes": shard["bytes"],
            "input_tokens": shard["input_tokens"],
            "packed_rows": shard["rows"],
            "raw_eligible_rows": raw_rows - invalid_count,
            "raw_input_rows": raw_rows,
            "raw_validation_excluded_rows": invalid_count,
            "shards": 1,
            "supervised_tokens": shard["supervised_tokens"],
        }
        for key, value in values.items():
            source_entry[key] += value
            split_totals[split][key] += value

    source_status = {}
    for source, presence in source_presence.items():
        status = "TRAIN_VALID_TEST_EXPOSED" if all(presence.values()) else "SPARSE"
        source_status[source] = {"split_presence": presence, "status": status}

    return {
        "policy_id": POLICY_ID,
        "policy": {
            "num_shards": NUM_SHARDS,
            "row_modulus": NUM_SHARDS,
            "train_remainders": [i for i in range(NUM_SHARDS) if i not in (VALID_SHARD, TEST_SHARD)],
            "valid_remainders": [VALID_SHARD],
            "test_remainders": [TEST_SHARD],
            "rule": (
                "For every included raw-pass source, shard rows by row_index % 16; "
                "assign remainder 14 to valid, remainder 15 to test, and all "
                "other remainders to train."
            ),
        },
        "status": "PASS_POLICY_DETERMINISTIC_NOT_APPLIED_TO_TASK329_ARTIFACTS",
        "source_split_exposure": source_status,
        "split_totals_if_relinked_from_task329_shards_after_structured_exclusion": split_totals,
        "swe_note": (
            "SWE would receive train/valid/test exposure under this policy, but "
            "current task329 SWE supervised_tokens remain 0; task331 must provide "
            "nonzero supervised-token remediation before a combined contract."
        ),
    }


def build_decontam_summary() -> dict[str, Any]:
    proof = load_json(TASK329_RUN_ROOT / "manifests/decontam_no_aime2025_train_proof.json")
    source_matrix = load_json(TASK329_RUN_ROOT / "manifests/source_matrix.json")
    return {
        "status": proof["status"],
        "all_included_sources_zero_hits": proof["all_included_sources_zero_hits"],
        "all_task327_blocked_sources_excluded": proof["all_task327_blocked_sources_excluded"],
        "included_source_names": proof["included_source_names"],
        "excluded_source_names": proof["excluded_source_names"],
        "excluded_source_count": len(proof["excluded_source_names"]),
        "source_matrix_included_zero_hit_check": [
            {
                "name": source["name"],
                "decontam_pass": source["decontam_pass"],
                "row_count": source["row_count"],
                "file_sha256": source["file_sha256"],
                "prompt_hash_hit_rows": source["prompt_hash_hit_rows"],
                "normalized_prompt_hit_rows": source["normalized_prompt_hit_rows"],
                "ngram_hit_rows": source["ngram_hit_rows"],
            }
            for source in source_matrix["included_sources"]
        ],
    }


def build_task331_dependency() -> dict[str, Any]:
    diff_name_status = run_git(["diff", "--name-status", "origin/main..." + TASK331_BRANCH])
    return {
        "branch": TASK331_BRANCH,
        "head": run_git(["rev-parse", TASK331_BRANCH]),
        "pr_search": run_gh_pr_search(),
        "visible_diff_name_status": diff_name_status.splitlines() if diff_name_status else [],
        "status": "PENDING_ACCEPTANCE_ONLY_NO_SWE_SUPERVISED_TOKEN_EVIDENCE_VISIBLE",
        "required_before_combined_contract": (
            "task331 must produce and pass review for SWE formatter/config evidence "
            "with nonzero Qwen supervised tokens before task310 or a combined all-SFT "
            "contract can proceed."
        ),
    }


def build_structured_summary(
    invalid_rows: list[dict[str, Any]],
    receipt_metrics: dict[str, Any],
) -> dict[str, Any]:
    invalid_by_shard = Counter(int(row["shard_index"]) for row in invalid_rows)
    receipt_structured = receipt_metrics["by_source"]["instruction-following-structured"]
    validation_error_shards = {}
    for shard_name, shard_metrics in receipt_metrics["by_source_shard"][
        "instruction-following-structured"
    ].items():
        if shard_metrics["num_validation_errors"]:
            validation_error_shards[shard_name] = shard_metrics
    return {
        "disposition": "PASS_STRUCTURED_ROWS_EXCLUDED_FAIL_CLOSED",
        "filtered_row_count": len(invalid_rows),
        "invalid_by_shard": {f"shard_{k:06d}": invalid_by_shard[k] for k in sorted(invalid_by_shard)},
        "receipt_structured_totals": receipt_structured,
        "receipt_validation_error_shards": validation_error_shards,
        "receipt_match": (
            receipt_structured["num_validation_errors"] == len(invalid_rows)
            and all(
                metrics["num_validation_errors"] == invalid_by_shard[int(shard_name.split("_")[1])]
                for shard_name, metrics in validation_error_shards.items()
            )
        ),
        "remediation_policy": (
            "Do not silently repair or include these rows in SFT. Exclude by "
            "exact source row hash/index unless a later source-remediation task "
            "adds the missing # Tools/tool schema context and re-runs the same "
            "validate_conversation check."
        ),
        "validation_function": "nemotron.data_prep.core.chat_template.validate_conversation",
    }


def build_command_env(run_root: Path, command: str) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": TASK_NAME,
        "cwd": os.getcwd(),
        "command": command,
        "output_root": str(run_root),
        "python": sys.version,
        "git_head": run_git(["rev-parse", "HEAD"]),
        "origin_main": run_git(["rev-parse", "origin/main"]),
        "task329_run_root": str(TASK329_RUN_ROOT),
        "boundaries": [
            "no training",
            "no optimizer steps",
            "no eval or benchmark rerun",
            "no export",
            "no endpoint",
            "no promotion",
            "no task255 reuse",
            "no AIME2025 prompt/label train rows",
            "no shared deletion",
            "no task329 artifact mutation",
            "no merge or main push",
        ],
    }


def write_checksums(run_root: Path, paths: list[Path]) -> None:
    checksum_path = run_root / "manifests/artifact_checksums.sha256"
    lines = []
    for path in sorted(paths):
        rel = path.relative_to(run_root)
        lines.append(f"{sha256_file(path)}  {rel.as_posix()}")
    checksum_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-base", default=str(DEFAULT_OUTPUT_BASE))
    args = parser.parse_args()

    run_root = Path(args.output_base) / args.run_id
    if run_root.exists():
        raise FileExistsError(f"output root already exists: {run_root}")
    manifests_dir = run_root / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=False)

    command = "PYTHONPATH=src python " + " ".join(sys.argv)
    raw_summaries: dict[str, dict[str, Any]] = {}
    invalid_rows: list[dict[str, Any]] = []
    for source, path in RAW_SOURCES.items():
        summary, source_invalid = scan_source_rows(
            path,
            validate_rows=(source == "instruction-following-structured"),
        )
        raw_summaries[source] = summary
        invalid_rows.extend(source_invalid)
    invalid_rows = sorted(invalid_rows, key=lambda row: (row["shard_index"], row["row_index"]))

    receipt_metrics = load_receipt_metrics()
    qwen_metrics = load_json(TASK329_RUN_ROOT / "manifests/qwen30b_packing_metrics.json")
    current_parity = load_json(TASK329_RUN_ROOT / "manifests/intended_vs_exposed_parity.json")
    split_summary = load_json(TASK329_RUN_ROOT / "manifests/split_manifest_summary.json")

    structured_summary = build_structured_summary(invalid_rows, receipt_metrics)
    split_policy = aggregate_policy_metrics(qwen_metrics, raw_summaries, invalid_rows)
    decontam_summary = build_decontam_summary()
    task331_dependency = build_task331_dependency()

    exposed_manifest = {
        "current_task329_exposure": {
            "source_split_exposure": current_parity["source_split_exposure"],
            "split_counts": split_summary["split_counts"],
            "status": "CURRENT_TASK329_SPARSE_VALID_TEST_EXPOSURE",
        },
        "proposed_task332_policy": split_policy,
        "status": "PASS_INTENDED_POLICY_EVIDENCED_NOT_APPLIED",
    }

    final_summary = {
        "disposition": "PASS_SPLIT_POLICY_READY_WITH_SWE_PENDING",
        "output_root": str(run_root),
        "task329_run_root": str(TASK329_RUN_ROOT),
        "structured_rows": structured_summary,
        "split_policy_status": split_policy["status"],
        "decontam_no_aime2025_train_status": decontam_summary["status"],
        "task331_dependency_status": task331_dependency["status"],
        "not_a_release": (
            "This is no-training remediation evidence only. It does not release "
            "task310, benchmark eval, export, endpoint, or promotion."
        ),
    }

    row_path = manifests_dir / "structured_filtered_rows.jsonl"
    with row_path.open("w") as f:
        for row in invalid_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    outputs = [
        row_path,
        manifests_dir / "raw_source_checksums_and_counts.json",
        manifests_dir / "structured_filtered_rows_summary.json",
        manifests_dir / "split_policy.json",
        manifests_dir / "proposed_intended_vs_exposed_manifest.json",
        manifests_dir / "decontam_no_aime2025_train_proof.json",
        manifests_dir / "task331_dependency.json",
        manifests_dir / "command_env_manifest.json",
        manifests_dir / "final_summary.json",
    ]
    write_json(outputs[1], raw_summaries)
    write_json(outputs[2], structured_summary)
    write_json(outputs[3], split_policy)
    write_json(outputs[4], exposed_manifest)
    write_json(outputs[5], decontam_summary)
    write_json(outputs[6], task331_dependency)
    write_json(outputs[7], build_command_env(run_root, command))
    write_json(outputs[8], final_summary)
    write_checksums(run_root, outputs)

    print(json.dumps(final_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
