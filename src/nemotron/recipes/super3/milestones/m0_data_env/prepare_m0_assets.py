#!/usr/bin/env python3
# /// script
# dependencies = ["datasets>=2.14.0", "pyyaml>=6.0"]
# ///

"""Prepare public M0 data and environment assets for multi-environment RL."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from nemotron.recipes.super3.milestones.lineage import (
        RAW_DATA_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from nemotron.recipes.super3.milestones.lineage import (
        make_record as make_lineage_record,
    )
except ModuleNotFoundError:
    # Allow `python prepare_m0_assets.py` from the module directory (the
    # script's PEP 723 banner enables that) by reaching for the sibling
    # lineage module on the import path.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lineage import (  # type: ignore[no-redef]
        RAW_DATA_ARTIFACT,
        LineageInput,
        LineageOutput,
    )
    from lineage import (
        make_record as make_lineage_record,
    )

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_REGISTRY_PATH = SCRIPT_DIR / "data_registry.yaml"
ENV_REGISTRY_PATH = SCRIPT_DIR / "environment_registry.yaml"
DEFAULT_OUTPUT_DIR = Path("data/super3/milestones/m0_data_env_foundation")
MISSING_CONFIG = object()

TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)

# Matches the contents of a `\boxed{...}` block. NuminaMath-style competition
# math problems carry the final answer here. The pattern is intentionally
# non-greedy and stops at the first unbalanced `}`; deeply nested LaTeX like
# `\boxed{\frac{a}{b}}` will be truncated. We accept this for M0 smoke — rows
# that fall through extraction become `manifest.errors`; a balanced-bracket
# parser is a task057 follow-up.
BOXED_ANSWER_RE = re.compile(r"\\boxed\{([^{}]*)\}")

# Matches both fenced markdown code blocks (```python ... ```) and the
# `<python>...</python>` tag form that MathCodeInstruct uses. Used by
# `transform_mathcode_instruct` (task057 Session 6) to detect whether
# the gold solution actually has a tool-use step.
PYTHON_CODE_BLOCK_RE = re.compile(
    r"```python\s*\n.*?```|<python>.*?</python>",
    re.DOTALL | re.IGNORECASE,
)

SYSTEM_PROMPTS = {
    "search_grounded_qa": "You answer questions using the provided retrieved passages.",
    "search_multihop_qa": (
        "You answer multi-hop questions using the provided retrieved passages. "
        "Cite the passages you used."
    ),
    "browser_qa": (
        "You answer questions by planning browser/search actions, then grounding "
        "the final answer in cited web evidence."
    ),
    "browsecomp_grounded": (
        "You solve hard browser/search questions by using web evidence. Return "
        "a concise answer and cite the pages that support it."
    ),
    "code_execution_python": "You are a Python coding assistant. Return a complete solution.",
    "general_tool_calling": "You are a tool-using assistant. Use the available functions when needed.",
    "multi_turn_tool_use": (
        "You are a tool-using assistant. Use the available functions across "
        "multiple turns when needed and incorporate tool results into the final answer."
    ),
    "structured_outputs_json": (
        "You are a structured-output assistant. Return only valid JSON that matches the schema."
    ),
    "terminal_basic_shell": "You are a terminal assistant. Return a safe shell command only.",
    "terminal_workplace": (
        "You are a terminal workplace assistant. Solve the task with safe shell "
        "commands. Return only the final command or command sequence."
    ),
    "swe_pivot_patch_supervision": "You are a software engineering assistant. Return a unified diff patch only.",
    "swe_pivot_tool_call": (
        "You are a software engineering agent. Decide the single next tool "
        "call that makes the most progress on the issue. Return one tool "
        "call from the provided schema; do not narrate."
    ),
    "swe2_openhands_trace": (
        "You are a software engineering agent running in a SWE-Bench sandbox. "
        "Use the OpenHands tool loop to read, edit, and test the repository "
        "until the issue is resolved. Reward is binary: the final patch must "
        "apply cleanly AND the test suite must pass."
    ),
    "helpsteer2_pref_compare": (
        "You are a helpful, accurate assistant. Respond to the user's prompt. "
        "A preference judge will compare your reply against another candidate "
        "to score helpfulness, coherence, and correctness."
    ),
    "multilingual_instruct": (
        "You are a helpful assistant. Respond in the same language as the "
        "user. Match the meaning of the target reference closely; small "
        "wording differences are fine."
    ),
    "multilingual_ifeval": (
        "You are a multilingual instruction-following assistant. Respond in "
        "the same language as the user while satisfying every stated constraint."
    ),
    "multilingual_humaneval": (
        "You are a multilingual coding assistant. Solve the programming task "
        "and return the complete answer requested by the prompt."
    ),
    "long_context_qa_smoke": (
        "You are a long-context reading-comprehension assistant. Read "
        "the document carefully and answer the user's question grounded "
        "in the document's content. Quote or paraphrase the relevant "
        "passage; do not invent facts."
    ),
    "sql_text_to_query": (
        "You are a text-to-SQL assistant. Given a natural-language "
        "question about a database schema, emit a single valid SQL "
        "query that answers it. Return ONLY the SQL — no commentary."
    ),
    "safety_reasoning_smoke": (
        "You are a content-safety analyst. Read the user prompt and "
        "decide whether to ALLOW or BLOCK the response. State your "
        "verdict clearly (one of ALLOW / BLOCK / ESCALATE), then "
        "briefly explain the reasoning."
    ),
    "math_with_tools": (
        "You are a careful math-reasoning assistant with access to a "
        "Python interpreter. When a calculation benefits from code, "
        "show it inside ```python ... ``` (or <python>...</python>) "
        "and incorporate the result. Put the final answer in \\boxed{}."
    ),
    "tool_call_repair_negative": (
        "You repair malformed or hallucinated tool-use attempts using the provided schema."
    ),
    "math_reasoning_numeric": "You are a careful reasoning assistant. Return the final numeric answer clearly.",
    "math_competition_numeric": (
        "You are a careful reasoning assistant. Solve the competition math problem "
        "step by step and put the final answer in \\boxed{}."
    ),
    "math_formal_lean": (
        "You are a formal-proof assistant. Read the Lean theorem statement and "
        "return a complete proof in the same Lean dialect. Do not add prose; "
        "return only the proof code."
    ),
}

JsonDict = dict[str, Any]


BROWSER_SEARCH_TOOLS: list[JsonDict] = [
    {
        "type": "function",
        "function": {
            "name": "browser_search",
            "description": "Search the web for pages relevant to the question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_open",
            "description": "Open a URL in the browser sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_find",
            "description": "Find text on the currently open page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_cite",
            "description": "Attach a supporting URL and short evidence note to the answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "evidence": {"type": "string"},
                },
                "required": ["url", "evidence"],
            },
        },
    },
]


def load_yaml(path: Path) -> JsonDict:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def normalize_numeric_answer(text: Any) -> str:
    value = str(text).strip()
    if "####" in value:
        value = value.rsplit("####", 1)[1].strip()
    return value.replace(",", "").strip()


def extract_boxed_answer(text: Any) -> str:
    """Return the contents of the LAST ``\\boxed{...}`` in *text*, or "" if absent.

    NuminaMath-CoT puts the final answer in a `\\boxed{...}` block at the end
    of the `solution` field. Several solutions wrap intermediate steps in
    `\\boxed{}` too — the convention is "last boxed = the answer", so we
    return the trailing match.
    """
    value = str(text)
    matches = BOXED_ANSWER_RE.findall(value)
    if not matches:
        return ""
    return matches[-1].strip()


def parse_json_maybe(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return default
    return value


def source_id(row: Mapping[str, Any]) -> str:
    for key in ("id", "task_id", "instance_id", "source_file"):
        if row.get(key) is not None:
            return str(row[key])
    return ""


def base_metadata(spec: Mapping[str, Any], row: Mapping[str, Any]) -> JsonDict:
    return {
        "source_dataset": spec["hf_dataset"],
        "source_config": spec.get("hf_config"),
        "source_split": spec["hf_split"],
        "source_revision": spec["hf_revision"],
        "source_url": spec["source_url"],
        "source_id": source_id(row),
        "license": spec["license"],
        "domain": spec["domain"],
        "difficulty": spec.get("difficulty"),
        "reward_type": spec["reward_type"],
        "contamination": spec["contamination"],
        "contamination_against": list(spec["contamination_against"]),
        "data_stage": spec["milestone"],
        "use_stage": list(spec["use_stage"]),
    }


def make_record(
    *,
    spec: Mapping[str, Any],
    row: Mapping[str, Any],
    question: str,
    expected_answer: Any,
    input_messages: list[JsonDict],
    reward_config: JsonDict,
    extra_env_info: JsonDict | None = None,
    tools: list[JsonDict] | None = None,
) -> JsonDict:
    tools = tools or []
    return {
        "environment": spec["environment"],
        "milestone": spec["milestone"],
        "use_stage": list(spec["use_stage"]),
        "question": question,
        "expected_answer": expected_answer,
        "responses_create_params": {
            "input": input_messages,
            "tools": tools,
        },
        "reward_config": reward_config,
        "extra_env_info": extra_env_info or {},
        "metadata": base_metadata(spec, row),
    }


def hotpot_documents(row: Mapping[str, Any]) -> list[JsonDict]:
    context = row.get("context") or {}
    if not isinstance(context, Mapping):
        return []
    titles = context.get("title") or []
    sentence_groups = context.get("sentences") or []
    docs = []
    for title, sentences in zip(titles, sentence_groups):
        if isinstance(sentences, list):
            text = "\n".join(str(sentence) for sentence in sentences)
        else:
            text = str(sentences)
        docs.append({"title": str(title), "text": text})
    return docs


def format_documents_for_prompt(documents: Sequence[Mapping[str, Any]]) -> str:
    blocks = []
    for index, doc in enumerate(documents, start=1):
        blocks.append(f"[{index}] {doc.get('title', '')}\n{doc.get('text', '')}")
    return "\n\n".join(blocks)


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, Mapping):
        return [str(value).strip()] if value else []
    if isinstance(value, Iterable):
        return [str(item).strip() for item in value if str(item).strip()]
    stripped = str(value).strip()
    return [stripped] if stripped else []


def transform_hotpotqa_search(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row["question"]).strip()
    expected_answer = str(row["answer"]).strip()
    documents = hotpot_documents(row)
    user_content = (
        "Answer the question using only the retrieved passages.\n\n"
        f"Question: {question}\n\n"
        f"Retrieved passages:\n{format_documents_for_prompt(documents)}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "normalized_exact_or_contains",
            "max_score": 1.0,
            "normalization": ["lowercase", "strip_articles", "strip_punctuation", "collapse_whitespace"],
        },
        extra_env_info={
            "context_documents": documents,
            "supporting_facts": row.get("supporting_facts"),
            "question_type": row.get("type"),
            "level": row.get("level"),
            "search_query": question,
        },
    )


def transform_browsecomp_grounded(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert a BrowseComp-style row to the M2 browser/search scaffold.

    Session 1 intentionally stops at a sandbox-runnable record contract:
    it emits browser/search tool schemas and an offline grounded-answer
    verifier stub, but it does not import or launch Playwright/Chromium.
    """
    question = str(row.get("question") or row.get("prompt") or "").strip()
    expected_answer = str(
        row.get("answer") or row.get("final_answer") or row.get("expected_answer") or ""
    ).strip()
    if not question:
        raise ValueError("browsecomp row must contain question or prompt")
    if not expected_answer:
        raise ValueError("browsecomp row must contain answer or final_answer")

    seed_urls = string_list(
        row.get("seed_urls")
        or row.get("supporting_urls")
        or row.get("source_urls")
        or row.get("gold_urls")
        or row.get("urls")
    )
    evidence = string_list(row.get("evidence") or row.get("supporting_facts") or row.get("rationale"))
    allowed_domains = string_list(row.get("allowed_domains") or row.get("domains"))

    seed_block = "\n".join(f"- {url}" for url in seed_urls) if seed_urls else "- none provided"
    user_content = (
        "Use browser/search tools to answer the question. Cite supporting pages in the final answer.\n\n"
        f"Question: {question}\n\n"
        f"Seed URLs:\n{seed_block}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "browser_grounded_answer_stub",
            "max_score": 1.0,
            "normalization": ["lowercase", "strip_articles", "strip_punctuation", "collapse_whitespace"],
            "grounding": "stub_requires_answer_match_only",
        },
        extra_env_info={
            "seed_urls": seed_urls,
            "allowed_domains": allowed_domains,
            "evidence": evidence,
            "requires_live_browser": False,
            "cluster_execution": "deferred_to_task022_session_3",
            "browser_runtime": "playwright_chromium_placeholder",
        },
        tools=copy.deepcopy(BROWSER_SEARCH_TOOLS),
    )


def transform_mbpp_code_execution(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row.get("prompt") or row.get("text") or "").strip()
    tests = list(row.get("test_list") or [])
    imports_value = row.get("test_imports")
    if imports_value is None:
        imports_value = row.get("test_setup_code")
    if isinstance(imports_value, str):
        imports = [imports_value] if imports_value.strip() else []
    else:
        imports = list(imports_value or [])
    user_content = (
        "Write a Python function or program for the task below. Return only executable Python code.\n\n"
        f"Task:\n{question}\n\n"
        "The solution will be checked with hidden and visible unit tests."
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=str(row.get("code") or "").strip(),
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "python_unit_tests",
            "max_score": 1.0,
            "timeout_s": 30,
            "sandbox": "python_subprocess_or_container",
        },
        extra_env_info={
            "task_id": row.get("task_id"),
            "test_imports": imports,
            "test_list": tests,
            "reference_code": row.get("code"),
        },
    )


def transform_bash_command(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row.get("prompt") or row.get("instruction") or "").strip()
    command = str(row.get("response") or row.get("command") or row.get("input") or "").strip()
    if not question or not command:
        raise ValueError("bash command row must contain prompt and response")
    user_content = (
        "Write one shell command for the terminal task below. "
        "Return only the command, without prose or Markdown.\n\n"
        f"Task:\n{question}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=command,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "command_substring_match",
            "max_score": 1.0,
            "match": ["normalized_command_substring"],
        },
        extra_env_info={
            "expected_command": command,
            "source_prompt": question,
        },
    )


# M0 smoke cap on bash command length (task057 Session 4).
# intercode-nl2bash includes some 500+ char commands that hurt eval
# more than they teach the model. Cap matches the README's
# documented limit; rows above the cap are dropped (not truncated —
# truncation would change the shell semantics).
INTERCODE_NL2BASH_MAX_CMD_CHARS: int = 200
TERMINAL_WORKPLACE_DEFAULT_TIMEOUT_S: int = 300
TERMINAL_WORKPLACE_TIMEOUT_PROFILE: str = "terminal_workplace_extended"


def transform_intercode_nl2bash(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one intercode-nl2bash-curated row to terminal_basic_shell shape.

    Tier-2 source for the existing terminal_basic_shell env (task057
    Session 4). intercode-nl2bash rows ship instruction + gold bash
    command pairs; row schema varies by snapshot:

    - ``nl`` / ``instruction`` / ``prompt``: natural-language task
    - ``cmd`` / ``bash`` / ``command`` / ``response``: gold shell command

    Compared to tier-1 ``transform_bash_command``, this converter:
    1. Accepts the intercode-native ``nl`` + ``cmd`` aliases
    2. Caps command length at ``INTERCODE_NL2BASH_MAX_CMD_CHARS`` (rows
       above the cap are rejected — README's documented limit; the
       intercode corpus has long-tail nightmare commands not useful
       for M0 smoke)
    3. Tags the converter origin in ``extra_env_info.source_dataset_kind``
       so downstream stratification can split tier-1 vs tier-2 data

    Output uses the same env (terminal_basic_shell) + verifier
    (command_substring_match) as tier-1; no new env or verifier
    needed.
    """
    question = str(
        row.get("nl")
        or row.get("instruction")
        or row.get("prompt")
        or ""
    ).strip()
    if not question:
        raise ValueError(
            "intercode-nl2bash row missing instruction "
            "(checked nl / instruction / prompt)"
        )
    command = str(
        row.get("cmd")
        or row.get("bash")
        or row.get("command")
        or row.get("response")
        or ""
    ).strip()
    if not command:
        raise ValueError(
            "intercode-nl2bash row missing gold command "
            "(checked cmd / bash / command / response)"
        )
    if len(command) > INTERCODE_NL2BASH_MAX_CMD_CHARS:
        raise ValueError(
            f"intercode-nl2bash row gold command exceeds M0 smoke cap "
            f"({len(command)} > {INTERCODE_NL2BASH_MAX_CMD_CHARS} chars); "
            "drop the nightmare row rather than truncate (shell semantics "
            "change under truncation)"
        )

    user_content = (
        "Write one shell command for the terminal task below. "
        "Return only the command, without prose or Markdown.\n\n"
        f"Task:\n{question}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=command,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "command_substring_match",
            "max_score": 1.0,
            "match": ["normalized_command"],
        },
        extra_env_info={
            "expected_command": command,
            "source_prompt": question,
            "source_dataset_kind": "intercode_nl2bash_tier2",
            "cmd_length_chars": len(command),
        },
    )


def _first_text(row: Mapping[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""


def _terminal_workplace_timeout(row: Mapping[str, Any], spec: Mapping[str, Any]) -> int:
    for key in ("timeout_s", "execution_timeout_s", "time_limit_s", "max_duration_s"):
        value = row.get(key)
        if value is None:
            continue
        try:
            timeout_s = int(value)
        except (TypeError, ValueError):
            continue
        if timeout_s > 0:
            return timeout_s
    return int(spec.get("default_timeout_s") or TERMINAL_WORKPLACE_DEFAULT_TIMEOUT_S)


def transform_terminalbench_v2(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert a TerminalBench v2-style row to the M2 terminal_workplace shape.

    Session 1 is a sandbox-runnable scaffold, not a real TerminalBench
    cluster runner. The record contract deliberately reuses the existing
    ``command_substring_match`` verifier while carrying explicit extended
    timeout metadata so future terminal sandbox execution can pick up the
    longer budget without changing the converter shape.
    """
    question = _first_text(
        row,
        (
            "instruction",
            "prompt",
            "task",
            "description",
            "question",
        ),
    )
    if not question:
        raise ValueError(
            "TerminalBench v2 row missing instruction "
            "(checked instruction / prompt / task / description / question)"
        )
    command = _first_text(
        row,
        (
            "expected_command",
            "gold_command",
            "reference_command",
            "command",
            "cmd",
            "solution",
            "answer",
        ),
    )
    if not command:
        raise ValueError(
            "TerminalBench v2 row missing gold command "
            "(checked expected_command / gold_command / reference_command / "
            "command / cmd / solution / answer)"
        )

    timeout_s = _terminal_workplace_timeout(row, spec)
    user_content = (
        "Complete the terminal workplace task below. Return only the shell "
        "command or command sequence, without prose or Markdown.\n\n"
        f"Task:\n{question}"
    )
    task_id = row.get("task_id") or row.get("id") or row.get("name")
    extra_env_info: JsonDict = {
        "expected_command": command,
        "source_prompt": question,
        "source_dataset_kind": "terminalbench_v2",
        "terminalbench_task_id": task_id,
        "extended_timeout_s": timeout_s,
        "timeout_profile": TERMINAL_WORKPLACE_TIMEOUT_PROFILE,
        "cluster_execution": {
            "required": False,
            "reason": "Session 1 scaffold defers real terminal sandbox/cluster smoke",
        },
    }
    for key in ("category", "difficulty", "workdir", "setup_commands"):
        if row.get(key) is not None:
            extra_env_info[key] = row[key]

    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=command,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "command_substring_match",
            "max_score": 1.0,
            "match": ["normalized_command_substring"],
            "timeout_s": timeout_s,
            "timeout_profile": TERMINAL_WORKPLACE_TIMEOUT_PROFILE,
            "sandbox": "terminal",
        },
        extra_env_info=extra_env_info,
    )


def transform_swe_bench_patch(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    problem_statement = str(row.get("problem_statement") or "").strip()
    patch = str(row.get("patch") or "").strip()
    if not problem_statement or not patch:
        raise ValueError("SWE-bench row must contain problem_statement and patch")
    repo = str(row.get("repo") or "").strip()
    instance_id = str(row.get("instance_id") or "").strip()
    user_content = (
        "Produce a minimal unified diff patch that resolves the software issue below.\n\n"
        f"Repository: {repo}\n"
        f"Instance: {instance_id}\n\n"
        f"Issue:\n{problem_statement}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=problem_statement,
        expected_answer=patch,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "patch_diff_match",
            "max_score": 1.0,
            "match": ["normalized_unified_diff"],
        },
        extra_env_info={
            "repo": repo,
            "instance_id": instance_id,
            "base_commit": row.get("base_commit"),
            "environment_setup_commit": row.get("environment_setup_commit"),
            "test_patch": row.get("test_patch"),
            "fail_to_pass": row.get("FAIL_TO_PASS"),
            "pass_to_pass": row.get("PASS_TO_PASS"),
            "gold_patch": patch,
        },
    )


# SWE pivot tool-call schema (task016 Session 2). Matches the
# `single_step_tool_use_with_argument_comparison` NeMo-Gym env's
# expectation for a generic SWE agent's first tool call. Kept small so
# the policy can learn the pivot decision rather than memorize the tool
# universe; richer tool sets (refactor, run_linter, ...) belong to M2.
SWE_PIVOT_TOOLS: list[JsonDict] = [
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "Show the contents of a file at the given repo-relative path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repo-relative file path"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the repo for a literal string or pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "path": {"type": "string", "description": "Optional directory to scope the search"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Apply an edit to a file by replacing a span of text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run the project's test suite, optionally scoped to a specific path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Optional path filter (file or test id)"},
                },
            },
        },
    },
]


# Tool names that are "exploration" (read-only) rather than "action"
# (state-changing). Exploration pivots are still emitted but tagged so
# downstream filters can choose between (a) training on exploration as a
# valid first move and (b) keeping only action pivots. Per task016 README:
# "那些只 view-or-search 的纯探索行为也要标".
SWE_PIVOT_EXPLORATION_TOOLS: frozenset[str] = frozenset({
    "view_file",
    "search",
    "search_dir",
    "find_file",
    "grep",
    "ls",
})


def _first_assistant_tool_call(messages: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Return the first assistant message's first tool_call dict.

    Raises ``ValueError`` if no assistant message in *messages* carries a
    non-empty ``tool_calls`` list. The first hit wins so the converter
    captures *the pivot decision*, not whatever the trajectory ended on.
    """
    for message in messages:
        if not isinstance(message, Mapping):
            continue
        if message.get("role") != "assistant":
            continue
        tool_calls = message.get("tool_calls") or []
        if not isinstance(tool_calls, list) or not tool_calls:
            continue
        first_call = tool_calls[0]
        if isinstance(first_call, Mapping):
            return first_call
    raise ValueError("SWE-Gym trajectory has no assistant message with tool_calls")


def _first_patch_file_path(patch: str) -> str:
    """Return the first modified target path from a unified diff."""
    for line in str(patch).splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                candidate = parts[3]
                if candidate.startswith("b/"):
                    candidate = candidate[2:]
                if candidate and candidate != "/dev/null":
                    return candidate
        if line.startswith("+++ "):
            candidate = line[4:].strip()
            if candidate.startswith("b/"):
                candidate = candidate[2:]
            if candidate and candidate != "/dev/null":
                return candidate
    return ""


def transform_swe_gym_lite_pivot(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one SWE-Gym-Lite trajectory into the SWE pivot tool-call shape.

    SWE-Gym-Lite ships agent trajectories per issue. We extract the
    *first* tool call the agent emits — that's the "pivot" decision the
    policy is being asked to learn. ``argument_match`` on the NeMo-Gym
    side compares the candidate's emitted first tool call against this
    gold call (name + arguments).

    The row's tool-call payload is normalized to ``{"name": ...,
    "arguments": <dict>}`` regardless of whether the upstream stores
    arguments as a JSON string (OpenAI agents convention) or a dict
    directly.

    Pure-exploration pivots (view_file / search / grep / ...) are not
    skipped — they're tagged in ``extra_env_info.pivot_type`` so the
    operator can filter at training time without re-running the
    converter.
    """
    problem_statement = str(row.get("problem_statement") or "").strip()
    if not problem_statement:
        raise ValueError("SWE-Gym row missing problem_statement")
    messages = row.get("messages")
    if isinstance(messages, list) and messages:
        first_call = _first_assistant_tool_call(messages)

        function = first_call.get("function")
        if not isinstance(function, Mapping):
            raise ValueError("SWE-Gym tool_call missing 'function' object")
        tool_name = str(function.get("name") or "").strip()
        if not tool_name:
            raise ValueError("SWE-Gym tool_call missing function name")

        raw_arguments = function.get("arguments")
        if isinstance(raw_arguments, Mapping):
            arguments: JsonDict = dict(raw_arguments)
        elif isinstance(raw_arguments, str):
            try:
                parsed = json.loads(raw_arguments)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"SWE-Gym tool_call {tool_name!r} has malformed JSON arguments: {exc}"
                ) from exc
            if not isinstance(parsed, dict):
                raise ValueError(
                    f"SWE-Gym tool_call {tool_name!r} arguments must decode to an object"
                )
            arguments = parsed
        elif raw_arguments is None:
            arguments = {}
        else:
            raise ValueError(
                f"SWE-Gym tool_call {tool_name!r} arguments must be a JSON string or object"
            )
        pivot_source = "trajectory_first_tool_call"
    else:
        patch = str(row.get("patch") or row.get("gold_patch") or "").strip()
        if not patch:
            raise ValueError("SWE-Gym row missing messages trajectory and patch fallback")
        first_path = _first_patch_file_path(patch)
        if not first_path:
            raise ValueError("SWE-Gym patch fallback could not determine modified file")
        tool_name = "view_file"
        arguments = {"path": first_path}
        pivot_source = "synthetic_from_gold_patch"

    repo = str(row.get("repo") or "").strip()
    instance_id = str(row.get("instance_id") or "").strip()
    pivot_type = "exploration" if tool_name in SWE_PIVOT_EXPLORATION_TOOLS else "action"

    gold_tool_call = {"name": tool_name, "arguments": arguments}

    user_content = (
        "Decide the next single tool call that best advances the issue "
        "below. Use only the provided tool schema.\n\n"
        f"Repository: {repo or '<unspecified>'}\n"
        f"Instance: {instance_id or '<unspecified>'}\n\n"
        f"Issue:\n{problem_statement}"
    )

    return make_record(
        spec=spec,
        row=row,
        question=problem_statement,
        expected_answer=gold_tool_call,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        tools=SWE_PIVOT_TOOLS,
        reward_config={
            "verifier": "argument_match",
            "max_score": 1.0,
            "match": ["name", "arguments"],
        },
        extra_env_info={
            "repo": repo,
            "instance_id": instance_id,
            "gold_tool_call": gold_tool_call,
            "pivot_type": pivot_type,
            "pivot_source": pivot_source,
        },
    )


# SWE2 OpenHands rollout tool schema (task017 Session 2). Larger than
# the SWE1 pivot tool set because the SWE2 verifier rewards a *full
# rollout* (binary patch+tests pass), not a single first call — the
# agent needs to read, edit, and verify. Tools mirror the OpenHands
# default action set.
SWE2_OPENHANDS_TOOLS: list[JsonDict] = [
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "Show the contents of a file at the given repo-relative path.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the repo for a literal string or pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Apply an edit to a file by replacing a span of text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command in the sandboxed working directory.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run the project's test suite, optionally scoped.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_patch",
            "description": "Submit the final unified diff that resolves the issue.",
            "parameters": {
                "type": "object",
                "properties": {"patch": {"type": "string"}},
                "required": ["patch"],
            },
        },
    },
]


def _normalize_trajectory_message(message: Mapping[str, Any]) -> JsonDict:
    """Strip OpenAI-tool-call argument JSON to dict form, drop unknown keys.

    Keeps the trajectory shape minimal and stable so the policy isn't
    learning artifacts of one upstream's serialization choices.
    """
    role = str(message.get("role") or "").strip() or "user"
    out: JsonDict = {"role": role}
    if "content" in message and message["content"] is not None:
        out["content"] = message["content"]
    tool_calls_raw = message.get("tool_calls")
    if isinstance(tool_calls_raw, list) and tool_calls_raw:
        normalized: list[JsonDict] = []
        for call in tool_calls_raw:
            if not isinstance(call, Mapping):
                continue
            function = call.get("function")
            if not isinstance(function, Mapping):
                continue
            name = str(function.get("name") or "").strip()
            if not name:
                continue
            raw_args = function.get("arguments")
            if isinstance(raw_args, Mapping):
                args: JsonDict = dict(raw_args)
            elif isinstance(raw_args, str):
                try:
                    parsed = json.loads(raw_args)
                except json.JSONDecodeError:
                    parsed = {}
                args = parsed if isinstance(parsed, dict) else {}
            else:
                args = {}
            normalized.append({"name": name, "arguments": args})
        if normalized:
            out["tool_calls"] = normalized
    tool_call_id = message.get("tool_call_id")
    if tool_call_id:
        out["tool_call_id"] = str(tool_call_id)
    return out


def transform_swe_gym_openhands_trace(
    row: Mapping[str, Any], spec: Mapping[str, Any]
) -> JsonDict:
    """Convert one SWE-Gym-Lite agent trajectory into the SWE2 OpenHands shape.

    Unlike ``transform_swe_gym_lite_pivot`` (task016 Session 2), which
    keeps only the first tool call as ground truth, this converter
    preserves the *whole trajectory* — the SWE2 verifier (``openhands_loop``)
    rewards the binary patch+tests outcome of a full agent rollout, so
    the policy needs the entire reference trajectory available at
    training time (for behavioral cloning, distillation, or reward
    shaping during exploration).

    Gold answer is the unified-diff patch the trajectory produces — read
    from a top-level ``patch`` / ``gold_patch`` field if present, else
    pulled from the last ``submit_patch`` tool call in the trajectory.
    Raises ``ValueError`` if no patch can be located — without ground
    truth the reward signal degenerates.

    ``extra_env_info.sif_source`` defaults to ``swegym`` (the SIF family
    that ships SWE-Gym containers). Operators with R2E-Gym sources
    override via spec override or a downstream re-tag.
    """
    problem_statement = str(row.get("problem_statement") or "").strip()
    if not problem_statement:
        raise ValueError("SWE-Gym row missing problem_statement")
    messages_raw = row.get("messages")
    messages = messages_raw if isinstance(messages_raw, list) and messages_raw else []

    gold_patch_raw = row.get("gold_patch") or row.get("patch")
    if not gold_patch_raw and messages:
        # Fallback: scan trajectory for a `submit_patch` tool call
        for message in messages:
            if not isinstance(message, Mapping):
                continue
            if message.get("role") != "assistant":
                continue
            for call in message.get("tool_calls") or []:
                if not isinstance(call, Mapping):
                    continue
                function = call.get("function") or {}
                if not isinstance(function, Mapping):
                    continue
                if function.get("name") != "submit_patch":
                    continue
                raw_args = function.get("arguments")
                args = raw_args
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = None
                if isinstance(args, Mapping):
                    candidate = args.get("patch")
                    if candidate:
                        gold_patch_raw = candidate
                        break
            if gold_patch_raw:
                break
    if not gold_patch_raw:
        raise ValueError(
            "SWE-Gym row has no gold patch — checked top-level patch / "
            "gold_patch and trajectory submit_patch calls"
        )
    gold_patch = str(gold_patch_raw).strip()

    repo = str(row.get("repo") or "").strip()
    instance_id = str(row.get("instance_id") or "").strip()
    sif_source = str(row.get("sif_source") or "swegym").strip() or "swegym"

    if messages:
        reference_trajectory = [
            _normalize_trajectory_message(message)
            for message in messages
            if isinstance(message, Mapping)
        ]
        trajectory_source = "upstream_messages"
    else:
        first_path = _first_patch_file_path(gold_patch)
        if not first_path:
            raise ValueError(
                "SWE-Gym row missing messages trajectory and patch fallback "
                "could not determine modified file"
            )
        reference_trajectory = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"name": "view_file", "arguments": {"path": first_path}},
                ],
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"name": "submit_patch", "arguments": {"patch": gold_patch}},
                ],
            },
        ]
        trajectory_source = "synthetic_from_gold_patch"

    user_content = (
        "Resolve the software issue below using the OpenHands agent "
        "loop. Submit your final unified-diff patch via "
        "`submit_patch` only when the test suite passes.\n\n"
        f"Repository: {repo or '<unspecified>'}\n"
        f"Instance: {instance_id or '<unspecified>'}\n\n"
        f"Issue:\n{problem_statement}"
    )

    return make_record(
        spec=spec,
        row=row,
        question=problem_statement,
        expected_answer=gold_patch,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        tools=SWE2_OPENHANDS_TOOLS,
        reward_config={
            "verifier": "openhands_loop",
            "max_score": 1.0,
            "match": ["patch_applies", "tests_pass"],
        },
        extra_env_info={
            "repo": repo,
            "instance_id": instance_id,
            "sif_source": sif_source,
            "gold_patch": gold_patch,
            "reference_trajectory": reference_trajectory,
            "trajectory_turns": len(reference_trajectory),
            "trajectory_source": trajectory_source,
        },
    )


# HelpSteer-2 attributes the aggregate label derivation considers.
# Per HelpSteer-2 paper: helpfulness + coherence dominate preference
# at scale; correctness can flip the call when the helpfulness gap is
# small. Verbosity and complexity intentionally NOT used — those should
# not directly drive preference (downstream RLHF will reward concise
# over verbose given equal helpfulness, but the *training pair* label
# should reflect preference on substance not length).
_HELPSTEER2_AGGREGATE_ATTRS: tuple[str, ...] = (
    "helpfulness",
    "coherence",
    "correctness",
)


def _helpsteer2_aggregate_score(side: str, row: Mapping[str, Any]) -> float | None:
    """Aggregate per-side rating attributes into one preference score.

    *side* is "a" or "b"; we read ``helpfulness_<side>`` etc. Returns
    None if every attribute is missing on that side — the caller falls
    back to the explicit preference_label path.
    """
    found_any = False
    total = 0.0
    for attr in _HELPSTEER2_AGGREGATE_ATTRS:
        value = row.get(f"{attr}_{side}")
        if value is None:
            continue
        try:
            total += float(value)
        except (TypeError, ValueError):
            continue
        found_any = True
    return total if found_any else None


def _is_helpsteer2_scalar_row(row: Mapping[str, Any]) -> bool:
    """Return True for the public HelpSteer-2 scalar-rating row shape."""
    return (
        "response" in row
        and not any(key in row for key in ("response_a", "response_b", "chosen", "rejected"))
    )


def _make_helpsteer2_pair_row(row_a: Mapping[str, Any], row_b: Mapping[str, Any]) -> JsonDict:
    prompt = str(row_a.get("prompt") or "").strip()
    response_a = str(row_a.get("response") or "").strip()
    response_b = str(row_b.get("response") or "").strip()
    digest = hashlib.sha1(
        f"{prompt}\0{response_a}\0{response_b}".encode()
    ).hexdigest()[:16]
    pair: JsonDict = {
        "id": f"helpsteer2_pair_{digest}",
        "prompt": prompt,
        "response_a": response_a,
        "response_b": response_b,
        "source_ids": [source_id(row_a), source_id(row_b)],
    }
    for attr in ("helpfulness", "coherence", "correctness", "complexity", "verbosity"):
        pair[f"{attr}_a"] = row_a.get(attr)
        pair[f"{attr}_b"] = row_b.get(attr)
    return pair


def iter_helpsteer2_preference_pairs(
    rows: Iterable[Mapping[str, Any]],
) -> Iterator[Mapping[str, Any]]:
    """Yield pairwise rows from HelpSteer-2's public scalar-rating data.

    The HF dataset's default config stores one response per row with
    scalar helpfulness/coherence/correctness ratings. In the pinned
    snapshot, responses for the same prompt are adjacent pairs. The
    converter consumes pair rows, so this streaming adapter buffers the
    first scalar row for a prompt and yields a synthetic
    ``response_a``/``response_b`` pair when the mate arrives. Already
    paired rows pass through unchanged for synthetic tests and future
    snapshots.
    """
    pending_by_prompt: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not _is_helpsteer2_scalar_row(row):
            yield row
            continue
        prompt = str(row.get("prompt") or "").strip()
        response = str(row.get("response") or "").strip()
        if not prompt or not response:
            yield row
            continue
        first = pending_by_prompt.pop(prompt, None)
        if first is None:
            pending_by_prompt[prompt] = row
            continue
        yield _make_helpsteer2_pair_row(first, row)


def transform_helpsteer2_pref(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one HelpSteer-2 preference row into the GenRM compare shape.

    HelpSteer-2 ships in two flavors:

    1. **Explicit-pair** rows carry ``response_a`` + ``response_b`` plus a
       ``preference_label`` ("A" or "B").
    2. **Attribute-derived** rows carry the same paired responses plus
       per-side rating attributes (``helpfulness_a``, ``coherence_a``,
       ``correctness_a``, mirrored ``_b``). Preference label is derived
       by aggregating those three attributes per side; tie → defaults to
       "A" (stable ordering; the operator can post-filter ties).

    Output shape per plan §5.6 RLHF acceptance:

    - ``responses_create_params.input``: [system, user(prompt)]
    - ``extra_env_info.completion_a`` / ``completion_b``: the two
      candidate completions the policy is being judged against
    - ``extra_env_info.preference_label``: "A" or "B"
    - ``expected_answer``: matches ``preference_label`` so existing
      verifier wiring (which reads ``expected_answer``) just works
    - ``reward_config.verifier``: ``genrm_compare``
    """
    prompt = str(row.get("prompt") or "").strip()
    if not prompt:
        raise ValueError("HelpSteer-2 row missing prompt")

    response_a = str(row.get("response_a") or row.get("chosen") or "").strip()
    response_b = str(row.get("response_b") or row.get("rejected") or "").strip()
    if not response_a or not response_b:
        raise ValueError(
            "HelpSteer-2 row missing one or both responses "
            "(expected response_a/response_b or chosen/rejected)"
        )

    explicit_label_raw = row.get("preference_label")
    if explicit_label_raw is not None:
        explicit_label = str(explicit_label_raw).strip().upper()
        if explicit_label not in ("A", "B"):
            raise ValueError(
                f"HelpSteer-2 preference_label must be 'A' or 'B', got "
                f"{explicit_label_raw!r}"
            )
        preference_label = explicit_label
        derivation = "explicit_label"
    else:
        score_a = _helpsteer2_aggregate_score("a", row)
        score_b = _helpsteer2_aggregate_score("b", row)
        if score_a is None and score_b is None:
            raise ValueError(
                "HelpSteer-2 row has neither preference_label nor "
                "rating attributes (helpfulness/coherence/correctness)"
            )
        # Treat one-sided missing data as "the side with data is the
        # preferred side" — preserves signal rather than dropping rows.
        if score_a is None:
            preference_label = "B"
        elif score_b is None:
            preference_label = "A"
        elif score_a > score_b:
            preference_label = "A"
        elif score_b > score_a:
            preference_label = "B"
        else:
            # Tie — default to A (stable ordering). Operators can
            # post-filter tied rows via metadata.
            preference_label = "A"
        derivation = "aggregate_score"

    return make_record(
        spec=spec,
        row=row,
        question=prompt,
        expected_answer=preference_label,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": prompt},
        ],
        reward_config={
            "verifier": "genrm_compare",
            "max_score": 1.0,
            "match": ["preference_label"],
        },
        extra_env_info={
            "completion_a": response_a,
            "completion_b": response_b,
            "preference_label": preference_label,
            "label_derivation": derivation,
        },
    )


# Aya dataset (CohereLabs/aya_dataset) language subset for plan §7
# multilingual coverage: de / es / fr / it / ja / zh. M0 smoke filter
# pulls only these 6 codes; full 65-language set is M2 task027 scope.
AYA_TARGET_LANGUAGES: frozenset[str] = frozenset({
    "Standard Arabic",   # used by Aya for ar — kept for forward compat
    "German",
    "Spanish",
    "French",
    "Italian",
    "Japanese",
    "Chinese",
    "Simplified Chinese",
    "Traditional Chinese",
})

# Per-language ISO codes the converter accepts on the language_code
# column (Aya sometimes stamps language as a full name, sometimes as
# ISO; converter normalizes via either field).
AYA_TARGET_LANGUAGE_CODES: frozenset[str] = frozenset({
    "de", "es", "fr", "it", "ja", "zh", "zh-Hans", "zh-Hant", "zh-CN", "zh-TW",
})


def _aya_language_in_scope(row: Mapping[str, Any]) -> bool:
    """True if *row*'s language is one of the M0 smoke 6.

    Aya rows carry both ``language`` (full English name like "German")
    and ``language_code`` (ISO). Accept either since upstream snapshots
    have shipped both conventions.
    """
    language = str(row.get("language") or "").strip()
    code = str(row.get("language_code") or "").strip()
    if language in AYA_TARGET_LANGUAGES:
        return True
    if code in AYA_TARGET_LANGUAGE_CODES:
        return True
    return False


def transform_aya_multilingual(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one Aya (CohereLabs/aya_dataset) row to the M0 contract.

    Aya is human-written instruction/response pairs across ~65
    languages. M0 smoke restricts to 6 languages (de / es / fr / it /
    ja / zh) — rows outside the set raise ``ValueError`` so the prep
    pipeline's row-level error counter surfaces them rather than
    silently emitting.

    Required input fields:

    - ``inputs`` (or ``instruction``): user prompt
    - ``targets`` (or ``response``): gold reference response
    - ``language`` / ``language_code``: at least one must resolve to a
      language in scope

    Output shape uses the multilingual_exact_or_contains verifier
    (defined in ``run_m0_health_baseline.py``) which normalizes case
    and whitespace per Unicode and then runs the same exact-or-contains
    check as the English HotpotQA / MuSiQue paths.
    """
    if not _aya_language_in_scope(row):
        raise ValueError(
            "Aya row language outside M0 smoke scope (de/es/fr/it/ja/zh)"
        )
    instruction = str(row.get("inputs") or row.get("instruction") or "").strip()
    if not instruction:
        raise ValueError("Aya row missing 'inputs' / 'instruction'")
    target = str(row.get("targets") or row.get("response") or "").strip()
    if not target:
        raise ValueError("Aya row missing 'targets' / 'response'")
    language = str(row.get("language") or "").strip() or None
    language_code = str(row.get("language_code") or "").strip() or None

    return make_record(
        spec=spec,
        row=row,
        question=instruction,
        expected_answer=target,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": instruction},
        ],
        reward_config={
            "verifier": "multilingual_exact_or_contains",
            "max_score": 1.0,
            "match": ["normalized_unicode_text"],
        },
        extra_env_info={
            "language": language,
            "language_code": language_code,
        },
    )


def transform_multilingual_ifeval(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert a multilingual IF row to the M2 sandbox scaffold contract.

    Session 1 intentionally uses the existing
    ``multilingual_exact_or_contains`` verifier as an offline fallback.
    Production instruction-following judge scoring is recorded as
    deferred metadata so the row shape can be exercised without a judge
    model or cluster runtime.
    """
    instruction = str(
        row.get("prompt") or row.get("instruction") or row.get("question") or ""
    ).strip()
    if not instruction:
        raise ValueError("multilingual IF row must contain prompt/instruction/question")
    expected_answer = str(
        row.get("reference_answer")
        or row.get("target")
        or row.get("expected_answer")
        or row.get("answer")
        or row.get("response")
        or ""
    ).strip()
    if not expected_answer:
        raise ValueError("multilingual IF row must contain a reference answer")
    language = str(row.get("language") or "").strip() or None
    language_code = str(row.get("language_code") or row.get("locale") or "").strip() or None
    if language is None and language_code is None:
        raise ValueError("multilingual IF row must contain language or language_code")

    constraints = string_list(row.get("constraints") or row.get("instruction_tags"))
    constraint_block = "\n".join(f"- {item}" for item in constraints) if constraints else "- see prompt"
    user_content = (
        "Follow the multilingual instruction and every constraint.\n\n"
        f"Language: {language or language_code}\n"
        f"Instruction:\n{instruction}\n\n"
        f"Constraints:\n{constraint_block}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=instruction,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "multilingual_exact_or_contains",
            "max_score": 1.0,
            "match": ["normalized_unicode_text"],
            "judge_model": "deferred",
        },
        extra_env_info={
            "language": language,
            "language_code": language_code,
            "constraints": constraints,
            "source_task_id": row.get("id") or row.get("task_id"),
            "judge_model": {
                "required_for_production": True,
                "sandbox_fallback": "multilingual_exact_or_contains",
                "status": "deferred_to_task027_followup",
            },
        },
    )


def transform_multilingual_humaneval(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert a multilingual HumanEval-style row to the M2 scaffold.

    Code execution is explicitly deferred. The sandbox contract uses
    the Unicode exact-or-contains verifier against the reference
    solution so converter, registry, and routing metadata can be tested
    without launching a code sandbox.
    """
    prompt = str(
        row.get("prompt") or row.get("instruction") or row.get("question") or ""
    ).strip()
    if not prompt:
        raise ValueError("multilingual HumanEval row must contain prompt/instruction/question")
    reference_solution = str(
        row.get("canonical_solution")
        or row.get("reference_solution")
        or row.get("solution")
        or row.get("expected_answer")
        or ""
    ).strip()
    if not reference_solution:
        raise ValueError("multilingual HumanEval row must contain a reference solution")
    language = str(row.get("language") or "").strip() or None
    language_code = str(row.get("language_code") or row.get("locale") or "").strip() or None
    if language is None and language_code is None:
        raise ValueError("multilingual HumanEval row must contain language or language_code")

    tests = string_list(row.get("tests") or row.get("test") or row.get("unit_tests"))
    user_content = (
        "Solve the multilingual programming task. Return the complete solution.\n\n"
        f"Language: {language or language_code}\n"
        f"Task:\n{prompt}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=prompt,
        expected_answer=reference_solution,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "multilingual_exact_or_contains",
            "max_score": 1.0,
            "match": ["normalized_unicode_text"],
            "code_execution": "deferred",
        },
        extra_env_info={
            "language": language,
            "language_code": language_code,
            "source_task_id": row.get("id") or row.get("task_id"),
            "unit_tests": tests,
            "code_execution": {
                "required_for_production": True,
                "sandbox_fallback": "multilingual_exact_or_contains",
                "status": "deferred_to_task027_followup",
            },
        },
    )


# LongAlpaca / long-context QA M0 smoke caps (task057 Session 2).
#
# LongAlpaca-12k carries documents spanning ~16K to ~100K characters
# (rough est. ~4-25K tokens). M0 smoke caps doc length to keep the
# oracle baseline tractable; rows above the cap are dropped (not
# truncated — truncation changes the QA answer span semantics, so
# silent truncation would corrupt the eval). True long-context (256K
# to 1M+) is M2 task028 / task037 scope.
LONGALPACA_MAX_DOC_CHARS: int = 32_000  # ~8K tokens; M0 smoke ceiling


def _approx_token_count(text: str) -> int:
    """Rough char-based token estimate (~4 chars/token for English).

    Used only for telemetry (`doc_token_estimate` field). Not for
    truncation decisions — those use exact char counts.
    """
    return max(1, len(text) // 4)


def transform_longalpaca_qa(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one LongAlpaca-12k row to the M0 long_context_qa_smoke contract.

    LongAlpaca-12k is Alpaca-format with optional long ``input`` field:

    - ``instruction``: the question (e.g., "What does the document say about X?")
    - ``input``: the long document the question is grounded in (16K-100K chars)
    - ``output``: the gold reference answer

    Rows missing ``input`` are dropped (this env requires a document
    context; question-only Alpaca rows don't belong in long-context QA).
    Rows whose ``input`` exceeds ``LONGALPACA_MAX_DOC_CHARS`` are also
    dropped — truncation would change answer-span semantics.

    Output uses the ``long_context_qa_stub`` verifier (M0 oracle stub
    delegating to contains-match; real long-context verifier is M2
    task028 territory).
    """
    instruction = str(row.get("instruction") or "").strip()
    if not instruction:
        raise ValueError("LongAlpaca row missing 'instruction'")
    output = str(row.get("output") or "").strip()
    if not output:
        raise ValueError("LongAlpaca row missing 'output'")
    document = str(row.get("input") or "").strip()
    if not document:
        raise ValueError("LongAlpaca row missing 'input' (long document required)")
    if len(document) > LONGALPACA_MAX_DOC_CHARS:
        raise ValueError(
            f"LongAlpaca row exceeds M0 smoke cap "
            f"({len(document)} > {LONGALPACA_MAX_DOC_CHARS} chars); "
            "real long-context support is M2 task028 / task037"
        )

    user_content = (
        f"Document:\n{document}\n\n"
        f"Question: {instruction}"
    )

    return make_record(
        spec=spec,
        row=row,
        question=instruction,
        expected_answer=output,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "long_context_qa_stub",
            "max_score": 1.0,
            "match": ["normalized_contains"],
        },
        extra_env_info={
            "doc_length_chars": len(document),
            "doc_token_estimate": _approx_token_count(document),
            "question": instruction,
        },
    )


# BIRD SQL normalization helpers (task057 Session 3).

# SQL is whitespace-insensitive and keywords are case-insensitive. The
# M0 oracle baseline uses normalized string match (NOT real execution
# — execution requires a database sandbox; that's task024 / M2 BIRD
# extension territory). Normalization:
#   - Lowercase all tokens
#   - Collapse runs of whitespace to single space
#   - Strip leading/trailing whitespace + trailing semicolon
#   - Remove surrounding backticks / quotes around identifiers (BIRD
#     mixes conventions across schemas)
_SQL_BACKTICK_RE = re.compile(r"`")
_SQL_WHITESPACE_RE = re.compile(r"\s+")


def normalize_sql(value: Any) -> str:
    """Normalize a SQL string for string-match scoring."""
    text = str(value or "").lower().strip()
    text = _SQL_BACKTICK_RE.sub("", text)
    text = _SQL_WHITESPACE_RE.sub(" ", text)
    if text.endswith(";"):
        text = text[:-1].rstrip()
    return text


def score_sql_execution_match_with_diagnostics(
    candidate: Any,
    expected: Any,
    execution_context: Mapping[str, Any] | None = None,
) -> tuple[float, JsonDict]:
    """Oracle stub for the BIRD SQL env.

    M0 baseline uses normalized SQL string match. M2 task024 Session 1
    adds an opt-in local SQLite scaffold: if a record carries
    ``extra_env_info.sql_execution`` with schema + fixtures, execute
    candidate and gold SQL against an in-memory SQLite DB and compare
    result rows. Records without that context keep the M0 fallback.
    """
    if execution_context:
        from nemotron.recipes.super3.milestones.m2_sql_execution import (
            has_sqlite_execution_context,
            score_sqlite_execution_match,
        )

        if has_sqlite_execution_context(execution_context):
            result = score_sqlite_execution_match(
                candidate,
                expected,
                execution_context,
            )
            result.diagnostics.setdefault("normalized_sql", normalize_sql(candidate))
            result.diagnostics.setdefault("normalized_expected_sql", normalize_sql(expected))
            return result.score, result.diagnostics

    norm_candidate = normalize_sql(candidate)
    norm_expected = normalize_sql(expected)
    diagnostics = {
        "sql_execution_mode": "normalized_sql",
        "normalized_sql": norm_candidate,
        "normalized_expected_sql": norm_expected,
    }
    if not norm_expected:
        diagnostics["sql_match"] = False
        return 0.0, diagnostics
    if norm_candidate == norm_expected:
        diagnostics["sql_match"] = True
        return 1.0, diagnostics
    score = 1.0 if norm_expected in norm_candidate else 0.0
    diagnostics["sql_match"] = bool(score == 1.0)
    return score, diagnostics


def score_sql_execution_match(
    candidate: Any,
    expected: Any,
    execution_context: Mapping[str, Any] | None = None,
) -> float:
    """Return only the score for callers that do not need diagnostics."""
    score, _ = score_sql_execution_match_with_diagnostics(
        candidate,
        expected,
        execution_context,
    )
    return score


def bird_sql_execution_context(row: Mapping[str, Any], *, db_id: str) -> JsonDict:
    """Extract optional local SQLite execution context from a BIRD-like row."""
    schema_sql = (
        row.get("schema_sql")
        or row.get("sqlite_schema")
        or row.get("schema")
        or row.get("db_schema")
    )
    fixture_rows = row.get("fixture_rows") or row.get("sqlite_fixture_rows")
    context: JsonDict = {
        "engine": "sqlite",
        "db_id": db_id,
        "available": bool(schema_sql or fixture_rows),
    }
    if schema_sql:
        context["schema_sql"] = str(schema_sql)
    if fixture_rows:
        context["fixture_rows"] = fixture_rows
    if "order_sensitive" in row:
        context["order_sensitive"] = bool(row["order_sensitive"])
    if "max_sql_steps" in row:
        context["max_sql_steps"] = row["max_sql_steps"]
    if not context["available"]:
        context["reason"] = "row has no local SQLite schema/fixtures"
    return context


def transform_bird_sql(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one BIRD SQL row to the M0 sql_text_to_query contract.

    BIRD rows (from `bird-bench/bird` train + `birdsql/bird_mini_dev`)
    typically carry:

    - ``question_id``: integer id (used for source_id)
    - ``db_id``: schema name (one of BIRD's 7 schemas)
    - ``question``: natural-language question
    - ``evidence``: optional hint text the model is allowed to use
    - ``SQL`` or ``query`` or ``sql``: gold SQL query
    - ``difficulty``: easy / medium / hard

    Output uses ``sql_execution_match`` verifier. Rows that carry
    local ``schema_sql`` / ``fixture_rows`` also carry an opt-in
    SQLite execution context for M2 task024 Session 1; plain BIRD rows
    keep the M0 normalized-SQL fallback until the DB sandbox lands.

    Cross-schema generalization is BIRD's central evaluation property,
    so ``db_id`` is preserved in ``extra_env_info`` for downstream
    per-schema stratification.
    """
    question = str(row.get("question") or "").strip()
    if not question:
        raise ValueError("BIRD row missing 'question'")
    # BIRD ships gold SQL under different keys per snapshot
    gold_sql = (
        row.get("SQL") or row.get("sql") or row.get("query") or row.get("gold_sql")
    )
    gold_sql = str(gold_sql or "").strip()
    if not gold_sql:
        raise ValueError(
            "BIRD row missing gold SQL (checked SQL / sql / query / gold_sql)"
        )
    db_id = str(row.get("db_id") or "").strip()
    if not db_id:
        raise ValueError("BIRD row missing 'db_id' (schema name required for grounding)")
    evidence = str(row.get("evidence") or "").strip()
    difficulty = str(row.get("difficulty") or "").strip() or None

    # User-turn content embeds the schema name + question + evidence
    # (if present). The schema itself is not included verbatim — BIRD
    # schemas are large; the model is expected to know the schema by
    # name during training (oracle pass-through) and to query DB
    # introspection at runtime in production.
    user_parts = [f"Database: {db_id}", f"Question: {question}"]
    if evidence:
        user_parts.append(f"Evidence: {evidence}")
    user_content = "\n\n".join(user_parts)

    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=gold_sql,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "sql_execution_match",
            "max_score": 1.0,
            "match": ["normalized_sql"],
        },
        extra_env_info={
            "db_id": db_id,
            "question_id": row.get("question_id"),
            "difficulty": difficulty,
            "has_evidence": bool(evidence),
            "sql_execution": bird_sql_execution_context(row, db_id=db_id),
        },
    )


# Nemotron-Content-Safety-Reasoning verdict vocabulary (task057
# Session 5). README of the dataset uses these three labels; verifier
# normalizes case + maps a few common aliases (e.g., "safe" → "allow",
# "unsafe" → "block").
SAFETY_VERDICT_CANONICAL: tuple[str, ...] = ("allow", "block", "escalate")

# Map alternate labels to the canonical 3. Operators add new aliases
# here when a snapshot ships an unexpected label.
SAFETY_VERDICT_ALIASES: dict[str, str] = {
    "allow": "allow",
    "safe": "allow",
    "pass": "allow",
    "ok": "allow",
    "block": "block",
    "unsafe": "block",
    "refuse": "block",
    "reject": "block",
    "deny": "block",
    "escalate": "escalate",
    "review": "escalate",
    "maybe": "escalate",
}


def _canonicalize_safety_verdict(raw: Any) -> str | None:
    """Return canonical verdict (allow/block/escalate) or None if absent.

    Accepts case-insensitive label; strips whitespace; runs through
    the alias map. ``None`` signals the row didn't carry a verdict —
    caller treats that as a row-quality bug (M0 safety dataset MUST
    label every row).
    """
    if raw is None:
        return None
    text = str(raw).strip().lower()
    if not text:
        return None
    return SAFETY_VERDICT_ALIASES.get(text)


def transform_nemotron_safety_reasoning(
    row: Mapping[str, Any], spec: Mapping[str, Any]
) -> JsonDict:
    """Convert one Nemotron-Content-Safety-Reasoning row to the M0 contract.

    Per README of the upstream dataset, rows ship a user prompt + a
    safety verdict + a reasoning explanation. The dataset viewer
    occasionally reports schema errors so this converter is permissive
    about field names — accepts the common variants:

    - **prompt** column: ``prompt`` / ``input`` / ``question`` / ``messages``
      (if ``messages`` is a list, last user message is taken)
    - **verdict** column: ``verdict`` / ``label`` / ``safety`` /
      ``classification`` / ``decision``
    - **reasoning** column (optional): ``reasoning`` / ``explanation`` /
      ``rationale``
    - **category** column (optional): ``category`` / ``risk_category`` /
      ``policy`` (informational; doesn't change reward)

    M0 verifier is `safety_judge_stub` — case-insensitive contains-
    match against the canonical verdict (allow / block / escalate).
    Real judge-model scoring is M2 task029 (safety) territory.
    """
    prompt = _extract_safety_prompt(row)
    if not prompt:
        raise ValueError(
            "Nemotron-Safety row missing prompt "
            "(checked prompt / input / question / messages)"
        )
    raw_verdict = (
        row.get("verdict")
        or row.get("label")
        or row.get("safety")
        or row.get("classification")
        or row.get("decision")
    )
    verdict = _canonicalize_safety_verdict(raw_verdict)
    if verdict is None:
        raise ValueError(
            "Nemotron-Safety row missing or unrecognized verdict "
            f"(raw={raw_verdict!r}; canonical labels: "
            f"{sorted(set(SAFETY_VERDICT_ALIASES.values()))})"
        )
    reasoning = str(
        row.get("reasoning")
        or row.get("explanation")
        or row.get("rationale")
        or ""
    ).strip()
    category = str(
        row.get("category")
        or row.get("risk_category")
        or row.get("policy")
        or ""
    ).strip() or None

    return make_record(
        spec=spec,
        row=row,
        question=prompt,
        expected_answer=verdict,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": prompt},
        ],
        reward_config={
            "verifier": "safety_judge_stub",
            "max_score": 1.0,
            "match": ["canonical_verdict"],
        },
        extra_env_info={
            "verdict": verdict,
            "reasoning": reasoning,
            "category": category,
        },
    )


def count_python_code_blocks(text: Any) -> int:
    """Return the number of Python code blocks (fenced or `<python>`-tagged)
    found in *text*. Used by `transform_mathcode_instruct` (task057
    Session 6) to attest the gold solution actually contains a tool-use
    step; the M0 health gate later asserts the same on candidate output.
    """
    if text is None:
        return 0
    return len(PYTHON_CODE_BLOCK_RE.findall(str(text)))


def is_numinamath_source_id(source_id: str, numinamath_index: Iterable[str]) -> bool:
    """Return True iff *source_id* appears in *numinamath_index*.

    task057 Session 6 NuminaMath dedup hook: MathCodeInstruct shares
    several seed problems with NuminaMath; per task README the policy is
    "重的全部移到 math_with_tools (因为它的代码块更有信息)" — i.e. drop
    NuminaMath rows whose source_id is present in MathCodeInstruct.

    Index construction is Session 6.5 territory (needs the actual SHA-
    pinned NuminaMath snapshot to enumerate source_ids); this helper is
    the pure-function building block that the future bridge will call.
    """
    if not source_id:
        return False
    return source_id in set(numinamath_index)


def transform_mathcode_instruct(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert one MathLLMs/MathCodeInstruct row to the M0 math_with_tools contract.

    Layout per row (alias-tolerant — upstream snapshots vary by minor
    revision):
      - **problem** column: ``problem`` / ``question`` / ``instruction`` / ``input``
      - **solution** column: ``solution`` / ``response`` / ``output`` / ``answer``

    Solutions are CoT with embedded Python code (``<python>...</python>``
    or ` ```python ... ``` `) culminating in a ``\\boxed{...}`` answer.
    We preserve the full solution text in ``extra_env_info.reference_solution``
    so SFT supervision keeps the tool-use trace verbatim, and surface
    ``has_code_block`` / ``code_block_count`` for the health gate to
    verify rows actually carry a code-block.

    M0 verifier is ``math_with_tools_match`` — extracts the candidate's
    last ``\\boxed{...}`` and compares against gold after normalization.
    Real Python-execution + math-judge scoring is M1 task011 territory;
    the "_match" suffix signals this is the oracle stub.
    """
    problem = (
        row.get("problem")
        or row.get("question")
        or row.get("instruction")
        or row.get("input")
    )
    if not isinstance(problem, str) or not problem.strip():
        raise ValueError(
            "MathCodeInstruct row missing problem "
            "(checked problem / question / instruction / input)"
        )
    problem = problem.strip()

    solution_raw = (
        row.get("solution")
        or row.get("response")
        or row.get("output")
        or row.get("answer")
    )
    if not isinstance(solution_raw, str) or not solution_raw.strip():
        raise ValueError(
            "MathCodeInstruct row missing solution "
            "(checked solution / response / output / answer)"
        )
    solution = solution_raw.strip()

    boxed = extract_boxed_answer(solution)
    if not boxed:
        raise ValueError(
            "MathCodeInstruct row missing \\boxed{...} final answer in solution"
        )

    code_block_count = count_python_code_blocks(solution)
    has_code_block = code_block_count > 0

    return make_record(
        spec=spec,
        row=row,
        question=problem,
        expected_answer=boxed,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": problem},
        ],
        reward_config={
            "verifier": "math_with_tools_match",
            "max_score": 1.0,
            "normalization": ["lowercase", "strip_punctuation", "collapse_whitespace"],
        },
        extra_env_info={
            "reference_solution": solution,
            "has_code_block": has_code_block,
            "code_block_count": code_block_count,
            "boxed_answer": boxed,
        },
    )


def _extract_safety_prompt(row: Mapping[str, Any]) -> str:
    """Pull the user prompt out of a Safety row.

    Handles flat string fields (``prompt`` / ``input`` / ``question``)
    AND a ``messages``-list shape where the dataset stores the prompt
    as the last user message in a chat-style array.
    """
    for key in ("prompt", "input", "question"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    messages = row.get("messages")
    if isinstance(messages, list):
        for message in reversed(messages):
            if not isinstance(message, Mapping):
                continue
            if message.get("role") == "user":
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
    return ""


def transform_musique_search(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert a MuSiQue (Ans config) row to the M0 NeMo-Gym JSONL contract.

    Layout per row:
      - ``question``: str
      - ``paragraphs``: list[{idx, title, paragraph_text, is_supporting}]
      - ``answer``: str, plus ``answer_aliases`` as optional list[str]
      - ``question_decomposition``: list, ``answerable``: bool

    The shape mirrors HotpotQA's `transform_hotpotqa_search` — verifier is the
    same (`normalized_exact_or_contains`), and the same documents-in-user-prompt
    layout is reused. MuSiQue-only fields (decomposition, is_supporting flag,
    answer aliases) land in `extra_env_info` so M1 SFT supervision + downstream
    eval can consume them.
    """
    question = str(row.get("question", "")).strip()
    expected_answer = str(row.get("answer", "")).strip()

    raw_paragraphs = row.get("paragraphs") or []
    documents: list[JsonDict] = []
    supporting_titles: list[str] = []
    for paragraph in raw_paragraphs:
        if not isinstance(paragraph, Mapping):
            continue
        title = str(paragraph.get("title", "")).strip()
        text = str(paragraph.get("paragraph_text", "")).strip()
        is_supporting = bool(paragraph.get("is_supporting"))
        documents.append({"title": title, "text": text, "is_supporting": is_supporting})
        if is_supporting and title:
            supporting_titles.append(title)

    answer_aliases_raw = row.get("answer_aliases") or []
    answer_aliases = (
        [str(alias) for alias in answer_aliases_raw if str(alias).strip()]
        if isinstance(answer_aliases_raw, list)
        else []
    )

    user_content = (
        "Answer the multi-hop question using only the retrieved passages.\n\n"
        f"Question: {question}\n\n"
        f"Retrieved passages:\n{format_documents_for_prompt(documents)}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "normalized_exact_or_contains",
            "max_score": 1.0,
            "normalization": ["lowercase", "strip_articles", "strip_punctuation", "collapse_whitespace"],
            "answer_aliases": answer_aliases,
        },
        extra_env_info={
            "context_documents": documents,
            "supporting_titles": supporting_titles,
            "answer_aliases": answer_aliases,
            "question_decomposition": row.get("question_decomposition"),
            "answerable": row.get("answerable"),
            "search_query": question,
        },
    )


def transform_numinamath_competition(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert an `AI-MO/NuminaMath-CoT` row to the M0 JSONL contract.

    Layout per row:
      - ``problem``: str (the math problem)
      - ``solution``: str (full CoT, final answer wrapped in ``\\boxed{...}``)
      - ``source``: str (olympiad / amc / aime / cn_k12 / ...)
      - ``messages``: list (alternate conversation form, unused at M0)

    The verifier is `normalized_exact_or_contains` rather than the strict
    `normalized_numeric_exact_match` used by GSM8K — NuminaMath answers can
    be fractions, intervals, or symbolic expressions where a numeric match
    is too strict. A stricter math-aware verifier is the right answer here
    but lives in M1+ once a math-judge service is wired (plan §5.3 names
    `math_with_judge` for exactly this).
    """
    problem = str(row.get("problem", "")).strip()
    solution = str(row.get("solution", "")).strip()
    boxed = extract_boxed_answer(solution)
    if boxed:
        expected_answer = boxed
    else:
        # Fall back to the trailing token of the solution; many cn_k12 rows
        # don't use \boxed{} and just close with "答案是 X" or similar.
        expected_answer = solution.split()[-1] if solution else ""
    return make_record(
        spec=spec,
        row=row,
        question=problem,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": problem},
        ],
        reward_config={
            "verifier": "normalized_exact_or_contains",
            "max_score": 1.0,
            "normalization": ["lowercase", "strip_punctuation", "collapse_whitespace"],
        },
        extra_env_info={
            "reference_solution": solution,
            "source": row.get("source"),
            "boxed_answer": boxed,
        },
    )


def transform_lean_proof_stub(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    """Convert a Lean theorem-proof row to the M0 JSONL contract.

    Source-agnostic: the upstream column names come from ``spec['fields']``
    (the same per-spec field-rename pattern HotpotQA / MuSiQue / Hermes
    use) so once legal/product clears a Lean dataset — whether
    ``nvidia/Nemotron-Math-Proofs-v1`` (CC-BY-SA-4.0, blocked today),
    LeanDojo-Bench (MIT), mathlib4 extraction (Apache-2.0), or an
    internal source — the only change needed is the ``data_registry.yaml``
    row with the right field mapping.

    Expected logical columns (rename via ``spec['fields']``):
      - ``statement``: str — the Lean theorem statement to prove
      - ``proof``: str — the gold Lean proof text
      - ``theorem_name``: str (optional) — short identifier
      - ``language``: str (optional) — defaults to "lean4"

    M0 verifier is ``lean_proof_stub``: non-empty proof → reward 1.0.
    Real Lean compiler verification is task017 / task049 territory and
    needs the Lean toolchain inside a sandbox container.
    """
    fields = spec.get("fields") or {}
    statement_key = fields.get("statement", "statement")
    proof_key = fields.get("proof", "proof")
    name_key = fields.get("theorem_name", "theorem_name")
    language_key = fields.get("language", "language")

    statement = str(row.get(statement_key) or "").strip()
    proof = str(row.get(proof_key) or "").strip()
    if not statement:
        raise ValueError(
            f"lean_proof_stub: row missing non-empty {statement_key!r} column"
        )
    theorem_name = str(row.get(name_key) or "").strip()
    language = str(row.get(language_key) or "lean4").strip() or "lean4"

    user_content = (
        f"Prove the following theorem in {language}. "
        "Return only the proof body (no Markdown, no prose, no explanation).\n\n"
        f"Theorem:\n{statement}"
    )
    return make_record(
        spec=spec,
        row=row,
        question=statement,
        expected_answer=proof,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": user_content},
        ],
        reward_config={
            "verifier": "lean_proof_stub",
            "max_score": 1.0,
            "checks": ["nonempty_after_strip"],
        },
        extra_env_info={
            "theorem_name": theorem_name,
            "language": language,
            "statement_only": statement,
            "reference_proof": proof,
        },
    )


def transform_gsm8k_numeric_reasoning(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    question = str(row["question"]).strip()
    expected_answer = normalize_numeric_answer(row["answer"])
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_answer,
        input_messages=[
            {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
            {"role": "user", "content": question},
        ],
        reward_config={
            "verifier": "normalized_numeric_exact_match",
            "max_score": 1.0,
            "normalization": ["strip_commas", "strip_whitespace"],
        },
        extra_env_info={
            "reference_solution": row.get("answer"),
        },
    )


def parse_tool_calls(text: str) -> list[JsonDict]:
    """Extract tool calls from a Hermes-style ``<tool_call>...</tool_call>`` block.

    Returns OpenAI-style tool-call dicts. Every call carries a deterministic
    ``id`` (``call_<index>``) so downstream chat templates can pair the
    assistant ``tool_calls[].id`` with the matching ``tool`` message's
    ``tool_call_id``.
    """
    calls = []
    for index, match in enumerate(TOOL_CALL_RE.finditer(text)):
        parsed = parse_json_maybe(match.group(1), default=None)
        if not isinstance(parsed, Mapping):
            continue
        call_id = f"call_{index}"
        if "function" in parsed:
            call: JsonDict = {"type": "function", **dict(parsed)}
            existing_id = parsed.get("id")
            if isinstance(existing_id, str) and existing_id:
                call["id"] = existing_id
            else:
                call["id"] = call_id
        else:
            call = {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": parsed.get("name"),
                    "arguments": parsed.get("arguments", {}),
                },
            }
        calls.append(call)
    return calls


def strip_tool_call_blocks(text: str) -> str:
    return TOOL_CALL_RE.sub("", text).strip()


HERMES_ROLE_MAP = {
    "system": "system",
    "human": "user",
    "user": "user",
    "gpt": "assistant",
    "assistant": "assistant",
    "tool": "tool",
    "function": "tool",
    "function_response": "tool",
    "observation": "tool",
}


def convert_hermes_conversations(conversations: Iterable[Mapping[str, Any]]) -> tuple[list[JsonDict], JsonDict]:
    """Split a Hermes function-calling conversation into model input vs expected trajectory.

    `input_messages` covers the prompt context up to (but not including) the first
    assistant turn — that is what the policy sees at inference time. Everything from
    the first assistant turn onward (assistant tool calls, tool observations,
    follow-up assistant turns, final answer) is captured in `expected_trajectory`
    so that downstream verifiers can score multi-turn behavior, not just the first
    tool emission.
    """
    input_messages: list[JsonDict] = []
    expected_trajectory: list[JsonDict] = []
    expected_tool_calls: list[JsonDict] = []
    expected_assistant_content = ""
    first_assistant_seen = False
    last_assistant_content = ""
    last_assistant_had_tool_calls = False
    # Maps tool-result turns to the id of the assistant tool call they answer.
    # Hermes interleaves <tool_call> blocks with tool-result turns one-for-one,
    # so we consume call ids in arrival order.
    pending_tool_call_ids: list[str] = []

    for turn in conversations:
        raw_role = str(turn.get("from") or turn.get("role") or "").strip()
        role = HERMES_ROLE_MAP.get(raw_role)
        if role is None:
            continue
        content = str(turn.get("value") or turn.get("content") or "")
        if role == "assistant":
            tool_calls = parse_tool_calls(content)
            stripped = strip_tool_call_blocks(content)
            expected_trajectory.append(
                {
                    "role": "assistant",
                    "content": stripped,
                    "tool_calls": tool_calls,
                }
            )
            pending_tool_call_ids.extend(
                str(call.get("id")) for call in tool_calls if isinstance(call.get("id"), str)
            )
            last_assistant_content = stripped
            last_assistant_had_tool_calls = bool(tool_calls)
            if not first_assistant_seen:
                expected_tool_calls = tool_calls
                expected_assistant_content = stripped
                first_assistant_seen = True
        elif role == "tool":
            tool_call_id = pending_tool_call_ids.pop(0) if pending_tool_call_ids else None
            tool_turn: JsonDict = {"role": "tool", "content": content, "tool_calls": []}
            if tool_call_id:
                tool_turn["tool_call_id"] = tool_call_id
            expected_trajectory.append(tool_turn)
        else:  # system / user
            if first_assistant_seen:
                # Late system/user turn after the assistant has spoken — record in
                # the trajectory rather than leaking it into model input.
                expected_trajectory.append({"role": role, "content": content, "tool_calls": []})
            else:
                input_messages.append({"role": role, "content": content})

    if not any(message["role"] == "system" for message in input_messages):
        input_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPTS["general_tool_calling"]})

    return input_messages, {
        "expected_tool_calls": expected_tool_calls,
        "expected_assistant_content": expected_assistant_content,
        "expected_trajectory": expected_trajectory,
        "expected_final_content": last_assistant_content if not last_assistant_had_tool_calls else "",
        "expected_turn_count": len(expected_trajectory),
    }


def transform_hermes_function_calling(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    conversations = row.get("conversations") or []
    if not isinstance(conversations, list):
        conversations = []
    input_messages, expected = convert_hermes_conversations(conversations)
    has_tool_calls = bool(expected["expected_tool_calls"])
    has_assistant_text = bool(str(expected["expected_assistant_content"]).strip())
    if not has_tool_calls and not has_assistant_text:
        raise ValueError(
            "hermes row has neither expected_tool_calls nor non-empty expected_assistant_content; "
            "cannot verify"
        )
    tools = parse_json_maybe(row.get("tools"), default=[])
    if isinstance(tools, Mapping):
        tools = [dict(tools)]
    if not isinstance(tools, list):
        tools = []
    question = next((message["content"] for message in input_messages if message["role"] == "user"), "")
    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected["expected_tool_calls"] or expected["expected_assistant_content"],
        input_messages=input_messages,
        tools=tools,
        reward_config={
            "verifier": "tool_schema_and_argument_match",
            "max_score": 1.0,
            "match": ["tool_name", "json_arguments"],
            "allow_extra_assistant_text": False,
        },
        extra_env_info={
            "expected_tool_calls": expected["expected_tool_calls"],
            "expected_assistant_content": expected["expected_assistant_content"],
            "expected_trajectory": expected["expected_trajectory"],
            "expected_final_content": expected["expected_final_content"],
            "expected_turn_count": expected["expected_turn_count"],
            "category": row.get("category"),
            "subcategory": row.get("subcategory"),
            "task": row.get("task"),
        },
    )


def transform_hermes_json_mode(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    conversations = row.get("conversations") or []
    if not isinstance(conversations, list):
        conversations = []

    input_messages: list[JsonDict] = []
    expected_json: Any = None
    expected_json_text = ""
    first_assistant_seen = False
    question = ""

    for turn in conversations:
        if not isinstance(turn, Mapping):
            continue
        raw_role = str(turn.get("from") or turn.get("role") or "").strip()
        role = HERMES_ROLE_MAP.get(raw_role)
        if role is None:
            continue
        content = str(turn.get("value") or turn.get("content") or "")
        if role == "assistant":
            if first_assistant_seen:
                continue
            expected_json = parse_json_maybe(content, default=None)
            if not isinstance(expected_json, (Mapping, list)):
                raise ValueError("hermes json-mode row has no parseable JSON assistant answer")
            expected_json_text = json.dumps(expected_json, ensure_ascii=False)
            first_assistant_seen = True
        elif role in {"system", "user"} and not first_assistant_seen:
            input_messages.append({"role": role, "content": content})
            if role == "user":
                question = content

    if not any(message["role"] == "system" for message in input_messages):
        input_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]})
    if not question:
        question = next((message["content"] for message in input_messages if message["role"] == "user"), "")
    if expected_json is None:
        raise ValueError("hermes json-mode row has no assistant answer")

    schema = parse_json_maybe(row.get("schema"), default={})
    if not isinstance(schema, Mapping):
        schema = {}

    return make_record(
        spec=spec,
        row=row,
        question=question,
        expected_answer=expected_json_text,
        input_messages=input_messages,
        reward_config={
            "verifier": "json_value_exact_match",
            "max_score": 1.0,
            "match": ["json_structure", "json_values"],
            "allow_extra_text": False,
        },
        extra_env_info={
            "schema": dict(schema),
            "expected_json": expected_json,
            "category": row.get("category"),
            "subcategory": row.get("subcategory"),
        },
    )


def stable_negative_kind(row: Mapping[str, Any]) -> str:
    text = source_id(row) or str(row.get("task") or row.get("category") or "")
    return "malformed_tool_call" if sum(ord(char) for char in text) % 2 == 0 else "hallucinated_tool_output"


def tool_call_name_and_arguments(call: Mapping[str, Any]) -> tuple[Any, Any]:
    function = call.get("function")
    if isinstance(function, Mapping):
        return function.get("name"), function.get("arguments", {})
    return call.get("name"), call.get("arguments", {})


def malformed_tool_call_artifact(call: Mapping[str, Any]) -> str:
    name, arguments = tool_call_name_and_arguments(call)
    canonical = {
        "name": name,
        "arguments": arguments,
    }
    broken_json = json.dumps(canonical, ensure_ascii=False)[:-1]
    return f"<tool_call>{broken_json}</tool_call>"


def hallucinated_tool_output_artifact(call: Mapping[str, Any]) -> str:
    name, _arguments = tool_call_name_and_arguments(call)
    fake_output = {
        "tool_name": name or "unknown_tool",
        "content": "The tool completed successfully, but no valid tool call was made.",
    }
    return f"<tool_output>{json.dumps(fake_output, ensure_ascii=False)}</tool_output>"


def escape_tool_markup_for_prompt(text: str) -> str:
    """Keep invalid tool markup as quoted text, not as raw chat-template syntax."""
    return (
        text.replace("<tool_call>", "&lt;tool_call&gt;")
        .replace("</tool_call>", "&lt;/tool_call&gt;")
        .replace("<tool_output>", "&lt;tool_output&gt;")
        .replace("</tool_output>", "&lt;/tool_output&gt;")
    )


def transform_hermes_tool_call_repair_negative(row: Mapping[str, Any], spec: Mapping[str, Any]) -> JsonDict:
    base_spec = dict(spec)
    base_spec["environment"] = "general_tool_calling"
    base_spec["reward_type"] = "tool_schema_and_argument_match"
    base_record = transform_hermes_function_calling(row, base_spec)
    repair_target = copy.deepcopy(base_record["extra_env_info"].get("expected_tool_calls") or [])
    if not repair_target:
        raise ValueError("repair negative requires at least one expected tool call")

    negative_kind = stable_negative_kind(row)
    first_call = repair_target[0]
    if negative_kind == "malformed_tool_call":
        bad_artifact = malformed_tool_call_artifact(first_call)
        repair_message = "The previous tool call is malformed. I will issue the corrected call."
    else:
        bad_artifact = hallucinated_tool_output_artifact(first_call)
        repair_message = "The previous tool output was hallucinated. I will issue the valid tool call instead."
    prompt_artifact = escape_tool_markup_for_prompt(bad_artifact)

    base_prompt_parts = [
        str(message.get("content") or "").strip()
        for message in base_record["responses_create_params"].get("input", [])
        if isinstance(message, Mapping) and message.get("role") == "user" and str(message.get("content") or "").strip()
    ]
    base_prompt = "\n\n".join(base_prompt_parts)
    repair_instruction = (
        "A previous assistant produced the invalid tool-use artifact below. "
        "Identify that it is invalid and repair it using the available tool schema.\n\n"
        f"Invalid artifact:\n{prompt_artifact}"
    )
    user_content = f"{base_prompt}\n\n{repair_instruction}" if base_prompt else repair_instruction
    input_messages = [
        {"role": "system", "content": SYSTEM_PROMPTS[spec["environment"]]},
        {"role": "user", "content": user_content},
    ]
    expected_answer = {
        "repair_message": repair_message,
        "tool_calls": repair_target,
    }
    record = make_record(
        spec=spec,
        row=row,
        question=str(base_record.get("question") or ""),
        expected_answer=expected_answer,
        input_messages=input_messages,
        tools=base_record["responses_create_params"].get("tools", []),
        reward_config={
            "verifier": "negative_recognition",
            "max_score": 1.0,
            "match": ["repair_target_tool_calls"],
        },
        extra_env_info={
            "negative_kind": negative_kind,
            "invalid_artifact": bad_artifact,
            "prompt_invalid_artifact": prompt_artifact,
            "repair_target": repair_target,
            "expected_assistant_content": repair_message,
            "source_expected_trajectory": base_record["extra_env_info"].get("expected_trajectory", []),
            "category": row.get("category"),
            "subcategory": row.get("subcategory"),
            "task": row.get("task"),
        },
    )
    record["metadata"]["negative_kind"] = negative_kind
    record["metadata"]["repair_target"] = repair_target
    return record


CONVERTERS = {
    "hotpotqa_search": transform_hotpotqa_search,
    "musique_search": transform_musique_search,
    "browsecomp_grounded": transform_browsecomp_grounded,
    "mbpp_code_execution": transform_mbpp_code_execution,
    "bash_command": transform_bash_command,
    "swe_bench_patch": transform_swe_bench_patch,
    "swe_gym_lite_pivot": transform_swe_gym_lite_pivot,
    "swe_gym_openhands_trace": transform_swe_gym_openhands_trace,
    "helpsteer2_pref_pair": transform_helpsteer2_pref,
    "aya_multilingual": transform_aya_multilingual,
    "multilingual_ifeval": transform_multilingual_ifeval,
    "multilingual_humaneval": transform_multilingual_humaneval,
    "longalpaca_qa": transform_longalpaca_qa,
    "bird_sql": transform_bird_sql,
    "intercode_nl2bash": transform_intercode_nl2bash,
    "terminalbench_v2": transform_terminalbench_v2,
    "nemotron_safety_reasoning": transform_nemotron_safety_reasoning,
    "mathcode_instruct": transform_mathcode_instruct,
    "hermes_function_calling": transform_hermes_function_calling,
    "hermes_json_mode": transform_hermes_json_mode,
    "hermes_tool_call_repair_negative": transform_hermes_tool_call_repair_negative,
    "gsm8k_numeric_reasoning": transform_gsm8k_numeric_reasoning,
    "numinamath_competition": transform_numinamath_competition,
    "lean_proof_stub": transform_lean_proof_stub,
}


def iter_hf_rows(
    spec: Mapping[str, Any],
    *,
    streaming: bool,
    split: str | None = None,
    config: str | None = MISSING_CONFIG,
) -> Iterator[Mapping[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install the `datasets` package or run inside /work-agents/.venv") from exc

    use_split = split if split is not None else spec["hf_split"]
    use_config = spec.get("hf_config") if config is MISSING_CONFIG else config
    kwargs: JsonDict = {
        "split": use_split,
        "revision": spec["hf_revision"],
        "streaming": streaming,
    }
    if spec.get("trust_remote_code"):
        # Required for HF datasets that ship a custom loader script (e.g. hotpotqa);
        # `datasets>=2.16` refuses to run those without an explicit opt-in.
        kwargs["trust_remote_code"] = True
    if use_config:
        dataset = load_dataset(spec["hf_dataset"], use_config, **kwargs)
    else:
        dataset = load_dataset(spec["hf_dataset"], **kwargs)
    yield from dataset


def desired_counts(spec: Mapping[str, Any], args: argparse.Namespace) -> tuple[int | None, int | None]:
    if getattr(args, "uncapped", False):
        return None, None
    train_rows = args.max_train_per_dataset
    val_rows = args.max_val_per_dataset
    if train_rows is None:
        train_rows = int(spec["default_train_rows"])
    if val_rows is None:
        val_rows = int(spec["default_val_rows"])
    if train_rows < 0 or val_rows < 0:
        raise ValueError("row counts must be non-negative")
    return train_rows, val_rows


def validate_registries(data_registry: Mapping[str, Any], env_registry: Mapping[str, Any]) -> None:
    env_ids = {env["id"] for env in env_registry.get("environments", [])}
    for spec in data_registry.get("datasets", []):
        if spec["environment"] not in env_ids:
            raise ValueError(f"{spec['id']} references unknown environment {spec['environment']}")
        if spec["converter"] not in CONVERTERS:
            raise ValueError(f"{spec['id']} references unknown converter {spec['converter']}")
        contamination_against = spec.get("contamination_against")
        if not isinstance(contamination_against, list):
            raise ValueError(f"{spec['id']} contamination_against must be a list")
        if any(not isinstance(item, str) or not item.strip() for item in contamination_against):
            raise ValueError(f"{spec['id']} contamination_against entries must be non-empty strings")
        if spec.get("milestone", data_registry.get("milestone")) != data_registry.get("milestone"):
            raise ValueError(f"{spec['id']} milestone must match registry milestone")


def selected_specs(data_registry: Mapping[str, Any], dataset_ids: Sequence[str] | None) -> list[JsonDict]:
    specs = [dict(spec) for spec in data_registry.get("datasets", [])]
    for spec in specs:
        spec.setdefault("milestone", data_registry["milestone"])
    if not dataset_ids:
        return specs
    wanted = set(dataset_ids)
    selected = [spec for spec in specs if spec["id"] in wanted]
    missing = sorted(wanted - {spec["id"] for spec in selected})
    if missing:
        raise ValueError(f"unknown dataset ids: {', '.join(missing)}")
    return selected


def target_files(output_dir: Path, specs: Sequence[Mapping[str, Any]]) -> list[Path]:
    paths = []
    for env_id in sorted({spec["environment"] for spec in specs}):
        paths.append(output_dir / env_id / "train-split.jsonl")
        paths.append(output_dir / env_id / "val-split.jsonl")
    paths.extend(
        [
            output_dir / "manifest.json",
            output_dir / "dataset_registry.resolved.json",
            output_dir / "environment_registry.resolved.json",
            output_dir / "report.md",
        ]
    )
    return paths


def check_overwrite(paths: Sequence[Path], overwrite: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"target files already exist; pass --overwrite to replace them:\n{formatted}")


def write_jsonl_line(path: Path, record: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def reset_target_files(paths: Sequence[Path]) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".jsonl":
            path.write_text("", encoding="utf-8")


def stale_split_files(output_dir: Path, active_paths: Sequence[Path]) -> list[Path]:
    if not output_dir.exists():
        return []
    active = {path.resolve() for path in active_paths if path.name.endswith("-split.jsonl")}
    return sorted(
        path
        for path in output_dir.glob("*/*-split.jsonl")
        if path.resolve() not in active
    )


def cleanup_stale_split_files(output_dir: Path, active_paths: Sequence[Path]) -> list[Path]:
    stale_paths = stale_split_files(output_dir, active_paths)
    for path in stale_paths:
        path.unlink()
    return stale_paths


def prepare_assets(args: argparse.Namespace) -> JsonDict:
    if args.uncapped and (args.max_train_per_dataset is not None or args.max_val_per_dataset is not None):
        raise ValueError("--uncapped cannot be combined with --max-train-per-dataset or --max-val-per-dataset")

    data_registry = load_yaml(args.data_registry)
    env_registry = load_yaml(args.environment_registry)
    specs = selected_specs(data_registry, args.dataset_id)
    validate_registries(data_registry, env_registry)

    output_dir = args.output_dir
    paths = target_files(output_dir, specs)
    stale_paths = stale_split_files(output_dir, paths)
    check_overwrite([*paths, *stale_paths], args.overwrite)
    if args.overwrite:
        cleanup_stale_split_files(output_dir, paths)
    reset_target_files(paths)

    manifest: JsonDict = {
        "schema_version": 1,
        "milestone": data_registry["milestone"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "data_registry": str(args.data_registry),
        "environment_registry": str(args.environment_registry),
        "requested_rows": {
            "uncapped": args.uncapped,
            "max_train_per_dataset": args.max_train_per_dataset,
            "max_val_per_dataset": args.max_val_per_dataset,
        },
        "datasets": [],
        "files": [],
        "errors": [],
        "warnings": [],
    }
    file_counts: dict[tuple[str, str], int] = defaultdict(int)

    for spec in specs:
        train_target, val_target = desired_counts(spec, args)
        split_counts = {"train": 0, "val": 0}
        converter = CONVERTERS[spec["converter"]]
        val_split_name = spec.get("hf_val_split")
        if val_split_name:
            val_config = spec.get("hf_val_config", spec.get("hf_config"))
            sources = [
                ("train", spec["hf_split"], spec.get("hf_config"), train_target),
                ("val", val_split_name, val_config, val_target),
            ]
        else:
            manifest["warnings"].append(
                {
                    "dataset": spec["id"],
                    "warning": (
                        f"no hf_val_split configured; val rows will be a sequential continuation of "
                        f"hf_split={spec['hf_split']} and are NOT a true holdout"
                    ),
                }
            )
            shared_target = None if train_target is None else train_target + (val_target or 0)
            sources = [("shared", spec["hf_split"], spec.get("hf_config"), shared_target)]

        for source_mode, hf_split, hf_config, source_target in sources:
            row_iter: Iterable[Mapping[str, Any]] = iter_hf_rows(
                spec,
                streaming=not args.non_streaming,
                split=hf_split,
                config=hf_config,
            )
            if spec["converter"] == "helpsteer2_pref_pair":
                row_iter = iter_helpsteer2_preference_pairs(row_iter)
            for raw_index, row in enumerate(row_iter):
                if source_mode == "shared":
                    if train_target is not None and split_counts["train"] >= train_target and (
                        val_target is None or split_counts["val"] >= val_target
                    ):
                        break
                else:
                    if source_target is not None and split_counts[source_mode] >= source_target:
                        break
                try:
                    record = converter(row, spec)
                except Exception as exc:  # noqa: BLE001 - keep data-prep running and report bad rows.
                    manifest["errors"].append(
                        {
                            "dataset": spec["id"],
                            "hf_split": hf_split,
                            "source_row_index": raw_index,
                            "error": str(exc),
                        }
                    )
                    continue

                if source_mode == "shared":
                    split = "train" if train_target is None or split_counts["train"] < train_target else "val"
                else:
                    split = source_mode
                split_counts[split] += 1
                record["metadata"]["source_row_index"] = raw_index
                record["metadata"]["source_hf_split"] = hf_split
                record["metadata"]["prepared_split"] = split
                record["metadata"]["prepared_by"] = "prepare_m0_assets.py"
                path = output_dir / spec["environment"] / f"{split}-split.jsonl"
                write_jsonl_line(path, record)
                file_counts[(spec["environment"], split)] += 1

        manifest["datasets"].append(
            {
                "id": spec["id"],
                "environment": spec["environment"],
                "domain": spec["domain"],
                "hf_dataset": spec["hf_dataset"],
                "hf_config": spec.get("hf_config"),
                "hf_split": spec["hf_split"],
                "hf_val_split": spec.get("hf_val_split"),
                "hf_revision": spec["hf_revision"],
                "source_url": spec["source_url"],
                "license": spec["license"],
                "contamination_against": spec["contamination_against"],
                "use_stage": spec["use_stage"],
                "train_rows": split_counts["train"],
                "val_rows": split_counts["val"],
                "val_holdout": bool(val_split_name),
            }
        )
        train_short = train_target is not None and split_counts["train"] < train_target
        val_short = val_target is not None and split_counts["val"] < val_target
        if train_short or val_short:
            manifest["errors"].append(
                {
                    "dataset": spec["id"],
                    "error": (
                        f"requested {train_target}/{val_target} train/val rows, "
                        f"prepared {split_counts['train']}/{split_counts['val']}"
                    ),
                }
            )

    for env_id, split in sorted(file_counts):
        manifest["files"].append(
            {
                "environment": env_id,
                "split": split,
                "path": str(output_dir / env_id / f"{split}-split.jsonl"),
                "rows": file_counts[(env_id, split)],
            }
        )

    # task021 Session 2: cross-stage lineage block. M0 is the chain root —
    # one HF source per registered dataset shows up as a `hf_dataset` input,
    # and every JSONL split file becomes a `m0_jsonl_split` output. Future
    # M1 / RL prep stages declare this manifest as a `manifest` input.
    lineage_inputs = [
        LineageInput(
            kind="hf_dataset",
            ref=spec["hf_dataset"],
            config=spec.get("hf_config"),
            split=spec["hf_split"],
            revision=spec["hf_revision"],
            notes=spec.get("source_url"),
        )
        for spec in specs
    ]
    lineage_outputs = [
        LineageOutput(
            kind="m0_jsonl_split",
            ref=str(Path(file_info["path"]).relative_to(output_dir)),
            rows=file_info["rows"],
            notes=f"environment={file_info['environment']} split={file_info['split']}",
        )
        for file_info in manifest["files"]
    ]
    lineage_record = make_lineage_record(
        stage=f"{manifest['milestone']} data_env_foundation",
        produced_by="prepare_m0_assets.py",
        artifact_type=RAW_DATA_ARTIFACT,
        artifact_name=output_dir.name or "m0_data_env_foundation",
        inputs=lineage_inputs,
        outputs=lineage_outputs,
    )
    manifest["lineage"] = lineage_record.to_jsonable()

    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "dataset_registry.resolved.json", data_registry)
    write_json(output_dir / "environment_registry.resolved.json", env_registry)
    write_report(output_dir / "report.md", manifest)
    return manifest


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_report(path: Path, manifest: Mapping[str, Any]) -> None:
    lines = [
        "# M0 Data and Environment Foundation Report",
        "",
        f"- Generated: `{manifest['created_at_utc']}`",
        f"- Output directory: `{manifest['output_dir']}`",
        f"- Milestone: `{manifest['milestone']}`",
        "",
        "## Dataset Outputs",
        "",
        "| Dataset | Environment | Train | Val | License | Use stage |",
        "|---|---|---:|---:|---|---|",
    ]
    for dataset in manifest["datasets"]:
        use_stage = "<br>".join(dataset["use_stage"])
        lines.append(
            f"| {dataset['id']} | {dataset['environment']} | {dataset['train_rows']} | "
            f"{dataset['val_rows']} | {dataset['license']} | {use_stage} |"
        )
    lines.extend(["", "## Files", ""])
    for file_info in manifest["files"]:
        lines.append(
            "- `{environment}/{split}-split.jsonl`: {rows} rows".format(
                **file_info,
            )
        )
    if manifest["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in manifest["errors"]:
            lines.append(f"- `{error.get('dataset', 'unknown')}`: {error['error']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--data-registry", type=Path, default=DATA_REGISTRY_PATH)
    parser.add_argument("--environment-registry", type=Path, default=ENV_REGISTRY_PATH)
    parser.add_argument("--dataset-id", action="append", help="Limit to one dataset id. May be passed multiple times.")
    parser.add_argument("--max-train-per-dataset", type=int, default=None)
    parser.add_argument("--max-val-per-dataset", type=int, default=None)
    parser.add_argument(
        "--uncapped",
        action="store_true",
        help=(
            "Exhaust each selected source split instead of using registry default "
            "row counts. Datasets without a native validation split assign all "
            "rows to train and emit the existing no-holdout warning."
        ),
    )
    parser.add_argument("--non-streaming", action="store_true", help="Use cached HF datasets instead of streaming.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite target files generated by this script.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = prepare_assets(args)
    except Exception as exc:  # noqa: BLE001 - CLI should render a concise error.
        print(f"prepare_m0_assets.py: error: {exc}", file=sys.stderr)
        return 1
    # task069 Session 2: auto-publish lineage to W&B (no-op without active run).
    try:
        from nemotron.recipes.super3.milestones.lineage_publisher import (
            maybe_publish_lineage_from_manifest,
        )
        maybe_publish_lineage_from_manifest(Path(manifest["output_dir"]) / "manifest.json")
    except Exception:  # noqa: BLE001
        pass
    print(json.dumps({"output_dir": manifest["output_dir"], "datasets": manifest["datasets"]}, indent=2))
    return 0 if not manifest["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
