# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Share-alike license cascade audit for the unified data registry.

task058 Session 2 follow-up. `docs/m0-dataset-expansion-plan.md` §6 Q1
documents the policy that CC-BY-SA-* sources cascade share-alike
obligations through every derived artifact (eval reports, distilled
SFT data, M1+ checkpoint outputs). Today that policy lives in prose
only; this module converts it into a machine-checkable audit:

- walk the unified index for ``m0_data_registry`` /
  ``pref_data_registry`` rows whose license slug matches a share-alike
  pattern,
- trace through ``m0_environment_registry`` to find the env id each
  source feeds,
- trace further through every ``bridge_env_registry`` row that
  references that env id as ``m0_env_id``, returning the chain plus
  the bridge row's ``status`` so operators see whether the cascade is
  *live* (active bridge mapping) or *latent* (m0_missing / blocked).

Today's data flow on main:

- `hotpotqa/hotpot_qa` is **CC-BY-SA-4.0** → feeds ``search_grounded_qa``
  M0 env. No active bridge mapping today (task015 found the rlvr1
  ``search_grounded_qa`` NeMo-Gym name doesn't exist), so the cascade
  is latent. The moment a future task wires ``search_grounded_qa``
  through, share-alike inherits silently — the audit makes that
  visible.

Sandbox-runnable; consumed by ``scripts/validate_data_registries.py
--license-cascade``.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


# Share-alike license slugs we audit for. Lower-case prefix match —
# real-world licenses ship in many capitalisations and we don't want
# the audit to miss a row over a typo.
#
# Sources of the cascade obligation:
#   - Creative Commons ShareAlike family (cc-by-sa-{2.0,3.0,4.0,...})
#   - GNU GPL / AGPL family (gpl-{2.0,3.0}, agpl-{3.0})
#   - Open Database Licence (odbl-1.0)
#
# Add new families here when legal flags additional licenses.
SHARE_ALIKE_LICENSE_PREFIXES: tuple[str, ...] = (
    "cc-by-sa",
    "cc-sa",
    "gpl",
    "agpl",
    "lgpl",
    "odbl",
)


def is_share_alike(license_str: Any) -> bool:
    """True iff *license_str* names a share-alike license family.

    Defensive against capitalisation (cc-by-sa vs CC-BY-SA) and
    whitespace; returns False for empty / None / non-string inputs.
    Substring containment (``"cc-by-sa" in license_str``) would miss
    a hyphen typo, so we compare against the prefix list explicitly
    after a light normalisation step.
    """
    if not isinstance(license_str, str):
        return False
    normalized = license_str.strip().lower()
    if not normalized:
        return False
    return any(normalized.startswith(prefix) for prefix in SHARE_ALIKE_LICENSE_PREFIXES)


def find_share_alike_sources(
    index_path: Path | None = None,
) -> list[JsonDict]:
    """Walk data-shape registries, return rows whose license is share-alike.

    Each returned row is the original registry row plus three extra
    keys: ``registry_id`` (unified-index id), ``kind``
    (``m0_data_registry`` / ``pref_data_registry``), and ``row_id``
    (the row's ``id`` field).
    """
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        INDEX_PATH,
        load_indexed_registry,
        load_unified_index,
    )

    target = index_path or INDEX_PATH
    matches: list[JsonDict] = []
    for entry in load_unified_index(target):
        if entry["kind"] not in ("m0_data_registry", "pref_data_registry"):
            continue
        data = load_indexed_registry(target, entry)
        rows_key = "datasets"  # both kinds use 'datasets'
        for row in data.get(rows_key) or []:
            if not isinstance(row, Mapping):
                continue
            if is_share_alike(row.get("license")):
                matches.append(
                    {
                        "registry_id": entry["id"],
                        "kind": entry["kind"],
                        "row_id": str(row.get("id", "<no-id>")),
                        "license": row["license"],
                        "hf_dataset": row.get("hf_dataset"),
                        "environment": row.get("environment"),
                    }
                )
    return matches


def license_cascade(
    index_path: Path | None = None,
) -> dict[str, JsonDict]:
    """Trace each share-alike source → M0 env → bridge mappings.

    Returns a dict keyed by share-alike source row id with shape::

        {
          "<source row id>": {
            "license": "cc-by-sa-4.0",
            "hf_dataset": "hotpotqa/hot_qa",
            "m0_env_id": "search_grounded_qa",   # may be None for pref data
            "bridge_mappings": [
              {
                "registry_id": "m1_rlvr_envs",
                "mix": "rlvr1",
                "status": "m0_missing",
                "nemo_gym_env": "search_pivot_...",
              }, ...
            ],
            "live_chains": int,    # count of bridge_mappings with status == active
          }
        }

    Use ``live_chains`` to triage: cascades with ``live_chains > 0`` are
    *actively* propagating share-alike obligations; ``live_chains == 0``
    are latent (gap or blocked).
    """
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        INDEX_PATH,
        load_indexed_registry,
        load_unified_index,
    )

    target = index_path or INDEX_PATH

    # Build bridge_env_registry rows index keyed by m0_env_id so we can
    # look up downstream mappings in one walk.
    bridge_rows_by_m0_env: dict[str, list[JsonDict]] = defaultdict(list)
    for entry in load_unified_index(target):
        if entry["kind"] != "bridge_env_registry":
            continue
        data = load_indexed_registry(target, entry)
        for row in data.get("envs") or []:
            if not isinstance(row, Mapping):
                continue
            m0_env = row.get("m0_env_id")
            if not m0_env:
                continue
            bridge_rows_by_m0_env[str(m0_env)].append(
                {
                    "registry_id": entry["id"],
                    "mix": row.get("mix"),
                    "status": row.get("status"),
                    "nemo_gym_env": row.get("nemo_gym_env"),
                }
            )

    cascade: dict[str, JsonDict] = {}
    for source in find_share_alike_sources(target):
        # `m0_env_id` for the chain is the data registry row's
        # ``environment`` field (pref_data rows don't carry it).
        m0_env_id = source.get("environment")
        bridge_mappings = bridge_rows_by_m0_env.get(str(m0_env_id), []) if m0_env_id else []
        live = sum(1 for row in bridge_mappings if row.get("status") == "active")
        cascade[source["row_id"]] = {
            "registry_id": source["registry_id"],
            "kind": source["kind"],
            "license": source["license"],
            "hf_dataset": source.get("hf_dataset"),
            "m0_env_id": m0_env_id,
            "bridge_mappings": bridge_mappings,
            "live_chains": live,
        }
    return cascade


def format_cascade_report(cascade: Mapping[str, Any]) -> str:
    """Human-readable rendering of ``license_cascade`` output.

    Used by ``scripts/validate_data_registries.py --license-cascade``.
    Returns a multi-line string; callers print it.
    """
    if not cascade:
        return "license-cascade audit: no share-alike sources found ✓\n"
    lines = [
        f"license-cascade audit: {len(cascade)} share-alike source(s) flagged",
        "",
    ]
    for row_id, info in sorted(cascade.items()):
        live_count = info["live_chains"]
        live_marker = "⚠ LIVE" if live_count > 0 else "latent"
        lines.append(
            f"- {row_id} ({info['license']}, {info['kind']}) — {live_marker}: "
            f"{live_count} active bridge mapping(s)"
        )
        lines.append(f"    hf_dataset={info['hf_dataset']!r}")
        lines.append(f"    m0_env_id={info['m0_env_id']!r}")
        if not info["bridge_mappings"]:
            lines.append("    bridge_mappings: (none — no bridge references this M0 env yet)")
        else:
            lines.append("    bridge_mappings:")
            for mapping in info["bridge_mappings"]:
                lines.append(
                    f"      • {mapping['registry_id']} {mapping['mix']!r} "
                    f"→ {mapping['nemo_gym_env']!r} [{mapping['status']}]"
                )
    return "\n".join(lines) + "\n"


__all__ = [
    "SHARE_ALIKE_LICENSE_PREFIXES",
    "find_share_alike_sources",
    "format_cascade_report",
    "is_share_alike",
    "license_cascade",
]
