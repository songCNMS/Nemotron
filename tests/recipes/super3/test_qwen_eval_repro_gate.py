"""Tests for task072 Qwen-first eval reproduction gate."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_eval_repro_gate import (  # noqa: E402
    QWEN_EVAL_REPRO_GATE_PATH,
    format_qwen_eval_repro_gate_report,
    load_qwen_eval_repro_gate,
    qwen_repro_evidence_by_benchmark,
    validate_raw_artifact_paths,
    validate_qwen_eval_repro_gate,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def _gate_data() -> dict:
    return yaml.safe_load(QWEN_EVAL_REPRO_GATE_PATH.read_text(encoding="utf-8"))


def test_qwen_eval_repro_gate_loads_valid_qwen_first_contract() -> None:
    gate = load_qwen_eval_repro_gate()

    assert gate["gate_id"] == "task072_qwen_eval_repro_gate_s1"
    assert gate["super3_template_consistency_is_sufficient"] is False
    assert gate["reference_model"]["source_model"] == (
        "Qwen/Qwen3-30B-A3B-Instruct-2507"
    )
    assert gate["reference_model"]["qwen_first"] is True
    assert gate["intended_eval_path"]["endpoint_type"] == (
        "openai_chat_completions"
    )
    assert gate["intended_eval_path"]["chat_route"] == "/v1/chat/completions"


def test_qwen_eval_repro_gate_source_manifests_exist() -> None:
    gate = load_qwen_eval_repro_gate()

    for manifest in gate["source_manifests"]:
        assert (REPO_ROOT / manifest).is_file(), manifest


def test_qwen_eval_repro_gate_requires_qwen_not_super3_only() -> None:
    data = _gate_data()
    data["super3_template_consistency_is_sufficient"] = True
    data["reference_model"]["source_model"] = "nvidia/super3"
    data["reference_model"]["qwen_first"] = False

    issues = validate_qwen_eval_repro_gate(data)

    assert any("must be false" in issue for issue in issues)
    assert any("must name a Qwen model" in issue for issue in issues)
    assert any("qwen_first must be true" in issue for issue in issues)


def test_qwen_eval_repro_gate_requires_raw_artifacts_for_evidence() -> None:
    data = _gate_data()
    data["evidence_records"][0]["raw_artifact_paths"] = []

    issues = validate_qwen_eval_repro_gate(data)

    assert any("raw_artifact_paths must be non-empty" in issue for issue in issues)


def test_qwen_eval_repro_gate_rejects_missing_local_raw_artifacts() -> None:
    data = _gate_data()
    data["evidence_records"][0]["raw_artifact_paths"] = [
        "/tmp/task072_missing_raw_artifact.json"
    ]

    issues = validate_qwen_eval_repro_gate(data)

    assert any("local path does not exist" in issue for issue in issues)


def test_remote_raw_artifact_refs_require_check_metadata() -> None:
    data = _gate_data()
    data["evidence_records"][0]["raw_artifact_paths"] = [
        "vm4vpn:/tmp/task071_vpn_eval_qwen30b_original_full/mmlu_pro/results.yml"
    ]
    data["evidence_records"][0].pop("remote_artifact_check", None)

    issues = validate_qwen_eval_repro_gate(data)

    assert any("remote_artifact_check must be a mapping" in issue for issue in issues)


def test_gate_raw_artifacts_are_existing_local_or_checked_remote_refs() -> None:
    gate = load_qwen_eval_repro_gate()

    for record in gate["evidence_records"]:
        assert (
            validate_raw_artifact_paths(
                record["raw_artifact_paths"],
                context=record["evidence_id"],
            )
            == []
        )
        if any(path.startswith("vm4vpn:") for path in record["raw_artifact_paths"]):
            assert record["remote_artifact_check"]["status"] == "pm_verified"


def test_qwen_eval_repro_gate_groups_valid_evidence_by_benchmark() -> None:
    grouped = qwen_repro_evidence_by_benchmark()

    assert "mmlu_pro" in grouped
    assert "aime25_hmmt_probe" in grouped
    assert "aime25_hmmt_full" in grouped
    assert grouped["mmlu_pro"][0]["route"] == "/v1/chat/completions"


def test_qwen_eval_repro_gate_records_invalid_legacy_surfaces() -> None:
    gate = load_qwen_eval_repro_gate()
    issue_types = {
        issue_type
        for finding in gate["invalid_task_findings"]
        for issue_type in finding["issue_types"]
    }

    assert {"completions_only", "short_generation_capped", "parser_misaligned"} <= (
        issue_types
    )
    mmlu = next(
        finding
        for finding in gate["invalid_task_findings"]
        if finding["benchmark_id"] == "mmlu_pro"
    )
    assert "completions_only" in mmlu["issue_types"]


def test_qwen_eval_repro_gate_rejects_missing_invalid_surface_type() -> None:
    data = _gate_data()
    for finding in data["invalid_task_findings"]:
        finding["issue_types"] = [
            item for item in finding["issue_types"] if item != "completions_only"
        ]

    issues = validate_qwen_eval_repro_gate(data)

    assert any("invalid_task_findings must cover issue types" in issue for issue in issues)


def test_qwen_eval_repro_gate_records_live_endpoint_blocker_probe() -> None:
    gate = load_qwen_eval_repro_gate()
    blockers = {blocker["blocker_id"]: blocker for blocker in gate["runtime_blockers"]}

    blocker = blockers["fresh_live_qwen_endpoint_unavailable"]
    assert blocker["status"] == "blocked_in_this_workspace"
    assert any("127.0.0.1:13000" in command for command in blocker["probe_commands"])
    assert "connection refused" in blocker["observed_result"]


def test_qwen_eval_repro_gate_records_endpoint_inventory_without_qwen() -> None:
    gate = load_qwen_eval_repro_gate()
    blockers = {blocker["blocker_id"]: blocker for blocker in gate["runtime_blockers"]}

    blocker = blockers["endpoint_inventory_has_no_qwen_surface"]
    assert blocker["status"] == "blocked_in_available_endpoint_inventory"
    assert "endpoints.txt" in " ".join(blocker["probe_commands"])
    assert "qwen_endpoint_hits=0" in blocker["observed_result"]


def test_qwen_eval_repro_gate_report_is_reviewable() -> None:
    text = format_qwen_eval_repro_gate_report()

    assert text.startswith("# Qwen eval reproduction gate: task072")
    assert "Reference model: `Qwen/Qwen3-30B-A3B-Instruct-2507`" in text
    assert "`mmlu_pro` via `/v1/chat/completions`" in text
    assert "fresh_live_qwen_endpoint_unavailable" in text


def test_qwen_eval_repro_gate_validator_rejects_non_chat_evidence_route() -> None:
    data = deepcopy(_gate_data())
    data["evidence_records"][0]["route"] = "/v1/completions"

    issues = validate_qwen_eval_repro_gate(data)

    assert any("route must be /v1/chat/completions" in issue for issue in issues)
