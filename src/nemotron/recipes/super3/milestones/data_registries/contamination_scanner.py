# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Local prompt-corpus contamination scanner.

task035 Session 2. This module is deliberately sandbox-only: it scans
caller-supplied local prompt/eval fixtures with deterministic token
n-gram overlap. It does not download HF datasets, call external APIs,
launch Docker, submit cluster jobs, or publish to W&B.

The scanner uses the same posture vocabulary as the task035 Session 1
matrix: ``clean``, ``informational``, and ``blocker``. Findings are
plain dicts so callers can serialize them as JSON or render them as
markdown in review reports.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]

POSTURES = ("clean", "informational", "blocker")
DEFAULT_TEXT_FIELDS = (
    "prompt",
    "question",
    "instruction",
    "input",
    "text",
    "completion",
    "answer",
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokenizer for deterministic overlap scans."""
    return _TOKEN_RE.findall(text.lower())


def token_ngrams(tokens: Sequence[str], ngram_size: int) -> set[str]:
    """Return whitespace-joined token n-grams.

    If a record is shorter than ``ngram_size``, the entire token
    sequence becomes one comparison unit. This keeps short local test
    prompts scannable without switching algorithms.
    """
    if ngram_size <= 0:
        raise ValueError("ngram_size must be positive")
    if not tokens:
        return set()
    if len(tokens) < ngram_size:
        return {" ".join(tokens)}
    return {
        " ".join(tokens[index : index + ngram_size])
        for index in range(0, len(tokens) - ngram_size + 1)
    }


def text_ngrams(text: str, ngram_size: int) -> set[str]:
    """Tokenize *text* and return token n-grams."""
    return token_ngrams(tokenize(text), ngram_size)


def _record_text(
    record: str | Mapping[str, Any],
    *,
    text_fields: Sequence[str],
) -> str:
    if isinstance(record, str):
        return record
    if not isinstance(record, Mapping):
        raise TypeError(f"record must be string or mapping, got {type(record).__name__}")
    values = [
        str(record[field])
        for field in text_fields
        if field in record and record[field] is not None
    ]
    return "\n".join(values)


def _record_id(
    record: str | Mapping[str, Any],
    *,
    fallback: str,
) -> str:
    if isinstance(record, Mapping):
        for field in ("id", "record_id", "prompt_id", "example_id", "benchmark_id"):
            value = record.get(field)
            if value is not None:
                return str(value)
    return fallback


def _load_records(path: Path) -> list[str | JsonDict]:
    if path.suffix == ".jsonl":
        records: list[str | JsonDict] = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records
    if path.suffix in {".yaml", ".yml"}:
        import yaml

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    elif path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("records", "prompts", "examples", "data", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    raise ValueError(f"{path}: expected list or mapping with records/prompts/examples")


def _classify_score(
    score: float,
    *,
    informational_threshold: float,
    blocker_threshold: float,
) -> str:
    if score >= blocker_threshold:
        return "blocker"
    if score >= informational_threshold:
        return "informational"
    return "clean"


def _build_index(
    records: Sequence[str | Mapping[str, Any]],
    *,
    ngram_size: int,
    text_fields: Sequence[str],
    id_prefix: str,
) -> list[JsonDict]:
    indexed: list[JsonDict] = []
    for index, record in enumerate(records):
        text = _record_text(record, text_fields=text_fields)
        tokens = tokenize(text)
        ngrams = token_ngrams(tokens, ngram_size)
        indexed.append(
            {
                "id": _record_id(record, fallback=f"{id_prefix}_{index}"),
                "text": text,
                "token_count": len(tokens),
                "ngrams": ngrams,
            }
        )
    return indexed


def scan_prompt_corpus(
    prompts: Sequence[str | Mapping[str, Any]],
    eval_sets: Mapping[str, Sequence[str | Mapping[str, Any]]],
    *,
    ngram_size: int = 8,
    informational_threshold: float = 0.25,
    blocker_threshold: float = 0.75,
    max_matched_ngrams: int = 8,
    text_fields: Sequence[str] = DEFAULT_TEXT_FIELDS,
) -> JsonDict:
    """Scan local prompts against local eval-set fixtures.

    ``score`` is ``max(prompt_overlap_ratio, eval_overlap_ratio)`` so
    both copied prompts and copied eval snippets surface. A finding is
    emitted for every pair whose score reaches ``informational_threshold``.
    """
    if not 0 <= informational_threshold <= blocker_threshold <= 1:
        raise ValueError(
            "thresholds must satisfy 0 <= informational_threshold <= blocker_threshold <= 1"
        )

    prompt_index = _build_index(
        prompts,
        ngram_size=ngram_size,
        text_fields=text_fields,
        id_prefix="prompt",
    )
    eval_index_by_set = {
        eval_set: _build_index(
            records,
            ngram_size=ngram_size,
            text_fields=text_fields,
            id_prefix=f"{eval_set}_eval",
        )
        for eval_set, records in sorted(eval_sets.items())
    }

    findings: list[JsonDict] = []
    counts = {posture: 0 for posture in POSTURES}
    for prompt in prompt_index:
        prompt_ngrams = prompt["ngrams"]
        if not prompt_ngrams:
            continue
        for eval_set, eval_records in eval_index_by_set.items():
            for eval_record in eval_records:
                eval_ngrams = eval_record["ngrams"]
                if not eval_ngrams:
                    continue
                overlap = prompt_ngrams & eval_ngrams
                if not overlap:
                    continue
                prompt_ratio = len(overlap) / len(prompt_ngrams)
                eval_ratio = len(overlap) / len(eval_ngrams)
                union = prompt_ngrams | eval_ngrams
                jaccard = len(overlap) / len(union)
                score = max(prompt_ratio, eval_ratio)
                posture = _classify_score(
                    score,
                    informational_threshold=informational_threshold,
                    blocker_threshold=blocker_threshold,
                )
                if posture == "clean":
                    continue
                counts[posture] += 1
                findings.append(
                    {
                        "prompt_id": prompt["id"],
                        "eval_set": eval_set,
                        "eval_id": eval_record["id"],
                        "posture": posture,
                        "score": round(score, 6),
                        "prompt_overlap_ratio": round(prompt_ratio, 6),
                        "eval_overlap_ratio": round(eval_ratio, 6),
                        "jaccard": round(jaccard, 6),
                        "overlap_ngram_count": len(overlap),
                        "prompt_ngram_count": len(prompt_ngrams),
                        "eval_ngram_count": len(eval_ngrams),
                        "matched_ngrams": sorted(overlap)[:max_matched_ngrams],
                    }
                )

    findings.sort(
        key=lambda item: (
            0 if item["posture"] == "blocker" else 1,
            -item["score"],
            item["prompt_id"],
            item["eval_set"],
            item["eval_id"],
        )
    )
    contaminated_prompt_ids = {item["prompt_id"] for item in findings}
    clean_prompts = max(len(prompt_index) - len(contaminated_prompt_ids), 0)
    counts["clean"] = clean_prompts
    return {
        "schema_version": 1,
        "scanner": "token_ngram_overlap",
        "ngram_size": ngram_size,
        "thresholds": {
            "informational": informational_threshold,
            "blocker": blocker_threshold,
        },
        "prompt_count": len(prompt_index),
        "eval_set_count": len(eval_index_by_set),
        "eval_record_count": sum(len(records) for records in eval_index_by_set.values()),
        "counts": counts,
        "findings": findings,
        "blockers": [item for item in findings if item["posture"] == "blocker"],
        "informational": [
            item for item in findings if item["posture"] == "informational"
        ],
    }


def scan_prompt_corpus_files(
    prompt_path: Path,
    eval_paths: Mapping[str, Path],
    **kwargs: Any,
) -> JsonDict:
    """Load local JSON/JSONL/YAML/text fixtures and scan them."""
    prompts = _load_records(prompt_path)
    eval_sets = {name: _load_records(path) for name, path in eval_paths.items()}
    return scan_prompt_corpus(prompts, eval_sets, **kwargs)


def format_prompt_contamination_markdown(report: Mapping[str, Any]) -> str:
    """Render scanner output as markdown-friendly text."""
    counts = report.get("counts", {})
    lines = [
        "# Prompt Corpus Contamination Scan",
        "",
        f"- scanner: `{report.get('scanner')}`",
        f"- ngram_size: `{report.get('ngram_size')}`",
        f"- prompts: `{report.get('prompt_count')}`",
        f"- eval_sets: `{report.get('eval_set_count')}`",
        f"- eval_records: `{report.get('eval_record_count')}`",
        f"- blockers: `{counts.get('blocker', 0)}`",
        f"- informational: `{counts.get('informational', 0)}`",
        "",
    ]
    findings = report.get("findings", [])
    if not findings:
        lines.append("No prompt/eval n-gram overlaps reached the reporting threshold.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "| posture | prompt_id | eval_set | eval_id | score | overlap |",
            "|---|---|---|---|---:|---:|",
        ]
    )
    for finding in findings:
        lines.append(
            (
                "| {posture} | {prompt_id} | {eval_set} | {eval_id} | "
                "{score:.6f} | {overlap} |"
            ).format(
                posture=finding["posture"],
                prompt_id=finding["prompt_id"],
                eval_set=finding["eval_set"],
                eval_id=finding["eval_id"],
                score=finding["score"],
                overlap=finding["overlap_ngram_count"],
            )
        )
    return "\n".join(lines) + "\n"


__all__ = [
    "DEFAULT_TEXT_FIELDS",
    "POSTURES",
    "format_prompt_contamination_markdown",
    "scan_prompt_corpus",
    "scan_prompt_corpus_files",
    "text_ngrams",
    "token_ngrams",
    "tokenize",
]
