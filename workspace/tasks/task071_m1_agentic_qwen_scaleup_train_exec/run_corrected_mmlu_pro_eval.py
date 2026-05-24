#!/usr/bin/env python3
"""Run a parser-aligned MMLU-Pro eval against an OpenAI chat endpoint.

This is a task071 diagnostic runner. It intentionally avoids lm-eval's
chain-of-thought completions path because Session 32 showed that path was
mostly measuring truncation and parser failure for Qwen3-30B-A3B-Instruct.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LETTER_RE = re.compile(r"\b([A-J])\b", re.I)
JSON_RE = re.compile(r'"answer"\s*:\s*"?([A-J])"?', re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--per-category", type=int, default=0)
    parser.add_argument("--parallelism", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1e-5)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def category_from_path(path: Path) -> str:
    return path.name.split("samples_mmlu_pro_", 1)[1].split("_2026-", 1)[0]


def load_rows(input_root: Path, per_category: int) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(input_root.glob("samples_mmlu_pro_*.jsonl")):
        category = category_from_path(path)
        selected = 0
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                obj = json.loads(line)
                rows.append(
                    {
                        "category": category,
                        "doc_id": obj["doc_id"],
                        "target": obj["target"],
                        "doc": obj["doc"],
                        "old_exact_match": obj.get("exact_match"),
                        "old_filtered_response": (obj.get("filtered_resps") or [""])[
                            0
                        ],
                    }
                )
                selected += 1
                if per_category > 0 and selected >= per_category:
                    break
    return rows


def result_key(result: dict[str, Any]) -> tuple[str, int]:
    return (str(result["category"]), int(result["doc_id"]))


def load_existing(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    if not path.exists():
        return {}
    existing = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            existing[result_key(item)] = item
    return existing


def build_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    doc = row["doc"]
    options = "\n".join(
        f"{chr(65 + index)}. {option}"
        for index, option in enumerate(doc["options"])
    )
    user = (
        "Answer the following MMLU-Pro multiple-choice question.\n"
        "Return exactly one JSON object with a single field named answer.\n"
        "The answer field must contain only the choice letter A-J.\n\n"
        f"Question:\n{doc['question']}\n\nOptions:\n{options}\n\nJSON:"
    )
    return [
        {
            "role": "system",
            "content": (
                "You answer multiple-choice questions. Output only JSON such as "
                '{"answer":"C"}.'
            ),
        },
        {"role": "user", "content": user},
    ]


def extract_letter(text: str | None) -> str | None:
    text = text or ""
    match = JSON_RE.search(text)
    if match:
        return match.group(1).upper()
    match = re.search(r"answer\s*[:：]\s*\(?([A-J])\)?", text, re.I)
    if match:
        return match.group(1).upper()
    match = LETTER_RE.search(text)
    if match:
        return match.group(1).upper()
    return None


def post(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "model": args.model_id,
        "messages": build_messages(row),
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
    }
    request = urllib.request.Request(
        args.endpoint_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.time()
    base = {
        "category": row["category"],
        "doc_id": row["doc_id"],
        "target": row["target"],
        "old_exact_match": row.get("old_exact_match"),
        "old_filtered_response": row.get("old_filtered_response"),
    }
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_payload = json.loads(response.read().decode())
        choice = response_payload["choices"][0]
        text = choice["message"]["content"]
        prediction = extract_letter(text)
        return {
            **base,
            "status": "ok",
            "latency_sec": round(time.time() - start, 4),
            "finish_reason": choice.get("finish_reason"),
            "response": text,
            "prediction": prediction,
            "parsed": prediction is not None,
            "correct": prediction == row["target"],
            "usage": response_payload.get("usage", {}),
        }
    except Exception as exc:  # noqa: BLE001 - preserve remote endpoint errors.
        return {
            **base,
            "status": "error",
            "latency_sec": round(time.time() - start, 4),
            "error": repr(exc),
            "prediction": None,
            "parsed": False,
            "correct": False,
        }


def summarize(
    results: list[dict[str, Any]],
    args: argparse.Namespace,
    runtime_sec: float,
    total_source_rows: int,
) -> dict[str, Any]:
    total = len(results)
    parsed = sum(result["parsed"] for result in results)
    correct = sum(result["correct"] for result in results)
    old_correct = sum(1 for result in results if result.get("old_exact_match") == 1.0)
    old_invalid = sum(
        1 for result in results if result.get("old_filtered_response") == "[invalid]"
    )
    by_category: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "count": 0,
            "parsed": 0,
            "correct": 0,
            "old_correct": 0,
            "old_invalid": 0,
        }
    )
    for result in results:
        item = by_category[result["category"]]
        item["count"] += 1
        item["parsed"] += int(result["parsed"])
        item["correct"] += int(result["correct"])
        item["old_correct"] += int(result.get("old_exact_match") == 1.0)
        item["old_invalid"] += int(result.get("old_filtered_response") == "[invalid]")

    return {
        "model": args.model_id,
        "endpoint": args.endpoint_url,
        "input_root": str(args.input_root),
        "output_dir": str(args.output_dir),
        "source_rows": total_source_rows,
        "evaluated_rows": total,
        "per_category": args.per_category,
        "prompting": "chat JSON answer-only",
        "generation": {
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "top_p": args.top_p,
        },
        "runtime_sec": round(runtime_sec, 3),
        "corrected": {
            "accuracy": correct / total if total else None,
            "parsed_rate": parsed / total if total else None,
            "correct": correct,
            "parsed": parsed,
            "finish_reason_counts": dict(
                Counter(result.get("finish_reason") for result in results)
            ),
            "status_counts": dict(Counter(result.get("status") for result in results)),
        },
        "old_same_rows": {
            "accuracy": old_correct / total if total else None,
            "invalid_rate": old_invalid / total if total else None,
            "correct": old_correct,
            "invalid": old_invalid,
        },
        "by_category": {
            category: {
                **stats,
                "accuracy": stats["correct"] / stats["count"],
                "parsed_rate": stats["parsed"] / stats["count"],
                "old_accuracy": stats["old_correct"] / stats["count"],
                "old_invalid_rate": stats["old_invalid"] / stats["count"],
            }
            for category, stats in sorted(by_category.items())
        },
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "results.jsonl"
    summary_path = args.output_dir / "summary.json"
    rows = load_rows(args.input_root, args.per_category)
    existing = load_existing(results_path) if args.resume else {}
    rows_to_run = [row for row in rows if result_key(row) not in existing]

    started = time.time()
    with results_path.open("a", encoding="utf-8") as output:
        with futures.ThreadPoolExecutor(max_workers=args.parallelism) as executor:
            pending = [executor.submit(post, row, args) for row in rows_to_run]
            for index, future in enumerate(futures.as_completed(pending), 1):
                result = future.result()
                existing[result_key(result)] = result
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
                output.flush()
                if index % 500 == 0:
                    print(
                        f"progress {index}/{len(rows_to_run)} "
                        f"total_done={len(existing)}/{len(rows)}",
                        flush=True,
                    )

    runtime_sec = time.time() - started
    results = [existing[key] for key in sorted(existing)]
    summary = summarize(results, args, runtime_sec, len(rows))
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
