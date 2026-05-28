"""Tests for the M1 eval basket scaffold (task019 Session 1).

Covers:

- ``m1_eval_basket_registry.yaml`` shape — 8 benchmark rows per roadmap
  §1.7, each with the required schema fields
- ``eval_basket_registry`` kind registered in
  ``data_registries.schema.KNOWN_KINDS``; unified index validates
  clean after the addition
- ``regression_report.py`` math — `load_eval_results`, `diff_eval_runs`
  (improved / regressed / unchanged / new / dropped + tolerance edge
  case), `format_regression_report` markdown output
- ``stage3_eval/config/m1_basket.yaml`` — valid YAML that selects the
  expected 8 benchmark task names
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m1_eval_basket.regression_report import (  # noqa: E402
    DEFAULT_REGRESSION_TOLERANCE,
    BenchmarkDelta,
    diff_eval_runs,
    format_regression_report,
    load_eval_results,
)
from nemotron.recipes.super3.milestones.m1_eval_basket.benchmark_alignment import (  # noqa: E402
    benchmark_alignment_target_suites,
    load_benchmark_alignment_ledger,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_basket_registry.yaml"
)
M1_BASKET_CONFIG_PATH = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage3_eval/config/m1_basket.yaml"
)


# ---------- Registry shape ----------


def test_registry_loads_with_eight_benchmark_rows() -> None:
    """Roadmap §1.7 names exactly 8 benchmarks for the v0 basket;
    any drift surfaces here so the basket / roadmap stay in sync."""
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["milestone"] == "M1"
    benchmarks = data["benchmarks"]
    assert len(benchmarks) == 8, f"expected 8 rows, got {len(benchmarks)}"
    ids = {row["benchmark_id"] for row in benchmarks}
    assert ids == {
        "mmlu_pro",
        "aime25",
        "gpqa",
        "livecodebench",
        "ifbench",
        "multichallenge",
        "ruler_256k",
        "taubench_airline",
    }


def test_every_benchmark_row_has_required_schema_fields() -> None:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    required = ("benchmark_id", "adapter", "category", "license", "gate_metric")
    for row in data["benchmarks"]:
        for field in required:
            assert field in row, f"row {row.get('benchmark_id')} missing {field}"


def test_aime25_row_flags_cc_by_sa_license() -> None:
    """task058 license cascade audit must pick up AIME25's share-alike
    posture. Lock the registry value so a future PR can't quietly
    relicense the row."""
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    aime = next(r for r in data["benchmarks"] if r["benchmark_id"] == "aime25")
    assert aime["license"] == "cc-by-sa-4.0"


# ---------- Schema integration (task030 Session 3 unblock) ----------


def test_eval_basket_registry_kind_is_registered_in_schema_layer() -> None:
    from nemotron.recipes.super3.milestones.data_registries.schema import (
        KNOWN_KINDS,
    )
    assert "eval_basket_registry" in KNOWN_KINDS


def test_eval_basket_registry_appears_in_unified_index() -> None:
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        load_unified_index,
    )
    rows = load_unified_index()
    eval_rows = [r for r in rows if r["kind"] == "eval_basket_registry"]
    assert eval_rows, "unified_index.yaml missing eval_basket_registry entry"
    assert eval_rows[0]["id"] == "m1_eval_basket"


def test_live_unified_index_validates_clean_after_eval_basket_addition() -> None:
    """task030 Session 3 dependency satisfied: adding the eval basket
    kind + index row must not break the unified validation pass."""
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        validate_unified_index,
    )
    issues = validate_unified_index()
    assert issues == [], (
        "live unified index has issues after eval_basket_registry addition:\n"
        + "\n".join(issues)
    )


# ---------- regression_report.load_eval_results ----------


def _write_eval_json(path: Path, model_name: str, tasks: dict) -> Path:
    path.write_text(
        json.dumps(
            {
                "model": {"name": model_name},
                "tasks": tasks,
            }
        ),
        encoding="utf-8",
    )
    return path


def test_load_eval_results_returns_top_level_dict(tmp_path: Path) -> None:
    path = _write_eval_json(
        tmp_path / "current.json",
        "super3-sft:v2",
        {"mmlu_pro": {"metrics": {"accuracy": 0.62}}},
    )
    data = load_eval_results(path)
    assert data["model"]["name"] == "super3-sft:v2"
    assert "mmlu_pro" in data["tasks"]


def test_load_eval_results_rejects_missing_tasks_key(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"model": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="'tasks' dict"):
        load_eval_results(bad)


def test_load_eval_results_rejects_non_mapping_tasks(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"model": {}, "tasks": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="'tasks' dict"):
        load_eval_results(bad)


# ---------- diff_eval_runs ----------


_DEFAULT_GATE_MAP = {
    "mmlu_pro": "accuracy",
    "aime25": "pass_at_1",
    "gpqa": "accuracy",
}


def test_diff_marks_improved_when_current_above_baseline() -> None:
    current = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.65}}}}
    baseline = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.60}}}}
    [delta] = diff_eval_runs(current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP)
    assert delta.status == "improved"
    assert delta.benchmark_id == "mmlu_pro"
    assert delta.delta == pytest.approx(0.05)


def test_diff_marks_regressed_when_current_below_baseline() -> None:
    current = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.55}}}}
    baseline = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.60}}}}
    [delta] = diff_eval_runs(current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP)
    assert delta.status == "regressed"
    assert delta.delta == pytest.approx(-0.05)


def test_diff_marks_unchanged_when_within_tolerance() -> None:
    """A run-to-run delta below ``DEFAULT_REGRESSION_TOLERANCE`` is
    noise — must not be reported as improved / regressed."""
    current = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.600005}}}}
    baseline = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.6}}}}
    [delta] = diff_eval_runs(current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP)
    assert delta.status == "unchanged"
    assert abs(delta.delta) < DEFAULT_REGRESSION_TOLERANCE


def test_diff_marks_new_when_benchmark_only_in_current() -> None:
    current = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.65}}}}
    baseline = {"tasks": {}}
    [delta] = diff_eval_runs(current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP)
    assert delta.status == "new"
    assert delta.baseline is None
    assert delta.delta is None


def test_diff_marks_dropped_when_benchmark_only_in_baseline() -> None:
    current = {"tasks": {}}
    baseline = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": 0.60}}}}
    [delta] = diff_eval_runs(current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP)
    assert delta.status == "dropped"
    assert delta.current is None
    assert delta.delta is None


def test_diff_skips_benchmarks_not_in_gate_metric_map() -> None:
    """The registry is the authoritative list — diffs on benchmarks
    not in the registry get ignored to avoid noisy reports during
    exploration."""
    current = {"tasks": {"random_eval": {"metrics": {"score": 0.5}}}}
    baseline = {"tasks": {"random_eval": {"metrics": {"score": 0.4}}}}
    assert diff_eval_runs(
        current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP
    ) == []


def test_diff_skips_benchmarks_missing_gate_metric_value() -> None:
    """Run that produced no gate_metric (e.g., harness crash mid-run)
    is treated as missing — emits no false-improved / regressed row."""
    current = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": None}}}}
    baseline = {"tasks": {"mmlu_pro": {"metrics": {"accuracy": None}}}}
    assert diff_eval_runs(
        current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP
    ) == []


def test_diff_returns_sorted_by_benchmark_id() -> None:
    """Deterministic ordering so the rendered markdown report has a
    stable diff across runs (important for code review)."""
    current = {
        "tasks": {
            "mmlu_pro": {"metrics": {"accuracy": 0.65}},
            "aime25": {"metrics": {"pass_at_1": 0.30}},
            "gpqa": {"metrics": {"accuracy": 0.45}},
        }
    }
    baseline = {
        "tasks": {
            "mmlu_pro": {"metrics": {"accuracy": 0.60}},
            "aime25": {"metrics": {"pass_at_1": 0.20}},
            "gpqa": {"metrics": {"accuracy": 0.40}},
        }
    }
    deltas = diff_eval_runs(
        current, baseline, gate_metric_by_id=_DEFAULT_GATE_MAP
    )
    assert [d.benchmark_id for d in deltas] == ["aime25", "gpqa", "mmlu_pro"]


# ---------- format_regression_report ----------


def test_format_empty_deltas_emits_no_findings_note() -> None:
    text = format_regression_report([])
    assert "no benchmarks compared" in text
    assert "Regression report" in text


def test_format_includes_summary_counts() -> None:
    deltas = [
        BenchmarkDelta(
            benchmark_id="mmlu_pro",
            metric="accuracy",
            baseline=0.6,
            current=0.65,
            delta=0.05,
            status="improved",
        ),
        BenchmarkDelta(
            benchmark_id="gpqa",
            metric="accuracy",
            baseline=0.5,
            current=0.4,
            delta=-0.1,
            status="regressed",
        ),
    ]
    text = format_regression_report(deltas)
    assert "1 improved" in text
    assert "1 regressed" in text
    assert "↑ improved" in text
    assert "↓ regressed" in text
    assert "`mmlu_pro`" in text
    assert "`gpqa`" in text
    # Signed delta column.
    assert "+0.0500" in text
    assert "-0.1000" in text


def test_format_handles_new_and_dropped_with_em_dash() -> None:
    """``new`` rows have no baseline; ``dropped`` rows have no current.
    The renderer uses em-dash for missing values so the table stays
    readable."""
    deltas = [
        BenchmarkDelta(
            benchmark_id="ruler_256k",
            metric="needle_accuracy",
            baseline=None,
            current=0.92,
            delta=None,
            status="new",
        ),
        BenchmarkDelta(
            benchmark_id="ifbench",
            metric="strict_accuracy",
            baseline=0.75,
            current=None,
            delta=None,
            status="dropped",
        ),
    ]
    text = format_regression_report(deltas)
    assert "+ new" in text
    assert "- dropped" in text
    # em-dash in baseline col for new / current col for dropped
    assert "—" in text


# ---------- m1_basket.yaml NeMo Evaluator config ----------


def test_m1_basket_config_is_valid_yaml() -> None:
    data = yaml.safe_load(M1_BASKET_CONFIG_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "tasks" in data


def test_m1_basket_config_inherits_from_default() -> None:
    """Matches the rlvr2/rlvr3/swe pattern (`defaults: default.yaml`)
    so common executor + deployment settings stay shared."""
    data = yaml.safe_load(M1_BASKET_CONFIG_PATH.read_text(encoding="utf-8"))
    assert data["defaults"] == "default.yaml"


def test_m1_basket_config_selects_eight_benchmark_tasks() -> None:
    """Task names declared in m1_basket.yaml must correspond to the 8
    benchmarks in the registry. NeMo Evaluator uses adapter-prefixed
    names (e.g., ``adlr_mmlu_pro``); the suffix must match the
    benchmark_id so a future task-name change is caught here."""
    data = yaml.safe_load(M1_BASKET_CONFIG_PATH.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 8
    # Strip adlr_ prefix to compare with registry ids.
    stripped = {t.removeprefix("adlr_") for t in tasks}
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_ids = {row["benchmark_id"] for row in registry["benchmarks"]}
    assert stripped == registry_ids


def test_alignment_ledger_matches_m1_v0_basket_gate_targets() -> None:
    """The task079 alignment ledger must follow the v0 registry exactly;
    otherwise MMLU-Pro/AIME25 evidence policy can drift from the basket
    still used by M1 gates."""
    suites = benchmark_alignment_target_suites(load_benchmark_alignment_ledger())
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_ids = {row["benchmark_id"] for row in registry["benchmarks"]}

    assert set(suites["m1_v0_basket_gate_targets"]) == registry_ids
