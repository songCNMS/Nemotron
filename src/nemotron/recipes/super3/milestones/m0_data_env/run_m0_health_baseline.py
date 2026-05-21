#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml>=6.0"]
# ///

"""Run M0 environment health checks and offline baseline reward smoke tests."""

from __future__ import annotations

import argparse
import json
import re
import string
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
        ENV_REGISTRY_PATH,
        load_yaml,
        normalize_numeric_answer,
        parse_json_maybe,
    )
except ModuleNotFoundError:
    from prepare_m0_assets import ENV_REGISTRY_PATH, load_yaml, normalize_numeric_answer, parse_json_maybe

DEFAULT_INPUT_DIR = Path("data/super3/milestones/m0_data_env_foundation")
DEFAULT_OUTPUT_SUBDIR = "health_baseline"
MISSING = object()
JsonDict = dict[str, Any]

TEXT_ARTICLES_RE = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
NUMBER_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?(?:/\d[\d,]*)?")


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


def get_path(value: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return MISSING
        current = current[part]
    return current


def normalize_text_answer(value: Any) -> str:
    text = str(value).lower()
    text = "".join(" " if char in string.punctuation else char for char in text)
    text = TEXT_ARTICLES_RE.sub(" ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_multilingual_text(value: Any) -> str:
    """Multilingual-aware text normalizer (task057 Session 1).

    Differs from :func:`normalize_text_answer`:

    - ``str.casefold()`` instead of ``.lower()`` so language-specific
      case folding works (German ß → ss, Turkish dotless İ → i, etc.)
    - Unicode NFC normalization so composed vs decomposed code points
      compare equal (é written as one code point vs e + combining
      accent)
    - **Does NOT strip punctuation** — some languages (notably Chinese
      / Japanese) rely on punctuation for meaning, and articles
      ("the" / "a" / "an") are English-only
    - Whitespace collapsed to single space, leading / trailing
      stripped — same as the English path
    """
    import unicodedata
    text = unicodedata.normalize("NFC", str(value)).casefold()
    return WHITESPACE_RE.sub(" ", text).strip()


def score_multilingual_text(candidate: Any, expected: Any) -> float:
    """Exact-or-contains scoring on Unicode-normalised text."""
    normalized_candidate = normalize_multilingual_text(candidate)
    normalized_expected = normalize_multilingual_text(expected)
    if not normalized_expected:
        return 0.0
    if normalized_candidate == normalized_expected:
        return 1.0
    return 1.0 if normalized_expected in normalized_candidate else 0.0


def normalize_numeric_candidate(value: Any) -> str:
    text = normalize_numeric_answer(value)
    matches = NUMBER_RE.findall(text)
    if matches:
        return matches[-1].replace(",", "").strip()
    return text.replace(",", "").strip()


def canonical_tool_call(call: Any) -> JsonDict:
    if isinstance(call, str):
        call = parse_json_maybe(call, default={})
    if not isinstance(call, Mapping):
        return {"name": None, "arguments": None}
    function = call.get("function")
    if isinstance(function, Mapping):
        name = function.get("name")
        arguments = function.get("arguments", {})
    else:
        name = call.get("name")
        arguments = call.get("arguments", {})
    if isinstance(arguments, str):
        arguments = parse_json_maybe(arguments, default=arguments)
    return {"name": name, "arguments": arguments}


def score_text(candidate: Any, expected: Any) -> float:
    normalized_candidate = normalize_text_answer(candidate)
    normalized_expected = normalize_text_answer(expected)
    if not normalized_expected:
        # An empty expected answer is a data-quality problem, not a wiring success.
        # Refuse to silently call this a pass.
        return 0.0
    if normalized_candidate == normalized_expected:
        return 1.0
    return 1.0 if normalized_expected in normalized_candidate else 0.0


def score_numeric(candidate: Any, expected: Any) -> float:
    return 1.0 if normalize_numeric_candidate(candidate) == normalize_numeric_answer(expected) else 0.0


def parse_json_strict(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return MISSING
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return MISSING
    if isinstance(value, (Mapping, list)):
        return value
    return MISSING


def score_json_value(candidate: Any, expected: Any) -> float:
    parsed_candidate = parse_json_strict(candidate)
    parsed_expected = parse_json_strict(expected)
    if parsed_candidate is MISSING or parsed_expected is MISSING:
        return 0.0
    return 1.0 if parsed_candidate == parsed_expected else 0.0


def normalize_command_text(value: Any) -> str:
    """Normalize a shell command string for substring-match scoring.

    Steps:
      1. Extract fenced code block content if present (operator-quoted)
      2. Collapse runs of whitespace to single space
      3. Normalize quote style — map double quotes to single quotes
         (functionally equivalent at the shell layer when no $var
         expansion is involved; tier-2 intercode-nl2bash mixes quote
         styles, this brings them onto a canonical form for compare)
      4. Strip leading + trailing whitespace
    """
    text = str(value).strip()
    blocks = re.findall(r"```(?:bash|sh|shell)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if blocks:
        text = blocks[-1].strip()
    text = WHITESPACE_RE.sub(" ", text).strip()
    # task057 Session 4: quote-style normalization for tier-2 robustness.
    # `find -name "*.txt"` and `find -name '*.txt'` are shell-equivalent
    # outside $var expansion; canonicalize to single quotes so the
    # oracle baseline doesn't false-negative on stylistic differences.
    text = text.replace('"', "'")
    return text


def score_command(candidate: Any, expected: Any) -> float:
    normalized_candidate = normalize_command_text(candidate)
    normalized_expected = normalize_command_text(expected)
    if not normalized_expected:
        return 0.0
    if normalized_candidate == normalized_expected:
        return 1.0
    return 1.0 if normalized_expected in normalized_candidate else 0.0


def normalize_patch_text(value: Any) -> str:
    return "\n".join(line.rstrip() for line in str(value).strip().splitlines()).strip()


def score_patch(candidate: Any, expected: Any) -> float:
    normalized_candidate = normalize_patch_text(candidate)
    normalized_expected = normalize_patch_text(expected)
    if not normalized_expected:
        return 0.0
    return 1.0 if normalized_candidate == normalized_expected else 0.0


def extract_tool_call_list(value: Any) -> list[Any]:
    parsed = parse_json_maybe(value, default=value)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, Mapping):
        for key in ("tool_calls", "repair_target", "expected_tool_calls"):
            calls = parsed.get(key)
            if isinstance(calls, list):
                return calls
    return []


def score_negative_recognition(candidate: Any, expected: Any, record: Mapping[str, Any]) -> float:
    expected_calls = extract_tool_call_list(record.get("extra_env_info", {}).get("repair_target"))
    if not expected_calls:
        expected_calls = extract_tool_call_list(expected)
    candidate_calls = extract_tool_call_list(candidate)
    if not expected_calls or not candidate_calls or len(expected_calls) != len(candidate_calls):
        return 0.0
    for candidate_call, expected_call in zip(candidate_calls, expected_calls):
        if canonical_tool_call(candidate_call) != canonical_tool_call(expected_call):
            return 0.0
    return 1.0


def score_tool_call(candidate: Any, expected: Any, record: Mapping[str, Any]) -> float:
    if isinstance(candidate, str):
        parsed = parse_json_maybe(candidate, default=candidate)
        candidate = parsed

    expected_content = record.get("extra_env_info", {}).get("expected_assistant_content", "")
    if isinstance(expected, str):
        parsed_expected = parse_json_maybe(expected, default=expected)
        expected = parsed_expected

    if isinstance(expected, list):
        if not expected and expected_content:
            return score_text(candidate, expected_content)
        if not expected and not expected_content:
            # No expected tool calls and no expected assistant content — cannot verify.
            return 0.0
        if not isinstance(candidate, list):
            return 0.0
        if len(candidate) != len(expected):
            return 0.0
        for candidate_call, expected_call in zip(candidate, expected):
            if canonical_tool_call(candidate_call) != canonical_tool_call(expected_call):
                return 0.0
        return 1.0

    return score_text(candidate, expected_content or expected)


def extract_code(candidate: Any) -> str:
    code = str(candidate)
    if "```" not in code:
        return code
    blocks = re.findall(r"```(?:python)?\s*(.*?)```", code, flags=re.DOTALL | re.IGNORECASE)
    return blocks[-1].strip() if blocks else code


def run_python_unit_tests(
    candidate: Any,
    record: Mapping[str, Any],
    timeout_s: int,
    *,
    container_runtime: str | None = None,
    rollout_policy: str = "oracle",
) -> tuple[float, JsonDict]:
    """Run python unit tests against *candidate*.

    When ``container_runtime`` is None (the default), candidate code
    runs in-process via ``sys.executable -I`` — unchanged from the M0
    oracle baseline path. Safe for the oracle policy (candidate ==
    expected gold patch).

    When ``container_runtime`` is one of ``docker`` / ``podman`` /
    ``singularity``, candidate code runs inside the env's registered
    sandbox image via ``ContainerSandbox`` (task021 Session 3 +
    Session 5). This is the path adversarial M1+ RLVR rollouts should
    take. ``record["environment"]`` is used to look up the image via
    ``sandbox_image_registry.yaml``; envs without a registered image
    fall back to in-process execution with an explicit
    ``container_fallback`` flag in the diagnostics.

    ``rollout_policy`` (task021 Session 6 guard rail) distinguishes
    oracle from adversarial candidates. When set to ``"adversarial"``
    AND ``container_runtime is None``, this function raises
    ``RuntimeError`` rather than silently running untrusted code on
    the host. Future M1+ RLVR rollouts that forget the container
    runtime hit this guard immediately. ``"oracle"`` (default) keeps
    today's in-process behavior unchanged.
    """
    from nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim import (
        KNOWN_ROLLOUT_POLICIES,
        ROLLOUT_POLICY_ADVERSARIAL,
    )

    if rollout_policy not in KNOWN_ROLLOUT_POLICIES:
        raise ValueError(
            f"unknown rollout_policy {rollout_policy!r}; "
            f"known: {sorted(KNOWN_ROLLOUT_POLICIES)}"
        )
    if rollout_policy == ROLLOUT_POLICY_ADVERSARIAL and container_runtime is None:
        # Guard rail: adversarial candidates must run inside a
        # container. The shim's in-process fallback for unregistered
        # envs would silently run untrusted code on the host, which is
        # the failure mode this guard exists to prevent.
        raise RuntimeError(
            "adversarial rollout policy requires an explicit "
            "container_runtime (docker / podman / singularity). "
            "Pass `container_runtime='docker'` (or override via the "
            "CLI flag `--container-runtime`) before scoring untrusted "
            "candidates."
        )
    extra = record.get("extra_env_info", {})
    tests = extra.get("test_list") or []
    imports = extra.get("test_imports") or []
    if isinstance(imports, str):
        imports = [imports] if imports.strip() else []
    if not tests:
        return 0.0, {"error": "missing tests"}

    code = extract_code(candidate)
    script = "\n\n".join([*imports, code, *tests])
    with tempfile.TemporaryDirectory(prefix="m0-code-smoke-") as tmpdir:
        script_path = Path(tmpdir) / "candidate_test.py"
        script_path.write_text(script, encoding="utf-8")
        sandbox = None
        if container_runtime is not None:
            # Lazy import keeps the runtime_shim module out of the
            # health-baseline import graph when no container runtime
            # is requested (sandbox CI doesn't have docker).
            from nemotron.recipes.super3.milestones.sandbox_containers.runtime_shim import (
                sandbox_for_env,
            )

            sandbox = sandbox_for_env(
                record.get("environment", ""),
                runtime=container_runtime,
            )

        try:
            if sandbox is None:
                result = subprocess.run(
                    [sys.executable, "-I", str(script_path)],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=timeout_s,
                    check=False,
                )
            else:
                result = sandbox.run(
                    host_workdir=Path(tmpdir),
                    command=["python", "-I", f"{sandbox.workdir_mount}/{script_path.name}"],
                    timeout_s=timeout_s,
                )
        except subprocess.TimeoutExpired as exc:
            return 0.0, {
                "error": "timeout",
                "timeout_s": timeout_s,
                "stdout": exc.stdout,
                "stderr": exc.stderr,
                "container_runtime": container_runtime,
            }
    score = 1.0 if result.returncode == 0 else 0.0
    diagnostics: JsonDict = {
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-1000:],
        "stderr_tail": result.stderr[-1000:],
    }
    if container_runtime is not None:
        diagnostics["container_runtime"] = container_runtime
        # When an env has no registered image, the shim returns None
        # and we fall back to in-process. Surface that in diagnostics
        # so coverage walks see the gap.
        diagnostics["container_fallback"] = sandbox is None
    if rollout_policy != "oracle":
        # Default oracle policy keeps diagnostics shape unchanged;
        # adversarial / other policies leave a breadcrumb so audits can
        # confirm the guard rail actually fired.
        diagnostics["rollout_policy"] = rollout_policy
    return score, diagnostics


def score_record(
    candidate: Any,
    record: Mapping[str, Any],
    *,
    run_code: bool = True,
    container_runtime: str | None = None,
    rollout_policy: str = "oracle",
) -> tuple[float | None, JsonDict]:
    """Score a row and emit per-verifier telemetry alongside the diagnostic dict.

    Telemetry names align with the `telemetry:` list each env declares in
    `environment_registry.yaml`; the M0 baseline is the first emitter
    (task021 Session 1). The shape stays compatible — telemetry rides
    inside the returned diagnostic dict — so existing callers and
    fixtures keep working unchanged.

    The scorer call itself is timed (`latency_ms`); the verifier-specific
    code below adds bool / numeric signals that are derivable at oracle
    time. Values that need a real model rollout (`overlong`,
    `malformed_thinking`, `crash`, etc.) are intentionally absent here
    and will be filled in by the future stage2_rl runtime emitter.
    """
    verifier = record.get("reward_config", {}).get("verifier")
    expected = record.get("expected_answer")
    if verifier == "python_unit_tests" and not run_code:
        return None, {"skipped": "code execution disabled"}

    t0 = time.perf_counter()
    score: float | None
    diagnostics: JsonDict
    if verifier == "normalized_exact_or_contains":
        score = score_text(candidate, expected)
        diagnostics = {
            "normalized_answer": normalize_text_answer(candidate),
        }
    elif verifier == "multilingual_exact_or_contains":
        # task057 Session 1 — Aya / multilingual envs. Unicode-aware
        # normalization (NFC + casefold; keeps punctuation since CJK
        # depends on it).
        score = score_multilingual_text(candidate, expected)
        normalized_candidate = normalize_multilingual_text(candidate)
        normalized_expected = normalize_multilingual_text(expected)
        diagnostics = {
            "normalized_answer": normalized_candidate,
            "exact_match": bool(
                normalized_expected and normalized_candidate == normalized_expected
            ),
            "contains_match": bool(
                normalized_expected and normalized_expected in normalized_candidate
            ),
        }
    elif verifier == "long_context_qa_stub":
        # task057 Session 2 — long_context_qa_smoke env (LongAlpaca-12k
        # source). M0 oracle baseline stub: delegates to the same
        # contains-match logic as `normalized_exact_or_contains`. The
        # "stub" suffix signals that a richer verifier (span-aware,
        # judge-graded) is M2 task028 / task037 territory; today's
        # M0 baseline just needs the oracle to pass through.
        score = score_text(candidate, expected)
        diagnostics = {
            "normalized_answer": normalize_text_answer(candidate),
            "contains_match": bool(score == 1.0),
        }
    elif verifier == "sql_execution_match":
        # task057 Session 3 — sql_text_to_query env (BIRD-SQL source).
        # M0 records without local DB context keep the normalized SQL
        # string-match fallback. M2 task024 Session 1 adds an opt-in
        # local SQLite scaffold when extra_env_info.sql_execution carries
        # schema + fixtures.
        from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
            normalize_sql,
            score_sql_execution_match_with_diagnostics,
        )
        score, diagnostics = score_sql_execution_match_with_diagnostics(
            candidate,
            expected,
            record.get("extra_env_info", {}),
        )
        diagnostics.setdefault("normalized_sql", normalize_sql(candidate))
        diagnostics["sql_match"] = bool(score == 1.0)
    elif verifier == "math_with_tools_match":
        # task057 Session 6 — math_with_tools env (MathCodeInstruct
        # source). M0 oracle stub: extract the candidate's LAST
        # `\boxed{...}` block, normalize (lowercase + whitespace-
        # collapsed + strip_punctuation per `score_text`), and contains-
        # match against the gold boxed answer. If no `\boxed{...}` is
        # present in the candidate, fall back to whole-candidate
        # contains-match (so oracle still passes for trailing-token
        # solutions that drop the box). Real Python-execution + math-
        # judge scoring is M1 task011 territory; the "_match" suffix
        # signals this M0 stub intent.
        from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
            count_python_code_blocks,
            extract_boxed_answer,
        )
        candidate_str = str(candidate or "")
        candidate_boxed = extract_boxed_answer(candidate_str)
        if candidate_boxed:
            score = score_text(candidate_boxed, expected)
            boxed_answer_extracted = True
        else:
            score = score_text(candidate_str, expected)
            boxed_answer_extracted = False
        diagnostics = {
            "normalized_answer": normalize_text_answer(
                candidate_boxed if candidate_boxed else candidate_str
            ),
            "boxed_answer_extracted": boxed_answer_extracted,
            "has_code_block_in_candidate": count_python_code_blocks(candidate_str) > 0,
            "malformed_final_answer": not boxed_answer_extracted,
        }
    elif verifier == "safety_judge_stub":
        # task057 Session 5 — safety_reasoning_smoke env. M0 oracle
        # baseline uses case-insensitive contains-match on the
        # canonical verdict (allow / block / escalate). Real judge-
        # model scoring is M2 task029 (safety) territory; the
        # "judge_stub" name signals the future verifier intent.
        norm_candidate = str(candidate or "").lower()
        norm_expected = str(expected or "").strip().lower()
        if not norm_expected:
            score = 0.0
        elif norm_expected in norm_candidate:
            score = 1.0
        else:
            score = 0.0
        diagnostics = {
            "expected_verdict": norm_expected,
            "verdict_match": bool(score == 1.0),
        }
    elif verifier == "normalized_numeric_exact_match":
        normalized_candidate = normalize_numeric_candidate(candidate)
        score = score_numeric(candidate, expected)
        diagnostics = {
            "normalized_answer": normalized_candidate,
            # No digit-bearing token in the candidate → the answer wasn't
            # parseable as a number. Trivially False at oracle time
            # (oracle always carries the cleaned numeric).
            "malformed_final_answer": not bool(NUMBER_RE.search(str(candidate))),
        }
    elif verifier == "json_value_exact_match":
        parsed = parse_json_strict(candidate)
        score = score_json_value(candidate, expected)
        diagnostics = {
            "json_parse_error": parsed is MISSING,
            "exact_value_match": bool(score == 1.0),
        }
    elif verifier == "command_substring_match":
        score = score_command(candidate, expected)
        diagnostics = {"command_match": bool(score == 1.0)}
    elif verifier == "patch_diff_match":
        normalized_candidate = normalize_patch_text(candidate)
        score = score_patch(candidate, expected)
        diagnostics = {
            "patch_match": bool(score == 1.0),
            # A "diff" without the `diff --git` / `---`/`+++` headers is
            # malformed. Trivially False at oracle time.
            "malformed_diff": (
                bool(normalized_candidate)
                and "diff --git" not in normalized_candidate
                and "---" not in normalized_candidate
            ),
        }
    elif verifier == "negative_recognition":
        score = score_negative_recognition(candidate, expected, record)
        diagnostics = {
            "repair_target_match": bool(score == 1.0),
            # Oracle replays the repair target → never invalid here.
            "invalid_tool_call": False,
        }
    elif verifier == "tool_schema_and_argument_match":
        score = score_tool_call(candidate, expected, record)
        # The verifier returns 0.0 either when the candidate isn't a valid
        # tool-call structure OR when args don't match. Distinguish the
        # two so the dashboard can separate format-drift from semantic
        # disagreement.
        candidate_calls = candidate
        if isinstance(candidate, str):
            candidate_calls = parse_json_maybe(candidate, default=candidate)
        diagnostics = {
            "invalid_tool_call": not isinstance(candidate_calls, list),
            "argument_match": bool(score == 1.0),
        }
    elif verifier == "python_unit_tests":
        timeout_s = int(record.get("reward_config", {}).get("timeout_s", 30))
        score, raw = run_python_unit_tests(
            candidate,
            record,
            timeout_s=timeout_s,
            container_runtime=container_runtime,
            rollout_policy=rollout_policy,
        )
        diagnostics = dict(raw)
        diagnostics.setdefault("timeout", diagnostics.get("error") == "timeout")
        # `returncode != 0` covers both syntax errors and assertion failures
        # in the candidate solution. Treat `timeout` separately for clarity.
        rc = diagnostics.get("returncode")
        diagnostics.setdefault(
            "runtime_error",
            bool(rc is not None and rc != 0) and not diagnostics["timeout"],
        )
    elif verifier == "lean_proof_stub":
        # M0 smoke verifier — non-empty proof → 1.0, empty → 0.0. Real
        # Lean compiler verification (run against mathlib4 + check
        # `#print axioms`) is task017 / task049 territory and needs the
        # Lean toolchain inside a sandbox container.
        candidate_str = str(candidate).strip() if candidate is not None else ""
        score = 1.0 if candidate_str else 0.0
        diagnostics = {
            "nonempty_proof": bool(candidate_str),
            "proof_length": len(candidate_str),
            "language": str(
                record.get("extra_env_info", {}).get("language", "lean4")
            ),
        }
    else:
        return 0.0, {"error": f"unsupported verifier: {verifier}"}

    diagnostics["latency_ms"] = (time.perf_counter() - t0) * 1000.0
    return score, diagnostics


def oracle_candidate(record: Mapping[str, Any]) -> Any:
    verifier = record.get("reward_config", {}).get("verifier")
    if verifier == "tool_schema_and_argument_match":
        expected = record.get("expected_answer")
        if expected:
            return expected
        return record.get("extra_env_info", {}).get("expected_assistant_content", "")
    return record.get("expected_answer", "")


def candidates_for_policy(record: Mapping[str, Any], policy: str) -> list[Any]:
    if policy == "oracle":
        return [oracle_candidate(record)]
    if policy == "empty":
        return [""]
    if policy == "oracle_then_empty":
        return [oracle_candidate(record), ""]
    raise ValueError(f"unknown baseline policy: {policy}")


def score_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    policy: str,
    best_k: int,
    run_code: bool,
    container_runtime: str | None = None,
    rollout_policy: str = "oracle",
) -> list[JsonDict]:
    """Score each row once and return raw per-row results.

    Pulled out of `evaluate_policy` so that aggregate metrics can be derived from
    the same per-row scores as the split metrics, instead of re-invoking the
    verifier (and, for python_unit_tests, re-spawning subprocesses).

    ``container_runtime`` (task021 Session 5) plumbs the container
    isolation choice down to ``run_python_unit_tests``. None keeps the
    pre-task021-Session-5 in-process behavior.
    """
    out: list[JsonDict] = []
    for index, record in enumerate(rows):
        candidates = candidates_for_policy(record, policy)
        scores: list[float] = []
        diagnostics: list[JsonDict] = []
        for candidate in candidates[: max(best_k, 1)]:
            score, detail = score_record(
                candidate,
                record,
                run_code=run_code,
                container_runtime=container_runtime,
                rollout_policy=rollout_policy,
            )
            diagnostics.append(detail)
            if score is None:
                continue
            scores.append(score)
        out.append(
            {
                "row_index": index,
                "scores": scores,
                "diagnostics": diagnostics,
                "metadata": record.get("metadata", {}),
                "verifier": record.get("reward_config", {}).get("verifier"),
            }
        )
    return out


def aggregate_scored_rows(
    scored: Sequence[Mapping[str, Any]],
    *,
    policy: str,
    best_k: int,
) -> JsonDict:
    pass_at_1 = 0
    best_at_k = 0
    total_score_at_1 = 0.0
    total_best_score_at_k = 0.0
    errors: list[JsonDict] = []
    skipped_rows = 0
    scored_rows = 0
    threshold = 1.0

    per_row_telemetry: list[JsonDict] = []
    for entry in scored:
        scores = entry["scores"]
        if not scores:
            skipped_rows += 1
            continue
        scored_rows += 1
        first_score = scores[0]
        best_score = max(scores[:best_k])
        pass_at_1 += int(first_score >= threshold)
        best_at_k += int(best_score >= threshold)
        total_score_at_1 += first_score
        total_best_score_at_k += best_score
        # Collect telemetry from the first scored candidate's diagnostics
        # so the aggregate reflects pass@1-style behavior. Skipped entries
        # contribute nothing.
        diagnostics_list = entry.get("diagnostics") or []
        if diagnostics_list:
            first_diag = diagnostics_list[0]
            if isinstance(first_diag, Mapping):
                per_row_telemetry.append(dict(first_diag))
        if best_score < threshold:
            metadata = entry["metadata"]
            errors.append(
                {
                    "row_index": entry["row_index"],
                    "source_dataset": metadata.get("source_dataset"),
                    "source_id": metadata.get("source_id"),
                    "source_row_index": metadata.get("source_row_index"),
                    "verifier": entry["verifier"],
                    "diagnostics": entry["diagnostics"],
                }
            )

    total = len(scored)
    denominator = scored_rows or 1
    return {
        "policy": policy,
        "rows": total,
        "scored_rows": scored_rows,
        "skipped_rows": skipped_rows,
        "pass_at_1": pass_at_1 / denominator,
        f"best_at_{best_k}": best_at_k / denominator,
        "mean_score_at_1": total_score_at_1 / denominator,
        f"mean_best_score_at_{best_k}": total_best_score_at_k / denominator,
        "telemetry": summarize_telemetry(per_row_telemetry),
        "failures": errors[:20],
        "failure_count": len(errors),
    }


# Telemetry-summary helpers. Designed so that environment_registry.yaml's
# `telemetry:` list (declaration) and the actual emitted keys (collected
# from `score_record` per-verifier diagnostics) can be cross-checked.
# `reward` is always derivable from the score and is included even if no
# verifier branch emits it explicitly — keep this name handy because
# every env declares it.


def summarize_telemetry(per_row: Sequence[Mapping[str, Any]]) -> JsonDict:
    """Aggregate per-row telemetry into a per-key summary.

    Coercion rules:
    - All-bool field → ``{"kind": "bool", "true_count", "false_count", "rows"}``
    - All-numeric field → ``{"kind": "numeric", "min", "max", "mean", "rows"}``
    - Mixed / other → ``{"kind": "other", "distinct_count", "rows"}``

    `latency_ms` is rounded to 3 decimals on the way out; raw values stay
    in the per-row diagnostics dicts for callers that want them.
    """
    if not per_row:
        return {}
    keys: set[str] = set()
    for row in per_row:
        if isinstance(row, Mapping):
            keys.update(row.keys())

    summary: JsonDict = {}
    for key in sorted(keys):
        values = [row[key] for row in per_row if isinstance(row, Mapping) and key in row]
        if not values:
            continue
        # bool is a subclass of int; check bool first.
        if all(isinstance(v, bool) for v in values):
            true_count = sum(1 for v in values if v)
            summary[key] = {
                "kind": "bool",
                "true_count": true_count,
                "false_count": len(values) - true_count,
                "rows": len(values),
            }
        elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            numeric = [float(v) for v in values]
            summary[key] = {
                "kind": "numeric",
                "min": round(min(numeric), 3),
                "max": round(max(numeric), 3),
                "mean": round(sum(numeric) / len(numeric), 3),
                "rows": len(numeric),
            }
        else:
            summary[key] = {
                "kind": "other",
                "distinct_count": len({str(v) for v in values}),
                "rows": len(values),
            }
    return summary


def telemetry_gap(
    declared: Sequence[str],
    emitted_summary: Mapping[str, Any],
) -> list[str]:
    """Names declared by env_registry but never emitted in this run.

    `reward` is treated as always-derivable from the score and never
    counted as a gap — every env declares it but it lives one level up
    in the aggregate (`pass_at_1`, `mean_score_at_1`).
    """
    emitted = set(emitted_summary.keys()) | {"reward"}
    return sorted(name for name in declared if name not in emitted)


def evaluate_policy(
    rows: Sequence[Mapping[str, Any]],
    *,
    policy: str,
    best_k: int,
    run_code: bool,
    container_runtime: str | None = None,
    rollout_policy: str = "oracle",
) -> JsonDict:
    """Score and aggregate in one pass. Kept for callers that don't need
    the per-row breakdown (existing tests, direct CLI users).
    """
    scored = score_rows(
        rows,
        policy=policy,
        best_k=best_k,
        run_code=run_code,
        container_runtime=container_runtime,
        rollout_policy=rollout_policy,
    )
    return aggregate_scored_rows(scored, policy=policy, best_k=best_k)


def load_environment_specs(path: Path) -> dict[str, JsonDict]:
    registry = load_yaml(path)
    specs = {}
    for env in registry.get("environments", []):
        specs[env["id"]] = env
    return specs


def discover_environment_rows(input_dir: Path) -> dict[str, dict[str, list[JsonDict]]]:
    rows_by_env: dict[str, dict[str, list[JsonDict]]] = defaultdict(dict)
    for path in sorted(input_dir.glob("*/*-split.jsonl")):
        split = path.name.replace("-split.jsonl", "")
        env_id = path.parent.name
        rows_by_env[env_id][split] = read_jsonl(path)
    return dict(rows_by_env)


def check_required_fields(rows: Sequence[Mapping[str, Any]], required_fields: Sequence[str]) -> dict[str, int]:
    missing_counts = {field: 0 for field in required_fields}
    for record in rows:
        for field in required_fields:
            if get_path(record, field) is MISSING:
                missing_counts[field] += 1
    return {field: count for field, count in missing_counts.items() if count}


def base_contract_fields() -> list[str]:
    return [
        "environment",
        "milestone",
        "use_stage",
        "question",
        "expected_answer",
        "responses_create_params.input",
        "reward_config.verifier",
        "metadata.source_dataset",
        "metadata.license",
        "metadata.data_stage",
    ]


def resolve_min_rows(
    spec_min_rows: int,
    *,
    split: str,
    requested_rows: Mapping[str, Any] | None,
) -> int:
    """Cap the env's spec-level min_rows_per_split by what prep was asked to produce.

    When ``prepare_m0_assets.py --max-train-per-dataset N`` writes a manifest
    requesting fewer rows than the env spec demands, the env's floor would
    auto-fail a legitimately small smoke run. Honor whichever is smaller and
    fall back to the spec floor when no manifest hint is present.
    """
    if not requested_rows:
        return spec_min_rows
    key = "max_train_per_dataset" if split == "train" else "max_val_per_dataset"
    requested = requested_rows.get(key)
    if requested is None:
        return spec_min_rows
    try:
        requested_int = int(requested)
    except (TypeError, ValueError):
        return spec_min_rows
    if requested_int <= 0:
        return spec_min_rows
    return min(spec_min_rows, requested_int)


def summarize_health(
    rows_by_env: Mapping[str, Mapping[str, Sequence[JsonDict]]],
    env_specs: Mapping[str, Mapping[str, Any]],
    *,
    requested_rows: Mapping[str, Any] | None = None,
) -> JsonDict:
    summary: JsonDict = {"environments": {}, "unknown_environments": []}
    for env_id, splits in rows_by_env.items():
        spec = env_specs.get(env_id)
        if spec is None:
            summary["unknown_environments"].append(env_id)
            continue
        spec_min_rows = int(spec.get("health_check", {}).get("min_rows_per_split", 1))
        required_fields = [*base_contract_fields(), *spec.get("health_check", {}).get("required_fields", [])]
        env_summary = {"splits": {}, "status": "pass"}
        for split, rows in sorted(splits.items()):
            min_rows = resolve_min_rows(spec_min_rows, split=split, requested_rows=requested_rows)
            missing_required = check_required_fields(rows, required_fields)
            row_count_ok = len(rows) >= min_rows
            split_status = "pass" if row_count_ok and not missing_required else "fail"
            if split_status == "fail":
                env_summary["status"] = "fail"
            env_summary["splits"][split] = {
                "rows": len(rows),
                "min_rows": min_rows,
                "spec_min_rows": spec_min_rows,
                "row_count_ok": row_count_ok,
                "missing_required_fields": missing_required,
                "status": split_status,
            }
        summary["environments"][env_id] = env_summary
    return summary


def summarize_baselines(
    rows_by_env: Mapping[str, Mapping[str, Sequence[JsonDict]]],
    *,
    policies: Sequence[str],
    best_k: int,
    run_code: bool,
    env_specs: Mapping[str, Mapping[str, Any]] | None = None,
    container_runtime: str | None = None,
    rollout_policy: str = "oracle",
) -> JsonDict:
    summary: JsonDict = {"best_k": best_k, "policies": list(policies), "environments": {}}
    for env_id, splits in rows_by_env.items():
        env_summary: JsonDict = {"splits": {}, "aggregate": {}}
        # Cache per-(split, policy) scored rows so the aggregate metric reuses
        # the same scores instead of re-running the verifier (which, for
        # python_unit_tests, halves the number of subprocess forks).
        scored_cache: dict[tuple[str, str], list[JsonDict]] = {}
        for split, rows in sorted(splits.items()):
            env_summary["splits"][split] = {}
            for policy in policies:
                scored = score_rows(
                    rows,
                    policy=policy,
                    best_k=best_k,
                    run_code=run_code,
                    container_runtime=container_runtime,
                    rollout_policy=rollout_policy,
                )
                scored_cache[(split, policy)] = scored
                env_summary["splits"][split][policy] = aggregate_scored_rows(
                    scored, policy=policy, best_k=best_k
                )
        declared_telemetry: list[str] = []
        if env_specs is not None and env_id in env_specs:
            declared_telemetry = list(env_specs[env_id].get("telemetry") or [])
        for policy in policies:
            combined: list[JsonDict] = []
            for split in sorted(splits):
                combined.extend(scored_cache[(split, policy)])
            aggregate = aggregate_scored_rows(combined, policy=policy, best_k=best_k)
            # Cross-check: every env_registry telemetry name should
            # eventually be emitted by some scorer. Names that aren't
            # populated yet land in `telemetry_gap` so dashboards /
            # downstream emitters can see what's still spec-only.
            aggregate["declared_telemetry"] = declared_telemetry
            aggregate["telemetry_gap"] = telemetry_gap(
                declared_telemetry, aggregate.get("telemetry") or {}
            )
            env_summary["aggregate"][policy] = aggregate
        summary["environments"][env_id] = env_summary
    return summary


def overall_status(health: Mapping[str, Any], baselines: Mapping[str, Any]) -> str:
    if not health.get("environments"):
        # No known M0 environment data was discovered. An empty report is not a pass.
        return "fail"
    if health.get("unknown_environments"):
        return "fail"
    for env_summary in health.get("environments", {}).values():
        if env_summary.get("status") != "pass":
            return "fail"
    for env_summary in baselines.get("environments", {}).values():
        oracle = env_summary.get("aggregate", {}).get("oracle")
        if not oracle:
            continue
        if oracle.get("scored_rows", 0) == 0:
            # Every oracle row was skipped (e.g. --skip-code-execution). Treat as
            # an unverified env and refuse to pass the gate.
            return "fail"
        if oracle.get("pass_at_1") != 1.0:
            return "fail"
    return "pass"


def load_requested_rows(input_dir: Path) -> JsonDict | None:
    """Read the row counts requested by prepare_m0_assets, if available.

    The manifest is the authoritative source for "how many rows did the user
    ask for"; falling back to env-registry floors when it's missing keeps the
    health check working for pre-existing data drops generated before this
    field was added.
    """
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        with manifest_path.open(encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    requested = manifest.get("requested_rows") if isinstance(manifest, Mapping) else None
    return requested if isinstance(requested, Mapping) else None


def build_report(args: argparse.Namespace) -> JsonDict:
    if not args.input_dir.is_dir():
        raise FileNotFoundError(f"input directory not found: {args.input_dir}")
    env_specs = load_environment_specs(args.environment_registry)
    rows_by_env = discover_environment_rows(args.input_dir)
    requested_rows = load_requested_rows(args.input_dir)
    policies = args.policy or ["oracle", "empty", "oracle_then_empty"]
    health = summarize_health(rows_by_env, env_specs, requested_rows=requested_rows)
    baselines = summarize_baselines(
        rows_by_env,
        policies=policies,
        best_k=args.best_k,
        run_code=not args.skip_code_execution,
        env_specs=env_specs,
        container_runtime=args.container_runtime,
        rollout_policy=args.rollout_policy,
    )
    report = {
        "schema_version": 1,
        "milestone": "M0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_dir": str(args.input_dir),
        "environment_registry": str(args.environment_registry),
        "code_execution": not args.skip_code_execution,
        "container_runtime": args.container_runtime,
        "rollout_policy": args.rollout_policy,
        "requested_rows": requested_rows or {},
        "health": health,
        "baselines": baselines,
    }
    report["status"] = overall_status(health, baselines)
    return report


def check_output_paths(output_dir: Path, overwrite: bool) -> None:
    targets = [output_dir / "health_baseline_report.json", output_dir / "health_baseline_report.md"]
    existing = [path for path in targets if path.exists()]
    if existing and not overwrite:
        formatted = "\n".join(f"  - {path}" for path in existing)
        raise FileExistsError(f"target reports already exist; pass --overwrite to replace them:\n{formatted}")


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_markdown(path: Path, report: Mapping[str, Any]) -> None:
    best_k = report["baselines"]["best_k"]
    lines = [
        "# M0 Health Check and Baseline Report",
        "",
        f"- Generated: `{report['generated_at_utc']}`",
        f"- Input directory: `{report['input_dir']}`",
        f"- Status: `{report['status']}`",
        f"- Code execution smoke: `{report['code_execution']}`",
        "",
        "Oracle baselines verify data/verifier wiring. They are not model performance numbers.",
        "",
        "## Health Checks",
        "",
        "| Environment | Split | Rows | Min Rows | Missing Required Fields | Status |",
        "|---|---|---:|---:|---|---|",
    ]
    for env_id, env_summary in sorted(report["health"]["environments"].items()):
        for split, split_summary in sorted(env_summary["splits"].items()):
            missing = ", ".join(
                f"{field}: {count}" for field, count in sorted(split_summary["missing_required_fields"].items())
            )
            lines.append(
                "| {env} | {split} | {rows} | {min_rows} | {missing} | {status} |".format(
                    env=env_id,
                    split=split,
                    rows=split_summary["rows"],
                    min_rows=split_summary["min_rows"],
                    missing=missing or "-",
                    status=split_summary["status"],
                )
            )

    lines.extend(
        [
            "",
            "## Baseline Metrics",
            "",
            f"| Environment | Policy | Rows | Scored | Skipped | pass@1 | best@{best_k} | mean score@1 | mean best@{best_k} | Failures |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for env_id, env_summary in sorted(report["baselines"]["environments"].items()):
        for policy, metrics in sorted(env_summary["aggregate"].items()):
            lines.append(
                (
                    f"| {env_id} | {policy} | {metrics['rows']} | "
                    f"{metrics.get('scored_rows', metrics['rows'])} | "
                    f"{metrics.get('skipped_rows', 0)} | "
                    f"{metrics['pass_at_1']:.3f} | "
                    f"{metrics[f'best_at_{best_k}']:.3f} | {metrics['mean_score_at_1']:.3f} | "
                    f"{metrics[f'mean_best_score_at_{best_k}']:.3f} | {metrics['failure_count']} |"
                )
            )

    # Per-env telemetry block (task021 Session 1). Surfaces the per-verifier
    # signals (latency, bool flags, etc.) collected during oracle scoring,
    # plus any telemetry names declared in env_registry that aren't yet
    # emitted (so the registry stops "lying").
    lines.extend(
        [
            "",
            "## Telemetry (oracle policy, aggregate across splits)",
            "",
            "Per-row scoring telemetry collected from `score_record` diagnostics.",
            "Numeric fields show min/mean/max; bool fields show true/false counts. ",
            "`gap` lists env_registry telemetry names that no scorer emits yet — they",
            "are reserved for the future stage2_rl runtime emitter.",
            "",
            "| Environment | Policy | Telemetry | Gap |",
            "|---|---|---|---|",
        ]
    )
    for env_id, env_summary in sorted(report["baselines"]["environments"].items()):
        for policy, metrics in sorted(env_summary["aggregate"].items()):
            telemetry = metrics.get("telemetry") or {}
            gap = metrics.get("telemetry_gap") or []
            if not telemetry and not gap:
                continue
            field_summaries = []
            for name, agg in telemetry.items():
                if agg.get("kind") == "numeric":
                    field_summaries.append(
                        f"`{name}` "
                        f"min={agg['min']}/mean={agg['mean']}/max={agg['max']} "
                        f"(n={agg['rows']})"
                    )
                elif agg.get("kind") == "bool":
                    field_summaries.append(
                        f"`{name}` "
                        f"true={agg['true_count']}/false={agg['false_count']}"
                    )
                else:
                    field_summaries.append(
                        f"`{name}` distinct={agg.get('distinct_count')} "
                        f"(n={agg.get('rows')})"
                    )
            telemetry_cell = "; ".join(field_summaries) if field_summaries else "-"
            gap_cell = ", ".join(f"`{name}`" for name in gap) if gap else "-"
            lines.append(f"| {env_id} | {policy} | {telemetry_cell} | {gap_cell} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--environment-registry", type=Path, default=ENV_REGISTRY_PATH)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--policy", action="append", choices=["oracle", "empty", "oracle_then_empty"])
    parser.add_argument("--best-k", type=int, default=2)
    parser.add_argument("--skip-code-execution", action="store_true")
    parser.add_argument(
        "--container-runtime",
        choices=["docker", "podman", "singularity"],
        default=None,
        help=(
            "Run `python_unit_tests` verifier inside a sandbox container "
            "(task021 Session 5). Default None keeps in-process execution. "
            "Image lookup goes through sandbox_image_registry.yaml; envs "
            "without a registered image fall back to in-process with a "
            "`container_fallback=true` flag in diagnostics."
        ),
    )
    parser.add_argument(
        "--rollout-policy",
        choices=["oracle", "adversarial"],
        default="oracle",
        help=(
            "Whose candidates the verifier is scoring (task021 Session 6 "
            "guard rail). Default `oracle` matches M0 health-baseline "
            "behavior (candidate=expected gold). `adversarial` is for "
            "future M1+ RLVR rollouts; combined with `--container-runtime "
            "None` it raises immediately rather than running untrusted "
            "code on the host."
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.best_k <= 0:
        print("run_m0_health_baseline.py: error: --best-k must be positive", file=sys.stderr)
        return 1
    if args.output_dir is None:
        args.output_dir = args.input_dir / DEFAULT_OUTPUT_SUBDIR
    try:
        check_output_paths(args.output_dir, args.overwrite)
        report = build_report(args)
        write_json(args.output_dir / "health_baseline_report.json", report)
        write_markdown(args.output_dir / "health_baseline_report.md", report)
    except Exception as exc:  # noqa: BLE001 - CLI should render concise failures.
        print(f"run_m0_health_baseline.py: error: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": report["status"],
                "input_dir": report["input_dir"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
