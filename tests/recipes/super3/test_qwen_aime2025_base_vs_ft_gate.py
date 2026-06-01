"""Tests for the task243 Qwen AIME2025 base-vs-FT gate."""

from __future__ import annotations

from copy import deepcopy

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_aime2025_base_vs_ft_gate import (  # noqa: E402
    QWEN_AIME2025_BASE_VS_FT_GATE_PATH,
    evaluate_base_vs_ft_gate,
    format_base_vs_ft_report,
    load_base_vs_ft_gate_config,
    normalize_aime2025_rows,
    validate_base_vs_ft_gate_config,
)


def _gate_data() -> dict:
    return yaml.safe_load(
        QWEN_AIME2025_BASE_VS_FT_GATE_PATH.read_text(encoding="utf-8")
    )


def _protocol() -> dict:
    return load_base_vs_ft_gate_config()["protocols"]["pilot_smoke"]


def _rows(*, correct: int, total: int, parsed: int | None = None) -> list[dict]:
    parsed = correct if parsed is None else parsed
    rows = []
    for index in range(total):
        is_correct = index < correct
        is_parsed = index < parsed
        problem = (index % 3) + 1
        repeat = (index // 3) + 1
        rows.append(
            {
                "task": "aime25",
                "sample_id": f"aime_{problem:02d}_r{repeat:02d}",
                "status": "ok",
                "finish_reason": "stop" if is_parsed else "length",
                "parsed": is_parsed,
                "correct": is_correct,
            }
        )
    return rows


def _score(*, correct: int, total: int, parsed: int | None = None, protocol: dict | None = None):
    return normalize_aime2025_rows(
        _rows(correct=correct, total=total, parsed=parsed),
        model_id="Qwen/Qwen3-4B-Instruct-2507",
        model_path="/models/qwen3-4b",
        protocol=protocol or _protocol(),
        artifact_paths=("results.jsonl",),
    )


def test_task243_gate_config_loads_and_pins_base_required_contract() -> None:
    gate = load_base_vs_ft_gate_config()

    assert validate_base_vs_ft_gate_config(_gate_data()) == []
    assert gate["base_score_required"] is True
    assert gate["ft_must_be_at_least_base"] is True
    assert gate["parsed_rate_is_diagnostic_only"] is True
    assert gate["protocols"]["pilot_smoke"]["route"] == "/v1/chat/completions"
    assert gate["protocols"]["pilot_smoke"]["chat_template_kwargs"] == {
        "enable_thinking": False,
        "truncate_history_thinking": False,
    }


def test_task243_gate_rejects_completions_route_and_thinking_drift() -> None:
    data = _gate_data()
    data["protocols"]["pilot_smoke"]["route"] = "/v1/completions"
    data["protocols"]["pilot_smoke"]["chat_template_kwargs"]["enable_thinking"] = True

    issues = validate_base_vs_ft_gate_config(data)

    assert any("route must be /v1/chat/completions" in issue for issue in issues)
    assert any("enable_thinking must be False" in issue for issue in issues)


def test_normalize_aime2025_rows_counts_all_requests_and_diagnostics() -> None:
    score = _score(correct=2, total=4, parsed=3)

    assert score.numerator == 2
    assert score.denominator == 4
    assert score.exact_normalized_accuracy == 0.5
    assert score.parsed_count == 3
    assert score.parsed_rate == 0.75
    assert score.finish_reason_counts == {"length": 1, "stop": 3}
    assert score.status_counts == {"ok": 4}
    assert score.per_problem_rows["aime_01"]["rows"] == 2
    assert score.per_problem_rows["aime_01"]["correct_rows"] == 1


def test_gate_blocks_ft_judgment_without_same_harness_base_score() -> None:
    ft = _score(correct=3, total=4, parsed=4)

    decision = evaluate_base_vs_ft_gate(base_score=None, ft_score=ft)

    assert decision.status == "blocked_missing_base"
    assert decision.delta_exact_normalized_accuracy is None
    assert decision.diagnostics["ft_judged"] is False
    assert "same-harness base" in decision.reasons[0]


def test_gate_fails_when_ft_exact_normalized_score_is_lower_than_base() -> None:
    base = _score(correct=3, total=4, parsed=3)
    ft = _score(correct=2, total=4, parsed=4)

    decision = evaluate_base_vs_ft_gate(base_score=base, ft_score=ft)

    assert decision.status == "fail_ft_below_base"
    assert decision.delta_exact_normalized_accuracy == pytest.approx(-0.25)
    assert decision.diagnostics["base_parsed_rate"] == 0.75
    assert decision.diagnostics["ft_parsed_rate"] == 1.0
    assert "lower than base" in decision.reasons[0]


def test_gate_passes_when_ft_matches_base_under_same_harness() -> None:
    base = _score(correct=2, total=4, parsed=2)
    ft = _score(correct=2, total=4, parsed=4)

    decision = evaluate_base_vs_ft_gate(base_score=base, ft_score=ft)

    assert decision.status == "pass_ft_at_least_base"
    assert decision.delta_exact_normalized_accuracy == pytest.approx(0.0)
    assert "finish reasons" in format_base_vs_ft_report(decision)


def test_gate_rejects_base_ft_protocol_mismatch() -> None:
    base = _score(correct=2, total=4)
    ft_protocol = deepcopy(_protocol())
    ft_protocol["max_tokens"] = 4096
    ft = _score(correct=3, total=4, protocol=ft_protocol)

    with pytest.raises(ValueError, match="mismatched fields: max_tokens"):
        evaluate_base_vs_ft_gate(base_score=base, ft_score=ft)
