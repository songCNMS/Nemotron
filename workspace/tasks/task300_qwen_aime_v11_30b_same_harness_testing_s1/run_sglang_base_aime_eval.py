#!/usr/bin/env python3
"""Run task300 30B base corrected AIME2025 eval through an SGLang endpoint.

This keeps the scoring path aligned with
workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py
while retaining full completions and task300 gate manifests.
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
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


TASK_ID = "task300_qwen_aime_v11_30b_same_harness_testing_s1"
ROUTE_ID = "eval_only_sglang_endpoint_direct_hf_30b_base_corrected_aime25"
PROMPT_VARIANTS = ("original", "concise_boxed", "answer_only")
TEMPERATURE = 0.0
TOP_P = 1e-5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aime-score-cache", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--model-path", required=True, type=Path)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--task298-approved-head", required=True)
    parser.add_argument("--task298-pr-merge-commit", required=True)
    parser.add_argument("--aime-prompt-variant", choices=PROMPT_VARIANTS, default="original")
    parser.add_argument("--aime-max-tokens", type=int, default=8192)
    parser.add_argument("--aime-limit-rows", type=int, default=30)
    parser.add_argument("--parallelism", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=900)
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
                "cache_key": item.get("key"),
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


def endpoint_base_url(endpoint_url: str) -> str:
    if endpoint_url.endswith("/v1/chat/completions"):
        return endpoint_url[: -len("/v1/chat/completions")]
    return endpoint_url.rsplit("/", 2)[0]


def post(job: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "model": args.model_id,
        "messages": [{"role": "user", "content": job["prompt"]}],
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
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
            "cache_key",
            "prompt_sha256",
            "prompt_chars",
        )
    }
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            response_payload = json.loads(response.read().decode())
        choice = response_payload["choices"][0]
        message = choice.get("message", {})
        text = message.get("content") or ""
        boxed = boxed_values(text)
        prediction = boxed[-1] if boxed else None
        expected = job.get("expected_answer")
        return {
            **base,
            "status": "ok",
            "latency_sec": round(time.time() - start, 4),
            "finish_reason": choice.get("finish_reason"),
            "response_chars": len(text),
            "response_sha256": sha256_text(text),
            "response_text": text,
            "response_tail": text[-1200:],
            "boxed_values": boxed,
            "parsed": prediction is not None,
            "prediction": prediction,
            "normalized_prediction": normalize_answer(prediction),
            "normalized_expected": normalize_answer(expected),
            "contains_expected": bool(
                expected and normalize_answer(expected) in normalize_answer(text)
            ),
            "correct": normalize_answer(prediction) == normalize_answer(expected),
            "usage": response_payload.get("usage", {}),
            "raw_choice": choice,
        }
    except Exception as exc:  # noqa: BLE001 - preserve endpoint failures.
        return {
            **base,
            "status": "error",
            "latency_sec": round(time.time() - start, 4),
            "finish_reason": None,
            "error": repr(exc),
            "traceback": traceback.format_exc(),
            "parsed": False,
            "prediction": None,
            "normalized_prediction": "",
            "normalized_expected": normalize_answer(job.get("expected_answer")),
            "contains_expected": False,
            "correct": False,
            "usage": {},
        }


def summarize_task(items: list[dict[str, Any]]) -> dict[str, Any]:
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
    return {
        "task": "aime25",
        "rows": total,
        "status_counts": dict(Counter(item.get("status") for item in items)),
        "finish_reason_counts": dict(Counter(item.get("finish_reason") for item in items)),
        "parsed_rows": parsed_rows,
        "parsed_rate": parsed_rows / total if total else None,
        "correct_rows": correct_rows,
        "exact_normalized_accuracy": correct_rows / total if total else None,
        "contains_expected_rows": sum(bool(item.get("contains_expected")) for item in items),
        "source_cache_old_score_mean": mean(old_scores) if old_scores else None,
        "successful_responses": len(ok_items),
        "avg_completion_tokens": mean(completion_tokens) if completion_tokens else None,
    }


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
    logs_dir = args.output_dir / "logs"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()

    if not args.aime_score_cache.is_file():
        raise FileNotFoundError(f"aime score cache not found: {args.aime_score_cache}")
    if not args.model_path.is_dir():
        raise FileNotFoundError(f"model path not found: {args.model_path}")

    rows = []
    for row in load_aime_rows(args.aime_score_cache, args.aime_limit_rows):
        prompt = prompt_for(row, args.aime_prompt_variant)
        rows.append(
            {
                **row,
                "prompt_variant": args.aime_prompt_variant,
                "max_tokens": args.aime_max_tokens,
                "prompt": prompt,
                "prompt_sha256": sha256_text(prompt),
                "prompt_chars": len(prompt),
            }
        )
    row_manifest = [
        {
            "task": row["task"],
            "sample_id": row["sample_id"],
            "expected_answer": row["expected_answer"],
            "normalized_expected": normalize_answer(row["expected_answer"]),
            "old_score": row["old_score"],
            "cache_key": row.get("cache_key"),
            "prompt_variant": row["prompt_variant"],
            "prompt_sha256": row["prompt_sha256"],
            "prompt_chars": row["prompt_chars"],
            "problem_sha256": sha256_text(row["problem"]),
        }
        for row in rows
    ]
    write_jsonl(manifests_dir / "aime_row_manifest.jsonl", row_manifest)

    endpoint_manifest: dict[str, Any] = {
        "endpoint_url": args.endpoint_url,
        "endpoint_base_url": endpoint_base_url(args.endpoint_url),
        "model_id": args.model_id,
        "model_path": str(args.model_path),
        "route": ROUTE_ID,
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

    command_manifest = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "route": ROUTE_ID,
        "source_head": args.source_head,
        "task298_approved_head": args.task298_approved_head,
        "task298_pr_merge_commit": args.task298_pr_merge_commit,
        "argv": sys.argv,
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.executable,
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "pythonpath": os.environ.get("PYTHONPATH"),
        "model_path": str(args.model_path),
        "aime_score_cache": str(args.aime_score_cache),
        "aime_score_cache_sha256": sha256_file(args.aime_score_cache),
        "endpoint_url": args.endpoint_url,
        "model_id": args.model_id,
        "protocol": {
            "task": "aime25",
            "aime_prompt_variant": args.aime_prompt_variant,
            "aime_limit_rows": args.aime_limit_rows,
            "aime_max_tokens": args.aime_max_tokens,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "parallelism": args.parallelism,
            "timeout": args.timeout,
            "parser": "last boxed value from boxed_values; normalize_answer exact match",
            "denominator": "all requested rows",
            "score_normalization": "exact-normalized accuracy = correct rows / all requested rows",
        },
        "boundary_confirmations": {
            "base_only": True,
            "eval_only_sglang_endpoint": True,
            "direct_hf_model_path": True,
            "no_training_or_optimizer_steps": True,
            "no_ft_eval": True,
            "no_non_aime_canary": True,
            "no_task255_reuse": True,
            "no_aime2025_train_prompts_or_labels": True,
            "aime2025_eval_input_only": True,
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
        pending = [executor.submit(post, job, args) for job in rows]
        for index, future in enumerate(futures.as_completed(pending), 1):
            result = future.result()
            results.append(result)
            print(
                f"progress {index}/{len(rows)} "
                f"{result['task']} {result['sample_id']} "
                f"{result.get('finish_reason')} parsed={result.get('parsed')} "
                f"correct={result.get('correct')} status={result.get('status')}",
                flush=True,
            )

    results = sorted(results, key=lambda item: (str(item["task"]), str(item["sample_id"])))
    summary = {
        "task_id": TASK_ID,
        "model": args.model_id,
        "model_path": str(args.model_path),
        "endpoint": args.endpoint_url,
        "route": ROUTE_ID,
        "source_head": args.source_head,
        "task298_approved_head": args.task298_approved_head,
        "task298_pr_merge_commit": args.task298_pr_merge_commit,
        "protocol": command_manifest["protocol"],
        "total_requests": len(results),
        "by_task": {"aime25": summarize_task(results)},
        "runtime_sec": round(time.time() - started, 3),
    }

    completion_rows = [
        {
            "sample_id": result["sample_id"],
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
            "sample_id": result["sample_id"],
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
