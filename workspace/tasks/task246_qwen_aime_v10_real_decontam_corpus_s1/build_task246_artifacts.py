#!/usr/bin/env python3
"""Build task246 heldout decontam corpus and V10 math sidecar M0 input.

This script intentionally writes prompt-only heldout records: answer and
solution fields from public evaluation datasets are read only to locate prompt
rows, then discarded before writing task artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
    load_yaml,
    transform_numinamath_competition,
)
from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
    MATH_DECONTAMINATION_DEFAULT_BLOCKER_THRESHOLD,
    MATH_DECONTAMINATION_DEFAULT_NGRAM_SIZE,
    convert_m0_record,
    decontaminate_math_rows,
    is_hard_math_recurrence_row,
    is_hard_math_runlength_dp_row,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT.parent
    / "outputs"
    / "task246_qwen_aime_v10_real_decontam_corpus_s1"
)
DATA_REGISTRY = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m0_data_env/data_registry.yaml"
)
ENV_REGISTRY = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml"
)

HELDOUT_SOURCES = (
    {
        "name": "aime25",
        "repo_id": "opencompass/AIME2025",
        "revision": "a6ad95f611d72cf628a80b58bd0432ef6638f958",
        "files": ("aime2025-I.jsonl", "aime2025-II.jsonl"),
        "prompt_field": "question",
        "license": "mit",
    },
    {
        "name": "hmmt_feb2025",
        "repo_id": "PraMamba/HMMT-202502",
        "revision": "9de5288c84abeb090b162f75e43a96ad971c7b26",
        "files": ("hmmt_feb_2025.jsonl",),
        "prompt_field": "problem",
        "license": "mit",
    },
    {
        "name": "math500",
        "repo_id": "HuggingFaceH4/MATH-500",
        "revision": "6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be",
        "files": ("test.jsonl",),
        "prompt_field": "problem",
        "license": "not_declared_in_dataset_card",
    },
)

NUMINA_REPO_ID = "AI-MO/NuminaMath-CoT"
NUMINA_REVISION = "9d8d210c9f6a36c8f3cd84045668c9b7800ef517"
NUMINA_TRAIN_SHARDS = tuple(f"data/train-{index:05d}-of-00005.parquet" for index in range(5))

LABELLIKE_KEYS = {
    "answer",
    "answers",
    "expected_answer",
    "gold",
    "label",
    "labels",
    "reference_solution",
    "solution",
    "target",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_prompt(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt).strip()


def safe_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("_") or "row"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                if not isinstance(data, dict):
                    raise ValueError(f"{path}: expected JSON object per line")
                records.append(data)
    return records


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            json.dump(row, f, ensure_ascii=False, sort_keys=True)
            f.write("\n")


def assert_prompt_only(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows):
        leaked = sorted(LABELLIKE_KEYS & set(row))
        if leaked:
            raise ValueError(f"heldout corpus row {index} contains label-like keys {leaked}")
        if not row.get("prompt"):
            raise ValueError(f"heldout corpus row {index} has empty prompt")


def build_heldout_corpus(output_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    corpus_rows: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []
    seen_prompt_hashes: dict[str, str] = {}

    for source in HELDOUT_SOURCES:
        source_count = 0
        kept_count = 0
        source_file_summaries = []
        for filename in source["files"]:
            source_path = Path(
                hf_hub_download(
                    repo_id=source["repo_id"],
                    filename=filename,
                    repo_type="dataset",
                    revision=source["revision"],
                )
            )
            source_file_summaries.append(
                {
                    "filename": filename,
                    "cache_path": str(source_path),
                    "sha256": sha256_file(source_path),
                }
            )
            for row_index, row in enumerate(read_jsonl(source_path)):
                source_count += 1
                prompt = normalize_prompt(str(row.get(source["prompt_field"], "")))
                if not prompt:
                    continue
                prompt_hash = sha256_text(prompt)
                source_id = str(
                    row.get("id")
                    or row.get("unique_id")
                    or f"{Path(filename).stem}_{row_index + 1:04d}"
                )
                record_id = f"{source['name']}_{safe_id(source_id)}"
                if prompt_hash in seen_prompt_hashes:
                    duplicates.append(
                        {
                            "duplicate_id": record_id,
                            "kept_id": seen_prompt_hashes[prompt_hash],
                            "prompt_sha256": prompt_hash,
                        }
                    )
                    continue
                seen_prompt_hashes[prompt_hash] = record_id
                corpus_rows.append(
                    {
                        "id": record_id,
                        "source": source["name"],
                        "source_dataset": source["repo_id"],
                        "source_file": filename,
                        "source_id": source_id,
                        "source_revision": source["revision"],
                        "prompt": prompt,
                        "prompt_sha256": prompt_hash,
                    }
                )
                kept_count += 1
        source_summaries.append(
            {
                "name": source["name"],
                "repo_id": source["repo_id"],
                "revision": source["revision"],
                "license": source["license"],
                "prompt_field": source["prompt_field"],
                "source_rows": source_count,
                "kept_prompt_rows": kept_count,
                "files": source_file_summaries,
            }
        )

    corpus_rows.sort(key=lambda row: (row["source"], row["id"]))
    assert_prompt_only(corpus_rows)

    heldout_dir = output_dir / "heldout"
    corpus_path = heldout_dir / "aime25_hmmt_math_heldout_decontam_corpus.jsonl"
    hashes_path = heldout_dir / "prompt_hashes.sha256"
    write_jsonl(corpus_path, corpus_rows)
    hashes_path.write_text(
        "".join(f"{row['prompt_sha256']}  {row['id']}\n" for row in corpus_rows),
        encoding="utf-8",
    )
    return corpus_rows, {
        "corpus_path": str(corpus_path),
        "corpus_sha256": sha256_file(corpus_path),
        "prompt_hashes_path": str(hashes_path),
        "prompt_hashes_sha256": sha256_file(hashes_path),
        "rows": len(corpus_rows),
        "prompt_hashes": len({row["prompt_sha256"] for row in corpus_rows}),
        "duplicates_removed": len(duplicates),
        "duplicates": duplicates,
        "sources": source_summaries,
        "label_fields_written": False,
    }


def m0_spec() -> dict[str, Any]:
    registry = load_yaml(DATA_REGISTRY)
    for spec in registry["datasets"]:
        if spec["id"] == "m0_math_numinamath":
            result = dict(spec)
            result.setdefault("milestone", registry["milestone"])
            return result
    raise ValueError("m0_math_numinamath not found in data registry")


def convert_numina_row(row: dict[str, Any], spec: dict[str, Any], *, source_row_index: int) -> dict[str, Any]:
    record = transform_numinamath_competition(row, spec)
    metadata = record.setdefault("metadata", {})
    metadata["source_row_index"] = source_row_index
    metadata["source_hf_split"] = "train"
    metadata["prepared_by"] = "build_task246_artifacts.py"
    return record


def scan_one_row_for_decontam(
    m0_record: dict[str, Any],
    corpus_rows: list[dict[str, Any]],
) -> tuple[bool, dict[str, Any]]:
    m1_row = convert_m0_record(m0_record, split="train")
    kept, summary = decontaminate_math_rows(
        [m1_row],
        corpus=corpus_rows,
        ngram_size=MATH_DECONTAMINATION_DEFAULT_NGRAM_SIZE,
        blocker_threshold=MATH_DECONTAMINATION_DEFAULT_BLOCKER_THRESHOLD,
    )
    return bool(kept), summary


def build_v10_m0_sidecar(
    output_dir: Path,
    corpus_rows: list[dict[str, Any]],
    *,
    max_train_rows: int,
    max_val_rows: int,
) -> dict[str, Any]:
    spec = m0_spec()
    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []
    scan_counts = Counter()
    source_files = []

    global_source_index = 0
    for shard_index, filename in enumerate(NUMINA_TRAIN_SHARDS):
        source_path = Path(
            hf_hub_download(
                repo_id=NUMINA_REPO_ID,
                filename=filename,
                repo_type="dataset",
                revision=NUMINA_REVISION,
            )
        )
        source_files.append(
            {
                "filename": filename,
                "cache_path": str(source_path),
                "sha256": sha256_file(source_path),
            }
        )
        parquet_file = pq.ParquetFile(source_path)
        for batch in parquet_file.iter_batches(
            batch_size=4096,
            columns=["source", "problem", "solution", "messages"],
        ):
            for row in batch.to_pylist():
                source_row_index = global_source_index
                global_source_index += 1
                scan_counts["source_rows_scanned"] += 1
                m0_record = convert_numina_row(row, spec, source_row_index=source_row_index)
                m1_row = convert_m0_record(m0_record, split="train")
                if is_hard_math_recurrence_row(m1_row):
                    scan_counts["v9_recurrence_rows"] += 1
                if not is_hard_math_runlength_dp_row(m1_row):
                    continue
                scan_counts["v10_candidate_rows"] += 1
                kept, decontam_summary = scan_one_row_for_decontam(m0_record, corpus_rows)
                if not kept:
                    blocked_rows.append(
                        {
                            "source_row_index": source_row_index,
                            "source_shard": filename,
                            "decontam_summary": decontam_summary,
                        }
                    )
                    continue
                metadata = m0_record.setdefault("metadata", {})
                metadata["source_shard"] = filename
                if len(train_rows) < max_train_rows:
                    metadata["prepared_split"] = "train"
                    train_rows.append(m0_record)
                elif len(val_rows) < max_val_rows:
                    metadata["prepared_split"] = "val"
                    val_rows.append(m0_record)
                if len(train_rows) >= max_train_rows and len(val_rows) >= max_val_rows:
                    break
            if len(train_rows) >= max_train_rows and len(val_rows) >= max_val_rows:
                break
        if len(train_rows) >= max_train_rows and len(val_rows) >= max_val_rows:
            break

    m0_dir = output_dir / "m0_v10_math_sidecar"
    env_dir = m0_dir / "math_competition_numeric"
    train_path = env_dir / "train-split.jsonl"
    val_path = env_dir / "val-split.jsonl"
    write_jsonl(train_path, train_rows)
    write_jsonl(val_path, val_rows)

    registry = load_yaml(DATA_REGISTRY)
    env_registry = load_yaml(ENV_REGISTRY)
    write_json(m0_dir / "dataset_registry.resolved.json", registry)
    write_json(m0_dir / "environment_registry.resolved.json", env_registry)

    manifest = {
        "schema_version": 1,
        "milestone": registry["milestone"],
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "output_dir": str(m0_dir),
        "produced_by": "workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/build_task246_artifacts.py",
        "selection": {
            "source_dataset": NUMINA_REPO_ID,
            "source_revision": NUMINA_REVISION,
            "strategy": "hard_math_runlength_dp_v10_candidate_rows_only",
            "decontam_ngram_size": MATH_DECONTAMINATION_DEFAULT_NGRAM_SIZE,
            "decontam_blocker_threshold": MATH_DECONTAMINATION_DEFAULT_BLOCKER_THRESHOLD,
            "source_rows_scanned": scan_counts["source_rows_scanned"],
            "v9_recurrence_rows": scan_counts["v9_recurrence_rows"],
            "v10_candidate_rows": scan_counts["v10_candidate_rows"],
            "blocked_by_decontam": len(blocked_rows),
        },
        "datasets": [
            {
                "id": spec["id"],
                "environment": spec["environment"],
                "hf_dataset": NUMINA_REPO_ID,
                "hf_revision": NUMINA_REVISION,
                "license": spec["license"],
                "train_rows": len(train_rows),
                "val_rows": len(val_rows),
                "source_files": source_files,
            }
        ],
        "files": [
            {
                "environment": spec["environment"],
                "split": "train",
                "path": str(train_path),
                "rows": len(train_rows),
                "sha256": sha256_file(train_path),
            },
            {
                "environment": spec["environment"],
                "split": "val",
                "path": str(val_path),
                "rows": len(val_rows),
                "sha256": sha256_file(val_path),
            },
        ],
        "blocked_rows": blocked_rows,
        "errors": [],
        "warnings": (
            [
                (
                    "Fewer V10 candidate rows were found than requested; this "
                    "sidecar input is real and non-placeholder but remains sparse."
                )
            ]
            if len(train_rows) < max_train_rows
            else []
        ),
    }
    write_json(m0_dir / "manifest.json", manifest)
    report_lines = [
        "# task246 V10 Math Sidecar M0 Report",
        "",
        f"- Output directory: `{m0_dir}`",
        f"- Source dataset: `{NUMINA_REPO_ID}` at `{NUMINA_REVISION}`",
        f"- Source rows scanned: `{scan_counts['source_rows_scanned']}`",
        f"- V9 recurrence rows observed: `{scan_counts['v9_recurrence_rows']}`",
        f"- V10 candidate rows observed: `{scan_counts['v10_candidate_rows']}`",
        f"- Decontam-blocked candidates: `{len(blocked_rows)}`",
        f"- Train rows written: `{len(train_rows)}`",
        f"- Val rows written: `{len(val_rows)}`",
        "",
    ]
    (m0_dir / "report.md").write_text("\n".join(report_lines), encoding="utf-8")
    manifest["manifest_path"] = str(m0_dir / "manifest.json")
    manifest["manifest_sha256"] = sha256_file(m0_dir / "manifest.json")
    return manifest


def build_replacement_paths(output_dir: Path, heldout: dict[str, Any], m0_manifest: dict[str, Any]) -> dict[str, Any]:
    replacement = {
        "task": "task246_qwen_aime_v10_real_decontam_corpus_s1",
        "replace_task242_placeholder_corpus": heldout["corpus_path"],
        "replace_task242_math_sidecar_m0_input_dir": m0_manifest["output_dir"],
        "task242_placeholder_corpus": (
            "/work-agents/intern_nemotron_worker_2/outputs/"
            "task242_qwen_aime_v10_4b_pilot/"
            "aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl"
        ),
        "task242_placeholder_math_sidecar_m0_input_dir": (
            "/work-agents/intern_nemotron_worker_2/outputs/"
            "task242_qwen_aime_v10_4b_pilot/task241_v10_math_sidecar_m0_PENDING"
        ),
        "no_training_or_eval_run": True,
    }
    path = output_dir / "task242_replacement_paths.json"
    write_json(path, replacement)
    replacement["path"] = str(path)
    replacement["sha256"] = sha256_file(path)
    return replacement


def build_all(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_rows, heldout = build_heldout_corpus(output_dir)
    m0_manifest = build_v10_m0_sidecar(
        output_dir,
        corpus_rows,
        max_train_rows=args.max_train_rows,
        max_val_rows=args.max_val_rows,
    )
    replacement = build_replacement_paths(output_dir, heldout, m0_manifest)
    manifest = {
        "schema_version": 1,
        "task": "task246_qwen_aime_v10_real_decontam_corpus_s1",
        "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "heldout_corpus": heldout,
        "v10_m0_input": {
            "path": m0_manifest["output_dir"],
            "manifest_path": m0_manifest["manifest_path"],
            "manifest_sha256": m0_manifest["manifest_sha256"],
            "train_rows": m0_manifest["datasets"][0]["train_rows"],
            "val_rows": m0_manifest["datasets"][0]["val_rows"],
            "selection": m0_manifest["selection"],
            "files": m0_manifest["files"],
        },
        "task242_replacement_paths": replacement,
        "leakage_status": {
            "heldout_corpus_prompt_only": True,
            "heldout_label_fields_written": False,
            "m0_sidecar_input_written": True,
            "sft_or_packed_train_outputs_written": False,
            "aime25_prompts_in_trainable_outputs": False,
            "aime25_labels_in_trainable_outputs": False,
            "m0_v10_candidates_decontam_blocked": m0_manifest["selection"]["blocked_by_decontam"],
        },
    }
    manifest_path = output_dir / "manifest.json"
    write_json(manifest_path, manifest)
    manifest["manifest_path"] = str(manifest_path)
    manifest["manifest_sha256"] = sha256_file(manifest_path)
    write_json(manifest_path, manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-train-rows", type=int, default=500)
    parser.add_argument("--max-val-rows", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    manifest = build_all(parse_args())
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
