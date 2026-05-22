"""Tests for task028 Session 1 long-context scaffold.

Session 1 is sandbox-only: source-agnostic RULER / AA-LCR / long-doc QA
record contracts, env-registry rows, and a small span-aware verifier.
Full 512K / 1M execution and benchmark source pins are cluster follow-ups.
"""

from __future__ import annotations

from typing import Any

import pytest

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    M2_LONG_CONTEXT_SCAFFOLD_MAX_DOC_CHARS,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_long_context_m2_qa,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec(env: str) -> dict[str, Any]:
    return {
        "id": f"m0_{env}",
        "environment": env,
        "domain": "long_context",
        "hf_dataset": f"synthetic/{env}",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": None,
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://example.invalid/long-context-placeholder",
        "license": "placeholder-pending-source-pin",
        "converter": "long_context_m2_qa",
        "difficulty": "long_context_m2_scaffold",
        "reward_type": "long_context_qa",
        "contamination": "synthetic test spec; source pin deferred",
        "contamination_against": ["RULER", "AA-LCR", "LongBench"],
        "milestone": "M0",
        "use_stage": ["M2 long-context expansion"],
        "target_context_tokens": 512_000,
    }


def _row() -> dict[str, Any]:
    return {
        "id": "lc-1",
        "question": "What is the codename?",
        "answer": "Aurora",
        "document": (
            "The meeting started with unrelated budget notes. "
            "In section nine, the project codename Aurora was approved "
            "after the risk review."
        ),
        "evidence_spans": [
            "the project codename Aurora was approved after the risk review"
        ],
        "target_context_tokens": 512_000,
    }


def test_long_context_m2_prompts_and_converter_are_registered() -> None:
    assert "long_context_ruler" in SYSTEM_PROMPTS
    assert "long_context_aalcr" in SYSTEM_PROMPTS
    assert "long_context_doc_qa" in SYSTEM_PROMPTS
    assert CONVERTERS.get("long_context_m2_qa") is transform_long_context_m2_qa


def test_transform_long_context_m2_emits_span_aware_record() -> None:
    record = transform_long_context_m2_qa(_row(), _spec("long_context_ruler"))

    assert record["environment"] == "long_context_ruler"
    assert record["expected_answer"] == "Aurora"
    assert record["reward_config"]["verifier"] == "long_context_qa"
    assert record["reward_config"]["requires_evidence_span"] is True
    assert record["extra_env_info"]["doc_length_chars"] == len(_row()["document"])
    assert record["extra_env_info"]["doc_token_estimate"] > 10
    assert record["extra_env_info"]["target_context_tokens"] == 512_000
    assert record["extra_env_info"]["cluster_execution"] == "deferred_to_task028_session_3"
    assert "Document:" in record["responses_create_params"]["input"][1]["content"]


def test_transform_long_context_m2_accepts_alias_fields_and_infers_span() -> None:
    row = {
        "query": "Which color is the vault door?",
        "answers": ["blue"],
        "context": "A long report says the vault door is blue near the end.",
    }
    record = transform_long_context_m2_qa(row, _spec("long_context_aalcr"))

    assert record["environment"] == "long_context_aalcr"
    assert record["question"] == "Which color is the vault door?"
    assert record["expected_answer"] == "blue"
    assert record["extra_env_info"]["evidence_spans"] == [
        "A long report says the vault door is blue near the end."
    ]


def test_transform_long_context_m2_inferred_span_preserves_non_ascii_indices() -> None:
    """Lock in correct span inference under non-ASCII length expansion.

    The implementation previously used `casefold()` for the answer index
    lookup, but `casefold()` can change string length (German `ß` → `ss`,
    Greek `ς` → `σ` only same length but `ϐ` → `β` same too — sharp s is
    the canonical expander). When the document contains a length-changing
    character BEFORE the matched answer, the casefolded `match_index`
    diverges from the original-document index by the cumulative expansion
    width, and any subsequent slice of the ORIGINAL document with that
    index can land off-by-N. The fix searches the original document with
    `re.IGNORECASE` so `match.start()` is in original-document coordinates.
    """
    row = {
        "question": "Wo liegt die Straße?",
        "answer": "Straße",
        "document": (
            "Größe spielt keine Rolle. "  # earlier `ß` expands casefolded form
            "Die Straße liegt im Norden. "
            "Weitere Notizen folgen."
        ),
    }
    record = transform_long_context_m2_qa(row, _spec("long_context_doc_qa"))
    spans = record["extra_env_info"]["evidence_spans"]
    assert len(spans) == 1
    # The inferred span must be the SENTENCE that contains the answer,
    # not a slice that drifted past it due to casefold-induced length
    # expansion in the document before the match site.
    assert spans[0] == "Die Straße liegt im Norden."


def test_transform_long_context_m2_rejects_missing_fields_or_over_cap() -> None:
    with pytest.raises(ValueError, match="question"):
        transform_long_context_m2_qa({"answer": "A", "document": "doc"}, _spec("long_context_doc_qa"))

    with pytest.raises(ValueError, match="answer"):
        transform_long_context_m2_qa({"question": "Q", "document": "doc"}, _spec("long_context_doc_qa"))

    with pytest.raises(ValueError, match="document"):
        transform_long_context_m2_qa({"question": "Q", "answer": "A"}, _spec("long_context_doc_qa"))

    with pytest.raises(ValueError, match="sandbox cap"):
        transform_long_context_m2_qa(
            {
                "question": "Q",
                "answer": "A",
                "document": "x" * (M2_LONG_CONTEXT_SCAFFOLD_MAX_DOC_CHARS + 1),
            },
            _spec("long_context_doc_qa"),
        )


def test_long_context_qa_verifier_requires_answer_and_span_when_configured() -> None:
    record = transform_long_context_m2_qa(_row(), _spec("long_context_ruler"))

    good = "Answer: Aurora. Evidence: the project codename Aurora was approved after the risk review."
    score_ok, diagnostics_ok = score_record(good, record)
    assert score_ok == 1.0
    assert diagnostics_ok["answer_match"] is True
    assert diagnostics_ok["evidence_span_match"] is True
    assert diagnostics_ok["requires_evidence_span"] is True

    score_no_span, diagnostics_no_span = score_record("The answer is Aurora.", record)
    assert score_no_span == 0.0
    assert diagnostics_no_span["answer_match"] is True
    assert diagnostics_no_span["evidence_span_match"] is False

    score_wrong, diagnostics_wrong = score_record("The answer is Borealis.", record)
    assert score_wrong == 0.0
    assert diagnostics_wrong["answer_match"] is False


def test_registry_consistency_holds_with_long_context_m2_env_rows() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_environment_registry_carries_long_context_m2_rows() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    by_id = {env["id"]: env for env in env_registry["environments"]}

    assert {"long_context_ruler", "long_context_aalcr", "long_context_doc_qa"} <= set(by_id)
    for env_id in ("long_context_ruler", "long_context_aalcr", "long_context_doc_qa"):
        env = by_id[env_id]
        assert env["family"] == "long_context"
        assert env["reward"]["verifier"] == "long_context_qa"
        assert env["resources"]["sandbox"] == "none"
        assert "evidence_span_match" in env["telemetry"]


def test_data_registry_defers_long_context_m2_rows_until_source_pins() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    ids = {dataset["id"] for dataset in data_registry["datasets"]}

    assert "m0_long_context_ruler" not in ids
    assert "m0_long_context_aalcr" not in ids
    assert "m0_long_context_doc_qa" not in ids
