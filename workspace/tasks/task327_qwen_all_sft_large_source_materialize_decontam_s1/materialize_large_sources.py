#!/usr/bin/env python3
"""Task-owned large-source materialize/count/decontam helper for task327."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from huggingface_hub import hf_hub_download


TASK322_SUMMARY = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task322_qwen_all_sft_raw_materialize_count_decontam_s1/"
    "run_20260603T203100Z/manifests/materialize_count_decontam_summary.json"
)
TASK246_HELDOUT = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/"
    "aime25_hmmt_math_heldout_decontam_corpus.jsonl"
)
TASK246_HASHES = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256"
)
TASK311_MMLU = Path(
    "/work-agents/intern_nemotron_worker_3/outputs/"
    "task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/input/"
    "mmlu_pro/mmlu_pro_test.jsonl"
)
TASK314_MMLU_TRANSITIONS = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/"
    "run_20260603T191500Z/mmlu_pro_row_transitions.jsonl"
)

WORD_RE = re.compile(r"[a-z0-9]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(extract_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(extract_strings(item))
    return strings


def run_capture(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def load_heldout() -> dict[str, Any]:
    prompt_hashes: set[str] = set()
    prompt_hash_rows = 0
    with TASK246_HASHES.open() as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                prompt_hashes.add(parts[0])
                prompt_hash_rows += 1

    prompts: list[dict[str, str]] = []
    with TASK246_HELDOUT.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            prompt = str(row.get("prompt", ""))
            prompt_id = str(row.get("id", row.get("source_id", len(prompts))))
            norm = normalize_text(prompt)
            prompts.append({"id": prompt_id, "prompt": prompt, "normalized": norm})

    ngram_to_ids: dict[tuple[str, ...], set[int]] = {}
    short_prompt_ids: list[int] = []
    for idx, item in enumerate(prompts):
        words = WORD_RE.findall(item["normalized"])
        if len(words) < 13:
            short_prompt_ids.append(idx)
            continue
        for pos in range(0, len(words) - 12):
            ngram_to_ids.setdefault(tuple(words[pos : pos + 13]), set()).add(idx)

    return {
        "prompt_hashes": prompt_hashes,
        "prompt_hash_rows": prompt_hash_rows,
        "prompts": prompts,
        "ngram_to_ids": ngram_to_ids,
        "short_prompt_ids": short_prompt_ids,
        "heldout_corpus_sha256": sha256_path(TASK246_HELDOUT),
        "heldout_prompt_hashes_sha256": sha256_path(TASK246_HASHES),
    }


def load_sources(summary_path: Path) -> list[dict[str, Any]]:
    rows = json.loads(summary_path.read_text())
    sources = []
    for row in rows:
        if row.get("included"):
            continue
        if row.get("status") != "EXCLUDED_SIZE_GT_1GB":
            continue
        sources.append(row)
    return sources


def detect_hits(strings: list[str], heldout: dict[str, Any]) -> tuple[bool, bool, bool]:
    prompt_hashes: set[str] = heldout["prompt_hashes"]
    prompts: list[dict[str, str]] = heldout["prompts"]
    ngram_to_ids: dict[tuple[str, ...], set[int]] = heldout["ngram_to_ids"]
    short_prompt_ids: list[int] = heldout["short_prompt_ids"]

    prompt_hash_hit = False
    normalized_prompt_hit = False
    ngram_hit = False

    for text in strings:
        raw = text.encode("utf-8", errors="ignore")
        stripped = text.strip().encode("utf-8", errors="ignore")
        if hashlib.sha256(raw).hexdigest() in prompt_hashes:
            prompt_hash_hit = True
        if stripped != raw and hashlib.sha256(stripped).hexdigest() in prompt_hashes:
            prompt_hash_hit = True

        norm = normalize_text(text)
        if not norm:
            continue
        candidate_prompt_ids: set[int] = set()
        words = WORD_RE.findall(norm)
        if len(words) >= 13:
            for pos in range(0, len(words) - 12):
                ids = ngram_to_ids.get(tuple(words[pos : pos + 13]))
                if ids:
                    ngram_hit = True
                    candidate_prompt_ids.update(ids)

        for idx in short_prompt_ids:
            candidate_prompt_ids.add(idx)

        for idx in candidate_prompt_ids:
            prompt_norm = prompts[idx]["normalized"]
            if prompt_norm and prompt_norm in norm:
                normalized_prompt_hit = True
                break

    return prompt_hash_hit, normalized_prompt_hit, ngram_hit


def write_results(output_root: Path, results: list[dict[str, Any]]) -> None:
    manifests = output_root / "manifests"
    matrices = output_root / "matrices"
    manifests.mkdir(parents=True, exist_ok=True)
    matrices.mkdir(parents=True, exist_ok=True)
    (manifests / "large_source_materialize_decontam_summary.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )

    fields = [
        "name",
        "status",
        "dataset_id",
        "repo_revision_from_task308",
        "selected_filename",
        "expected_bytes",
        "file_bytes",
        "expected_sha256",
        "file_sha256",
        "row_count",
        "parse_errors",
        "row_manifest_sha256",
        "prompt_hash_hit_rows",
        "normalized_prompt_hit_rows",
        "ngram_hit_rows",
        "split_exposure_status",
        "local_path",
        "blocker",
    ]
    lines = ["\t".join(fields)]
    for result in results:
        lines.append("\t".join(str(result.get(field, "")) for field in fields))
    (matrices / "large_source_materialize_decontam_matrix.tsv").write_text(
        "\n".join(lines) + "\n"
    )


def process_source(
    source: dict[str, Any],
    output_root: Path,
    hf_cache: Path,
    heldout: dict[str, Any],
) -> dict[str, Any]:
    name = source["name"]
    expected_sha = source["selected_lfs_sha256"]
    expected_bytes = int(source["selected_size"])
    result: dict[str, Any] = {
        "name": name,
        "status": "STARTED",
        "dataset_id": source["dataset_id"],
        "repo_revision_from_task308": source["repo_revision_from_task308"],
        "selected_filename": source["selected_filename"],
        "expected_bytes": expected_bytes,
        "expected_sha256": expected_sha,
        "started_at": utc_now(),
        "split_exposure_status": "RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW",
    }

    try:
        local_path = Path(
            hf_hub_download(
                repo_id=source["dataset_id"],
                filename=source["selected_filename"],
                revision=source["repo_revision_from_task308"],
                repo_type="dataset",
                cache_dir=str(hf_cache),
            )
        )
        result["local_path"] = str(local_path)
        result["file_bytes"] = local_path.stat().st_size
    except Exception as exc:  # pragma: no cover - evidence path
        result["status"] = "BLOCKED_DOWNLOAD"
        result["blocker"] = f"{type(exc).__name__}: {exc}"
        result["finished_at"] = utc_now()
        return result

    rows = 0
    parse_errors = 0
    prompt_hash_hit_rows = 0
    normalized_prompt_hit_rows = 0
    ngram_hit_rows = 0
    file_hash = hashlib.sha256()
    row_manifest = output_root / "row_manifests" / f"{name}.rows.tsv.gz"
    decontam_report = output_root / "decontam" / f"{name}.decontam.json"
    row_manifest.parent.mkdir(parents=True, exist_ok=True)
    decontam_report.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    offset = 0
    with local_path.open("rb") as src, gzip.open(row_manifest, "wt", encoding="utf-8") as manifest:
        manifest.write("source\trow_index\tbyte_start\tbyte_len\tline_sha256\tparse_ok\n")
        for raw_line in src:
            rows += 1
            byte_len = len(raw_line)
            file_hash.update(raw_line)
            row_hash = hashlib.sha256(raw_line.rstrip(b"\r\n")).hexdigest()
            parse_ok = True
            try:
                decoded = raw_line.decode("utf-8")
                parsed = json.loads(decoded)
            except Exception:
                parse_ok = False
                parsed = None
                parse_errors += 1
            manifest.write(f"{name}\t{rows}\t{offset}\t{byte_len}\t{row_hash}\t{int(parse_ok)}\n")
            offset += byte_len

            if parsed is not None:
                p_hit, norm_hit, n_hit = detect_hits(extract_strings(parsed), heldout)
                if p_hit:
                    prompt_hash_hit_rows += 1
                if norm_hit:
                    normalized_prompt_hit_rows += 1
                if n_hit:
                    ngram_hit_rows += 1

            if rows % 100000 == 0:
                elapsed = max(time.time() - start, 0.001)
                mib = offset / (1024 * 1024)
                print(
                    f"{utc_now()} PROGRESS {name} rows={rows} mib={mib:.1f} "
                    f"rate_mib_s={mib / elapsed:.2f}",
                    flush=True,
                )

    file_sha = file_hash.hexdigest()
    row_manifest_sha = sha256_path(row_manifest)
    result.update(
        {
            "finished_at": utc_now(),
            "file_sha256": file_sha,
            "row_count": rows,
            "parse_errors": parse_errors,
            "row_manifest": str(row_manifest),
            "row_manifest_sha256": row_manifest_sha,
            "prompt_hash_hit_rows": prompt_hash_hit_rows,
            "normalized_prompt_hit_rows": normalized_prompt_hit_rows,
            "ngram_hit_rows": ngram_hit_rows,
            "decontam_report": str(decontam_report),
            "decontam_pass": (
                prompt_hash_hit_rows == 0
                and normalized_prompt_hit_rows == 0
                and ngram_hit_rows == 0
            ),
        }
    )

    if result["file_bytes"] != expected_bytes:
        result["status"] = "BLOCKED_SIZE_MISMATCH"
        result["blocker"] = f"expected {expected_bytes}, got {result['file_bytes']}"
    elif file_sha != expected_sha:
        result["status"] = "BLOCKED_SHA_MISMATCH"
        result["blocker"] = f"expected {expected_sha}, got {file_sha}"
    elif parse_errors:
        result["status"] = "BLOCKED_PARSE_ERRORS"
        result["blocker"] = f"{parse_errors} JSON parse errors"
    elif not result["decontam_pass"]:
        result["status"] = "BLOCKED_DECONTAM_HIT"
        result["blocker"] = (
            f"hits prompt={prompt_hash_hit_rows} normalized={normalized_prompt_hit_rows} "
            f"ngram={ngram_hit_rows}"
        )
    else:
        result["status"] = "INCLUDED_PASS"

    decontam_report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--task322-summary", default=str(TASK322_SUMMARY))
    parser.add_argument("--source", action="append", help="optional source name filter")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    logs = output_root / "logs"
    resource = output_root / "resource"
    manifests = output_root / "manifests"
    for directory in [logs, resource, manifests]:
        directory.mkdir(parents=True, exist_ok=True)

    write_text(resource / "df_before.txt", run_capture(["df", "-h", str(output_root)])["stdout"])
    write_text(manifests / "command_env_manifest.json", json.dumps({
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "env": {
            key: os.environ.get(key, "")
            for key in ["HF_HOME", "HF_HUB_CACHE", "CUDA_VISIBLE_DEVICES", "PYTHONPATH"]
        },
        "started_at": utc_now(),
        "task322_summary": str(args.task322_summary),
        "task246_heldout": str(TASK246_HELDOUT),
        "task246_prompt_hashes": str(TASK246_HASHES),
        "task311_mmlu_reference": str(TASK311_MMLU),
        "task314_mmlu_transitions_reference": str(TASK314_MMLU_TRANSITIONS),
    }, indent=2, sort_keys=True) + "\n")

    sources = load_sources(Path(args.task322_summary))
    if args.source:
        selected = set(args.source)
        sources = [source for source in sources if source["name"] in selected]
    heldout = load_heldout()
    hf_cache = output_root / "hf_cache"
    results: list[dict[str, Any]] = []

    print(f"{utc_now()} START task327 sources={len(sources)} output_root={output_root}", flush=True)
    for source in sources:
        print(f"{utc_now()} SOURCE_START {source['name']}", flush=True)
        result = process_source(source, output_root, hf_cache, heldout)
        print(f"{utc_now()} SOURCE_DONE {source['name']} status={result.get('status')}", flush=True)
        results.append(result)
        write_results(output_root, results)

    write_text(resource / "df_after.txt", run_capture(["df", "-h", str(output_root)])["stdout"])
    write_text(resource / "du_output_root.txt", run_capture(["du", "-sh", str(output_root)])["stdout"])
    write_results(output_root, results)

    checksum_files = []
    for pattern in ["decontam/*.json", "manifests/*.json", "matrices/*.tsv", "row_manifests/*.gz", "resource/*.txt"]:
        checksum_files.extend(sorted(output_root.glob(pattern)))
    checksum_path = manifests / "artifact_checksums.sha256"
    with checksum_path.open("w") as f:
        for path in checksum_files:
            f.write(f"{sha256_path(path)}  {path}\n")

    statuses = {result.get("status") for result in results}
    if statuses == {"INCLUDED_PASS"} and len(results) == 10:
        disposition = "PASS_LARGE_SOURCE_MATERIALIZE_DECONTAM"
        rc = 0
    elif any(status == "INCLUDED_PASS" for status in statuses):
        disposition = "PARTIAL_PASS_WITH_EXACT_BLOCKERS"
        rc = 2
    else:
        disposition = "BLOCK_RESOURCE_OR_SAFETY"
        rc = 3

    final = {
        "disposition": disposition,
        "return_code": rc,
        "source_count": len(sources),
        "included_pass_count": sum(1 for result in results if result.get("status") == "INCLUDED_PASS"),
        "blocked_count": sum(1 for result in results if result.get("status") != "INCLUDED_PASS"),
        "finished_at": utc_now(),
    }
    (manifests / "final_disposition.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    print(f"{utc_now()} FINAL {json.dumps(final, sort_keys=True)}", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
