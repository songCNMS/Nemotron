# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Eval-overlap matrix for the unified M0 data registry.

task035 Session 1 scaffold. This module renders each M0 data row as a
small contamination/eval-overlap record keyed by environment. It reuses
``contamination_audit.classify_contamination_row`` for the
blocker/informational split so this report composes with the existing
CI-facing contamination audit instead of creating a second policy.

Sandbox-only: reads local YAML registries through ``unified_index.yaml``;
does not download HF datasets, scan prompt corpora, run Docker, or submit
cluster jobs.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from nemotron.recipes.super3.milestones.data_registries.contamination_audit import (
    classify_contamination_row,
)

JsonDict = dict[str, Any]

POSTURES = ("clean", "informational", "blocker")


def _clean_targets(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [entry.strip() for entry in value if isinstance(entry, str) and entry.strip()]


def _row_posture(
    blocker_reasons: list[str],
    informational_reasons: list[str],
) -> str:
    if blocker_reasons:
        return "blocker"
    if informational_reasons:
        return "informational"
    return "clean"


def _env_posture(rows: list[JsonDict]) -> str:
    postures = {row["posture"] for row in rows}
    if "blocker" in postures:
        return "blocker"
    if "informational" in postures:
        return "informational"
    return "clean"


def _load_environment_metadata(index_path: Path) -> dict[str, JsonDict]:
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        load_indexed_registry,
        load_unified_index,
    )

    by_env_id: dict[str, JsonDict] = {}
    for entry in load_unified_index(index_path):
        if entry["kind"] != "m0_environment_registry":
            continue
        data = load_indexed_registry(index_path, entry)
        for row in data.get("environments") or []:
            if not isinstance(row, Mapping):
                continue
            env_id = str(row.get("id", "<no-id>"))
            by_env_id[env_id] = {
                "registry_id": entry["id"],
                "family": row.get("family"),
                "stage": row.get("stage"),
                "reward_verifier": (row.get("reward") or {}).get("verifier")
                if isinstance(row.get("reward"), Mapping)
                else None,
            }
    return by_env_id


def build_eval_overlap_matrix(index_path: Path | None = None) -> JsonDict:
    """Return a per-environment matrix of M0 data eval-overlap targets.

    Result shape::

        {
          "schema_version": 1,
          "row_count": 2,
          "counts": {"clean": 1, "informational": 1, "blocker": 0},
          "environments": [
            {
              "environment": "search_grounded_qa",
              "family": "search",
              "stage": "M0 data_env_foundation",
              "posture": "clean",
              "datasets": [
                {
                  "row_id": "m0_search_hotpotqa",
                  "eval_overlap_targets": ["HotpotQA validation"],
                  "posture": "clean",
                  ...
                }
              ],
            },
          ],
        }
    """
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        INDEX_PATH,
        load_indexed_registry,
        load_unified_index,
    )

    target = index_path or INDEX_PATH
    environments = _load_environment_metadata(target)
    rows_by_env: dict[str, list[JsonDict]] = defaultdict(list)
    counts = {posture: 0 for posture in POSTURES}

    for entry in load_unified_index(target):
        if entry["kind"] != "m0_data_registry":
            continue
        data = load_indexed_registry(target, entry)
        for row in data.get("datasets") or []:
            if not isinstance(row, Mapping):
                continue
            blocker_reasons, informational_reasons = classify_contamination_row(row)
            posture = _row_posture(blocker_reasons, informational_reasons)
            counts[posture] += 1

            env_id = str(row.get("environment") or "<no-environment>")
            rows_by_env[env_id].append(
                {
                    "registry_id": entry["id"],
                    "row_id": str(row.get("id", "<no-id>")),
                    "environment": env_id,
                    "domain": row.get("domain"),
                    "hf_dataset": row.get("hf_dataset"),
                    "hf_config": row.get("hf_config"),
                    "hf_split": row.get("hf_split"),
                    "hf_revision": row.get("hf_revision"),
                    "license": row.get("license"),
                    "use_stage": row.get("use_stage") or [],
                    "contamination_against": row.get("contamination_against"),
                    "eval_overlap_targets": _clean_targets(
                        row.get("contamination_against")
                    ),
                    "posture": posture,
                    "blocker_reasons": blocker_reasons,
                    "informational_reasons": informational_reasons,
                }
            )

    env_rows: list[JsonDict] = []
    for env_id in sorted(rows_by_env):
        datasets = sorted(rows_by_env[env_id], key=lambda row: row["row_id"])
        metadata = environments.get(env_id, {})
        env_rows.append(
            {
                "environment": env_id,
                "known_in_environment_registry": env_id in environments,
                "family": metadata.get("family"),
                "stage": metadata.get("stage"),
                "reward_verifier": metadata.get("reward_verifier"),
                "posture": _env_posture(datasets),
                "datasets": datasets,
            }
        )

    return {
        "schema_version": 1,
        "row_count": sum(counts.values()),
        "counts": counts,
        "environments": env_rows,
    }


def format_eval_overlap_matrix(matrix: Mapping[str, Any]) -> str:
    """Human-readable rendering of ``build_eval_overlap_matrix`` output."""
    row_count = matrix.get("row_count", 0)
    counts = matrix.get("counts", {})
    if not row_count:
        return "eval-overlap matrix: no m0_data_registry rows found\n"

    lines = [
        "eval-overlap matrix: "
        f"{row_count} m0 data row(s), "
        f"{counts.get('blocker', 0)} blocker(s), "
        f"{counts.get('informational', 0)} informational, "
        f"{counts.get('clean', 0)} clean",
        "",
    ]
    for env in matrix.get("environments", []):
        datasets = env.get("datasets", [])
        lines.append(
            f"- {env['environment']} [{env['posture']}] "
            f"family={env.get('family')!r} stage={env.get('stage')!r} "
            f"rows={len(datasets)}"
        )
        if not env.get("known_in_environment_registry"):
            lines.append("  environment_registry: missing")
        for row in datasets:
            targets = row.get("eval_overlap_targets") or []
            target_text = "; ".join(targets) if targets else "(none)"
            lines.append(
                f"  - {row['row_id']} [{row['posture']}] "
                f"hf_dataset={row.get('hf_dataset')!r} targets={target_text}"
            )
            if row.get("blocker_reasons"):
                lines.append("    blockers: " + "; ".join(row["blocker_reasons"]))
            if row.get("informational_reasons"):
                lines.append(
                    "    informational: "
                    + "; ".join(row["informational_reasons"])
                )
    if not counts.get("blocker"):
        lines.append("")
        lines.append("(no blockers - informational findings do not fail CI)")
    return "\n".join(lines) + "\n"


__all__ = [
    "POSTURES",
    "build_eval_overlap_matrix",
    "format_eval_overlap_matrix",
]
