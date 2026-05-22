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
    "REGISTRY_PATH",
    "adapter_config_by_id",
    "benchmarks_by_category",
    "format_runtime_blocker_report",
    "load_m2_adapter_config",
    "load_m2_eval_basket",
    "runtime_blockers",
    "validate_m2_adapter_config",
    "validate_m2_eval_basket",
]
