# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Per-kind schema validators for the unified data registry index.

Plan §6 W1 / task030 Session 1. The Super3 pipeline today has 9
distinct registry YAML files spread across ``m0_data_env/``,
``m1_rlvr/``, ``m1_swe1/``, ``m1_swe2/``, ``m1_rlhf/``, and
``sandbox_containers/``. Each one is authored by hand and consumed by
its own module's loader. This file declares the *shape* each kind
must hold so a single validation pass can catch drift before a
cluster run wastes a slot.

Six registry kinds are recognised today:

- ``m0_data_registry`` — `m0_data_env/data_registry.yaml` — 11 HF
  datasets backing M0 envs (hf_revision pin + license + contamination
  posture).
- ``m0_environment_registry`` — `m0_data_env/environment_registry.yaml`
  — 12 reward env definitions with verifier + telemetry + health-check
  (math_formal_lean landed Session 2 of task056).
- ``bridge_env_registry`` — `m1_*/[stage]_env_registry.yaml`` — M0 →
  NeMo-Gym mappings per RL stage (RLVR / SWE1 / SWE2 / RLHF).
- ``sif_registry`` — `m1_swe2/swe2_sif_registry.yaml` — SIF filename
  templates for the OpenHands SWE-Bench loop.
- ``pref_data_registry`` — `m1_rlhf/rlhf_pref_data_registry.yaml` —
  preference-data candidate sources (HelpSteer-2 / UltraFeedback / …).
- ``sandbox_image_registry`` —
  `sandbox_containers/sandbox_image_registry.yaml` — code-exec / Lean /
  terminal Dockerfiles + per-env routing (task021 Session 3).

Adding a new kind (e.g., the future M1 eval basket from task019) is a
one-validator addition here + one row in ``unified_index.yaml``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

JsonDict = dict[str, Any]


# Top-level fields every registry must declare for the unified index
# to identify it.
_TOP_LEVEL_REQUIRED = ("schema_version", "milestone")


# Per-kind row schema. Each row of the registry data must carry these
# fields; the validator checks presence (not types) — types stay loose
# so YAML quoting differences don't break validation.
_KIND_SCHEMAS: dict[str, dict[str, Any]] = {
    "m0_data_registry": {
        "rows_key": "datasets",
        "required_row_fields": (
            "id",
            "environment",
            "hf_dataset",
            "hf_split",
            "hf_revision",
            "license",
            "contamination_against",
            "converter",
            "use_stage",
        ),
        "expected_top_level": ("description",),
    },
    "m0_environment_registry": {
        "rows_key": "environments",
        "required_row_fields": (
            "id",
            "family",
            "stage",
            "input_schema",
            "reward",
            "telemetry",
            "health_check",
        ),
        "expected_top_level": ("description",),
    },
    "bridge_env_registry": {
        "rows_key": "envs",
        "required_row_fields": (
            "nemo_gym_env",
            "mix",
            "status",
        ),
        "expected_top_level": ("description",),
    },
    "sif_registry": {
        "rows_key": "sif_sources",
        "required_row_fields": (
            "source",
            "filename_template",
        ),
        "expected_top_level": ("description",),
    },
    "pref_data_registry": {
        "rows_key": "datasets",
        "required_row_fields": (
            "id",
            "hf_dataset",
            "license",
        ),
        "expected_top_level": ("description",),
    },
    "sandbox_image_registry": {
        "rows_key": "images",
        "required_row_fields": (
            "image_id",
            "version_tag",
            "dockerfile_path",
            "target_envs",
        ),
        "expected_top_level": ("description",),
    },
}

KNOWN_KINDS = frozenset(_KIND_SCHEMAS.keys())


# Statuses accepted in any ``bridge_env_registry``. Matches the
# canonical set in ``_bridge_base.KNOWN_STATUSES`` — duplicated here so
# the data-registries layer can validate registries without importing
# the bridge runtime (and the bridge layer doesn't depend on this
# schema module either, keeping the cycle clean).
KNOWN_BRIDGE_STATUSES = frozenset(
    {"active", "m0_missing", "verifier_mismatch", "blocked_external"}
)


def validate_top_level(data: Any, *, kind: str) -> None:
    """Validate the top-level dict shape of a registry YAML."""
    if not isinstance(data, dict):
        raise ValueError(f"{kind} registry must be a YAML mapping at top level")
    for field in _TOP_LEVEL_REQUIRED:
        if field not in data:
            raise ValueError(f"{kind} registry missing top-level {field!r}")
    schema = _KIND_SCHEMAS.get(kind)
    if schema is None:
        raise ValueError(f"unknown registry kind {kind!r}; known: {sorted(KNOWN_KINDS)}")
    rows_key = schema["rows_key"]
    if rows_key not in data:
        raise ValueError(f"{kind} registry missing rows key {rows_key!r}")
    if not isinstance(data[rows_key], list):
        raise ValueError(f"{kind} registry: {rows_key!r} must be a list, got {type(data[rows_key]).__name__}")


def validate_rows(
    data: dict[str, Any],
    *,
    kind: str,
    extra_validators: Iterable[Any] = (),
) -> list[str]:
    """Validate each row against its kind's schema.

    Returns a list of human-readable issue strings. Empty list = clean.
    Callers decide whether to raise on non-empty (CLI mode) or surface
    as warnings (manifest mode).

    *extra_validators* is a sequence of ``callable(row, index) -> str | None``
    — returning a non-empty string flags an issue, returning None passes.
    Used by ``bridge_env_registry`` to check status vocabulary against
    the expected_mixes field declared in the unified index.
    """
    schema = _KIND_SCHEMAS[kind]
    rows = data[schema["rows_key"]]
    required = schema["required_row_fields"]
    issues: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            issues.append(f"{kind}/{index}: row must be a mapping")
            continue
        for field in required:
            if field not in row:
                issues.append(f"{kind}/{index}: missing required field {field!r}")
        for validator in extra_validators:
            verdict = validator(row, index)
            if verdict:
                issues.append(f"{kind}/{index}: {verdict}")
    return issues


def bridge_status_validator(row: JsonDict, index: int) -> str | None:
    """Validate that a bridge_env_registry row's status is in the known
    vocabulary. Returns issue string or None."""
    status = row.get("status")
    if status is not None and status not in KNOWN_BRIDGE_STATUSES:
        return (
            f"status {status!r} not in {sorted(KNOWN_BRIDGE_STATUSES)} — "
            "expected one of the canonical bridge statuses"
        )
    return None


def bridge_mix_validator_factory(expected_mixes: Sequence[str]):
    """Build a row validator that checks ``row['mix']`` is in
    *expected_mixes*. The unified index declares per-bridge-registry
    expected mixes so the schema layer can catch e.g., an RLVR row
    accidentally placed in the SWE1 registry."""
    expected = frozenset(expected_mixes)

    def _validator(row: JsonDict, index: int) -> str | None:
        mix = row.get("mix")
        if mix is None:
            return None  # missing-field check happens via required_row_fields
        if mix not in expected:
            return (
                f"mix {mix!r} not in declared expected_mixes {sorted(expected)}"
            )
        return None

    return _validator


__all__ = [
    "KNOWN_KINDS",
    "KNOWN_BRIDGE_STATUSES",
    "validate_top_level",
    "validate_rows",
    "bridge_status_validator",
    "bridge_mix_validator_factory",
]
