# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""RLHF tool-call pairing harness (task068 Session 2).

Implements the converter Session 1's `task068_design.md` specified:

- Input: HelpSteer-2 prompts (instruction + paired responses) + a
  full M0 Hermes function-calling corpus + an eval-prompt set for
  decontamination.
- For each HelpSteer-2 prompt:
  1. Apply ``relevance_filter`` (keyword heuristic + Hermes template
     match by default). Drop if not tool-call eligible.
  2. Apply ``gold_call_finder`` (function-name match heuristic with
     required-arg tiebreak by default). Drop if no Hermes pair.
  3. Apply contamination check vs ``eval_prompt_set``. Drop if
     contaminated.
  4. Emit a paired row in NeMo-Gym single_step_tool_use_with_argument_comparison
     shape (argument_match verifier).
- Output: stream of paired NeMo-Gym JSONL rows.

Sandbox-runnable. Real corpus build happens at M0 prep time via a new
CLI dispatch path Session 3 wires; this Session lands the strategy.

Unlike the per-row converters in :mod:`prepare_m0_assets`, this is a
STREAM operation — needs the full Hermes corpus in memory to do
function-name match. The orchestrator yields paired rows so callers
can write them to JSONL incrementally.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from typing import Any


# ---------- Relevance filter ----------

# Cheap keyword heuristic — any prompt mentioning one of these
# primitives implies an actionable, tool-able task. Case-insensitive
# substring match. Order doesn't matter; presence of any one keyword
# admits the prompt.
RELEVANCE_KEYWORDS: tuple[str, ...] = (
    "look up",
    "find out",
    "find me",
    "search for",
    "compute",
    "calculate",
    "convert",
    "translate",
    "schedule",
    "lookup",
    "fetch",
    "what is the",
    "how many",
    "which",
    "weather",
    "near",
)


def default_relevance_filter(prompt: str) -> bool:
    """True iff *prompt* admits a tool-call follow-up.

    Default impl: keyword heuristic only. Hermes-template match is left
    as a hook Session 3+ can extend if recall is too low — for the
    Session 2 design baseline, keywords cover the common surface (~30%
    of HelpSteer-2 prompts in the design doc's estimate).
    """
    text = prompt.lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


# ---------- Gold-call finder ----------


def _extract_function_call(hermes_row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Pull the gold tool call out of a Hermes M0 row.

    Hermes rows store the gold tool call(s) under
    ``expected_answer.tool_calls`` (Hermes function-calling convention)
    or under ``expected_answer`` directly for older formats. Return the
    first call's ``function`` block (name + arguments) or None if the
    row doesn't have one.
    """
    expected = hermes_row.get("expected_answer")
    if isinstance(expected, Mapping):
        # Newer Hermes format: {"tool_calls": [{"function": {"name", "arguments"}}, ...]}
        tool_calls = expected.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            first = tool_calls[0]
            if isinstance(first, Mapping):
                function = first.get("function")
                if isinstance(function, Mapping):
                    return function
        # Older format: {"name", "arguments"} directly
        if "name" in expected and "arguments" in expected:
            return expected
    return None


def _function_name_keywords(function_name: str) -> tuple[str, ...]:
    """Generate keyword candidates from a function name.

    ``get_weather`` → ("get_weather", "get weather", "weather"). Match
    against the prompt happens on all of these; presence of any one
    counts.
    """
    name = function_name.lower()
    candidates = [name]
    if "_" in name:
        candidates.append(name.replace("_", " "))
        # Trailing fragment ("weather" out of "get_weather") — often the
        # noun that appears in natural prompts
        candidates.append(name.rsplit("_", 1)[-1])
    return tuple(candidates)


def default_gold_call_finder(
    prompt: str, hermes_corpus: Sequence[Mapping[str, Any]]
) -> Mapping[str, Any] | None:
    """Return the Hermes row whose gold call best matches *prompt*.

    Strategy: function-name match heuristic (per Session 1 design doc).

    1. Find every Hermes row whose gold function name (or a derived
       keyword) appears in *prompt*.
    2. Tie-break by counting how many of the gold call's required
       argument names also appear in the prompt — more arg overlap
       = more grounded.
    3. Return the highest-scoring row; ``None`` if no row matches.

    Deterministic: same input → same output (sorted before tiebreak;
    stable Python sort).
    """
    text = prompt.lower()
    matches: list[Mapping[str, Any]] = []
    for hrow in hermes_corpus:
        function = _extract_function_call(hrow)
        if function is None:
            continue
        function_name = str(function.get("name") or "").strip()
        if not function_name:
            continue
        keywords = _function_name_keywords(function_name)
        if not any(kw in text for kw in keywords):
            continue
        matches.append(hrow)

    if not matches:
        return None

    def _arg_overlap(hrow: Mapping[str, Any]) -> int:
        function = _extract_function_call(hrow) or {}
        arguments = function.get("arguments") or {}
        if not isinstance(arguments, Mapping):
            return 0
        return sum(
            1 for arg_name in arguments
            if isinstance(arg_name, str) and arg_name.replace("_", " ").lower() in text
        )

    matches.sort(key=_arg_overlap, reverse=True)
    return matches[0]


# ---------- Decontamination ----------


_PUNCT_TABLE = str.maketrans({c: " " for c in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"})


def _normalize_for_contam_check(text: str) -> str:
    return " ".join(text.lower().translate(_PUNCT_TABLE).split())


def _five_grams(text: str) -> Iterator[str]:
    """Yield word 5-grams from *text* (already-normalized)."""
    words = text.split()
    for i in range(len(words) - 4):
        yield " ".join(words[i : i + 5])


def build_eval_prompt_set(eval_prompts: Iterable[str]) -> frozenset[str]:
    """Build a frozenset of normalized 5-grams from an eval-prompt list.

    Callers pass the union of every M1 eval-basket benchmark's prompt
    surface (BFCL / TauBench airline / MCP-Mark / HelpSteer1). The
    converter checks each candidate HelpSteer-2 prompt's 5-grams
    against this set; any hit → contaminated.
    """
    out: set[str] = set()
    for prompt in eval_prompts:
        normalized = _normalize_for_contam_check(prompt)
        out.update(_five_grams(normalized))
        # Also include the full normalized prompt for exact-match check
        if normalized:
            out.add(normalized)
    return frozenset(out)


def is_contaminated(prompt: str, eval_prompt_set: frozenset[str]) -> bool:
    """True iff *prompt* contaminates against the eval prompt set.

    Two-tier check: exact-normalized match OR any-5-gram match. The
    5-gram check catches paraphrases that share verbatim phrasing
    (e.g., "passenger announcement" appearing in both a HelpSteer-2
    prompt and a TauBench airline prompt).
    """
    normalized = _normalize_for_contam_check(prompt)
    if not normalized:
        return False
    if normalized in eval_prompt_set:
        return True
    return any(g in eval_prompt_set for g in _five_grams(normalized))


# ---------- Orchestrator ----------


_TOOLCALL_SYSTEM_PROMPT = (
    "You are a tool-using assistant. Use the provided function "
    "schema to satisfy the user request. Emit a single tool call "
    "matching the schema exactly."
)


# Contamination targets per Session 1 design doc — every output row
# carries this list so task030 Session 7's contamination_audit can
# audit downstream consumers the same way it audits M0 data rows.
PAIRED_CONTAMINATION_AGAINST: tuple[str, ...] = (
    "BFCL",
    "TauBench airline",
    "MCP-Mark",
    "HelpSteer1",
)


def transform_rlhf_toolcall_pairing(
    helpsteer2_rows: Iterable[Mapping[str, Any]],
    *,
    hermes_corpus: Sequence[Mapping[str, Any]],
    eval_prompt_set: frozenset[str] = frozenset(),
    relevance_filter: Callable[[str], bool] = default_relevance_filter,
    gold_call_finder: Callable[
        [str, Sequence[Mapping[str, Any]]], Mapping[str, Any] | None
    ] = default_gold_call_finder,
) -> Iterator[dict[str, Any]]:
    """Stream paired (HelpSteer-2 prompt, Hermes gold call) rows.

    Each emitted row is shaped for the NeMo-Gym
    ``single_step_tool_use_with_argument_comparison`` env: prompt as
    user message, gold tool call as ``expected_answer``, argument_match
    verifier, ``contamination_against`` metadata pre-filled.

    Filtering happens in this order:

    1. *relevance_filter*(prompt) → drop if False
    2. *gold_call_finder*(prompt, hermes_corpus) → drop if None
    3. ``is_contaminated``(prompt, eval_prompt_set) → drop if True

    Caller writes the stream to JSONL incrementally. Total row count
    ≪ HelpSteer-2 row count (Session 1 design estimates ~17% retention
    on the full HelpSteer-2 train corpus).
    """
    for helpsteer_row in helpsteer2_rows:
        prompt = str(helpsteer_row.get("prompt") or "").strip()
        if not prompt:
            continue
        if not relevance_filter(prompt):
            continue
        gold_hermes = gold_call_finder(prompt, hermes_corpus)
        if gold_hermes is None:
            continue
        if is_contaminated(prompt, eval_prompt_set):
            continue

        function = _extract_function_call(gold_hermes)
        if function is None:
            continue
        gold_call = {
            "name": str(function.get("name") or "").strip(),
            "arguments": (
                dict(function["arguments"])
                if isinstance(function.get("arguments"), Mapping)
                else {}
            ),
        }
        tool_schema = _extract_tool_schema(gold_hermes, gold_call["name"])

        yield {
            "environment": "single_step_tool_use_with_argument_comparison",
            "milestone": "M0",
            "use_stage": [
                "M0 data_env_foundation",
                "M1 RLHF tool-call validity",
            ],
            "question": prompt,
            "expected_answer": gold_call,
            "responses_create_params": {
                "input": [
                    {"role": "system", "content": _TOOLCALL_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "tools": [tool_schema],
            },
            "reward_config": {
                "verifier": "argument_match",
                "max_score": 1.0,
                "match": ["name", "arguments"],
            },
            "extra_env_info": {
                "source_helpsteer2_id": str(
                    helpsteer_row.get("id")
                    or helpsteer_row.get("source_id")
                    or ""
                ),
                "source_hermes_id": str(
                    gold_hermes.get("id")
                    or gold_hermes.get("metadata", {}).get("source_id")
                    or ""
                ),
                "match_strategy": "function_name_overlap",
            },
            "metadata": {
                "source_dataset": "rlhf_toolcall_pairing",
                "source_helpsteer2_id": str(
                    helpsteer_row.get("id")
                    or helpsteer_row.get("source_id")
                    or ""
                ),
                "source_hermes_id": str(
                    gold_hermes.get("id")
                    or gold_hermes.get("metadata", {}).get("source_id")
                    or ""
                ),
                "contamination_against": list(PAIRED_CONTAMINATION_AGAINST),
            },
        }


def _extract_tool_schema(
    hermes_row: Mapping[str, Any], function_name: str
) -> dict[str, Any]:
    """Pull the tool schema for *function_name* out of a Hermes row.

    The schema lives under ``responses_create_params.tools`` per the
    M0 contract. We pick the first tool whose function name matches
    *function_name*; the other tools (if any) are alternate offerings
    the agent could have chosen but isn't required to know about.

    Always returns a schema — synthesizes a minimal one if the Hermes
    row doesn't include it explicitly. This keeps the output row
    well-formed (the verifier needs a tool schema to validate against).
    """
    rcp = hermes_row.get("responses_create_params")
    if isinstance(rcp, Mapping):
        tools = rcp.get("tools")
        if isinstance(tools, list):
            for tool in tools:
                if not isinstance(tool, Mapping):
                    continue
                function = tool.get("function")
                if isinstance(function, Mapping) and function.get("name") == function_name:
                    return dict(tool)
    # Fallback: synthesise a minimal schema.
    return {
        "type": "function",
        "function": {
            "name": function_name,
            "description": f"Tool schema for {function_name}",
            "parameters": {"type": "object", "properties": {}},
        },
    }


__all__ = [
    "PAIRED_CONTAMINATION_AGAINST",
    "RELEVANCE_KEYWORDS",
    "build_eval_prompt_set",
    "default_gold_call_finder",
    "default_relevance_filter",
    "is_contaminated",
    "transform_rlhf_toolcall_pairing",
]
