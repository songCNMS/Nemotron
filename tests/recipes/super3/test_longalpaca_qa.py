"""Tests for the LongAlpaca → long_context_qa_smoke env + converter
(task057 Session 2).

Covers:

- `transform_longalpaca_qa` happy path: instruction + long doc + gold
  output → NeMo-Gym record with `long_context_qa_stub` verifier
- Output shape: user message embeds the document context
- M0 smoke cap: rows above `LONGALPACA_MAX_DOC_CHARS` (32K) rejected
  (M2 task028 / task037 will lift this)
- Error surfaces: missing instruction / missing output / missing
  document (this env REQUIRES a long doc context)
- doc_length_chars + doc_token_estimate captured in extra_env_info
- `score_record` dispatches `long_context_qa_stub` verifier; emits
  `contains_match` + `normalized_answer` diagnostics
- Registry integration: env_registry row present; m0_longalpaca data
  row deliberately deferred (no HF SHA pin in sandbox); converter
  wired into CONVERTERS
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    LONGALPACA_MAX_DOC_CHARS,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_longalpaca_qa,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec(dataset_id: str) -> dict:
    """Build a synthetic spec for the long-context env.

    The m0_longalpaca data_registry row is deferred (Session 2.5) — we
    use a synthetic spec matching the shape the converter expects.
    """
    if dataset_id == "m0_longalpaca_qa":
        return {
            "id": "m0_longalpaca_qa",
            "environment": "long_context_qa_smoke",
            "domain": "long_context",
            "hf_dataset": "THUDM/LongAlpaca-12k",
            "hf_config": None,
            "hf_split": "train",
            "hf_val_split": None,
            "hf_revision": "synthetic-test-spec",
            "source_url": "https://huggingface.co/datasets/THUDM/LongAlpaca-12k",
            "license": "apache-2.0",
            "converter": "longalpaca_qa",
            "difficulty": "long_context_qa_smoke",
            "reward_type": "long_context_qa_stub",
            "contamination": "synthetic test spec",
            "contamination_against": ["AA-LCR", "RULER 256K"],
            "milestone": "M0",
            "use_stage": ["M0 data_env_foundation"],
        }
    registry = load_yaml(DATA_REGISTRY_PATH)
    for dataset in registry["datasets"]:
        if dataset["id"] == dataset_id:
            spec = dict(dataset)
            spec["milestone"] = registry["milestone"]
            return spec
    raise AssertionError(f"missing dataset {dataset_id}")


def _row(*, instruction: str, output: str, doc: str | None) -> dict:
    """LongAlpaca-format row: instruction + optional input + output."""
    row: dict[str, Any] = {
        "instruction": instruction,
        "output": output,
    }
    if doc is not None:
        row["input"] = doc
    return row


# ---------- Module surface ----------


def test_system_prompt_for_long_context_qa_smoke_exists() -> None:
    assert "long_context_qa_smoke" in SYSTEM_PROMPTS
    assert "long-context" in SYSTEM_PROMPTS["long_context_qa_smoke"]


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("longalpaca_qa") is transform_longalpaca_qa


def test_max_doc_chars_is_32k_smoke_cap() -> None:
    """Lock the smoke cap so M2 task028 deliberately lifting it is an
    explicit edit, not a silent drift."""
    assert LONGALPACA_MAX_DOC_CHARS == 32_000


# ---------- Happy path ----------


def test_transform_emits_record_for_valid_longalpaca_row() -> None:
    row = _row(
        instruction="What does the document say about quicksort?",
        output="Quicksort uses a pivot to recursively partition.",
        doc="Quicksort is a sorting algorithm that uses a pivot. " * 100,
    )
    record = transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))
    assert record["environment"] == "long_context_qa_smoke"
    assert record["question"] == "What does the document say about quicksort?"
    assert record["expected_answer"].startswith("Quicksort uses a pivot")
    assert record["reward_config"]["verifier"] == "long_context_qa_stub"


def test_transform_embeds_document_in_user_message() -> None:
    """The doc must appear in the user-turn content so the model sees
    it. Question is also present."""
    doc = "DOC_MARKER_FOR_TEST " * 50
    row = _row(
        instruction="What is the marker?",
        output="DOC_MARKER_FOR_TEST",
        doc=doc,
    )
    record = transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))
    user_content = record["responses_create_params"]["input"][1]["content"]
    assert "Document:" in user_content
    assert "Question:" in user_content
    assert "DOC_MARKER_FOR_TEST" in user_content
    assert "What is the marker?" in user_content


def test_transform_captures_doc_length_chars_in_extra_env_info() -> None:
    """Telemetry: extra_env_info.doc_length_chars surfaces the doc size
    so the M0 health baseline can split per-row by doc length."""
    doc = "x" * 5000
    row = _row(instruction="Q?", output="A.", doc=doc)
    record = transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))
    assert record["extra_env_info"]["doc_length_chars"] == 5000
    # Token estimate ~ doc_length // 4
    assert record["extra_env_info"]["doc_token_estimate"] >= 1000


# ---------- M0 smoke cap ----------


def test_transform_rejects_row_exceeding_smoke_cap() -> None:
    """A 100K-char doc is in LongAlpaca's distribution but blows past
    the M0 smoke ceiling. Must be rejected (not silently truncated —
    truncation changes QA answer-span semantics)."""
    row = _row(
        instruction="What is the answer?",
        output="42",
        doc="x" * (LONGALPACA_MAX_DOC_CHARS + 1),
    )
    with pytest.raises(ValueError, match="exceeds M0 smoke cap"):
        transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))


def test_transform_accepts_row_exactly_at_smoke_cap() -> None:
    """Exactly-at-cap rows must pass; the check is strictly >."""
    row = _row(
        instruction="Q",
        output="A",
        doc="x" * LONGALPACA_MAX_DOC_CHARS,
    )
    record = transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))
    assert record["extra_env_info"]["doc_length_chars"] == LONGALPACA_MAX_DOC_CHARS


# ---------- Error surfaces ----------


def test_transform_rejects_missing_instruction() -> None:
    row = _row(instruction="", output="A", doc="some doc")
    with pytest.raises(ValueError, match="instruction"):
        transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))


def test_transform_rejects_missing_output() -> None:
    row = _row(instruction="Q?", output="", doc="some doc")
    with pytest.raises(ValueError, match="output"):
        transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))


def test_transform_rejects_row_without_document() -> None:
    """This env REQUIRES a long doc context — question-only Alpaca
    rows don't belong in long-context QA."""
    row = _row(instruction="Q?", output="A", doc=None)
    with pytest.raises(ValueError, match="input"):
        transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))


def test_transform_rejects_empty_document() -> None:
    row = _row(instruction="Q?", output="A", doc="   ")
    with pytest.raises(ValueError, match="input"):
        transform_longalpaca_qa(row, _spec("m0_longalpaca_qa"))


# ---------- score_record dispatch ----------


def test_score_record_dispatches_long_context_qa_stub_verifier() -> None:
    record = {
        "environment": "long_context_qa_smoke",
        "expected_answer": "the marker is here",
        "reward_config": {"verifier": "long_context_qa_stub"},
        "extra_env_info": {"doc_length_chars": 5000},
    }
    # Oracle: candidate contains the gold answer → score 1.0
    score, diagnostics = score_record("Yes, the marker is here.", record)
    assert score == 1.0
    assert diagnostics["contains_match"] is True
    assert "normalized_answer" in diagnostics


def test_score_record_long_context_qa_stub_no_match() -> None:
    record = {
        "environment": "long_context_qa_smoke",
        "expected_answer": "specific gold answer",
        "reward_config": {"verifier": "long_context_qa_stub"},
        "extra_env_info": {"doc_length_chars": 5000},
    }
    score, diagnostics = score_record("Unrelated response.", record)
    assert score == 0.0
    assert diagnostics["contains_match"] is False


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_long_context_qa_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_env_registry_carries_new_long_context_qa_smoke_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "long_context_qa_smoke"),
        None,
    )
    assert env is not None
    assert env["family"] == "long_context"
    assert env["reward"]["verifier"] == "long_context_qa_stub"
    assert env["resources"]["sandbox"] == "none"
    # Required fields include doc_length_chars (telemetry contract)
    required = env["health_check"]["required_fields"]
    assert any("doc_length_chars" in r for r in required)


def test_data_registry_does_not_yet_carry_m0_longalpaca_qa_row() -> None:
    """task057 Session 2 defers the data_registry row to a follow-up
    once a real LongAlpaca commit SHA is verified against the live HF
    source. Lock the deferral so a future PR can't accidentally re-add
    it without a real pin (would trigger the revision-pin audit
    blocker)."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    rows = [d for d in data_registry["datasets"] if d["id"] == "m0_longalpaca_qa"]
    assert rows == [], (
        "m0_longalpaca_qa row should NOT be in data_registry yet — pin a "
        "real LongAlpaca commit SHA first, then add the row in a follow-up"
    )
