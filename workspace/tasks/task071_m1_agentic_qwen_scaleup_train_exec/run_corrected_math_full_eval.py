#!/usr/bin/env python3
"""Run full corrected AIME25/HMMT comparisons against an OpenAI chat endpoint."""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import html
import json
import re
import sqlite3
import time
import urllib.request
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

PROMPT_VARIANTS = ("original", "concise_boxed", "answer_only")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aime-score-cache", required=True, type=Path)
    parser.add_argument("--hmmt-output-jsonl", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--aime-prompt-variant", choices=PROMPT_VARIANTS, default="original")
    parser.add_argument("--hmmt-prompt-variant", choices=PROMPT_VARIANTS, default="original")
    parser.add_argument("--aime-max-tokens", type=int, default=8192)
    parser.add_argument("--hmmt-max-tokens", type=int, default=8192)
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=("aime25", "hmmt"),
        default=["aime25", "hmmt"],
    )
    parser.add_argument("--aime-limit-rows", type=int, default=0)
    parser.add_argument("--hmmt-limit-rows", type=int, default=0)
    parser.add_argument("--parallelism", type=int, default=16)
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args()


def cache_values(path: Path) -> list[dict[str, Any]]:
    connection = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        rows = connection.execute("select value from Cache").fetchall()
    finally:
        connection.close()
    return [json.loads(row[0]) for row in rows]


def first_pre_block(markup: str) -> str:
    match = re.search(r"<pre>(.*?)</pre>", markup or "", re.S)
    return html.unescape(match.group(1)) if match else ""


def html_value(markup: str, label: str) -> str | None:
    match = re.search(rf"<p>{re.escape(label)}:\s*(.*?)</p>", markup or "", re.S)
    return html.unescape(match.group(1)).strip() if match else None


def boxed_values(text: str) -> list[str]:
    values = []
    for pattern in ("\\boxed", "\\\\boxed"):
        index = 0
        while True:
            start = text.find(pattern, index)
            if start < 0:
                break
            open_brace = text.find("{", start)
            if open_brace < 0:
                break
            depth = 0
            for offset in range(open_brace, len(text)):
                if text[offset] == "{":
                    depth += 1
                elif text[offset] == "}":
                    depth -= 1
                    if depth == 0:
                        values.append(text[open_brace + 1 : offset])
                        index = offset + 1
                        break
            else:
                index = open_brace + 1
    deduped = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def normalize_answer(value: str | None) -> str:
    value = value or ""
    value = html.unescape(value)
    value = value.strip().strip("$").strip()
    value = value.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    value = value.replace("\\left", "").replace("\\right", "")
    value = value.replace("\\,", "").replace("\\!", "")
    value = value.replace("−", "-")
    value = re.sub(r"\\text\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\s+", "", value)
    return value


def problem_from_prompt(prompt: str) -> str:
    if "Question:" in prompt:
        return prompt.split("Question:", 1)[-1].strip()
    return prompt.strip()


def load_aime_rows(score_cache: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    per_prompt_counts: Counter[str] = Counter()
    prompt_indices: dict[str, int] = {}
    for item in cache_values(score_cache):
        markup = item.get("html", "")
        prompt = first_pre_block(markup)
        expected = html_value(markup, "Correct Answer")
        if not prompt or expected is None:
            continue
        if prompt not in prompt_indices:
            prompt_indices[prompt] = len(prompt_indices) + 1
        per_prompt_counts[prompt] += 1
        rows.append(
            {
                "task": "aime25",
                "sample_id": (
                    f"aime_{prompt_indices[prompt]:02d}"
                    f"_r{per_prompt_counts[prompt]:02d}"
                ),
                "problem": problem_from_prompt(prompt),
                "original_prompt": prompt,
                "expected_answer": expected,
                "old_score": item.get("score"),
            }
        )
        if limit and len(rows) >= limit:
            break
    return rows


def load_hmmt_rows(output_jsonl: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    with output_jsonl.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            rows.append(
                {
                    "task": "hmmt",
                    "sample_id": f"hmmt_{item['problem_idx']:02d}",
                    "problem": item["problem"],
                    "original_prompt": (
                        "Solve the following math problem. Make sure to put "
                        "the answer (and only answer) inside \\boxed{}.\n\n"
                        f"{item['problem']}"
                    ),
                    "expected_answer": item["expected_answer"],
                    "old_score": item.get("is_correct"),
                }
            )
            if limit and len(rows) >= limit:
                break
    return rows


def prompt_for(row: dict[str, Any], variant: str) -> str:
    if variant == "original":
        return row["original_prompt"]
    if variant == "concise_boxed":
        return (
            "Solve the following math problem. Keep the solution concise. "
            "End with exactly one final line of the form \\boxed{answer}. "
            "Do not write anything after the boxed answer.\n\n"
            f"Problem: {row['problem']}"
        )
    if variant == "answer_only":
        return (
            "Solve the problem internally. Return only the final answer inside "
            "\\boxed{answer}; do not include explanation or any extra text.\n\n"
            f"Problem: {row['problem']}"
        )
    raise ValueError(f"unknown prompt variant: {variant}")


def post(job: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "model": args.model_id,
        "messages": [{"role": "user", "content": job["prompt"]}],
        "temperature": 0.0,
        "top_p": 1e-5,
        "max_tokens": job["max_tokens"],
    }
    request = urllib.request.Request(
        args.endpoint_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.time()
    base = {
        key: job[key]
        for key in (
            "task",
            "sample_id",
            "prompt_variant",
            "max_tokens",
            "expected_answer",
            "old_score",
        )
    }
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_payload = json.loads(response.read().decode())
        choice = response_payload["choices"][0]
        text = choice["message"]["content"]
        boxed = boxed_values(text)
        prediction = boxed[-1] if boxed else None
        expected = job.get("expected_answer")
        return {
            **base,
            "status": "ok",
            "latency_sec": round(time.time() - start, 4),
            "finish_reason": choice.get("finish_reason"),
            "response_chars": len(text),
            "response_tail": text[-1200:],
            "boxed_values": boxed,
            "parsed": prediction is not None,
            "prediction": prediction,
            "contains_expected": bool(
                expected and normalize_answer(expected) in normalize_answer(text)
            ),
            "correct": normalize_answer(prediction) == normalize_answer(expected),
            "usage": response_payload.get("usage", {}),
        }
    except Exception as exc:  # noqa: BLE001 - preserve endpoint failures.
        return {
            **base,
            "status": "error",
            "latency_sec": round(time.time() - start, 4),
            "finish_reason": None,
            "error": repr(exc),
            "parsed": False,
            "prediction": None,
            "contains_expected": False,
            "correct": False,
            "usage": {},
        }


def summarize_task(task: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    ok_items = [item for item in items if item.get("status") == "ok"]
    correct_rows = sum(bool(item.get("correct")) for item in items)
    parsed_rows = sum(bool(item.get("parsed")) for item in items)
    old_scores = [
        float(item["old_score"])
        for item in items
        if isinstance(item.get("old_score"), (int, float))
    ]
    completion_tokens = [
        item.get("usage", {}).get("completion_tokens")
        for item in ok_items
        if item.get("usage", {}).get("completion_tokens") is not None
    ]
    summary = {
        "task": task,
        "rows": total,
        "status_counts": dict(Counter(item.get("status") for item in items)),
        "finish_reason_counts": dict(
            Counter(item.get("finish_reason") for item in items)
        ),
        "parsed_rows": parsed_rows,
        "parsed_rate": parsed_rows / total if total else None,
        "correct_rows": correct_rows,
        "exact_normalized_accuracy": correct_rows / total if total else None,
        "contains_expected_rows": sum(
            bool(item.get("contains_expected")) for item in items
        ),
        "source_cache_old_score_mean": mean(old_scores) if old_scores else None,
        "successful_responses": len(ok_items),
        "avg_completion_tokens": mean(completion_tokens) if completion_tokens else None,
    }
    if task == "hmmt":
        summary["exact_normalized_correct_percent"] = (
            100.0 * correct_rows / total if total else None
        )
    return summary


def summarize(results: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    by_task = {}
    for task in ("aime25", "hmmt"):
        items = [result for result in results if result["task"] == task]
        by_task[task] = summarize_task(task, items)
    return {
        "model": args.model_id,
        "endpoint": args.endpoint_url,
        "protocol": {
            "aime_prompt_variant": args.aime_prompt_variant,
            "hmmt_prompt_variant": args.hmmt_prompt_variant,
            "aime_max_tokens": args.aime_max_tokens,
            "hmmt_max_tokens": args.hmmt_max_tokens,
            "temperature": 0.0,
            "top_p": 1e-5,
            "tasks": args.tasks,
        },
        "total_requests": len(results),
        "by_task": by_task,
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    if "aime25" in args.tasks:
        for row in load_aime_rows(args.aime_score_cache, args.aime_limit_rows):
            rows.append(
                {
                    **row,
                    "prompt_variant": args.aime_prompt_variant,
                    "max_tokens": args.aime_max_tokens,
                    "prompt": prompt_for(row, args.aime_prompt_variant),
                }
            )
    if "hmmt" in args.tasks:
        for row in load_hmmt_rows(args.hmmt_output_jsonl, args.hmmt_limit_rows):
            rows.append(
                {
                    **row,
                    "prompt_variant": args.hmmt_prompt_variant,
                    "max_tokens": args.hmmt_max_tokens,
                    "prompt": prompt_for(row, args.hmmt_prompt_variant),
                }
            )

    started = time.time()
    results = []
    with futures.ThreadPoolExecutor(max_workers=args.parallelism) as executor:
        pending = [executor.submit(post, job, args) for job in rows]
        for index, future in enumerate(futures.as_completed(pending), 1):
            result = future.result()
            results.append(result)
            print(
                f"progress {index}/{len(rows)} "
                f"{result['task']} {result['sample_id']} "
                f"{result.get('finish_reason')} parsed={result.get('parsed')} "
                f"correct={result.get('correct')}",
                flush=True,
            )

    results = sorted(
        results,
        key=lambda item: (str(item["task"]), str(item["sample_id"])),
    )
    summary = summarize(results, args)
    summary["runtime_sec"] = round(time.time() - started, 3)
    (args.output_dir / "results.jsonl").write_text(
        "".join(json.dumps(result, ensure_ascii=False) + "\n" for result in results),
        encoding="utf-8",
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
