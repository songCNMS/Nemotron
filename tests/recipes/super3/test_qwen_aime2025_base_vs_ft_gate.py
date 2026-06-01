"""Tests for the task243 Qwen AIME2025 base-vs-FT gate."""

from __future__ import annotations

from copy import deepcopy

import pytest

yaml = pytest.importorskip("yaml")

from nemotron.recipes.super3.milestones.m1_eval_basket.qwen_aime2025_base_vs_ft_gate import (  # noqa: E402
    QWEN_AIME2025_BASE_VS_FT_GATE_PATH,
    QWEN_V11_EXPORT_LOAD_CANARY_PROMPTS_PATH,
    evaluate_base_vs_ft_gate,
    evaluate_v11_base_vs_ft_gate,
    evaluate_v11_export_load_canary,
    format_base_vs_ft_report,
    load_base_vs_ft_gate_config,
    load_v11_canary_prompt_set,
    normalize_aime2025_rows,
    validate_base_vs_ft_gate_config,
    validate_v11_artifact_retention_schema,
    validate_v11_canary_prompt_set,
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
    assert gate["v11_pre_aime_export_load_canary"]["required_before_aime_comparison"]
    assert gate["v11_artifact_retention_schema"]["required_for_aime_comparison"]


def test_task243_gate_rejects_completions_route_and_thinking_drift() -> None:
    data = _gate_data()
    data["protocols"]["pilot_smoke"]["route"] = "/v1/completions"
    data["protocols"]["pilot_smoke"]["chat_template_kwargs"]["enable_thinking"] = True

    issues = validate_base_vs_ft_gate_config(data)

    assert any("route must be /v1/chat/completions" in issue for issue in issues)
    assert any("enable_thinking must be False" in issue for issue in issues)


def test_task264_v11_canary_prompt_set_loads_and_is_non_aime() -> None:
    prompt_set = load_v11_canary_prompt_set()

    assert validate_v11_canary_prompt_set(prompt_set) == []
    assert prompt_set["prompt_set_id"] == "qwen_v11_non_aime_export_load_canary_v1"
    assert prompt_set["non_aime_non_train_confirmation"] == {
        "synthetic_prompts_only": True,
        "excludes_aime2025": True,
        "excludes_training_rows": True,
        "review_only_not_trainable": True,
        "no_aime2025_prompt_or_label_text": True,
    }
    assert len(prompt_set["prompts"]) >= 5
    prompt_texts = "\n".join(prompt["prompt"] for prompt in prompt_set["prompts"])
    assert "aime" not in prompt_texts.lower()
    assert QWEN_V11_EXPORT_LOAD_CANARY_PROMPTS_PATH.name.endswith(".yaml")


def test_task264_gate_rejects_missing_full_completion_retention() -> None:
    gate = _gate_data()
    schema = gate["v11_artifact_retention_schema"]
    schema["required_files"].remove("full_completions.jsonl")
    schema["results_jsonl_required_fields"].remove("response_text_sha256")

    issues = validate_v11_artifact_retention_schema(schema)

    assert any("full_completions.jsonl" in issue for issue in issues)
    assert any("response_text_sha256" in issue for issue in issues)


def _passing_canary_rows() -> list[dict]:
    prompt_set = load_v11_canary_prompt_set()
    rows = []
    for prompt in prompt_set["prompts"]:
        answer = prompt["expected_answer"]
        rows.append(
            {
                "prompt_id": prompt["id"],
                "status": "ok",
                "response_text": f"The canary response is coherent. Final Answer: \\boxed{{{answer}}}",
                "usage": {"completion_tokens": 24},
                "finish_reason": "stop",
            }
        )
    return rows


def test_task264_export_load_canary_passes_clean_synthetic_rows() -> None:
    decision = evaluate_v11_export_load_canary(_passing_canary_rows())

    assert decision.passed is True
    assert decision.status == "pass"
    assert decision.failed_prompt_ids == ()
    assert decision.missing_prompt_ids == ()
    assert decision.diagnostics["denominator_policy"] == "all_canary_prompts"


def test_task264_export_load_canary_fails_corrupted_or_missing_rows() -> None:
    rows = _passing_canary_rows()
    rows.pop()
    rows[0]["response_text"] = (
        "HaveBeenCalledWith HTMLElement SharedPreferences "
        "Final Answer: \\boxed{wrong}"
    )

    decision = evaluate_v11_export_load_canary(rows)

    assert decision.passed is False
    assert decision.status == "fail"
    assert decision.missing_prompt_ids
    assert rows[0]["prompt_id"] in decision.failed_prompt_ids
    assert any("mixed-script/code-token" in reason for reason in decision.reasons)


def test_task264_v11_gate_blocks_without_passed_canary() -> None:
    base = _score(correct=3, total=4, parsed=3)
    ft = _score(correct=4, total=4, parsed=4)

    missing = evaluate_v11_base_vs_ft_gate(
        base_score=base,
        ft_score=ft,
        canary_decision=None,
    )
    failed = evaluate_v11_base_vs_ft_gate(
        base_score=base,
        ft_score=ft,
        canary_decision=evaluate_v11_export_load_canary(_passing_canary_rows()[:-1]),
    )

    assert missing.status == "blocked_missing_export_load_canary"
    assert missing.diagnostics["ft_judged"] is False
    assert failed.status == "blocked_failed_export_load_canary"
    assert failed.diagnostics["ft_judged"] is False


def test_task264_v11_gate_allows_same_harness_decision_after_canary_passes() -> None:
    base = _score(correct=3, total=4, parsed=3)
    ft = _score(correct=4, total=4, parsed=4)

    decision = evaluate_v11_base_vs_ft_gate(
        base_score=base,
        ft_score=ft,
        canary_decision=evaluate_v11_export_load_canary(_passing_canary_rows()),
    )

    assert decision.status == "pass_ft_at_least_base"
    assert decision.diagnostics["canary_required"] is True
    assert decision.diagnostics["canary"]["passed"] is True


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
