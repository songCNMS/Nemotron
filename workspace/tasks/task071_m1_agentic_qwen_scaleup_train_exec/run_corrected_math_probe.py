#!/usr/bin/env python3
"""Run small corrected AIME/HMMT math probes against an OpenAI chat endpoint."""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import html
import json
import re
import sqlite3
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aime-score-cache", required=True, type=Path)
    parser.add_argument("--hmmt-output-jsonl", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--max-tokens", nargs="+", type=int, default=[2048, 4096, 8192])
    parser.add_argument("--aime-count", type=int, default=3)
    parser.add_argument("--hmmt-count", type=int, default=3)
    parser.add_argument("--parallelism", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args()


def cache_values(path: Path) -> list[dict[str, Any]]:
    connection = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        rows = connection.execute("select value from Cache").fetchall()
    finally:
        connection.close()
    return [json.loads(row[0]) for row in rows]


def pre_blocks(markup: str) -> list[str]:
    return [
        html.unescape(block)
        for block in re.findall(r"<pre>(.*?)</pre>", markup or "", re.S)
    ]


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
    value = value.strip().strip("$")
    value = value.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    value = re.sub(r"\s+", "", value)
    return value


def load_aime_prompts(score_cache: Path, limit: int) -> list[dict[str, Any]]:
    seen = set()
    rows = []
    for item in cache_values(score_cache):
        blocks = pre_blocks(item.get("html", ""))
        if not blocks:
            continue
        prompt = blocks[0]
        if prompt in seen:
            continue
        seen.add(prompt)
        rows.append(
            {
                "task": "aime25",
                "sample_id": f"aime_{len(rows) + 1}",
                "problem": prompt.split("Question:", 1)[-1].strip(),
                "original_prompt": prompt,
                "expected_answer": None,
            }
        )
        if len(rows) >= limit:
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
                    "sample_id": f"hmmt_{item['problem_idx']}",
                    "problem": item["problem"],
                    "original_prompt": (
                        "Solve the following math problem. Make sure to put "
                        "the answer (and only answer) inside \\boxed{}.\n\n"
                        f"{item['problem']}"
                    ),
                    "expected_answer": item["expected_answer"],
                }
            )
            if len(rows) >= limit:
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
            "contains_expected": bool(expected and normalize_answer(expected) in normalize_answer(text)),
            "correct": (
                normalize_answer(prediction) == normalize_answer(expected)
                if expected is not None
                else None
            ),
            "usage": response_payload.get("usage", {}),
        }
    except Exception as exc:  # noqa: BLE001 - preserve endpoint failures.
        return {
            **base,
            "status": "error",
            "latency_sec": round(time.time() - start, 4),
            "error": repr(exc),
            "parsed": False,
            "prediction": None,
            "contains_expected": False,
            "correct": False if job.get("expected_answer") is not None else None,
        }


def summarize(results: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    groups: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        groups[
            (
                str(result["task"]),
                str(result["prompt_variant"]),
                int(result["max_tokens"]),
            )
        ].append(result)

    by_group = {}
    for (task, variant, cap), items in sorted(groups.items()):
        key = f"{task}|{variant}|{cap}"
        total = len(items)
        correct_items = [item for item in items if item.get("correct") is not None]
        by_group[key] = {
            "task": task,
            "prompt_variant": variant,
            "max_tokens": cap,
            "rows": total,
            "status_counts": dict(Counter(item.get("status") for item in items)),
            "finish_reason_counts": dict(
                Counter(item.get("finish_reason") for item in items)
            ),
            "parsed_rows": sum(bool(item.get("parsed")) for item in items),
            "parsed_rate": (
                sum(bool(item.get("parsed")) for item in items) / total
                if total
                else None
            ),
            "contains_expected_rows": sum(
                bool(item.get("contains_expected")) for item in items
            ),
            "correct_rows": sum(bool(item.get("correct")) for item in correct_items),
            "correct_rate": (
                sum(bool(item.get("correct")) for item in correct_items)
                / len(correct_items)
                if correct_items
                else None
            ),
        }

    return {
        "model": args.model_id,
        "endpoint": args.endpoint_url,
        "aime_count": args.aime_count,
        "hmmt_count": args.hmmt_count,
        "max_tokens": args.max_tokens,
        "prompt_variants": ["original", "concise_boxed", "answer_only"],
        "total_requests": len(results),
        "by_group": by_group,
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_aime_prompts(args.aime_score_cache, args.aime_count)
    rows.extend(load_hmmt_rows(args.hmmt_output_jsonl, args.hmmt_count))

    jobs = []
    for row in rows:
        for variant in ("original", "concise_boxed", "answer_only"):
            for cap in args.max_tokens:
                jobs.append(
                    {
                        **row,
                        "prompt_variant": variant,
                        "max_tokens": cap,
                        "prompt": prompt_for(row, variant),
                    }
                )

    started = time.time()
    results = []
    with futures.ThreadPoolExecutor(max_workers=args.parallelism) as executor:
        pending = [executor.submit(post, job, args) for job in jobs]
        for index, future in enumerate(futures.as_completed(pending), 1):
            result = future.result()
            results.append(result)
            print(
                f"progress {index}/{len(jobs)} "
                f"{result['task']} {result['prompt_variant']} {result['max_tokens']} "
                f"{result.get('finish_reason')} parsed={result.get('parsed')}",
                flush=True,
            )

    results = sorted(
        results,
        key=lambda item: (
            str(item["task"]),
            str(item["sample_id"]),
            str(item["prompt_variant"]),
            int(item["max_tokens"]),
        ),
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
