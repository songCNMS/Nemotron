#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 Agentic SFT v0 chat/tool data from M0 NeMo-Gym JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M0_INPUT_DIR: Path | None = None
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_agentic_sft_v0")
USED_IN_TAG = "super3_agentic_sft_v0"
MILESTONE = "M1"
TOOL_CALLING_SYSTEM_PROMPT = "You are a tool-using assistant. Use the available functions when needed."

JsonDict = dict[str, Any]


def read_jsonl(path: Path) -> list[JsonDict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            json.dump(row, f, ensure_ascii=False, sort_keys=True)
            f.write("\n")


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def normalize_tool_call(call: Any, *, fallback_id: str | None = None) -> JsonDict | None:
    if not isinstance(call, Mapping):
        return None
    function = call.get("function")
    if isinstance(function, Mapping):
        name = function.get("name")
        arguments = function.get("arguments", {})
    else:
        name = call.get("name")
        arguments = call.get("arguments", {})
    if isinstance(arguments, str):
        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError:
            parsed_arguments = {}
        arguments = parsed_arguments if isinstance(parsed_arguments, Mapping) else {}
    if not name:
        return None
    call_id = call.get("id")
    if not isinstance(call_id, str) or not call_id:
        call_id = fallback_id
    normalized: JsonDict = {
        "type": "function",
        "function": {
            "name": name,
            "arguments": arguments if isinstance(arguments, Mapping) else {},
        },
    }
    if call_id:
        normalized["id"] = call_id
    return normalized


def normalize_tools(tools: Any) -> list[JsonDict]:
    if not isinstance(tools, list):
        return []
    normalized = []
    for tool in tools:
        if isinstance(tool, Mapping):
            normalized.append(dict(tool))
    return normalized


def base_messages(record: Mapping[str, Any]) -> list[JsonDict]:
    params = record.get("responses_create_params", {})
    messages = params.get("input", [])
    if not isinstance(messages, list):
        raise ValueError("responses_create_params.input must be a list")
    converted = []
    for message in messages:
        if not isinstance(message, Mapping):
            continue
        role = message.get("role")
        content = message.get("content")
        if role in {"system", "user", "assistant", "tool"} and content is not None:
            converted.append({"role": role, "content": str(content)})
    if not converted or not any(message["role"] == "user" for message in converted):
        raise ValueError("M0 record must contain at least one user message")
    return converted


def prompt_messages(record: Mapping[str, Any], environment: str) -> list[JsonDict]:
    messages = base_messages(record)
    if environment != "general_tool_calling":
        return messages
    non_system_messages = [message for message in messages if message["role"] != "system"]
    return [{"role": "system", "content": TOOL_CALLING_SYSTEM_PROMPT}, *non_system_messages]


def assistant_for_search(record: Mapping[str, Any]) -> JsonDict:
    """Render a grounded SFT target instead of a bare short answer.

    plan §8 names "search pattern" as a v0 goal: the model should learn to
    attend to retrieved passages and acknowledge them, not just memorize the
    answer string. Wrap the M0 short answer in a template that references the
    titles named in `supporting_facts`, so the SFT supervision shapes a
    grounding habit even though the verifier still only checks the answer span.

    Returns an assistant message with empty content when `expected_answer` is
    missing — the global empty-supervision guard in `convert_m0_record` then
    refuses the row rather than emitting "Based on the retrieved passages, the
    answer is ." as a (technically non-empty) target.
    """
    expected_answer = str(record.get("expected_answer", "")).strip()
    if not expected_answer:
        return {"role": "assistant", "content": ""}
    titles = _supporting_fact_titles(record)
    if titles:
        evidence_line = ", ".join(f"[{i + 1}] {title}" for i, title in enumerate(titles))
        content = (
            f"Based on the retrieved passages ({evidence_line}), "
            f"the answer is {expected_answer}."
        )
    else:
        content = f"Based on the retrieved passages, the answer is {expected_answer}."
    return {"role": "assistant", "content": content}


def _supporting_fact_titles(record: Mapping[str, Any]) -> list[str]:
    extra = record.get("extra_env_info", {}) or {}
    supporting_facts = extra.get("supporting_facts")
    if not isinstance(supporting_facts, Mapping):
        return []
    raw_titles = supporting_facts.get("title")
    if not isinstance(raw_titles, list):
        return []
    seen: list[str] = []
    for title in raw_titles:
        text = str(title).strip()
        if text and text not in seen:
            seen.append(text)
    return seen


def assistant_for_code(record: Mapping[str, Any]) -> JsonDict:
    reference = record.get("extra_env_info", {}).get("reference_code")
    if reference is None:
        reference = record.get("expected_answer", "")
    return {"role": "assistant", "content": str(reference).strip()}


def assistant_for_reasoning(record: Mapping[str, Any]) -> JsonDict:
    # GSM8K's raw `answer` (M0 carries it as extra_env_info.reference_solution)
    # ends with the verifier marker `#### <number>`. If we put that string into
    # the SFT target verbatim, the model learns to literally emit `####` on
    # every reasoning task — that pattern then escapes GSM8K and shows up on
    # unrelated math prompts at inference. M0's `expected_answer` is the
    # already-normalized numeric answer (no `####`), so prefer it; fall back to
    # `reference_solution` only with the marker stripped.
    expected_answer = str(record.get("expected_answer", "")).strip()
    if expected_answer:
        return {"role": "assistant", "content": expected_answer}
    reference = record.get("extra_env_info", {}).get("reference_solution")
    if reference is None:
        reference = ""
    return {"role": "assistant", "content": _strip_gsm8k_marker(str(reference)).strip()}


_GSM8K_MARKER_RE = re.compile(r"####\s*")


def _strip_gsm8k_marker(text: str) -> str:
    return _GSM8K_MARKER_RE.sub("", text)


def assistant_for_tool_calling(record: Mapping[str, Any]) -> JsonDict:
    extra = record.get("extra_env_info", {})
    expected_calls = extra.get("expected_tool_calls") or record.get("expected_answer") or []
    if not isinstance(expected_calls, list):
        expected_calls = []
    tool_calls: list[JsonDict] = []
    for index, call in enumerate(expected_calls):
        normalized = normalize_tool_call(call, fallback_id=f"call_{index}")
        if normalized is not None:
            tool_calls.append(normalized)
    content = str(extra.get("expected_assistant_content") or "").strip()
    return {
        "role": "assistant",
        "content": content,
        "tool_calls": tool_calls,
    }


def trajectory_for_tool_calling(record: Mapping[str, Any]) -> list[JsonDict]:
    trajectory = record.get("extra_env_info", {}).get("expected_trajectory")
    if not isinstance(trajectory, list) or not trajectory:
        return [assistant_for_tool_calling(record)]

    messages: list[JsonDict] = []
    # Track outstanding assistant tool_call ids so the following `tool` turn(s)
    # can reference the right call via `tool_call_id`. Hermes interleaves
    # one tool result per assistant tool_call, so we consume ids in arrival
    # order, with `call_<assistant-index>_<call-index>` as a deterministic
    # fallback when the upstream trajectory left the id unset.
    pending_tool_call_ids: list[str] = []
    assistant_count = 0
    for turn in trajectory:
        if not isinstance(turn, Mapping):
            continue
        role = turn.get("role")
        content = turn.get("content")
        if role == "assistant":
            tool_calls = turn.get("tool_calls") or []
            if not isinstance(tool_calls, list):
                tool_calls = []
            normalized_calls: list[JsonDict] = []
            for call_index, call in enumerate(tool_calls):
                fallback_id = f"call_{assistant_count}_{call_index}"
                normalized = normalize_tool_call(call, fallback_id=fallback_id)
                if normalized is None:
                    continue
                normalized_calls.append(normalized)
                pending_tool_call_ids.append(str(normalized.get("id") or fallback_id))
            assistant_count += 1
            message: JsonDict = {"role": "assistant", "content": str(content or "").strip()}
            if normalized_calls:
                message["tool_calls"] = normalized_calls
            messages.append(message)
        elif role == "tool" and content is not None:
            tool_message: JsonDict = {"role": "tool", "content": str(content)}
            explicit_id = turn.get("tool_call_id")
            if isinstance(explicit_id, str) and explicit_id:
                tool_message["tool_call_id"] = explicit_id
            elif pending_tool_call_ids:
                tool_message["tool_call_id"] = pending_tool_call_ids.pop(0)
            messages.append(tool_message)
        elif role in {"user", "system"} and content is not None:
            messages.append({"role": str(role), "content": str(content)})

    return messages or [assistant_for_tool_calling(record)]


ASSISTANT_BUILDERS = {
    "search_grounded_qa": assistant_for_search,
    "code_execution_python": assistant_for_code,
    "math_reasoning_numeric": assistant_for_reasoning,
}


def m1_metadata(record: Mapping[str, Any], split: str) -> JsonDict:
    source_metadata = record.get("metadata", {})
    return {
        "m1_stage": "Agentic SFT v0",
        "m1_milestone": MILESTONE,
        "m1_use": [
            "tool call syntax",
            "search grounded answer format",
            "code solution format",
            "reasoning answer format",
        ],
        "m0_environment": record.get("environment"),
        "m0_split": split,
        "m0_source_dataset": source_metadata.get("source_dataset"),
        "m0_source_config": source_metadata.get("source_config"),
        "m0_source_revision": source_metadata.get("source_revision"),
        "m0_source_id": source_metadata.get("source_id"),
        "m0_source_row_index": source_metadata.get("source_row_index"),
        "license": source_metadata.get("license"),
        "domain": source_metadata.get("domain"),
        "reward_type": source_metadata.get("reward_type"),
        "contamination": source_metadata.get("contamination"),
    }


def convert_m0_record(record: Mapping[str, Any], *, split: str) -> JsonDict:
    environment = record.get("environment")
    environment_id = str(environment)
    if environment_id == "general_tool_calling":
        supervision_messages = trajectory_for_tool_calling(record)
    else:
        builder = ASSISTANT_BUILDERS.get(environment_id)
        if builder is None:
            raise ValueError(f"unsupported M0 environment: {environment}")
        supervision_messages = [builder(record)]
    if not supervision_messages:
        raise ValueError(f"unsupported M0 environment: {environment}")
    _ensure_assistant_supervision_non_empty(supervision_messages, environment_id=environment_id)
    messages = [*prompt_messages(record, environment_id), *supervision_messages]
    tools = normalize_tools(record.get("responses_create_params", {}).get("tools"))
    output = {
        "messages": messages,
        "tools": tools,
        "used_in": ["super3", USED_IN_TAG, "m1_agentic_sft_v0"],
        "metadata": m1_metadata(record, split),
    }
    return output


def _ensure_assistant_supervision_non_empty(
    supervision_messages: Sequence[Mapping[str, Any]],
    *,
    environment_id: str,
) -> None:
    """Refuse rows where the assistant target is empty across the board.

    M0 task001 already raises in transform_hermes_function_calling when a Hermes
    record has neither expected_tool_calls nor expected_assistant_content; we
    mirror that on the M1 side so reasoning / code / search rows with empty
    expected_answer (and empty reference_*) can't quietly write a `loss_mask=1`
    target of empty tokens.
    """
    has_assistant_signal = False
    for message in supervision_messages:
        if message.get("role") != "assistant":
            continue
        if str(message.get("content") or "").strip():
            has_assistant_signal = True
            break
        if message.get("tool_calls"):
            has_assistant_signal = True
            break
    if not has_assistant_signal:
        raise ValueError(
            f"M0 record for environment {environment_id!r} has no assistant content "
            "and no tool_calls; supervision target would be empty"
        )


def discover_m0_files(input_dir: Path) -> dict[str, dict[str, Path]]:
    files: dict[str, dict[str, Path]] = defaultdict(dict)
    for path in sorted(input_dir.glob("*/*-split.jsonl")):
        environment = path.parent.name
        split = path.name.replace("-split.jsonl", "")
        files[environment][split] = path
    return dict(files)


def convert_split(
    files_by_env: Mapping[str, Mapping[str, Path]],
    *,
    split: str,
    max_records_per_env: int | None,
) -> tuple[list[JsonDict], list[JsonDict]]:
    converted = []
    errors = []
    for environment, split_files in sorted(files_by_env.items()):
        path = split_files.get(split)
        if path is None:
            errors.append({"environment": environment, "split": split, "error": "missing split file"})
            continue
        rows = read_jsonl(path)
        if max_records_per_env is not None:
            rows = rows[:max_records_per_env]
        for row_index, record in enumerate(rows):
            try:
                converted.append(convert_m0_record(record, split=split))
            except Exception as exc:  # noqa: BLE001 - keep conversion running and report row-level issues.
                errors.append(
                    {
                        "environment": environment,
                        "split": split,
                        "row_index": row_index,
                        "error": str(exc),
                    }
                )
    return converted, errors


def build_blend(train_path: Path) -> JsonDict:
    return {
        "_comment": "M1 Agentic SFT v0 blend generated from M0 public smoke data. M0 val shadow is not included.",
        "datasets": [
            {
                "name": "m1-agentic-sft-v0-from-m0",
                "path": str(train_path),
                "weight": 1.0,
            }
        ],
    }


def count_by_environment(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        env = row.get("metadata", {}).get("m0_environment", "unknown")
        counts[str(env)] += 1
    return dict(sorted(counts.items()))


def check_output_paths(output_dir: Path, overwrite: bool) -> None:
    targets = [
        output_dir / "agentic_sft_v0_train.jsonl",
        output_dir / "agentic_sft_v0_val_shadow.jsonl",
        output_dir / "data_blend_agentic_sft_v0.json",
        output_dir / "manifest.json",
        output_dir / "report.md",
    ]
    existing = [path for path in targets if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"target files already exist; pass --overwrite to replace them:\n{formatted}")


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        "# M1 Agentic SFT v0 Data Report",
        "",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- M0 input directory: `{manifest['m0_input_dir']}`",
        f"- Output directory: `{manifest['output_dir']}`",
        f"- Training blend: `{manifest['blend_path']}`",
        "",
        "## Counts",
        "",
        "| Split | Environment | Rows |",
        "|---|---|---:|",
    ]
    for split in ("train", "val_shadow"):
        for environment, count in manifest["counts"][split].items():
            lines.append(f"| {split} | {environment} | {count} |")
    if manifest["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in manifest["errors"]:
            location = f"{error.get('environment', 'unknown')}/{error.get('split', 'unknown')}"
            lines.append(f"- `{location}`: {error['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(args: argparse.Namespace) -> JsonDict:
    if args.m0_input_dir is None:
        raise ValueError("--m0-input-dir is required")
    check_output_paths(args.output_dir, args.overwrite)
    files_by_env = discover_m0_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    train_rows, train_errors = convert_split(
        files_by_env,
        split="train",
        max_records_per_env=args.max_records_per_env,
    )
    val_rows, val_errors = convert_split(
        files_by_env,
        split="val",
        max_records_per_env=args.max_val_shadow_per_env,
    )

    train_path = args.output_dir / "agentic_sft_v0_train.jsonl"
    val_shadow_path = args.output_dir / "agentic_sft_v0_val_shadow.jsonl"
    blend_path = args.output_dir / "data_blend_agentic_sft_v0.json"
    write_jsonl(train_path, train_rows)
    write_jsonl(val_shadow_path, val_rows)
    write_json(blend_path, build_blend(train_path))

    manifest = {
        "schema_version": 1,
        "milestone": MILESTONE,
        "stage": "Agentic SFT v0",
        "used_in_tag": USED_IN_TAG,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "m0_input_dir": str(args.m0_input_dir),
        "output_dir": str(args.output_dir),
        "train_path": str(train_path),
        "val_shadow_path": str(val_shadow_path),
        "blend_path": str(blend_path),
        "counts": {
            "train": count_by_environment(train_rows),
            "val_shadow": count_by_environment(val_rows),
        },
        "errors": [*train_errors, *val_errors],
    }
    write_json(args.output_dir / "manifest.json", manifest)
    write_report(args.output_dir / "report.md", manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m0-input-dir", type=Path, default=DEFAULT_M0_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-records-per-env", type=int, default=None)
    parser.add_argument("--max-val-shadow-per-env", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare(args)
    except Exception as exc:  # noqa: BLE001 - CLI should render concise failures.
        print(f"prepare_m1_agentic_sft.py: error: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "train_rows": sum(manifest["counts"]["train"].values()),
                "val_shadow_rows": sum(manifest["counts"]["val_shadow"].values()),
                "blend_path": manifest["blend_path"],
                "errors": len(manifest["errors"]),
            },
            indent=2,
        )
    )
    return 0 if not manifest["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
