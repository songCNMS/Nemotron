"""Tests for the M1 eval *full* basket extension (task020 Session 1).

Covers:

- ``m1_eval_full_basket_registry.yaml`` shape — 11 additional benchmark
  rows per roadmap §1.7 task020 / plan §5.7 acceptance basket, each
  with the same schema fields as the v0 registry
- No benchmark_id overlap between v0 and full registries
- Same ``eval_basket_registry`` kind reused; unified index registers
  ``m1_eval_full_basket`` and live validate stays clean
- Combined ``stage3_eval/config/m1_full_basket.yaml`` selects all 19
  benchmarks; every config task name has a matching registry row
- ``regression_report.diff_eval_runs`` works on the combined gate-metric
  lookup (no source changes needed — function already accepts an
  arbitrary map)
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.cli.commands.super3.eval import (  # noqa: E402
    CONFIG_DIR,
    load_stage3_eval_config,
    normalize_evaluator_launcher_config,
)
from nemotron.recipes.super3.milestones.m1_eval_basket.regression_report import (  # noqa: E402
    diff_eval_runs,
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
FULL_BASKET_CONFIG_PATH = (
    REPO_ROOT / "src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket.yaml"
)
LAUNCHER_MAPPING_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_eval_launcher_mapping.yaml"
)
LAUNCHER_AVAILABLE_CONFIG_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/stage3_eval/config/m1_full_basket_launcher_available.yaml"
)
TASK071_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_non_dry_results_task071_iter0000122.yaml"
)
TASK071_UNCAPPED_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_eval_basket/m1_full_basket_non_dry_results_task071_iter0012158.yaml"
)
TASK071_UNCAPPED_FULL_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / (
        "src/nemotron/recipes/super3/milestones/m1_eval_basket/"
        "m1_full_basket_full_non_dry_results_task071_iter0012158.yaml"
    )
)
QWEN3_4B_ORIGINAL_FULL_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / (
        "src/nemotron/recipes/super3/milestones/m1_eval_basket/"
        "m1_full_basket_full_non_dry_results_qwen3_4b_instruct_2507_original.yaml"
    )
)
TASK071_QWEN3_30B_A3B_FULL_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / (
        "src/nemotron/recipes/super3/milestones/m1_eval_basket/"
        "m1_full_basket_full_non_dry_results_task071_qwen3_30b_a3b_iter0009119.yaml"
    )
)
QWEN3_30B_A3B_ORIGINAL_FULL_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / (
        "src/nemotron/recipes/super3/milestones/m1_eval_basket/"
        "m1_full_basket_full_non_dry_results_qwen3_30b_a3b_instruct_2507_original.yaml"
    )
)
TASK071_QWEN3_30B_A3B_CONSERVATIVE_FULL_NON_DRY_RESULTS_PATH = (
    REPO_ROOT
    / (
        "src/nemotron/recipes/super3/milestones/m1_eval_basket/"
        "m1_full_basket_full_non_dry_results_task071_qwen3_30b_a3b_conservative_iter0010110.yaml"
    )
)


EXPECTED_FULL_IDS = {
    "hmmt",
    "hle",
    "scicode",
    "terminalbench",
    "swe_bench_verified",
    "aa_lcr",
    "mmlu_prox",
    "wmt24pp",
    "bfcl",
    "mcp_mark",
    "tool_decathlon",
}

EXPECTED_V0_IDS = {
    "mmlu_pro",
    "aime25",
    "gpqa",
    "livecodebench",
    "ifbench",
    "multichallenge",
    "ruler_256k",
    "taubench_airline",
}

EXPECTED_LAUNCHER_MISSING_IDS = {
    "multichallenge",
    "terminalbench",
    "swe_bench_verified",
    "mcp_mark",
    "tool_decathlon",
}

EXPECTED_NON_DRY_STATUSES = {"scored", "blocked", "partial"}


def _load_rows(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["benchmarks"]


def _load_launcher_rows() -> list[dict]:
    data = yaml.safe_load(LAUNCHER_MAPPING_PATH.read_text(encoding="utf-8"))
    return data["tasks"]


def _load_task071_non_dry_results() -> dict:
    return yaml.safe_load(TASK071_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8"))


def _load_task071_uncapped_non_dry_results() -> dict:
    return yaml.safe_load(TASK071_UNCAPPED_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8"))


def _load_task071_uncapped_full_non_dry_results() -> dict:
    return yaml.safe_load(
        TASK071_UNCAPPED_FULL_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    )


def _load_qwen3_4b_original_full_non_dry_results() -> dict:
    return yaml.safe_load(
        QWEN3_4B_ORIGINAL_FULL_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    )


def _load_task071_qwen3_30b_a3b_full_non_dry_results() -> dict:
    return yaml.safe_load(
        TASK071_QWEN3_30B_A3B_FULL_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    )


def _load_qwen3_30b_a3b_original_full_non_dry_results() -> dict:
    return yaml.safe_load(
        QWEN3_30B_A3B_ORIGINAL_FULL_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    )


def _load_task071_qwen3_30b_a3b_conservative_full_non_dry_results() -> dict:
    return yaml.safe_load(
        TASK071_QWEN3_30B_A3B_CONSERVATIVE_FULL_NON_DRY_RESULTS_PATH.read_text(
            encoding="utf-8"
        )
    )


# ---------- Registry shape ----------


def test_full_registry_loads_with_eleven_benchmark_rows() -> None:
    """Roadmap §1.7 task020 lists exactly 11 extension benchmarks;
    drift in either direction surfaces here."""
    data = yaml.safe_load(FULL_REGISTRY_PATH.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["milestone"] == "M1"
    rows = data["benchmarks"]
    assert len(rows) == 11, f"expected 11 rows, got {len(rows)}"
    ids = {row["benchmark_id"] for row in rows}
    assert ids == EXPECTED_FULL_IDS


def test_every_full_basket_row_has_required_schema_fields() -> None:
    required = ("benchmark_id", "adapter", "category", "license", "gate_metric")
    for row in _load_rows(FULL_REGISTRY_PATH):
        for field in required:
            assert field in row, f"row {row.get('benchmark_id')} missing {field}"


def test_hmmt_row_flags_cc_by_sa_license() -> None:
    """HMMT mirrors AIME25's share-alike posture; task058 license
    cascade audit relies on this row staying CC-BY-SA-4.0 so the
    informational eval-time signal stays consistent."""
    row = next(r for r in _load_rows(FULL_REGISTRY_PATH) if r["benchmark_id"] == "hmmt")
    assert row["license"] == "cc-by-sa-4.0"


def test_full_basket_adapter_names_match_benchmark_ids() -> None:
    """Adapter convention is ``nemo_evaluator.<benchmark_id>`` so the
    schema-layer audit can cross-walk config selectors and registry
    rows without ambiguity. Lock the convention for the full extension."""
    for row in _load_rows(FULL_REGISTRY_PATH):
        bid = row["benchmark_id"]
        assert row["adapter"] == f"nemo_evaluator.{bid}", (
            f"row {bid} adapter does not match nemo_evaluator.{bid}"
        )


# ---------- No overlap with v0 ----------


def test_full_basket_does_not_redefine_any_v0_benchmark() -> None:
    """Each benchmark_id should live in exactly one registry; otherwise
    the combined gate-metric lookup needs conflict resolution."""
    v0_ids = {r["benchmark_id"] for r in _load_rows(V0_REGISTRY_PATH)}
    full_ids = {r["benchmark_id"] for r in _load_rows(FULL_REGISTRY_PATH)}
    overlap = v0_ids & full_ids
    assert not overlap, f"benchmark_id overlap between v0 and full: {overlap}"


def test_combined_basket_covers_plan_5_7_acceptance_set() -> None:
    """Sanity-check that v0 + full = 19 distinct benchmarks per plan §5.7."""
    v0_ids = {r["benchmark_id"] for r in _load_rows(V0_REGISTRY_PATH)}
    full_ids = {r["benchmark_id"] for r in _load_rows(FULL_REGISTRY_PATH)}
    combined = v0_ids | full_ids
    assert combined == EXPECTED_V0_IDS | EXPECTED_FULL_IDS
    assert len(combined) == 19


# ---------- Schema integration ----------


def test_full_basket_registered_in_unified_index() -> None:
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        load_unified_index,
    )
    rows = load_unified_index()
    full_basket_rows = [r for r in rows if r.get("id") == "m1_eval_full_basket"]
    assert full_basket_rows, "unified_index.yaml missing m1_eval_full_basket entry"
    assert full_basket_rows[0]["kind"] == "eval_basket_registry"


def test_live_unified_index_validates_clean_after_full_basket_addition() -> None:
    """Adding the full basket file + index row must not break the
    unified validation pass (uses the same eval_basket_registry kind
    introduced by task019 Session 1, so no schema change needed)."""
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        validate_unified_index,
    )
    issues = validate_unified_index()
    assert issues == [], (
        "live unified index has issues after m1_eval_full_basket addition:\n"
        + "\n".join(issues)
    )


def test_full_basket_uses_existing_eval_basket_registry_kind() -> None:
    """task020 Session 1 explicitly reuses task019's schema kind — no
    new eval-basket-specific KNOWN_KINDS entry expected. Lock that to
    catch accidental expansion while allowing unrelated registry kinds
    such as M2 SWE harness metadata."""
    from nemotron.recipes.super3.milestones.data_registries.schema import (
        KNOWN_KINDS,
    )
    assert "eval_basket_registry" in KNOWN_KINDS
    assert "m2_eval_basket_registry" not in KNOWN_KINDS


# ---------- m1_full_basket.yaml ----------


def test_full_basket_config_is_valid_yaml() -> None:
    data = yaml.safe_load(FULL_BASKET_CONFIG_PATH.read_text(encoding="utf-8"))
    assert data["defaults"] == "default.yaml"
    assert isinstance(data["tasks"], list)


def test_full_basket_config_selects_all_nineteen_tasks() -> None:
    data = yaml.safe_load(FULL_BASKET_CONFIG_PATH.read_text(encoding="utf-8"))
    tasks = data["tasks"]
    assert len(tasks) == 19, f"expected 19 task entries, got {len(tasks)}"


def test_full_basket_config_task_names_match_registry_benchmark_ids() -> None:
    """The convention is ``adlr_<benchmark_id>`` for every task; if the
    config picks a name that isn't in either registry the cross-walk
    breaks and the regression report will silently skip that task."""
    data = yaml.safe_load(FULL_BASKET_CONFIG_PATH.read_text(encoding="utf-8"))
    tasks = set(data["tasks"])
    combined_ids = (
        {r["benchmark_id"] for r in _load_rows(V0_REGISTRY_PATH)}
        | {r["benchmark_id"] for r in _load_rows(FULL_REGISTRY_PATH)}
    )
    expected = {f"adlr_{bid}" for bid in combined_ids}
    assert tasks == expected, (
        f"config / registry drift — missing in config: {expected - tasks}, "
        f"extra in config: {tasks - expected}"
    )


def test_launcher_mapping_covers_full_basket_and_locks_known_gaps() -> None:
    """The runtime mapping records every intended benchmark, including
    launcher 0.2.5 gaps. This avoids silently replacing missing SWE /
    terminal / MCP tasks with unrelated proxy benchmarks."""
    rows = _load_launcher_rows()
    ids = {row["benchmark_id"] for row in rows}
    assert ids == EXPECTED_V0_IDS | EXPECTED_FULL_IDS

    missing = {row["benchmark_id"] for row in rows if row["status"] == "missing"}
    assert missing == EXPECTED_LAUNCHER_MISSING_IDS

    available = [row for row in rows if row["status"] == "available"]
    assert len(available) == 14
    for row in available:
        assert row["launcher_task"]
        assert "." in row["launcher_task"]
        assert not row["launcher_task"].startswith(("adlr_", "nemo_evaluator."))


def test_launcher_available_config_uses_only_verified_available_tasks() -> None:
    data = yaml.safe_load(LAUNCHER_AVAILABLE_CONFIG_PATH.read_text(encoding="utf-8"))
    assert data["defaults"] == "default.yaml"

    expected = {
        row["launcher_task"]
        for row in _load_launcher_rows()
        if row["status"] == "available"
    }
    tasks = set(data["tasks"])
    assert tasks == expected
    assert len(tasks) == 14


def test_task071_non_dry_results_cover_launcher_available_config() -> None:
    """The task071 run manifest is useful only if it covers every
    launcher task we selected for the runnable full-basket subset."""
    config = yaml.safe_load(LAUNCHER_AVAILABLE_CONFIG_PATH.read_text(encoding="utf-8"))
    result_manifest = _load_task071_non_dry_results()

    config_tasks = config["tasks"]
    result_tasks = [row["launcher_task"] for row in result_manifest["results"]]

    assert result_manifest["schema_version"] == 1
    assert result_manifest["launcher"]["config"] == "m1_full_basket_launcher_available"
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is True
    assert result_tasks == config_tasks
    assert result_manifest["summary"]["attempted_tasks"] == len(config_tasks)


def test_task071_non_dry_results_match_launcher_mapping_ids() -> None:
    mapping_by_task = {
        row["launcher_task"]: row
        for row in _load_launcher_rows()
        if row["status"] == "available"
    }
    result_manifest = _load_task071_non_dry_results()

    for row in result_manifest["results"]:
        mapping_row = mapping_by_task[row["launcher_task"]]
        assert row["benchmark_id"] == mapping_row["benchmark_id"]
        assert row["source_basket"] == mapping_row["source_basket"]


def test_task071_non_dry_results_make_scored_and_blocked_states_explicit() -> None:
    result_manifest = _load_task071_non_dry_results()
    rows = result_manifest["results"]

    statuses = [row["attempt_status"] for row in rows]
    assert set(statuses) <= EXPECTED_NON_DRY_STATUSES
    assert statuses.count("scored") == result_manifest["summary"]["scored_tasks"]
    assert len([s for s in statuses if s != "scored"]) == result_manifest["summary"][
        "blocked_or_partial_tasks"
    ]

    for row in rows:
        if row["attempt_status"] == "scored":
            assert row["docker_exit"] == 0
            assert row["artifacts"].startswith("vm4vpn:")
            assert row["observed_metrics"]
            assert row["response_stats"]["successful_responses"] > 0
        else:
            assert row["blocker"]["type"]
            assert row["response_stats"]["total_responses"] >= 0


def test_task071_non_dry_results_do_not_store_secret_tokens() -> None:
    text = TASK071_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_task071_uncapped_non_dry_results_record_selected_regression_subset() -> None:
    """The uncapped checkpoint comparison is a selected non-dry subset,
    not a replacement for the full 14-task iter0000122 sweep."""
    result_manifest = _load_task071_uncapped_non_dry_results()
    config = yaml.safe_load(LAUNCHER_AVAILABLE_CONFIG_PATH.read_text(encoding="utf-8"))

    result_tasks = [row["launcher_task"] for row in result_manifest["results"]]
    config_tasks = set(config["tasks"])

    assert result_manifest["schema_version"] == 1
    assert result_manifest["model"]["artifact"].endswith("iter0012158-hf:v1")
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["selected_regression_tasks"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is False
    assert set(result_tasks) <= config_tasks
    assert result_manifest["summary"]["attempted_tasks"] == len(result_tasks) == 5
    assert result_manifest["summary"]["scored_tasks"] == 5
    assert result_manifest["not_attempted_in_this_pass"]

    for row in result_manifest["results"]:
        assert row["attempt_status"] == "scored"
        assert row["docker_exit"] == 0
        assert row["artifacts"].startswith("vm4vpn:")
        assert row["observed_metrics"]
        assert "baseline_iter0000122" in row
        assert "delta_vs_iter0000122" in row


def test_task071_uncapped_non_dry_results_do_not_store_secret_tokens() -> None:
    text = TASK071_UNCAPPED_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_task071_uncapped_full_non_dry_results_record_full_selected_runs() -> None:
    """The full-selected follow-up removes the smoke-run sample limits
    for the same 5 scored tasks while keeping it separate from the
    small regression manifest."""
    result_manifest = _load_task071_uncapped_full_non_dry_results()
    rows = result_manifest["results"]

    assert result_manifest["schema_version"] == 1
    assert result_manifest["model"]["artifact"].endswith("iter0012158-hf:v1")
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["selected_regression_tasks"] is True
    assert result_manifest["run_scope"]["full_selected_tasks_attempted"] is True
    assert result_manifest["run_scope"]["sample_limits_removed"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is False
    assert result_manifest["summary"]["attempted_tasks"] == len(rows) == 5
    assert result_manifest["summary"]["scored_tasks"] == 5

    assert [row["benchmark_id"] for row in rows] == [
        "ifbench",
        "aime25",
        "hmmt",
        "wmt24pp",
        "mmlu_pro",
    ]
    for row in rows:
        assert row["attempt_status"] == "scored"
        assert row["docker_exit"] == 0
        assert row["sample_scope"]["limit_samples"] is None
        assert row["artifacts"].startswith("vm4vpn:")
        assert row["observed_metrics"]
        assert row["response_stats"]["successful_responses"] > 0


def test_task071_uncapped_full_non_dry_results_lock_key_metrics() -> None:
    result_manifest = _load_task071_uncapped_full_non_dry_results()
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert by_id["ifbench"]["sample_scope"]["prompts"] == 294
    assert by_id["ifbench"]["observed_metrics"][
        "prompt_level_strict_accuracy"
    ] == pytest.approx(0.2755102040816326)

    assert by_id["aime25"]["sample_scope"]["requests"] == 300
    assert by_id["aime25"]["observed_metrics"]["score"] == pytest.approx(0.11)

    assert by_id["hmmt"]["sample_scope"]["entries"] == 30
    assert by_id["hmmt"]["observed_metrics"]["symbolic_correct_percent"] == 0.0
    assert by_id["hmmt"]["observed_metrics"]["no_answer_percent"] == pytest.approx(
        93.33333333333333
    )

    assert by_id["wmt24pp"]["sample_scope"]["output_jsonl_rows"] == 4990
    assert by_id["wmt24pp"]["observed_metrics"]["bleu_xx_to_xx"] == pytest.approx(
        29.295411202064134
    )

    assert by_id["mmlu_pro"]["sample_scope"]["requests"] == 12032
    assert by_id["mmlu_pro"]["observed_metrics"]["group_exact_match"] == pytest.approx(
        0.1346409574468085
    )
    assert by_id["mmlu_pro"]["response_stats"]["successful_responses"] == 12032


def test_task071_uncapped_full_non_dry_results_do_not_store_secret_tokens() -> None:
    text = TASK071_UNCAPPED_FULL_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_qwen3_4b_original_full_non_dry_results_record_full_selected_runs() -> None:
    """The original-Qwen baseline must match the same 5 full-selected
    benchmark tasks and sample scopes as the iter0012158 SFT comparison
    run, so metric deltas are interpretable."""
    result_manifest = _load_qwen3_4b_original_full_non_dry_results()
    rows = result_manifest["results"]

    assert result_manifest["schema_version"] == 1
    assert result_manifest["model"]["source_model"] == "Qwen/Qwen3-4B-Instruct-2507"
    assert (
        result_manifest["model"]["endpoint_model_id"]
        == "qwen3-4b-instruct-2507-original"
    )
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["selected_regression_tasks"] is True
    assert result_manifest["run_scope"]["full_selected_tasks_attempted"] is True
    assert result_manifest["run_scope"]["sample_limits_removed"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is False
    assert result_manifest["summary"]["attempted_tasks"] == len(rows) == 5
    assert result_manifest["summary"]["scored_tasks"] == 5

    assert [row["benchmark_id"] for row in rows] == [
        "ifbench",
        "aime25",
        "hmmt",
        "wmt24pp",
        "mmlu_pro",
    ]
    for row in rows:
        assert row["attempt_status"] == "scored"
        assert row["docker_exit"] == 0
        assert row["sample_scope"]["limit_samples"] is None
        assert row["artifacts"].startswith("vm4vpn:")
        assert row["observed_metrics"]
        assert row["response_stats"]["successful_responses"] > 0
        assert "comparison_vs_iter0012158_sft" in row


def test_qwen3_4b_original_full_non_dry_results_lock_key_metrics() -> None:
    result_manifest = _load_qwen3_4b_original_full_non_dry_results()
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert by_id["ifbench"]["sample_scope"]["prompts"] == 294
    assert by_id["ifbench"]["observed_metrics"][
        "prompt_level_strict_accuracy"
    ] == pytest.approx(0.30612244897959184)

    assert by_id["aime25"]["sample_scope"]["requests"] == 300
    assert by_id["aime25"]["observed_metrics"]["score"] == pytest.approx(
        0.09333333333333335
    )

    assert by_id["hmmt"]["sample_scope"]["entries"] == 30
    assert by_id["hmmt"]["observed_metrics"]["symbolic_correct_percent"] == pytest.approx(
        6.666666666666667
    )
    assert by_id["hmmt"]["observed_metrics"]["no_answer_percent"] == pytest.approx(
        83.33333333333333
    )

    assert by_id["wmt24pp"]["sample_scope"]["output_jsonl_rows"] == 4990
    assert by_id["wmt24pp"]["observed_metrics"]["bleu_xx_to_xx"] == pytest.approx(
        28.361839067434847
    )

    assert by_id["mmlu_pro"]["sample_scope"]["requests"] == 12032
    assert by_id["mmlu_pro"]["observed_metrics"]["group_exact_match"] == pytest.approx(
        0.0078125
    )
    assert by_id["mmlu_pro"]["response_stats"]["successful_responses"] == 12032


def test_qwen3_4b_original_full_non_dry_results_lock_sft_comparison() -> None:
    result_manifest = _load_qwen3_4b_original_full_non_dry_results()
    summary_rows = {
        row["benchmark_id"]: row
        for row in result_manifest["summary"]["primary_metric_comparison"]
    }
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert result_manifest["summary"]["comparison_direction"] == (
        "original_minus_iter0012158_sft"
    )
    assert summary_rows["ifbench"]["original_minus_iter0012158_sft"] == pytest.approx(
        0.03061224489795924
    )
    assert summary_rows["aime25"]["original_minus_iter0012158_sft"] == pytest.approx(
        -0.01666666666666665
    )
    assert summary_rows["hmmt"]["original_minus_iter0012158_sft"] == pytest.approx(
        6.666666666666667
    )
    assert summary_rows["wmt24pp"]["original_minus_iter0012158_sft"] == pytest.approx(
        -0.933572134629287
    )
    assert summary_rows["mmlu_pro"]["original_minus_iter0012158_sft"] == pytest.approx(
        -0.1268284574468085
    )

    assert by_id["mmlu_pro"]["comparison_vs_iter0012158_sft"][
        "iter0012158_sft"
    ] == pytest.approx(0.1346409574468085)


def test_qwen3_4b_original_full_non_dry_results_do_not_store_secret_tokens() -> None:
    text = QWEN3_4B_ORIGINAL_FULL_NON_DRY_RESULTS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_task071_qwen3_30b_a3b_full_non_dry_results_record_full_selected_runs() -> None:
    """The 30B-A3B follow-up must use the same full-selected benchmark
    subset as the 4B comparison so the before/after score deltas stay
    interpretable."""
    result_manifest = _load_task071_qwen3_30b_a3b_full_non_dry_results()
    rows = result_manifest["results"]

    assert result_manifest["schema_version"] == 1
    assert result_manifest["model"]["artifact"].endswith("iter0009119-hf:v1")
    assert result_manifest["model"]["training"]["train_iters"] == 9119
    assert result_manifest["model"]["training"]["global_batch_size"] == 8
    assert result_manifest["model"]["validation"]["final_loss"] == pytest.approx(
        0.3001248
    )
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["full_selected_tasks_attempted"] is True
    assert result_manifest["run_scope"]["sample_limits_removed"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is False
    assert result_manifest["summary"]["attempted_tasks"] == len(rows) == 5
    assert result_manifest["summary"]["scored_tasks"] == 5
    assert result_manifest["summary"]["total_successful_responses_from_stats"] == 17627
    assert result_manifest["summary"]["official_comparability"]["status"] == (
        "regression_only_not_official_comparable"
    )

    assert [row["benchmark_id"] for row in rows] == [
        "ifbench",
        "aime25",
        "hmmt",
        "wmt24pp",
        "mmlu_pro",
    ]
    for row in rows:
        assert row["attempt_status"] == "scored"
        assert row["docker_exit"] == 0
        assert row["sample_scope"]["limit_samples"] is None
        assert row["artifacts"].startswith("vm4vpn:")
        assert row["observed_metrics"]
        assert row["response_stats"]["successful_responses"] > 0


def test_task071_qwen3_30b_a3b_full_non_dry_results_lock_key_metrics() -> None:
    result_manifest = _load_task071_qwen3_30b_a3b_full_non_dry_results()
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert by_id["ifbench"]["sample_scope"]["prompts"] == 294
    assert by_id["ifbench"]["observed_metrics"][
        "prompt_level_strict_accuracy"
    ] == pytest.approx(0.30272108843537415)

    assert by_id["aime25"]["sample_scope"]["requests"] == 300
    assert by_id["aime25"]["observed_metrics"]["score"] == 0.0

    assert by_id["hmmt"]["sample_scope"]["entries"] == 30
    assert by_id["hmmt"]["observed_metrics"]["symbolic_correct_percent"] == 0.0
    assert by_id["hmmt"]["observed_metrics"]["no_answer_percent"] == pytest.approx(
        93.33333333333333
    )

    assert by_id["wmt24pp"]["sample_scope"]["output_jsonl_rows"] == 4990
    assert by_id["wmt24pp"]["observed_metrics"]["bleu_xx_to_xx"] == pytest.approx(
        33.332009385866584
    )
    assert by_id["wmt24pp"]["response_stats"]["successful_responses"] == 4971

    assert by_id["mmlu_pro"]["sample_scope"]["requests"] == 12032
    assert by_id["mmlu_pro"]["observed_metrics"]["group_exact_match"] == pytest.approx(
        0.07737699468085106
    )
    assert by_id["mmlu_pro"]["response_stats"]["successful_responses"] == 12032


def test_task071_qwen3_30b_a3b_full_non_dry_results_do_not_store_secret_tokens() -> None:
    text = TASK071_QWEN3_30B_A3B_FULL_NON_DRY_RESULTS_PATH.read_text(
        encoding="utf-8"
    )
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_qwen3_30b_a3b_original_full_non_dry_results_record_full_selected_runs() -> None:
    result_manifest = _load_qwen3_30b_a3b_original_full_non_dry_results()
    rows = result_manifest["results"]

    assert result_manifest["schema_version"] == 1
    assert (
        result_manifest["model"]["source_model"]
        == "Qwen/Qwen3-30B-A3B-Instruct-2507"
    )
    assert (
        result_manifest["model"]["endpoint_model_id"]
        == "qwen3-30b-a3b-instruct-2507-original"
    )
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["full_selected_tasks_attempted"] is True
    assert result_manifest["run_scope"]["sample_limits_removed"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is False
    assert result_manifest["summary"]["attempted_tasks"] == len(rows) == 5
    assert result_manifest["summary"]["scored_tasks"] == 5
    assert result_manifest["summary"]["total_successful_responses_from_stats"] == 17626
    assert result_manifest["summary"]["official_comparability"]["status"] == (
        "not_official_comparable"
    )

    assert [row["benchmark_id"] for row in rows] == [
        "ifbench",
        "aime25",
        "hmmt",
        "wmt24pp",
        "mmlu_pro",
    ]
    for row in rows:
        assert row["attempt_status"] == "scored"
        assert row["docker_exit"] == 0
        assert row["sample_scope"]["limit_samples"] is None
        assert row["artifacts"].startswith("vm4vpn:")
        assert row["observed_metrics"]
        assert row["response_stats"]["successful_responses"] > 0
        assert "comparison_vs_qwen3_30b_a3b_sft_iter0009119" in row


def test_qwen3_30b_a3b_original_full_non_dry_results_lock_key_metrics() -> None:
    result_manifest = _load_qwen3_30b_a3b_original_full_non_dry_results()
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert by_id["ifbench"]["sample_scope"]["prompts"] == 294
    assert by_id["ifbench"]["observed_metrics"][
        "prompt_level_strict_accuracy"
    ] == pytest.approx(0.3197278911564626)

    assert by_id["aime25"]["sample_scope"]["requests"] == 300
    assert by_id["aime25"]["observed_metrics"]["score"] == pytest.approx(
        0.16666666666666666
    )

    assert by_id["hmmt"]["sample_scope"]["entries"] == 30
    assert by_id["hmmt"]["observed_metrics"]["symbolic_correct_percent"] == pytest.approx(
        6.666666666666667
    )
    assert by_id["hmmt"]["observed_metrics"]["no_answer_percent"] == pytest.approx(
        93.33333333333333
    )

    assert by_id["wmt24pp"]["sample_scope"]["output_jsonl_rows"] == 4990
    assert by_id["wmt24pp"]["observed_metrics"]["bleu_xx_to_xx"] == pytest.approx(
        33.03998831072459
    )
    assert by_id["wmt24pp"]["response_stats"]["successful_responses"] == 4970

    assert by_id["mmlu_pro"]["sample_scope"]["requests"] == 12032
    assert by_id["mmlu_pro"]["observed_metrics"]["group_exact_match"] == pytest.approx(
        8.311170212765957e-05
    )
    assert by_id["mmlu_pro"]["response_stats"]["successful_responses"] == 12032


def test_qwen3_30b_a3b_original_full_non_dry_results_lock_sft_comparison() -> None:
    result_manifest = _load_qwen3_30b_a3b_original_full_non_dry_results()
    summary_rows = {
        row["benchmark_id"]: row
        for row in result_manifest["summary"]["primary_metric_comparison"]
    }
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert result_manifest["summary"]["comparison_direction"] == (
        "original_minus_qwen3_30b_a3b_sft_iter0009119"
    )
    assert summary_rows["ifbench"][
        "original_minus_qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(0.017006802721088454)
    assert summary_rows["aime25"][
        "original_minus_qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(0.16666666666666666)
    assert summary_rows["hmmt"][
        "original_minus_qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(6.666666666666667)
    assert summary_rows["wmt24pp"][
        "original_minus_qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(-0.2920210751419958)
    assert summary_rows["mmlu_pro"][
        "original_minus_qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(-0.0772938829787234)

    assert by_id["mmlu_pro"]["comparison_vs_qwen3_30b_a3b_sft_iter0009119"][
        "qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(0.07737699468085106)


def test_qwen3_30b_a3b_original_full_non_dry_results_do_not_store_secret_tokens() -> None:
    text = QWEN3_30B_A3B_ORIGINAL_FULL_NON_DRY_RESULTS_PATH.read_text(
        encoding="utf-8"
    )
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_task071_qwen3_30b_a3b_conservative_results_record_full_selected_runs() -> None:
    result_manifest = _load_task071_qwen3_30b_a3b_conservative_full_non_dry_results()
    rows = result_manifest["results"]

    assert result_manifest["schema_version"] == 1
    assert result_manifest["model"]["artifact"].endswith("iter0010110-hf:v1")
    assert result_manifest["model"]["training"]["train_iters"] == 10110
    assert result_manifest["model"]["training"]["global_batch_size"] == 8
    assert result_manifest["model"]["training"]["target_epoch_fraction"] == 0.5
    assert result_manifest["model"]["validation"]["final_loss"] == pytest.approx(
        0.3727816
    )
    assert result_manifest["model"]["validation"]["best_iter"] == 9000
    assert result_manifest["run_scope"]["non_dry"] is True
    assert result_manifest["run_scope"]["full_selected_tasks_attempted"] is True
    assert result_manifest["run_scope"]["sample_limits_removed"] is True
    assert result_manifest["run_scope"]["all_available_tasks_attempted"] is False
    assert result_manifest["summary"]["attempted_tasks"] == len(rows) == 5
    assert result_manifest["summary"]["scored_tasks"] == 5
    assert result_manifest["summary"]["total_successful_responses_from_stats"] == 17627
    assert result_manifest["summary"]["official_comparability"]["status"] == (
        "regression_only_not_official_comparable"
    )

    assert [row["benchmark_id"] for row in rows] == [
        "ifbench",
        "aime25",
        "hmmt",
        "wmt24pp",
        "mmlu_pro",
    ]
    for row in rows:
        assert row["attempt_status"] == "scored"
        assert row["docker_exit"] == 0
        assert row["sample_scope"]["limit_samples"] is None
        assert row["artifacts"].startswith("vm4vpn:")
        assert row["observed_metrics"]
        assert row["response_stats"]["successful_responses"] > 0
        assert "comparison_vs_baselines" in row


def test_task071_qwen3_30b_a3b_conservative_results_lock_key_metrics() -> None:
    result_manifest = _load_task071_qwen3_30b_a3b_conservative_full_non_dry_results()
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert by_id["ifbench"]["sample_scope"]["prompts"] == 294
    assert by_id["ifbench"]["observed_metrics"][
        "prompt_level_strict_accuracy"
    ] == pytest.approx(0.3401360544217687)
    assert by_id["ifbench"]["observed_metrics"][
        "instruction_level_strict_accuracy"
    ] == pytest.approx(0.3641791044776119)

    assert by_id["aime25"]["sample_scope"]["requests"] == 300
    assert by_id["aime25"]["observed_metrics"]["score"] == pytest.approx(
        0.03333333333333333
    )

    assert by_id["hmmt"]["sample_scope"]["entries"] == 30
    assert by_id["hmmt"]["observed_metrics"]["symbolic_correct_percent"] == 0.0
    assert by_id["hmmt"]["observed_metrics"]["no_answer_percent"] == 0.0

    assert by_id["wmt24pp"]["sample_scope"]["output_jsonl_rows"] == 4990
    assert by_id["wmt24pp"]["observed_metrics"]["bleu_xx_to_xx"] == pytest.approx(
        33.361471695801946
    )
    assert by_id["wmt24pp"]["response_stats"]["successful_responses"] == 4971

    assert by_id["mmlu_pro"]["sample_scope"]["requests"] == 12032
    assert by_id["mmlu_pro"]["observed_metrics"]["group_exact_match"] == pytest.approx(
        0.010388962765957447
    )
    assert by_id["mmlu_pro"]["response_stats"]["successful_responses"] == 12032


def test_task071_qwen3_30b_a3b_conservative_results_lock_comparison() -> None:
    result_manifest = _load_task071_qwen3_30b_a3b_conservative_full_non_dry_results()
    summary_rows = {
        row["benchmark_id"]: row
        for row in result_manifest["summary"]["primary_metric_comparison"]
    }
    by_id = {row["benchmark_id"]: row for row in result_manifest["results"]}

    assert (
        result_manifest["summary"]["comparison_direction"]
        == "conservative_iter0010110_minus_baselines"
    )
    assert summary_rows["ifbench"][
        "conservative_iter0010110_minus_iter0009119"
    ] == pytest.approx(0.037414965986394544)
    assert summary_rows["ifbench"][
        "conservative_iter0010110_minus_original"
    ] == pytest.approx(0.02040816326530609)
    assert summary_rows["aime25"][
        "conservative_iter0010110_minus_iter0009119"
    ] == pytest.approx(0.03333333333333333)
    assert summary_rows["aime25"][
        "conservative_iter0010110_minus_original"
    ] == pytest.approx(-0.13333333333333333)
    assert summary_rows["hmmt"][
        "conservative_iter0010110_minus_original"
    ] == pytest.approx(-6.666666666666667)
    assert summary_rows["wmt24pp"][
        "conservative_iter0010110_minus_iter0009119"
    ] == pytest.approx(0.029462309935361475)
    assert summary_rows["wmt24pp"][
        "conservative_iter0010110_minus_original"
    ] == pytest.approx(0.3214833850773573)
    assert summary_rows["mmlu_pro"][
        "conservative_iter0010110_minus_iter0009119"
    ] == pytest.approx(-0.06698803191489361)
    assert summary_rows["mmlu_pro"][
        "conservative_iter0010110_minus_original"
    ] == pytest.approx(0.010305851063829786)

    assert by_id["mmlu_pro"]["comparison_vs_baselines"][
        "qwen3_30b_a3b_sft_iter0009119"
    ] == pytest.approx(0.07737699468085106)


def test_task071_qwen3_30b_a3b_conservative_results_do_not_store_secret_tokens() -> None:
    text = TASK071_QWEN3_30B_A3B_CONSERVATIVE_FULL_NON_DRY_RESULTS_PATH.read_text(
        encoding="utf-8"
    )
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "HF_TOKEN" not in text


def test_launcher_available_config_expands_into_evaluator_schema() -> None:
    """The recipe CLI must merge the compact basket overlay with
    default.yaml; otherwise dry-run only prints top-level tasks and the
    launcher receives no execution/deployment/evaluation schema."""
    ctx = SimpleNamespace(
        config="m1_full_basket_launcher_available",
        dotlist=[],
    )
    config = load_stage3_eval_config(ctx, REPO_ROOT / CONFIG_DIR, "default")

    expected = {
        row["launcher_task"]
        for row in _load_launcher_rows()
        if row["status"] == "available"
    }
    tasks = {task["name"] for task in config.evaluation.tasks}

    assert tasks == expected
    assert "execution" in config
    assert "deployment" in config
    assert "tasks" not in config


def test_eval_config_normalization_matches_launcher_0_2_schema() -> None:
    ctx = SimpleNamespace(
        config="m1_full_basket_launcher_available",
        dotlist=[],
    )
    config = load_stage3_eval_config(ctx, REPO_ROOT / CONFIG_DIR, "default")
    assert "env_vars" in config.execution

    normalize_evaluator_launcher_config(config)

    assert "env_vars" not in config.execution
    assert config.execution.mode == "sequential"
    assert config.evaluation.env_vars.HF_HOME == "lit:/cache/huggingface"
    assert config.deployment.env_vars.HF_TOKEN == "host:HF_TOKEN"


# ---------- regression_report works on combined gate map ----------


def _combined_gate_map() -> dict[str, str]:
    """Merge v0 + full registries the way task020 Session 2 CLI will."""
    out: dict[str, str] = {}
    for path in (V0_REGISTRY_PATH, FULL_REGISTRY_PATH):
        for row in _load_rows(path):
            out[row["benchmark_id"]] = row["gate_metric"]
    return out


def test_combined_gate_map_drives_diff_across_both_registries() -> None:
    """Spot-check that diff_eval_runs treats v0 and full rows
    interchangeably under a single merged lookup — covers the Session 2
    CLI's combined-basket plumbing without needing the CLI itself."""
    gate_map = _combined_gate_map()
    assert "mmlu_pro" in gate_map and "hmmt" in gate_map
    current = {
        "tasks": {
            "mmlu_pro": {"metrics": {"accuracy": 0.66}},
            "hmmt": {"metrics": {"pass_at_1": 0.18}},
            "bfcl": {"metrics": {"accuracy": 0.71}},
        }
    }
    baseline = {
        "tasks": {
            "mmlu_pro": {"metrics": {"accuracy": 0.62}},
            "hmmt": {"metrics": {"pass_at_1": 0.20}},
            "bfcl": {"metrics": {"accuracy": 0.71}},
        }
    }
    deltas = diff_eval_runs(current, baseline, gate_metric_by_id=gate_map)
    statuses = {d.benchmark_id: d.status for d in deltas}
    assert statuses == {
        "mmlu_pro": "improved",
        "hmmt": "regressed",
        "bfcl": "unchanged",
    }


def test_combined_gate_map_metric_lookup_matches_registry_for_full_rows() -> None:
    """Every full-basket row's gate_metric must appear under its
    benchmark_id in the merged map — protects against silent rename
    drift between yaml and the in-memory dict."""
    gate_map = _combined_gate_map()
    for row in _load_rows(FULL_REGISTRY_PATH):
        assert gate_map[row["benchmark_id"]] == row["gate_metric"]
