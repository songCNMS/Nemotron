#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Prepare M1 Agentic SFT v0 chat/tool data from M0 NeMo-Gym JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from nemotron.recipes.super3.milestones.lineage import (
        SFT_DATA_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from nemotron.recipes.super3.milestones.lineage import (
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    # Fallback for direct-script execution (PEP 723 banner enables that).
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
    from lineage import (  # type: ignore[no-redef]
        SFT_DATA_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from lineage import (  # type: ignore[no-redef]
        make_record as make_lineage_record,
    )

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_M0_INPUT_DIR: Path | None = None
DEFAULT_OUTPUT_DIR = Path("../output/super3/m1_agentic_sft_v0")
USED_IN_TAG = "super3_agentic_sft_v0"
MILESTONE = "M1"
TOOL_CALLING_SYSTEM_PROMPT = "You are a tool-using assistant. Use the available functions when needed."
MATH_FINAL_ANSWER_ENVIRONMENTS = frozenset(
    {
        "math_reasoning_numeric",
        "math_competition_numeric",
    }
)
MATH_FINAL_ANSWER_FORMAT = "boxed_final_line"
MATH_FINAL_ANSWER_SIDECAR_WEIGHT = 1.0
MATH_FINAL_ANSWER_EFFECTIVE_WEIGHT = 2.0
MATH_FINAL_ANSWER_SIDECAR_NAME = "m1-agentic-sft-v0-math-final-answer"
MATH_SUPERVISION_STRATEGY_V1 = "final_answer_sidecar_v1"
MATH_SUPERVISION_STRATEGY_V3 = "reasoning_replay_v3"
MATH_SUPERVISION_STRATEGY_V4 = "hard_math_recovery_v4"
MATH_SUPERVISION_STRATEGIES = (
    MATH_SUPERVISION_STRATEGY_V1,
    MATH_SUPERVISION_STRATEGY_V3,
    MATH_SUPERVISION_STRATEGY_V4,
)
MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION = "hard_verified_full_solution"
MATH_BUCKET_VERIFIED_FULL_SOLUTION = "verified_full_solution"
MATH_BUCKET_FINAL_ANSWER_AUX = "final_answer_aux"
MATH_BUCKET_FORMAT_REPAIR = "format_repair"
MATH_BUCKET_HELDOUT_EVAL = "heldout_eval"
MATH_V3_BUCKETS = (
    MATH_BUCKET_VERIFIED_FULL_SOLUTION,
    MATH_BUCKET_FINAL_ANSWER_AUX,
    MATH_BUCKET_FORMAT_REPAIR,
    MATH_BUCKET_HELDOUT_EVAL,
)
MATH_V4_BUCKETS = (
    MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION,
    MATH_BUCKET_VERIFIED_FULL_SOLUTION,
    MATH_BUCKET_FINAL_ANSWER_AUX,
    MATH_BUCKET_FORMAT_REPAIR,
    MATH_BUCKET_HELDOUT_EVAL,
)
MATH_ALL_BUCKETS = tuple(dict.fromkeys((*MATH_V3_BUCKETS, *MATH_V4_BUCKETS)))
MATH_V3_BUCKET_FILENAMES = {
    MATH_BUCKET_VERIFIED_FULL_SOLUTION: "agentic_sft_v0_math_verified_full_solution_train.jsonl",
    MATH_BUCKET_FINAL_ANSWER_AUX: "agentic_sft_v0_math_final_answer_aux_train.jsonl",
    MATH_BUCKET_FORMAT_REPAIR: "agentic_sft_v0_math_format_repair_train.jsonl",
    MATH_BUCKET_HELDOUT_EVAL: "agentic_sft_v0_math_heldout_eval.jsonl",
}
MATH_V4_BUCKET_FILENAMES = {
    MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION: (
        "agentic_sft_v0_math_hard_verified_full_solution_train.jsonl"
    ),
    MATH_BUCKET_VERIFIED_FULL_SOLUTION: "agentic_sft_v0_math_verified_full_solution_train.jsonl",
    MATH_BUCKET_FINAL_ANSWER_AUX: "agentic_sft_v0_math_final_answer_aux_train.jsonl",
    MATH_BUCKET_FORMAT_REPAIR: "agentic_sft_v0_math_format_repair_train.jsonl",
    MATH_BUCKET_HELDOUT_EVAL: "agentic_sft_v0_math_heldout_eval.jsonl",
}
MATH_V3_BUCKET_DATASET_NAMES = {
    MATH_BUCKET_VERIFIED_FULL_SOLUTION: "m1-agentic-sft-v0-math-verified-full-solution",
    MATH_BUCKET_FINAL_ANSWER_AUX: "m1-agentic-sft-v0-math-final-answer-aux",
    MATH_BUCKET_FORMAT_REPAIR: "m1-agentic-sft-v0-math-format-repair",
}
MATH_V4_BUCKET_DATASET_NAMES = {
    MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION: (
        "m1-agentic-sft-v0-math-hard-verified-full-solution"
    ),
    **MATH_V3_BUCKET_DATASET_NAMES,
}
MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT = 1.0
MATH_V3_FINAL_ANSWER_AUX_WEIGHT = 0.2
MATH_V3_FORMAT_REPAIR_WEIGHT = 0.05
MATH_V4_HARD_VERIFIED_FULL_SOLUTION_WEIGHT = 1.0
MATH_V4_VERIFIED_FULL_SOLUTION_WEIGHT = 0.25
MATH_V4_FINAL_ANSWER_AUX_WEIGHT = 0.0
MATH_V4_FORMAT_REPAIR_WEIGHT = 0.0
MATH_V4_ANSWER_SEEKING_PATTERNS = (
    "compute",
    "determine",
    "evaluate",
    "find",
    "how many",
    "what is",
)
MATH_V4_PROOF_LIKE_PATTERNS = (
    "prove",
    "show that",
)
MATH_V4_TOPIC_KEYWORDS = (
    "angle",
    "area",
    "circle",
    "choose",
    "combin",
    "congru",
    "digit",
    "divisor",
    "equation",
    "factor",
    "function",
    "integer",
    "log",
    "mod",
    "point",
    "polynomial",
    "prime",
    "probability",
    "radius",
    "remainder",
    "sqrt",
    "system",
    "tangent",
    "triangle",
    "ways",
)

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


_TOOL_CALL_OR_TOOLS_RE = re.compile(
    r"<(tool_call|tools)>.*?</\1>\s*", re.DOTALL | re.IGNORECASE
)


def _scrub_tool_call_xml(text: str) -> str:
    """Strip Hermes-style ``<tool_call>...</tool_call>`` and ``<tools>...</tools>``
    blocks from user content.

    The tool schema is delivered via the OpenAI-style ``tools`` field that the
    chat template injects on its own; leaving demo / example tool-call XML in
    the user message would teach the model to echo the example or interpret
    user-typed XML as a real call. Mirrors the system-side scrub
    (``TOOL_CALLING_SYSTEM_PROMPT``) but for the user turn so the cleanup is
    symmetric.
    """
    return _TOOL_CALL_OR_TOOLS_RE.sub("", text).strip()


def prompt_messages(record: Mapping[str, Any], environment: str) -> list[JsonDict]:
    messages = base_messages(record)
    if environment not in _TOOL_CALLING_ENVIRONMENTS:
        return messages
    cleaned: list[JsonDict] = []
    for message in messages:
        if message["role"] == "system":
            continue
        if message["role"] == "user":
            cleaned.append({"role": "user", "content": _scrub_tool_call_xml(message["content"])})
        else:
            cleaned.append(message)
    return [{"role": "system", "content": TOOL_CALLING_SYSTEM_PROMPT}, *cleaned]


# Environments that share the multi-turn tool-trajectory supervision builder
# instead of a per-env `assistant_for_*` function. Both single-turn and
# multi-turn Hermes envs route through `trajectory_for_tool_calling` and the
# tool-calling system-prompt + user-content scrub above. Declared up here so
# `prompt_messages` can reference it before `ASSISTANT_BUILDERS` is built.
_TOOL_CALLING_ENVIRONMENTS = frozenset({"general_tool_calling", "multi_turn_tool_use"})


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
    """Return de-duplicated supporting-passage titles for a search record.

    HotpotQA carries them under ``extra_env_info.supporting_facts.title``
    (dict shape from the HF loader). MuSiQue carries them under
    ``extra_env_info.supporting_titles`` (flat list, derived from each
    paragraph's ``is_supporting`` flag at M0-prep time). Both shapes feed
    the same M1 grounded-template builder.
    """
    extra = record.get("extra_env_info", {}) or {}
    raw_titles: Any = None
    supporting_facts = extra.get("supporting_facts")
    if isinstance(supporting_facts, Mapping):
        raw_titles = supporting_facts.get("title")
    elif isinstance(extra.get("supporting_titles"), list):
        raw_titles = extra["supporting_titles"]
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
    expected_answer = str(record.get("expected_answer", "")).strip()
    reference = record.get("extra_env_info", {}).get("reference_solution")
    if reference is not None and str(reference).strip():
        return {
            "role": "assistant",
            "content": _reasoning_target_from_reference(str(reference), expected_answer),
        }
    if expected_answer:
        return {"role": "assistant", "content": f"Final answer: {_boxed_final_answer(expected_answer)}"}
    return {"role": "assistant", "content": expected_answer}


_GSM8K_MARKER_RE = re.compile(r"####\s*")
_BOXED_ANSWER_FULL_RE = re.compile(r"^\\+boxed\s*\{(?P<answer>.*)\}$", re.DOTALL)


def _strip_gsm8k_marker(text: str) -> str:
    return _GSM8K_MARKER_RE.sub("", text)


def _unbox_expected_answer(expected_answer: str) -> str:
    expected_answer = expected_answer.strip()
    match = _BOXED_ANSWER_FULL_RE.match(expected_answer)
    if match:
        return match.group("answer").strip()
    return expected_answer


def _boxed_final_answer(expected_answer: str) -> str:
    return f"\\boxed{{{_unbox_expected_answer(expected_answer)}}}"


def _compact_math_text(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _contains_boxed_expected_answer(content: str, expected_answer: str) -> bool:
    if not expected_answer.strip():
        return False
    compact_content = _compact_math_text(content)
    compact_boxed = _compact_math_text(_boxed_final_answer(expected_answer))
    return compact_boxed in compact_content


def _remove_boxed_spans(text: str) -> str:
    return re.sub(r"\\+boxed\s*\{[^{}]*\}", " ", text)


def _has_reasoning_trace(reference_solution: str, expected_answer: str) -> bool:
    """Heuristic for separating real solution traces from answer-only rows."""
    content = _strip_gsm8k_marker(reference_solution).strip()
    if not content:
        return False
    reduced = _remove_boxed_spans(content)
    for value in {
        expected_answer,
        _unbox_expected_answer(expected_answer),
        _boxed_final_answer(expected_answer),
    }:
        value = value.strip()
        if value:
            reduced = reduced.replace(value, " ")
    reduced = re.sub(r"(?i)\bfinal\s+answer\b\s*:?", " ", reduced)
    reduced = re.sub(r"\s+", " ", reduced).strip()
    if not reduced:
        return False
    if len(reduced) >= 32:
        return True
    return len(re.findall(r"[A-Za-z]{2,}|[=+\-*/^]", reduced)) >= 3


def classify_math_supervision_bucket(record: Mapping[str, Any]) -> str | None:
    env_id = str(record.get("environment", ""))
    if env_id not in MATH_FINAL_ANSWER_ENVIRONMENTS:
        return None
    expected_answer = str(record.get("expected_answer", "")).strip()
    reference = str(record.get("extra_env_info", {}).get("reference_solution") or "").strip()
    if reference and _has_reasoning_trace(reference, expected_answer):
        if expected_answer and _contains_boxed_expected_answer(reference, expected_answer):
            return MATH_BUCKET_VERIFIED_FULL_SOLUTION
        return MATH_BUCKET_FORMAT_REPAIR
    if env_id == "math_competition_numeric" and not reference:
        return MATH_BUCKET_HELDOUT_EVAL
    return MATH_BUCKET_FINAL_ANSWER_AUX


def _message_content(row: Mapping[str, Any], role: str) -> str:
    messages = row.get("messages")
    if not isinstance(messages, list):
        return ""
    for message in messages:
        if isinstance(message, Mapping) and message.get("role") == role:
            return str(message.get("content", ""))
    return ""


def is_hard_math_recovery_row(row: Mapping[str, Any]) -> bool:
    metadata = row.get("metadata")
    if not isinstance(metadata, Mapping):
        return False
    if metadata.get("m0_environment") != "math_competition_numeric":
        return False
    prompt = _message_content(row, "user")
    solution = _message_content(row, "assistant")
    lower_prompt = prompt.lower()
    if any(pattern in lower_prompt for pattern in MATH_V4_PROOF_LIKE_PATTERNS):
        return False
    if not any(pattern in lower_prompt for pattern in MATH_V4_ANSWER_SEEKING_PATTERNS):
        return False
    if len(prompt) < 80 or len(solution) < 700 or len(solution) > 12000:
        return False
    lower_text = f"{prompt}\n{solution}".lower()
    return any(keyword in lower_text for keyword in MATH_V4_TOPIC_KEYWORDS)


def _reasoning_target_from_reference(reference_solution: str, expected_answer: str) -> str:
    """Preserve solution traces while enforcing parser-readable math finals."""
    content = _strip_gsm8k_marker(reference_solution).strip()
    expected_answer = expected_answer.strip()
    if expected_answer and not _contains_boxed_expected_answer(content, expected_answer):
        boxed_answer = _boxed_final_answer(expected_answer)
        if content:
            content = f"{content}\n\nFinal answer: {boxed_answer}"
        else:
            content = f"Final answer: {boxed_answer}"
    return content


def assistant_for_structured_output(record: Mapping[str, Any]) -> JsonDict:
    expected = record.get("expected_answer", "")
    if not str(expected).strip():
        expected = record.get("extra_env_info", {}).get("expected_json", "")
    if isinstance(expected, str):
        try:
            expected = json.loads(expected)
        except json.JSONDecodeError:
            return {"role": "assistant", "content": expected.strip()}
    if isinstance(expected, (Mapping, list)):
        return {"role": "assistant", "content": json.dumps(expected, ensure_ascii=False)}
    return {"role": "assistant", "content": str(expected).strip()}


def assistant_for_terminal(record: Mapping[str, Any]) -> JsonDict:
    command = record.get("extra_env_info", {}).get("expected_command")
    if command is None:
        command = record.get("expected_answer", "")
    return {"role": "assistant", "content": str(command).strip()}


def assistant_for_swe_patch(record: Mapping[str, Any]) -> JsonDict:
    patch = record.get("extra_env_info", {}).get("gold_patch")
    if patch is None:
        patch = record.get("expected_answer", "")
    return {"role": "assistant", "content": str(patch).strip()}


def assistant_for_lean_proof(record: Mapping[str, Any]) -> JsonDict:
    """SFT target for ``math_formal_lean``: the gold Lean proof body.

    Source-agnostic — works against any Lean dataset whose M0 transform
    is ``transform_lean_proof_stub``. The transform puts the gold proof
    in ``expected_answer`` (canonical) and also in
    ``extra_env_info.reference_proof`` (defensive copy); we prefer the
    canonical path so re-prep with a different source flows through
    without touching this builder.
    """
    proof = str(record.get("expected_answer") or "").strip()
    if not proof:
        proof = str(record.get("extra_env_info", {}).get("reference_proof", "")).strip()
    return {"role": "assistant", "content": proof}


def assistant_for_tool_call_repair(record: Mapping[str, Any]) -> JsonDict:
    extra = record.get("extra_env_info", {})
    expected_answer = record.get("expected_answer")
    expected_calls = extra.get("repair_target")
    if expected_calls is None and isinstance(expected_answer, Mapping):
        expected_calls = expected_answer.get("tool_calls", [])
    if not isinstance(expected_calls, list):
        expected_calls = []
    tool_calls: list[JsonDict] = []
    for index, call in enumerate(expected_calls):
        normalized = normalize_tool_call(call, fallback_id=f"repair_call_{index}")
        if normalized is not None:
            tool_calls.append(normalized)
    content = str(extra.get("expected_assistant_content") or "").strip()
    return {
        "role": "assistant",
        "content": content,
        "tool_calls": tool_calls,
    }


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
    # MuSiQue's `supporting_titles` flat list also feeds the grounded
    # search template; `_supporting_fact_titles` accepts both shapes.
    "search_multihop_qa": assistant_for_search,
    "code_execution_python": assistant_for_code,
    "terminal_basic_shell": assistant_for_terminal,
    "swe_pivot_patch_supervision": assistant_for_swe_patch,
    "structured_outputs_json": assistant_for_structured_output,
    "tool_call_repair_negative": assistant_for_tool_call_repair,
    "math_reasoning_numeric": assistant_for_reasoning,
    # NuminaMath competition math reuses `assistant_for_reasoning`; when
    # reference_solution is present the builder preserves the solution path
    # instead of training only on the extracted boxed answer.
    "math_competition_numeric": assistant_for_reasoning,
    # math_formal_lean uses a dedicated builder so the Lean proof text
    # passes through verbatim — no boxed-answer extraction, no marker
    # stripping (Lean proof syntax must stay literal).
    "math_formal_lean": assistant_for_lean_proof,
}


# Per-environment supervision targets, aligned with plan §8 v0 goals. Each
# record only carries the capability tag for the env it actually exercises, so
# downstream curriculum samplers can stratify by skill instead of treating
# every record as covering all four areas.
M1_USE_BY_ENV: dict[str, list[str]] = {
    "search_grounded_qa": ["search pattern"],
    "search_multihop_qa": ["search pattern", "multi-hop reasoning"],
    "code_execution_python": ["code solution format", "structured output"],
    "terminal_basic_shell": ["terminal basics"],
    "swe_pivot_patch_supervision": ["short SWE traces"],
    "general_tool_calling": ["tool call syntax"],
    "multi_turn_tool_use": ["tool call syntax", "multi-turn tool trace"],
    "structured_outputs_json": ["structured output"],
    "tool_call_repair_negative": ["malformed tool call negatives", "hallucinated tool output negatives"],
    "math_reasoning_numeric": ["reasoning answer format"],
    "math_competition_numeric": ["reasoning answer format", "competition math"],
    "math_formal_lean": ["formal-proof syntax", "Lean tactic-style proof"],
}


def _m1_use_for_env(env_id: str) -> list[str]:
    return list(M1_USE_BY_ENV.get(env_id, ["unknown"]))


def _math_final_answer_supervision(env_id: str) -> JsonDict | None:
    if env_id not in MATH_FINAL_ANSWER_ENVIRONMENTS:
        return None
    return {
        "format": MATH_FINAL_ANSWER_FORMAT,
        "target_template": "Final answer: \\boxed{expected_answer}",
        "base_blend_weight": 1.0,
        "sidecar_blend_weight": MATH_FINAL_ANSWER_SIDECAR_WEIGHT,
        "effective_weight": MATH_FINAL_ANSWER_EFFECTIVE_WEIGHT,
    }


DIFFICULTY_UNKNOWN = "unknown"
DIFFICULTY_TRIVIAL = "trivial"
DIFFICULTY_HARD = "hard"


def load_difficulty_signal(path: Path | None) -> dict[tuple[str, str, int], str]:
    """Read M0 health_baseline_report.json into a per-row difficulty map.

    plan §6 calls out difficulty curriculum / pass-rate filtering as a v0 → v1
    lever. The oracle baseline is the only signal we have at SFT-prep time —
    cheap, deterministic, and already produced by `run_m0_health_baseline.py`.

    Mapping:
      (env_id, split, row_index) → ``"trivial"`` when oracle passed,
                                   ``"hard"`` when oracle failed.

    Rows whose oracle bucket cannot be determined (no report, missing env,
    truncated `failures` list capped at 20 by evaluate_policy) are left
    unmapped; callers fall back to ``"unknown"`` for those.
    """
    if path is None:
        return {}
    if not path.is_file():
        logger.warning(
            "M0 health baseline report not found at %s; every M1 SFT row will be tagged difficulty=unknown",
            path,
        )
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        # Silent failure here used to hide bad / truncated baseline files: every
        # row would be tagged difficulty=unknown with no signal to the operator.
        # Surface the underlying error so the misconfiguration is visible.
        logger.warning(
            "M0 health baseline at %s could not be parsed (%s: %s); falling back to difficulty=unknown",
            path,
            type(exc).__name__,
            exc,
        )
        return {}
    out: dict[tuple[str, str, int], str] = {}
    if not isinstance(report, Mapping):
        logger.warning(
            "M0 health baseline at %s did not contain a JSON object; falling back to difficulty=unknown",
            path,
        )
        return out
    envs = report.get("baselines", {}).get("environments", {})
    if not isinstance(envs, Mapping):
        logger.warning(
            "M0 health baseline at %s has no `baselines.environments` mapping; falling back to difficulty=unknown",
            path,
        )
        return out
    for env_id, env_data in envs.items():
        if not isinstance(env_data, Mapping):
            continue
        splits = env_data.get("splits")
        if not isinstance(splits, Mapping):
            continue
        for split_name, policies in splits.items():
            if not isinstance(policies, Mapping):
                continue
            oracle = policies.get("oracle")
            if not isinstance(oracle, Mapping):
                continue
            scored_rows = int(oracle.get("scored_rows") or 0)
            if scored_rows <= 0:
                continue
            failures = oracle.get("failures") or []
            failure_count = int(oracle.get("failure_count") or 0)
            failed_indices: set[int] = set()
            for failure in failures:
                if not isinstance(failure, Mapping):
                    continue
                row_idx = failure.get("row_index")
                if isinstance(row_idx, int):
                    failed_indices.add(row_idx)
            # `evaluate_policy` caps `failures` at the first 20 rows. Only mark
            # rows trivial when we know we have every failed index — otherwise
            # they stay unmapped (caller renders as "unknown").
            all_failures_listed = len(failed_indices) >= failure_count
            total_rows = int(oracle.get("rows") or 0)
            for idx in range(total_rows):
                if idx in failed_indices:
                    out[(str(env_id), str(split_name), idx)] = DIFFICULTY_HARD
                elif all_failures_listed:
                    out[(str(env_id), str(split_name), idx)] = DIFFICULTY_TRIVIAL
    return out


def _difficulty_for(
    record: Mapping[str, Any],
    *,
    split: str,
    row_index: int | None,
    difficulty_signal: Mapping[tuple[str, str, int], str] | None,
) -> str:
    if difficulty_signal is None or row_index is None:
        return DIFFICULTY_UNKNOWN
    env_id = str(record.get("environment", ""))
    # `difficulty_signal` is keyed by M0 split names (`train` / `val`). The
    # converter passes the M0 split verbatim (`"train"` or `"val"`); the
    # `"val_shadow"` tag is applied during manifest summarization,
    # so we never look up by `"val_shadow"` here.
    return difficulty_signal.get((env_id, split, row_index), DIFFICULTY_UNKNOWN)


def m1_metadata(
    record: Mapping[str, Any],
    split: str,
    *,
    row_index: int | None = None,
    difficulty_signal: Mapping[tuple[str, str, int], str] | None = None,
    math_supervision_bucket: str | None = None,
) -> JsonDict:
    source_metadata = record.get("metadata", {})
    env_id = str(record.get("environment", ""))
    # P3 #12: preserve the M0 stage lineage (e.g. ["M0 data_env_foundation",
    # "M1 RLVR …"]) so downstream contamination / curriculum tooling can still
    # see which M0 stages this row was tagged for, even after we overwrite the
    # top-level `used_in` with the M1-specific tags.
    m0_use_stage = record.get("used_in")
    if not isinstance(m0_use_stage, list):
        m0_use_stage = record.get("use_stage")
    if not isinstance(m0_use_stage, list):
        m0_use_stage = []
    metadata = {
        "m1_stage": "Agentic SFT v0",
        "m1_milestone": MILESTONE,
        "m1_use": _m1_use_for_env(env_id),
        "difficulty_bucket": _difficulty_for(
            record, split=split, row_index=row_index, difficulty_signal=difficulty_signal
        ),
        "m0_environment": record.get("environment"),
        "m0_split": split,
        "m0_use_stage": list(m0_use_stage),
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
    final_answer_supervision = _math_final_answer_supervision(env_id)
    if final_answer_supervision is not None:
        metadata["final_answer_supervision"] = final_answer_supervision
    if math_supervision_bucket is not None:
        metadata["math_supervision_bucket"] = math_supervision_bucket
    return metadata


def convert_m0_record(
    record: Mapping[str, Any],
    *,
    split: str,
    row_index: int | None = None,
    difficulty_signal: Mapping[tuple[str, str, int], str] | None = None,
) -> JsonDict:
    environment = record.get("environment")
    environment_id = str(environment)
    math_supervision_bucket = classify_math_supervision_bucket(record)
    if environment_id in _TOOL_CALLING_ENVIRONMENTS:
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
        "metadata": m1_metadata(
            record,
            split,
            row_index=row_index,
            difficulty_signal=difficulty_signal,
            math_supervision_bucket=math_supervision_bucket,
        ),
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
    difficulty_signal: Mapping[tuple[str, str, int], str] | None = None,
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
                converted.append(
                    convert_m0_record(
                        record,
                        split=split,
                        row_index=row_index,
                        difficulty_signal=difficulty_signal,
                    )
                )
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


def _is_math_final_answer_row(row: Mapping[str, Any]) -> bool:
    env = str(row.get("metadata", {}).get("m0_environment", ""))
    return env in MATH_FINAL_ANSWER_ENVIRONMENTS


def _math_supervision_bucket(row: Mapping[str, Any]) -> str | None:
    bucket = row.get("metadata", {}).get("math_supervision_bucket")
    if isinstance(bucket, str) and bucket in MATH_ALL_BUCKETS:
        return bucket
    return None


def _math_buckets_for_strategy(strategy: str) -> tuple[str, ...]:
    if strategy == MATH_SUPERVISION_STRATEGY_V4:
        return MATH_V4_BUCKETS
    return MATH_V3_BUCKETS


def _math_bucket_filenames_for_strategy(strategy: str) -> dict[str, str]:
    if strategy == MATH_SUPERVISION_STRATEGY_V4:
        return dict(MATH_V4_BUCKET_FILENAMES)
    return dict(MATH_V3_BUCKET_FILENAMES)


def split_math_supervision_buckets(
    train_rows: Sequence[Mapping[str, Any]],
    val_rows: Sequence[Mapping[str, Any]] = (),
    *,
    buckets: Sequence[str] = MATH_V3_BUCKETS,
) -> dict[str, list[Mapping[str, Any]]]:
    split: dict[str, list[Mapping[str, Any]]] = {bucket: [] for bucket in buckets}
    for row in train_rows:
        bucket = _math_supervision_bucket(row)
        if bucket is not None and bucket in split:
            split[bucket].append(row)
    for row in val_rows:
        if _is_math_final_answer_row(row):
            split[MATH_BUCKET_HELDOUT_EVAL].append(row)
    return split


def filter_v3_training_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if _math_supervision_bucket(row) != MATH_BUCKET_HELDOUT_EVAL
    ]


def count_math_supervision_buckets(
    rows: Sequence[Mapping[str, Any]],
    *,
    buckets: Sequence[str] = MATH_V3_BUCKETS,
) -> dict[str, int]:
    counts: dict[str, int] = {bucket: 0 for bucket in buckets}
    for row in rows:
        bucket = _math_supervision_bucket(row)
        if bucket is not None and bucket in counts:
            counts[bucket] += 1
    return {bucket: count for bucket, count in counts.items() if count}


def sample_rows_by_fraction(
    rows: Sequence[Mapping[str, Any]],
    *,
    fraction: float,
    salt: str,
) -> list[Mapping[str, Any]]:
    if not rows or fraction <= 0.0:
        return []
    if fraction >= 1.0:
        return list(rows)
    target = max(1, round(len(rows) * fraction))
    ranked: list[tuple[str, int]] = []
    for index, row in enumerate(rows):
        metadata = row.get("metadata", {})
        identity = {
            "salt": salt,
            "index": index,
            "source_id": metadata.get("m0_source_id") if isinstance(metadata, Mapping) else None,
            "source_row_index": metadata.get("m0_source_row_index") if isinstance(metadata, Mapping) else None,
            "environment": metadata.get("m0_environment") if isinstance(metadata, Mapping) else None,
        }
        digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
        ranked.append((digest, index))
    selected = {index for _, index in sorted(ranked)[:target]}
    return [row for index, row in enumerate(rows) if index in selected]


def apply_math_supervision_strategy_metadata(
    rows: Sequence[Mapping[str, Any]],
    *,
    strategy: str,
    bucket_weights: Mapping[str, float] | None = None,
) -> None:
    bucket_weights = bucket_weights or {}
    for row in rows:
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            continue
        supervision = metadata.get("final_answer_supervision")
        if not isinstance(supervision, dict):
            continue
        supervision["strategy"] = strategy
        if strategy not in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
            continue
        bucket = (
            MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION
            if strategy == MATH_SUPERVISION_STRATEGY_V4
            and _math_supervision_bucket(row) == MATH_BUCKET_VERIFIED_FULL_SOLUTION
            and is_hard_math_recovery_row(row)
            else _math_supervision_bucket(row)
        )
        if isinstance(metadata, dict) and bucket is not None:
            metadata["math_supervision_bucket"] = bucket
        sidecar_weight = float(bucket_weights.get(bucket or "", 0.0))
        if bucket == MATH_BUCKET_HELDOUT_EVAL or metadata.get("m0_split") != "train":
            sidecar_weight = 0.0
        supervision["sidecar_blend_weight"] = sidecar_weight
        supervision["effective_weight"] = 1.0 + sidecar_weight


def build_blend(
    train_path: Path,
    *,
    math_final_answer_train_path: Path | None = None,
    math_final_answer_weight: float = MATH_FINAL_ANSWER_SIDECAR_WEIGHT,
    extra_datasets: Sequence[Mapping[str, Any]] = (),
    comment: str | None = None,
) -> JsonDict:
    datasets: list[JsonDict] = [
        {
            "name": "m1-agentic-sft-v0-from-m0",
            "path": str(train_path),
            "weight": 1.0,
        }
    ]
    if math_final_answer_train_path is not None and math_final_answer_weight > 0.0:
        datasets.append(
            {
                "name": MATH_FINAL_ANSWER_SIDECAR_NAME,
                "path": str(math_final_answer_train_path),
                "weight": float(math_final_answer_weight),
            }
        )
    for dataset in extra_datasets:
        datasets.append(dict(dataset))
    return {
        "_comment": comment or (
            "M1 Agentic SFT v0 blend generated from M0 public data. "
            "M0 val shadow is not included. Numeric math rows are duplicated "
            "into the math-final-answer sidecar when present so boxed final-answer "
            "supervision gets an extra training weight."
        ),
        "datasets": datasets,
    }


def _math_v3_weights(args: argparse.Namespace) -> dict[str, float]:
    return {
        MATH_BUCKET_VERIFIED_FULL_SOLUTION: float(
            getattr(args, "math_v3_verified_full_solution_weight", MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT)
        ),
        MATH_BUCKET_FINAL_ANSWER_AUX: float(
            getattr(args, "math_v3_final_answer_aux_weight", MATH_V3_FINAL_ANSWER_AUX_WEIGHT)
        ),
        MATH_BUCKET_FORMAT_REPAIR: float(
            getattr(args, "math_v3_format_repair_weight", MATH_V3_FORMAT_REPAIR_WEIGHT)
        ),
    }


def _math_v4_weights(args: argparse.Namespace) -> dict[str, float]:
    return {
        MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION: float(
            getattr(
                args,
                "math_v4_hard_verified_full_solution_weight",
                MATH_V4_HARD_VERIFIED_FULL_SOLUTION_WEIGHT,
            )
        ),
        MATH_BUCKET_VERIFIED_FULL_SOLUTION: float(
            getattr(
                args,
                "math_v4_verified_full_solution_weight",
                MATH_V4_VERIFIED_FULL_SOLUTION_WEIGHT,
            )
        ),
        MATH_BUCKET_FINAL_ANSWER_AUX: float(
            getattr(args, "math_v4_final_answer_aux_weight", MATH_V4_FINAL_ANSWER_AUX_WEIGHT)
        ),
        MATH_BUCKET_FORMAT_REPAIR: float(
            getattr(args, "math_v4_format_repair_weight", MATH_V4_FORMAT_REPAIR_WEIGHT)
        ),
    }


def _math_weights_for_strategy(args: argparse.Namespace, strategy: str) -> dict[str, float]:
    if strategy == MATH_SUPERVISION_STRATEGY_V4:
        return _math_v4_weights(args)
    return _math_v3_weights(args)


def build_math_strategy_blend(
    train_path: Path,
    *,
    strategy: str,
    bucket_paths: Mapping[str, Path],
    bucket_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    bucket_weights: Mapping[str, float],
) -> JsonDict:
    extra_datasets: list[JsonDict] = []
    bucket_names = (
        MATH_V4_BUCKET_DATASET_NAMES
        if strategy == MATH_SUPERVISION_STRATEGY_V4
        else MATH_V3_BUCKET_DATASET_NAMES
    )
    for bucket in _math_buckets_for_strategy(strategy):
        if bucket == MATH_BUCKET_HELDOUT_EVAL:
            continue
        rows = bucket_rows.get(bucket, ())
        if not rows:
            continue
        extra_datasets.append(
            {
                "name": bucket_names[bucket],
                "path": str(bucket_paths[bucket]),
                "weight": 1.0,
            }
        )
    comment = (
        "M1 Agentic SFT v0 hard_math_recovery_v4 blend. The base train JSONL "
        "keeps agentic coverage; hard AIME/HMMT-style verified solution traces "
        "are duplicated as a focused sidecar; broad verified math replay is "
        "downsampled; final-answer-only and format-repair rows are disabled by "
        "default because V3 failures were reasoning-correctness failures."
        if strategy == MATH_SUPERVISION_STRATEGY_V4
        else (
            "M1 Agentic SFT v0 reasoning_replay_v3 blend. The base train JSONL "
            "keeps normal agentic SFT coverage; verified math solution traces, "
            "low-weight final-answer auxiliary rows, and low-weight format-repair "
            "rows are separate sidecars. Held-out math rows are written for eval "
            "and excluded from the training blend."
        )
    )
    return build_blend(
        train_path,
        extra_datasets=extra_datasets,
        comment=comment,
    )


def build_math_v3_blend(
    train_path: Path,
    *,
    bucket_paths: Mapping[str, Path],
    bucket_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    bucket_weights: Mapping[str, float],
) -> JsonDict:
    return build_math_strategy_blend(
        train_path,
        strategy=MATH_SUPERVISION_STRATEGY_V3,
        bucket_paths=bucket_paths,
        bucket_rows=bucket_rows,
        bucket_weights=bucket_weights,
    )


def count_by_environment(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        env = row.get("metadata", {}).get("m0_environment", "unknown")
        counts[str(env)] += 1
    return dict(sorted(counts.items()))


def count_difficulty_buckets(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        bucket = row.get("metadata", {}).get("difficulty_bucket", DIFFICULTY_UNKNOWN)
        counts[str(bucket)] += 1
    return dict(sorted(counts.items()))


def _apply_curriculum_to_train(
    train_rows: Sequence[Mapping[str, Any]],
    *,
    policy: str = "as_is",
    seed: int = 0,
    pass_rates_path: Path | None = None,
    solved_threshold: float = 0.9,
) -> tuple[list[Mapping[str, Any]], JsonDict]:
    """Apply the task040 W1 curriculum sampler to *train_rows*.

    Returns ``(reordered_rows, audit_dict)``. The audit dict carries
    the inputs + outcome so the manifest can record what was applied:

    - ``policy``: the policy that ran (matches the CLI flag value)
    - ``seed``: rng seed used (only meaningful for ``shuffle``)
    - ``pass_rates_provided``: whether a pass-rates JSON was loaded
    - ``solved_threshold``: threshold used for ``filter_solved``
    - ``rows_in`` / ``rows_out``: count before + after filtering
    - ``rows_dropped_solved``: count of rows the pass-rate filter dropped

    Sandbox-runnable; back-compat: with default ``as_is`` policy and no
    pass-rates JSON, this is a passthrough (rows_in == rows_out, no
    reordering).
    """
    import json as _json
    import random

    from nemotron.recipes.super3.milestones.m0_data_env.difficulty_sampler import (
        bucket_rows,
        filter_solved,
    )

    rows_list = list(train_rows)
    rows_in = len(rows_list)

    pass_rates: Mapping[str, float] | None = None
    if pass_rates_path is not None:
        if not pass_rates_path.is_file():
            raise FileNotFoundError(
                f"--curriculum-pass-rates-json not found: {pass_rates_path}"
            )
        with pass_rates_path.open(encoding="utf-8") as f:
            raw = _json.load(f)
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"{pass_rates_path}: pass-rates JSON must be an object mapping row_id → float"
            )
        pass_rates = {str(k): float(v) for k, v in raw.items()}

    rows_after_filter = filter_solved(
        rows_list, pass_rates=pass_rates, threshold=solved_threshold
    )
    rows_dropped = rows_in - len(rows_after_filter)

    rng = random.Random(seed) if policy == "shuffle" else None
    reordered = bucket_rows(rows_after_filter, policy=policy, rng=rng)

    audit: JsonDict = {
        "policy": policy,
        "seed": seed,
        "pass_rates_provided": pass_rates is not None,
        "solved_threshold": solved_threshold if pass_rates is not None else None,
        "rows_in": rows_in,
        "rows_out": len(reordered),
        "rows_dropped_solved": rows_dropped,
    }
    return reordered, audit


def check_output_paths(
    output_dir: Path,
    overwrite: bool,
    *,
    math_supervision_strategy: str = MATH_SUPERVISION_STRATEGY_V1,
) -> None:
    targets = [
        output_dir / "agentic_sft_v0_train.jsonl",
        output_dir / "agentic_sft_v0_math_final_answer_train.jsonl",
        output_dir / "agentic_sft_v0_val_shadow.jsonl",
        output_dir / "data_blend_agentic_sft_v0.json",
        output_dir / "manifest.json",
        output_dir / "report.md",
    ]
    if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
        targets.extend(
            output_dir / filename
            for filename in _math_bucket_filenames_for_strategy(math_supervision_strategy).values()
        )
    existing = [path for path in targets if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"target files already exist; pass --overwrite to replace them:\n{formatted}")


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    health_baseline = manifest.get("m0_health_baseline") or "(none — every row tagged difficulty=unknown)"
    lines = [
        "# M1 Agentic SFT v0 Data Report",
        "",
        f"- Generated: `{manifest['generated_at_utc']}`",
        f"- M0 input directory: `{manifest['m0_input_dir']}`",
        f"- Output directory: `{manifest['output_dir']}`",
        f"- Training blend: `{manifest['blend_path']}`",
        f"- M0 health baseline: `{health_baseline}`",
        f"- Math supervision strategy: `{manifest.get('math_supervision_strategy', MATH_SUPERVISION_STRATEGY_V1)}`",
        "",
        "## Math final-answer supervision",
        "",
        f"- Format: `{manifest['math_final_answer_supervision']['format']}`",
        f"- Train sidecar rows: `{manifest['math_final_answer_supervision']['train_rows']}`",
        f"- Effective weight: `{manifest['math_final_answer_supervision']['effective_weight']}`",
        f"- Sidecar path: `{manifest['math_final_answer_supervision']['sidecar_path']}`",
        "",
    ]
    math_v3 = manifest.get("math_reasoning_replay_v3")
    if isinstance(math_v3, Mapping):
        lines.extend(
            [
                "## Math reasoning replay v3 buckets",
                "",
                "| Bucket | Source rows | Written rows | Sample fraction | Blend weight | Path |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        buckets = math_v3.get("buckets") or {}
        if isinstance(buckets, Mapping):
            for bucket in MATH_V3_BUCKETS:
                info = buckets.get(bucket) or {}
                if not isinstance(info, Mapping):
                    continue
                lines.append(
                    f"| {bucket} | {info.get('source_rows', info.get('rows', 0))} | "
                    f"{info.get('rows', 0)} | {info.get('sample_fraction', 0.0)} | "
                    f"{info.get('blend_weight', 0.0)} | "
                    f"`{info.get('path', '')}` |"
                )
        lines.append("")
    math_v4 = manifest.get("math_hard_recovery_v4")
    if isinstance(math_v4, Mapping):
        lines.extend(
            [
                "## Math hard recovery v4 buckets",
                "",
                "| Bucket | Source rows | Written rows | Sample fraction | Blend weight | Path |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        buckets = math_v4.get("buckets") or {}
        if isinstance(buckets, Mapping):
            for bucket in MATH_V4_BUCKETS:
                info = buckets.get(bucket) or {}
                if not isinstance(info, Mapping):
                    continue
                lines.append(
                    f"| {bucket} | {info.get('source_rows', info.get('rows', 0))} | "
                    f"{info.get('rows', 0)} | {info.get('sample_fraction', 0.0)} | "
                    f"{info.get('blend_weight', 0.0)} | "
                    f"`{info.get('path', '')}` |"
                )
        lines.append("")
    lines.extend(["## Counts", "", "| Split | Environment | Rows |", "|---|---|---:|"])
    for split in ("train", "val_shadow"):
        for environment, count in manifest["counts"][split].items():
            lines.append(f"| {split} | {environment} | {count} |")
    difficulty_buckets = manifest.get("difficulty_buckets") or {}
    if difficulty_buckets:
        lines.extend(
            [
                "",
                "## Difficulty buckets",
                "",
                "Derived from `oracle` policy in the M0 health-baseline report. "
                "`trivial` = oracle passed, `hard` = oracle failed, `unknown` = "
                "no signal (no report, oracle skipped, or truncated failures list).",
                "",
                "| Split | Bucket | Rows |",
                "|---|---|---:|",
            ]
        )
        for split in ("train", "val_shadow"):
            buckets = difficulty_buckets.get(split) or {}
            for bucket in (DIFFICULTY_TRIVIAL, DIFFICULTY_HARD, DIFFICULTY_UNKNOWN):
                if bucket in buckets:
                    lines.append(f"| {split} | {bucket} | {buckets[bucket]} |")
    if manifest["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in manifest["errors"]:
            location = f"{error.get('environment', 'unknown')}/{error.get('split', 'unknown')}"
            lines.append(f"- `{location}`: {error['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(args: argparse.Namespace) -> JsonDict:
    if args.m0_input_dir is None:
        raise ValueError("--m0-input-dir is required")
    math_supervision_strategy = getattr(
        args,
        "math_supervision_strategy",
        MATH_SUPERVISION_STRATEGY_V1,
    )
    if math_supervision_strategy not in MATH_SUPERVISION_STRATEGIES:
        raise ValueError(
            f"--math-supervision-strategy must be one of {MATH_SUPERVISION_STRATEGIES}, "
            f"got {math_supervision_strategy!r}"
        )
    check_output_paths(
        args.output_dir,
        args.overwrite,
        math_supervision_strategy=math_supervision_strategy,
    )
    files_by_env = discover_m0_files(args.m0_input_dir)
    if not files_by_env:
        raise ValueError(f"no M0 split files found under {args.m0_input_dir}")

    health_baseline_path = args.m0_health_baseline
    if health_baseline_path is None:
        # Default to the path run_m0_health_baseline.py writes when --output-dir
        # is left at its default.
        candidate = args.m0_input_dir / "health_baseline" / "health_baseline_report.json"
        if candidate.is_file():
            health_baseline_path = candidate
    difficulty_signal = load_difficulty_signal(health_baseline_path)

    train_rows, train_errors = convert_split(
        files_by_env,
        split="train",
        max_records_per_env=args.max_records_per_env,
        difficulty_signal=difficulty_signal,
    )
    val_rows, val_errors = convert_split(
        files_by_env,
        split="val",
        max_records_per_env=args.max_val_shadow_per_env,
        difficulty_signal=difficulty_signal,
    )

    math_strategy_weights = _math_weights_for_strategy(args, math_supervision_strategy)
    math_strategy_heldout_train_rows: list[Mapping[str, Any]] = []
    if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
        math_strategy_heldout_train_rows = [
            row for row in train_rows if _math_supervision_bucket(row) == MATH_BUCKET_HELDOUT_EVAL
        ]
        train_rows = filter_v3_training_rows(train_rows)

    # task040 Session 2: W1 curriculum sampler wiring. Applies to TRAIN
    # only — val rows stay in stable order so shadow eval is reproducible.
    train_rows, curriculum_audit = _apply_curriculum_to_train(
        train_rows,
        policy=getattr(args, "curriculum_policy", "as_is"),
        seed=getattr(args, "curriculum_seed", 0),
        pass_rates_path=getattr(args, "curriculum_pass_rates_json", None),
        solved_threshold=getattr(args, "curriculum_solved_threshold", 0.9),
    )

    train_path = args.output_dir / "agentic_sft_v0_train.jsonl"
    math_final_answer_train_path = args.output_dir / "agentic_sft_v0_math_final_answer_train.jsonl"
    val_shadow_path = args.output_dir / "agentic_sft_v0_val_shadow.jsonl"
    blend_path = args.output_dir / "data_blend_agentic_sft_v0.json"
    math_final_answer_rows = [row for row in train_rows if _is_math_final_answer_row(row)]
    math_bucket_order = _math_buckets_for_strategy(math_supervision_strategy)
    math_bucket_paths = {
        bucket: args.output_dir / filename
        for bucket, filename in _math_bucket_filenames_for_strategy(
            math_supervision_strategy
        ).items()
    }
    math_bucket_rows: dict[str, list[Mapping[str, Any]]] = {}
    math_bucket_source_rows: dict[str, list[Mapping[str, Any]]] = {}
    if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
        base_bucket_source_rows = split_math_supervision_buckets(
            train_rows,
            val_rows,
            buckets=MATH_V3_BUCKETS,
        )
        if math_supervision_strategy == MATH_SUPERVISION_STRATEGY_V4:
            verified_source = base_bucket_source_rows[MATH_BUCKET_VERIFIED_FULL_SOLUTION]
            hard_verified_source = [
                row for row in verified_source if is_hard_math_recovery_row(row)
            ]
            hard_verified_ids = {id(row) for row in hard_verified_source}
            math_bucket_source_rows = {bucket: [] for bucket in MATH_V4_BUCKETS}
            math_bucket_source_rows[MATH_BUCKET_HARD_VERIFIED_FULL_SOLUTION] = (
                hard_verified_source
            )
            math_bucket_source_rows[MATH_BUCKET_VERIFIED_FULL_SOLUTION] = [
                row for row in verified_source if id(row) not in hard_verified_ids
            ]
            math_bucket_source_rows[MATH_BUCKET_FINAL_ANSWER_AUX] = base_bucket_source_rows[
                MATH_BUCKET_FINAL_ANSWER_AUX
            ]
            math_bucket_source_rows[MATH_BUCKET_FORMAT_REPAIR] = base_bucket_source_rows[
                MATH_BUCKET_FORMAT_REPAIR
            ]
            math_bucket_source_rows[MATH_BUCKET_HELDOUT_EVAL] = base_bucket_source_rows[
                MATH_BUCKET_HELDOUT_EVAL
            ]
        else:
            math_bucket_source_rows = base_bucket_source_rows
        math_bucket_source_rows[MATH_BUCKET_HELDOUT_EVAL] = [
            *math_strategy_heldout_train_rows,
            *math_bucket_source_rows[MATH_BUCKET_HELDOUT_EVAL],
        ]
        math_bucket_rows = {
            MATH_BUCKET_HELDOUT_EVAL: list(math_bucket_source_rows[MATH_BUCKET_HELDOUT_EVAL])
        }
        for bucket in math_bucket_order:
            if bucket == MATH_BUCKET_HELDOUT_EVAL:
                continue
            math_bucket_rows[bucket] = sample_rows_by_fraction(
                math_bucket_source_rows[bucket],
                fraction=float(math_strategy_weights.get(bucket, 0.0)),
                salt=f"{math_supervision_strategy}:{bucket}",
            )
        apply_math_supervision_strategy_metadata(
            [*train_rows, *val_rows, *math_strategy_heldout_train_rows],
            strategy=math_supervision_strategy,
            bucket_weights=math_strategy_weights,
        )
    else:
        apply_math_supervision_strategy_metadata(
            [*train_rows, *val_rows],
            strategy=math_supervision_strategy,
        )
    write_jsonl(train_path, train_rows)
    write_jsonl(math_final_answer_train_path, math_final_answer_rows)
    write_jsonl(val_shadow_path, val_rows)
    if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
        for bucket, path in math_bucket_paths.items():
            write_jsonl(path, math_bucket_rows.get(bucket, []))
    write_json(
        blend_path,
        (
            build_math_strategy_blend(
                train_path,
                strategy=math_supervision_strategy,
                bucket_paths=math_bucket_paths,
                bucket_rows=math_bucket_rows,
                bucket_weights=math_strategy_weights,
            )
            if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}
            else build_blend(
                train_path,
                math_final_answer_train_path=(
                    math_final_answer_train_path if math_final_answer_rows else None
                ),
                math_final_answer_weight=MATH_FINAL_ANSWER_SIDECAR_WEIGHT,
            )
        ),
    )

    legacy_sidecar_in_blend = (
        math_supervision_strategy == MATH_SUPERVISION_STRATEGY_V1
        and bool(math_final_answer_rows)
    )
    legacy_sidecar_weight = (
        MATH_FINAL_ANSWER_SIDECAR_WEIGHT if legacy_sidecar_in_blend else 0.0
    )

    manifest = {
        "schema_version": 1,
        "milestone": MILESTONE,
        "stage": "Agentic SFT v0",
        "used_in_tag": USED_IN_TAG,
        "math_supervision_strategy": math_supervision_strategy,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "m0_input_dir": str(args.m0_input_dir),
        "output_dir": str(args.output_dir),
        "train_path": str(train_path),
        "math_final_answer_train_path": str(math_final_answer_train_path),
        "val_shadow_path": str(val_shadow_path),
        "blend_path": str(blend_path),
        "m0_health_baseline": str(health_baseline_path) if health_baseline_path else None,
        "counts": {
            "train": count_by_environment(train_rows),
            "val_shadow": count_by_environment(val_rows),
        },
        "difficulty_buckets": {
            "train": count_difficulty_buckets(train_rows),
            "val_shadow": count_difficulty_buckets(val_rows),
        },
        "curriculum": curriculum_audit,
        "math_final_answer_supervision": {
            "environments": sorted(MATH_FINAL_ANSWER_ENVIRONMENTS),
            "format": MATH_FINAL_ANSWER_FORMAT,
            "target_template": "Final answer: \\boxed{expected_answer}",
            "base_blend_weight": 1.0,
            "sidecar_blend_weight": legacy_sidecar_weight,
            "effective_weight": 1.0 + legacy_sidecar_weight,
            "sidecar_dataset_name": MATH_FINAL_ANSWER_SIDECAR_NAME,
            "sidecar_path": str(math_final_answer_train_path),
            "sidecar_in_blend": legacy_sidecar_in_blend,
            "train_rows": len(math_final_answer_rows),
        },
        "errors": [*train_errors, *val_errors],
    }
    if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
        math_strategy_manifest_key = (
            "math_hard_recovery_v4"
            if math_supervision_strategy == MATH_SUPERVISION_STRATEGY_V4
            else "math_reasoning_replay_v3"
        )
        math_strategy_description = (
            "Separates hard AIME/HMMT-style verified full-solution rows, "
            "broad verified full-solution replay, disabled final-answer auxiliary rows, "
            "disabled format-repair rows, and held-out eval rows."
            if math_supervision_strategy == MATH_SUPERVISION_STRATEGY_V4
            else (
                "Separates math rows into verified full-solution replay, "
                "low-weight final-answer auxiliary rows, low-weight format-repair rows, "
                "and held-out eval rows."
            )
        )
        manifest[math_strategy_manifest_key] = {
            "description": (
                math_strategy_description
            ),
            "buckets": {
                bucket: {
                    "rows": len(math_bucket_rows.get(bucket, [])),
                    "source_rows": len(math_bucket_source_rows.get(bucket, [])),
                    "path": str(math_bucket_paths[bucket]),
                    "sample_fraction": float(math_strategy_weights.get(bucket, 0.0)),
                    "blend_weight": (
                        0.0
                        if bucket == MATH_BUCKET_HELDOUT_EVAL
                        else (1.0 if math_bucket_rows.get(bucket) else 0.0)
                    ),
                    "in_training_blend": (
                        bucket != MATH_BUCKET_HELDOUT_EVAL
                        and bool(math_bucket_rows.get(bucket))
                    ),
                }
                for bucket in math_bucket_order
            },
            "train_rows_excluded_as_heldout": len(math_strategy_heldout_train_rows),
            "bucket_counts": count_math_supervision_buckets(
                [*train_rows, *math_strategy_heldout_train_rows],
                buckets=math_bucket_order,
            ),
            "sampled_bucket_counts": count_math_supervision_buckets(
                [
                    row
                    for bucket in math_bucket_order
                    if bucket != MATH_BUCKET_HELDOUT_EVAL
                    for row in math_bucket_rows.get(bucket, [])
                ],
                buckets=math_bucket_order,
            ),
        }
        if math_supervision_strategy == MATH_SUPERVISION_STRATEGY_V4:
            manifest[math_strategy_manifest_key]["hard_filter"] = {
                "environment": "math_competition_numeric",
                "answer_seeking_patterns": list(MATH_V4_ANSWER_SEEKING_PATTERNS),
                "proof_like_exclusions": list(MATH_V4_PROOF_LIKE_PATTERNS),
                "min_prompt_chars": 80,
                "min_solution_chars": 700,
                "max_solution_chars": 12000,
                "topic_keywords": list(MATH_V4_TOPIC_KEYWORDS),
            }

    # task021 Session 2: cross-stage lineage block. M1 declares the M0
    # manifest as its single upstream manifest input plus the optional
    # M0 health-baseline as a sibling input; outputs are the SFT train
    # JSONL, the val_shadow JSONL, and the data-prep blend JSON.
    lineage_inputs: list[LineageInput] = [
        LineageInput(
            kind="manifest",
            ref=str(args.m0_input_dir / "manifest.json"),
            notes="M0 RawDataArtifact",
        ),
    ]
    if health_baseline_path is not None:
        lineage_inputs.append(
            LineageInput(
                kind="m0_health_baseline_report",
                ref=str(health_baseline_path),
                notes="oracle baseline → difficulty signal",
            )
        )
    lineage_outputs = [
        LineageOutput(
            kind="m1_sft_jsonl",
            ref=str(train_path.relative_to(args.output_dir)),
            rows=sum(manifest["counts"]["train"].values()),
            notes="SFT training input",
        ),
        LineageOutput(
            kind="m1_sft_val_shadow_jsonl",
            ref=str(val_shadow_path.relative_to(args.output_dir)),
            rows=sum(manifest["counts"]["val_shadow"].values()),
            notes="held-out shadow file; not used at training time",
        ),
        LineageOutput(
            kind="m1_sft_math_final_answer_jsonl",
            ref=str(math_final_answer_train_path.relative_to(args.output_dir)),
            rows=len(math_final_answer_rows),
            notes="numeric math rows duplicated for boxed final-answer supervision",
        ),
        LineageOutput(
            kind="m1_sft_blend",
            ref=str(blend_path.relative_to(args.output_dir)),
            notes="`nemotron super3 data prep sft -c agentic_v0` consumes this",
        ),
    ]
    if math_supervision_strategy in {MATH_SUPERVISION_STRATEGY_V3, MATH_SUPERVISION_STRATEGY_V4}:
        for bucket in math_bucket_order:
            lineage_outputs.append(
                LineageOutput(
                    kind=f"m1_sft_math_{bucket}_jsonl",
                    ref=str(math_bucket_paths[bucket].relative_to(args.output_dir)),
                    rows=len(math_bucket_rows.get(bucket, [])),
                    notes=f"{math_supervision_strategy} math supervision bucket",
                )
            )
    lineage_record = make_lineage_record(
        stage=f"{MILESTONE} Agentic SFT v0",
        produced_by="prepare_m1_agentic_sft.py",
        artifact_type=SFT_DATA_ARTIFACT,
        artifact_name=args.output_dir.name or "m1_agentic_sft_v0",
        inputs=lineage_inputs,
        outputs=lineage_outputs,
    )
    manifest["lineage"] = lineage_record.to_jsonable()

    write_json(args.output_dir / "manifest.json", manifest)
    write_report(args.output_dir / "report.md", manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m0-input-dir", type=Path, default=DEFAULT_M0_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--m0-health-baseline",
        type=Path,
        default=None,
        help=(
            "Path to run_m0_health_baseline.py's health_baseline_report.json. "
            "Used to populate metadata.difficulty_bucket and "
            "manifest.difficulty_buckets. Defaults to "
            "<m0_input_dir>/health_baseline/health_baseline_report.json when present."
        ),
    )
    parser.add_argument("--max-records-per-env", type=int, default=None)
    parser.add_argument("--max-val-shadow-per-env", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--math-supervision-strategy",
        choices=MATH_SUPERVISION_STRATEGIES,
        default=MATH_SUPERVISION_STRATEGY_V1,
        help=(
            "`final_answer_sidecar_v1` preserves the legacy 1.0-weight boxed-answer "
            "sidecar. `reasoning_replay_v3` writes separate verified-solution, "
            "final-answer-aux, format-repair, and heldout-eval math buckets and "
            "uses lower sidecar weights for answer-only formatting rows. "
            "`hard_math_recovery_v4` focuses sidecar replay on AIME/HMMT-style "
            "verified full solutions and disables answer-only/format-repair rows "
            "by default."
        ),
    )
    parser.add_argument(
        "--math-v3-verified-full-solution-weight",
        type=float,
        default=MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT,
        help="Blend weight for the reasoning_replay_v3 verified full-solution math sidecar.",
    )
    parser.add_argument(
        "--math-v3-final-answer-aux-weight",
        type=float,
        default=MATH_V3_FINAL_ANSWER_AUX_WEIGHT,
        help="Blend weight for reasoning_replay_v3 final-answer-only auxiliary math rows.",
    )
    parser.add_argument(
        "--math-v3-format-repair-weight",
        type=float,
        default=MATH_V3_FORMAT_REPAIR_WEIGHT,
        help="Blend weight for reasoning_replay_v3 rows whose reference solution needed boxed-final repair.",
    )
    parser.add_argument(
        "--math-v4-hard-verified-full-solution-weight",
        type=float,
        default=MATH_V4_HARD_VERIFIED_FULL_SOLUTION_WEIGHT,
        help="Sample fraction for hard_math_recovery_v4 AIME/HMMT-style verified full-solution rows.",
    )
    parser.add_argument(
        "--math-v4-verified-full-solution-weight",
        type=float,
        default=MATH_V4_VERIFIED_FULL_SOLUTION_WEIGHT,
        help="Sample fraction for hard_math_recovery_v4 broad verified full-solution rows.",
    )
    parser.add_argument(
        "--math-v4-final-answer-aux-weight",
        type=float,
        default=MATH_V4_FINAL_ANSWER_AUX_WEIGHT,
        help="Sample fraction for hard_math_recovery_v4 final-answer-only auxiliary math rows.",
    )
    parser.add_argument(
        "--math-v4-format-repair-weight",
        type=float,
        default=MATH_V4_FORMAT_REPAIR_WEIGHT,
        help="Sample fraction for hard_math_recovery_v4 format-repair math rows.",
    )
    # task040 Session 2: W1 curriculum sampler wiring. Off by default
    # (as_is = passthrough). Operators opt in via --curriculum-policy.
    parser.add_argument(
        "--curriculum-policy",
        choices=["as_is", "easy_first", "hard_first", "shuffle"],
        default="as_is",
        help=(
            "Reorder train rows by per-row difficulty bucket (task040 W1 sampler). "
            "Default `as_is` is a no-op for back-compat. `easy_first` sorts "
            "trivial→unknown→hard; `hard_first` reverses; `shuffle` with "
            "--curriculum-seed gives a deterministic permutation. Val rows "
            "are NEVER reordered (shadow eval needs stable order)."
        ),
    )
    parser.add_argument(
        "--curriculum-seed",
        type=int,
        default=0,
        help="Seed for the `shuffle` curriculum policy (deterministic given seed).",
    )
    parser.add_argument(
        "--curriculum-pass-rates-json",
        type=Path,
        default=None,
        help=(
            "Optional path to a JSON file mapping row id → pass_rate (float 0..1). "
            "If provided, rows whose pass_rate > --curriculum-solved-threshold "
            "are dropped from train before policy reordering. Row id resolves "
            "in this order: metadata.m0_source_id > metadata.source_id > id > "
            "instance_id. (M2 task032 rollout store will feed this; M1 sandbox "
            "operators supply a static JSON.)"
        ),
    )
    parser.add_argument(
        "--curriculum-solved-threshold",
        type=float,
        default=0.9,
        help="Pass-rate threshold above which rows are considered solved.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare(args)
    except Exception as exc:  # noqa: BLE001 - CLI should render concise failures.
        print(f"prepare_m1_agentic_sft.py: error: {exc}", file=sys.stderr)
        return 1
    # task069 Session 2: auto-publish lineage to W&B (no-op without active run).
    try:
        from nemotron.recipes.super3.milestones.lineage_publisher import (
            maybe_publish_lineage_from_manifest,
        )
        maybe_publish_lineage_from_manifest(args.output_dir / "manifest.json")
    except Exception:  # noqa: BLE001
        pass
    print(
        json.dumps(
            {
                "train_rows": sum(manifest["counts"]["train"].values()),
                "val_shadow_rows": sum(manifest["counts"]["val_shadow"].values()),
                "blend_path": manifest["blend_path"],
                "math_supervision_strategy": manifest["math_supervision_strategy"],
                "errors": len(manifest["errors"]),
            },
            indent=2,
        )
    )
    return 0 if not manifest["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
