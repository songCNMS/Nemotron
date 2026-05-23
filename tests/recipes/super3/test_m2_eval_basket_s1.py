"""Tests for task039 M2 eval basket Session 1 scaffold."""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m2_eval_basket.registry import (  # noqa: E402
    ADAPTER_CONFIG_PATH,
    EXPECTED_M2_BENCHMARK_IDS,
    REGISTRY_PATH,
    adapter_config_by_id,
    benchmarks_by_category,
    format_runtime_blocker_report,
    load_m2_adapter_config,
    load_m2_eval_basket,
    runtime_blockers,
    validate_m2_adapter_config,
    validate_m2_eval_basket,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_m2_eval_basket_registry_loads_expected_benchmarks() -> None:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    rows = load_m2_eval_basket()

    assert data["schema_version"] == 1
    assert data["milestone"] == "M2"
    assert len(rows) == 8
    assert {row["benchmark_id"] for row in rows} == EXPECTED_M2_BENCHMARK_IDS


def test_all_planned_m2_benchmark_families_are_declared() -> None:
    rows = {row["benchmark_id"]: row for row in load_m2_eval_basket()}

    expected_categories = {
        "hle": "reasoning_extreme_difficulty",
        "browsecomp": "browser_search",
        "bird_real_execution": "sql_execution",
        "bfcl_full": "tool_use_function_call",
        "mcp_mark": "tool_use_mcp",
        "tool_decathlon": "tool_use_agentic",
        "multilingual_ifeval": "multilingual_instruction_following",
        "multilingual_humaneval": "multilingual_code",
    }
    assert {
        benchmark_id: rows[benchmark_id]["category"]
        for benchmark_id in expected_categories
    } == expected_categories


def test_adapter_metadata_and_profiles_match_registry_rows() -> None:
    rows = load_m2_eval_basket()
    registry_adapters = adapter_config_by_id(rows)
    profiles = {row["benchmark_id"]: row for row in load_m2_adapter_config()}

    assert set(profiles) == EXPECTED_M2_BENCHMARK_IDS
    for benchmark_id, adapter in registry_adapters.items():
        profile = profiles[benchmark_id]
        assert adapter["task_name"] == profile["task_name"]
        assert adapter["evaluator_task"] == profile["evaluator_task"]
        assert profile["adapter"] == f"nemo_evaluator.{benchmark_id}"
        assert profile["dry_run_mode"] == "config_validate_only"
        assert profile["default_runtime"] == "cluster_deferred"


def test_benchmarks_by_category_groups_rows_for_reporting() -> None:
    grouped = benchmarks_by_category()

    assert grouped["browser_search"][0]["benchmark_id"] == "browsecomp"
    assert grouped["sql_execution"][0]["benchmark_id"] == "bird_real_execution"
    assert {
        row["benchmark_id"]
        for row in grouped["tool_use_agentic"]
    } == {"tool_decathlon"}


def test_runtime_blockers_surface_cluster_api_assets_and_baseline() -> None:
    blockers = {row["benchmark_id"]: row for row in runtime_blockers()}

    assert set(blockers) == EXPECTED_M2_BENCHMARK_IDS
    assert all(row["cluster_required"] for row in blockers.values())
    assert all(row["live_assets_required"] for row in blockers.values())
    assert all(row["qwen_baseline_required"] for row in blockers.values())
    assert blockers["browsecomp"]["api_required"]
    assert blockers["mcp_mark"]["api_required"]
    assert blockers["tool_decathlon"]["api_required"]
    assert blockers["bird_real_execution"]["database_required"]
    assert "BIRD database assets" in " ".join(
        blockers["bird_real_execution"]["blockers"]
    )


def test_runtime_blocker_report_mentions_deferred_runtime_surfaces() -> None:
    text = format_runtime_blocker_report()

    assert "8 benchmark(s) deferred" in text
    assert "browsecomp" in text
    assert "api_required" in text
    assert "bird_real_execution" in text
    assert "database_required" in text
    assert "qwen_baseline_required" in text


def test_registry_and_adapter_config_validate_clean() -> None:
    registry_data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    adapter_data = yaml.safe_load(ADAPTER_CONFIG_PATH.read_text(encoding="utf-8"))

    assert validate_m2_eval_basket(registry_data) == []
    assert validate_m2_adapter_config(adapter_data) == []


def test_validator_rejects_missing_runtime_blockers() -> None:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    data["benchmarks"][0]["runtime_requirements"]["blockers"] = []

    issues = validate_m2_eval_basket(data)

    assert any("blockers must be non-empty strings" in issue for issue in issues)


def test_adapter_config_validator_rejects_duplicate_benchmark_ids() -> None:
    """Regression: ``validate_m2_eval_basket`` catches duplicate
    ``benchmark_id``s in the registry, but the sibling
    ``validate_m2_adapter_config`` previously did not — a YAML edit that
    listed the same id twice across adapter profiles slipped through.
    Both validators should agree on uniqueness as the data contract."""
    data = yaml.safe_load(ADAPTER_CONFIG_PATH.read_text(encoding="utf-8"))
    duplicate = dict(data["adapter_profiles"][0])
    data["adapter_profiles"].append(duplicate)

    issues = validate_m2_adapter_config(data)

    assert any("duplicate benchmark_id" in issue for issue in issues)


def test_unified_index_registers_m2_eval_basket_and_validates_clean() -> None:
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        load_unified_index,
        validate_unified_index,
    )

    rows = load_unified_index()
    m2_rows = [row for row in rows if row["id"] == "m2_eval_basket"]
    assert len(m2_rows) == 1
    assert m2_rows[0]["kind"] == "eval_basket_registry"
    assert validate_unified_index() == []


def test_task039_docs_record_session_scope() -> None:
    task_dir = REPO_ROOT / "workspace/tasks/task039_m2_eval_basket"
    assert (task_dir / "README.md").is_file()
    assert (task_dir / "history_log.md").is_file()
    assert (task_dir / "task_knowledge.md").is_file()
