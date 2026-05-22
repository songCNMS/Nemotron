"""Tests for task027 Session 1 multilingual IF/code scaffold."""

from __future__ import annotations

from typing import Any

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_multilingual_humaneval,
    transform_multilingual_ifeval,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec(env: str) -> dict[str, Any]:
    return {
        "id": f"synthetic_{env}",
        "environment": env,
        "domain": "multilingual",
        "hf_dataset": f"synthetic/{env}",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": None,
        "hf_revision": "synthetic-test-spec",
        "source_url": f"https://example.invalid/{env}",
        "license": "placeholder-pending-source-selection",
        "converter": env,
        "difficulty": "m2_multilingual_scaffold",
        "reward_type": "multilingual_exact_or_contains",
        "contamination": "synthetic test spec only; pin source before adding data_registry row",
        "contamination_against": ["MMLU-ProX", "WMT24++", "HumanEval"],
        "milestone": "M0",
        "use_stage": ["M2 multilingual IF/code scaffold"],
    }


def test_multilingual_if_code_prompts_and_converters_are_registered() -> None:
    assert "multilingual_ifeval" in SYSTEM_PROMPTS
    assert "multilingual_humaneval" in SYSTEM_PROMPTS
    assert CONVERTERS.get("multilingual_ifeval") is transform_multilingual_ifeval
    assert CONVERTERS.get("multilingual_humaneval") is transform_multilingual_humaneval


def test_transform_multilingual_ifeval_emits_sandbox_judge_deferred_record() -> None:
    row = {
        "id": "if-ja-1",
        "prompt": "箇条書きで二つの利点を答えてください。",
        "reference_answer": "利点: 速度と安全性。",
        "language": "Japanese",
        "language_code": "ja",
        "constraints": ["two bullet points", "same language"],
    }
    record = transform_multilingual_ifeval(row, _spec("multilingual_ifeval"))

    assert record["environment"] == "multilingual_ifeval"
    assert record["question"] == row["prompt"]
    assert record["expected_answer"] == row["reference_answer"]
    assert record["reward_config"]["verifier"] == "multilingual_exact_or_contains"
    assert record["reward_config"]["judge_model"] == "deferred"
    assert record["extra_env_info"]["language_code"] == "ja"
    assert record["extra_env_info"]["judge_model"]["status"] == "deferred_to_task027_followup"
    assert "Constraints:" in record["responses_create_params"]["input"][1]["content"]


def test_transform_multilingual_ifeval_accepts_alias_columns() -> None:
    row = {
        "instruction": "Responde en español con una frase.",
        "target": "Una frase corta.",
        "locale": "es",
    }
    record = transform_multilingual_ifeval(row, _spec("multilingual_ifeval"))
    assert record["question"] == row["instruction"]
    assert record["expected_answer"] == row["target"]
    assert record["extra_env_info"]["language_code"] == "es"


def test_multilingual_ifeval_reuses_multilingual_exact_or_contains_verifier() -> None:
    record = transform_multilingual_ifeval(
        {
            "prompt": "Antwort auf Deutsch.",
            "answer": "große Straße",
            "language_code": "de",
        },
        _spec("multilingual_ifeval"),
    )
    score, diagnostics = score_record("Die Antwort ist GROSSE STRAßE.", record)
    assert score == 1.0
    assert diagnostics["contains_match"] is True


def test_transform_multilingual_ifeval_rejects_missing_required_fields() -> None:
    try:
        transform_multilingual_ifeval({"answer": "x", "language_code": "fr"}, _spec("multilingual_ifeval"))
    except ValueError as exc:
        assert "prompt" in str(exc)
    else:
        raise AssertionError("missing prompt should raise")

    try:
        transform_multilingual_ifeval({"prompt": "x", "language_code": "fr"}, _spec("multilingual_ifeval"))
    except ValueError as exc:
        assert "reference answer" in str(exc)
    else:
        raise AssertionError("missing reference answer should raise")

    try:
        transform_multilingual_ifeval({"prompt": "x", "answer": "y"}, _spec("multilingual_ifeval"))
    except ValueError as exc:
        assert "language" in str(exc)
    else:
        raise AssertionError("missing language should raise")


def test_transform_multilingual_humaneval_emits_runtime_deferred_record() -> None:
    row = {
        "task_id": "humaneval-es-1",
        "prompt": "Escribe una función add(a, b) que devuelva la suma.",
        "canonical_solution": "def add(a, b):\n    return a + b",
        "language": "Spanish",
        "language_code": "es",
        "tests": ["assert add(2, 3) == 5"],
    }
    record = transform_multilingual_humaneval(row, _spec("multilingual_humaneval"))

    assert record["environment"] == "multilingual_humaneval"
    assert record["question"] == row["prompt"]
    assert record["expected_answer"] == row["canonical_solution"]
    assert record["reward_config"]["verifier"] == "multilingual_exact_or_contains"
    assert record["reward_config"]["code_execution"] == "deferred"
    assert record["extra_env_info"]["unit_tests"] == ["assert add(2, 3) == 5"]
    assert record["extra_env_info"]["code_execution"]["status"] == "deferred_to_task027_followup"


def test_multilingual_humaneval_sandbox_fallback_scores_reference_solution() -> None:
    record = transform_multilingual_humaneval(
        {
            "question": "Écris une fonction carre(x).",
            "solution": "def carre(x):\n    return x * x",
            "language_code": "fr",
        },
        _spec("multilingual_humaneval"),
    )
    score, diagnostics = score_record(
        "Solution:\ndef carre(x):\n    return x * x",
        record,
    )
    assert score == 1.0
    assert diagnostics["contains_match"] is True


def test_transform_multilingual_humaneval_rejects_missing_required_fields() -> None:
    try:
        transform_multilingual_humaneval(
            {"canonical_solution": "pass", "language_code": "fr"},
            _spec("multilingual_humaneval"),
        )
    except ValueError as exc:
        assert "prompt" in str(exc)
    else:
        raise AssertionError("missing prompt should raise")

    try:
        transform_multilingual_humaneval(
            {"prompt": "x", "language_code": "fr"},
            _spec("multilingual_humaneval"),
        )
    except ValueError as exc:
        assert "reference solution" in str(exc)
    else:
        raise AssertionError("missing solution should raise")

    try:
        transform_multilingual_humaneval(
            {"prompt": "x", "canonical_solution": "pass"},
            _spec("multilingual_humaneval"),
        )
    except ValueError as exc:
        assert "language" in str(exc)
    else:
        raise AssertionError("missing language should raise")


def test_registry_consistency_holds_with_multilingual_if_code_env_rows() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_environment_registry_carries_multilingual_if_code_scaffold_rows() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    by_id = {env["id"]: env for env in env_registry["environments"]}

    assert {"multilingual_ifeval", "multilingual_humaneval"} <= set(by_id)
    assert by_id["multilingual_ifeval"]["reward"]["verifier"] == "multilingual_exact_or_contains"
    assert by_id["multilingual_ifeval"]["resources"]["sandbox"] == "judge_model_cluster_deferred"
    assert "extra_env_info.judge_model" in by_id["multilingual_ifeval"]["health_check"]["required_fields"]
    assert by_id["multilingual_humaneval"]["reward"]["verifier"] == "multilingual_exact_or_contains"
    assert by_id["multilingual_humaneval"]["resources"]["sandbox"] == "code_execution_cluster_deferred"
    assert "extra_env_info.code_execution" in by_id["multilingual_humaneval"]["health_check"]["required_fields"]


def test_data_registry_defers_task027_rows_until_source_and_runtime_pins() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    ids = {dataset["id"] for dataset in data_registry["datasets"]}

    assert "m0_multilingual_ifeval" not in ids
    assert "m0_multilingual_humaneval" not in ids
