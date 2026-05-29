# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Benchmark-alignment ledger validation for Qwen eval evidence.

The task079 ledger is deliberately stricter than the generic M1/M2 basket
registries. Basket membership says which tasks are in scope; this module says
which run artifacts are allowed to count as Qwen benchmark-improvement evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_eval_repro_gate import (
    VALID_ARTIFACT_CHECK_STATUSES,
    is_remote_artifact_reference,
    validate_local_raw_artifact_fingerprints,
    validate_raw_artifact_paths,
)

JsonDict = dict[str, Any]

M1_EVAL_BASKET_DIR = Path(__file__).resolve().parent
REPO_ROOT = M1_EVAL_BASKET_DIR.parents[5]
MILESTONES_DIR = M1_EVAL_BASKET_DIR.parent
SUPER3_DIR = MILESTONES_DIR.parent
STAGE3_EVAL_CONFIG_DIR = SUPER3_DIR / "stage3_eval" / "config"
M2_EVAL_BASKET_DIR = MILESTONES_DIR / "m2_eval_basket"

BENCHMARK_ALIGNMENT_LEDGER_PATH = M1_EVAL_BASKET_DIR / (
    "qwen_benchmark_alignment_ledger.yaml"
)
M1_V0_REGISTRY_PATH = M1_EVAL_BASKET_DIR / "m1_eval_basket_registry.yaml"
M1_FULL_REGISTRY_PATH = M1_EVAL_BASKET_DIR / "m1_eval_full_basket_registry.yaml"
M1_LAUNCHER_MAPPING_PATH = M1_EVAL_BASKET_DIR / "m1_eval_launcher_mapping.yaml"
M2_REGISTRY_PATH = M2_EVAL_BASKET_DIR / "m2_eval_basket_registry.yaml"

QWEN_CORRECTED_BENCHMARK_IDS = frozenset({"mmlu_pro", "aime25", "hmmt"})
REQUIRED_TARGET_SUITE_IDS = frozenset(
    {
        "m1_v0_basket_gate_targets",
        "m1_full_basket_target",
        "m1_full_basket_launcher_available",
        "m1_qwen_corrected_improvement_subset",
        "m2_eval_basket_config_only",
    }
)
VALID_GATE_USAGES = frozenset(
    {
        "target_acceptance_basket",
        "runnable_regression_subset",
        "qwen_benchmark_improvement_gate",
        "config_only_gate",
    }
)
VALID_EVIDENCE_STATUSES = frozenset({"valid_delta_evidence"})
VALID_INVALID_EVAL_TYPES = frozenset(
    {
        "completions_only",
        "short_generation_capped",
        "parser_misaligned",
        "missing_raw_artifact",
        "missing_baseline_delta",
        "open_pr_context_only",
        "targeted_smoke_only",
        "config_only_no_frozen_baseline",
    }
)

REQUIRED_SUITE_FIELDS = (
    "suite_id",
    "milestone",
    "gate_usage",
    "benchmark_ids",
    "evidence_policy",
)
REQUIRED_PROTOCOL_FIELDS = (
    "benchmark_id",
    "suite_id",
    "endpoint_type",
    "route",
    "endpoint_url_shape",
    "prompt_contract",
    "parser",
    "final_answer_format",
    "min_max_generation_tokens",
    "accepted_max_generation_tokens",
    "raw_artifact_requirements",
    "invalid_legacy_issue_types",
)
REQUIRED_EVIDENCE_FIELDS = (
    "evidence_id",
    "benchmark_id",
    "suite_id",
    "source_manifests",
    "baseline",
    "current",
    "delta",
    "endpoint_type",
    "route",
    "endpoint_url_shape",
    "prompt_contract",
    "parser",
    "final_answer_format",
    "max_generation_tokens",
    "raw_artifact_paths",
    "artifact_check",
    "gate_status",
)
REQUIRED_RECORD_FIELDS = (
    "model_id",
    "model_path",
    "endpoint_model_id",
    "metric_name",
    "metric_value",
)
REQUIRED_DELTA_FIELDS = (
    "metric_name",
    "baseline_value",
    "current_value",
    "current_minus_baseline",
    "higher_is_better",
    "counts_as_improvement",
)


def _load_yaml(path: Path) -> JsonDict:
    import yaml

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected YAML mapping at top level")
    return data


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _load_benchmark_ids(path: Path) -> set[str]:
    data = _load_yaml(path)
    rows = data.get("benchmarks")
    if not isinstance(rows, list):
        return set()
    return {
        str(row["benchmark_id"])
        for row in rows
        if isinstance(row, Mapping) and _is_non_empty_string(row.get("benchmark_id"))
    }


def _load_launcher_available_ids() -> set[str]:
    data = _load_yaml(M1_LAUNCHER_MAPPING_PATH)
    rows = data.get("tasks")
    if not isinstance(rows, list):
        return set()
    return {
        str(row["benchmark_id"])
        for row in rows
        if isinstance(row, Mapping)
        and row.get("status") == "available"
        and _is_non_empty_string(row.get("benchmark_id"))
    }


def _validate_artifact_check(
    value: Any,
    *,
    context: str,
    requires_pm_verified: bool = False,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{context} must be a mapping for checked raw artifacts"]
    issues: list[str] = []
    status = value.get("status")
    if not _is_non_empty_string(status):
        issues.append(f"{context}.status must be a non-empty string")
    elif status not in VALID_ARTIFACT_CHECK_STATUSES:
        issues.append(
            f"{context}.status must be one of "
            f"{sorted(VALID_ARTIFACT_CHECK_STATUSES)}; got {status!r}"
        )
    elif requires_pm_verified and status != "pm_verified":
        issues.append(
            f"{context}.status must be 'pm_verified' for remote raw artifact "
            f"references; got {status!r}"
        )
    for field in ("checked_at_utc", "checked_by"):
        if not _is_non_empty_string(value.get(field)):
            issues.append(f"{context}.{field} must be a non-empty string")
    return issues


def _validate_repo_relative_existing_paths(
    paths: list[str],
    *,
    context: str,
) -> list[str]:
    issues: list[str] = []
    repo_root = REPO_ROOT.resolve(strict=True)
    for path in paths:
        candidate = Path(path)
        if candidate.is_absolute():
            issues.append(f"{context} must be repo-relative: {path}")
            continue
        components = path.split("/")
        if any(component in {"", "."} for component in components):
            issues.append(
                f"{context} must use normal repo-relative path components: {path}"
            )
            continue
        if ".." in components:
            issues.append(f"{context} must not contain traversal components: {path}")
            continue
        try:
            resolved = (repo_root / candidate).resolve(strict=True)
        except FileNotFoundError:
            issues.append(f"{context} repo-relative path does not exist: {path}")
            continue
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            issues.append(f"{context} must stay under repo root: {path}")
            continue
        if not resolved.is_file():
            issues.append(f"{context} repo-relative path must be a file: {path}")
    return issues


def _validate_declared_source_manifests(
    value: Any,
) -> tuple[set[str] | None, list[str]]:
    if (
        not isinstance(value, list)
        or not value
        or not all(_is_non_empty_string(path) for path in value)
    ):
        return None, ["source_manifests must be non-empty strings"]

    paths = [str(path) for path in value]
    return set(paths), _validate_repo_relative_existing_paths(
        paths,
        context="source_manifests",
    )


def _validate_record(value: Any, *, context: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{context} must be a mapping"]
    issues: list[str] = []
    for field in REQUIRED_RECORD_FIELDS:
        if field not in value:
            issues.append(f"{context} missing required field {field!r}")
    for field in ("model_id", "model_path", "endpoint_model_id", "metric_name"):
        if field in value and not _is_non_empty_string(value[field]):
            issues.append(f"{context}.{field} must be a non-empty string")
    if "metric_value" in value and not _is_number(value["metric_value"]):
        issues.append(f"{context}.metric_value must be a number")
    return issues


def _validate_delta(value: Any, *, context: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{context} must be a mapping"]
    issues: list[str] = []
    for field in REQUIRED_DELTA_FIELDS:
        if field not in value:
            issues.append(f"{context} missing required field {field!r}")
    for field in ("baseline_value", "current_value", "current_minus_baseline"):
        if field in value and not _is_number(value[field]):
            issues.append(f"{context}.{field} must be a number")
    if "higher_is_better" in value and not isinstance(value["higher_is_better"], bool):
        issues.append(f"{context}.higher_is_better must be a bool")
    if "counts_as_improvement" in value and not isinstance(
        value["counts_as_improvement"], bool
    ):
        issues.append(f"{context}.counts_as_improvement must be a bool")

    if all(
        _is_number(value.get(field))
        for field in ("baseline_value", "current_value", "current_minus_baseline")
    ):
        expected = float(value["current_value"]) - float(value["baseline_value"])
        if abs(expected - float(value["current_minus_baseline"])) > 1e-12:
            issues.append(
                f"{context}.current_minus_baseline must equal "
                "current_value - baseline_value"
            )
        if isinstance(value.get("higher_is_better"), bool) and isinstance(
            value.get("counts_as_improvement"), bool
        ):
            improvement = (
                expected > 0 if value["higher_is_better"] else expected < 0
            )
            if value["counts_as_improvement"] is not improvement:
                issues.append(
                    f"{context}.counts_as_improvement must match metric direction"
                )
    return issues


def _suite_ids_by_id(suites: Any, issues: list[str]) -> dict[str, set[str]]:
    by_id: dict[str, set[str]] = {}
    if not isinstance(suites, list) or not suites:
        issues.append("target_suites must be a non-empty list")
        return by_id

    seen: set[str] = set()
    for index, suite in enumerate(suites):
        prefix = f"target_suites[{index}]"
        if not isinstance(suite, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in REQUIRED_SUITE_FIELDS:
            if field not in suite:
                issues.append(f"{prefix} missing required field {field!r}")
        suite_id = suite.get("suite_id")
        if not _is_non_empty_string(suite_id):
            issues.append(f"{prefix}.suite_id must be a non-empty string")
            continue
        suite_id = str(suite_id)
        if suite_id in seen:
            issues.append(f"{prefix} duplicate suite_id {suite_id!r}")
        seen.add(suite_id)
        if suite.get("gate_usage") not in VALID_GATE_USAGES:
            issues.append(
                f"{prefix}.gate_usage must be one of {sorted(VALID_GATE_USAGES)}"
            )
        benchmark_ids = suite.get("benchmark_ids")
        if (
            not isinstance(benchmark_ids, list)
            or not benchmark_ids
            or not all(_is_non_empty_string(item) for item in benchmark_ids)
        ):
            issues.append(f"{prefix}.benchmark_ids must be non-empty strings")
            continue
        by_id[suite_id] = {str(item) for item in benchmark_ids}
        policy = suite.get("evidence_policy")
        if not isinstance(policy, Mapping):
            issues.append(f"{prefix}.evidence_policy must be a mapping")
        elif "accepts_improvement_evidence" not in policy:
            issues.append(
                f"{prefix}.evidence_policy missing 'accepts_improvement_evidence'"
            )
    missing = REQUIRED_TARGET_SUITE_IDS - seen
    if missing:
        issues.append(f"target_suites missing required suite ids: {sorted(missing)}")
    return by_id


def _validate_target_suite_crosswalk(suite_ids: dict[str, set[str]]) -> list[str]:
    issues: list[str] = []
    v0_ids = _load_benchmark_ids(M1_V0_REGISTRY_PATH)
    full_ids = _load_benchmark_ids(M1_FULL_REGISTRY_PATH)
    m2_ids = _load_benchmark_ids(M2_REGISTRY_PATH)
    available_ids = _load_launcher_available_ids()

    expected_by_suite = {
        "m1_v0_basket_gate_targets": v0_ids,
        "m1_full_basket_target": v0_ids | full_ids,
        "m1_full_basket_launcher_available": available_ids,
        "m1_qwen_corrected_improvement_subset": set(QWEN_CORRECTED_BENCHMARK_IDS),
        "m2_eval_basket_config_only": m2_ids,
    }
    for suite_id, expected in expected_by_suite.items():
        if suite_id not in suite_ids:
            continue
        actual = suite_ids[suite_id]
        if actual != expected:
            issues.append(
                f"{suite_id} benchmark_ids drift: "
                f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
            )
    return issues


def _protocols_by_benchmark(
    protocols: Any,
    issues: list[str],
) -> dict[str, Mapping[str, Any]]:
    by_id: dict[str, Mapping[str, Any]] = {}
    if not isinstance(protocols, list) or not protocols:
        issues.append("benchmark_protocols must be a non-empty list")
        return by_id

    for index, protocol in enumerate(protocols):
        prefix = f"benchmark_protocols[{index}]"
        if not isinstance(protocol, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in REQUIRED_PROTOCOL_FIELDS:
            if field not in protocol:
                issues.append(f"{prefix} missing required field {field!r}")
        benchmark_id = protocol.get("benchmark_id")
        if not _is_non_empty_string(benchmark_id):
            issues.append(f"{prefix}.benchmark_id must be a non-empty string")
            continue
        benchmark_id = str(benchmark_id)
        if benchmark_id in by_id:
            issues.append(f"{prefix} duplicate benchmark_id {benchmark_id!r}")
        by_id[benchmark_id] = protocol
        if protocol.get("suite_id") != "m1_qwen_corrected_improvement_subset":
            issues.append(
                f"{prefix}.suite_id must be m1_qwen_corrected_improvement_subset"
            )
        if protocol.get("endpoint_type") != "openai_chat_completions":
            issues.append(f"{prefix}.endpoint_type must be openai_chat_completions")
        if protocol.get("route") != "/v1/chat/completions":
            issues.append(f"{prefix}.route must be /v1/chat/completions")
        if not _is_positive_int(protocol.get("min_max_generation_tokens")):
            issues.append(f"{prefix}.min_max_generation_tokens must be positive int")
        if not _is_positive_int(protocol.get("accepted_max_generation_tokens")):
            issues.append(f"{prefix}.accepted_max_generation_tokens must be positive int")
        requirements = protocol.get("raw_artifact_requirements")
        if (
            not isinstance(requirements, list)
            or not requirements
            or not all(_is_non_empty_string(item) for item in requirements)
        ):
            issues.append(f"{prefix}.raw_artifact_requirements must be non-empty strings")
        issue_types = protocol.get("invalid_legacy_issue_types")
        if not isinstance(issue_types, list) or not issue_types:
            issues.append(f"{prefix}.invalid_legacy_issue_types must be non-empty")
        else:
            unknown = set(issue_types) - VALID_INVALID_EVAL_TYPES
            if unknown:
                issues.append(
                    f"{prefix}.invalid_legacy_issue_types unknown values: "
                    f"{sorted(unknown)}"
                )
            if "missing_raw_artifact" not in issue_types:
                issues.append(
                    f"{prefix}.invalid_legacy_issue_types must include "
                    "missing_raw_artifact"
                )

    missing = QWEN_CORRECTED_BENCHMARK_IDS - set(by_id)
    if missing:
        issues.append(f"benchmark_protocols missing corrected ids: {sorted(missing)}")
    return by_id


def _validate_evidence_records(
    records: Any,
    *,
    protocols: Mapping[str, Mapping[str, Any]],
    declared_source_manifests: set[str] | None,
) -> list[str]:
    issues: list[str] = []
    if not isinstance(records, list) or not records:
        return ["evidence_records must be a non-empty list"]

    seen: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"evidence_records[{index}]"
        if not isinstance(record, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in REQUIRED_EVIDENCE_FIELDS:
            if field not in record:
                issues.append(f"{prefix} missing required field {field!r}")
        evidence_id = record.get("evidence_id")
        if not _is_non_empty_string(evidence_id):
            issues.append(f"{prefix}.evidence_id must be a non-empty string")
        elif str(evidence_id) in seen:
            issues.append(f"{prefix} duplicate evidence_id {evidence_id!r}")
        else:
            seen.add(str(evidence_id))

        benchmark_id = str(record.get("benchmark_id", ""))
        protocol = protocols.get(benchmark_id)
        if protocol is None:
            issues.append(f"{prefix}.benchmark_id has no corrected protocol")
            continue
        if record.get("suite_id") != "m1_qwen_corrected_improvement_subset":
            issues.append(
                f"{prefix}.suite_id must be m1_qwen_corrected_improvement_subset"
            )
        if record.get("endpoint_type") != "openai_chat_completions":
            issues.append(
                f"{prefix}: completions-only evidence cannot count as benchmark "
                "improvement evidence; endpoint_type must be openai_chat_completions"
            )
        if record.get("route") != "/v1/chat/completions":
            issues.append(
                f"{prefix}: completions-only evidence cannot count as benchmark "
                "improvement evidence; route must be /v1/chat/completions"
            )
        if record.get("parser") != protocol.get("parser"):
            issues.append(
                f"{prefix}: parser-misaligned evidence cannot count as benchmark "
                f"improvement evidence for {benchmark_id}"
            )
        if record.get("final_answer_format") != protocol.get("final_answer_format"):
            issues.append(
                f"{prefix}.final_answer_format must match corrected protocol"
            )
        min_tokens = protocol.get("min_max_generation_tokens")
        max_tokens = record.get("max_generation_tokens")
        if not _is_positive_int(max_tokens):
            issues.append(f"{prefix}.max_generation_tokens must be positive int")
        elif _is_positive_int(min_tokens) and max_tokens < min_tokens:
            issues.append(
                f"{prefix}: short generation cap cannot count as benchmark "
                f"improvement evidence for {benchmark_id}; "
                f"got {max_tokens}, require >= {min_tokens}"
            )

        source_manifests = record.get("source_manifests")
        if (
            not isinstance(source_manifests, list)
            or not source_manifests
            or not all(_is_non_empty_string(path) for path in source_manifests)
        ):
            issues.append(f"{prefix}.source_manifests must be non-empty strings")
        else:
            issues.extend(
                _validate_repo_relative_existing_paths(
                    list(source_manifests),
                    context=f"{prefix}.source_manifests",
                )
            )
            if declared_source_manifests is not None:
                for source_manifest in source_manifests:
                    if str(source_manifest) not in declared_source_manifests:
                        issues.append(
                            f"{prefix}.source_manifests entry is not declared in "
                            f"top-level source_manifests: {source_manifest}"
                        )

        issues.extend(_validate_record(record.get("baseline"), context=f"{prefix}.baseline"))
        issues.extend(_validate_record(record.get("current"), context=f"{prefix}.current"))
        issues.extend(_validate_delta(record.get("delta"), context=f"{prefix}.delta"))
        if (
            isinstance(record.get("baseline"), Mapping)
            and isinstance(record.get("current"), Mapping)
            and isinstance(record.get("delta"), Mapping)
        ):
            baseline_metric = record["baseline"].get("metric_value")
            current_metric = record["current"].get("metric_value")
            delta = record["delta"]
            if _is_number(baseline_metric) and _is_number(delta.get("baseline_value")):
                if abs(float(baseline_metric) - float(delta["baseline_value"])) > 1e-12:
                    issues.append(f"{prefix}.delta.baseline_value must match baseline")
            if _is_number(current_metric) and _is_number(delta.get("current_value")):
                if abs(float(current_metric) - float(delta["current_value"])) > 1e-12:
                    issues.append(f"{prefix}.delta.current_value must match current")

        raw_paths = record.get("raw_artifact_paths")
        raw_issues = validate_raw_artifact_paths(
            raw_paths,
            context=f"{prefix}.raw_artifact_paths",
        )
        for issue in raw_issues:
            issues.append(
                f"{prefix}: missing raw artifact evidence cannot count as "
                f"benchmark improvement evidence ({issue})"
            )
        issues.extend(
            validate_local_raw_artifact_fingerprints(
                raw_paths,
                record.get("raw_artifact_sha256"),
                context=prefix,
            )
        )
        has_remote_raw_artifacts = isinstance(raw_paths, list) and any(
            isinstance(path, str) and is_remote_artifact_reference(path)
            for path in raw_paths
        )
        if has_remote_raw_artifacts:
            issues.extend(
                _validate_artifact_check(
                    record.get("artifact_check"),
                    context=f"{prefix}.artifact_check",
                    requires_pm_verified=True,
                )
            )
        if record.get("gate_status") not in VALID_EVIDENCE_STATUSES:
            issues.append(
                f"{prefix}.gate_status must be one of {sorted(VALID_EVIDENCE_STATUSES)}"
            )
    return issues


def _validate_invalid_surfaces(value: Any) -> list[str]:
    issues: list[str] = []
    if not isinstance(value, list) or not value:
        return ["invalid_legacy_eval_surfaces must be a non-empty list"]
    covered: set[str] = set()
    for index, finding in enumerate(value):
        prefix = f"invalid_legacy_eval_surfaces[{index}]"
        if not isinstance(finding, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        for field in (
            "finding_id",
            "benchmark_id",
            "issue_types",
            "invalid_reason",
            "required_remediation",
        ):
            if field not in finding:
                issues.append(f"{prefix} missing required field {field!r}")
        issue_types = finding.get("issue_types")
        if (
            not isinstance(issue_types, list)
            or not issue_types
            or not all(_is_non_empty_string(item) for item in issue_types)
        ):
            issues.append(f"{prefix}.issue_types must be non-empty strings")
            continue
        unknown = set(issue_types) - VALID_INVALID_EVAL_TYPES
        if unknown:
            issues.append(f"{prefix}.issue_types unknown values: {sorted(unknown)}")
        covered.update(str(item) for item in issue_types)
    required = {
        "completions_only",
        "short_generation_capped",
        "parser_misaligned",
        "missing_raw_artifact",
    }
    missing = required - covered
    if missing:
        issues.append(
            "invalid_legacy_eval_surfaces must cover issue types: "
            f"{sorted(missing)}"
        )
    return issues


def _validate_context_only_records(value: Any) -> list[str]:
    issues: list[str] = []
    if value is None:
        return issues
    if not isinstance(value, list):
        return ["context_only_records must be a list"]
    for index, record in enumerate(value):
        prefix = f"context_only_records[{index}]"
        if not isinstance(record, Mapping):
            issues.append(f"{prefix} must be a mapping")
            continue
        if record.get("count_as_improvement_evidence") is not False:
            issues.append(
                f"{prefix}.count_as_improvement_evidence must be false until "
                "the referenced PR evidence is merged and artifact-checked"
            )
        for field in ("source", "reason"):
            if not _is_non_empty_string(record.get(field)):
                issues.append(f"{prefix}.{field} must be a non-empty string")
    return issues


def validate_benchmark_alignment_ledger(data: Mapping[str, Any]) -> list[str]:
    """Return validation issues for the task079 benchmark-alignment ledger."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("ledger schema_version must be 1")
    if data.get("ledger_id") != "task079_qwen_benchmark_alignment_s1":
        issues.append("ledger_id must be task079_qwen_benchmark_alignment_s1")

    suite_ids = _suite_ids_by_id(data.get("target_suites"), issues)
    issues.extend(_validate_target_suite_crosswalk(suite_ids))

    protocols = _protocols_by_benchmark(data.get("benchmark_protocols"), issues)
    declared_source_manifests, source_manifest_issues = (
        _validate_declared_source_manifests(data.get("source_manifests"))
    )
    issues.extend(source_manifest_issues)
    issues.extend(
        _validate_evidence_records(
            data.get("evidence_records"),
            protocols=protocols,
            declared_source_manifests=declared_source_manifests,
        )
    )
    issues.extend(_validate_invalid_surfaces(data.get("invalid_legacy_eval_surfaces")))
    issues.extend(_validate_context_only_records(data.get("context_only_records")))
    return issues


def load_benchmark_alignment_ledger(path: Path | None = None) -> JsonDict:
    """Load the benchmark-alignment ledger, raising on invalid shape."""
    target = path or BENCHMARK_ALIGNMENT_LEDGER_PATH
    data = _load_yaml(target)
    issues = validate_benchmark_alignment_ledger(data)
    if issues:
        raise ValueError(
            f"{target}: invalid benchmark alignment ledger:\n- "
            + "\n- ".join(issues)
        )
    return data


def benchmark_alignment_target_suites(
    data: Mapping[str, Any] | None = None,
) -> dict[str, list[str]]:
    """Return ``{suite_id: benchmark_ids}`` for deterministic reporting."""
    source = data if data is not None else load_benchmark_alignment_ledger()
    return {
        str(suite["suite_id"]): list(suite["benchmark_ids"])
        for suite in sorted(source["target_suites"], key=lambda row: row["suite_id"])
    }


def valid_benchmark_improvement_evidence(
    data: Mapping[str, Any] | None = None,
) -> list[JsonDict]:
    """Return countable benchmark-improvement evidence rows.

    A valid evidence row still counts as an improvement only when its recorded
    delta moves in the metric's configured direction. Negative or neutral
    corrected deltas remain auditable evidence but do not become promotions.
    """
    source = data if data is not None else load_benchmark_alignment_ledger()
    issues = validate_benchmark_alignment_ledger(source)
    if issues:
        raise ValueError(
            "invalid benchmark alignment ledger:\n- " + "\n- ".join(issues)
        )
    return [
        dict(record)
        for record in source["evidence_records"]
        if record.get("gate_status") in VALID_EVIDENCE_STATUSES
        and record.get("delta", {}).get("counts_as_improvement") is True
    ]


__all__ = [
    "BENCHMARK_ALIGNMENT_LEDGER_PATH",
    "QWEN_CORRECTED_BENCHMARK_IDS",
    "VALID_ARTIFACT_CHECK_STATUSES",
    "VALID_INVALID_EVAL_TYPES",
    "benchmark_alignment_target_suites",
    "load_benchmark_alignment_ledger",
    "valid_benchmark_improvement_evidence",
    "validate_benchmark_alignment_ledger",
]
