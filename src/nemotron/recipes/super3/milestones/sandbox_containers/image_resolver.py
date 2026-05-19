# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Sandbox container image registry loader + per-env resolver.

Roadmap §1.8 task021 Session 3. ``sandbox_image_registry.yaml`` is the
source of truth pairing an M0 env id with the sandbox image that
isolates its runtime (code-exec / Lean / terminal). The bare image
build is shell (``build_sandbox_containers.sh``); the Python helpers
here are the sandbox-side surface that future ContainerSandbox shim
(task021 Session 4) will call from inside ``run_m0_health_baseline``
and the M1 RLVR rollout path.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]


REGISTRY_PATH = Path(__file__).with_name("sandbox_image_registry.yaml")


def load_sandbox_image_registry(path: Path | None = None) -> list[JsonDict]:
    """Load ``sandbox_image_registry.yaml`` rows.

    task030 Session 4: row shape delegated to
    ``data_registries.schema.validate_rows`` (fail_fast=True). Two
    module-specific checks stay inline as ``extra_validators``:

    - ``target_envs`` must be a non-empty list (schema-level
      "field present" check would accept an empty list)
    - ``image_id`` must be unique across rows (cross-row check; not
      expressible as a per-row schema rule)
    """
    import yaml

    from nemotron.recipes.super3.milestones.data_registries.schema import (
        validate_rows,
        validate_top_level,
    )

    target = path or REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    validate_top_level(
        data, kind="sandbox_image_registry", source_path=target, strict=False
    )

    seen_ids: set[str] = set()

    def _target_envs_validator(row: JsonDict, index: int) -> str | None:
        target_envs = row.get("target_envs")
        if target_envs is not None and (
            not isinstance(target_envs, list) or not target_envs
        ):
            return "target_envs must be a non-empty list"
        return None

    def _unique_image_id_validator(row: JsonDict, index: int) -> str | None:
        image_id = row.get("image_id")
        if not image_id:
            return None
        if image_id in seen_ids:
            return f"duplicate image_id {image_id!r}"
        seen_ids.add(image_id)
        return None

    validate_rows(
        data,
        kind="sandbox_image_registry",
        fail_fast=True,
        source_path=target,
        extra_validators=[_target_envs_validator, _unique_image_id_validator],
    )
    return data["images"]


def resolve_dockerfile_path(
    row: Mapping[str, Any],
    *,
    registry_dir: Path | None = None,
) -> Path:
    """Resolve a registry row's ``dockerfile_path`` to an absolute path.

    Relative paths are taken relative to the registry YAML's parent dir
    (default: the module dir). Absolute paths pass through unchanged.
    """
    base = registry_dir or REGISTRY_PATH.parent
    candidate = Path(row["dockerfile_path"])
    if candidate.is_absolute():
        return candidate
    return (base / candidate).resolve()


def validate_dockerfile_exists(
    row: Mapping[str, Any],
    *,
    registry_dir: Path | None = None,
) -> bool:
    """Check that a registry row's Dockerfile exists on disk."""
    return resolve_dockerfile_path(row, registry_dir=registry_dir).is_file()


def image_tag(row: Mapping[str, Any]) -> str:
    """Return the canonical ``<image_id>:<version_tag>`` reference."""
    return f"{row['image_id']}:{row['version_tag']}"


def resolve_image_for_env(
    env_id: str,
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> str | None:
    """Return the canonical ``<image_id>:<version_tag>`` for *env_id*,
    or None if no registered image targets that env.

    M0 envs without a sandbox image (e.g., `search_grounded_qa` which
    runs no untrusted code) return None — callers are expected to
    fall back to in-process execution. The future ContainerSandbox
    shim should ``if resolve_image_for_env(env_id) is None: run_in_process()``.
    """
    if registry is None:
        registry = load_sandbox_image_registry()
    for row in registry:
        if env_id in row["target_envs"]:
            return image_tag(row)
    return None


def envs_covered_by_registry(
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> set[str]:
    """Return every env id that has a sandbox image declared."""
    if registry is None:
        registry = load_sandbox_image_registry()
    out: set[str] = set()
    for row in registry:
        out.update(row["target_envs"])
    return out


__all__ = [
    "REGISTRY_PATH",
    "load_sandbox_image_registry",
    "resolve_dockerfile_path",
    "validate_dockerfile_exists",
    "image_tag",
    "resolve_image_for_env",
    "envs_covered_by_registry",
]
