"""Tests for task072 Qwen-first eval reproduction gate."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m1_eval_basket.benchmark_alignment import (  # noqa: E402
    BENCHMARK_ALIGNMENT_LEDGER_PATH,
    load_benchmark_alignment_ledger,
    valid_benchmark_improvement_evidence,
    validate_benchmark_alignment_ledger,
)
from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_eval_repro_gate import (  # noqa: E402
    QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS,
    QWEN_EVAL_REPRO_GATE_PATH,
    VALID_ARTIFACT_CHECK_STATUSES,
    format_qwen_eval_repro_gate_report,
    load_qwen_eval_repro_gate,
    qwen_repro_evidence_by_benchmark,
    validate_qwen_eval_repro_gate,
    validate_raw_artifact_paths,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


# The production YAML references absolute paths under
# /work-agents/intern_nemontron_code_reading/... that only exist on the
# author's workstation. Tests that call `load_qwen_eval_repro_gate()`
# directly fail on a clean sandbox where those paths don't exist. We
# detect this once at module load and mark the load-dependent tests
# skip-if-unloadable; synthetic tests that build their own gate dicts
# (e.g. via `_gate_data()` + edits) still run.
try:
    load_qwen_eval_repro_gate()
    _PRODUCTION_GATE_LOAD_ERROR: str | None = None
except (FileNotFoundError, ValueError) as exc:
    _PRODUCTION_GATE_LOAD_ERROR = str(exc).splitlines()[0]

requires_production_gate = pytest.mark.skipif(
    _PRODUCTION_GATE_LOAD_ERROR is not None,
    reason=(
        "Qwen eval repro gate YAML references local-only artifacts not "
        f"present in this environment: {_PRODUCTION_GATE_LOAD_ERROR}"
    ),
)


def _gate_data() -> dict:
    return yaml.safe_load(QWEN_EVAL_REPRO_GATE_PATH.read_text(encoding="utf-8"))


def _alignment_ledger_data() -> dict:
    return yaml.safe_load(BENCHMARK_ALIGNMENT_LEDGER_PATH.read_text(encoding="utf-8"))


@requires_production_gate
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


@requires_production_gate
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


def test_remote_raw_artifact_refs_reject_unverified_statuses() -> None:
    assert VALID_ARTIFACT_CHECK_STATUSES == {
        "pm_verified",
        "local_workspace_verified",
    }
    for status in ("unchecked", "unverified", "missing", "reviewed_elsewhere"):
        data = _gate_data()
        record = data["evidence_records"][1]
        record["remote_artifact_check"]["status"] = status

        issues = validate_qwen_eval_repro_gate(data)

        assert any(
            "remote_artifact_check.status must be one of" in issue
            and status in issue
            for issue in issues
        ), f"expected status rejection for {status!r}, got: {issues}"


def test_vm4vpn_remote_raw_artifact_refs_require_pm_verified_status() -> None:
    data = deepcopy(_gate_data())
    record = data["evidence_records"][1]
    assert any(
        path.startswith("vm4vpn:") for path in record["raw_artifact_paths"]
    )
    record["remote_artifact_check"]["status"] = "local_workspace_verified"

    issues = validate_qwen_eval_repro_gate(data)

    assert any(
        "remote_artifact_check.status must be 'pm_verified' for remote raw "
        "artifact references" in issue
        for issue in issues
    ), f"expected vm4vpn remote artifact pm_verified issue, got: {issues}"


def test_vpn_remote_raw_artifact_refs_require_pm_verified_status() -> None:
    data = deepcopy(_gate_data())
    record = data["evidence_records"][0]
    record["raw_artifact_paths"] = [
        "vpn:/tmp/task071_vpn_eval_qwen30b_original_full/mmlu_pro/results.yml"
    ]
    record["remote_artifact_check"] = {
        "status": "local_workspace_verified",
        "checked_at_utc": "2026-05-28T20:46:00Z",
        "checked_by": "intern_nem_dev_2",
    }

    issues = validate_qwen_eval_repro_gate(data)

    assert any(
        "remote_artifact_check.status must be 'pm_verified' for remote raw "
        "artifact references" in issue
        for issue in issues
    ), f"expected vpn remote artifact pm_verified issue, got: {issues}"


def test_local_raw_artifacts_allow_local_workspace_verified_status(
    tmp_path: Path,
) -> None:
    data = deepcopy(_gate_data())
    local_artifact = tmp_path / "local_artifact.json"
    local_artifact.write_text("{}\n", encoding="utf-8")
    record = data["evidence_records"][0]
    record["raw_artifact_paths"] = [str(local_artifact)]
    record["remote_artifact_check"] = {
        "status": "local_workspace_verified",
        "checked_at_utc": "2026-05-28T20:46:00Z",
        "checked_by": "intern_nem_dev_2",
    }

    issues = validate_qwen_eval_repro_gate(data)

    assert issues == []


@requires_production_gate
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


@requires_production_gate
def test_qwen_eval_repro_gate_groups_valid_evidence_by_benchmark() -> None:
    grouped = qwen_repro_evidence_by_benchmark()

    assert "mmlu_pro" in grouped
    assert "aime25_hmmt_probe" in grouped
    assert "aime25_hmmt_full" in grouped
    assert grouped["mmlu_pro"][0]["route"] == "/v1/chat/completions"


@requires_production_gate
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


@requires_production_gate
def test_qwen_eval_repro_gate_records_live_endpoint_blocker_probe() -> None:
    gate = load_qwen_eval_repro_gate()
    blockers = {blocker["blocker_id"]: blocker for blocker in gate["runtime_blockers"]}

    blocker = blockers["fresh_live_qwen_endpoint_unavailable"]
    assert blocker["status"] == "blocked_in_this_workspace"
    assert any("127.0.0.1:13000" in command for command in blocker["probe_commands"])
    assert "connection refused" in blocker["observed_result"]


@requires_production_gate
def test_qwen_eval_repro_gate_records_endpoint_inventory_without_qwen() -> None:
    gate = load_qwen_eval_repro_gate()
    blockers = {blocker["blocker_id"]: blocker for blocker in gate["runtime_blockers"]}

    blocker = blockers["endpoint_inventory_has_no_qwen_surface"]
    assert blocker["status"] == "blocked_in_available_endpoint_inventory"
    assert "endpoints.txt" in " ".join(blocker["probe_commands"])
    assert "qwen_endpoint_hits=0" in blocker["observed_result"]


@requires_production_gate
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


def test_qwen_eval_repro_gate_validator_pins_chat_template_kwarg_values() -> None:
    """Regression: `_validate_chat_template_kwargs` previously only
    type-checked (bool present). A YAML edit re-introducing
    `enable_thinking: true` — undoing PR D's SFT/RL alignment — would
    silently pass. The Qwen reproduction gate exists to enforce the
    Qwen chat-template contract; it must enforce the contract
    VALUES, not just types.
    """
    # Contract sanity: both kwargs must be False.
    assert QWEN_CHAT_TEMPLATE_REQUIRED_KWARGS == {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }

    # Flip enable_thinking to True on the intended eval path — validator
    # must surface the contract violation, not silently accept it.
    data = deepcopy(_gate_data())
    data["intended_eval_path"]["chat_template_kwargs"]["enable_thinking"] = True
    issues = validate_qwen_eval_repro_gate(data)
    assert any(
        "intended_eval_path.chat_template_kwargs.enable_thinking must be False" in issue
        for issue in issues
    ), f"expected enable_thinking value violation, got: {issues}"

    # Same protection at the per-evidence level — task072 evidence
    # records are part of the Qwen contract too.
    data = deepcopy(_gate_data())
    data["evidence_records"][0]["chat_template_kwargs"]["truncate_history_thinking"] = True
    issues = validate_qwen_eval_repro_gate(data)
    assert any(
        "truncate_history_thinking must be False" in issue for issue in issues
    ), f"expected truncate_history_thinking value violation, got: {issues}"


def test_qwen_benchmark_alignment_ledger_loads_and_records_no_task071_improvement() -> None:
    ledger = load_benchmark_alignment_ledger()

    corrected = next(
        suite
        for suite in ledger["target_suites"]
        if suite["suite_id"] == "m1_qwen_corrected_improvement_subset"
    )
    assert corrected["benchmark_ids"] == ["mmlu_pro", "aime25", "hmmt"]
    assert valid_benchmark_improvement_evidence(ledger) == []
    assert {
        record["benchmark_id"] for record in ledger["evidence_records"]
    } == {"mmlu_pro", "aime25", "hmmt"}


def test_qwen_benchmark_alignment_rejects_completions_only_evidence() -> None:
    data = deepcopy(_alignment_ledger_data())
    data["evidence_records"][0]["endpoint_type"] = "openai_completions"
    data["evidence_records"][0]["route"] = "/v1/completions"

    issues = validate_benchmark_alignment_ledger(data)

    assert any("completions-only evidence cannot count" in issue for issue in issues)


def test_qwen_benchmark_alignment_rejects_short_cap_math_evidence() -> None:
    data = deepcopy(_alignment_ledger_data())
    aime = next(
        record
        for record in data["evidence_records"]
        if record["benchmark_id"] == "aime25"
    )
    aime["max_generation_tokens"] = 2048

    issues = validate_benchmark_alignment_ledger(data)

    assert any("short generation cap cannot count" in issue for issue in issues)


def test_qwen_benchmark_alignment_rejects_parser_misaligned_evidence() -> None:
    data = deepcopy(_alignment_ledger_data())
    hmmt = next(
        record
        for record in data["evidence_records"]
        if record["benchmark_id"] == "hmmt"
    )
    hmmt["parser"] = "free_text_contains_answer"

    issues = validate_benchmark_alignment_ledger(data)

    assert any("parser-misaligned evidence cannot count" in issue for issue in issues)


def test_qwen_benchmark_alignment_rejects_missing_raw_artifacts() -> None:
    data = deepcopy(_alignment_ledger_data())
    data["evidence_records"][0]["raw_artifact_paths"] = [
        "/tmp/task079_missing_raw_artifact.jsonl"
    ]

    issues = validate_benchmark_alignment_ledger(data)

    assert any("missing raw artifact evidence cannot count" in issue for issue in issues)


def test_qwen_benchmark_alignment_rejects_unverified_artifact_check_statuses() -> None:
    for status in ("unchecked", "unverified", "missing", "reviewed_elsewhere"):
        data = deepcopy(_alignment_ledger_data())
        data["evidence_records"][0]["artifact_check"]["status"] = status

        issues = validate_benchmark_alignment_ledger(data)

        assert any(
            "artifact_check.status must be one of" in issue and status in issue
            for issue in issues
        ), f"expected status rejection for {status!r}, got: {issues}"


def test_qwen_benchmark_alignment_remote_raw_refs_require_pm_verified() -> None:
    data = deepcopy(_alignment_ledger_data())
    data["evidence_records"][0]["artifact_check"]["status"] = (
        "local_workspace_verified"
    )

    issues = validate_benchmark_alignment_ledger(data)

    assert any(
        "artifact_check.status must be 'pm_verified' for remote raw artifact references"
        in issue
        for issue in issues
    ), f"expected remote artifact pm_verified issue, got: {issues}"


def test_qwen_benchmark_alignment_current_remote_artifacts_are_pm_verified() -> None:
    ledger = load_benchmark_alignment_ledger()

    for record in ledger["evidence_records"]:
        if any(
            isinstance(path, str) and path.startswith(("vm4vpn:", "vpn:"))
            for path in record["raw_artifact_paths"]
        ):
            assert record["artifact_check"]["status"] == "pm_verified"


def test_qwen_benchmark_alignment_requires_existing_repo_relative_source_manifests() -> None:
    data = deepcopy(_alignment_ledger_data())
    data["evidence_records"][0]["source_manifests"] = [
        "/tmp/not_repo_relative.yaml"
    ]

    issues = validate_benchmark_alignment_ledger(data)
    assert any("source_manifests must be repo-relative" in issue for issue in issues)

    data = deepcopy(_alignment_ledger_data())
    data["evidence_records"][0]["source_manifests"] = [
        "src/nemotron/recipes/super3/milestones/m1_eval_basket/missing.yaml"
    ]

    issues = validate_benchmark_alignment_ledger(data)
    assert any("source_manifests repo-relative path does not exist" in issue for issue in issues)
