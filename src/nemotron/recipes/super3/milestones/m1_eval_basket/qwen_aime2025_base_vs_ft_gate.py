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
import re
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
QWEN_V11_EXPORT_LOAD_CANARY_PROMPTS_PATH = Path(__file__).with_name(
    "qwen_v11_export_load_canary_prompts.yaml"
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
VALID_V11_CANARY_PROMPT_SET_ID = "qwen_v11_non_aime_export_load_canary_v1"
VALID_CANARY_DENOMINATOR_POLICY = "all_canary_prompts"
FINAL_ANSWER_RE = re.compile(
    r"\\boxed\{([^{}]+)\}|Final\s+Answer\s*:\s*\\boxed\{([^{}]+)\}|"
    r"Final\s+Answer\s*:\s*([A-Za-z0-9.+\\-_/ ]+)",
    re.IGNORECASE,
)
CODE_NOISE_RE = re.compile(
    r"(HaveBeenCalledWith|HTMLElement|SharedPreferences|ReactDOM|"
    r"Exception|QObject|addWidget|InputBorder|LayoutInflater|"
    r"BaseEntity|SelectList|onResponse|get[A-Za-z]+|set[A-Za-z]+)"
)
SCRIPT_NOISE_PATTERNS = (
    ("cjk", re.compile(r"[\u4e00-\u9fff]")),
    ("kana", re.compile(r"[\u3040-\u30ff]")),
    ("hangul", re.compile(r"[\uac00-\ud7af]")),
    ("arabic", re.compile(r"[\u0600-\u06ff]")),
    ("hebrew", re.compile(r"[\u0590-\u05ff]")),
    ("thai", re.compile(r"[\u0e00-\u0e7f]")),
    ("cyrillic", re.compile(r"[\u0400-\u04ff]")),
)


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


@dataclass(frozen=True)
class ExportLoadCanaryDecision:
    """Pre-AIME export-load canary decision for future V11 artifacts."""

    status: str
    passed: bool
    checked_prompt_ids: tuple[str, ...]
    failed_prompt_ids: tuple[str, ...] = ()
    missing_prompt_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: JsonDict = field(default_factory=dict)

    def to_jsonable(self) -> JsonDict:
        return {
            "status": self.status,
            "passed": self.passed,
            "checked_prompt_ids": list(self.checked_prompt_ids),
            "failed_prompt_ids": list(self.failed_prompt_ids),
            "missing_prompt_ids": list(self.missing_prompt_ids),
            "reasons": list(self.reasons),
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


def _as_non_empty_string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or not value:
        return None
    if not all(_is_non_empty_string(item) for item in value):
        return None
    return [str(item) for item in value]


def _normalize_final_answer(value: Any) -> str:
    text = str(value).strip().lower()
    text = text.replace("\\boxed", "")
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"[^a-z0-9.+\\-_/]+", "", text)
    return text


def _extract_final_answer(text: str) -> str | None:
    for match in FINAL_ANSWER_RE.finditer(text):
        for group in match.groups():
            if group and group.strip():
                return group.strip()
    return None


def _script_hits(text: str) -> tuple[str, ...]:
    return tuple(name for name, pattern in SCRIPT_NOISE_PATTERNS if pattern.search(text))


def _has_mixed_script_or_code_noise(text: str) -> bool:
    return len(_script_hits(text)) >= 3 or len(CODE_NOISE_RE.findall(text)) >= 2


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


def validate_v11_canary_prompt_set(data: Mapping[str, Any]) -> list[str]:
    """Validate the synthetic non-AIME V11 canary prompt set."""
    issues: list[str] = []
    if data.get("schema_version") != 1:
        issues.append("canary prompt set schema_version must be 1")
    if data.get("prompt_set_id") != VALID_V11_CANARY_PROMPT_SET_ID:
        issues.append(
            f"canary prompt_set_id must be {VALID_V11_CANARY_PROMPT_SET_ID!r}"
        )

    confirmation = data.get("non_aime_non_train_confirmation")
    if not isinstance(confirmation, Mapping):
        issues.append("non_aime_non_train_confirmation must be a mapping")
    else:
        for key in (
            "synthetic_prompts_only",
            "excludes_aime2025",
            "excludes_training_rows",
            "review_only_not_trainable",
            "no_aime2025_prompt_or_label_text",
        ):
            if confirmation.get(key) is not True:
                issues.append(f"non_aime_non_train_confirmation.{key} must be true")

    contract = data.get("generation_contract")
    if not isinstance(contract, Mapping):
        issues.append("generation_contract must be a mapping")
    else:
        if contract.get("endpoint_type") != "openai_chat_completions":
            issues.append("generation_contract.endpoint_type must be openai_chat_completions")
        if contract.get("route") != "/v1/chat/completions":
            issues.append("generation_contract.route must be /v1/chat/completions")
        if not _is_positive_int(contract.get("max_tokens")):
            issues.append("generation_contract.max_tokens must be a positive int")
        for field_name in ("temperature", "top_p"):
            if not _is_number(contract.get(field_name)):
                issues.append(f"generation_contract.{field_name} must be numeric")
        kwargs = contract.get("chat_template_kwargs")
        if not isinstance(kwargs, Mapping):
            issues.append("generation_contract.chat_template_kwargs must be a mapping")
        else:
            for key, expected in QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS.items():
                if kwargs.get(key) is not expected:
                    issues.append(
                        "generation_contract.chat_template_kwargs."
                        f"{key} must be {expected!s}"
                    )

    prompts = data.get("prompts")
    if not isinstance(prompts, list) or not prompts:
        issues.append("prompts must be a non-empty list")
        return issues

    seen_prompt_ids: set[str] = set()
    for index, prompt in enumerate(prompts, 1):
        context = f"prompts[{index}]"
        if not isinstance(prompt, Mapping):
            issues.append(f"{context} must be a mapping")
            continue
        prompt_id = prompt.get("id")
        if not _is_non_empty_string(prompt_id):
            issues.append(f"{context}.id must be a non-empty string")
        elif prompt_id in seen_prompt_ids:
            issues.append(f"{context}.id {prompt_id!r} is duplicated")
        else:
            seen_prompt_ids.add(str(prompt_id))
        for field_name in ("category", "prompt", "expected_answer"):
            if not _is_non_empty_string(prompt.get(field_name)):
                issues.append(f"{context}.{field_name} must be a non-empty string")
        prompt_text = str(prompt.get("prompt") or "").lower()
        if "aime" in prompt_text:
            issues.append(f"{context}.prompt must not contain AIME text")
    return issues


def validate_v11_artifact_retention_schema(
    schema: Mapping[str, Any],
    *,
    context: str = "v11_artifact_retention_schema",
) -> list[str]:
    """Validate required full-completion/debug-transcript retention fields."""
    issues: list[str] = []
    if schema.get("required_for_aime_comparison") is not True:
        issues.append(f"{context}.required_for_aime_comparison must be true")
    if schema.get("usage") != "review_only_not_trainable":
        issues.append(f"{context}.usage must be review_only_not_trainable")

    required_files = _as_non_empty_string_list(schema.get("required_files"))
    if required_files is None:
        issues.append(f"{context}.required_files must be non-empty strings")
    else:
        for file_name in ("full_completions.jsonl", "completion_retention_manifest.json"):
            if file_name not in required_files:
                issues.append(f"{context}.required_files must include {file_name!r}")

    result_fields = _as_non_empty_string_list(
        schema.get("results_jsonl_required_fields")
    )
    if result_fields is None:
        issues.append(
            f"{context}.results_jsonl_required_fields must be non-empty strings"
        )
    else:
        for field_name in ("response_text_sha256", "response_text_ref", "response_tail"):
            if field_name not in result_fields:
                issues.append(
                    f"{context}.results_jsonl_required_fields must include {field_name!r}"
                )

    completion_fields = _as_non_empty_string_list(
        schema.get("full_completions_jsonl_required_fields")
    )
    if completion_fields is None:
        issues.append(
            f"{context}.full_completions_jsonl_required_fields must be non-empty strings"
        )
    else:
        for field_name in ("response_text", "response_text_sha256", "prompt_sha256"):
            if field_name not in completion_fields:
                issues.append(
                    f"{context}.full_completions_jsonl_required_fields must include "
                    f"{field_name!r}"
                )

    manifest_fields = _as_non_empty_string_list(schema.get("manifest_required_fields"))
    if manifest_fields is None:
        issues.append(f"{context}.manifest_required_fields must be non-empty strings")
    else:
        for field_name in (
            "review_only_not_trainable",
            "artifact_sha256",
            "generation_config",
        ):
            if field_name not in manifest_fields:
                issues.append(
                    f"{context}.manifest_required_fields must include {field_name!r}"
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

    canary = data.get("v11_pre_aime_export_load_canary")
    if not isinstance(canary, Mapping):
        issues.append("v11_pre_aime_export_load_canary must be a mapping")
    else:
        if canary.get("required_before_aime_comparison") is not True:
            issues.append(
                "v11_pre_aime_export_load_canary.required_before_aime_comparison "
                "must be true"
            )
        if canary.get("prompt_set_id") != VALID_V11_CANARY_PROMPT_SET_ID:
            issues.append(
                "v11_pre_aime_export_load_canary.prompt_set_id must be "
                f"{VALID_V11_CANARY_PROMPT_SET_ID!r}"
            )
        for field_name in ("prompt_set_path", "prompt_source"):
            if not _is_non_empty_string(canary.get(field_name)):
                issues.append(
                    f"v11_pre_aime_export_load_canary.{field_name} must be "
                    "a non-empty string"
                )
        if canary.get("endpoint_type") != "openai_chat_completions":
            issues.append(
                "v11_pre_aime_export_load_canary.endpoint_type must be "
                "openai_chat_completions"
            )
        if canary.get("route") != "/v1/chat/completions":
            issues.append("v11_pre_aime_export_load_canary.route must be /v1/chat/completions")
        if canary.get("denominator_policy") != VALID_CANARY_DENOMINATOR_POLICY:
            issues.append(
                "v11_pre_aime_export_load_canary.denominator_policy must be "
                f"{VALID_CANARY_DENOMINATOR_POLICY!r}"
            )
        if not _is_positive_int(canary.get("max_tokens")):
            issues.append("v11_pre_aime_export_load_canary.max_tokens must be a positive int")
        for field_name in ("temperature", "top_p"):
            if not _is_number(canary.get(field_name)):
                issues.append(f"v11_pre_aime_export_load_canary.{field_name} must be numeric")
        kwargs = canary.get("chat_template_kwargs")
        if not isinstance(kwargs, Mapping):
            issues.append(
                "v11_pre_aime_export_load_canary.chat_template_kwargs must be a mapping"
            )
        else:
            for key, expected in QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS.items():
                if kwargs.get(key) is not expected:
                    issues.append(
                        "v11_pre_aime_export_load_canary.chat_template_kwargs."
                        f"{key} must be {expected!s}"
                    )
        if _as_non_empty_string_list(canary.get("pass_conditions")) is None:
            issues.append(
                "v11_pre_aime_export_load_canary.pass_conditions must be "
                "non-empty strings"
            )

    retention_schema = data.get("v11_artifact_retention_schema")
    if not isinstance(retention_schema, Mapping):
        issues.append("v11_artifact_retention_schema must be a mapping")
    else:
        issues.extend(validate_v11_artifact_retention_schema(retention_schema))
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


def load_v11_canary_prompt_set(path: Path | None = None) -> JsonDict:
    """Load and validate the synthetic non-AIME V11 canary prompt set."""
    target = path or QWEN_V11_EXPORT_LOAD_CANARY_PROMPTS_PATH
    data = _load_yaml(target)
    issues = validate_v11_canary_prompt_set(data)
    if issues:
        raise ValueError(
            f"{target}: invalid Qwen V11 export-load canary prompt set:\n- "
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


def evaluate_v11_export_load_canary(
    rows: Sequence[Mapping[str, Any]],
    *,
    prompt_set: Mapping[str, Any] | None = None,
) -> ExportLoadCanaryDecision:
    """Evaluate future V11 non-AIME export-load canary rows.

    This is an offline artifact decision helper. It does not launch endpoints or
    run generation. All rows are expected to come from a task-owned canary run.
    """
    canary = prompt_set or load_v11_canary_prompt_set()
    prompt_issues = validate_v11_canary_prompt_set(canary)
    if prompt_issues:
        raise ValueError("invalid canary prompt set:\n- " + "\n- ".join(prompt_issues))

    contract = canary["generation_contract"]
    max_tokens = int(contract["max_tokens"])
    expected_prompts = {prompt["id"]: prompt for prompt in canary["prompts"]}
    row_by_prompt_id: dict[str, Mapping[str, Any]] = {}
    duplicate_prompt_ids: list[str] = []
    for row in rows:
        prompt_id = str(row.get("prompt_id") or row.get("sample_id") or row.get("id") or "")
        if not prompt_id:
            continue
        if prompt_id in row_by_prompt_id:
            duplicate_prompt_ids.append(prompt_id)
            continue
        row_by_prompt_id[prompt_id] = row

    missing_prompt_ids: list[str] = []
    failed_prompt_ids: list[str] = []
    reasons: list[str] = []
    diagnostics_by_prompt: dict[str, JsonDict] = {}

    for prompt_id, prompt in expected_prompts.items():
        row = row_by_prompt_id.get(prompt_id)
        if row is None:
            missing_prompt_ids.append(prompt_id)
            reasons.append(f"{prompt_id}: missing canary row")
            continue

        row_reasons: list[str] = []
        status = str(row.get("status") or "missing")
        content = str(
            row.get("response_text")
            or row.get("content")
            or row.get("message_content")
            or ""
        )
        usage = row.get("usage")
        completion_tokens = None
        if isinstance(usage, Mapping):
            completion_tokens = usage.get("completion_tokens")
        if completion_tokens is None and "completion_tokens" in row:
            completion_tokens = row.get("completion_tokens")

        if status != "ok":
            row_reasons.append(f"status is {status!r}, expected 'ok'")
        if not content.strip():
            row_reasons.append("response content is empty")
        if row.get("reasoning_content") and not content.strip():
            row_reasons.append("response is reasoning-content-only")
        if not _is_positive_int(completion_tokens):
            row_reasons.append("completion token count is missing or invalid")
        elif int(completion_tokens) > max_tokens:
            row_reasons.append(
                f"completion token count {completion_tokens} exceeds {max_tokens}"
            )

        extracted = _extract_final_answer(content)
        expected_answer = prompt["expected_answer"]
        if extracted is None:
            row_reasons.append("missing final-answer marker")
        elif _normalize_final_answer(extracted) != _normalize_final_answer(expected_answer):
            row_reasons.append(
                f"final answer {extracted!r} does not match {expected_answer!r}"
            )
        if _has_mixed_script_or_code_noise(content):
            row_reasons.append("mixed-script/code-token degeneration signature")

        diagnostics_by_prompt[prompt_id] = {
            "status": status,
            "completion_tokens": completion_tokens,
            "extracted_final_answer": extracted,
            "expected_answer": expected_answer,
            "script_hits": list(_script_hits(content)),
            "content_chars": len(content),
        }
        if row_reasons:
            failed_prompt_ids.append(prompt_id)
            reasons.extend(f"{prompt_id}: {reason}" for reason in row_reasons)

    if duplicate_prompt_ids:
        reasons.append(
            "duplicate canary rows for prompt ids: "
            + ", ".join(sorted(set(duplicate_prompt_ids)))
        )
        failed_prompt_ids.extend(sorted(set(duplicate_prompt_ids)))

    passed = not missing_prompt_ids and not failed_prompt_ids
    return ExportLoadCanaryDecision(
        status="pass" if passed else "fail",
        passed=passed,
        checked_prompt_ids=tuple(sorted(row_by_prompt_id)),
        failed_prompt_ids=tuple(sorted(set(failed_prompt_ids))),
        missing_prompt_ids=tuple(missing_prompt_ids),
        reasons=tuple(reasons),
        diagnostics={
            "prompt_set_id": canary["prompt_set_id"],
            "denominator_policy": VALID_CANARY_DENOMINATOR_POLICY,
            "expected_prompt_count": len(expected_prompts),
            "observed_prompt_count": len(row_by_prompt_id),
            "duplicate_prompt_ids": sorted(set(duplicate_prompt_ids)),
            "by_prompt": diagnostics_by_prompt,
        },
    )


def evaluate_v11_base_vs_ft_gate(
    *,
    base_score: Aime2025Score | None,
    ft_score: Aime2025Score | None,
    canary_decision: ExportLoadCanaryDecision | None,
) -> BaseVsFtDecision:
    """Compare V11 FT against base only after the export-load canary passes."""
    if canary_decision is None:
        return BaseVsFtDecision(
            status="blocked_missing_export_load_canary",
            base_score=base_score,
            ft_score=ft_score,
            delta_exact_normalized_accuracy=None,
            reasons=(
                "V11 FT artifact must pass the non-AIME export-load canary "
                "before same-harness AIME2025 comparison is requested",
            ),
            diagnostics={
                "canary_required": True,
                "ft_judged": False,
            },
        )
    if not canary_decision.passed:
        return BaseVsFtDecision(
            status="blocked_failed_export_load_canary",
            base_score=base_score,
            ft_score=ft_score,
            delta_exact_normalized_accuracy=None,
            reasons=(
                "V11 FT artifact failed the non-AIME export-load canary; "
                "do not run or judge AIME2025 comparison",
                *canary_decision.reasons,
            ),
            diagnostics={
                "canary_required": True,
                "ft_judged": False,
                "canary": canary_decision.to_jsonable(),
            },
        )
    decision = evaluate_base_vs_ft_gate(base_score=base_score, ft_score=ft_score)
    diagnostics = dict(decision.diagnostics)
    diagnostics["canary_required"] = True
    diagnostics["canary"] = canary_decision.to_jsonable()
    return BaseVsFtDecision(
        status=decision.status,
        base_score=decision.base_score,
        ft_score=decision.ft_score,
        delta_exact_normalized_accuracy=decision.delta_exact_normalized_accuracy,
        reasons=decision.reasons,
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
    "ExportLoadCanaryDecision",
    "PROTOCOL_MATCH_FIELDS",
    "QWEN_AIME2025_BASE_VS_FT_GATE_PATH",
    "QWEN_V11_EXPORT_LOAD_CANARY_PROMPTS_PATH",
    "VALID_CANARY_DENOMINATOR_POLICY",
    "VALID_DENOMINATOR_POLICY",
    "VALID_SCORER",
    "VALID_V11_CANARY_PROMPT_SET_ID",
    "assert_same_harness",
    "evaluate_base_vs_ft_gate",
    "evaluate_v11_base_vs_ft_gate",
    "evaluate_v11_export_load_canary",
    "format_base_vs_ft_report",
    "load_base_vs_ft_gate_config",
    "load_jsonl",
    "load_v11_canary_prompt_set",
    "normalize_aime2025_rows",
    "validate_aime2025_protocol",
    "validate_base_vs_ft_gate_config",
    "validate_v11_artifact_retention_schema",
    "validate_v11_canary_prompt_set",
]
