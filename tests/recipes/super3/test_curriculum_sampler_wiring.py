"""Tests for the curriculum sampler wiring in prepare_m1_agentic_sft
(task040 Session 2).

Covers:

- `_apply_curriculum_to_train` helper end-to-end:
  - Default `as_is` policy is a passthrough (back-compat)
  - `easy_first` reorders trivial → unknown → hard within train
  - `hard_first` reverses
  - `shuffle` with fixed seed is deterministic
- Pass-rates JSON wiring: loads file, drops rows above threshold,
  records counts in audit dict
- Audit dict shape: matches the manifest contract Session 2 introduces
- Error surfaces: missing pass-rates file / malformed JSON
- CLI flag dispatch (smoke): `build_parser` exposes the 4 new flags
  with correct defaults

Tests target the `_apply_curriculum_to_train` helper + `build_parser`
directly. End-to-end `prepare()` test would require pyarrow-dependent
M0 fixtures; that's collect-errored in sandbox so we skip it here and
exercise the small surface that matters.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# The prepare module imports pydantic lazily; the curriculum helper
# itself uses only stdlib + difficulty_sampler. Imports work cleanly
# in sandbox without pydantic; if a future change requires it, replace
# this stub with `pytest.importorskip("pydantic")`.
def _import_prepare_module():
    from nemotron.recipes.super3.milestones.m1_agentic_sft import prepare_m1_agentic_sft
    return prepare_m1_agentic_sft


def _row(*, bucket: str, source_id: str, environment: str = "math_reasoning_numeric") -> dict:
    return {
        "environment": environment,
        "metadata": {
            "difficulty_bucket": bucket,
            "m0_source_id": source_id,
        },
        "responses_create_params": {"input": []},
    }


# ---------- Helper: as_is default ----------


def test_as_is_policy_is_passthrough() -> None:
    """Default policy preserves order — guarantees back-compat for
    existing callers that don't pass --curriculum-policy."""
    mod = _import_prepare_module()
    rows = [
        _row(bucket="hard", source_id="h1"),
        _row(bucket="trivial", source_id="t1"),
        _row(bucket="unknown", source_id="u1"),
    ]
    reordered, audit = mod._apply_curriculum_to_train(rows, policy="as_is")
    assert [r["metadata"]["m0_source_id"] for r in reordered] == ["h1", "t1", "u1"]
    assert audit["policy"] == "as_is"
    assert audit["rows_in"] == 3
    assert audit["rows_out"] == 3
    assert audit["rows_dropped_solved"] == 0
    assert audit["pass_rates_provided"] is False


# ---------- Helper: policy reorderings ----------


def test_easy_first_policy_reorders_trivial_to_hard() -> None:
    mod = _import_prepare_module()
    rows = [
        _row(bucket="hard", source_id="h1"),
        _row(bucket="trivial", source_id="t1"),
        _row(bucket="unknown", source_id="u1"),
        _row(bucket="trivial", source_id="t2"),
    ]
    reordered, audit = mod._apply_curriculum_to_train(rows, policy="easy_first")
    ids = [r["metadata"]["m0_source_id"] for r in reordered]
    # Trivials first, then unknown, then hard
    assert ids.index("t1") < ids.index("u1") < ids.index("h1")
    assert ids.index("t2") < ids.index("u1")
    assert audit["policy"] == "easy_first"


def test_hard_first_policy_reverses_easy_first() -> None:
    mod = _import_prepare_module()
    rows = [
        _row(bucket="trivial", source_id="t1"),
        _row(bucket="hard", source_id="h1"),
        _row(bucket="unknown", source_id="u1"),
    ]
    reordered, _ = mod._apply_curriculum_to_train(rows, policy="hard_first")
    ids = [r["metadata"]["m0_source_id"] for r in reordered]
    assert ids.index("h1") < ids.index("u1") < ids.index("t1")


def test_shuffle_policy_deterministic_under_fixed_seed() -> None:
    mod = _import_prepare_module()
    rows = [_row(bucket="trivial", source_id=f"r{i}") for i in range(10)]
    a, _ = mod._apply_curriculum_to_train(rows, policy="shuffle", seed=42)
    b, _ = mod._apply_curriculum_to_train(rows, policy="shuffle", seed=42)
    c, _ = mod._apply_curriculum_to_train(rows, policy="shuffle", seed=43)
    a_ids = [r["metadata"]["m0_source_id"] for r in a]
    b_ids = [r["metadata"]["m0_source_id"] for r in b]
    c_ids = [r["metadata"]["m0_source_id"] for r in c]
    assert a_ids == b_ids
    assert a_ids != c_ids  # different seeds → different permutations


# ---------- Helper: pass_rates JSON wiring ----------


def test_pass_rates_drops_solved_rows_above_threshold(tmp_path: Path) -> None:
    mod = _import_prepare_module()
    rows = [
        _row(bucket="trivial", source_id="solved_a"),
        _row(bucket="hard", source_id="not_solved_b"),
        _row(bucket="unknown", source_id="solved_c"),
    ]
    pass_rates_path = tmp_path / "pass_rates.json"
    pass_rates_path.write_text(
        json.dumps({"solved_a": 0.95, "not_solved_b": 0.30, "solved_c": 0.99}),
        encoding="utf-8",
    )
    reordered, audit = mod._apply_curriculum_to_train(
        rows,
        policy="as_is",
        pass_rates_path=pass_rates_path,
        solved_threshold=0.9,
    )
    ids = [r["metadata"]["m0_source_id"] for r in reordered]
    assert ids == ["not_solved_b"]
    assert audit["rows_in"] == 3
    assert audit["rows_out"] == 1
    assert audit["rows_dropped_solved"] == 2
    assert audit["pass_rates_provided"] is True
    assert audit["solved_threshold"] == 0.9


def test_pass_rates_default_threshold_keeps_rows_at_exactly_threshold(tmp_path: Path) -> None:
    """`filter_solved` is strict > threshold; a row exactly at 0.9 stays."""
    mod = _import_prepare_module()
    rows = [_row(bucket="trivial", source_id="exactly_at_threshold")]
    pass_rates_path = tmp_path / "pass_rates.json"
    pass_rates_path.write_text(
        json.dumps({"exactly_at_threshold": 0.9}), encoding="utf-8"
    )
    reordered, audit = mod._apply_curriculum_to_train(
        rows, policy="as_is", pass_rates_path=pass_rates_path
    )
    assert len(reordered) == 1
    assert audit["rows_dropped_solved"] == 0


def test_pass_rates_combines_with_policy_reorder(tmp_path: Path) -> None:
    """Drop happens BEFORE policy reorder. Verify both effects compose."""
    mod = _import_prepare_module()
    rows = [
        _row(bucket="hard", source_id="solved_hard"),  # will drop
        _row(bucket="hard", source_id="hard_keep"),
        _row(bucket="trivial", source_id="trivial_keep"),
    ]
    pass_rates_path = tmp_path / "pass_rates.json"
    pass_rates_path.write_text(
        json.dumps({"solved_hard": 0.99}), encoding="utf-8"
    )
    reordered, audit = mod._apply_curriculum_to_train(
        rows,
        policy="easy_first",
        pass_rates_path=pass_rates_path,
    )
    ids = [r["metadata"]["m0_source_id"] for r in reordered]
    assert ids == ["trivial_keep", "hard_keep"]  # solved_hard dropped, easy_first ordered
    assert audit["rows_dropped_solved"] == 1


# ---------- Error surfaces ----------


def test_missing_pass_rates_file_raises_file_not_found(tmp_path: Path) -> None:
    mod = _import_prepare_module()
    rows = [_row(bucket="trivial", source_id="r1")]
    with pytest.raises(FileNotFoundError, match="curriculum-pass-rates-json"):
        mod._apply_curriculum_to_train(
            rows,
            policy="as_is",
            pass_rates_path=tmp_path / "nonexistent.json",
        )


def test_malformed_pass_rates_json_raises_value_error(tmp_path: Path) -> None:
    mod = _import_prepare_module()
    rows = [_row(bucket="trivial", source_id="r1")]
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
    with pytest.raises(ValueError, match="must be an object"):
        mod._apply_curriculum_to_train(
            rows, policy="as_is", pass_rates_path=bad_path
        )


# ---------- CLI flag surface ----------


def test_build_parser_exposes_curriculum_policy_choices() -> None:
    mod = _import_prepare_module()
    parser = mod.build_parser()
    args = parser.parse_args([])
    # Defaults
    assert args.curriculum_policy == "as_is"
    assert args.curriculum_seed == 0
    assert args.curriculum_pass_rates_json is None
    assert args.curriculum_solved_threshold == pytest.approx(0.9)


def test_build_parser_rejects_unknown_curriculum_policy() -> None:
    """Locking the 4 valid choices means typos surface at CLI parse
    time instead of producing a confusing reorder."""
    mod = _import_prepare_module()
    parser = mod.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--curriculum-policy", "nonsense"])


def test_build_parser_accepts_each_valid_policy() -> None:
    mod = _import_prepare_module()
    parser = mod.build_parser()
    for policy in ("as_is", "easy_first", "hard_first", "shuffle"):
        args = parser.parse_args(["--curriculum-policy", policy])
        assert args.curriculum_policy == policy


# ---------- Audit dict shape ----------


def test_audit_dict_shape_matches_manifest_contract() -> None:
    """The audit dict becomes the ``curriculum`` block in the
    manifest. Lock its shape so downstream consumers (W&B / dashboard)
    can rely on it."""
    mod = _import_prepare_module()
    rows = [_row(bucket="trivial", source_id="r1")]
    _, audit = mod._apply_curriculum_to_train(
        rows, policy="easy_first", seed=7
    )
    assert set(audit.keys()) == {
        "policy",
        "seed",
        "pass_rates_provided",
        "solved_threshold",
        "rows_in",
        "rows_out",
        "rows_dropped_solved",
    }
    assert audit["policy"] == "easy_first"
    assert audit["seed"] == 7
    assert audit["solved_threshold"] is None  # No pass_rates → None
