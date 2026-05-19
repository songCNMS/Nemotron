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


def validate_top_level(
    data: Any,
    *,
    kind: str,
    source_path: Any = None,
    strict: bool = True,
) -> None:
    """Validate the top-level dict shape of a registry YAML.

    Two consumer modes match the row-validator split (Session 1 / Session 4):

    - **Audit mode** (default, ``strict=True``): require
      ``schema_version`` + ``milestone`` top-level fields. Used by
      ``unified_index_loader`` so registries declare their version /
      milestone for cross-cut discovery.
    - **Runtime mode** (``strict=False``): only require the kind's
      ``rows_key`` is present + is a list. Used by bridge / M0
      module-local loaders that hard-code the kind and only need the
      data rows — schema_version / milestone are documentation, not
      runtime contract.

    When *source_path* is provided, the YAML path prefixes every error
    message so the offending file is obvious in stack traces.
    """
    prefix = f"{source_path}: " if source_path is not None else ""
    if not isinstance(data, dict):
        raise ValueError(f"{prefix}{kind} registry must be a YAML mapping at top level")
    if strict:
        for field in _TOP_LEVEL_REQUIRED:
            if field not in data:
                raise ValueError(f"{prefix}{kind} registry missing top-level {field!r}")
    schema = _KIND_SCHEMAS.get(kind)
    if schema is None:
        raise ValueError(f"{prefix}unknown registry kind {kind!r}; known: {sorted(KNOWN_KINDS)}")
    rows_key = schema["rows_key"]
    if rows_key not in data:
        raise ValueError(f"{prefix}{kind} registry missing rows key {rows_key!r}")
    if not isinstance(data[rows_key], list):
        raise ValueError(
            f"{prefix}{kind} registry: {rows_key!r} must be a list, "
            f"got {type(data[rows_key]).__name__}"
        )


def validate_rows(
    data: dict[str, Any],
    *,
    kind: str,
    extra_validators: Iterable[Any] = (),
    fail_fast: bool = False,
    source_path: Any = None,
) -> list[str]:
    """Validate each row against its kind's schema.

    Two consumer modes by design (task030 Session 1 + Session 4 decision):

    - **Audit mode** (default, ``fail_fast=False``): collect every issue
      and return as a list. Empty list = clean. Used by
      ``unified_index_loader.validate_unified_index`` so a single
      validation pass surfaces every problem at once.
    - **Runtime mode** (``fail_fast=True``): raise ``ValueError`` on
      first issue with the file path prefixed. Used by bridge / M0
      module-local loaders so a single bad row aborts the prepare step
      immediately rather than emitting partial bad data.

    The shape definitions (``required_row_fields``, ``rows_key``) are
    the *same* in both modes — Session 4 merge of bridge / M0 loaders
    into the schema layer means adding a field to the contract is a
    one-edit change here, not a two-edit (schema + each module).

    *extra_validators* is a sequence of ``callable(row, index) -> str | None``
    — returning a non-empty string flags an issue, returning None passes.
    Used by ``bridge_env_registry`` for status + per-mix validators.
    """
    schema = _KIND_SCHEMAS[kind]
    rows_key = schema["rows_key"]
    rows = data[rows_key]
    required = schema["required_row_fields"]

    # Issue format mirrors the format runtime loaders already emit:
    # `envs[0] missing required field 'status'`. Unified loader (audit)
    # prefixes with the registry id; runtime loader (fail-fast) prefixes
    # with the YAML path via *source_path*.
    issues: list[str] = []

    def _record(issue_body: str) -> None:
        if fail_fast:
            prefix = f"{source_path}: " if source_path is not None else ""
            raise ValueError(f"{prefix}{issue_body}")
        issues.append(issue_body)

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            _record(f"{rows_key}[{index}] row must be a mapping")
            continue
        for field in required:
            if field not in row:
                _record(f"{rows_key}[{index}] missing required field {field!r}")
        for validator in extra_validators:
            verdict = validator(row, index)
            if verdict:
                _record(f"{rows_key}[{index}] {verdict}")
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


def m0_contamination_against_validator(row: JsonDict, index: int) -> str | None:
    """Validate M0 ``contamination_against`` carries ``list[str]``.

    Presence is already enforced by the required-field schema. This validator
    tightens the contract from "field exists" to the documented data shape.
    Empty lists are allowed and mean "audited, no known overlap".
    """
    value = row.get("contamination_against")
    if value is None:
        return None
    if not isinstance(value, list):
        return "contamination_against must be a list"
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return "contamination_against entries must be non-empty strings"
    return None


__all__ = [
    "KNOWN_KINDS",
    "KNOWN_BRIDGE_STATUSES",
    "validate_top_level",
    "validate_rows",
    "bridge_status_validator",
    "bridge_mix_validator_factory",
    "m0_contamination_against_validator",
]
