# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Qwen-first eval reproduction gate for chat-template changes.

This gate is deliberately evidence-first. Matching the repo's
``super3.jinja`` settings is not enough for Qwen-targeted work; a
candidate must preserve or refresh base-Qwen eval reproduction evidence
that records the checkpoint/tokenizer, endpoint route, prompt/parser
contract, raw artifacts, and known harness mismatches.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

JsonDict = dict[str, Any]

QWEN_EVAL_REPRO_GATE_PATH = Path(__file__).with_name(
    "qwen_eval_repro_gate.yaml"
)
REPO_ROOT = Path(__file__).resolve().parents[6]

REQUIRED_REFERENCE_MODEL_FIELDS = (
    "source_model",
    "local_model_path",
    "tokenizer_reference",
    "chat_template_reference",
    "qwen_first",
)
REQUIRED_EVAL_PATH_FIELDS = (
    "endpoint_type",
    "chat_route",
    "completions_route",
    "endpoint_url_shape",
    "chat_template_kwargs",
    "parser_contract",
)
REQUIRED_EVIDENCE_FIELDS = (
    "evidence_id",
    "benchmark_id",
    "benchmark_name",
    "evidence_type",
    "gate_status",
    "source_manifest",
    "model_id",
    "model_path",
    "endpoint_type",
    "route",
    "endpoint_url_shape",
    "chat_template_source",
    "chat_template_kwargs",
    "max_generation_tokens",
    "parser",
    "final_answer_format",
    "sample_scope",
    "baseline_numbers",
    "raw_artifact_paths",
)
REQUIRED_INVALID_FINDING_FIELDS = (
    "finding_id",
    "benchmark_id",
    "issue_types",
    "invalid_reason",
    "required_remediation",
)
VALID_INVALID_FINDING_TYPES = frozenset(
    {"completions_only", "short_generation_capped", "parser_misaligned"}
)
VALID_EVIDENCE_STATUSES = frozenset(
    {"valid_qwen_reproduction_smoke", "valid_qwen_reproduction_full"}
)
VALID_ARTIFACT_CHECK_STATUSES = frozenset(
    {
        "pm_verified",
        "local_workspace_verified",
    }
)
REMOTE_ARTIFACT_PREFIXES = ("vm4vpn:", "vpn:")


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


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS: dict[str, bool] = {
    "enable_thinking": False,
    "truncate_history_thinking": False,
}


def _validate_chat_template_kwargs(
    value: Any,
    *,
    context: str,
) -> list[str]:
    """Validate the Qwen chat-template kwargs at a fixed contract.

    The gate exists to certify that Qwen reproduction evidence and the
    intended eval path actually use the Qwen contract — false/false for
    both `enable_thinking` and `truncate_history_thinking` (the values
    SFT trains against; see docs/chat-template-consistency-review.md
    PRs C+D). A type-only check would let a future YAML edit silently
    flip a value and still pass validation; pin the contract values
    here so any drift surfaces immediately.
    """
    issues: list[str] = []
    if not isinstance(value, Mapping):
        return [f"{context} must be a mapping"]
    for key, expected in QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS.items():
        if key not in value:
            issues.append(f"{context}.{key} must be present")
            continue
        actual = value[key]
        if not isinstance(actual, bool):
            issues.append(f"{context}.{key} must be a bool")
            continue
        if actual is not expected:
            issues.append(
                f"{context}.{key} must be {expected!s} for the Qwen "
                "chat-template contract (matches SFT-time rendering); "
                f"got {actual!s}"
            )
    return issues


def is_remote_artifact_reference(path: str) -> bool:
    """Return whether *path* is an explicitly remote artifact reference."""
    return path.startswith(REMOTE_ARTIFACT_PREFIXES)


def _validate_remote_artifact_check(
    value: Any,
    *,
    context: str,
    requires_pm_verified: bool = False,
) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{context} must be a mapping for remote raw artifact paths"]
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
    if not _is_non_empty_string(value.get("checked_at_utc")):
        issues.append(f"{context}.checked_at_utc must be a non-empty string")
    if not _is_non_empty_string(value.get("checked_by")):
        issues.append(f"{context}.checked_by must be a non-empty string")
    return issues


def validate_raw_artifact_paths(paths: Any, *, context: str) -> list[str]:
    """Validate raw artifact paths used as gate evidence.

    Local paths must be regular files in the current filesystem. Remote
    references are allowed only when they use an explicit checked remote prefix
    such as ``vm4vpn:``; the caller validates the corresponding check metadata.
    """
    if (
        not isinstance(paths, list)
        or not paths
        or not all(_is_non_empty_string(path) for path in paths)
    ):
        return [f"{context} must be non-empty strings"]

    issues: list[str] = []
    for path in paths:
        if is_remote_artifact_reference(path):
            continue
        local_path = Path(path).expanduser()
        if not local_path.exists():
            issues.append(
                f"{context} local path does not exist and is not a checked "
                f"remote artifact reference: {path}"
            )
            continue
        if not local_path.is_file():
            issues.append(
                f"{context} local path must be a regular file and is not a "
                f"checked remote artifact reference: {path}"
            )
    return issues


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_local_raw_artifact_fingerprints(
    paths: Any,
    fingerprints: Any,
    *,
    context: str,
) -> list[str]:
    if not isinstance(paths, list):
        return []
    local_paths = [
        path
        for path in paths
        if _is_non_empty_string(path) and not is_remote_artifact_reference(path)
    ]
    if not local_paths:
        return []
    if not isinstance(fingerprints, Mapping):
        return [f"{context}.raw_artifact_sha256 must be a mapping for local raw artifact paths"]

    issues: list[str] = []
    for path in local_paths:
        expected = fingerprints.get(path)
        if not _is_non_empty_string(expected):
            issues.append(
                f"{context}.raw_artifact_sha256 missing SHA256 for local raw artifact path: {path}"
            )
            continue
        normalized_expected = str(expected).strip().lower()
        if len(normalized_expected) != 64 or any(
            char not in "0123456789abcdef" for char in normalized_expected
        ):
            issues.append(
                f"{context}.raw_artifact_sha256 must be a 64-character hex SHA256 for {path}"
            )
            continue

        local_path = Path(path).expanduser()
        if not local_path.is_file():
            continue
        actual = _sha256_file(local_path)
        if normalized_expected != actual:
            issues.append(
                f"{context}.raw_artifact_sha256 mismatch for {path}: "
                f"expected {normalized_expected}, actual {actual}"
            )
    return issues


def _validate_repo_relative_existing_paths(
    paths: list[str],
    *,
    context: str,
) -> list[str]:
    issues: list[str] = []
    repo_root = REPO_ROOT.resolve(strict=True)
    for path in paths:
        if not _is_non_empty_string(path):
            issues.append(f"{context} must be a non-empty repo-relative path: {path!r}")
            continue
        if path != path.strip():
            issues.append(
                f"{context} must not contain leading or trailing whitespace: {path!r}"
            )
            continue

        candidate = PurePosixPath(path)
        if candidate.is_absolute():
            issues.append(f"{context} must be repo-relative: {path}")
            continue
        parts = path.split("/")
        if any(part in ("", ".", "..") for part in parts):
            issues.append(
                f"{context} must be a normal repo-relative path without empty, '.', "
                f"or '..' components: {path}"
            )
            continue

        repo_path = REPO_ROOT.joinpath(*parts)
        try:
            resolved = repo_path.resolve(strict=True)
        except FileNotFoundError:
            issues.append(f"{context} repo-relative path does not exist: {path}")
            continue

        if resolved != repo_root and repo_root not in resolved.parents:
            issues.append(
                f"{context} repo-relative path resolves outside the repo: {path}"
            )
            continue
        if not resolved.is_file():
            issues.append(f"{context} repo-relative path must be a file: {path}")
    return issues


def validate_qwen_eval_repro_gate(data: Mapping[str, Any]) -> list[str]:
    """Return validation issues for the Qwen eval reproduction gate."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("gate schema_version must be 1")
    if data.get("milestone") != "M1":
        issues.append("gate milestone must be M1")
    if data.get("gate_id") != "task072_qwen_eval_repro_gate_s1":
        issues.append("gate_id must be task072_qwen_eval_repro_gate_s1")
    if data.get("super3_template_consistency_is_sufficient") is not False:
        issues.append(
            "super3_template_consistency_is_sufficient must be false; "
            "Qwen checkpoint/tokenizer reproduction evidence is required"
        )

    reference_model = data.get("reference_model")
    if not _is_mapping(reference_model):
        issues.append("reference_model must be a mapping")
    else:
        for field in REQUIRED_REFERENCE_MODEL_FIELDS:
            if field not in reference_model:
                issues.append(f"reference_model missing required field {field!r}")
        source_model = reference_model.get("source_model")
        if not _is_non_empty_string(source_model) or "Qwen" not in source_model:
            issues.append("reference_model.source_model must name a Qwen model")
        if reference_model.get("qwen_first") is not True:
            issues.append("reference_model.qwen_first must be true")
        for field in (
            "local_model_path",
            "tokenizer_reference",
            "chat_template_reference",
        ):
            if field in reference_model and not _is_non_empty_string(
                reference_model[field]
            ):
                issues.append(f"reference_model.{field} must be a non-empty string")

    eval_path = data.get("intended_eval_path")
    if not _is_mapping(eval_path):
        issues.append("intended_eval_path must be a mapping")
    else:
        for field in REQUIRED_EVAL_PATH_FIELDS:
            if field not in eval_path:
                issues.append(f"intended_eval_path missing required field {field!r}")
        if eval_path.get("endpoint_type") != "openai_chat_completions":
            issues.append(
                "intended_eval_path.endpoint_type must be openai_chat_completions"
            )
        if eval_path.get("chat_route") != "/v1/chat/completions":
            issues.append(
                "intended_eval_path.chat_route must be /v1/chat/completions"
            )
        if eval_path.get("completions_route") != "/v1/completions":
            issues.append(
                "intended_eval_path.completions_route must be /v1/completions"
            )
        issues.extend(
            _validate_chat_template_kwargs(
                eval_path.get("chat_template_kwargs"),
                context="intended_eval_path.chat_template_kwargs",
            )
        )

    source_manifests = data.get("source_manifests")
    if (
        not isinstance(source_manifests, list)
        or not source_manifests
        or not all(_is_non_empty_string(path) for path in source_manifests)
    ):
        issues.append("source_manifests must be non-empty strings")
    else:
        issues.extend(
            _validate_repo_relative_existing_paths(
                list(source_manifests),
                context="source_manifests",
            )
        )

    evidence_records = data.get("evidence_records")
    valid_evidence_count = 0
    if not isinstance(evidence_records, list) or not evidence_records:
        issues.append("evidence_records must be a non-empty list")
    else:
        seen: set[str] = set()
        for index, record in enumerate(evidence_records):
            prefix = f"evidence_records[{index}]"
            if not isinstance(record, Mapping):
                issues.append(f"{prefix} must be a mapping")
                continue
            for field in REQUIRED_EVIDENCE_FIELDS:
                if field not in record:
                    issues.append(f"{prefix} missing required field {field!r}")
            source_manifest = record.get("source_manifest")
            if not _is_non_empty_string(source_manifest):
                issues.append(f"{prefix}.source_manifest must be a non-empty string")
            else:
                issues.extend(
                    _validate_repo_relative_existing_paths(
                        [str(source_manifest)],
                        context=f"{prefix}.source_manifest",
                    )
                )
            evidence_id = record.get("evidence_id")
            if _is_non_empty_string(evidence_id):
                if evidence_id in seen:
                    issues.append(f"{prefix} duplicate evidence_id {evidence_id!r}")
                seen.add(str(evidence_id))
            else:
                issues.append(f"{prefix}.evidence_id must be a non-empty string")
            if "Qwen" not in str(record.get("model_id", "")):
                issues.append(f"{prefix}.model_id must name a Qwen model")
            if record.get("endpoint_type") != "openai_chat_completions":
                issues.append(
                    f"{prefix}.endpoint_type must be openai_chat_completions"
                )
            if record.get("route") != "/v1/chat/completions":
                issues.append(f"{prefix}.route must be /v1/chat/completions")
            issues.extend(
                _validate_chat_template_kwargs(
                    record.get("chat_template_kwargs"),
                    context=f"{prefix}.chat_template_kwargs",
                )
            )
            if not _is_positive_int(record.get("max_generation_tokens")):
                issues.append(f"{prefix}.max_generation_tokens must be positive int")
            raw_paths = record.get("raw_artifact_paths")
            issues.extend(
                validate_raw_artifact_paths(
                    raw_paths,
                    context=f"{prefix}.raw_artifact_paths",
                )
            )
            issues.extend(
                validate_local_raw_artifact_fingerprints(
                    raw_paths,
                    record.get("raw_artifact_sha256"),
                    context=prefix,
                )
            )
            if isinstance(raw_paths, list) and any(
                isinstance(path, str) and is_remote_artifact_reference(path)
                for path in raw_paths
            ):
                issues.extend(
                    _validate_remote_artifact_check(
                        record.get("remote_artifact_check"),
                        context=f"{prefix}.remote_artifact_check",
                        requires_pm_verified=True,
                    )
                )
            if not _is_mapping(record.get("baseline_numbers")):
                issues.append(f"{prefix}.baseline_numbers must be a mapping")
            if record.get("gate_status") in VALID_EVIDENCE_STATUSES:
                valid_evidence_count += 1

    if valid_evidence_count == 0:
        issues.append(
            "at least one evidence record must be a valid Qwen reproduction smoke"
        )

    invalid_findings = data.get("invalid_task_findings")
    seen_issue_types: set[str] = set()
    if not isinstance(invalid_findings, list) or not invalid_findings:
        issues.append("invalid_task_findings must be a non-empty list")
    else:
        for index, finding in enumerate(invalid_findings):
            prefix = f"invalid_task_findings[{index}]"
            if not isinstance(finding, Mapping):
                issues.append(f"{prefix} must be a mapping")
                continue
            for field in REQUIRED_INVALID_FINDING_FIELDS:
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
            unknown = set(issue_types) - VALID_INVALID_FINDING_TYPES
            if unknown:
                issues.append(f"{prefix}.issue_types unknown values: {sorted(unknown)}")
            seen_issue_types.update(str(item) for item in issue_types)
    missing_issue_types = VALID_INVALID_FINDING_TYPES - seen_issue_types
    if missing_issue_types:
        issues.append(
            "invalid_task_findings must cover issue types: "
            f"{sorted(missing_issue_types)}"
        )

    blockers = data.get("runtime_blockers")
    if not isinstance(blockers, list):
        issues.append("runtime_blockers must be a list")
    else:
        for index, blocker in enumerate(blockers):
            prefix = f"runtime_blockers[{index}]"
            if not isinstance(blocker, Mapping):
                issues.append(f"{prefix} must be a mapping")
                continue
            for field in ("blocker_id", "status", "probe_commands", "impact"):
                if field not in blocker:
                    issues.append(f"{prefix} missing required field {field!r}")
            commands = blocker.get("probe_commands")
            if (
                not isinstance(commands, list)
                or not commands
                or not all(_is_non_empty_string(command) for command in commands)
            ):
                issues.append(f"{prefix}.probe_commands must be non-empty strings")
    return issues


def load_qwen_eval_repro_gate(path: Path | None = None) -> JsonDict:
    """Load the Qwen eval reproduction gate, raising on invalid shape."""
    target = path or QWEN_EVAL_REPRO_GATE_PATH
    data = _load_yaml(target)
    issues = validate_qwen_eval_repro_gate(data)
    if issues:
        raise ValueError(
            f"{target}: invalid Qwen eval reproduction gate:\n- "
            + "\n- ".join(issues)
        )
    return data


def qwen_repro_evidence_by_benchmark(
    data: Mapping[str, Any] | None = None,
) -> dict[str, list[JsonDict]]:
    """Group valid Qwen reproduction evidence by benchmark id."""
    source = data if data is not None else load_qwen_eval_repro_gate()
    grouped: dict[str, list[JsonDict]] = {}
    for record in source["evidence_records"]:
        if record["gate_status"] not in VALID_EVIDENCE_STATUSES:
            continue
        grouped.setdefault(str(record["benchmark_id"]), []).append(dict(record))
    return {
        benchmark_id: sorted(rows, key=lambda row: row["evidence_id"])
        for benchmark_id, rows in sorted(grouped.items())
    }


def format_qwen_eval_repro_gate_report(
    data: Mapping[str, Any] | None = None,
) -> str:
    """Render a compact human-readable gate report."""
    source = data if data is not None else load_qwen_eval_repro_gate()
    model = source["reference_model"]["source_model"]
    lines = [
        f"# Qwen eval reproduction gate: {source['gate_id']}",
        "",
        f"Reference model: `{model}`",
        "Super3 template consistency sufficient: `false`",
        "",
        "## Valid Qwen Evidence",
    ]
    for record in sorted(source["evidence_records"], key=lambda row: row["evidence_id"]):
        lines.append(
            f"- `{record['benchmark_id']}` via `{record['route']}`: "
            f"{record['evidence_id']} ({record['gate_status']}, "
            f"max_generation_tokens={record['max_generation_tokens']})"
        )

    lines.extend(["", "## Invalid Legacy Surfaces"])
    for finding in sorted(
        source["invalid_task_findings"], key=lambda row: row["finding_id"]
    ):
        lines.append(
            f"- `{finding['benchmark_id']}`: "
            f"{', '.join(finding['issue_types'])}"
        )

    if source.get("runtime_blockers"):
        lines.extend(["", "## Runtime Blockers"])
        for blocker in source["runtime_blockers"]:
            lines.append(f"- `{blocker['blocker_id']}`: {blocker['status']}")
    return "\n".join(lines) + "\n"


__all__ = [
    "QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS",
    "QWEN_EVAL_REPRO_GATE_PATH",
    "VALID_ARTIFACT_CHECK_STATUSES",
    "VALID_EVIDENCE_STATUSES",
    "VALID_INVALID_FINDING_TYPES",
    "format_qwen_eval_repro_gate_report",
    "is_remote_artifact_reference",
    "load_qwen_eval_repro_gate",
    "qwen_repro_evidence_by_benchmark",
    "validate_local_raw_artifact_fingerprints",
    "validate_raw_artifact_paths",
    "validate_qwen_eval_repro_gate",
]
