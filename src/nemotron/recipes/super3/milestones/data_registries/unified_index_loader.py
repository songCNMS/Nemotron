# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Loader + cross-registry inventory walks for the unified data registry.

Plan §6 W1 / task030 Session 1. The unified index
(``unified_index.yaml``) catalogs every registry YAML in the pipeline;
this module:

- loads the index + the registries it points at;
- validates each registry against its declared kind via ``schema.py``;
- runs read-only cross-registry inventory walks (licenses, hf datasets,
  M0-to-downstream cross-walk) so operators have one CLI surface to
  audit "what data flows through the pipeline today".

Designed to fail fast on shape drift before any cluster run touches the
data; designed to stay dependency-light (just pyyaml) so the audit can
run in sandbox CI without booting Megatron-Bridge / torch.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.data_registries.schema import (
    KNOWN_KINDS,
    bridge_mix_validator_factory,
    bridge_status_validator,
    m0_contamination_against_validator,
    pref_contamination_against_validator,
    validate_rows,
    validate_top_level,
)

JsonDict = dict[str, Any]


INDEX_PATH = Path(__file__).with_name("unified_index.yaml")


def load_unified_index(path: Path | None = None) -> list[JsonDict]:
    """Load and validate the meta-registry rows.

    Each row must declare ``id``, ``kind``, ``path``, ``summary``;
    ``kind`` must be in ``KNOWN_KINDS``; ``path`` is resolved relative
    to the unified_index.yaml's parent directory.
    """
    import yaml

    target = path or INDEX_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "registries" not in data:
        raise ValueError(f"{target}: unified index must declare a 'registries' list")
    rows = data["registries"]
    if not isinstance(rows, list):
        raise ValueError(f"{target}: 'registries' must be a list")
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{target}: registries[{index}] must be a mapping")
        for field in ("id", "kind", "path", "summary"):
            if field not in row:
                raise ValueError(
                    f"{target}: registries[{index}] missing required field {field!r}"
                )
        if row["kind"] not in KNOWN_KINDS:
            raise ValueError(
                f"{target}: registries[{index}] kind {row['kind']!r} not in {sorted(KNOWN_KINDS)}"
            )
        if row["id"] in seen_ids:
            raise ValueError(
                f"{target}: duplicate registry id {row['id']!r}"
            )
        seen_ids.add(row["id"])
    return rows


def _registry_containment_root(index_path: Path) -> Path:
    """Return the directory registry paths are allowed to resolve under."""
    index_dir = index_path.resolve(strict=True).parent
    if index_dir.name == "data_registries":
        return index_dir.parent.resolve(strict=True)
    return index_dir


def _resolve_registry_path(
    index_path: Path,
    registry_path: Any,
) -> tuple[Path | None, str | None]:
    """Resolve a registry path with containment checks.

    Production ``unified_index.yaml`` lives in ``data_registries/`` but
    intentionally points at sibling milestone directories, so that index is
    contained by the parent milestones directory. Other indexes are contained by
    their own directory.
    """
    if not isinstance(registry_path, str) or not registry_path:
        return None, "must be a non-empty string"
    candidate = Path(registry_path)
    if candidate.is_absolute():
        return None, "must be relative to the unified index"
    components = registry_path.split("/")
    if any(component in {"", "."} for component in components):
        return None, "must use normal relative path components"

    index_dir = index_path.resolve(strict=True).parent
    containment_root = _registry_containment_root(index_path)
    try:
        resolved = (index_dir / candidate).resolve(strict=True)
    except FileNotFoundError:
        return None, "does not exist"
    except OSError as exc:
        return None, f"could not be resolved: {exc}"

    try:
        resolved.relative_to(containment_root)
    except ValueError:
        return None, f"must stay under registry root ({containment_root})"
    if not resolved.is_file():
        return None, "must resolve to a file"
    return resolved, None


def resolve_registry_path(index_path: Path, registry_path: Any) -> Path:
    """Resolve a registry path or raise a clear containment error."""
    resolved, path_issue = _resolve_registry_path(index_path, registry_path)
    if path_issue:
        raise ValueError(f"declared path {registry_path!r} {path_issue}")
    if resolved is None:
        raise ValueError(f"declared path {registry_path!r} could not be resolved")
    return resolved


def load_registry_file(path: Path) -> JsonDict:
    """Load a single registry YAML and return the top-level dict."""
    import yaml

    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_indexed_registry(index_path: Path, entry: Mapping[str, Any]) -> JsonDict:
    """Resolve and load a registry row from a unified index."""
    registry_path = resolve_registry_path(index_path, entry.get("path"))
    return load_registry_file(registry_path)


def validate_unified_index(
    index_path: Path | None = None,
) -> list[str]:
    """Run a full validation pass over every registry the index points at.

    Returns a list of human-readable issues. Empty list = all clean.
    Use ``raise_on_issues=True`` semantics by checking ``if issues:``
    at the call site.
    """
    target = index_path or INDEX_PATH
    index_rows = load_unified_index(target)
    issues: list[str] = []
    for entry in index_rows:
        resolved, path_issue = _resolve_registry_path(target, entry["path"])
        if path_issue:
            issues.append(
                f"{entry['id']}: declared path {entry['path']!r} {path_issue}"
            )
            continue
        try:
            data = load_registry_file(resolved)
        except Exception as exc:  # noqa: BLE001
            issues.append(f"{entry['id']}: load failed: {exc}")
            continue
        try:
            validate_top_level(data, kind=entry["kind"])
        except ValueError as exc:
            issues.append(f"{entry['id']}: {exc}")
            continue
        extra_validators = []
        if entry["kind"] == "m0_data_registry":
            extra_validators.append(m0_contamination_against_validator)
        if entry["kind"] == "pref_data_registry":
            extra_validators.append(pref_contamination_against_validator)
        if entry["kind"] == "bridge_env_registry":
            extra_validators.append(bridge_status_validator)
            if "expected_mixes" in entry:
                extra_validators.append(
                    bridge_mix_validator_factory(entry["expected_mixes"])
                )
        row_issues = validate_rows(
            data,
            kind=entry["kind"],
            extra_validators=extra_validators,
        )
        for issue in row_issues:
            issues.append(f"{entry['id']}: {issue}")
    return issues


# --- Cross-registry inventories ------------------------------------------


def licenses_inventory(
    index_path: Path | None = None,
) -> dict[str, list[JsonDict]]:
    """Walk every registry, return ``{license: [{registry_id, kind, row_id, ...}]}``.

    Surfaces which licenses cascade where (operators reviewing share-
    alike obligations get a single map). Rows that don't declare a
    license land under ``"<unknown>"`` so they show up in audits.
    """
    target = index_path or INDEX_PATH
    out: dict[str, list[JsonDict]] = defaultdict(list)
    for entry in load_unified_index(target):
        resolved, path_issue = _resolve_registry_path(target, entry["path"])
        if path_issue:
            continue
        data = load_registry_file(resolved)
        rows = _rows_of(data, entry["kind"])
        for row in rows:
            license_name = str(row.get("license") or "<unknown>")
            row_id = _row_identity(row, entry["kind"])
            out[license_name].append(
                {
                    "registry_id": entry["id"],
                    "kind": entry["kind"],
                    "row_id": row_id,
                }
            )
    return dict(sorted(out.items()))


def hf_dataset_inventory(
    index_path: Path | None = None,
) -> dict[str, list[JsonDict]]:
    """Walk data-shape registries, return ``{hf_dataset: [{revision, license, ...}]}``.

    Only ``m0_data_registry`` and ``pref_data_registry`` rows carry
    ``hf_dataset`` directly. Bridge env registries reference upstream
    M0 envs (not raw HF datasets) — they're skipped.
    """
    target = index_path or INDEX_PATH
    out: dict[str, list[JsonDict]] = defaultdict(list)
    for entry in load_unified_index(target):
        if entry["kind"] not in ("m0_data_registry", "pref_data_registry"):
            continue
        resolved, path_issue = _resolve_registry_path(target, entry["path"])
        if path_issue:
            continue
        data = load_registry_file(resolved)
        rows = _rows_of(data, entry["kind"])
        for row in rows:
            hf_dataset = row.get("hf_dataset")
            if not hf_dataset:
                continue
            out[str(hf_dataset)].append(
                {
                    "registry_id": entry["id"],
                    "kind": entry["kind"],
                    "row_id": _row_identity(row, entry["kind"]),
                    "hf_revision": row.get("hf_revision"),
                    "hf_revision_pin_required": row.get("hf_revision_pin_required"),
                    "license": row.get("license"),
                }
            )
    return dict(sorted(out.items()))


def m0_to_downstream_inventory(
    index_path: Path | None = None,
) -> dict[str, list[JsonDict]]:
    """Walk bridge env registries, return ``{m0_env_id: [{registry, mix, status, ...}]}``.

    Answers "if I add an M0 env, which downstream mixes light up?".
    Rows whose ``m0_env_id`` is null (m0_missing slots) are skipped —
    those are the gap rows the bridges already surface in coverage.
    """
    target = index_path or INDEX_PATH
    out: dict[str, list[JsonDict]] = defaultdict(list)
    for entry in load_unified_index(target):
        if entry["kind"] != "bridge_env_registry":
            continue
        resolved, path_issue = _resolve_registry_path(target, entry["path"])
        if path_issue:
            continue
        data = load_registry_file(resolved)
        rows = _rows_of(data, entry["kind"])
        for row in rows:
            m0_env = row.get("m0_env_id")
            if not m0_env:
                continue
            out[str(m0_env)].append(
                {
                    "registry_id": entry["id"],
                    "mix": row.get("mix"),
                    "nemo_gym_env": row.get("nemo_gym_env"),
                    "status": row.get("status"),
                }
            )
    return dict(sorted(out.items()))


# --- helpers --------------------------------------------------------------


_ROWS_KEY_BY_KIND = {
    "m0_data_registry": "datasets",
    "m0_environment_registry": "environments",
    "bridge_env_registry": "envs",
    "sif_registry": "sif_sources",
    "pref_data_registry": "datasets",
    "sandbox_image_registry": "images",
    "swe_harness_registry": "harnesses",
    "eval_basket_registry": "benchmarks",
}


def _rows_of(data: Mapping[str, Any], kind: str) -> list[JsonDict]:
    return data.get(_ROWS_KEY_BY_KIND[kind], []) or []


def _row_identity(row: Mapping[str, Any], kind: str) -> str:
    """Best-effort human-readable row id for inventory output."""
    if kind in ("m0_data_registry", "pref_data_registry"):
        return str(row.get("id", "<no-id>"))
    if kind == "m0_environment_registry":
        return str(row.get("id", "<no-id>"))
    if kind == "bridge_env_registry":
        return f"{row.get('nemo_gym_env', '<no-env>')}@{row.get('mix', '?')}"
    if kind == "sif_registry":
        return str(row.get("source", "<no-source>"))
    if kind == "sandbox_image_registry":
        return str(row.get("image_id", "<no-image-id>"))
    if kind == "swe_harness_registry":
        return str(row.get("harness_id", "<no-harness-id>"))
    if kind == "eval_basket_registry":
        return str(row.get("benchmark_id", "<no-benchmark-id>"))
    return "<unknown-kind>"


__all__ = [
    "INDEX_PATH",
    "load_unified_index",
    "load_registry_file",
    "load_indexed_registry",
    "resolve_registry_path",
    "validate_unified_index",
    "licenses_inventory",
    "hf_dataset_inventory",
    "m0_to_downstream_inventory",
]
