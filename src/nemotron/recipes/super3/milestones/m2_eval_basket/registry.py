# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox loader for the M2 eval basket registry.

task039 Session 1 is deliberately configuration-only. The registry and
adapter config declare the benchmark targets and their runtime blockers
without launching NeMo Evaluator, downloading live benchmark assets, or
submitting cluster jobs.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]

REGISTRY_PATH = Path(__file__).with_name("m2_eval_basket_registry.yaml")
ADAPTER_CONFIG_PATH = Path(__file__).with_name("m2_eval_adapter_config.yaml")
GAP_THRESHOLDS_PATH = Path(__file__).with_name("m2_eval_gap_thresholds.yaml")
TARGET_122B_MODEL_CLASS = "qwen3_5_122b_a10b_class"

EXPECTED_M2_BENCHMARK_IDS = frozenset(
    {
        "hle",
        "browsecomp",
        "bird_real_execution",
        "bfcl_full",
        "mcp_mark",
        "tool_decathlon",
        "multilingual_ifeval",
        "multilingual_humaneval",
    }
)

REQUIRED_ROW_FIELDS = (
    "benchmark_id",
    "adapter",
    "category",
    "license",
    "gate_metric",
    "adapter_config",
    "runtime_requirements",
)
REQUIRED_ADAPTER_FIELDS = (
    "adapter_class",
    "evaluator_task",
    "runner",
    "result_metrics",
)
REQUIRED_RUNTIME_FIELDS = (
    "sandbox_status",
    "cluster_required",
    "live_assets_required",
    "api_required",
    "database_required",
    "qwen_baseline_required",
    "blockers",
)
DEFERRED_SANDBOX_STATUSES = frozenset({"config_only", "runtime_deferred"})
REQUIRED_GAP_THRESHOLD_FIELDS = (
    "category",
    "benchmark_ids",
    "max_regression",
    "gate_action",
    "blocker_scope",
    "rationale",
)
GAP_GATE_ACTIONS = frozenset({"hold", "monitor", "rollback"})


def _load_yaml(path: Path) -> JsonDict:
    import yaml

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected YAML mapping at top level")
    return data


def _as_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{context}: expected mapping, got {type(value).__name__}")
    return value


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _benchmarks_by_category_from_rows(
    rows: list[Mapping[str, Any]] | None = None,
) -> dict[str, list[str]]:
    source = rows if rows is not None else load_m2_eval_basket()
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in source:
        category = row.get("category")
        benchmark_id = row.get("benchmark_id")
        if (
            isinstance(category, str)
            and category
            and isinstance(benchmark_id, str)
            and benchmark_id
        ):
            grouped[category].append(benchmark_id)
    return {
        category: sorted(ids)
        for category, ids in sorted(grouped.items())
    }


def validate_m2_eval_basket(data: Mapping[str, Any]) -> list[str]:
    """Return validation issues for the M2 eval basket registry."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("registry schema_version must be 1")
    if data.get("milestone") != "M2":
        issues.append("registry milestone must be M2")
    rows = data.get("benchmarks")
    if not isinstance(rows, list):
        return issues + ["registry benchmarks must be a list"]

    seen: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"benchmarks[{index}]"
        if not isinstance(row, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in REQUIRED_ROW_FIELDS:
            if field not in row:
                issues.append(f"{prefix} missing required field {field!r}")
        benchmark_id = str(row.get("benchmark_id", ""))
        if benchmark_id in seen:
            issues.append(f"{prefix} duplicate benchmark_id {benchmark_id!r}")
        seen.add(benchmark_id)
        if row.get("adapter") != f"nemo_evaluator.{benchmark_id}":
            issues.append(
                f"{prefix} adapter must be nemo_evaluator.{benchmark_id}"
            )

        adapter_config = row.get("adapter_config")
        if isinstance(adapter_config, Mapping):
            for field in REQUIRED_ADAPTER_FIELDS:
                if field not in adapter_config:
                    issues.append(
                        f"{prefix}.adapter_config missing required field {field!r}"
                    )
            metrics = adapter_config.get("result_metrics")
            if not isinstance(metrics, list) or not all(
                isinstance(metric, str) and metric for metric in metrics
            ):
                issues.append(
                    f"{prefix}.adapter_config.result_metrics must be non-empty strings"
                )
        elif "adapter_config" in row:
            issues.append(f"{prefix}.adapter_config must be a mapping")

        runtime = row.get("runtime_requirements")
        if isinstance(runtime, Mapping):
            for field in REQUIRED_RUNTIME_FIELDS:
                if field not in runtime:
                    issues.append(
                        f"{prefix}.runtime_requirements missing required field {field!r}"
                    )
            if runtime.get("sandbox_status") not in DEFERRED_SANDBOX_STATUSES:
                issues.append(
                    f"{prefix}.runtime_requirements.sandbox_status must be one of "
                    f"{sorted(DEFERRED_SANDBOX_STATUSES)}"
                )
            blockers = runtime.get("blockers")
            if (
                not isinstance(blockers, list)
                or not blockers
                or not all(
                    isinstance(blocker, str) and blocker.strip()
                    for blocker in blockers
                )
            ):
                issues.append(
                    f"{prefix}.runtime_requirements.blockers must be non-empty strings"
                )
        elif "runtime_requirements" in row:
            issues.append(f"{prefix}.runtime_requirements must be a mapping")

    missing = EXPECTED_M2_BENCHMARK_IDS - seen
    extra = seen - EXPECTED_M2_BENCHMARK_IDS
    if missing:
        issues.append(f"missing expected M2 benchmark ids: {sorted(missing)}")
    if extra:
        issues.append(f"unexpected M2 benchmark ids: {sorted(extra)}")
    return issues


def load_m2_eval_basket(path: Path | None = None) -> list[JsonDict]:
    """Load the M2 eval basket benchmark rows, raising on invalid shape."""
    target = path or REGISTRY_PATH
    data = _load_yaml(target)
    issues = validate_m2_eval_basket(data)
    if issues:
        raise ValueError(
            f"{target}: invalid M2 eval basket registry:\n- "
            + "\n- ".join(issues)
        )
    return list(data["benchmarks"])


def validate_m2_adapter_config(data: Mapping[str, Any]) -> list[str]:
    """Return validation issues for the task039 adapter-config scaffold."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("adapter config schema_version must be 1")
    if data.get("milestone") != "M2":
        issues.append("adapter config milestone must be M2")
    profiles = data.get("adapter_profiles")
    if not isinstance(profiles, list):
        return issues + ["adapter_profiles must be a list"]

    seen: set[str] = set()
    for index, profile in enumerate(profiles):
        prefix = f"adapter_profiles[{index}]"
        if not isinstance(profile, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in (
            "benchmark_id",
            "task_name",
            "adapter",
            "evaluator_task",
            "dry_run_mode",
            "default_runtime",
        ):
            if field not in profile:
                issues.append(f"{prefix} missing required field {field!r}")
        benchmark_id = str(profile.get("benchmark_id", ""))
        if benchmark_id in seen:
            issues.append(f"{prefix} duplicate benchmark_id {benchmark_id!r}")
        seen.add(benchmark_id)
        if profile.get("task_name") != f"adlr_m2_{benchmark_id}":
            issues.append(f"{prefix}.task_name must be adlr_m2_{benchmark_id}")
        if profile.get("adapter") != f"nemo_evaluator.{benchmark_id}":
            issues.append(f"{prefix}.adapter must be nemo_evaluator.{benchmark_id}")
        if profile.get("dry_run_mode") != "config_validate_only":
            issues.append(f"{prefix}.dry_run_mode must be config_validate_only")
        if profile.get("default_runtime") != "cluster_deferred":
            issues.append(f"{prefix}.default_runtime must be cluster_deferred")

    missing = EXPECTED_M2_BENCHMARK_IDS - seen
    extra = seen - EXPECTED_M2_BENCHMARK_IDS
    if missing:
        issues.append(f"adapter config missing expected ids: {sorted(missing)}")
    if extra:
        issues.append(f"adapter config has unexpected ids: {sorted(extra)}")
    return issues


def load_m2_adapter_config(path: Path | None = None) -> list[JsonDict]:
    """Load adapter profiles, raising on invalid shape."""
    target = path or ADAPTER_CONFIG_PATH
    data = _load_yaml(target)
    issues = validate_m2_adapter_config(data)
    if issues:
        raise ValueError(
            f"{target}: invalid M2 eval adapter config:\n- "
            + "\n- ".join(issues)
        )
    return list(data["adapter_profiles"])


def validate_m2_gap_thresholds(
    data: Mapping[str, Any],
    registry_rows: list[Mapping[str, Any]] | None = None,
) -> list[str]:
    """Return validation issues for sandbox M2 per-category gap thresholds."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("gap thresholds schema_version must be 1")
    if data.get("milestone") != "M2":
        issues.append("gap thresholds milestone must be M2")
    if data.get("target_model_class") != TARGET_122B_MODEL_CLASS:
        issues.append(
            "gap thresholds target_model_class must be "
            f"{TARGET_122B_MODEL_CLASS}"
        )
    rows = data.get("category_thresholds")
    if not isinstance(rows, list):
        return issues + ["category_thresholds must be a list"]

    expected_by_category = _benchmarks_by_category_from_rows(registry_rows)
    expected_categories = set(expected_by_category)
    seen_categories: set[str] = set()

    for index, row in enumerate(rows):
        prefix = f"category_thresholds[{index}]"
        if not isinstance(row, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in REQUIRED_GAP_THRESHOLD_FIELDS:
            if field not in row:
                issues.append(f"{prefix} missing required field {field!r}")

        category = row.get("category")
        if not isinstance(category, str) or not category:
            issues.append(f"{prefix}.category must be a non-empty string")
            continue
        if category in seen_categories:
            issues.append(f"{prefix} duplicate category {category!r}")
        seen_categories.add(category)

        benchmark_ids = row.get("benchmark_ids")
        if (
            not isinstance(benchmark_ids, list)
            or not benchmark_ids
            or not all(
                isinstance(benchmark_id, str) and benchmark_id
                for benchmark_id in benchmark_ids
            )
        ):
            issues.append(f"{prefix}.benchmark_ids must be non-empty strings")
        elif category in expected_by_category:
            expected_ids = expected_by_category[category]
            if sorted(benchmark_ids) != expected_ids:
                issues.append(
                    f"{prefix}.benchmark_ids must match registry category "
                    f"{category!r}: {expected_ids}"
                )

        max_regression = row.get("max_regression")
        if not _is_number(max_regression):
            issues.append(f"{prefix}.max_regression must be a number")
        elif not 0 < float(max_regression) <= 0.10:
            issues.append(
                f"{prefix}.max_regression must be > 0 and <= 0.10"
            )

        if row.get("gate_action") not in GAP_GATE_ACTIONS:
            issues.append(
                f"{prefix}.gate_action must be one of "
                f"{sorted(GAP_GATE_ACTIONS)}"
            )
        if row.get("blocker_scope") != "sandbox_threshold_only":
            issues.append(
                f"{prefix}.blocker_scope must be sandbox_threshold_only"
            )
        rationale = row.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            issues.append(f"{prefix}.rationale must be a non-empty string")

    missing = expected_categories - seen_categories
    extra = seen_categories - expected_categories
    if missing:
        issues.append(f"missing threshold categories: {sorted(missing)}")
    if extra:
        issues.append(f"unexpected threshold categories: {sorted(extra)}")
    return issues


def load_m2_gap_thresholds(path: Path | None = None) -> list[JsonDict]:
    """Load sandbox per-category gap thresholds, raising on invalid shape."""
    target = path or GAP_THRESHOLDS_PATH
    data = _load_yaml(target)
    issues = validate_m2_gap_thresholds(data)
    if issues:
        raise ValueError(
            f"{target}: invalid M2 eval gap thresholds:\n- "
            + "\n- ".join(issues)
        )
    return list(data["category_thresholds"])


def gap_thresholds_by_category(
    rows: list[Mapping[str, Any]] | None = None,
) -> dict[str, JsonDict]:
    """Return ``{category: threshold_row}`` for sandbox M2 gap thresholds."""
    source = rows if rows is not None else load_m2_gap_thresholds()
    return {
        str(row["category"]): dict(row)
        for row in sorted(source, key=lambda item: str(item["category"]))
    }


def evaluate_m2_gap_thresholds(
    current_scores: Mapping[str, float],
    baseline_scores: Mapping[str, float],
    thresholds: list[Mapping[str, Any]] | None = None,
) -> list[JsonDict]:
    """Evaluate local score maps against sandbox M2 gap thresholds.

    The function accepts already-materialized score dictionaries only. It
    deliberately performs no dataset downloads, API calls, cluster launches,
    or lookup of production Qwen baseline numbers.
    """
    source = thresholds if thresholds is not None else load_m2_gap_thresholds()
    results: list[JsonDict] = []
    for row in sorted(source, key=lambda item: str(item["category"])):
        benchmark_ids = list(row["benchmark_ids"])
        comparable_ids: list[str] = []
        current_values: list[float] = []
        baseline_values: list[float] = []
        missing_in_current: list[str] = []
        missing_in_baseline: list[str] = []

        for benchmark_id in benchmark_ids:
            has_current = benchmark_id in current_scores and _is_number(
                current_scores[benchmark_id]
            )
            has_baseline = benchmark_id in baseline_scores and _is_number(
                baseline_scores[benchmark_id]
            )
            if not has_current:
                missing_in_current.append(benchmark_id)
            if not has_baseline:
                missing_in_baseline.append(benchmark_id)
            if has_current and has_baseline:
                comparable_ids.append(benchmark_id)
                current_values.append(float(current_scores[benchmark_id]))
                baseline_values.append(float(baseline_scores[benchmark_id]))

        if comparable_ids:
            current_mean = sum(current_values) / len(current_values)
            baseline_mean = sum(baseline_values) / len(baseline_values)
            gap = current_mean - baseline_mean
            status = (
                "behind"
                if gap < -float(row["max_regression"])
                else "pass"
            )
        else:
            current_mean = None
            baseline_mean = None
            gap = None
            status = "missing"

        results.append(
            {
                "category": row["category"],
                "benchmark_ids": benchmark_ids,
                "comparable_benchmark_ids": comparable_ids,
                "current_mean": current_mean,
                "baseline_mean": baseline_mean,
                "gap": gap,
                "max_regression": float(row["max_regression"]),
                "status": status,
                "gate_action": row["gate_action"],
                "missing_in_current": missing_in_current,
                "missing_in_baseline": missing_in_baseline,
                "target_model_class": TARGET_122B_MODEL_CLASS,
            }
        )
    return results


def _format_percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def format_m2_gap_threshold_report(
    results: list[Mapping[str, Any]] | None = None,
) -> str:
    """Render a deterministic sandbox gap-threshold report."""
    findings = results if results is not None else evaluate_m2_gap_thresholds({}, {})
    if not findings:
        return "M2 eval basket gap thresholds: no results\n"

    target = str(findings[0].get("target_model_class", TARGET_122B_MODEL_CLASS))
    lines = [
        f"# M2 eval basket gap thresholds ({target})",
        "",
        "| category | status | gap | max regression | comparable | missing | gate action |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for item in sorted(findings, key=lambda row: str(row["category"])):
        comparable = ", ".join(item.get("comparable_benchmark_ids", [])) or "none"
        missing = sorted(
            set(item.get("missing_in_current", []))
            | set(item.get("missing_in_baseline", []))
        )
        lines.append(
            f"| `{item['category']}` | {item['status']} | "
            f"{_format_percent(item.get('gap'))} | "
            f"{_format_percent(item.get('max_regression'))} | "
            f"`{comparable}` | `{', '.join(missing) or 'none'}` | "
            f"{item['gate_action']} |"
        )
    return "\n".join(lines) + "\n"


def benchmarks_by_category(rows: list[Mapping[str, Any]] | None = None) -> dict[str, list[JsonDict]]:
    """Group M2 benchmark rows by category."""
    source = rows or load_m2_eval_basket()
    grouped: dict[str, list[JsonDict]] = defaultdict(list)
    for row in source:
        grouped[str(row["category"])].append(dict(row))
    return {
        category: sorted(items, key=lambda item: item["benchmark_id"])
        for category, items in sorted(grouped.items())
    }


def adapter_config_by_id(rows: list[Mapping[str, Any]] | None = None) -> dict[str, JsonDict]:
    """Return ``{benchmark_id: adapter_config}`` for registry rows."""
    source = rows or load_m2_eval_basket()
    return {
        str(row["benchmark_id"]): dict(_as_mapping(row["adapter_config"], context=str(row["benchmark_id"])))
        for row in source
    }


def runtime_blockers(rows: list[Mapping[str, Any]] | None = None) -> list[JsonDict]:
    """Return rows whose runtime is not sandbox-ready."""
    source = rows or load_m2_eval_basket()
    blockers: list[JsonDict] = []
    for row in source:
        runtime = _as_mapping(
            row["runtime_requirements"],
            context=f"{row['benchmark_id']}.runtime_requirements",
        )
        if runtime.get("sandbox_status") not in DEFERRED_SANDBOX_STATUSES:
            continue
        blockers.append(
            {
                "benchmark_id": row["benchmark_id"],
                "category": row["category"],
                "sandbox_status": runtime["sandbox_status"],
                "cluster_required": bool(runtime["cluster_required"]),
                "live_assets_required": bool(runtime["live_assets_required"]),
                "api_required": bool(runtime["api_required"]),
                "database_required": bool(runtime["database_required"]),
                "qwen_baseline_required": bool(runtime["qwen_baseline_required"]),
                "blockers": list(runtime["blockers"]),
            }
        )
    return sorted(blockers, key=lambda item: item["benchmark_id"])


def format_runtime_blocker_report(blockers: list[Mapping[str, Any]] | None = None) -> str:
    """Render a concise human-readable deferred-runtime report."""
    findings = blockers if blockers is not None else runtime_blockers()
    if not findings:
        return "M2 eval basket runtime blockers: none\n"

    lines = [
        f"M2 eval basket runtime blockers: {len(findings)} benchmark(s) deferred",
        "",
    ]
    for item in findings:
        flags = [
            flag
            for flag in (
                "cluster_required",
                "live_assets_required",
                "api_required",
                "database_required",
                "qwen_baseline_required",
            )
            if item.get(flag)
        ]
        lines.append(
            f"- {item['benchmark_id']} ({item['category']}): "
            f"{item['sandbox_status']} [{', '.join(flags)}]"
        )
        for blocker in item.get("blockers", []):
            lines.append(f"  - {blocker}")
    return "\n".join(lines) + "\n"


__all__ = [
    "ADAPTER_CONFIG_PATH",
    "EXPECTED_M2_BENCHMARK_IDS",
    "GAP_GATE_ACTIONS",
    "GAP_THRESHOLDS_PATH",
    "REGISTRY_PATH",
    "TARGET_122B_MODEL_CLASS",
    "adapter_config_by_id",
    "evaluate_m2_gap_thresholds",
    "format_m2_gap_threshold_report",
    "benchmarks_by_category",
    "gap_thresholds_by_category",
    "format_runtime_blocker_report",
    "load_m2_adapter_config",
    "load_m2_eval_basket",
    "load_m2_gap_thresholds",
    "runtime_blockers",
    "validate_m2_adapter_config",
    "validate_m2_eval_basket",
    "validate_m2_gap_thresholds",
]
