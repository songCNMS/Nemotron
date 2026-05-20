"""Tests for the W1 difficulty curriculum sampler (task040 Session 1).

Covers:

- ``BUCKET_ORDER`` / ``KNOWN_BUCKETS`` / ``VALID_POLICIES`` constants
- ``bucket_rows`` — easy_first / hard_first / shuffle / as_is policies;
  stable ordering within a bucket; unknown / missing bucket handling
- ``filter_solved`` — threshold semantics; missing-row pass-through;
  row-id extraction order
- ``weighted_sample`` — per-bucket weighting; replace vs no-replace; zero
  weights; deterministic rng; n>len behavior
"""

from __future__ import annotations

import random

import pytest


from nemotron.recipes.super3.milestones.m0_data_env.difficulty_sampler import (  # noqa: E402
    BUCKET_ORDER,
    DEFAULT_SOLVED_THRESHOLD,
    KNOWN_BUCKETS,
    VALID_POLICIES,
    bucket_rows,
    filter_solved,
    weighted_sample,
)


def _row(
    *,
    bucket: str | None = "unknown",
    source_id: str | None = None,
    m0_source_id: str | None = None,
    instance_id: str | None = None,
    payload: str = "",
) -> dict:
    """Synthesize a row in the M0 → M1 metadata shape."""
    metadata: dict = {}
    if bucket is not None:
        metadata["difficulty_bucket"] = bucket
    if source_id is not None:
        metadata["source_id"] = source_id
    if m0_source_id is not None:
        metadata["m0_source_id"] = m0_source_id
    out: dict = {"payload": payload}
    if metadata:
        out["metadata"] = metadata
    if instance_id is not None:
        out["instance_id"] = instance_id
    return out


# ---------- Constants ----------


def test_bucket_order_matches_task008_vocabulary() -> None:
    """task008 added the 3-bucket categorical (trivial / unknown /
    hard); the sampler must match exactly or downstream rows get
    re-bucketed as unknown."""
    assert BUCKET_ORDER == ("trivial", "unknown", "hard")
    assert KNOWN_BUCKETS == {"trivial", "unknown", "hard"}


def test_valid_policies_lock_the_four_supported_modes() -> None:
    assert VALID_POLICIES == {"easy_first", "hard_first", "shuffle", "as_is"}


def test_default_solved_threshold_is_0_9() -> None:
    """0.9 = "model gets this right 9 times out of 10" — common
    industry default. Operators tighten or loosen, but the default
    must be documented."""
    assert DEFAULT_SOLVED_THRESHOLD == pytest.approx(0.9)


# ---------- bucket_rows ----------


def test_easy_first_sorts_trivial_before_unknown_before_hard() -> None:
    rows = [
        _row(bucket="hard", payload="h1"),
        _row(bucket="trivial", payload="t1"),
        _row(bucket="unknown", payload="u1"),
        _row(bucket="hard", payload="h2"),
        _row(bucket="trivial", payload="t2"),
    ]
    ordered = bucket_rows(rows, policy="easy_first")
    payloads = [r["payload"] for r in ordered]
    # All trivials first, then all unknowns, then all hards
    assert payloads.index("t1") < payloads.index("u1") < payloads.index("h1")
    assert payloads.index("t2") < payloads.index("u1") < payloads.index("h2")


def test_hard_first_reverses_easy_first() -> None:
    rows = [
        _row(bucket="trivial", payload="t1"),
        _row(bucket="hard", payload="h1"),
        _row(bucket="unknown", payload="u1"),
    ]
    ordered = bucket_rows(rows, policy="hard_first")
    payloads = [r["payload"] for r in ordered]
    assert payloads.index("h1") < payloads.index("u1") < payloads.index("t1")


def test_bucket_rows_is_stable_within_a_bucket() -> None:
    """Two rows with the same bucket retain input order — important
    for reproducibility across runs."""
    rows = [
        _row(bucket="trivial", payload="t1"),
        _row(bucket="trivial", payload="t2"),
        _row(bucket="trivial", payload="t3"),
    ]
    ordered = bucket_rows(rows, policy="easy_first")
    assert [r["payload"] for r in ordered] == ["t1", "t2", "t3"]


def test_unknown_bucket_treated_as_middle_not_dropped() -> None:
    """Rows with missing or unknown bucket land in the middle ordinal
    slot — not silently dropped."""
    rows = [
        _row(bucket="hard", payload="h1"),
        {"payload": "no_metadata"},  # missing metadata
        _row(bucket=None, payload="no_bucket"),  # metadata but no difficulty_bucket
        _row(bucket="invalid_value", payload="bad_bucket"),  # unknown bucket value
        _row(bucket="trivial", payload="t1"),
    ]
    ordered = bucket_rows(rows, policy="easy_first")
    payloads = [r["payload"] for r in ordered]
    # All five rows present
    assert len(ordered) == 5
    # trivial first, hard last, unknowns in the middle
    assert payloads[0] == "t1"
    assert payloads[-1] == "h1"
    middle = set(payloads[1:4])
    assert middle == {"no_metadata", "no_bucket", "bad_bucket"}


def test_as_is_policy_passes_through() -> None:
    rows = [
        _row(bucket="hard", payload="h1"),
        _row(bucket="trivial", payload="t1"),
    ]
    out = bucket_rows(rows, policy="as_is")
    assert [r["payload"] for r in out] == ["h1", "t1"]


def test_shuffle_with_seeded_rng_is_deterministic() -> None:
    """Reproducibility: same rng seed → same shuffle. Critical for
    curriculum runs that need to be repeatable."""
    rows = [_row(bucket="trivial", payload=f"r{i}") for i in range(5)]
    shuffled_a = bucket_rows(rows, policy="shuffle", rng=random.Random(42))
    shuffled_b = bucket_rows(rows, policy="shuffle", rng=random.Random(42))
    assert [r["payload"] for r in shuffled_a] == [r["payload"] for r in shuffled_b]


def test_unknown_policy_raises() -> None:
    with pytest.raises(ValueError, match="unknown curriculum policy"):
        bucket_rows([], policy="nonsense")


# ---------- filter_solved ----------


def test_filter_solved_drops_rows_above_threshold() -> None:
    rows = [
        _row(m0_source_id="a", payload="solved"),
        _row(m0_source_id="b", payload="hard"),
        _row(m0_source_id="c", payload="unrated"),
    ]
    pass_rates = {"a": 0.95, "b": 0.30}  # 'c' not rated → keep
    out = filter_solved(rows, pass_rates=pass_rates, threshold=0.9)
    payloads = [r["payload"] for r in out]
    assert "solved" not in payloads
    assert "hard" in payloads
    assert "unrated" in payloads


def test_filter_solved_keeps_row_exactly_at_threshold() -> None:
    """Strict > threshold means a row with pass_rate exactly 0.9 stays
    (might still have something to teach)."""
    rows = [_row(m0_source_id="a", payload="threshold")]
    pass_rates = {"a": 0.9}
    out = filter_solved(rows, pass_rates=pass_rates, threshold=0.9)
    assert len(out) == 1


def test_filter_solved_no_pass_rates_keeps_everything() -> None:
    """No signal → no decision. Caller may want to call ``filter_solved``
    unconditionally in a pipeline even before pass rates exist."""
    rows = [_row(payload=f"r{i}") for i in range(5)]
    out = filter_solved(rows, pass_rates=None)
    assert len(out) == 5


def test_filter_solved_keys_on_m0_source_id_preferred_over_instance_id() -> None:
    """Row id preference: metadata.m0_source_id > metadata.source_id >
    top-level id > instance_id. Lock the preference order."""
    rows = [
        # m0_source_id wins over instance_id
        _row(m0_source_id="prefer_me", instance_id="ignored", payload="r1"),
        # source_id used when m0_source_id absent
        _row(source_id="src_b", payload="r2"),
        # instance_id used when both metadata ids absent
        {"instance_id": "inst_c", "metadata": {"difficulty_bucket": "hard"}, "payload": "r3"},
    ]
    pass_rates = {"prefer_me": 0.99, "src_b": 0.99, "inst_c": 0.99}
    out = filter_solved(rows, pass_rates=pass_rates, threshold=0.9)
    # All three should be dropped — id resolution worked
    assert out == []


def test_filter_solved_rows_without_id_pass_through() -> None:
    rows = [
        {"payload": "no_id_at_all"},
        _row(m0_source_id="b", payload="rated"),
    ]
    pass_rates = {"b": 0.99}
    out = filter_solved(rows, pass_rates=pass_rates, threshold=0.9)
    payloads = [r["payload"] for r in out]
    assert "no_id_at_all" in payloads  # kept (no id)
    assert "rated" not in payloads     # dropped (solved)


# ---------- weighted_sample ----------


def test_weighted_sample_respects_per_bucket_weights() -> None:
    """1000 trials with weights 0.0 / 1.0 / 0.0 → every sampled row
    must be unknown bucket."""
    rows = [
        _row(bucket="trivial", payload=f"t{i}") for i in range(20)
    ] + [
        _row(bucket="unknown", payload=f"u{i}") for i in range(20)
    ] + [
        _row(bucket="hard", payload=f"h{i}") for i in range(20)
    ]
    weights = {"trivial": 0.0, "unknown": 1.0, "hard": 0.0}
    rng = random.Random(0)
    picked = weighted_sample(rows, weights=weights, n=10, rng=rng, replace=True)
    buckets = {r["metadata"]["difficulty_bucket"] for r in picked}
    assert buckets == {"unknown"}


def test_weighted_sample_deterministic_under_fixed_rng() -> None:
    rows = [_row(bucket="trivial", payload=f"t{i}") for i in range(10)]
    weights = {"trivial": 1.0}
    a = weighted_sample(rows, weights=weights, n=5, rng=random.Random(7), replace=True)
    b = weighted_sample(rows, weights=weights, n=5, rng=random.Random(7), replace=True)
    assert [r["payload"] for r in a] == [r["payload"] for r in b]


def test_weighted_sample_without_replace_caps_at_pool_size() -> None:
    rows = [_row(bucket="trivial", payload=f"t{i}") for i in range(3)]
    weights = {"trivial": 1.0}
    out = weighted_sample(
        rows, weights=weights, n=100, rng=random.Random(0), replace=False
    )
    assert len(out) == 3


def test_weighted_sample_with_replace_emits_exactly_n() -> None:
    rows = [_row(bucket="trivial", payload="t0")]
    weights = {"trivial": 1.0}
    out = weighted_sample(
        rows, weights=weights, n=4, rng=random.Random(0), replace=True
    )
    assert len(out) == 4
    # Every pick must be the only row available
    assert all(r["payload"] == "t0" for r in out)


def test_weighted_sample_all_zero_weights_returns_empty() -> None:
    """If the operator zeros every bucket they actually have data for,
    the sample is empty — fail loud (return []) rather than silently
    drawing equal-weight."""
    rows = [
        _row(bucket="trivial", payload="t0"),
        _row(bucket="hard", payload="h0"),
    ]
    weights = {"trivial": 0.0, "hard": 0.0}
    out = weighted_sample(rows, weights=weights, n=5, rng=random.Random(0), replace=True)
    assert out == []


def test_weighted_sample_rejects_negative_weights() -> None:
    rows = [_row(bucket="trivial", payload="t0")]
    with pytest.raises(ValueError, match="non-negative"):
        weighted_sample(rows, weights={"trivial": -1.0}, n=1, replace=True)


def test_weighted_sample_buckets_without_weight_excluded() -> None:
    """A bucket not in the weights dict has weight 0 → rows in that
    bucket are excluded."""
    rows = [
        _row(bucket="trivial", payload="t0"),
        _row(bucket="hard", payload="h0"),
    ]
    # Only trivial gets weight; hard absent from dict → weight 0
    out = weighted_sample(
        rows, weights={"trivial": 1.0}, n=10, rng=random.Random(0), replace=True
    )
    assert all(r["payload"] == "t0" for r in out)
    assert len(out) == 10


def test_weighted_sample_n_zero_returns_empty() -> None:
    rows = [_row(bucket="trivial", payload="t0")]
    out = weighted_sample(rows, weights={"trivial": 1.0}, n=0)
    assert out == []
