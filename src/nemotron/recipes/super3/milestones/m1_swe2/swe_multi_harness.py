# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""SWE multi-harness adapter declarations (task026 Session 1).

This module is intentionally sandbox-only. It declares the OpenHands,
OpenCode, and Codex harness surfaces that the M2 SWE expansion routes
through, but does not import OpenCode/Codex packages, launch Docker, or
touch SIF containers. Real adapter implementations and cluster smoke
runs remain follow-up work.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.m1_swe2.openhands_loop import Instance, RolloutResult


JsonDict = dict[str, Any]


REGISTRY_PATH = Path(__file__).with_name("swe_harness_registry.yaml")

MIX_NAME = "swe2"

HARNESS_OPENHANDS = "openhands"
HARNESS_OPENCODE = "opencode"
HARNESS_CODEX = "codex"
KNOWN_HARNESS_IDS = frozenset({HARNESS_OPENHANDS, HARNESS_OPENCODE, HARNESS_CODEX})

STATUS_PROTOCOL_READY = "protocol_ready"
STATUS_SANDBOX_DECLARED = "sandbox_declared"
STATUS_BLOCKED_EXTERNAL = "blocked_external"
KNOWN_HARNESS_STATUSES = frozenset({
    STATUS_PROTOCOL_READY,
    STATUS_SANDBOX_DECLARED,
    STATUS_BLOCKED_EXTERNAL,
})


@dataclass(frozen=True)
class AdapterDeclaration:
    """Static declaration for a SWE harness adapter surface."""

    harness_id: str
    adapter_class: str
    tool_format: str
    supports_sandbox_tests: bool
    requires_cluster_smoke: bool


@dataclass(frozen=True)
class HarnessRoute:
    """Routing metadata consumed by future SWE rollout launchers."""

    harness_id: str
    nemo_gym_env: str
    mix: str
    adapter_class: str
    tool_format: str
    config_path: str
    status: str
    cluster_smoke_required: bool
    m0_env_id: str | None = None
    sif_source: str | None = None


class _DeclarationOnlyAdapter:
    """Placeholder base for M2 harnesses whose real runtime lands later."""

    harness_id: str

    def rollout(self, instance: Instance) -> RolloutResult:
        raise NotImplementedError(
            f"{self.harness_id} adapter is declaration-only in task026 Session 1; "
            "real adapter implementation and cluster smoke are follow-up work"
        )


class OpenCodeLoopAdapter(_DeclarationOnlyAdapter):
    """Declaration-only OpenCode adapter symbol for registry routing."""

    harness_id = HARNESS_OPENCODE


class CodexLoopAdapter(_DeclarationOnlyAdapter):
    """Declaration-only Codex adapter symbol for registry routing."""

    harness_id = HARNESS_CODEX


ADAPTER_DECLARATIONS: dict[str, AdapterDeclaration] = {
    HARNESS_OPENHANDS: AdapterDeclaration(
        harness_id=HARNESS_OPENHANDS,
        adapter_class="nemotron.recipes.super3.milestones.m1_swe2.openhands_loop.OpenHandsLoop",
        tool_format="openhands",
        supports_sandbox_tests=True,
        requires_cluster_smoke=True,
    ),
    HARNESS_OPENCODE: AdapterDeclaration(
        harness_id=HARNESS_OPENCODE,
        adapter_class="nemotron.recipes.super3.milestones.m1_swe2.swe_multi_harness.OpenCodeLoopAdapter",
        tool_format="opencode",
        supports_sandbox_tests=True,
        requires_cluster_smoke=True,
    ),
    HARNESS_CODEX: AdapterDeclaration(
        harness_id=HARNESS_CODEX,
        adapter_class="nemotron.recipes.super3.milestones.m1_swe2.swe_multi_harness.CodexLoopAdapter",
        tool_format="codex",
        supports_sandbox_tests=True,
        requires_cluster_smoke=True,
    ),
}


def load_swe_harness_registry(path: Path | None = None) -> list[JsonDict]:
    """Load and validate the SWE harness registry.

    The validation is shape-only plus local vocabulary checks, so it is
    safe for sandbox CI and does not require any external harness package.
    """
    import yaml

    from nemotron.recipes.super3.milestones.data_registries.schema import (
        validate_rows,
        validate_top_level,
    )

    target = path or REGISTRY_PATH
    with target.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    validate_top_level(data, kind="swe_harness_registry", source_path=target, strict=False)

    seen_ids: set[str] = set()

    def _row_validator(row: JsonDict, index: int) -> str | None:
        harness_id = row.get("harness_id")
        if harness_id is not None:
            if harness_id not in KNOWN_HARNESS_IDS:
                return f"harness_id {harness_id!r} not in {sorted(KNOWN_HARNESS_IDS)}"
            if harness_id in seen_ids:
                return f"duplicate harness_id {harness_id!r}"
            seen_ids.add(harness_id)

        mix = row.get("mix")
        if mix is not None and mix != MIX_NAME:
            return f"mix {mix!r} is not {MIX_NAME!r}"

        status = row.get("status")
        if status is not None and status not in KNOWN_HARNESS_STATUSES:
            return f"status {status!r} not in {sorted(KNOWN_HARNESS_STATUSES)}"

        cluster_smoke_required = row.get("cluster_smoke_required")
        if cluster_smoke_required is not None and not isinstance(cluster_smoke_required, bool):
            return "cluster_smoke_required must be a boolean"

        declaration = ADAPTER_DECLARATIONS.get(str(harness_id))
        if declaration is None:
            return None
        if row.get("adapter_class") != declaration.adapter_class:
            return (
                f"adapter_class {row.get('adapter_class')!r} does not match "
                f"declaration for {harness_id!r}"
            )
        if row.get("tool_format") != declaration.tool_format:
            return (
                f"tool_format {row.get('tool_format')!r} does not match "
                f"declaration for {harness_id!r}"
            )
        if row.get("cluster_smoke_required") != declaration.requires_cluster_smoke:
            return (
                f"cluster_smoke_required {row.get('cluster_smoke_required')!r} does not match "
                f"declaration for {harness_id!r}"
            )
        return None

    validate_rows(
        data,
        kind="swe_harness_registry",
        fail_fast=True,
        source_path=target,
        extra_validators=[_row_validator],
    )
    return data["harnesses"]


def build_harness_routes(registry: Sequence[Mapping[str, Any]] | None = None) -> dict[str, HarnessRoute]:
    """Return ``{harness_id: HarnessRoute}`` for launcher selection."""
    rows = registry if registry is not None else load_swe_harness_registry()
    routes: dict[str, HarnessRoute] = {}
    for row in rows:
        route = HarnessRoute(
            harness_id=str(row["harness_id"]),
            nemo_gym_env=str(row["nemo_gym_env"]),
            mix=str(row["mix"]),
            adapter_class=str(row["adapter_class"]),
            tool_format=str(row["tool_format"]),
            config_path=str(row["config_path"]),
            status=str(row["status"]),
            cluster_smoke_required=bool(row["cluster_smoke_required"]),
            m0_env_id=row.get("m0_env_id"),
            sif_source=row.get("sif_source"),
        )
        if route.harness_id in routes:
            raise ValueError(f"duplicate harness route for {route.harness_id!r}")
        routes[route.harness_id] = route
    return routes


def route_for_harness(
    harness_id: str,
    registry: Sequence[Mapping[str, Any]] | None = None,
) -> HarnessRoute:
    """Resolve one harness route by id."""
    routes = build_harness_routes(registry)
    if harness_id not in routes:
        raise ValueError(f"unknown SWE harness {harness_id!r}; known: {sorted(routes)}")
    return routes[harness_id]


__all__ = [
    "ADAPTER_DECLARATIONS",
    "AdapterDeclaration",
    "HARNESS_CODEX",
    "HARNESS_OPENCODE",
    "HARNESS_OPENHANDS",
    "HarnessRoute",
    "KNOWN_HARNESS_IDS",
    "KNOWN_HARNESS_STATUSES",
    "MIX_NAME",
    "CodexLoopAdapter",
    "OpenCodeLoopAdapter",
    "REGISTRY_PATH",
    "STATUS_BLOCKED_EXTERNAL",
    "STATUS_PROTOCOL_READY",
    "STATUS_SANDBOX_DECLARED",
    "build_harness_routes",
    "load_swe_harness_registry",
    "route_for_harness",
]
