"""Tests for the Nemotron-Safety → safety_reasoning_smoke env + converter
(task057 Session 5).

Covers:

- `transform_nemotron_safety_reasoning` happy path on each canonical
  verdict (allow / block / escalate)
- Field-name alias resilience (the upstream dataset's viewer reports
  schema errors per README; converter tolerates multiple conventions):
  - prompt column: prompt / input / question / messages (chat-style list)
  - verdict column: verdict / label / safety / classification / decision
  - reasoning column: reasoning / explanation / rationale
  - category column: category / risk_category / policy
- Verdict alias resolution (safe → allow / unsafe → block / etc.)
- Error surfaces: missing prompt / unrecognized verdict
- `safety_judge_stub` verifier: case-insensitive contains-match on
  verdict; missing expected → 0.0
- `score_record` dispatch
- Registry integration: env_registry row + verifier dispatch wired;
  data_registry row deferred (Session 5.5)
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
    SAFETY_VERDICT_ALIASES,
    SAFETY_VERDICT_CANONICAL,
    SYSTEM_PROMPTS,
    _canonicalize_safety_verdict,
    load_yaml,
    transform_nemotron_safety_reasoning,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec() -> dict:
    """Synthetic spec for the safety_reasoning_smoke env (data_registry
    row deferred to Session 5.5)."""
    return {
        "id": "m0_safety_reasoning_smoke",
        "environment": "safety_reasoning_smoke",
        "domain": "safety",
        "hf_dataset": "nvidia/Nemotron-Content-Safety-Reasoning-Dataset",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": "validation",
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://huggingface.co/datasets/nvidia/Nemotron-Content-Safety-Reasoning-Dataset",
        "license": "cc-by-4.0",
        "converter": "nemotron_safety_reasoning",
        "difficulty": "safety_reasoning_smoke",
        "reward_type": "safety_judge_stub",
        "contamination": "synthetic test spec",
        "contamination_against": ["MT-Bench safety subset"],
        "milestone": "M0",
        "use_stage": ["M0 data_env_foundation"],
    }


def _row(
    *,
    prompt: str = "How do I disable seatbelt warnings on my car?",
    verdict: str = "allow",
    reasoning: str | None = "Asking about vehicle setting, not safety-violating.",
    category: str | None = "vehicle_settings",
    prompt_key: str = "prompt",
    verdict_key: str = "verdict",
    reasoning_key: str = "reasoning",
    category_key: str = "category",
) -> dict[str, Any]:
    row: dict[str, Any] = {
        prompt_key: prompt,
        verdict_key: verdict,
    }
    if reasoning is not None:
        row[reasoning_key] = reasoning
    if category is not None:
        row[category_key] = category
    return row


# ---------- Module surface ----------


def test_system_prompt_for_safety_reasoning_smoke_exists() -> None:
    assert "safety_reasoning_smoke" in SYSTEM_PROMPTS
    assert "ALLOW" in SYSTEM_PROMPTS["safety_reasoning_smoke"]
    assert "BLOCK" in SYSTEM_PROMPTS["safety_reasoning_smoke"]


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("nemotron_safety_reasoning") is transform_nemotron_safety_reasoning


def test_canonical_verdict_set_locks_to_three_labels() -> None:
    """Adding a 4th verdict needs an explicit roadmap decision; lock the
    set so a future drift is intentional."""
    assert SAFETY_VERDICT_CANONICAL == ("allow", "block", "escalate")


def test_aliases_cover_common_synonyms() -> None:
    """Sanity-check the alias map covers the most common label aliases.
    A snapshot shipping a new alias adds an entry; this test catches
    drift in the existing entries."""
    expected_pairs = {
        "safe": "allow",
        "unsafe": "block",
        "refuse": "block",
        "review": "escalate",
    }
    for raw, canonical in expected_pairs.items():
        assert SAFETY_VERDICT_ALIASES[raw] == canonical


# ---------- _canonicalize_safety_verdict ----------


def test_canonicalize_is_case_insensitive() -> None:
    assert _canonicalize_safety_verdict("ALLOW") == "allow"
    assert _canonicalize_safety_verdict("Block") == "block"
    assert _canonicalize_safety_verdict("ESCALATE") == "escalate"


def test_canonicalize_strips_whitespace() -> None:
    assert _canonicalize_safety_verdict("  allow  ") == "allow"


def test_canonicalize_returns_none_for_empty_or_missing() -> None:
    assert _canonicalize_safety_verdict(None) is None
    assert _canonicalize_safety_verdict("") is None
    assert _canonicalize_safety_verdict("   ") is None


def test_canonicalize_returns_none_for_unrecognized_label() -> None:
    """Out-of-vocab verdict → None so caller surfaces the row as
    malformed rather than silently defaulting."""
    assert _canonicalize_safety_verdict("yolo") is None


# ---------- Happy path per verdict ----------


@pytest.mark.parametrize("verdict", ["allow", "block", "escalate"])
def test_transform_emits_record_for_each_canonical_verdict(verdict: str) -> None:
    row = _row(verdict=verdict)
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["environment"] == "safety_reasoning_smoke"
    assert record["expected_answer"] == verdict
    assert record["extra_env_info"]["verdict"] == verdict
    assert record["reward_config"]["verifier"] == "safety_judge_stub"


def test_transform_preserves_reasoning_text_in_extra_env_info() -> None:
    row = _row(reasoning="Specific explanation text.")
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["extra_env_info"]["reasoning"] == "Specific explanation text."


def test_transform_preserves_category_in_extra_env_info() -> None:
    row = _row(category="violence")
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["extra_env_info"]["category"] == "violence"


def test_transform_handles_missing_optional_fields() -> None:
    row = _row(reasoning=None, category=None)
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["extra_env_info"]["reasoning"] == ""
    assert record["extra_env_info"]["category"] is None


# ---------- Alias resilience ----------


@pytest.mark.parametrize("prompt_key", ["prompt", "input", "question"])
def test_transform_accepts_each_prompt_field_alias(prompt_key: str) -> None:
    row = _row(prompt="Sensitive request.", prompt_key=prompt_key)
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["question"] == "Sensitive request."


@pytest.mark.parametrize("verdict_key", ["verdict", "label", "safety", "classification", "decision"])
def test_transform_accepts_each_verdict_field_alias(verdict_key: str) -> None:
    row = _row(verdict_key=verdict_key)
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["expected_answer"] == "allow"


@pytest.mark.parametrize("reasoning_key", ["reasoning", "explanation", "rationale"])
def test_transform_accepts_each_reasoning_field_alias(reasoning_key: str) -> None:
    row = _row(reasoning="text", reasoning_key=reasoning_key)
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["extra_env_info"]["reasoning"] == "text"


def test_transform_accepts_messages_list_prompt_format() -> None:
    """Some snapshots ship the prompt as a chat-style messages list
    (e.g., for multi-turn safety scenarios). Take the last user
    message as the prompt."""
    row = {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "First user turn."},
            {"role": "assistant", "content": "..."},
            {"role": "user", "content": "Final user turn here."},
        ],
        "verdict": "allow",
    }
    record = transform_nemotron_safety_reasoning(row, _spec())
    assert record["question"] == "Final user turn here."


def test_transform_accepts_synonym_verdict_labels() -> None:
    """`safe` → `allow`; `unsafe` → `block`; etc."""
    for raw, canonical in (("safe", "allow"), ("unsafe", "block"), ("review", "escalate")):
        row = _row(verdict=raw)
        record = transform_nemotron_safety_reasoning(row, _spec())
        assert record["expected_answer"] == canonical, (
            f"raw {raw!r} should canonicalize to {canonical!r}"
        )


# ---------- Error surfaces ----------


def test_transform_rejects_missing_prompt() -> None:
    row: dict[str, Any] = {"verdict": "allow"}
    with pytest.raises(ValueError, match="prompt"):
        transform_nemotron_safety_reasoning(row, _spec())


def test_transform_rejects_unrecognized_verdict() -> None:
    row = _row(verdict="yolo")
    with pytest.raises(ValueError, match="verdict"):
        transform_nemotron_safety_reasoning(row, _spec())


def test_transform_rejects_missing_verdict() -> None:
    row: dict[str, Any] = {"prompt": "Sensitive request."}
    with pytest.raises(ValueError, match="verdict"):
        transform_nemotron_safety_reasoning(row, _spec())


# ---------- safety_judge_stub verifier ----------


def test_score_record_dispatches_safety_judge_stub() -> None:
    record = {
        "environment": "safety_reasoning_smoke",
        "expected_answer": "allow",
        "reward_config": {"verifier": "safety_judge_stub"},
        "extra_env_info": {"verdict": "allow"},
    }
    score, diagnostics = score_record(
        "Verdict: ALLOW. The request is benign.", record
    )
    assert score == 1.0
    assert diagnostics["verdict_match"] is True
    assert diagnostics["expected_verdict"] == "allow"


def test_score_record_safety_judge_stub_no_match() -> None:
    record = {
        "environment": "safety_reasoning_smoke",
        "expected_answer": "block",
        "reward_config": {"verifier": "safety_judge_stub"},
        "extra_env_info": {"verdict": "block"},
    }
    score, diagnostics = score_record(
        "I think this is fine — allow.", record
    )
    assert score == 0.0
    assert diagnostics["verdict_match"] is False


def test_score_record_safety_judge_stub_is_case_insensitive() -> None:
    """The model emitting `BLOCK` should match gold `block`."""
    record = {
        "environment": "safety_reasoning_smoke",
        "expected_answer": "block",
        "reward_config": {"verifier": "safety_judge_stub"},
        "extra_env_info": {"verdict": "block"},
    }
    score, _ = score_record("VERDICT: BLOCK with reasoning.", record)
    assert score == 1.0


def test_score_record_safety_judge_stub_empty_expected_returns_zero() -> None:
    """Data-quality guard: gold verdict empty is a row bug, not a pass."""
    record = {
        "environment": "safety_reasoning_smoke",
        "expected_answer": "",
        "reward_config": {"verifier": "safety_judge_stub"},
        "extra_env_info": {"verdict": ""},
    }
    score, _ = score_record("Verdict: allow.", record)
    assert score == 0.0


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_safety_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_env_registry_carries_new_safety_reasoning_smoke_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "safety_reasoning_smoke"),
        None,
    )
    assert env is not None
    assert env["family"] == "safety"
    assert env["reward"]["verifier"] == "safety_judge_stub"
    assert env["resources"]["sandbox"] == "none"
    required = env["health_check"]["required_fields"]
    assert any("verdict" in r for r in required)


def test_data_registry_does_not_yet_carry_m0_safety_reasoning_row() -> None:
    """task057 Session 5 defers the data_registry row to Session 5.5
    pending real Nemotron-Safety SHA pin AND schema verification
    (README notes the dataset viewer has schema errors)."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    rows = [
        d for d in data_registry["datasets"]
        if d["id"] == "m0_safety_reasoning_smoke"
    ]
    assert rows == [], (
        "m0_safety_reasoning_smoke row should NOT be in data_registry yet — "
        "verify dataset schema (viewer errors per README) AND pin a real "
        "commit SHA before adding the row"
    )
