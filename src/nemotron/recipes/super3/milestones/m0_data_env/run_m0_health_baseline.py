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


def run_python_unit_tests(candidate: Any, record: Mapping[str, Any], timeout_s: int) -> tuple[float, JsonDict]:
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
        try:
            result = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return 0.0, {"error": "timeout", "timeout_s": timeout_s, "stdout": exc.stdout, "stderr": exc.stderr}
    score = 1.0 if result.returncode == 0 else 0.0
    return score, {
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-1000:],
        "stderr_tail": result.stderr[-1000:],
    }


def score_record(candidate: Any, record: Mapping[str, Any], *, run_code: bool = True) -> tuple[float | None, JsonDict]:
    verifier = record.get("reward_config", {}).get("verifier")
    expected = record.get("expected_answer")
    if verifier == "normalized_exact_or_contains":
        return score_text(candidate, expected), {}
    if verifier == "normalized_numeric_exact_match":
        return score_numeric(candidate, expected), {}
    if verifier == "tool_schema_and_argument_match":
        return score_tool_call(candidate, expected, record), {}
    if verifier == "python_unit_tests":
        if not run_code:
            return None, {"skipped": "code execution disabled"}
        timeout_s = int(record.get("reward_config", {}).get("timeout_s", 30))
        return run_python_unit_tests(candidate, record, timeout_s=timeout_s)
    return 0.0, {"error": f"unsupported verifier: {verifier}"}


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
) -> list[JsonDict]:
    """Score each row once and return raw per-row results.

    Pulled out of `evaluate_policy` so that aggregate metrics can be derived from
    the same per-row scores as the split metrics, instead of re-invoking the
    verifier (and, for python_unit_tests, re-spawning subprocesses).
    """
    out: list[JsonDict] = []
    for index, record in enumerate(rows):
        candidates = candidates_for_policy(record, policy)
        scores: list[float] = []
        diagnostics: list[JsonDict] = []
        for candidate in candidates[: max(best_k, 1)]:
            score, detail = score_record(candidate, record, run_code=run_code)
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
        "failures": errors[:20],
        "failure_count": len(errors),
    }


def evaluate_policy(
    rows: Sequence[Mapping[str, Any]],
    *,
    policy: str,
    best_k: int,
    run_code: bool,
) -> JsonDict:
    """Score and aggregate in one pass. Kept for callers that don't need
    the per-row breakdown (existing tests, direct CLI users).
    """
    scored = score_rows(rows, policy=policy, best_k=best_k, run_code=run_code)
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
                scored = score_rows(rows, policy=policy, best_k=best_k, run_code=run_code)
                scored_cache[(split, policy)] = scored
                env_summary["splits"][split][policy] = aggregate_scored_rows(
                    scored, policy=policy, best_k=best_k
                )
        for policy in policies:
            combined: list[JsonDict] = []
            for split in sorted(splits):
                combined.extend(scored_cache[(split, policy)])
            env_summary["aggregate"][policy] = aggregate_scored_rows(
                combined, policy=policy, best_k=best_k
            )
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
    baselines = summarize_baselines(rows_by_env, policies=policies, best_k=args.best_k, run_code=not args.skip_code_execution)
    report = {
        "schema_version": 1,
        "milestone": "M0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_dir": str(args.input_dir),
        "environment_registry": str(args.environment_registry),
        "code_execution": not args.skip_code_execution,
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

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--environment-registry", type=Path, default=ENV_REGISTRY_PATH)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--policy", action="append", choices=["oracle", "empty", "oracle_then_empty"])
    parser.add_argument("--best-k", type=int, default=2)
    parser.add_argument("--skip-code-execution", action="store_true")
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
