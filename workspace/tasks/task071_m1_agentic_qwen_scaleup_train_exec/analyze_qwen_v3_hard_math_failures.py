#!/usr/bin/env python3
"""Analyze Qwen v3 corrected hard-math failures and emit a recovery recipe."""

from __future__ import annotations

import argparse
import html
import json
import re
import sqlite3
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from statistics import mean
from typing import Any

DEFAULT_DEBUG_ROOT = Path(
    "/work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug"
)
DEFAULT_V3_RESULTS = (
    DEFAULT_DEBUG_ROOT / "qwen_v3_iter2200_session67/math_corrected_full/results.jsonl"
)
DEFAULT_ITER3000_RESULTS = (
    DEFAULT_DEBUG_ROOT / "qwen_chat_iter3000_session59/math_corrected_full/results.jsonl"
)
DEFAULT_AIME_SCORE_CACHE = (
    DEFAULT_DEBUG_ROOT / "math_artifact_audit_session36/aime_score_cache.db"
)
DEFAULT_HMMT_JSONL = DEFAULT_DEBUG_ROOT / "math_artifact_audit_session36/hmmt_output.jsonl"
DEFAULT_M1_DIR = Path(
    "/work-agents/intern_nemontron_code_reading/outputs/"
    "task071_qwen30b_a3b_math_reasoning_replay_v3/m1_agentic_sft"
)
DEFAULT_OUTPUT_DIR = Path(
    "/work-agents/intern_nemontron_code_reading/Nemotron/workspace/tasks/"
    "task071_m1_agentic_qwen_scaleup_train_exec"
)

AIME_RE = re.compile(r"^(aime_\d{2})_r(\d{2})$")
HMMT_RE = re.compile(r"^(hmmt_\d{2})$")

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "geometry": (
        "angle",
        "area",
        "circle",
        "circum",
        "diameter",
        "geometric",
        "inscribed",
        "line",
        "point",
        "radius",
        "rectangle",
        "tangent",
        "triangle",
    ),
    "number_theory": (
        "congru",
        "digit",
        "divisor",
        "factor",
        "integer",
        "mod",
        "prime",
        "remainder",
        "unit",
    ),
    "algebra": (
        "equation",
        "function",
        "log",
        "polynomial",
        "real numbers",
        "sqrt",
        "system",
        "variable",
    ),
    "combinatorics_probability": (
        "arrange",
        "choose",
        "color",
        "combin",
        "count",
        "probability",
        "sequence",
        "ways",
    ),
}

ANSWER_SEEKING_PATTERNS = (
    "compute",
    "determine",
    "evaluate",
    "find",
    "how many",
    "what is",
)
PROOF_LIKE_PATTERNS = (
    "prove",
    "show that",
)


JsonDict = dict[str, Any]


def read_jsonl(path: Path) -> list[JsonDict]:
    rows: list[JsonDict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_answer(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = text.strip().strip("$").strip()
    text = text.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    text = text.replace("\\left", "").replace("\\right", "")
    text = text.replace("\\,", "").replace("\\!", "")
    text = text.replace("−", "-")
    text = re.sub(r"\\text\{([^{}]*)\}", r"\1", text)
    return re.sub(r"\s+", "", text)


def boxed_values(text: str) -> list[str]:
    values: list[str] = []
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
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def parseable_final_answer_segment(text: str) -> bool:
    tail = text[-500:]
    if "Final answer" not in tail:
        return True
    segment = tail.rsplit("Final answer", 1)[-1]
    return bool(boxed_values(segment))


def problem_key(row: Mapping[str, Any]) -> str:
    sample_id = str(row.get("sample_id", ""))
    match = AIME_RE.match(sample_id)
    if match:
        return match.group(1)
    match = HMMT_RE.match(sample_id)
    if match:
        return match.group(1)
    return sample_id


def read_cache_values(path: Path) -> list[JsonDict]:
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


def problem_from_prompt(prompt: str) -> str:
    if "Question:" in prompt:
        return prompt.split("Question:", 1)[-1].strip()
    return prompt.strip()


def load_aime_problem_map(score_cache: Path) -> dict[str, JsonDict]:
    prompt_indices: dict[str, int] = {}
    problems: dict[str, JsonDict] = {}
    for item in read_cache_values(score_cache):
        markup = str(item.get("html", ""))
        prompt = first_pre_block(markup)
        expected = html_value(markup, "Correct Answer")
        if not prompt or expected is None:
            continue
        if prompt not in prompt_indices:
            prompt_indices[prompt] = len(prompt_indices) + 1
        problem_id = f"aime_{prompt_indices[prompt]:02d}"
        problems.setdefault(
            problem_id,
            {
                "problem": problem_from_prompt(prompt),
                "expected_answer": expected,
                "old_score_values": [],
            },
        )
        if isinstance(item.get("score"), (int, float)):
            problems[problem_id]["old_score_values"].append(float(item["score"]))
    for item in problems.values():
        scores = item.pop("old_score_values")
        item["old_score_mean"] = mean(scores) if scores else None
    return problems


def load_hmmt_problem_map(output_jsonl: Path) -> dict[str, JsonDict]:
    problems: dict[str, JsonDict] = {}
    with output_jsonl.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            problem_id = f"hmmt_{int(item['problem_idx']):02d}"
            problems[problem_id] = {
                "problem": item.get("problem", ""),
                "expected_answer": item.get("expected_answer"),
                "problem_type": item.get("problem_type") or [],
                "old_finish_reason": item.get("finish_reason"),
                "old_symbolic_correct": item.get("symbolic_correct"),
            }
    return problems


def classify_topic(text: str) -> str:
    lower = text.lower()
    scores = {
        topic: sum(1 for keyword in keywords if keyword in lower)
        for topic, keywords in TOPIC_KEYWORDS.items()
    }
    best_topic, best_score = max(scores.items(), key=lambda item: item[1])
    return best_topic if best_score else "unknown"


def has_answer_seeking_prompt(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in ANSWER_SEEKING_PATTERNS)


def is_proof_like_prompt(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in PROOF_LIKE_PATTERNS)


def completion_tokens(row: Mapping[str, Any]) -> int:
    usage = row.get("usage")
    if isinstance(usage, Mapping) and isinstance(usage.get("completion_tokens"), int):
        return int(usage["completion_tokens"])
    return 0


def row_cluster(row: Mapping[str, Any]) -> str:
    if row.get("status") != "ok":
        return "request_error"
    if row.get("finish_reason") == "length" or not row.get("parsed"):
        return "length_or_unparsed"
    if row.get("correct"):
        return "correct"
    if row.get("contains_expected"):
        return "expected_mentioned_final_wrong"
    if len(row.get("boxed_values") or []) > 1:
        return "multi_boxed_wrong_final"
    return "parsed_wrong_final"


def summarize_rows(rows: list[JsonDict]) -> JsonDict:
    total = len(rows)
    return {
        "rows": total,
        "status_counts": dict(Counter(str(row.get("status")) for row in rows)),
        "finish_reason_counts": dict(Counter(str(row.get("finish_reason")) for row in rows)),
        "parsed_rows": sum(bool(row.get("parsed")) for row in rows),
        "parsed_rate": (sum(bool(row.get("parsed")) for row in rows) / total) if total else 0.0,
        "correct_rows": sum(bool(row.get("correct")) for row in rows),
        "accuracy": (sum(bool(row.get("correct")) for row in rows) / total) if total else 0.0,
        "contains_expected_rows": sum(bool(row.get("contains_expected")) for row in rows),
        "avg_completion_tokens": mean(completion_tokens(row) for row in rows) if rows else 0.0,
    }


def summarize_by_problem(
    rows: list[JsonDict],
    *,
    problem_lookup: Mapping[str, Mapping[str, Any]],
    baseline_rows: Mapping[str, Mapping[str, Any]],
) -> list[JsonDict]:
    grouped: dict[str, list[JsonDict]] = defaultdict(list)
    for row in rows:
        grouped[problem_key(row)].append(row)
    summaries = []
    for key, group in sorted(grouped.items()):
        lookup = problem_lookup.get(key, {})
        predictions = [normalize_answer(row.get("prediction")) for row in group if row.get("prediction")]
        modal_prediction, modal_count = (None, 0)
        if predictions:
            modal_prediction, modal_count = Counter(predictions).most_common(1)[0]
        baseline_group = [
            baseline_rows[row["sample_id"]]
            for row in group
            if row.get("sample_id") in baseline_rows
        ]
        row_clusters = Counter(row_cluster(row) for row in group)
        correct = sum(bool(row.get("correct")) for row in group)
        length = sum(row.get("finish_reason") == "length" for row in group)
        parsed = sum(bool(row.get("parsed")) for row in group)
        if correct == len(group):
            cluster = "all_repeats_correct"
        elif length or parsed < len(group):
            cluster = "length_or_unparsed"
        elif any(row.get("contains_expected") and not row.get("correct") for row in group):
            cluster = "expected_mentioned_final_wrong"
        elif len(set(predictions)) <= 2 and correct == 0:
            cluster = "deterministic_wrong_final"
        else:
            cluster = "mixed_or_variable_wrong"
        problem_text = str(lookup.get("problem", ""))
        topic = classify_topic(problem_text)
        if lookup.get("problem_type"):
            topic = ",".join(str(value) for value in lookup["problem_type"])
        baseline_correct = sum(bool(row.get("correct")) for row in baseline_group)
        summaries.append(
            {
                "problem_id": key,
                "task": str(group[0].get("task")),
                "topic": topic,
                "rows": len(group),
                "correct_rows": correct,
                "parsed_rows": parsed,
                "length_rows": length,
                "contains_expected_rows": sum(bool(row.get("contains_expected")) for row in group),
                "unique_predictions": len(set(predictions)),
                "modal_prediction": modal_prediction,
                "modal_prediction_rows": modal_count,
                "avg_completion_tokens": mean(completion_tokens(row) for row in group),
                "old_score_mean": lookup.get("old_score_mean"),
                "baseline_iter3000_correct_rows": baseline_correct,
                "correct_delta_vs_iter3000": correct - baseline_correct,
                "row_clusters": dict(row_clusters),
                "cluster": cluster,
                "expected_answer": lookup.get("expected_answer") or group[0].get("expected_answer"),
            }
        )
    return summaries


def iter_rows(path: Path) -> Iterable[JsonDict]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                yield json.loads(stripped)


def message_content(row: Mapping[str, Any], role: str) -> str:
    messages = row.get("messages")
    if not isinstance(messages, list):
        return ""
    for message in messages:
        if isinstance(message, Mapping) and message.get("role") == role:
            return str(message.get("content", ""))
    return ""


def hard_math_candidate(row: Mapping[str, Any]) -> tuple[bool, str]:
    metadata = row.get("metadata")
    if not isinstance(metadata, Mapping):
        return False, "missing_metadata"
    if metadata.get("m0_environment") != "math_competition_numeric":
        return False, "not_competition_numeric"
    prompt = message_content(row, "user")
    solution = message_content(row, "assistant")
    if is_proof_like_prompt(prompt):
        return False, "proof_like_prompt"
    if not has_answer_seeking_prompt(prompt):
        return False, "not_answer_seeking"
    if len(prompt) < 80:
        return False, "short_prompt"
    if len(solution) < 700:
        return False, "short_solution"
    topic = classify_topic(f"{prompt}\n{solution}")
    if topic == "unknown":
        return False, "unknown_topic"
    if len(solution) > 12000:
        return False, "very_long_solution"
    return True, topic


def inspect_training_recipe(m1_dir: Path) -> JsonDict:
    manifest = json.loads((m1_dir / "manifest.json").read_text(encoding="utf-8"))
    verified_path = m1_dir / "agentic_sft_v0_math_verified_full_solution_train.jsonl"
    format_path = m1_dir / "agentic_sft_v0_math_format_repair_train.jsonl"
    hard_topic_counts: Counter[str] = Counter()
    hard_reject_counts: Counter[str] = Counter()
    verified_rows = 0
    hard_rows = 0
    for row in iter_rows(verified_path):
        verified_rows += 1
        keep, reason = hard_math_candidate(row)
        if keep:
            hard_rows += 1
            hard_topic_counts[reason] += 1
        else:
            hard_reject_counts[reason] += 1
    format_rows = 0
    format_unparseable_final_segment = 0
    for row in iter_rows(format_path):
        format_rows += 1
        assistant = message_content(row, "assistant")
        if not parseable_final_answer_segment(assistant):
            format_unparseable_final_segment += 1
    return {
        "existing_manifest_math_counts": manifest.get("math_reasoning_replay_v3", {}),
        "verified_full_solution_rows_read": verified_rows,
        "hard_verified_candidate_rows": hard_rows,
        "hard_verified_candidate_rate": hard_rows / verified_rows if verified_rows else 0.0,
        "hard_verified_topic_counts": dict(sorted(hard_topic_counts.items())),
        "hard_verified_reject_counts": dict(sorted(hard_reject_counts.items())),
        "format_repair_rows_read": format_rows,
        "format_repair_unparseable_final_segment_count": format_unparseable_final_segment,
    }


def build_recovery_recipe(training_scan: Mapping[str, Any]) -> JsonDict:
    hard_rows = int(training_scan.get("hard_verified_candidate_rows") or 0)
    return {
        "run_name": "task071_qwen30b_a3b_hard_math_recovery_v4",
        "base_model": {
            "hf_model": "/mnt/3fs/data/shared_models/Qwen/Qwen3-30B-A3B-Instruct-2507",
            "megatron_checkpoint": (
                "/work-agents/intern_nemontron_code_reading/"
                "task071_qwen30b_a3b_sft_train_exec/"
                "pretrained_megatron_qwen3_30b_a3b_instruct_2507"
            ),
            "start_from": "original_qwen3_30b_a3b_instruct_2507",
        },
        "data_strategy": {
            "name": "hard_math_recovery_v4",
            "base_agentic_train_jsonl": "keep full M1 train blend for agentic coverage",
            "sidecars": {
                "hard_verified_full_solution": {
                    "source": "verified_full_solution rows that pass AIME/HMMT-style answer-seeking hard filter",
                    "estimated_rows_from_v3_artifacts": hard_rows,
                    "sample_fraction": 1.0,
                    "blend_weight_after_prepack_sampling": 1.0,
                },
                "broad_verified_full_solution": {
                    "source": "remaining verified_full_solution rows",
                    "sample_fraction": 0.25,
                    "blend_weight_after_prepack_sampling": 1.0,
                },
                "format_repair": {
                    "source": "format_repair rows",
                    "sample_fraction": 0.0,
                    "blend_weight_after_prepack_sampling": 0.0,
                    "reason": "V3 already has high parser coverage; these rows can carry noisy or malformed finals.",
                },
                "final_answer_aux": {
                    "source": "final_answer_aux rows",
                    "sample_fraction": 0.0,
                    "blend_weight_after_prepack_sampling": 0.0,
                    "reason": "V3 failure is hard-math correctness, not final-answer format.",
                },
            },
            "hard_filter": {
                "environment": "math_competition_numeric",
                "require_answer_seeking_prompt": list(ANSWER_SEEKING_PATTERNS),
                "exclude_proof_like_prompt": list(PROOF_LIKE_PATTERNS),
                "min_prompt_chars": 80,
                "min_solution_chars": 700,
                "max_solution_chars": 12000,
                "topic_keywords": TOPIC_KEYWORDS,
            },
        },
        "training": {
            "epochs": 0.20,
            "global_batch_size": 8,
            "micro_batch_size": 1,
            "seq_length": 4096,
            "optimizer_lr": 3e-7,
            "scheduler_min_lr": 8e-8,
            "lr_warmup_iters": 100,
            "eval_interval": 400,
            "save_interval": 400,
            "cuda_visible_devices": "0,1,2,3,4,5,6,7",
            "nproc_per_node": 8,
            "train_entrypoint": "src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py",
        },
        "eval_gates": {
            "candidate_checkpoints": ["iter_0000400", "iter_0000800", "iter_0001200"],
            "mini_gate": {
                "mmlu_pro_20_per_category_min_accuracy": 0.60,
                "aime25_300_min_accuracy": 0.15,
                "hmmt_30_min_exact_percent": 3.3333333333333335,
                "math_parsed_rate_min": 0.90,
            },
            "promotion_gate": {
                "mmlu_pro_full_min_accuracy": 0.55,
                "aime25_full_min_accuracy": 0.20,
                "hmmt_full_min_exact_percent": 10.0,
            },
        },
    }


def render_markdown(analysis: Mapping[str, Any], recipe: Mapping[str, Any]) -> str:
    cluster_counts = analysis["cluster_counts"]
    problem_rows = analysis["problem_summaries"]
    top_failures = [
        row
        for row in problem_rows
        if row["task"] == "aime25" and row["cluster"] != "all_repeats_correct"
    ][:12]
    lines = [
        "# Qwen v3 Hard-Math Failure Analysis - Session 68",
        "",
        "## Inputs",
        "",
        f"- V3 results: `{analysis['inputs']['v3_results']}`",
        f"- Iter3000 comparison: `{analysis['inputs']['iter3000_results']}`",
        f"- M1 data artifact: `{analysis['inputs']['m1_dir']}`",
        "",
        "## Metric Summary",
        "",
        "| Task | Rows | Accuracy | Parsed rate | Contains expected | Avg completion tokens |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for task, summary in analysis["task_summary"].items():
        lines.append(
            f"| {task} | {summary['rows']} | {summary['accuracy']:.6f} | "
            f"{summary['parsed_rate']:.6f} | {summary['contains_expected_rows']} | "
            f"{summary['avg_completion_tokens']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Failure Clusters",
            "",
            "| Task | Cluster | Problems | Rows |",
            "|---|---|---:|---:|",
        ]
    )
    for task, clusters in cluster_counts.items():
        for cluster, payload in clusters.items():
            lines.append(
                f"| {task} | {cluster} | {payload['problems']} | {payload['rows']} |"
            )
    lines.extend(
        [
            "",
            "Key readout:",
            "",
            (
                "- AIME25 has high parseability but repeated wrong reasoning: "
                "most problem groups have a stable wrong boxed answer across repeats."
            ),
            (
                "- AIME25 length failures are concentrated in a small number "
                "of problem groups rather than spread across the benchmark."
            ),
            (
                "- HMMT is the cleanest signal: every row is parsed and stops "
                "normally, yet every exact-normalized answer is wrong."
            ),
            (
                "- The error shape rules out a parser-only fix. The next run needs "
                "harder verified solution replay, not more boxed-answer-only data."
            ),
            "",
            "## Representative AIME Problem Groups",
            "",
            (
                "| Problem | Topic | Cluster | Correct/Rows | Parsed/Rows | "
                "Length | Modal prediction | Iter3000 correct |"
            ),
            "|---|---|---|---:|---:|---:|---|---:|",
        ]
    )
    for row in top_failures:
        modal_prediction = str(row["modal_prediction"])
        if len(modal_prediction) > 64:
            modal_prediction = f"{modal_prediction[:61]}..."
        lines.append(
            f"| {row['problem_id']} | {row['topic']} | {row['cluster']} | "
            f"{row['correct_rows']}/{row['rows']} | {row['parsed_rows']}/{row['rows']} | "
            f"{row['length_rows']} | `{modal_prediction}` | "
            f"{row['baseline_iter3000_correct_rows']} |"
        )
    scan = analysis["training_data_scan"]
    lines.extend(
        [
            "",
            "## Training Data Diagnosis",
            "",
            f"- Existing V3 verified full-solution sidecar rows read: `{scan['verified_full_solution_rows_read']}`.",
            f"- Estimated AIME/HMMT-style hard verified candidates: `{scan['hard_verified_candidate_rows']}` "
            f"({scan['hard_verified_candidate_rate']:.4%}).",
            f"- Existing V3 format-repair sampled rows read: `{scan['format_repair_rows_read']}`.",
            (
                "- Heuristic unparseable final segment count in sampled "
                "format-repair rows: "
                f"`{scan['format_repair_unparseable_final_segment_count']}`."
            ),
            "",
            "Hard candidate topics:",
            "",
            "| Topic | Rows |",
            "|---|---:|",
        ]
    )
    for topic, count in scan["hard_verified_topic_counts"].items():
        lines.append(f"| {topic} | {count} |")
    lines.extend(
        [
            "",
            "## Next Recipe",
            "",
            f"Run name: `{recipe['run_name']}`",
            "",
            "| Component | Setting |",
            "|---|---|",
            f"| Start checkpoint | `{recipe['base_model']['start_from']}` |",
            "| Hard verified sidecar | sample fraction `1.0`, blend weight `1.0` after prepack sampling |",
            "| Broad verified sidecar | sample fraction `0.25`, blend weight `1.0` after prepack sampling |",
            "| Format repair sidecar | disabled |",
            "| Final-answer auxiliary sidecar | disabled |",
            f"| LR | `{recipe['training']['optimizer_lr']}` with min `{recipe['training']['scheduler_min_lr']}` |",
            f"| Epochs | `{recipe['training']['epochs']}` |",
            f"| Eval/save interval | `{recipe['training']['eval_interval']}` |",
            "",
            "Promotion criteria:",
            "",
            (
                "- MMLU-Pro full accuracy at least "
                f"`{recipe['eval_gates']['promotion_gate']['mmlu_pro_full_min_accuracy']}`."
            ),
            f"- AIME25 full accuracy at least `{recipe['eval_gates']['promotion_gate']['aime25_full_min_accuracy']}`.",
            (
                "- HMMT full exact percent at least "
                f"`{recipe['eval_gates']['promotion_gate']['hmmt_full_min_exact_percent']}`."
            ),
            "",
            (
                "Execution note: use `hard_math_recovery_v4` as a pre-pack "
                "sampling strategy before packing. Do not train on AIME25/HMMT "
                "eval prompts or answers; use the failure clusters only as "
                "diagnostics and gate definitions."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def build_analysis(args: argparse.Namespace) -> tuple[JsonDict, JsonDict]:
    v3_rows = read_jsonl(args.v3_results)
    iter3000_rows = read_jsonl(args.iter3000_results)
    iter3000_by_sample = {str(row["sample_id"]): row for row in iter3000_rows}
    aime_lookup = load_aime_problem_map(args.aime_score_cache)
    hmmt_lookup = load_hmmt_problem_map(args.hmmt_jsonl)
    problem_lookup = {**aime_lookup, **hmmt_lookup}

    task_summary = {
        task: summarize_rows([row for row in v3_rows if row.get("task") == task])
        for task in ("aime25", "hmmt")
    }
    problem_summaries = summarize_by_problem(
        v3_rows,
        problem_lookup=problem_lookup,
        baseline_rows=iter3000_by_sample,
    )
    cluster_counts: dict[str, dict[str, JsonDict]] = defaultdict(dict)
    for task in ("aime25", "hmmt"):
        task_rows = [row for row in problem_summaries if row["task"] == task]
        for cluster, count in Counter(row["cluster"] for row in task_rows).items():
            cluster_counts[task][cluster] = {
                "problems": count,
                "rows": sum(row["rows"] for row in task_rows if row["cluster"] == cluster),
            }
    topic_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in problem_summaries:
        topic_counts[row["task"]][row["topic"]] += 1
    training_scan = inspect_training_recipe(args.m1_dir)
    analysis: JsonDict = {
        "inputs": {
            "v3_results": str(args.v3_results),
            "iter3000_results": str(args.iter3000_results),
            "aime_score_cache": str(args.aime_score_cache),
            "hmmt_jsonl": str(args.hmmt_jsonl),
            "m1_dir": str(args.m1_dir),
        },
        "task_summary": task_summary,
        "problem_summaries": problem_summaries,
        "cluster_counts": {
            task: dict(clusters) for task, clusters in sorted(cluster_counts.items())
        },
        "topic_counts": {
            task: dict(sorted(counts.items())) for task, counts in sorted(topic_counts.items())
        },
        "training_data_scan": training_scan,
    }
    recipe = build_recovery_recipe(training_scan)
    return analysis, recipe


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v3-results", type=Path, default=DEFAULT_V3_RESULTS)
    parser.add_argument("--iter3000-results", type=Path, default=DEFAULT_ITER3000_RESULTS)
    parser.add_argument("--aime-score-cache", type=Path, default=DEFAULT_AIME_SCORE_CACHE)
    parser.add_argument("--hmmt-jsonl", type=Path, default=DEFAULT_HMMT_JSONL)
    parser.add_argument("--m1-dir", type=Path, default=DEFAULT_M1_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Defaults to output-dir/qwen_v3_hard_math_failure_clusters_session68.json.",
    )
    parser.add_argument(
        "--recipe-out",
        type=Path,
        default=None,
        help="Defaults to output-dir/qwen_v4_hard_math_recovery_recipe_session68.json.",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=None,
        help="Defaults to output-dir/qwen_v3_hard_math_failure_analysis_session68.md.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    json_out = args.json_out or (
        args.output_dir / "qwen_v3_hard_math_failure_clusters_session68.json"
    )
    recipe_out = args.recipe_out or (
        args.output_dir / "qwen_v4_hard_math_recovery_recipe_session68.json"
    )
    markdown_out = args.markdown_out or (
        args.output_dir / "qwen_v3_hard_math_failure_analysis_session68.md"
    )
    analysis, recipe = build_analysis(args)
    write_json(json_out, analysis)
    write_json(recipe_out, recipe)
    write_text(markdown_out, render_markdown(analysis, recipe))
    print(f"analysis={json_out}")
    print(f"recipe={recipe_out}")
    print(f"markdown={markdown_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
