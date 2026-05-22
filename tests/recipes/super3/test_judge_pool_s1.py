"""Tests for task034 Session 1 judge-pool scaffold."""

from __future__ import annotations

import pytest

from nemotron.recipes.super3.milestones.m2_judge_pool import (
    DEFAULT_JUDGE_POOL_BLOCKERS,
    CalibrationSet,
    DeferredLiveJudgeAdapter,
    JudgeModelVersion,
    JudgeRequest,
    JudgeVersionRegistry,
    MockJudge,
    build_default_sandbox_judge_pool,
    evaluate_ensemble,
    format_ensemble_report,
)


def _request(request_id: str = "req-001") -> JudgeRequest:
    return JudgeRequest(
        request_id=request_id,
        env_id="safety_judge",
        prompt="Classify this response.",
        candidate_response="ALLOW: benign educational content",
        reference_response="ALLOW",
        rubric="Return pass for an aligned safety verdict.",
    )


def test_registry_resolves_alias_to_frozen_judge_version() -> None:
    registry = build_default_sandbox_judge_pool()

    version = registry.resolve_version("safety_primary")

    assert version.version_key == "safety_judge@mock-s1"
    assert version.frozen is True
    assert version.calibration_set_id == "safety_calibration_s1"
    assert registry.resolve_version("safety_judge@mock-s1") == version
    assert registry.aliases["genrm_primary"] == "genrm_compare@mock-s1"


def test_calibration_metadata_validation_and_normalization() -> None:
    calibration = CalibrationSet(
        calibration_set_id="calib",
        env_id="browser_qa",
        revision="rev-a",
        sample_count=4,
        score_min=0.2,
        score_max=0.8,
        score_mean=0.5,
        score_std=0.1,
    )

    assert calibration.calibrate_score(0.5) == pytest.approx(0.5)
    assert calibration.calibrate_score(1.0) == 1.0
    assert calibration.z_score(0.7) == pytest.approx(2.0)

    with pytest.raises(ValueError, match="sample_count"):
        CalibrationSet("bad", "env", "rev", sample_count=0)
    with pytest.raises(ValueError, match="score_std"):
        CalibrationSet("bad", "env", "rev", sample_count=1, score_std=0.0)
    with pytest.raises(ValueError, match="score_min"):
        CalibrationSet("bad", "env", "rev", sample_count=1, score_min=1.0, score_max=1.0)


def test_mock_judge_carries_frozen_version_through_result() -> None:
    registry = build_default_sandbox_judge_pool()
    judge = registry.build_mock_judge(
        "safety_primary",
        score_overrides={"req-001": {"score": 0.9, "confidence": 0.8}},
    )

    response = judge.judge(_request())

    assert response.judge_version.version_key == "safety_judge@mock-s1"
    assert response.judge_version.frozen is True
    assert response.calibration_set_id == "safety_calibration_s1"
    assert response.score == pytest.approx(0.9)
    assert response.confidence == pytest.approx(0.8)
    assert response.label == "pass"
    assert response.to_jsonable()["judge_version"]["version_key"] == "safety_judge@mock-s1"


def test_ensemble_voting_and_confidence_aggregation_are_deterministic() -> None:
    request = _request("ensemble-001")
    versions = (
        JudgeModelVersion(judge_id="judge_b", version="mock-s1"),
        JudgeModelVersion(judge_id="judge_a", version="mock-s1"),
        JudgeModelVersion(judge_id="judge_c", version="mock-s1"),
    )
    registry = JudgeVersionRegistry(versions=versions)
    judges = [
        MockJudge(
            version=registry.resolve_version("judge_b@mock-s1"),
            score_overrides={"ensemble-001": {"score": 0.0, "confidence": 0.6}},
        ),
        MockJudge(
            version=registry.resolve_version("judge_a@mock-s1"),
            score_overrides={"ensemble-001": {"score": 1.0, "confidence": 0.9}},
        ),
        MockJudge(
            version=registry.resolve_version("judge_c@mock-s1"),
            score_overrides={"ensemble-001": {"score": 0.75, "confidence": 0.8}},
        ),
    ]

    result = evaluate_ensemble(request, judges)
    repeat = evaluate_ensemble(request, list(reversed(judges)))

    assert result.to_jsonable() == repeat.to_jsonable()
    assert result.judge_version_keys == (
        "judge_a@mock-s1",
        "judge_b@mock-s1",
        "judge_c@mock-s1",
    )
    assert result.aggregate_score == pytest.approx(0.583333)
    assert result.aggregate_confidence == pytest.approx(0.766667)
    assert result.votes_by_label == {"fail": 1, "pass": 2}
    assert result.label == "pass"


def test_deterministic_hash_mock_score_is_stable() -> None:
    version = JudgeModelVersion(judge_id="hash_judge", version="mock-s1")
    judge = MockJudge(version=version)
    request = _request("hash-001")

    first = judge.judge(request)
    second = judge.judge(request)

    assert first.to_jsonable() == second.to_jsonable()
    assert first.metadata["score_source"] == "deterministic_hash"


def test_live_adapter_boundary_is_explicitly_deferred() -> None:
    adapter = DeferredLiveJudgeAdapter(endpoint_name="genrm-live")

    with pytest.raises(NotImplementedError, match="live judge service adapter is deferred"):
        adapter.judge(_request())

    payload = adapter.to_jsonable()
    assert payload["status"] == "deferred"
    for blocker in DEFAULT_JUDGE_POOL_BLOCKERS:
        assert blocker in payload["blockers"]


def test_ensemble_report_includes_versions_and_blockers() -> None:
    registry = build_default_sandbox_judge_pool()
    judges = registry.build_default_mock_ensemble(
        score_overrides={
            "safety_primary": {"req-001": {"score": 0.9, "confidence": 0.8}},
            "if_primary": {"req-001": {"score": 0.7, "confidence": 0.7}},
            "genrm_primary": {"req-001": {"score": 0.4, "confidence": 0.6}},
        }
    )

    text = format_ensemble_report(evaluate_ensemble(_request(), judges))

    assert "# Judge ensemble result: **PASS**" in text
    assert "safety_judge@mock-s1" in text
    assert "genrm_compare@mock-s1" in text
    for blocker in DEFAULT_JUDGE_POOL_BLOCKERS:
        assert blocker in text
