# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Corrected AIME2025 base-vs-FT non-regression gate for Qwen.

The gate is intentionally narrower than the general M1 promotion gate: a
fine-tuned Qwen checkpoint cannot be judged until the matching base checkpoint
has a score from the same corrected AIME2025 harness. Parsed-rate improvements
are surfaced as diagnostics only; the promotion decision is based on
exact-normalized accuracy over the full denominator.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_eval_repro_gate import (
    QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS,
)

JsonDict = dict[str, Any]

QWEN_AIME2025_BASE_VS_FT_GATE_PATH = Path(__file__).with_name(
    "qwen_aime2025_base_vs_ft_gate.yaml"
)

REQUIRED_PROTOCOL_FIELDS = (
    "model_family",
    "benchmark_id",
    "endpoint_type",
    "route",
    "tokenizer_chat_template",
    "chat_template_kwargs",
    "prompt_set_id",
    "prompt_source",
    "repeats_per_problem",
    "max_tokens",
    "temperature",
    "top_p",
    "parser",
    "scorer",
    "denominator_policy",
)
PROTOCOL_MATCH_FIELDS = (
    "model_family",
    "benchmark_id",
    "endpoint_type",
    "route",
    "tokenizer_chat_template",
    "chat_template_kwargs",
    "prompt_set_id",
    "prompt_source",
    "repeats_per_problem",
    "max_tokens",
    "temperature",
    "top_p",
    "parser",
    "scorer",
    "denominator_policy",
)
VALID_DENOMINATOR_POLICY = "all_requests"
VALID_SCORER = "exact_normalized_boxed_or_symbolic_answer"


@dataclass(frozen=True)
class Aime2025Score:
    """Normalized AIME2025 score plus diagnostics."""

    model_id: str
    model_path: str
    protocol: JsonDict
    numerator: int
    denominator: int
    exact_normalized_accuracy: float
    parsed_count: int
    parsed_rate: float
    finish_reason_counts: dict[str, int]
    status_counts: dict[str, int]
    per_problem_rows: dict[str, JsonDict]
    artifact_paths: tuple[str, ...] = ()

    def to_jsonable(self) -> JsonDict:
        return {
            "model_id": self.model_id,
            "model_path": self.model_path,
            "protocol": dict(self.protocol),
            "score_normalization": {
                "metric": "exact_normalized_accuracy",
                "numerator": self.numerator,
                "denominator": self.denominator,
                "value": self.exact_normalized_accuracy,
                "denominator_policy": VALID_DENOMINATOR_POLICY,
            },
            "parsed_count": self.parsed_count,
            "parsed_rate": self.parsed_rate,
            "finish_reason_counts": dict(self.finish_reason_counts),
            "status_counts": dict(self.status_counts),
            "per_problem_rows": dict(self.per_problem_rows),
            "artifact_paths": list(self.artifact_paths),
        }


@dataclass(frozen=True)
class BaseVsFtDecision:
    """Decision from comparing one FT score against its same-harness base."""

    status: str
    base_score: Aime2025Score | None
    ft_score: Aime2025Score | None
    delta_exact_normalized_accuracy: float | None
    reasons: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: JsonDict = field(default_factory=dict)

    def to_jsonable(self) -> JsonDict:
        return {
            "status": self.status,
            "delta_exact_normalized_accuracy": self.delta_exact_normalized_accuracy,
            "reasons": list(self.reasons),
            "base_score": self.base_score.to_jsonable() if self.base_score else None,
            "ft_score": self.ft_score.to_jsonable() if self.ft_score else None,
            "diagnostics": dict(self.diagnostics),
        }


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


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _protocol_for_compare(protocol: Mapping[str, Any]) -> JsonDict:
    """Return only the fields that must match between base and FT."""
    return {field: protocol.get(field) for field in PROTOCOL_MATCH_FIELDS}


def _problem_id_from_sample(sample_id: str, fallback_index: int) -> str:
    """Map rows such as ``aime_06_r03`` to ``aime_06``."""
    parts = sample_id.split("_")
    if len(parts) >= 3 and parts[0] == "aime" and parts[1].isdigit():
        return f"aime_{parts[1]}"
    if len(parts) >= 2 and parts[0] == "aime" and parts[1].isdigit():
        return f"aime_{parts[1]}"
    return f"row_{fallback_index:04d}"


def validate_aime2025_protocol(protocol: Mapping[str, Any], *, context: str) -> list[str]:
    """Validate one corrected AIME2025 protocol signature."""
    issues: list[str] = []
    for field_name in REQUIRED_PROTOCOL_FIELDS:
        if field_name not in protocol:
            issues.append(f"{context} missing required field {field_name!r}")
    if protocol.get("benchmark_id") != "aime25":
        issues.append(f"{context}.benchmark_id must be 'aime25'")
    if protocol.get("endpoint_type") != "openai_chat_completions":
        issues.append(f"{context}.endpoint_type must be openai_chat_completions")
    if protocol.get("route") != "/v1/chat/completions":
        issues.append(f"{context}.route must be /v1/chat/completions")
    if protocol.get("denominator_policy") != VALID_DENOMINATOR_POLICY:
        issues.append(f"{context}.denominator_policy must be {VALID_DENOMINATOR_POLICY!r}")
    if protocol.get("scorer") != VALID_SCORER:
        issues.append(f"{context}.scorer must be {VALID_SCORER!r}")
    for field_name in ("model_family", "prompt_set_id", "prompt_source", "parser"):
        if field_name in protocol and not _is_non_empty_string(protocol[field_name]):
            issues.append(f"{context}.{field_name} must be a non-empty string")
    for field_name in ("repeats_per_problem", "max_tokens"):
        if field_name in protocol and not _is_positive_int(protocol[field_name]):
            issues.append(f"{context}.{field_name} must be a positive int")
    for field_name in ("temperature", "top_p"):
        if field_name in protocol and not _is_number(protocol[field_name]):
            issues.append(f"{context}.{field_name} must be numeric")
    kwargs = protocol.get("chat_template_kwargs")
    if not isinstance(kwargs, Mapping):
        issues.append(f"{context}.chat_template_kwargs must be a mapping")
    else:
        for key, expected in QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS.items():
            actual = kwargs.get(key)
            if actual is not expected:
                issues.append(
                    f"{context}.chat_template_kwargs.{key} must be {expected!s}"
                )
    return issues


def validate_base_vs_ft_gate_config(data: Mapping[str, Any]) -> list[str]:
    """Validate the static task243 AIME2025 gate config."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("schema_version must be 1")
    if data.get("gate_id") != "task243_qwen_aime2025_base_vs_ft_eval_gate_s1":
        issues.append("gate_id must be task243_qwen_aime2025_base_vs_ft_eval_gate_s1")
    if data.get("base_score_required") is not True:
        issues.append("base_score_required must be true")
    if data.get("ft_must_be_at_least_base") is not True:
        issues.append("ft_must_be_at_least_base must be true")

    base_model = data.get("base_model")
    if not isinstance(base_model, Mapping):
        issues.append("base_model must be a mapping")
    else:
        for field_name in ("model_id", "checkpoint_path", "tokenizer_path"):
            if not _is_non_empty_string(base_model.get(field_name)):
                issues.append(f"base_model.{field_name} must be a non-empty string")

    protocols = data.get("protocols")
    if not isinstance(protocols, Mapping):
        issues.append("protocols must be a mapping")
    else:
        for protocol_name in ("pilot_smoke", "final_full"):
            protocol = protocols.get(protocol_name)
            if not isinstance(protocol, Mapping):
                issues.append(f"protocols.{protocol_name} must be a mapping")
                continue
            issues.extend(
                validate_aime2025_protocol(
                    protocol,
                    context=f"protocols.{protocol_name}",
                )
            )

    schema = data.get("score_normalization_schema")
    if not isinstance(schema, Mapping):
        issues.append("score_normalization_schema must be a mapping")
    else:
        required_fields = schema.get("required_fields")
        if (
            not isinstance(required_fields, list)
            or not required_fields
            or not all(_is_non_empty_string(field) for field in required_fields)
        ):
            issues.append("score_normalization_schema.required_fields must be non-empty strings")
        for required in (
            "numerator",
            "denominator",
            "parsed_count",
            "finish_reason_counts",
            "per_problem_rows",
            "exact_normalized_accuracy",
        ):
            if isinstance(required_fields, list) and required not in required_fields:
                issues.append(
                    "score_normalization_schema.required_fields must include "
                    f"{required!r}"
                )
    return issues


def load_base_vs_ft_gate_config(path: Path | None = None) -> JsonDict:
    """Load and validate the task243 gate config."""
    target = path or QWEN_AIME2025_BASE_VS_FT_GATE_PATH
    data = _load_yaml(target)
    issues = validate_base_vs_ft_gate_config(data)
    if issues:
        raise ValueError(
            f"{target}: invalid Qwen AIME2025 base-vs-FT gate:\n- "
            + "\n- ".join(issues)
        )
    return data


def load_jsonl(path: Path) -> list[JsonDict]:
    """Load JSONL result rows."""
    rows: list[JsonDict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(item)
    return rows


def normalize_aime2025_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    model_id: str,
    model_path: str,
    protocol: Mapping[str, Any],
    artifact_paths: Iterable[str] = (),
) -> Aime2025Score:
    """Normalize corrected AIME2025 result rows into a promotion score.

    The denominator is all request rows, including unparsed, length-capped, and
    error rows. This prevents parser coverage or short completions from being
    mistaken for accuracy improvement.
    """
    protocol_issues = validate_aime2025_protocol(protocol, context="protocol")
    if protocol_issues:
        raise ValueError("invalid AIME2025 protocol:\n- " + "\n- ".join(protocol_issues))
    if not _is_non_empty_string(model_id):
        raise ValueError("model_id must be a non-empty string")
    if not _is_non_empty_string(model_path):
        raise ValueError("model_path must be a non-empty string")
    if not rows:
        raise ValueError("AIME2025 score requires at least one result row")

    numerator = 0
    parsed_count = 0
    finish_reasons: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    per_problem: dict[str, JsonDict] = defaultdict(
        lambda: {
            "rows": 0,
            "correct_rows": 0,
            "parsed_rows": 0,
            "finish_reason_counts": {},
            "sample_ids": [],
        }
    )

    for index, row in enumerate(rows, 1):
        if not isinstance(row, Mapping):
            raise ValueError(f"AIME2025 result row {index} must be a mapping")
        if row.get("task") not in (None, "aime25"):
            raise ValueError(f"AIME2025 result row {index} has non-aime task {row.get('task')!r}")

        sample_id = str(row.get("sample_id") or f"row_{index:04d}")
        problem_id = str(row.get("problem_id") or _problem_id_from_sample(sample_id, index))
        correct = bool(row.get("correct"))
        parsed = bool(row.get("parsed"))
        finish_reason = str(row.get("finish_reason") or "missing")
        status = str(row.get("status") or "missing")

        numerator += int(correct)
        parsed_count += int(parsed)
        finish_reasons[finish_reason] += 1
        statuses[status] += 1

        bucket = per_problem[problem_id]
        bucket["rows"] += 1
        bucket["correct_rows"] += int(correct)
        bucket["parsed_rows"] += int(parsed)
        bucket["sample_ids"].append(sample_id)
        finish_counts = Counter(bucket["finish_reason_counts"])
        finish_counts[finish_reason] += 1
        bucket["finish_reason_counts"] = dict(sorted(finish_counts.items()))

    denominator = len(rows)
    return Aime2025Score(
        model_id=model_id,
        model_path=model_path,
        protocol=dict(protocol),
        numerator=numerator,
        denominator=denominator,
        exact_normalized_accuracy=numerator / denominator,
        parsed_count=parsed_count,
        parsed_rate=parsed_count / denominator,
        finish_reason_counts=dict(sorted(finish_reasons.items())),
        status_counts=dict(sorted(statuses.items())),
        per_problem_rows=dict(sorted(per_problem.items())),
        artifact_paths=tuple(str(path) for path in artifact_paths),
    )


def assert_same_harness(base_score: Aime2025Score, ft_score: Aime2025Score) -> None:
    """Raise if base and FT scores are not comparable."""
    base_protocol = _protocol_for_compare(base_score.protocol)
    ft_protocol = _protocol_for_compare(ft_score.protocol)
    if base_protocol != ft_protocol:
        mismatches = [
            field
            for field in PROTOCOL_MATCH_FIELDS
            if base_protocol.get(field) != ft_protocol.get(field)
        ]
        raise ValueError(
            "base and FT AIME2025 scores must use the same harness; "
            f"mismatched fields: {', '.join(mismatches)}"
        )


def evaluate_base_vs_ft_gate(
    *,
    base_score: Aime2025Score | None,
    ft_score: Aime2025Score | None,
) -> BaseVsFtDecision:
    """Compare FT against the same-harness base score."""
    if base_score is None:
        return BaseVsFtDecision(
            status="blocked_missing_base",
            base_score=None,
            ft_score=ft_score,
            delta_exact_normalized_accuracy=None,
            reasons=(
                "same-harness base AIME2025 score is mandatory before judging FT",
            ),
            diagnostics={
                "base_score_required": True,
                "ft_judged": False,
            },
        )
    if ft_score is None:
        return BaseVsFtDecision(
            status="blocked_missing_ft",
            base_score=base_score,
            ft_score=None,
            delta_exact_normalized_accuracy=None,
            reasons=("FT AIME2025 score is missing",),
            diagnostics={
                "base_score_required": True,
                "ft_judged": False,
            },
        )

    assert_same_harness(base_score, ft_score)
    delta = ft_score.exact_normalized_accuracy - base_score.exact_normalized_accuracy
    diagnostics = {
        "base_parsed_rate": base_score.parsed_rate,
        "ft_parsed_rate": ft_score.parsed_rate,
        "base_finish_reason_counts": dict(base_score.finish_reason_counts),
        "ft_finish_reason_counts": dict(ft_score.finish_reason_counts),
        "base_denominator": base_score.denominator,
        "ft_denominator": ft_score.denominator,
    }
    if delta < 0:
        return BaseVsFtDecision(
            status="fail_ft_below_base",
            base_score=base_score,
            ft_score=ft_score,
            delta_exact_normalized_accuracy=delta,
            reasons=(
                "FT exact-normalized AIME2025 accuracy is lower than base under the same harness",
            ),
            diagnostics=diagnostics,
        )
    return BaseVsFtDecision(
        status="pass_ft_at_least_base",
        base_score=base_score,
        ft_score=ft_score,
        delta_exact_normalized_accuracy=delta,
        reasons=(
            "FT exact-normalized AIME2025 accuracy is at least base under the same harness",
        ),
        diagnostics=diagnostics,
    )


def format_base_vs_ft_report(decision: BaseVsFtDecision) -> str:
    """Render a compact review report."""
    lines = [
        "# Qwen AIME2025 base-vs-FT gate",
        "",
        f"Status: `{decision.status}`",
    ]
    if decision.delta_exact_normalized_accuracy is not None:
        lines.append(
            "Delta exact-normalized accuracy "
            f"(FT - base): `{decision.delta_exact_normalized_accuracy:+.6f}`"
        )
    lines.extend(["", "## Reasons"])
    for reason in decision.reasons:
        lines.append(f"- {reason}")
    if decision.base_score is not None:
        lines.extend(
            [
                "",
                "## Base",
                (
                    f"- `{decision.base_score.model_id}`: "
                    f"{decision.base_score.numerator}/"
                    f"{decision.base_score.denominator} = "
                    f"{decision.base_score.exact_normalized_accuracy:.6f}"
                ),
                (
                    f"- parsed: {decision.base_score.parsed_count}/"
                    f"{decision.base_score.denominator}; finish reasons: "
                    f"{decision.base_score.finish_reason_counts}"
                ),
            ]
        )
    if decision.ft_score is not None:
        lines.extend(
            [
                "",
                "## Fine-tuned",
                (
                    f"- `{decision.ft_score.model_id}`: "
                    f"{decision.ft_score.numerator}/"
                    f"{decision.ft_score.denominator} = "
                    f"{decision.ft_score.exact_normalized_accuracy:.6f}"
                ),
                (
                    f"- parsed: {decision.ft_score.parsed_count}/"
                    f"{decision.ft_score.denominator}; finish reasons: "
                    f"{decision.ft_score.finish_reason_counts}"
                ),
            ]
        )
    return "\n".join(lines) + "\n"


__all__ = [
    "Aime2025Score",
    "BaseVsFtDecision",
    "PROTOCOL_MATCH_FIELDS",
    "QWEN_AIME2025_BASE_VS_FT_GATE_PATH",
    "VALID_DENOMINATOR_POLICY",
    "VALID_SCORER",
    "assert_same_harness",
    "evaluate_base_vs_ft_gate",
    "format_base_vs_ft_report",
    "load_base_vs_ft_gate_config",
    "load_jsonl",
    "normalize_aime2025_rows",
    "validate_aime2025_protocol",
    "validate_base_vs_ft_gate_config",
]
