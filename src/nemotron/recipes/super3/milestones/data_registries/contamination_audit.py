# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Contamination_against semantic audit for the unified data registry.

task058 license/contamination follow-up (task030 Session 7). Sister
module to ``license_audit.py`` (share-alike cascade) and
``revision_audit.py`` (HF pin lint).

Today's schema layer enforces that ``contamination_against`` is present
on every ``m0_data_registry`` row and on operationally relevant
``pref_data_registry`` rows. This audit verifies the field is meaningful
rather than an empty list or placeholder-only list.

Two classes of finding:

- **Blockers** — empty list / non-list value / list containing
  non-string or empty-string entries. Authoring mistakes that should
  fail CI immediately.
- **Informational** — every entry contains a placeholder sentinel
  phrase (``"TBD"``, ``"todo"``, ``"pending"``, ``"manual review"``,
  ``"fixme"``). The field is non-empty but the operator hasn't filled
  in real eval names yet. Tracked rather than blocking so a row can
  land with a documented TODO and CI doesn't gate on it.

Sandbox-runnable; consumed by ``scripts/validate_data_registries.py
--check-contamination``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


# Substring matches (case-insensitive) that mark a placeholder entry.
# Lower-case + bare phrase form so "TBD" / "tbd" / "TBD review" all
# match. The set is closed and matching is delimiter-aware, so a real
# eval name like "Pending-Eval-2026" doesn't trigger false positives.
SENTINEL_PHRASES = frozenset(
    {
        "tbd",
        "todo",
        "to-do",
        "pending",
        "manual review",
        "fixme",
        "xxx",
        "n/a",
        "none",
    }
)


def is_placeholder_entry(entry: Any) -> bool:
    """True iff *entry* looks like an unfilled placeholder.

    Delimiter-aware prefix match (case-insensitive) against
    ``SENTINEL_PHRASES``. We accept exact sentinels plus forms like
    ``"TBD: AIME"`` or ``"FIXME later"``, while avoiding substring
    false positives such as ``"Pending-Eval-2026"``. Non-string
    inputs return False — those are caught as blockers by the type
    check, not as placeholders.
    """
    if not isinstance(entry, str):
        return False
    normalized = entry.strip().lower()
    if not normalized:
        return False
    for phrase in SENTINEL_PHRASES:
        if normalized == phrase:
            return True
        if normalized.startswith(f"{phrase} ") or normalized.startswith(f"{phrase}:"):
            return True
    return False


def _classify_row(row: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """Inspect a single row's ``contamination_against`` value.

    Returns ``(blocker_reasons, informational_reasons)`` — each a list
    of short reason strings (empty if the row is clean / not in that
    bucket). Caller collects these with the row's identity for the
    report.
    """
    value = row.get("contamination_against")
    blocker_reasons: list[str] = []
    informational_reasons: list[str] = []

    if value is None:
        blocker_reasons.append("contamination_against missing")
        return blocker_reasons, informational_reasons
    if not isinstance(value, list):
        blocker_reasons.append(
            f"contamination_against must be a list, got {type(value).__name__}"
        )
        return blocker_reasons, informational_reasons
    if not value:
        blocker_reasons.append("contamination_against is empty []")
        return blocker_reasons, informational_reasons

    # Type-check each entry first; bad types are authoring mistakes,
    # not placeholders.
    non_string_indices = [
        index for index, entry in enumerate(value) if not isinstance(entry, str)
    ]
    if non_string_indices:
        blocker_reasons.append(
            f"non-string entries at indices {non_string_indices}"
        )
    empty_string_indices = [
        index
        for index, entry in enumerate(value)
        if isinstance(entry, str) and not entry.strip()
    ]
    if empty_string_indices:
        blocker_reasons.append(
            f"empty-string entries at indices {empty_string_indices}"
        )
    if blocker_reasons:
        return blocker_reasons, informational_reasons

    # Every entry passed the type check. Check whether all entries are
    # placeholder sentinels — that's informational, not a blocker.
    if all(is_placeholder_entry(entry) for entry in value):
        informational_reasons.append(
            "all contamination_against entries are placeholders "
            f"(sentinels in {sorted(SENTINEL_PHRASES)})"
        )
    return blocker_reasons, informational_reasons


def classify_contamination_row(row: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """Public wrapper for row-level contamination posture.

    Returns ``(blocker_reasons, informational_reasons)`` using the same
    semantics as ``find_weak_contamination``. Other registry reports use
    this helper so blocker/informational posture does not drift.
    """
    return _classify_row(row)


def find_weak_contamination(
    index_path: Path | None = None,
) -> dict[str, list[JsonDict]]:
    """Walk m0_data_registry rows, classify each by contamination_against
    quality.

    Result shape::

        {
          "blockers": [
            {registry_id, row_id, hf_dataset, value, reasons: [...]},
            ...
          ],
          "informational": [
            {registry_id, row_id, hf_dataset, value, reasons: [...]},
            ...
          ],
        }

    ``pref_data_registry`` rows are included only after they are promoted
    enough to be operationally relevant: either ``m0_landed`` is true or
    ``hf_revision_pin_required`` is true.
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
        if entry["kind"] not in ("m0_data_registry", "pref_data_registry"):
            continue
        registry_path = (target.parent / entry["path"]).resolve()
        if not registry_path.is_file():
            continue
        data = load_registry_file(registry_path)
        for row in data.get("datasets") or []:
            if not isinstance(row, Mapping):
                continue
            if (
                entry["kind"] == "pref_data_registry"
                and not row.get("m0_landed")
                and not row.get("hf_revision_pin_required")
            ):
                continue
            blocker_reasons, informational_reasons = _classify_row(row)
            if not blocker_reasons and not informational_reasons:
                continue
            base = {
                "registry_id": entry["id"],
                "row_id": str(row.get("id", "<no-id>")),
                "hf_dataset": row.get("hf_dataset"),
                "value": row.get("contamination_against"),
            }
            if blocker_reasons:
                blockers.append({**base, "reasons": blocker_reasons})
            if informational_reasons:
                informational.append({**base, "reasons": informational_reasons})
    return {"blockers": blockers, "informational": informational}


def format_contamination_report(result: Mapping[str, list]) -> str:
    """Human-readable rendering of ``find_weak_contamination`` output."""
    blockers = result.get("blockers", [])
    informational = result.get("informational", [])
    if not blockers and not informational:
        return (
            "contamination audit: every audited m0_data_registry and "
            "pref_data_registry row has a real contamination_against list ✓\n"
        )
    lines: list[str] = []
    if blockers:
        lines.append(
            f"contamination audit: {len(blockers)} BLOCKER(s) — broken contamination_against fields"
        )
        lines.append("")
        for finding in blockers:
            reasons = "; ".join(finding["reasons"])
            lines.append(
                f"- ⚠ {finding['row_id']} ({finding['registry_id']}) "
                f"hf_dataset={finding['hf_dataset']!r} value={finding['value']!r} "
                f"— {reasons}"
            )
        lines.append("")
    if informational:
        lines.append(
            f"contamination audit: {len(informational)} informational — "
            "rows with only placeholder entries"
        )
        lines.append("")
        for finding in informational:
            reasons = "; ".join(finding["reasons"])
            lines.append(
                f"- {finding['row_id']} ({finding['registry_id']}) "
                f"value={finding['value']!r} — {reasons}"
            )
        lines.append("")
    if not blockers:
        lines.append("(no blockers — informational findings do not fail CI)")
    return "\n".join(lines) + "\n"


__all__ = [
    "SENTINEL_PHRASES",
    "classify_contamination_row",
    "find_weak_contamination",
    "format_contamination_report",
    "is_placeholder_entry",
]
