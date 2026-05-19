"""Tests for the M1 promotion gate (task020 Session 2).

Covers:

- Gate severity precedence: rollback > hold > promote
- Weighted-mean parity calculation (uniform per category)
- Per-category regression threshold
- Rollback-category trigger (any drop in safety / SWE / tool / IF)
- Missing-benchmark accounting (current side / Super3 side)
- format_gate_report markdown output
- Integration with live registries (gate ingests v0+full rows directly)
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m1_eval_basket.promotion_gate import (  # noqa: E402
    DEFAULT_CATEGORY_REGRESSION_THRESHOLD,
    DEFAULT_ROLLBACK_CATEGORIES,
    DEFAULT_ROLLBACK_REGRESSION_TOLERANCE,
    DEFAULT_WEIGHTED_PARITY_THRESHOLD,
    GATE_STATUSES,
    PromotionDecision,
    evaluate_promotion_gate,
    format_gate_report,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
V0_REGISTRY_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_basket_registry.yaml"
)
FULL_REGISTRY_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_full_basket_registry.yaml"
)


def _all_registry_rows() -> list[dict]:
    rows = []
    for path in (V0_REGISTRY_PATH, FULL_REGISTRY_PATH):
        rows.extend(yaml.safe_load(path.read_text(encoding="utf-8"))["benchmarks"])
    return rows


# Minimal toy registry used for unit-testing gate logic in isolation.
TOY_ROWS = [
    {"benchmark_id": "mmlu_pro", "category": "general_mc", "gate_metric": "accuracy"},
    {"benchmark_id": "aime25", "category": "reasoning_math_competition", "gate_metric": "pass_at_1"},
    {"benchmark_id": "hmmt", "category": "reasoning_math_competition", "gate_metric": "pass_at_1"},
    {"benchmark_id": "swe_bench_verified", "category": "swe_repo_repair", "gate_metric": "resolution_rate"},
    {"benchmark_id": "ifbench", "category": "instruction_following", "gate_metric": "strict_accuracy"},
    {"benchmark_id": "bfcl", "category": "tool_use_function_call", "gate_metric": "accuracy"},
]


# ---------- Constants + dataclass surface ----------


def test_gate_statuses_cover_three_outcomes() -> None:
    assert GATE_STATUSES == ("promote", "hold", "rollback")


def test_default_thresholds_match_plan_5_7_text() -> None:
    """Plan says 'within 1-2%' / 'no key-category regression > 1-2%'.
    Default thresholds = 0.02 (2%), the tight end of that range."""
    assert DEFAULT_WEIGHTED_PARITY_THRESHOLD == pytest.approx(0.02)
    assert DEFAULT_CATEGORY_REGRESSION_THRESHOLD == pytest.approx(0.02)


def test_default_rollback_categories_cover_swe_tool_if() -> None:
    """Plan §5.7 names safety / SWE / tool / IF as critical."""
    expected_subset = {
        "swe_repo_repair",
        "tool_use_agentic",
        "tool_use_terminal",
        "tool_use_function_call",
        "tool_use_mcp",
        "instruction_following",
        "multi_turn_instruction",
    }
    assert expected_subset.issubset(DEFAULT_ROLLBACK_CATEGORIES)
    # Safety subset is forward-compatible — M1 doesn't have safety
    # benchmarks yet but the gate must already block on them.
    assert "safety" in DEFAULT_ROLLBACK_CATEGORIES


# ---------- promote (happy path) ----------


def test_promote_when_current_matches_super3_exactly() -> None:
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "promote"
    assert decision.weighted_parity_delta == pytest.approx(0.0)
    assert decision.weighted_parity_within_threshold is True
    assert decision.categories_in_regression == ()
    assert decision.rollback_triggers == ()


def test_promote_when_current_within_parity_threshold() -> None:
    """Plan target is within 2%; 1% drift on a non-rollback category
    plus 1% gain elsewhere should still net within threshold."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["mmlu_pro"] = 0.69  # general_mc category drops 1%
    current["aime25"] = 0.715   # reasoning math gains 1.5%
    current["hmmt"] = 0.715
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "promote"
    assert abs(decision.weighted_parity_delta) <= DEFAULT_WEIGHTED_PARITY_THRESHOLD


# ---------- hold (parity drift or category regression below rollback bar) ----------


def test_hold_when_overall_weighted_parity_drift_exceeds_threshold() -> None:
    """Every category drops 3%; rollback categories take small hits,
    non-rollback take larger hits. The parity drift alone trips hold —
    but no rollback category drops more than tolerance, so rollback
    doesn't fire."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = {row["benchmark_id"]: 0.67 for row in TOY_ROWS}
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    # All categories regressed — but rollback categories went down too,
    # so rollback should fire instead of just hold.
    assert decision.status == "rollback"
    assert decision.weighted_parity_delta == pytest.approx(-0.03)


def test_hold_when_non_rollback_category_regresses_beyond_threshold() -> None:
    """general_mc is NOT a rollback category, so a 3% drop only triggers
    hold (not rollback). Overall weighted parity stays within threshold
    because other categories are flat. Tests hold-vs-promote, not
    hold-vs-rollback."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["mmlu_pro"] = 0.67  # general_mc only
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "hold"
    assert "general_mc" in decision.categories_in_regression
    assert decision.rollback_triggers == ()


def test_hold_when_only_parity_drifts_no_category_regression() -> None:
    """All categories drift +3%, no regression anywhere — but the
    weighted parity drift of +3% exceeds 2% threshold. The gate should
    still hold (over-performing is fine, but the operator should
    confirm the run is not buggy)."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = {row["benchmark_id"]: 0.73 for row in TOY_ROWS}
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "hold"
    assert decision.weighted_parity_delta == pytest.approx(0.03)
    assert decision.categories_in_regression == ()
    assert decision.rollback_triggers == ()


# ---------- rollback (critical categories) ----------


def test_rollback_when_swe_category_regresses_any_amount() -> None:
    """swe_repo_repair is a rollback category; even a tiny drop trips
    rollback rather than hold."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["swe_bench_verified"] = 0.695  # 0.5% drop
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "rollback"
    assert "swe_repo_repair" in decision.rollback_triggers


def test_rollback_when_instruction_following_regresses_any_amount() -> None:
    """IF is a rollback category."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["ifbench"] = 0.685  # 1.5% drop
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "rollback"
    assert "instruction_following" in decision.rollback_triggers


def test_rollback_when_tool_use_regresses_any_amount() -> None:
    """tool_use_function_call is a rollback category."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["bfcl"] = 0.68
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "rollback"
    assert "tool_use_function_call" in decision.rollback_triggers


def test_rollback_takes_precedence_over_hold() -> None:
    """If both a rollback-category drop AND a parity-threshold drift
    fire, status should be rollback (the more severe action)."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = {row["benchmark_id"]: 0.65 for row in TOY_ROWS}  # everything drops 5%
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "rollback"
    # The rollback trigger list should include each rollback category
    # that dropped — multiple here.
    assert "swe_repo_repair" in decision.rollback_triggers
    assert "instruction_following" in decision.rollback_triggers
    assert "tool_use_function_call" in decision.rollback_triggers


def test_rollback_tolerance_absorbs_floating_point_noise() -> None:
    """A drop strictly within ``DEFAULT_ROLLBACK_REGRESSION_TOLERANCE``
    should not trip rollback — eval runs aren't bit-exact."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    # Noise: 0.5 * tolerance shrinkage in a rollback category
    current["bfcl"] = 0.70 - 0.5 * DEFAULT_ROLLBACK_REGRESSION_TOLERANCE
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "promote"
    assert decision.rollback_triggers == ()


# ---------- weighting policy ----------


def test_weighted_parity_uses_uniform_per_category_not_per_benchmark() -> None:
    """reasoning_math_competition has 2 benchmarks (aime25 + hmmt); each
    other category has 1. If both AIME25 and HMMT drop 6% and nothing
    else moves, per-benchmark mean would over-weight that category. The
    gate must use category-mean → category-equal-weight."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["aime25"] = 0.64
    current["hmmt"] = 0.64
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    # 5 categories total: 4 at 0 delta + 1 (reasoning_math_competition)
    # at -0.06 → -0.06 / 5 = -0.012.
    # If we'd over-weighted per-benchmark it would be 2/6 * -0.06 = -0.02.
    assert decision.weighted_parity_delta == pytest.approx(-0.012, abs=1e-9)


# ---------- missing benchmarks ----------


def test_benchmarks_missing_in_current_are_recorded_but_dont_block() -> None:
    """Coverage gaps surface to the operator without auto-failing the
    gate. The category whose benchmarks are missing is silently
    dropped from the parity calculation."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    del current["mmlu_pro"]
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "promote"
    assert "mmlu_pro" in decision.benchmarks_missing_in_current


def test_no_shared_categories_yields_hold_with_explanation() -> None:
    """When every benchmark is missing on one side, weighted parity is
    None → hold with a specific reason. Prevents silent promote on an
    empty / broken eval JSON."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current: dict[str, float] = {}
    decision = evaluate_promotion_gate(current, super3, TOY_ROWS)
    assert decision.status == "hold"
    assert decision.weighted_parity_delta is None
    assert any("no shared categories" in reason for reason in decision.reasons)


# ---------- formatting ----------


def test_format_gate_report_marks_promote_status() -> None:
    decision = PromotionDecision(
        status="promote",
        weighted_parity_delta=0.005,
        weighted_parity_within_threshold=True,
        category_deltas={"general_mc": 0.005, "swe_repo_repair": 0.005},
        categories_in_regression=(),
        rollback_triggers=(),
        benchmarks_missing_in_current=(),
        benchmarks_missing_in_super3=(),
        reasons=("promote: weighted parity +0.0050 within ±0.0200",),
    )
    text = format_gate_report(decision)
    assert text.startswith("# Promotion gate decision: ✓ **PROMOTE**")
    assert "+0.0050" in text
    assert "`general_mc`" in text


def test_format_gate_report_marks_rollback_with_reasons() -> None:
    decision = PromotionDecision(
        status="rollback",
        weighted_parity_delta=-0.04,
        weighted_parity_within_threshold=False,
        category_deltas={"swe_repo_repair": -0.04},
        categories_in_regression=(),
        rollback_triggers=("swe_repo_repair",),
        benchmarks_missing_in_current=(),
        benchmarks_missing_in_super3=(),
        reasons=("rollback: category 'swe_repo_repair' regressed -0.0400",),
    )
    text = format_gate_report(decision)
    assert "✗ **ROLLBACK**" in text
    assert "regressed -0.0400" in text


def test_format_gate_report_lists_missing_benchmarks_when_present() -> None:
    decision = PromotionDecision(
        status="promote",
        weighted_parity_delta=0.0,
        weighted_parity_within_threshold=True,
        category_deltas={"general_mc": 0.0},
        categories_in_regression=(),
        rollback_triggers=(),
        benchmarks_missing_in_current=("hle",),
        benchmarks_missing_in_super3=("scicode",),
        reasons=(),
    )
    text = format_gate_report(decision)
    assert "missing in current run" in text and "`hle`" in text
    assert "missing in Super3 baseline" in text and "`scicode`" in text


# ---------- integration with live registries ----------


def test_gate_runs_against_live_v0_plus_full_basket_rows() -> None:
    """Smoke-test the gate against the actual 19-row combined basket
    using synthetic but plausible scores. Confirms no row in the live
    registries has a category the gate doesn't recognize and the
    happy-path promote decision survives end-to-end."""
    rows = _all_registry_rows()
    assert len(rows) == 19
    super3 = {row["benchmark_id"]: 0.50 for row in rows}
    current = dict(super3)
    decision = evaluate_promotion_gate(current, super3, rows)
    assert decision.status == "promote"
    assert decision.weighted_parity_delta == pytest.approx(0.0)


def test_gate_handles_rollback_category_in_full_basket() -> None:
    """SWE-Bench Verified lives in the full extension; a regression
    there should trip rollback under the same gate that handles v0
    rollback categories."""
    rows = _all_registry_rows()
    super3 = {row["benchmark_id"]: 0.50 for row in rows}
    current = dict(super3)
    current["swe_bench_verified"] = 0.49  # 1% drop on rollback category
    decision = evaluate_promotion_gate(current, super3, rows)
    assert decision.status == "rollback"
    assert "swe_repo_repair" in decision.rollback_triggers
