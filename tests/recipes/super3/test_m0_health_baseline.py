from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m0_data_env import run_m0_health_baseline
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (
    MISSING,
    aggregate_scored_rows,
    build_report,
    evaluate_policy,
    get_path,
    normalize_numeric_candidate,
    normalize_text_answer,
    overall_status,
    run_python_unit_tests,
    score_command,
    score_json_value,
    score_negative_recognition,
    score_patch,
    score_record,
    score_rows,
    score_text,
    score_tool_call,
    summarize_baselines,
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


def test_json_value_verifier_matches_parsed_json_exactly() -> None:
    record = {
        "expected_answer": "{\"city\":\"Paris\",\"population\":2148000}",
        "reward_config": {"verifier": "json_value_exact_match"},
    }

    assert score_json_value('{"city": "Paris", "population": 2148000}', record["expected_answer"]) == 1.0
    assert score_record({"city": "Paris", "population": 2148000}, record)[0] == 1.0
    assert score_record('{"city": "Paris"}', record)[0] == 0.0
    assert score_record("The answer is {\"city\":\"Paris\",\"population\":2148000}", record)[0] == 0.0


def test_command_substring_verifier_matches_fenced_or_plain_command() -> None:
    record = {
        "expected_answer": "mv ~/Desktop/x ~/Downloads/",
        "reward_config": {"verifier": "command_substring_match"},
    }

    assert score_command("```bash\nmv ~/Desktop/x ~/Downloads/\n```", record["expected_answer"]) == 1.0
    assert score_record("Run: mv ~/Desktop/x ~/Downloads/", record)[0] == 1.0
    assert score_record("cp ~/Desktop/x ~/Downloads/", record)[0] == 0.0


def test_patch_diff_verifier_matches_normalized_patch() -> None:
    patch = "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n-old\n+new\n"
    record = {
        "expected_answer": patch,
        "reward_config": {"verifier": "patch_diff_match"},
    }

    assert score_patch(patch.rstrip(), patch) == 1.0
    assert score_record(patch, record)[0] == 1.0
    assert score_record(patch.replace("+new", "+other"), record)[0] == 0.0


def test_negative_recognition_verifier_matches_repair_target_tool_calls() -> None:
    tool_calls = [{"type": "function", "function": {"name": "lookup", "arguments": {"query": "x"}}}]
    record = {
        "expected_answer": {"repair_message": "fixed", "tool_calls": tool_calls},
        "extra_env_info": {"repair_target": tool_calls},
        "reward_config": {"verifier": "negative_recognition"},
    }

    assert score_negative_recognition({"tool_calls": tool_calls}, record["expected_answer"], record) == 1.0
    assert score_record({"tool_calls": tool_calls}, record)[0] == 1.0
    assert score_record({"tool_calls": [{"type": "function", "function": {"name": "lookup", "arguments": {"query": "y"}}}]}, record)[0] == 0.0


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


def test_resolve_min_rows_caps_floor_to_requested_count() -> None:
    """Regression for review finding S6: small smoke runs must not auto-fail."""
    from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import resolve_min_rows

    assert resolve_min_rows(25, split="train", requested_rows=None) == 25
    assert resolve_min_rows(25, split="train", requested_rows={"max_train_per_dataset": 10}) == 10
    assert resolve_min_rows(25, split="val", requested_rows={"max_val_per_dataset": 5}) == 5
    # Requesting more than the spec floor doesn't raise the gate above the spec.
    assert resolve_min_rows(25, split="train", requested_rows={"max_train_per_dataset": 100}) == 25
    # Bad / unset values fall back to the spec floor.
    assert resolve_min_rows(25, split="train", requested_rows={"max_train_per_dataset": None}) == 25
    assert resolve_min_rows(25, split="train", requested_rows={"max_train_per_dataset": 0}) == 25


def test_summarize_health_honors_requested_rows() -> None:
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
                "min_rows_per_split": 25,
                "required_fields": ["question", "expected_answer", "responses_create_params.input"],
            }
        }
    }

    # Without prep manifest hints the floor is the env spec → 1 row fails.
    strict = summarize_health(rows_by_env, env_specs)
    assert strict["environments"]["math_reasoning_numeric"]["splits"]["train"]["status"] == "fail"

    # With a small requested count the floor moves down → 1 row passes.
    relaxed = summarize_health(
        rows_by_env, env_specs, requested_rows={"max_train_per_dataset": 1}
    )
    split = relaxed["environments"]["math_reasoning_numeric"]["splits"]["train"]
    assert split["status"] == "pass"
    assert split["min_rows"] == 1
    assert split["spec_min_rows"] == 25


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


def test_score_text_rejects_empty_expected() -> None:
    """Regression for review finding #1: empty expected used to score 1.0."""
    assert score_text("", "") == 0.0
    assert score_text("anything", "") == 0.0


def test_score_tool_call_rejects_empty_expected_and_empty_content() -> None:
    record = {"extra_env_info": {"expected_assistant_content": ""}}

    assert score_tool_call([], [], record) == 0.0


def test_score_record_marks_python_unit_tests_as_skipped_when_run_code_disabled() -> None:
    record = {
        "expected_answer": "def square(x):\n    return x * x",
        "reward_config": {"verifier": "python_unit_tests"},
        "extra_env_info": {"test_imports": [], "test_list": ["assert square(2) == 4"]},
    }

    score, detail = score_record(record["expected_answer"], record, run_code=False)

    assert score is None
    assert "skipped" in detail


def test_evaluate_policy_counts_skipped_rows_separately() -> None:
    """Regression for review finding #2: --skip-code-execution must not look like failure."""
    rows = [
        {
            "expected_answer": "def f():\n    return 1",
            "reward_config": {"verifier": "python_unit_tests"},
            "extra_env_info": {"test_imports": [], "test_list": ["assert f() == 1"]},
        }
    ]

    skipped = evaluate_policy(rows, policy="oracle", best_k=1, run_code=False)

    assert skipped["skipped_rows"] == 1
    assert skipped["scored_rows"] == 0
    assert skipped["failure_count"] == 0
    assert skipped["pass_at_1"] == 0.0


def test_overall_status_fails_when_no_environments_discovered() -> None:
    """Regression for review finding #3: empty input dir used to silently return pass."""
    status = overall_status({"environments": {}, "unknown_environments": []}, {"environments": {}})
    assert status == "fail"


def test_overall_status_fails_when_oracle_all_skipped() -> None:
    """Skipping all oracle candidates must not implicitly pass the gate."""
    health = {
        "environments": {
            "code_execution_python": {"status": "pass", "splits": {}}
        },
        "unknown_environments": [],
    }
    baselines = {
        "environments": {
            "code_execution_python": {
                "aggregate": {
                    "oracle": {"rows": 5, "scored_rows": 0, "skipped_rows": 5, "pass_at_1": 0.0},
                }
            }
        }
    }
    assert overall_status(health, baselines) == "fail"


def test_build_report_raises_for_missing_input_dir(tmp_path: Path) -> None:
    """Regression for review finding #3."""
    missing = tmp_path / "does-not-exist"
    args = type(
        "Args",
        (),
        {
            "input_dir": missing,
            "environment_registry": Path(
                "src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml"
            ),
            "policy": None,
            "best_k": 2,
            "skip_code_execution": False,
        },
    )()

    with pytest.raises(FileNotFoundError):
        build_report(args)


def test_summarize_baselines_does_not_rescore_for_aggregate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression for review finding #15: aggregate used to re-run the verifier per row."""
    rows_by_env = {
        "math_reasoning_numeric": {
            "train": [
                {"expected_answer": "1", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
                {"expected_answer": "2", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
            ],
            "val": [
                {"expected_answer": "3", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
            ],
        }
    }
    calls = {"count": 0}
    original_score_record = run_m0_health_baseline.score_record

    def counting_score_record(*args, **kwargs):
        calls["count"] += 1
        return original_score_record(*args, **kwargs)

    monkeypatch.setattr(run_m0_health_baseline, "score_record", counting_score_record)

    summary = summarize_baselines(
        rows_by_env,
        policies=["oracle"],
        best_k=1,
        run_code=False,
    )

    # oracle policy has 1 candidate; total rows = 3; aggregate must reuse split scores.
    assert calls["count"] == 3

    env = summary["environments"]["math_reasoning_numeric"]
    assert env["splits"]["train"]["oracle"]["scored_rows"] == 2
    assert env["splits"]["val"]["oracle"]["scored_rows"] == 1
    assert env["aggregate"]["oracle"]["scored_rows"] == 3
    assert env["aggregate"]["oracle"]["pass_at_1"] == 1.0


def test_score_rows_and_aggregate_match_evaluate_policy() -> None:
    """evaluate_policy keeps working as a thin wrapper after the refactor."""
    rows = [
        {"expected_answer": "42", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
        {"expected_answer": "7", "reward_config": {"verifier": "normalized_numeric_exact_match"}},
    ]

    scored = score_rows(rows, policy="oracle", best_k=2, run_code=False)
    aggregated = aggregate_scored_rows(scored, policy="oracle", best_k=2)
    direct = evaluate_policy(rows, policy="oracle", best_k=2, run_code=False)

    assert aggregated == direct
