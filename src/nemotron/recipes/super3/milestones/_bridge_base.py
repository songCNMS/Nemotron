# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Shared scaffolding for the M0 → M1 stage bridges.

`m1_rlvr/`, `m1_swe1/`, `m1_swe2/`, and `m1_rlhf/` all run the same
registry-driven JSONL bridge pattern: read M0 split files, filter rows
to the active env_map, tag each row with the NeMo-Gym env name + mix
metadata, emit ``train.jsonl`` / ``val.jsonl`` / ``manifest.json`` with
a ``coverage`` block + a stage-specific lineage record.

Session 4 of task017 pulls the ~80% shared helpers out so each module
only carries its mix-specific bits:

- per-module: ``MIX_NAME``, registry path, mix profile, ``prepare()``
  (manifest field set + lineage outputs + extra coverage breakdowns),
  per-row extension fields (SWE2 ``sif_source``, RLHF ``pref_dataset``),
  secondary registries (SWE2 SIF, RLHF pref data candidates).
- in this base module: JSONL/JSON helpers, ``discover_m0_split_files``,
  status constants, generic ``load_env_registry``, ``derive_env_map``,
  ``base_coverage_report``, ``base_tag_record``, ``collect_mix_rows``.

No behavior change vs the pre-extraction copies — the 4 module test
suites are the validation surface for this refactor.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]


# Common status vocabulary used by every bridge module's env registry.
STATUS_ACTIVE = "active"
STATUS_M0_MISSING = "m0_missing"
STATUS_VERIFIER_MISMATCH = "verifier_mismatch"
STATUS_BLOCKED_EXTERNAL = "blocked_external"
KNOWN_STATUSES = frozenset(
    {STATUS_ACTIVE, STATUS_M0_MISSING, STATUS_VERIFIER_MISMATCH, STATUS_BLOCKED_EXTERNAL}
)


# --- JSONL / JSON I/O -----------------------------------------------------


def read_jsonl(path: Path) -> list[JsonDict]:
    """Read a JSONL file. One JSON object per non-empty line."""
    rows: list[JsonDict] = []
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


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    """Write a JSONL file (one row per line, sorted keys for diff stability)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            json.dump(row, f, ensure_ascii=False, sort_keys=True)
            f.write("\n")


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    """Write a JSON file (indent=2, sorted keys)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


# --- M0 split discovery ---------------------------------------------------


def discover_m0_split_files(input_dir: Path) -> dict[str, dict[str, Path]]:
    """Return ``{environment: {split: path}}`` for every
    ``<env>/<split>-split.jsonl`` under *input_dir*.

    The shape mirrors what ``prepare_m0_assets.py`` writes: one
    directory per M0 environment, holding ``train-split.jsonl`` /
    ``val-split.jsonl`` files. All 4 bridge modules consume this layout
    unchanged.
    """
    files: dict[str, dict[str, Path]] = defaultdict(dict)
    for path in sorted(input_dir.glob("*/*-split.jsonl")):
        environment = path.parent.name
        split = path.name.replace("-split.jsonl", "")
        files[environment][split] = path
    return dict(files)


# --- Generic env registry loader -----------------------------------------


def load_env_registry(
    path: Path,
    *,
    expected_mix: str | set[str],
    display_label: str | None = None,
    extra_row_validator: Callable[[JsonDict, int], None] | None = None,
    required_fields: Sequence[str] | None = None,
) -> list[JsonDict]:
    """Load a bridge module env registry from YAML.

    task030 Session 4: this runtime loader delegates row-shape +
    top-level checks to the central ``data_registries.schema`` layer
    (``validate_top_level`` + ``validate_rows(fail_fast=True)``). The
    bridge-specific bits — mix-set membership with a module-friendly
    error message, and the ``extra_row_validator`` callback — stay
    inline as a closure passed to schema's ``extra_validators``. Single
    source of truth for the row-shape definition, no behavior change.

    *required_fields* is kept for API compatibility; today's
    ``bridge_env_registry`` schema declares its own required set so
    the param is unused unless a caller passes a non-default override.
    """
    import yaml

    from nemotron.recipes.super3.milestones.data_registries.schema import (
        bridge_status_validator,
        validate_rows,
        validate_top_level,
    )

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Top-level shape via schema layer. Errors get the YAML path
    # prefixed for ops debuggability (matches the pre-Session-4
    # message format).
    validate_top_level(data, kind="bridge_env_registry", source_path=path, strict=False)

    expected_set = {expected_mix} if isinstance(expected_mix, str) else set(expected_mix)
    label = (
        display_label
        if display_label is not None
        else (expected_mix.upper() if isinstance(expected_mix, str) else "/".join(sorted(expected_set)))
    )
    mix_value_label = expected_mix if isinstance(expected_mix, str) else "/".join(sorted(expected_set))

    def _mix_validator(row: JsonDict, index: int) -> str | None:
        if row["mix"] not in expected_set:
            return (
                f"mix {row['mix']!r} not in {{{mix_value_label!r}}} "
                f"— {label} registry should only carry {mix_value_label} rows"
            )
        return None

    def _extra_row_adapter(row: JsonDict, index: int) -> str | None:
        if extra_row_validator is not None:
            try:
                extra_row_validator(row, index)
            except ValueError as exc:
                return str(exc)
        return None

    # Row-shape via schema layer. fail_fast=True keeps the runtime
    # contract: a single bad row aborts the prepare step rather than
    # silently writing partial bad data.
    validate_rows(
        data,
        kind="bridge_env_registry",
        fail_fast=True,
        source_path=path,
        extra_validators=[
            bridge_status_validator,
            _mix_validator,
            _extra_row_adapter,
        ],
    )
    return data["envs"]


# --- Env map derivation + coverage report --------------------------------


def derive_env_map(
    registry: Sequence[Mapping[str, Any]],
    mix_name: str | None = None,
) -> dict[str, str]:
    """Pull ``{m0_env_id: nemo_gym_env}`` from active rows.

    If *mix_name* is None, accepts all mixes (used by single-mix modules
    whose registry only carries one mix anyway). If *mix_name* is given,
    filters to that mix — used by RLVR's per-mix derivation.

    Raises ``ValueError`` when two active rows claim the same M0 env for
    different NeMo-Gym targets (registry authorship bug).
    """
    env_map: dict[str, str] = {}
    for row in registry:
        if mix_name is not None and row["mix"] != mix_name:
            continue
        if row["status"] != STATUS_ACTIVE:
            continue
        m0_env = row.get("m0_env_id")
        if not m0_env:
            continue
        if m0_env in env_map and env_map[m0_env] != row["nemo_gym_env"]:
            raise ValueError(
                f"registry has two active mappings for M0 env {m0_env!r}"
                + (f" in mix {mix_name}" if mix_name else "")
                + f": {env_map[m0_env]} vs {row['nemo_gym_env']}"
            )
        env_map[m0_env] = row["nemo_gym_env"]
    return env_map


def base_coverage_report(
    registry: Sequence[Mapping[str, Any]],
    mix_name: str,
    *,
    filter_to_mix: bool = False,
) -> JsonDict:
    """Per-mix counts + per-status env lists.

    Module-specific coverage extensions (SWE2 ``sif_source_breakdown``,
    RLHF ``pref_dataset_breakdown`` / ``known_pref_candidates``) are
    merged on top by the caller — the base report has no knowledge of
    those.

    *filter_to_mix=True* restricts counts to rows whose ``mix`` matches
    *mix_name* (used by RLVR's per-mix view); single-mix registries pass
    ``filter_to_mix=False`` since they only carry one mix anyway.
    """
    rows = [
        row for row in registry
        if not filter_to_mix or row["mix"] == mix_name
    ]
    by_status: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_status[row["status"]].append(row["nemo_gym_env"])
    return {
        "mix": mix_name,
        "total_target_envs": len(rows),
        "counts": {status: len(by_status.get(status, [])) for status in sorted(KNOWN_STATUSES)},
        "active": sorted(by_status.get(STATUS_ACTIVE, [])),
        "m0_missing": sorted(by_status.get(STATUS_M0_MISSING, [])),
        "verifier_mismatch": sorted(by_status.get(STATUS_VERIFIER_MISMATCH, [])),
        "blocked_external": sorted(by_status.get(STATUS_BLOCKED_EXTERNAL, [])),
    }


# --- Row tagging + collection --------------------------------------------


def base_tag_record(
    record: Mapping[str, Any],
    *,
    nemo_gym_env: str,
    mix_name: str,
    row_index: int,
    split: str,
    extra_row_fields: Mapping[str, Any] | None = None,
    extra_metadata_fields: Mapping[str, Any] | None = None,
    row_index_key: str = "row_index",
    split_key: str = "split",
) -> JsonDict:
    """Tag an M0 row with NeMo-Gym env name + mix metadata.

    Module-specific extras (SWE2 ``sif_source``, RLHF ``pref_dataset``)
    are merged via ``extra_row_fields`` (top-level) and
    ``extra_metadata_fields`` (under ``metadata``). The base contract
    preserves M0 ``environment`` / ``responses_create_params`` /
    ``reward_config`` / ``extra_env_info`` unchanged so health-baseline
    / lineage / down-stage routing stay self-consistent.

    *row_index_key* / *split_key* are the metadata field names that
    carry the per-bridge index info (e.g., RLVR uses ``rlvr_row_index``
    / ``rlvr_split``, SWE1 uses ``swe1_row_index`` / ``swe1_split``).
    """
    tagged = dict(record)
    tagged["nemo_gym_env"] = nemo_gym_env
    tagged["nemo_gym_mix"] = mix_name
    if extra_row_fields:
        for key, value in extra_row_fields.items():
            if value is not None:
                tagged[key] = value

    metadata = dict(tagged.get("metadata") or {})
    metadata.setdefault("m0_environment", record.get("environment"))
    metadata["nemo_gym_env"] = nemo_gym_env
    metadata["nemo_gym_mix"] = mix_name
    metadata[row_index_key] = row_index
    metadata[split_key] = split
    if extra_metadata_fields:
        for key, value in extra_metadata_fields.items():
            if value is not None:
                metadata[key] = value
    tagged["metadata"] = metadata
    return tagged


def collect_mix_rows(
    files_by_env: Mapping[str, Mapping[str, Path]],
    *,
    env_map: Mapping[str, str],
    split: str,
    max_records_per_env: int | None,
    tag_fn: Callable[[Mapping[str, Any], str, str, int, str], JsonDict],
) -> tuple[list[JsonDict], list[JsonDict], dict[str, int]]:
    """Slice M0 records into a mix and tag them.

    *tag_fn(record, m0_env, nemo_gym_env, row_index, split)* returns a
    tagged JsonDict. Each bridge module supplies its own ``tag_fn``
    closure that wraps ``base_tag_record`` with module-specific extras
    (``sif_source`` for SWE2, ``pref_dataset`` for RLHF, or none for
    RLVR / SWE1).

    Returns ``(rows, errors, per_env_counts)``. Errors collect per-env
    issues (missing split file, missing env in M0, row tag failure)
    without aborting the run — the caller decides whether to surface
    them as warnings or hard failures.
    """
    rows: list[JsonDict] = []
    errors: list[JsonDict] = []
    counts: dict[str, int] = defaultdict(int)
    for m0_env, nemo_gym_env in sorted(env_map.items()):
        split_files = files_by_env.get(m0_env)
        if split_files is None:
            errors.append(
                {
                    "environment": m0_env,
                    "split": split,
                    "error": "M0 has no rows for this environment (not in M0 mix)",
                }
            )
            continue
        path = split_files.get(split)
        if path is None:
            errors.append(
                {
                    "environment": m0_env,
                    "split": split,
                    "error": f"missing {split}-split.jsonl",
                }
            )
            continue
        env_rows = read_jsonl(path)
        if max_records_per_env is not None:
            env_rows = env_rows[:max_records_per_env]
        for row_index, record in enumerate(env_rows):
            try:
                tagged = tag_fn(record, m0_env, nemo_gym_env, row_index, split)
            except Exception as exc:  # noqa: BLE001 - keep mixing on row failure
                errors.append(
                    {
                        "environment": m0_env,
                        "split": split,
                        "row_index": row_index,
                        "error": str(exc),
                    }
                )
                continue
            rows.append(tagged)
            counts[m0_env] += 1
    return rows, errors, dict(sorted(counts.items()))


__all__ = [
    # status vocabulary
    "STATUS_ACTIVE",
    "STATUS_M0_MISSING",
    "STATUS_VERIFIER_MISMATCH",
    "STATUS_BLOCKED_EXTERNAL",
    "KNOWN_STATUSES",
    # i/o
    "read_jsonl",
    "write_jsonl",
    "write_json",
    # discovery
    "discover_m0_split_files",
    # registry + derivation
    "load_env_registry",
    "derive_env_map",
    "base_coverage_report",
    # tagging + collection
    "base_tag_record",
    "collect_mix_rows",
    # type
    "JsonDict",
]
