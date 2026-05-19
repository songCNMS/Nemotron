"""Tests for the M1 per-category gap analysis (task020 Session 4).

Covers:

- ``CategoryGap`` / ``BenchmarkGap`` dataclass surface + sorting
- ``analyze_gaps`` — single-category drill-down, multi-category sorted
  ranking, per-benchmark contribution math
- Missing benchmarks handled (one side / both sides)
- ``count_categories_below_threshold`` math
- ``format_gap_analysis`` markdown shape (header / table / drill-down)
- Live 19-row integration against v0 + full registries
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m1_eval_basket.gap_analysis import (  # noqa: E402
    DEFAULT_GAP_THRESHOLD,
    BenchmarkGap,
    CategoryGap,
    analyze_gaps,
    count_categories_below_threshold,
    format_gap_analysis,
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


# Multi-benchmark toy registry — categories chosen so we can exercise
# per-benchmark sorting (reasoning_math has 2 rows) and missing-data
# branches.
TOY_ROWS = [
    {"benchmark_id": "mmlu_pro", "category": "general_mc", "gate_metric": "accuracy"},
    {"benchmark_id": "aime25", "category": "reasoning_math", "gate_metric": "pass_at_1"},
    {"benchmark_id": "hmmt", "category": "reasoning_math", "gate_metric": "pass_at_1"},
    {"benchmark_id": "swe_bench_verified", "category": "swe_repo_repair", "gate_metric": "resolution_rate"},
    {"benchmark_id": "ifbench", "category": "instruction_following", "gate_metric": "strict_accuracy"},
]


# ---------- Dataclass surface ----------


def test_default_gap_threshold_matches_plan_5_7_text() -> None:
    """Plan §5.7 promotion gate uses 1-2 % — gap threshold defaults to
    the tight end so 'category behind' aligns with 'category in
    regression' in the promotion gate report."""
    assert DEFAULT_GAP_THRESHOLD == pytest.approx(0.02)


def test_benchmark_gap_dataclass_holds_optional_values() -> None:
    bg = BenchmarkGap(benchmark_id="aime25", current=0.6, super3=0.7, gap=-0.1)
    assert bg.gap == pytest.approx(-0.1)
    bg_missing = BenchmarkGap(benchmark_id="hle", current=None, super3=0.5, gap=None)
    assert bg_missing.gap is None


# ---------- Single-category drill-down ----------


def test_analyze_gaps_returns_one_category_gap_per_category() -> None:
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    expected_categories = {row["category"] for row in TOY_ROWS}
    assert {cg.category for cg in gaps} == expected_categories


def test_category_gap_means_correctly_computed_for_two_benchmark_category() -> None:
    """reasoning_math has 2 benchmarks (aime25 + hmmt). Mean should
    average them, not pick one."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["aime25"] = 0.50
    current["hmmt"] = 0.60
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    rm = next(cg for cg in gaps if cg.category == "reasoning_math")
    assert rm.current_mean == pytest.approx(0.55)
    assert rm.super3_mean == pytest.approx(0.70)
    assert rm.gap == pytest.approx(-0.15)


def test_benchmark_drill_down_sorted_by_gap_ascending() -> None:
    """Operator should see the worst-contributing benchmark first
    within each category drill-down."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["aime25"] = 0.50  # gap -0.20 (worst)
    current["hmmt"] = 0.65    # gap -0.05
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    rm = next(cg for cg in gaps if cg.category == "reasoning_math")
    assert rm.benchmark_gaps[0].benchmark_id == "aime25"
    assert rm.benchmark_gaps[1].benchmark_id == "hmmt"


# ---------- Multi-category ranking ----------


def test_categories_sorted_worst_gap_first() -> None:
    """The category most behind Super3 should sort to the top of the
    returned list so the markdown table shows priorities first."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["mmlu_pro"] = 0.65            # general_mc gap -0.05
    current["swe_bench_verified"] = 0.55  # swe gap -0.15 (worst)
    current["ifbench"] = 0.68             # if gap -0.02
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    assert gaps[0].category == "swe_repo_repair"
    assert gaps[0].gap == pytest.approx(-0.15)


def test_categories_without_gap_sort_to_end() -> None:
    """Categories with no computable gap (one side empty) should sort
    after categories with a real gap. They have no actionable signal
    but should still appear so the operator knows they were missing."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    # Remove all reasoning_math benchmarks from current → that
    # category has no current_mean → gap = None.
    del current["aime25"]
    del current["hmmt"]
    current["mmlu_pro"] = 0.65  # general_mc gap -0.05 (computable)
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    # reasoning_math must come last; the worst computable gap first
    assert gaps[-1].category == "reasoning_math"
    assert gaps[-1].gap is None


# ---------- Missing benchmarks ----------


def test_benchmark_gap_is_none_when_either_side_missing() -> None:
    super3 = {"aime25": 0.7}  # hmmt missing on super3 side
    current = {"aime25": 0.6, "hmmt": 0.5}
    rows = [
        {"benchmark_id": "aime25", "category": "reasoning_math"},
        {"benchmark_id": "hmmt", "category": "reasoning_math"},
    ]
    gaps = analyze_gaps(current, super3, rows)
    rm = next(cg for cg in gaps if cg.category == "reasoning_math")
    hmmt_gap = next(bg for bg in rm.benchmark_gaps if bg.benchmark_id == "hmmt")
    aime_gap = next(bg for bg in rm.benchmark_gaps if bg.benchmark_id == "aime25")
    assert hmmt_gap.gap is None
    assert aime_gap.gap == pytest.approx(-0.1)


def test_category_mean_excludes_missing_benchmarks() -> None:
    """When one benchmark is missing on the current side, the category
    mean is computed over the remaining benchmark — partial coverage
    shouldn't drag the mean to zero."""
    super3 = {"aime25": 0.7, "hmmt": 0.7}
    current = {"aime25": 0.6}  # hmmt missing
    rows = [
        {"benchmark_id": "aime25", "category": "reasoning_math"},
        {"benchmark_id": "hmmt", "category": "reasoning_math"},
    ]
    gaps = analyze_gaps(current, super3, rows)
    rm = next(cg for cg in gaps if cg.category == "reasoning_math")
    # current_mean should average aime25 alone since hmmt is missing
    assert rm.current_mean == pytest.approx(0.6)
    # super3_mean averages both
    assert rm.super3_mean == pytest.approx(0.7)
    assert rm.gap == pytest.approx(-0.1)


# ---------- count_categories_below_threshold ----------


def test_count_below_threshold_only_counts_computable_gaps() -> None:
    gaps = [
        CategoryGap(category="a", current_mean=0.5, super3_mean=0.7, gap=-0.2, benchmark_gaps=()),
        CategoryGap(category="b", current_mean=0.65, super3_mean=0.7, gap=-0.05, benchmark_gaps=()),
        CategoryGap(category="c", current_mean=None, super3_mean=0.7, gap=None, benchmark_gaps=()),
        CategoryGap(category="d", current_mean=0.7, super3_mean=0.7, gap=0.0, benchmark_gaps=()),
    ]
    # a (-0.20) below -0.02; b (-0.05) below -0.02; c (None) skipped; d (0.0) not below
    assert count_categories_below_threshold(gaps) == 2


def test_count_below_threshold_respects_custom_threshold() -> None:
    gaps = [
        CategoryGap(category="a", current_mean=0.5, super3_mean=0.6, gap=-0.10, benchmark_gaps=()),
        CategoryGap(category="b", current_mean=0.55, super3_mean=0.6, gap=-0.05, benchmark_gaps=()),
    ]
    # Tight threshold (1%) catches both; loose threshold (8%) catches one
    assert count_categories_below_threshold(gaps, threshold=0.01) == 2
    assert count_categories_below_threshold(gaps, threshold=0.08) == 1


# ---------- format_gap_analysis ----------


def test_format_gap_analysis_renders_summary_and_table() -> None:
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["swe_bench_verified"] = 0.50  # behind by 0.20
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    text = format_gap_analysis(gaps)
    assert text.startswith("# Gap analysis vs Super3")
    assert "1 category/categories more than 2.00% behind Super3" in text
    assert "`swe_repo_repair`" in text
    assert "behind" in text  # status column


def test_format_gap_analysis_includes_drill_down_for_behind_categories() -> None:
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    current["aime25"] = 0.50  # contributes worst within reasoning_math
    current["hmmt"] = 0.65
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    text = format_gap_analysis(gaps)
    assert "## Drill-down" in text
    assert "### `reasoning_math`" in text
    # The drill-down must show both benchmarks, worst-first.
    aime_idx = text.find("`aime25`")
    hmmt_idx = text.find("`hmmt`")
    assert aime_idx != -1 and hmmt_idx != -1
    assert aime_idx < hmmt_idx


def test_format_gap_analysis_handles_empty_input() -> None:
    text = format_gap_analysis([])
    assert "registry empty" in text or "zero benchmarks" in text


def test_format_gap_analysis_omits_drill_down_when_all_on_par() -> None:
    """A run where every category is within threshold should not emit
    a drill-down section — keeps the report clean for healthy runs."""
    super3 = {row["benchmark_id"]: 0.70 for row in TOY_ROWS}
    current = dict(super3)
    gaps = analyze_gaps(current, super3, TOY_ROWS)
    text = format_gap_analysis(gaps)
    assert "## Drill-down" not in text


# ---------- Live registry integration ----------


def test_analyze_gaps_runs_against_live_19_row_basket() -> None:
    """Smoke test against the actual v0+full 19-row registry. Confirms
    every category in the live basket produces a CategoryGap row when
    paired with synthetic scores covering all 19 benchmarks."""
    rows = _all_registry_rows()
    assert len(rows) == 19
    super3 = {row["benchmark_id"]: 0.50 for row in rows}
    current = dict(super3)
    gaps = analyze_gaps(current, super3, rows)
    expected_categories = {row["category"] for row in rows}
    assert {cg.category for cg in gaps} == expected_categories
    # Every category should be exactly on par (gap == 0)
    for cg in gaps:
        assert cg.gap == pytest.approx(0.0)


def test_live_basket_surfaces_worst_category_first() -> None:
    """When one category in the full basket is dragged down, it must
    appear first in the ranking — exercises the sort against the live
    category set, not just the toy registry."""
    rows = _all_registry_rows()
    super3 = {row["benchmark_id"]: 0.50 for row in rows}
    current = dict(super3)
    current["scicode"] = 0.30  # code_scientific category drops 20%
    gaps = analyze_gaps(current, super3, rows)
    assert gaps[0].category == "code_scientific"
    assert gaps[0].gap == pytest.approx(-0.20)
