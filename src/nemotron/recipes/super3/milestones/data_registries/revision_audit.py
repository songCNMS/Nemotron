# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""HuggingFace revision-pin audit for the unified data registry.

task058 license/contamination follow-up (task030 Session 6). Sister
module to ``license_audit.py``. Production data drift silently when a
loader is given a floating reference (``main`` / ``master`` / no
revision at all) — the dataset on HF can be reshaped overnight and the
next prep run silently consumes the new shape.

This module surfaces two classes of finding:

- **Blockers** — rows in ``m0_data_registry`` that are *actively used*
  by the M0 prep but don't carry a pinned commit SHA. Exit 1 in CI
  mode so PR pre-merge gates fire.
- **Informational** — rows in ``pref_data_registry`` that declare
  ``hf_revision_pin_required: true`` but don't have a pin yet. Those
  are *candidate* preference sources (HelpSteer-2 / UltraFeedback /
  Orca DPO pairs); task018 Session 2 picks one and pins it. Reporting
  them keeps the to-do visible without failing CI.

Sandbox-runnable; consumed by ``scripts/validate_data_registries.py
--check-revision-pins``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


JsonDict = dict[str, Any]


# Floating refs that HF resolves at fetch time — not real pins. Empty
# string and None also count as unpinned. The set is intentionally
# closed (no glob match) so a real branch named `production` doesn't
# accidentally trip the audit; if a team needs a new floating ref
# detected, add it here explicitly.
FLOATING_REVISION_REFS = frozenset({"main", "master", "head", "latest", ""})


def is_pinned(hf_revision: Any) -> bool:
    """True iff *hf_revision* is a real commit-pinned reference.

    Pin = non-empty string that isn't a floating ref. Case-insensitive
    comparison so ``MAIN`` / ``Main`` are equally floating. Defensive
    against None / non-string inputs (those return False — caller can
    treat as unpinned).
    """
    if not isinstance(hf_revision, str):
        return False
    normalized = hf_revision.strip().lower()
    if not normalized:
        return False
    return normalized not in FLOATING_REVISION_REFS


def find_unpinned_revisions(
    index_path: Path | None = None,
) -> dict[str, list[JsonDict]]:
    """Walk the unified index, return categorised unpinned findings.

    Result shape::

        {
          "blockers": [{registry_id, row_id, hf_dataset, hf_revision, ...}],
          "informational": [{registry_id, row_id, hf_dataset, hf_revision, ...}],
        }

    - **blockers**: ``m0_data_registry`` rows with unpinned
      ``hf_revision``. Either the field is missing, or its value is a
      floating ref. These rows are part of the M0 prep pipeline; a
      drift here propagates downstream silently.
    - **informational**: ``pref_data_registry`` rows that *declare*
      ``hf_revision_pin_required: true`` but haven't been pinned yet.
      Tracking issue rather than a release blocker — those are
      candidate sources waiting to be picked.
    """
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        INDEX_PATH,
        load_registry_file,
        load_unified_index,
    )

    target = index_path or INDEX_PATH
    blockers: list[JsonDict] = []
    informational: list[JsonDict] = []

    for entry in load_unified_index(target):
        kind = entry["kind"]
        if kind not in ("m0_data_registry", "pref_data_registry"):
            continue
        registry_path = (target.parent / entry["path"]).resolve()
        if not registry_path.is_file():
            continue
        data = load_registry_file(registry_path)
        rows = data.get("datasets") or []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            hf_revision = row.get("hf_revision")
            if is_pinned(hf_revision):
                continue
            row_id = str(row.get("id", "<no-id>"))
            finding = {
                "registry_id": entry["id"],
                "kind": kind,
                "row_id": row_id,
                "hf_dataset": row.get("hf_dataset"),
                "hf_revision": hf_revision,
            }
            if kind == "m0_data_registry":
                # Active prep pipeline row; unpinned = blocker.
                blockers.append(finding)
            else:
                # pref_data_registry candidate. Flag iff the row
                # declares it *should* be pinned (some pref rows may
                # be intentionally floating during exploration).
                if row.get("hf_revision_pin_required"):
                    informational.append(finding)
    return {"blockers": blockers, "informational": informational}


def format_revision_audit_report(result: Mapping[str, list]) -> str:
    """Human-readable rendering of ``find_unpinned_revisions`` output.

    Used by ``scripts/validate_data_registries.py --check-revision-pins``.
    Returns a multi-line string; callers print it.
    """
    blockers = result.get("blockers", [])
    informational = result.get("informational", [])
    if not blockers and not informational:
        return "revision-pin audit: all production data registry rows pinned ✓\n"

    lines = []
    if blockers:
        lines.append(
            f"revision-pin audit: {len(blockers)} BLOCKER(s) — unpinned m0_data_registry rows"
        )
        lines.append("")
        for finding in blockers:
            lines.append(
                f"- ⚠ {finding['row_id']} ({finding['registry_id']}) "
                f"hf_dataset={finding['hf_dataset']!r} "
                f"hf_revision={finding['hf_revision']!r}"
            )
        lines.append("")
    if informational:
        lines.append(
            f"revision-pin audit: {len(informational)} informational — "
            "pref_data_registry candidate(s) pending task018 Session 2 pin"
        )
        lines.append("")
        for finding in informational:
            lines.append(
                f"- {finding['row_id']} ({finding['registry_id']}) "
                f"hf_dataset={finding['hf_dataset']!r} "
                f"hf_revision={finding['hf_revision']!r}"
            )
        lines.append("")
    if not blockers:
        lines.append("(no blockers — informational findings do not fail CI)")
    return "\n".join(lines) + "\n"


__all__ = [
    "FLOATING_REVISION_REFS",
    "find_unpinned_revisions",
    "format_revision_audit_report",
    "is_pinned",
]
