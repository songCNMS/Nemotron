from pathlib import Path

from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (
    MISSING,
    evaluate_policy,
    get_path,
    normalize_numeric_candidate,
    normalize_text_answer,
    run_python_unit_tests,
    score_record,
    summarize_health,
)


def test_get_path_handles_missing_nested_fields() -> None:
    record = {"a": {"b": 1}}

    assert get_path(record, "a.b") == 1
    assert get_path(record, "a.c") is MISSING


def test_text_and_numeric_verifiers_score_normalized_answers() -> None:
    text_record = {
        "expected_answer": "The Eiffel Tower",
        "reward_config": {"verifier": "normalized_exact_or_contains"},
    }
    numeric_record = {
        "expected_answer": "1234",
        "reward_config": {"verifier": "normalized_numeric_exact_match"},
    }

    assert normalize_text_answer("An Eiffel tower!") == "eiffel tower"
    assert normalize_numeric_candidate("Final answer: 1,234") == "1234"
    assert score_record("It is the Eiffel Tower.", text_record)[0] == 1.0
    assert score_record("Final answer: 1,234", numeric_record)[0] == 1.0


def test_tool_call_verifier_matches_name_and_arguments() -> None:
    record = {
        "expected_answer": [{"type": "function", "function": {"name": "lookup", "arguments": {"query": "x"}}}],
        "reward_config": {"verifier": "tool_schema_and_argument_match"},
        "extra_env_info": {"expected_tool_calls": []},
    }

    score, _ = score_record(
        [{"type": "function", "function": {"name": "lookup", "arguments": {"query": "x"}}}],
        record,
    )

    assert score == 1.0
    assert score_record([{"type": "function", "function": {"name": "lookup", "arguments": {"query": "y"}}}], record)[0] == 0.0


def test_python_unit_test_verifier_runs_reference_code() -> None:
    record = {
        "expected_answer": "def square(x):\n    return x * x",
        "reward_config": {"verifier": "python_unit_tests", "timeout_s": 5},
        "extra_env_info": {"test_imports": [], "test_list": ["assert square(4) == 16"]},
    }

    score, detail = run_python_unit_tests(record["expected_answer"], record, timeout_s=5)

    assert score == 1.0
    assert detail["returncode"] == 0


def test_policy_metrics_compute_pass_at_1_and_best_at_k() -> None:
    rows = [
        {"expected_answer": "42", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
        {"expected_answer": "7", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
    ]

    oracle = evaluate_policy(rows, policy="oracle", best_k=2, run_code=False)
    empty = evaluate_policy(rows, policy="empty", best_k=2, run_code=False)

    assert oracle["pass_at_1"] == 1.0
    assert oracle["best_at_2"] == 1.0
    assert empty["pass_at_1"] == 0.0
    assert empty["failure_count"] == 2


def test_health_summary_checks_required_fields_and_min_rows(tmp_path: Path) -> None:
    del tmp_path
    rows_by_env = {
        "math_reasoning_numeric": {
            "train": [
                {
                    "environment": "math_reasoning_numeric",
                    "milestone": "M0",
                    "use_stage": ["M0 data_env_foundation"],
                    "question": "1+1?",
                    "expected_answer": "2",
                    "responses_create_params": {"input": [{"role": "user", "content": "1+1?"}]},
                    "reward_config": {"verifier": "normalized_numeric_exact_match"},
                    "metadata": {"source_dataset": "x", "license": "mit", "data_stage": "M0"},
                }
            ]
        }
    }
    env_specs = {
        "math_reasoning_numeric": {
            "health_check": {
                "min_rows_per_split": 1,
                "required_fields": ["question", "expected_answer", "responses_create_params.input"],
            }
        }
    }

    summary = summarize_health(rows_by_env, env_specs)

    assert summary["environments"]["math_reasoning_numeric"]["status"] == "pass"
