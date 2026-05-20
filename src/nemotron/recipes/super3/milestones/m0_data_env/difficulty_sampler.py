# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""W1 difficulty curriculum sampler (task040 Session 1).

Plan §6 W1 deliverable:

> Create difficulty curricula by filtering samples the current SFT model
> already solves consistently, then sorting the remaining samples by
> pass rate, judge confidence, and rollout length.

task008 added a 3-bucket categorical (``trivial`` / ``unknown`` /
``hard``) per row via ``metadata.difficulty_bucket``. This module
operates on that bucket signal — no numeric pass-rate / judge-confidence
required yet (those flow in via task032 rollout store in M2).

Three public helpers compose to produce a curriculum:

- ``bucket_rows(rows, policy)`` — re-order rows per a policy
  (``easy_first`` / ``hard_first`` / ``random`` / ``shuffle``)
- ``filter_solved(rows, pass_rates, threshold)`` — drop rows whose prior-
  checkpoint pass rate exceeds *threshold*
- ``weighted_sample(rows, weights, n, rng)`` — emit *n* rows with per-
  bucket sampling weights

Pure stdlib; sandbox-runnable; no external deps.
"""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


# Bucket vocabulary from task008's `_difficulty_for` / DIFFICULTY_*
# constants in m1_agentic_sft/prepare_m1_agentic_sft.py. Listed in
# easy → hard ordinal order so ``easy_first`` policy sorts ascending.
BUCKET_ORDER: tuple[str, ...] = ("trivial", "unknown", "hard")
"""Bucket ordering: trivial (easy) < unknown (in between) < hard."""

KNOWN_BUCKETS: frozenset[str] = frozenset(BUCKET_ORDER)

VALID_POLICIES: frozenset[str] = frozenset({
    "easy_first",
    "hard_first",
    "shuffle",
    "as_is",
})
"""Curriculum policy names accepted by ``bucket_rows``.

- ``easy_first`` — ascending bucket ordinal (trivial → hard)
- ``hard_first`` — descending (hard → trivial); used for finetuning
  models already strong on easy distributions
- ``shuffle`` — random permutation (operator supplies rng)
- ``as_is`` — passthrough; control / "no curriculum"
"""

DEFAULT_SOLVED_THRESHOLD = 0.9
"""Default pass-rate threshold for `filter_solved`.

Rows whose pass_rate strictly exceeds 0.9 are considered "already
solved" and dropped. Operators tighten for high-signal datasets (e.g.,
math) or loosen for noisier verifiers.
"""


def _bucket_of(row: Mapping[str, Any]) -> str:
    """Read the bucket from a row; default to ``unknown``.

    Rows missing ``metadata`` or ``metadata.difficulty_bucket`` are
    treated as ``unknown`` (the middle bucket) so the sampler doesn't
    silently drop unbucketed data.
    """
    metadata = row.get("metadata")
    if not isinstance(metadata, Mapping):
        return "unknown"
    bucket = metadata.get("difficulty_bucket")
    if not isinstance(bucket, str) or bucket not in KNOWN_BUCKETS:
        return "unknown"
    return bucket


def _row_id(row: Mapping[str, Any]) -> str | None:
    """Extract the row's stable id for pass-rate lookup.

    Order of preference: ``metadata.m0_source_id`` (task008 added) →
    ``metadata.source_id`` → top-level ``id`` / ``instance_id``. Returns
    None if none present (caller treats as no pass-rate data).
    """
    metadata = row.get("metadata") or {}
    for key in ("m0_source_id", "source_id"):
        value = metadata.get(key) if isinstance(metadata, Mapping) else None
        if isinstance(value, str) and value:
            return value
    for key in ("id", "instance_id"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def bucket_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    policy: str = "easy_first",
    rng: random.Random | None = None,
) -> list[Mapping[str, Any]]:
    """Return *rows* re-ordered per *policy*.

    Stable ordering within a bucket: rows tied on bucket keep their
    input order (so the same input twice gives the same output twice).
    The exception is ``shuffle``, which uses a deterministic seed if
    *rng* is provided (operator's responsibility).
    """
    if policy not in VALID_POLICIES:
        raise ValueError(
            f"unknown curriculum policy {policy!r}; expected one of "
            f"{sorted(VALID_POLICIES)}"
        )
    rows_list = list(rows)
    if policy == "as_is":
        return rows_list
    if policy == "shuffle":
        if rng is None:
            rng = random.Random()
        shuffled = rows_list.copy()
        rng.shuffle(shuffled)
        return shuffled
    descending = policy == "hard_first"
    ordinal = {bucket: idx for idx, bucket in enumerate(BUCKET_ORDER)}
    return sorted(
        rows_list,
        key=lambda r: ordinal.get(_bucket_of(r), ordinal["unknown"]),
        reverse=descending,
    )


def filter_solved(
    rows: Iterable[Mapping[str, Any]],
    *,
    pass_rates: Mapping[str, float] | None = None,
    threshold: float = DEFAULT_SOLVED_THRESHOLD,
) -> list[Mapping[str, Any]]:
    """Drop rows whose prior-checkpoint pass rate exceeds *threshold*.

    *pass_rates* maps row id (see ``_row_id``) to pass rate in [0, 1].
    Rows missing from the map are kept (no signal → no decision).
    *threshold* is strict: a row with pass_rate exactly equal to
    threshold is KEPT (might still teach the model something).

    Returns a new list; does not mutate input.
    """
    if pass_rates is None:
        return list(rows)
    out: list[Mapping[str, Any]] = []
    for row in rows:
        row_id = _row_id(row)
        if row_id is None:
            out.append(row)
            continue
        rate = pass_rates.get(row_id)
        if rate is None or rate <= threshold:
            out.append(row)
    return out


def weighted_sample(
    rows: Sequence[Mapping[str, Any]],
    *,
    weights: Mapping[str, float],
    n: int,
    rng: random.Random | None = None,
    replace: bool = False,
) -> list[Mapping[str, Any]]:
    """Sample *n* rows with per-bucket weights.

    *weights* maps bucket name to relative weight (does not have to sum
    to 1; the function normalises). Buckets absent from *weights* get
    weight 0 (rows in those buckets are excluded).

    With ``replace=False`` (default), at most ``len(rows)`` rows are
    returned even if *n* is larger; if every input row has weight 0
    (all buckets excluded), returns ``[]``. With ``replace=True``,
    returns exactly *n* rows by sampling with replacement.

    Deterministic given fixed *rng*. The default rng (``None``) uses a
    fresh ``random.Random()`` — production callers SHOULD pass a seeded
    rng so curriculum runs are reproducible.
    """
    if n <= 0:
        return []
    rng = rng if rng is not None else random.Random()
    rows_list = list(rows)
    if not rows_list:
        return []

    per_row_weights: list[float] = []
    for row in rows_list:
        bucket = _bucket_of(row)
        w = float(weights.get(bucket, 0.0))
        if w < 0:
            raise ValueError(
                f"weights must be non-negative; got {w} for bucket {bucket!r}"
            )
        per_row_weights.append(w)

    total = sum(per_row_weights)
    if total <= 0:
        return []

    if replace:
        return rng.choices(rows_list, weights=per_row_weights, k=n)

    cap = min(n, len(rows_list))
    # Without replacement: use weighted-without-replacement via repeated
    # selection from remaining pool. ``random.choices`` is with-replacement;
    # for without, we shrink the pool each round.
    pool: list[tuple[Mapping[str, Any], float]] = list(zip(rows_list, per_row_weights))
    picked: list[Mapping[str, Any]] = []
    while len(picked) < cap and pool:
        weights_only = [w for _, w in pool]
        if sum(weights_only) <= 0:
            break
        idx = rng.choices(range(len(pool)), weights=weights_only, k=1)[0]
        row, _w = pool.pop(idx)
        picked.append(row)
    return picked


__all__ = [
    "BUCKET_ORDER",
    "DEFAULT_SOLVED_THRESHOLD",
    "KNOWN_BUCKETS",
    "VALID_POLICIES",
    "bucket_rows",
    "filter_solved",
    "weighted_sample",
]
