#!/usr/bin/env python3
"""Run task311 corrected endpoint benchmarks with retained evidence.

This task-owned runner keeps the endpoint protocol aligned with the accepted
Qwen corrected AIME/MMLU-Pro/HMMT routes while retaining full completions,
parser diagnostics, command/env manifests, endpoint probe, and checksums.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import html
import json
import os
import platform
import re
import socket
import sqlite3
import sys
import time
import traceback
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


TASK_ID = "task311_qwen_all_sft_benchmark_eval_s1"
PROMPT_VARIANTS = ("original", "concise_boxed", "answer_only")
MMLU_JSON_RE = re.compile(r'"answer"\s*:\s*"?([A-J])"?', re.I)
MMLU_LETTER_RE = re.compile(r"\b([A-J])\b", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, choices=("aime25", "hmmt", "mmlu_pro"))
    parser.add_argument("--input-path", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--model-path", required=True, type=Path)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--route-id", required=True)
    parser.add_argument("--benchmark-role", required=True, choices=("base", "ft"))
    parser.add_argument("--comparison-base-summary", type=Path)
    parser.add_argument("--prompt-variant", choices=PROMPT_VARIANTS, default="original")
    parser.add_argument("--limit-rows", type=int, default=0)
    parser.add_argument("--max-tokens", type=int, default=0)
    parser.add_argument("--parallelism", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1e-5)
    return parser.parse_args()


def jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return repr(value)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(jsonable(row), ensure_ascii=False, sort_keys=True) + "\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def endpoint_base_url(endpoint_url: str) -> str:
    if endpoint_url.endswith("/v1/chat/completions"):
        return endpoint_url[: -len("/v1/chat/completions")]
    return endpoint_url.rsplit("/", 2)[0]


def http_json(url: str, payload: dict[str, Any] | None, timeout: int) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


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
    value = value.replace("\u2212", "-")
    value = re.sub(r"\\text\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\s+", "", value)
    return value


def problem_from_prompt(prompt: str) -> str:
    if "Question:" in prompt:
        return prompt.split("Question:", 1)[-1].strip()
    return prompt.strip()


def load_aime_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    per_prompt_counts: Counter[str] = Counter()
    prompt_indices: dict[str, int] = {}
    for item in cache_values(path):
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
                "cache_key": item.get("key"),
            }
        )
        if limit and len(rows) >= limit:
            break
    return rows


def load_hmmt_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if not line.strip():
                continue
            item = json.loads(line)
            problem_idx = item.get("problem_idx", item.get("id", index))
            expected = item.get("expected_answer", item.get("answer"))
            problem = item["problem"]
            rows.append(
                {
                    "task": "hmmt",
                    "sample_id": f"hmmt_{int(problem_idx):02d}",
                    "problem": problem,
                    "original_prompt": (
                        "Solve the following math problem. Make sure to put "
                        "the answer (and only answer) inside \\boxed{}.\n\n"
                        f"{problem}"
                    ),
                    "expected_answer": expected,
                    "old_score": item.get("is_correct"),
                    "cache_key": item.get("id", item.get("problem_idx")),
                }
            )
            if limit and len(rows) >= limit:
                break
    return rows


def load_mmlu_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if not line.strip():
                continue
            item = json.loads(line)
            rows.append(
                {
                    "task": "mmlu_pro",
                    "sample_id": item.get("sample_id", f"mmlu_pro_{index:05d}"),
                    "category": item.get("category", "unknown"),
                    "doc_id": item.get("doc_id", index),
                    "question": item["question"],
                    "options": item["options"],
                    "expected_answer": item["target"],
                    "old_score": item.get("old_exact_match"),
                    "cache_key": item.get("source_id", item.get("doc_id", index)),
                }
            )
            if limit and len(rows) >= limit:
                break
    return rows


def prompt_for_math(row: dict[str, Any], variant: str) -> str:
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


def messages_for_mmlu(row: dict[str, Any]) -> list[dict[str, str]]:
    options = "\n".join(
        f"{chr(65 + index)}. {option}"
        for index, option in enumerate(row["options"])
    )
    user = (
        "Answer the following MMLU-Pro multiple-choice question.\n"
        "Return exactly one JSON object with a single field named answer.\n"
        "The answer field must contain only the choice letter A-J.\n\n"
        f"Question:\n{row['question']}\n\nOptions:\n{options}\n\nJSON:"
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


def extract_mmlu_letter(text: str | None) -> str | None:
    text = text or ""
    match = MMLU_JSON_RE.search(text)
    if match:
        return match.group(1).upper()
    match = re.search(r"answer\s*[:：]\s*\(?([A-J])\)?", text, re.I)
    if match:
        return match.group(1).upper()
    match = MMLU_LETTER_RE.search(text)
    if match:
        return match.group(1).upper()
    return None


def build_jobs(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str]:
    if args.task == "aime25":
        rows = load_aime_rows(args.input_path, args.limit_rows)
        jobs = []
        for row in rows:
            prompt = prompt_for_math(row, args.prompt_variant)
            jobs.append(
                {
                    **row,
                    "prompt_variant": args.prompt_variant,
                    "max_tokens": args.max_tokens or 8192,
                    "messages": [{"role": "user", "content": prompt}],
                    "prompt_sha256": sha256_text(prompt),
                    "prompt_chars": len(prompt),
                    "problem_sha256": sha256_text(row["problem"]),
                }
            )
        return jobs, "last boxed value from boxed_values; normalize_answer exact match"
    if args.task == "hmmt":
        rows = load_hmmt_rows(args.input_path, args.limit_rows)
        jobs = []
        for row in rows:
            prompt = prompt_for_math(row, args.prompt_variant)
            jobs.append(
                {
                    **row,
                    "prompt_variant": args.prompt_variant,
                    "max_tokens": args.max_tokens or 8192,
                    "messages": [{"role": "user", "content": prompt}],
                    "prompt_sha256": sha256_text(prompt),
                    "prompt_chars": len(prompt),
                    "problem_sha256": sha256_text(row["problem"]),
                }
            )
        return jobs, "last boxed value from boxed_values; normalize_answer exact match"
    rows = load_mmlu_rows(args.input_path, args.limit_rows)
    jobs = []
    for row in rows:
        messages = messages_for_mmlu(row)
        prompt_text = json.dumps(messages, ensure_ascii=False, sort_keys=True)
        jobs.append(
            {
                **row,
                "prompt_variant": "chat_json_answer_only",
                "max_tokens": args.max_tokens or 64,
                "messages": messages,
                "prompt_sha256": sha256_text(prompt_text),
                "prompt_chars": len(prompt_text),
                "problem_sha256": sha256_text(row["question"]),
            }
        )
    return jobs, "JSON answer field A-J, then answer-colon fallback, then letter fallback"


def post(job: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "model": args.model_id,
        "messages": job["messages"],
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": job["max_tokens"],
    }
    request = urllib.request.Request(
        args.endpoint_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    base = {
        key: job.get(key)
        for key in (
            "task",
            "sample_id",
            "category",
            "doc_id",
            "prompt_variant",
            "max_tokens",
            "expected_answer",
            "old_score",
            "cache_key",
            "prompt_sha256",
            "prompt_chars",
            "problem_sha256",
        )
    }
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_payload = json.loads(response.read().decode())
        choice = response_payload["choices"][0]
        message = choice.get("message", {})
        text = message.get("content") or ""
        if args.task == "mmlu_pro":
            prediction = extract_mmlu_letter(text)
            normalized_prediction = prediction or ""
            normalized_expected = str(job.get("expected_answer") or "").strip().upper()
            parsed = prediction is not None
            correct = normalized_prediction == normalized_expected
            boxed = []
        else:
            boxed = boxed_values(text)
            prediction = boxed[-1] if boxed else None
            normalized_prediction = normalize_answer(prediction)
            normalized_expected = normalize_answer(job.get("expected_answer"))
            parsed = prediction is not None
            correct = normalized_prediction == normalized_expected
        return {
            **base,
            "status": "ok",
            "latency_sec": round(time.time() - started, 4),
            "finish_reason": choice.get("finish_reason"),
            "response_chars": len(text),
            "response_sha256": sha256_text(text),
            "response_text": text,
            "response_tail": text[-1200:],
            "boxed_values": boxed,
            "parsed": parsed,
            "prediction": prediction,
            "normalized_prediction": normalized_prediction,
            "normalized_expected": normalized_expected,
            "contains_expected": bool(
                normalized_expected and normalized_expected in normalize_answer(text)
            )
            if args.task != "mmlu_pro"
            else bool(prediction and prediction == normalized_expected),
            "correct": correct,
            "usage": response_payload.get("usage", {}),
            "raw_choice": choice,
        }
    except Exception as exc:  # noqa: BLE001 - preserve endpoint failures.
        return {
            **base,
            "status": "error",
            "latency_sec": round(time.time() - started, 4),
            "finish_reason": None,
            "error": repr(exc),
            "traceback": traceback.format_exc(),
            "parsed": False,
            "prediction": None,
            "normalized_prediction": "",
            "normalized_expected": normalize_answer(job.get("expected_answer"))
            if args.task != "mmlu_pro"
            else str(job.get("expected_answer") or "").strip().upper(),
            "contains_expected": False,
            "correct": False,
            "usage": {},
        }


def summarize_task(
    items: list[dict[str, Any]],
    args: argparse.Namespace,
    parser_contract: str,
    runtime_sec: float,
) -> dict[str, Any]:
    total = len(items)
    ok_items = [item for item in items if item.get("status") == "ok"]
    correct_rows = sum(bool(item.get("correct")) for item in items)
    parsed_rows = sum(bool(item.get("parsed")) for item in items)
    completion_tokens = [
        item.get("usage", {}).get("completion_tokens")
        for item in ok_items
        if item.get("usage", {}).get("completion_tokens") is not None
    ]
    summary: dict[str, Any] = {
        "task": args.task,
        "benchmark_role": args.benchmark_role,
        "rows": total,
        "status_counts": dict(Counter(item.get("status") for item in items)),
        "finish_reason_counts": dict(Counter(item.get("finish_reason") for item in items)),
        "parsed_rows": parsed_rows,
        "parsed_rate": parsed_rows / total if total else None,
        "correct_rows": correct_rows,
        "exact_normalized_accuracy": correct_rows / total if total else None,
        "contains_expected_rows": sum(bool(item.get("contains_expected")) for item in items),
        "successful_responses": len(ok_items),
        "avg_completion_tokens": mean(completion_tokens) if completion_tokens else None,
        "runtime_sec": round(runtime_sec, 3),
        "parser": parser_contract,
        "denominator": "all requested rows",
        "score_normalization": "exact-normalized accuracy = correct rows / all requested rows",
    }
    if args.task == "mmlu_pro":
        by_category: dict[str, dict[str, int]] = defaultdict(
            lambda: {"count": 0, "parsed": 0, "correct": 0}
        )
        for item in items:
            stats = by_category[str(item.get("category", "unknown"))]
            stats["count"] += 1
            stats["parsed"] += int(bool(item.get("parsed")))
            stats["correct"] += int(bool(item.get("correct")))
        summary["by_category"] = {
            category: {
                **stats,
                "accuracy": stats["correct"] / stats["count"] if stats["count"] else None,
                "parsed_rate": stats["parsed"] / stats["count"] if stats["count"] else None,
            }
            for category, stats in sorted(by_category.items())
        }
    return summary


def checksum_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name == "checksum_manifest.json":
            continue
        rows.append(
            {
                "relative_path": str(path.relative_to(root)),
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir = args.output_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    if not args.input_path.is_file():
        raise FileNotFoundError(f"input path not found: {args.input_path}")
    if not args.model_path.is_dir():
        raise FileNotFoundError(f"model path not found: {args.model_path}")

    started = time.time()
    jobs, parser_contract = build_jobs(args)
    row_manifest = [
        {
            "task": job["task"],
            "sample_id": job["sample_id"],
            "category": job.get("category"),
            "doc_id": job.get("doc_id"),
            "expected_answer": job.get("expected_answer"),
            "normalized_expected": normalize_answer(job.get("expected_answer"))
            if args.task != "mmlu_pro"
            else str(job.get("expected_answer") or "").strip().upper(),
            "old_score": job.get("old_score"),
            "cache_key": job.get("cache_key"),
            "prompt_variant": job["prompt_variant"],
            "prompt_sha256": job["prompt_sha256"],
            "prompt_chars": job["prompt_chars"],
            "problem_sha256": job["problem_sha256"],
        }
        for job in jobs
    ]
    write_jsonl(manifests_dir / f"{args.task}_row_manifest.jsonl", row_manifest)

    endpoint_manifest: dict[str, Any] = {
        "endpoint_url": args.endpoint_url,
        "endpoint_base_url": endpoint_base_url(args.endpoint_url),
        "model_id": args.model_id,
        "model_path": str(args.model_path),
        "route": args.route_id,
        "benchmark_role": args.benchmark_role,
        "probe_started_unix": time.time(),
    }
    try:
        endpoint_manifest["models_response"] = http_json(
            endpoint_base_url(args.endpoint_url) + "/v1/models",
            payload=None,
            timeout=min(args.timeout, 60),
        )
        endpoint_manifest["probe_status"] = "ok"
    except Exception as exc:  # noqa: BLE001 - preserve endpoint probe failure.
        endpoint_manifest["probe_status"] = "error"
        endpoint_manifest["probe_error"] = repr(exc)
    endpoint_manifest["probe_finished_unix"] = time.time()
    write_json(manifests_dir / "endpoint_manifest.json", endpoint_manifest)

    comparison_base_summary = None
    if args.comparison_base_summary:
        comparison_base_summary = json.loads(args.comparison_base_summary.read_text())
    command_manifest = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "route": args.route_id,
        "source_head": args.source_head,
        "argv": sys.argv,
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.executable,
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "pythonpath": os.environ.get("PYTHONPATH"),
        "benchmark_role": args.benchmark_role,
        "task": args.task,
        "model_path": str(args.model_path),
        "input_path": str(args.input_path),
        "input_sha256": sha256_file(args.input_path),
        "endpoint_url": args.endpoint_url,
        "model_id": args.model_id,
        "comparison_base_summary_path": str(args.comparison_base_summary)
        if args.comparison_base_summary
        else None,
        "comparison_base_summary": comparison_base_summary,
        "protocol": {
            "task": args.task,
            "prompt_variant": args.prompt_variant
            if args.task != "mmlu_pro"
            else "chat_json_answer_only",
            "limit_rows": args.limit_rows,
            "max_tokens": args.max_tokens or (64 if args.task == "mmlu_pro" else 8192),
            "temperature": args.temperature,
            "top_p": args.top_p,
            "parallelism": args.parallelism,
            "timeout": args.timeout,
            "parser": parser_contract,
            "denominator": "all requested rows",
            "score_normalization": "exact-normalized accuracy = correct rows / all requested rows",
        },
        "boundary_confirmations": {
            "eval_only_endpoint": True,
            "no_training_or_optimizer_steps": True,
            "no_aime2025_train_prompts_or_labels": True,
            "aime2025_eval_input_only": args.task == "aime25",
            "no_task255_reuse": True,
            "no_export_for_promotion": True,
            "no_endpoint_promotion": True,
            "no_promotion_or_go_no_go": True,
            "no_shared_deletion": True,
            "no_main_push_or_merge": True,
        },
    }
    write_json(manifests_dir / "command_env_manifest.json", command_manifest)

    results = []
    with futures.ThreadPoolExecutor(max_workers=args.parallelism) as executor:
        pending = [executor.submit(post, job, args) for job in jobs]
        for index, future in enumerate(futures.as_completed(pending), 1):
            result = future.result()
            results.append(result)
            print(
                f"progress {index}/{len(jobs)} {result['task']} "
                f"{result['sample_id']} {result.get('finish_reason')} "
                f"parsed={result.get('parsed')} correct={result.get('correct')} "
                f"status={result.get('status')}",
                flush=True,
            )

    results = sorted(
        results,
        key=lambda item: (
            str(item.get("task")),
            str(item.get("category", "")),
            str(item.get("sample_id")),
        ),
    )
    runtime_sec = time.time() - started
    task_summary = summarize_task(results, args, parser_contract, runtime_sec)
    summary = {
        "task_id": TASK_ID,
        "task": args.task,
        "benchmark_role": args.benchmark_role,
        "model": args.model_id,
        "model_path": str(args.model_path),
        "endpoint": args.endpoint_url,
        "route": args.route_id,
        "source_head": args.source_head,
        "protocol": command_manifest["protocol"],
        "total_requests": len(results),
        "by_task": {args.task: task_summary},
        "comparison_base_summary_path": str(args.comparison_base_summary)
        if args.comparison_base_summary
        else None,
        "runtime_sec": round(runtime_sec, 3),
    }

    completion_rows = [
        {
            "task": result["task"],
            "sample_id": result["sample_id"],
            "category": result.get("category"),
            "doc_id": result.get("doc_id"),
            "prompt_sha256": result["prompt_sha256"],
            "expected_answer": result["expected_answer"],
            "prediction": result.get("prediction"),
            "normalized_expected": result.get("normalized_expected"),
            "normalized_prediction": result.get("normalized_prediction"),
            "correct": result.get("correct"),
            "parsed": result.get("parsed"),
            "finish_reason": result.get("finish_reason"),
            "status": result.get("status"),
            "response_sha256": result.get("response_sha256"),
            "response_text": result.get("response_text", ""),
        }
        for result in results
    ]
    parser_rows = [
        {
            "task": result["task"],
            "sample_id": result["sample_id"],
            "category": result.get("category"),
            "doc_id": result.get("doc_id"),
            "status": result.get("status"),
            "finish_reason": result.get("finish_reason"),
            "boxed_values": result.get("boxed_values", []),
            "prediction": result.get("prediction"),
            "normalized_prediction": result.get("normalized_prediction"),
            "expected_answer": result.get("expected_answer"),
            "normalized_expected": result.get("normalized_expected"),
            "parsed": result.get("parsed"),
            "correct": result.get("correct"),
            "contains_expected": result.get("contains_expected"),
            "response_chars": result.get("response_chars"),
            "response_sha256": result.get("response_sha256"),
            "usage": result.get("usage", {}),
            "error": result.get("error"),
        }
        for result in results
    ]

    write_jsonl(args.output_dir / "results.jsonl", results)
    write_jsonl(args.output_dir / "full_completions.jsonl", completion_rows)
    write_jsonl(args.output_dir / "parser_diagnostics.jsonl", parser_rows)
    write_json(args.output_dir / "summary.json", summary)
    write_json(args.output_dir / "checksum_manifest.json", checksum_inventory(args.output_dir))
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
