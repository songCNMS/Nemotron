#!/usr/bin/env python3
"""Audit AIME/HMMT math eval artifacts for truncation and parse failures."""

from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aime-score-cache", required=True, type=Path)
    parser.add_argument("--aime-response-cache", required=True, type=Path)
    parser.add_argument("--hmmt-output-jsonl", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    return parser.parse_args()


def connect_readonly(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)


def cache_values(path: Path) -> list[dict[str, Any]]:
    with connect_readonly(path) as connection:
        rows = connection.execute("select value from Cache").fetchall()
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


def audit_aime(score_cache: Path, response_cache: Path) -> dict[str, Any]:
    score_rows = []
    for item in cache_values(score_cache):
        blocks = pre_blocks(item.get("html", ""))
        prompt = blocks[0] if len(blocks) >= 1 else ""
        output = blocks[1] if len(blocks) >= 2 else ""
        score_rows.append(
            {
                "score": item.get("score"),
                "prompt": prompt,
                "boxed": boxed_values(output),
            }
        )

    response_rows = []
    for item in cache_values(response_cache):
        choice = item["choices"][0]
        response_rows.append(
            {
                "finish_reason": choice.get("finish_reason"),
                "boxed": boxed_values(choice["message"]["content"]),
            }
        )

    total = len(score_rows)
    correct = sum(row["score"] == 1 for row in score_rows)
    boxed = sum(bool(row["boxed"]) for row in score_rows)
    correct_with_boxed = sum(
        row["score"] == 1 and bool(row["boxed"]) for row in score_rows
    )
    wrong_with_boxed = sum(
        row["score"] == 0 and bool(row["boxed"]) for row in score_rows
    )
    return {
        "score_rows": total,
        "unique_prompts": len({row["prompt"] for row in score_rows}),
        "score": correct / total if total else None,
        "correct_rows": correct,
        "boxed_rows_in_score_cache": boxed,
        "correct_with_boxed": correct_with_boxed,
        "correct_without_boxed": correct - correct_with_boxed,
        "wrong_with_boxed": wrong_with_boxed,
        "response_rows": len(response_rows),
        "finish_reason_counts": dict(
            Counter(row["finish_reason"] for row in response_rows)
        ),
        "boxed_rows_in_response_cache": sum(bool(row["boxed"]) for row in response_rows),
    }


def audit_hmmt(output_jsonl: Path) -> dict[str, Any]:
    rows = []
    with output_jsonl.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            generation = item.get("generation", "")
            expected = str(item.get("expected_answer"))
            rows.append(
                {
                    "finish_reason": item.get("finish_reason"),
                    "predicted_answer": item.get("predicted_answer"),
                    "symbolic_correct": bool(item.get("symbolic_correct")),
                    "contains_expected_answer": expected in generation,
                    "boxed": boxed_values(generation),
                }
            )

    total = len(rows)
    return {
        "rows": total,
        "symbolic_correct_rows": sum(row["symbolic_correct"] for row in rows),
        "symbolic_correct_percent": (
            100.0 * sum(row["symbolic_correct"] for row in rows) / total
            if total
            else None
        ),
        "finish_reason_counts": dict(Counter(row["finish_reason"] for row in rows)),
        "predicted_answer_rows": sum(
            row["predicted_answer"] is not None for row in rows
        ),
        "boxed_rows": sum(bool(row["boxed"]) for row in rows),
        "contains_expected_answer_rows": sum(
            row["contains_expected_answer"] for row in rows
        ),
        "length_contains_expected_without_prediction": sum(
            row["finish_reason"] == "length"
            and row["contains_expected_answer"]
            and row["predicted_answer"] is None
            for row in rows
        ),
    }


def main() -> None:
    args = parse_args()
    summary = {
        "aime25": audit_aime(args.aime_score_cache, args.aime_response_cache),
        "hmmt": audit_hmmt(args.hmmt_output_jsonl),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
