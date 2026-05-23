"""Tests for task039 M2 eval basket Session 2 gap thresholds."""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m2_eval_basket.registry import (  # noqa: E402
    GAP_THRESHOLDS_PATH,
    TARGET_122B_MODEL_CLASS,
    evaluate_m2_gap_thresholds,
    format_m2_gap_threshold_report,
    load_m2_eval_basket,
    load_m2_gap_thresholds,
    validate_m2_gap_thresholds,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def _threshold_data() -> dict:
    return yaml.safe_load(GAP_THRESHOLDS_PATH.read_text(encoding="utf-8"))


def test_gap_threshold_config_loads_for_all_m2_categories() -> None:
    rows = load_m2_eval_basket()
    thresholds = load_m2_gap_thresholds()

    registry_categories = {row["category"] for row in rows}
    assert {row["category"] for row in thresholds} == registry_categories
    assert _threshold_data()["target_model_class"] == TARGET_122B_MODEL_CLASS
    assert all(
        row["blocker_scope"] == "sandbox_threshold_only"
        for row in thresholds
    )


def test_gap_threshold_validator_rejects_missing_category() -> None:
    data = _threshold_data()
    data["category_thresholds"] = data["category_thresholds"][:-1]

    issues = validate_m2_gap_thresholds(data)

    assert any("missing threshold categories" in issue for issue in issues)


def test_gap_threshold_validator_rejects_benchmark_mismatch() -> None:
    data = _threshold_data()
    data["category_thresholds"][0]["benchmark_ids"] = ["browsecomp"]

    issues = validate_m2_gap_thresholds(data)

    assert any("benchmark_ids must match registry category" in issue for issue in issues)


def test_gap_threshold_validator_rejects_invalid_threshold_and_action() -> None:
    data = _threshold_data()
    data["category_thresholds"][0]["max_regression"] = 0.25
    data["category_thresholds"][0]["gate_action"] = "promote"

    issues = validate_m2_gap_thresholds(data)

    assert any("max_regression must be > 0 and <= 0.10" in issue for issue in issues)
    assert any("gate_action must be one of" in issue for issue in issues)


def test_gap_threshold_evaluation_flags_only_rows_beyond_configured_gap() -> None:
    thresholds = load_m2_gap_thresholds()
    benchmark_ids = {
        benchmark_id
        for threshold in thresholds
        for benchmark_id in threshold["benchmark_ids"]
    }
    baseline_scores = {benchmark_id: 0.80 for benchmark_id in benchmark_ids}
    current_scores = dict(baseline_scores)
    current_scores["hle"] = 0.785
    current_scores["browsecomp"] = 0.785

    results = {
        row["category"]: row
        for row in evaluate_m2_gap_thresholds(current_scores, baseline_scores)
    }

    assert results["reasoning_extreme_difficulty"]["status"] == "behind"
    assert results["reasoning_extreme_difficulty"]["gap"] == pytest.approx(-0.015)
    assert results["browser_search"]["status"] == "pass"
    assert results["browser_search"]["target_model_class"] == TARGET_122B_MODEL_CLASS


def test_gap_threshold_evaluation_surfaces_missing_scores() -> None:
    results = {
        row["category"]: row
        for row in evaluate_m2_gap_thresholds({"hle": 0.80}, {"hle": 0.80})
    }

    browser = results["browser_search"]
    assert browser["status"] == "missing"
    assert browser["missing_in_current"] == ["browsecomp"]
    assert browser["missing_in_baseline"] == ["browsecomp"]


def test_gap_threshold_report_is_deterministic_and_mentions_target_class() -> None:
    results = evaluate_m2_gap_thresholds(
        {"hle": 0.785},
        {"hle": 0.80},
        thresholds=[
            {
                "category": "reasoning_extreme_difficulty",
                "benchmark_ids": ["hle"],
                "max_regression": 0.010,
                "gate_action": "hold",
            }
        ],
    )

    text = format_m2_gap_threshold_report(results)

    assert text.startswith(
        f"# M2 eval basket gap thresholds ({TARGET_122B_MODEL_CLASS})"
    )
    assert "| `reasoning_extreme_difficulty` | behind | -1.50% | 1.00% |" in text


def test_task039_docs_record_session2_gap_threshold_scope() -> None:
    task_dir = REPO_ROOT / "workspace/tasks/task039_m2_eval_basket"
    assert "Session 2" in (task_dir / "README.md").read_text(encoding="utf-8")
