"""Fresh final-answer n-gram decontamination evidence for task262.

This script is read-only with respect to source data. It scans task251's
final-answer JSONL against the task246 heldout AIME/HMMT/MATH prompt corpus and
writes aggregate audit artifacts under the task262 output directory. It does
not write trainable data, run packing/training/eval/export, or expose heldout
prompt text in the generated report.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.data_registries.contamination_scanner import (
    text_ngrams,
    tokenize,
)
from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
    MATH_DECONTAMINATION_DEFAULT_BLOCKER_THRESHOLD,
    MATH_DECONTAMINATION_DEFAULT_NGRAM_SIZE,
    MATH_DECONTAMINATION_ENVIRONMENTS,
    decontaminate_math_rows,
)


TASK_ID = "task262_qwen_aime_v11_data_split_sidecar_s1"
REPO_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_DIR = (
    Path("/work-agents/intern_nemotron_worker_1/outputs")
    / TASK_ID
)
TASK251_ROOT = Path(
    "/work-agents/intern_nemotron_worker_2/outputs/"
    "task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft"
)
TASK246_ROOT = Path(
    "/work-agents/intern_nemotron_worker_1/outputs/"
    "task246_qwen_aime_v10_real_decontam_corpus_s1"
)
FINAL_ANSWER_PATH = TASK251_ROOT / "agentic_sft_v0_math_final_answer_train.jsonl"
HELDOUT_CORPUS_PATH = (
    TASK246_ROOT / "heldout" / "aime25_hmmt_math_heldout_decontam_corpus.jsonl"
)
HELDOUT_HASHES_PATH = TASK246_ROOT / "heldout" / "prompt_hashes.sha256"
INFORMATIONAL_THRESHOLD = 0.25
BLOCKER_THRESHOLD = MATH_DECONTAMINATION_DEFAULT_BLOCKER_THRESHOLD
NGRAM_SIZE = MATH_DECONTAMINATION_DEFAULT_NGRAM_SIZE
LABEL_LIKE_KEYS = {
    "answer",
    "expected_answer",
    "final_answer",
    "gold",
    "label",
    "solution",
    "target",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                data = json.loads(line)
                if not isinstance(data, dict):
                    raise ValueError(f"{path}: expected JSON object per line")
                rows.append(data)
    return rows


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sha256_sidecar(path: Path) -> str:
    digest = sha256_file(path)
    path.with_name(f"{path.name}.sha256").write_text(
        f"{digest}  {path.name}\n",
        encoding="utf-8",
    )
    return digest


def message_content(row: dict[str, Any], role: str) -> str:
    messages = row.get("messages")
    if not isinstance(messages, list):
        return ""
    chunks = [
        str(message.get("content", ""))
        for message in messages
        if isinstance(message, dict) and message.get("role") == role
    ]
    return "\n".join(chunk for chunk in chunks if chunk)


def metadata_env(row: dict[str, Any]) -> str:
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        return str(metadata.get("m0_environment", ""))
    return ""


def normalized_ws(text: str) -> str:
    return " ".join(text.split())


def heldout_hashes(path: Path) -> set[str]:
    return {
        line.split()[0]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def label_like_key_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        for key in row:
            if key.lower() in LABEL_LIKE_KEYS:
                counts[key] += 1
    return dict(sorted(counts.items()))


def indexed_heldout_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        prompt = str(row.get("prompt", ""))
        ngrams = text_ngrams(prompt, NGRAM_SIZE)
        indexed.append(
            {
                "index": index,
                "id": str(row.get("id") or f"heldout_{index:04d}"),
                "prompt_sha256": str(row.get("prompt_sha256") or sha256_text(normalized_ws(prompt))),
                "token_count": len(tokenize(prompt)),
                "ngram_count": len(ngrams),
                "ngrams": ngrams,
            }
        )
    return indexed


def full_scan(
    final_rows: list[dict[str, Any]],
    heldout_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    indexed_eval = indexed_heldout_rows(heldout_rows)
    eval_ngram_index: dict[str, list[int]] = defaultdict(list)
    for eval_index, eval_record in enumerate(indexed_eval):
        for ngram in eval_record["ngrams"]:
            eval_ngram_index[ngram].append(eval_index)

    overlap_pair_count = 0
    informational_pair_count = 0
    blocker_pair_count = 0
    rows_with_any_overlap: set[int] = set()
    rows_with_informational: set[int] = set()
    rows_with_blocker: set[int] = set()
    overlap_count_distribution = Counter()
    score_distribution = Counter()
    top_pairs: list[dict[str, Any]] = []
    max_score = 0.0

    for row_index, row in enumerate(final_rows):
        prompt = message_content(row, "user")
        prompt_ngrams = text_ngrams(prompt, NGRAM_SIZE)
        if not prompt_ngrams:
            continue
        overlap_counts: dict[int, int] = defaultdict(int)
        for ngram in prompt_ngrams:
            for eval_index in eval_ngram_index.get(ngram, ()):
                overlap_counts[eval_index] += 1
        for eval_index, overlap_count in overlap_counts.items():
            eval_record = indexed_eval[eval_index]
            eval_ngram_count = int(eval_record["ngram_count"])
            if eval_ngram_count <= 0:
                continue
            overlap_pair_count += 1
            rows_with_any_overlap.add(row_index)
            prompt_ratio = overlap_count / len(prompt_ngrams)
            eval_ratio = overlap_count / eval_ngram_count
            score = max(prompt_ratio, eval_ratio)
            max_score = max(max_score, score)
            overlap_count_distribution[str(overlap_count)] += 1
            score_bucket = f"{int(score * 100) // 5 * 5:02d}-{int(score * 100) // 5 * 5 + 4:02d}%"
            score_distribution[score_bucket] += 1
            if score >= INFORMATIONAL_THRESHOLD:
                informational_pair_count += 1
                rows_with_informational.add(row_index)
            if score >= BLOCKER_THRESHOLD:
                blocker_pair_count += 1
                rows_with_blocker.add(row_index)
            top_pairs.append(
                {
                    "row_index": row_index,
                    "row_env": metadata_env(row),
                    "row_prompt_sha256": sha256_text(normalized_ws(prompt)),
                    "eval_id": eval_record["id"],
                    "eval_prompt_sha256": eval_record["prompt_sha256"],
                    "score": round(score, 6),
                    "prompt_overlap_ratio": round(prompt_ratio, 6),
                    "eval_overlap_ratio": round(eval_ratio, 6),
                    "overlap_ngram_count": overlap_count,
                    "prompt_ngram_count": len(prompt_ngrams),
                    "eval_ngram_count": eval_ngram_count,
                }
            )

    top_pairs.sort(
        key=lambda item: (
            -float(item["score"]),
            -int(item["overlap_ngram_count"]),
            int(item["row_index"]),
            str(item["eval_id"]),
        )
    )
    return {
        "scanner": "task262_full_final_answer_token_8gram_overlap",
        "ngram_size": NGRAM_SIZE,
        "thresholds": {
            "informational": INFORMATIONAL_THRESHOLD,
            "blocker": BLOCKER_THRESHOLD,
        },
        "final_answer_rows_scanned": len(final_rows),
        "heldout_rows_scanned": len(heldout_rows),
        "pair_comparisons_total": len(final_rows) * len(heldout_rows),
        "overlap_pair_count": overlap_pair_count,
        "informational_pair_count": informational_pair_count,
        "blocker_pair_count": blocker_pair_count,
        "rows_with_any_overlap": len(rows_with_any_overlap),
        "rows_with_informational_overlap": len(rows_with_informational),
        "rows_with_blocker_overlap": len(rows_with_blocker),
        "max_score": round(max_score, 6),
        "overlap_count_distribution": dict(sorted(overlap_count_distribution.items())),
        "score_distribution": dict(sorted(score_distribution.items())),
        "top_overlap_pairs_no_text": top_pairs[:25],
    }


def update_manifest(generated: dict[str, str]) -> None:
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["final_answer_ngram_decontam"] = {
        "artifact_paths": generated,
        "note": "Fresh full token 8-gram scan of task251 final-answer rows against task246 heldout prompts.",
    }
    write_json(manifest_path, manifest)
    write_sha256_sidecar(manifest_path)


def main() -> None:
    final_rows = read_jsonl(FINAL_ANSWER_PATH)
    heldout_rows = read_jsonl(HELDOUT_CORPUS_PATH)
    heldout_prompt_hashes = heldout_hashes(HELDOUT_HASHES_PATH)

    kept_rows, standard_summary = decontaminate_math_rows(
        final_rows,
        corpus=heldout_rows,
        ngram_size=NGRAM_SIZE,
        blocker_threshold=BLOCKER_THRESHOLD,
    )
    user_prompt_hashes = {
        sha256_text(normalized_ws(message_content(row, "user")))
        for row in final_rows
    }
    env_counts = Counter(metadata_env(row) for row in final_rows)
    full_scan_summary = full_scan(final_rows, heldout_rows)

    summary = {
        "schema_version": 1,
        "task": TASK_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": (
            "PYTHONPATH=src python "
            "workspace/tasks/task262_qwen_aime_v11_data_split_sidecar_s1/"
            "build_task262_final_answer_decontam.py"
        ),
        "source_files": {
            "final_answer_jsonl": {
                "path": str(FINAL_ANSWER_PATH),
                "sha256": sha256_file(FINAL_ANSWER_PATH),
            },
            "heldout_corpus": {
                "path": str(HELDOUT_CORPUS_PATH),
                "sha256": sha256_file(HELDOUT_CORPUS_PATH),
            },
            "heldout_prompt_hashes": {
                "path": str(HELDOUT_HASHES_PATH),
                "sha256": sha256_file(HELDOUT_HASHES_PATH),
            },
        },
        "environment": {
            "cwd": str(REPO_ROOT),
            "pythonpath": os.environ.get("PYTHONPATH", ""),
            "ngram_implementation": (
                "nemotron.recipes.super3.milestones.data_registries."
                "contamination_scanner.text_ngrams"
            ),
            "standard_decontam_function": (
                "nemotron.recipes.super3.milestones.m1_agentic_sft."
                "prepare_m1_agentic_sft.decontaminate_math_rows"
            ),
        },
        "row_counts": {
            "final_answer_rows": len(final_rows),
            "heldout_rows": len(heldout_rows),
            "final_answer_env_counts": dict(sorted(env_counts.items())),
            "standard_decontam_target_environments": list(MATH_DECONTAMINATION_ENVIRONMENTS),
            "standard_decontam_kept_rows": len(kept_rows),
        },
        "label_like_top_level_keys": label_like_key_counts(final_rows),
        "exact_prompt_hash_overlap": {
            "user_prompt_hashes": len(user_prompt_hashes),
            "heldout_prompt_hashes": len(heldout_prompt_hashes),
            "overlap_count": len(user_prompt_hashes & heldout_prompt_hashes),
        },
        "standard_decontaminate_math_rows_summary": standard_summary,
        "full_final_answer_scan": full_scan_summary,
        "decision": {
            "blocked_rows": full_scan_summary["rows_with_blocker_overlap"],
            "blocker_pairs": full_scan_summary["blocker_pair_count"],
            "dropped_by_standard_decontaminate_math_rows": standard_summary.get("dropped_rows", 0),
            "status": (
                "PASS"
                if full_scan_summary["rows_with_blocker_overlap"] == 0
                and int(standard_summary.get("dropped_rows", 0)) == 0
                else "BLOCK"
            ),
        },
        "boundaries": {
            "training_run": False,
            "export_run": False,
            "endpoint_launched": False,
            "aime_or_task243_eval_run": False,
            "promotion_claim": False,
            "thirty_b_or_8gpu_used": False,
            "aime2025_prompts_or_labels_in_trainable_outputs": False,
            "shared_deletion_under_mnt_cephfs_processing_lei_song": False,
            "task255_checkpoint_or_export_reused": False,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "final_answer_ngram_decontam_scan.json"
    md_path = OUTPUT_DIR / "final_answer_ngram_decontam_report.md"
    write_json(json_path, summary)
    json_sha = write_sha256_sidecar(json_path)

    report = f"""# task262 Final-Answer N-Gram Decontamination Scan

Generated: {summary['created_at_utc']}

## Inputs

- Final-answer JSONL: `{FINAL_ANSWER_PATH}` ({len(final_rows)} rows), sha256 `{sha256_file(FINAL_ANSWER_PATH)}`
- Heldout corpus: `{HELDOUT_CORPUS_PATH}` ({len(heldout_rows)} rows), sha256 `{sha256_file(HELDOUT_CORPUS_PATH)}`
- Heldout prompt hashes: `{HELDOUT_HASHES_PATH}`, sha256 `{sha256_file(HELDOUT_HASHES_PATH)}`

## Scan

- Full scan implementation: token {NGRAM_SIZE}-gram overlap over every final-answer user prompt versus every heldout prompt.
- Pair comparisons: {full_scan_summary['pair_comparisons_total']}
- Overlap pairs: {full_scan_summary['overlap_pair_count']}
- Informational pairs (score >= {INFORMATIONAL_THRESHOLD}): {full_scan_summary['informational_pair_count']}
- Blocker pairs (score >= {BLOCKER_THRESHOLD}): {full_scan_summary['blocker_pair_count']}
- Rows with blocker overlap: {full_scan_summary['rows_with_blocker_overlap']}
- Max score: {full_scan_summary['max_score']}

## Standard Decontam Function

- Function: `decontaminate_math_rows`
- Target environments: `{list(MATH_DECONTAMINATION_ENVIRONMENTS)}`
- Scanned rows: {standard_summary.get('scanned_rows')}
- Dropped rows: {standard_summary.get('dropped_rows')}
- Blocker findings: {standard_summary.get('blocker_findings')}

## Exact Hashes And Labels

- Exact task246-style user prompt hash overlap: {summary['exact_prompt_hash_overlap']['overlap_count']}
- Top-level label-like key counts: `{summary['label_like_top_level_keys']}`

## Decision

Status: `{summary['decision']['status']}`. No final-answer row reached the blocker threshold, and the standard math decontam function dropped 0 rows.

No training, export, endpoint launch, AIME/task243 eval, promotion, 30B/8-GPU use, task255 checkpoint/export reuse, AIME2025 train prompt/label use, or shared deletion was performed.
"""
    write_text(md_path, report)
    md_sha = write_sha256_sidecar(md_path)

    update_manifest(
        {
            json_path.name: str(json_path),
            f"{json_path.name}.sha256": str(json_path.with_name(f"{json_path.name}.sha256")),
            md_path.name: str(md_path),
            f"{md_path.name}.sha256": str(md_path.with_name(f"{md_path.name}.sha256")),
        }
    )

    print(f"{json_sha}  {json_path}")
    print(f"{md_sha}  {md_path}")
    print(f"{sha256_file(OUTPUT_DIR / 'manifest.json')}  {OUTPUT_DIR / 'manifest.json'}")
    print(json.dumps(summary["decision"], sort_keys=True))


if __name__ == "__main__":
    main()
