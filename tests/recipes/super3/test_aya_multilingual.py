"""Tests for the Aya multilingual_instruct env + converter (task057 Session 1).

Covers:

- `transform_aya_multilingual` happy path for each of the 6 M0 smoke
  languages (de / es / fr / it / ja / zh)
- Language-scope filter rejects rows outside the smoke 6
- Error surfaces: missing inputs / missing targets / out-of-scope
  language
- Accepts both `inputs`/`targets` and `instruction`/`response`
  alternate column names
- Accepts both full language name (`German`) and ISO code (`de`)
- `normalize_multilingual_text` does Unicode NFC + casefold (German ß
  / decomposed é); does NOT strip CJK punctuation
- `score_multilingual_text` exact-or-contains semantics
- `score_record` dispatch: `multilingual_exact_or_contains` verifier
  hits the new code path and emits expected diagnostics
- Registry integration: m0_multilingual_aya row + multilingual_instruct
  env row + converter wired into CONVERTERS
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    AYA_TARGET_LANGUAGE_CODES,
    AYA_TARGET_LANGUAGES,
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_aya_multilingual,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    normalize_multilingual_text,
    score_multilingual_text,
    score_record,
)


def _spec(dataset_id: str) -> dict:
    """Build a synthetic spec for the multilingual env.

    Per task057 Session 1's README: we deliberately don't add the
    m0_multilingual_aya row to data_registry.yaml yet (requires HF
    access to pin a real revision SHA). Tests use a synthetic spec
    matching the shape the converter expects."""
    if dataset_id == "m0_multilingual_aya":
        return {
            "id": "m0_multilingual_aya",
            "environment": "multilingual_instruct",
            "domain": "multilingual",
            "hf_dataset": "CohereLabs/aya_dataset",
            "hf_config": None,
            "hf_split": "train",
            "hf_val_split": "test",
            "hf_revision": "synthetic-test-spec",
            "source_url": "https://huggingface.co/datasets/CohereLabs/aya_dataset",
            "license": "apache-2.0",
            "converter": "aya_multilingual",
            "difficulty": "human_written_instruct",
            "reward_type": "multilingual_exact_or_contains",
            "contamination": "synthetic test spec",
            "contamination_against": ["MMLU-ProX", "WMT24++"],
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


# ---------- Module surface ----------


def test_system_prompt_for_multilingual_instruct_exists() -> None:
    assert "multilingual_instruct" in SYSTEM_PROMPTS
    assert "same language" in SYSTEM_PROMPTS["multilingual_instruct"]


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("aya_multilingual") is transform_aya_multilingual


def test_target_language_sets_cover_plan_six() -> None:
    """Plan §7 multilingual baseline calls out 6 languages.
    Lock the set; future M2 expansion will widen it as task027 lands."""
    # Codes covering: de / es / fr / it / ja / zh (incl. zh variants)
    expected_codes_subset = {"de", "es", "fr", "it", "ja", "zh"}
    assert expected_codes_subset.issubset(AYA_TARGET_LANGUAGE_CODES)
    # Full-name table includes the same 6 (or more for zh variants)
    assert "German" in AYA_TARGET_LANGUAGES
    assert "Spanish" in AYA_TARGET_LANGUAGES
    assert "French" in AYA_TARGET_LANGUAGES
    assert "Italian" in AYA_TARGET_LANGUAGES
    assert "Japanese" in AYA_TARGET_LANGUAGES
    assert "Chinese" in AYA_TARGET_LANGUAGES


# ---------- Happy path per language ----------


@pytest.mark.parametrize(
    "language,language_code,instruction,target",
    [
        ("German", "de", "Wie spät ist es?", "Es ist drei Uhr."),
        ("Spanish", "es", "¿Qué hora es?", "Son las tres."),
        ("French", "fr", "Quelle heure est-il ?", "Il est trois heures."),
        ("Italian", "it", "Che ora è?", "Sono le tre."),
        ("Japanese", "ja", "今何時ですか？", "三時です。"),
        ("Chinese", "zh", "现在几点？", "三点。"),
    ],
)
def test_transform_aya_emits_record_for_each_smoke_language(
    language: str, language_code: str, instruction: str, target: str
) -> None:
    row = {
        "inputs": instruction,
        "targets": target,
        "language": language,
        "language_code": language_code,
    }
    record = transform_aya_multilingual(row, _spec("m0_multilingual_aya"))
    assert record["environment"] == "multilingual_instruct"
    assert record["question"] == instruction
    assert record["expected_answer"] == target
    assert record["reward_config"]["verifier"] == "multilingual_exact_or_contains"
    assert record["extra_env_info"]["language"] == language
    assert record["extra_env_info"]["language_code"] == language_code


def test_transform_accepts_instruction_response_aliases() -> None:
    """Some Aya snapshots ship `instruction`/`response` instead of
    `inputs`/`targets`. Converter must handle both."""
    row = {
        "instruction": "Hola, ¿cómo estás?",
        "response": "Estoy bien, gracias.",
        "language_code": "es",
    }
    record = transform_aya_multilingual(row, _spec("m0_multilingual_aya"))
    assert record["question"] == "Hola, ¿cómo estás?"
    assert record["expected_answer"] == "Estoy bien, gracias."


def test_transform_uses_language_code_when_language_name_missing() -> None:
    """If only `language_code` is set (ISO), language scope must still
    accept the row."""
    row = {
        "inputs": "Wie geht's?",
        "targets": "Gut.",
        "language_code": "de",
    }
    record = transform_aya_multilingual(row, _spec("m0_multilingual_aya"))
    assert record["extra_env_info"]["language_code"] == "de"


# ---------- Language scope filter ----------


def test_transform_rejects_language_outside_smoke_scope() -> None:
    row = {
        "inputs": "Mwidzo bwanji?",
        "targets": "Tikuda.",
        "language": "Chichewa",
        "language_code": "ny",
    }
    with pytest.raises(ValueError, match="outside M0 smoke scope"):
        transform_aya_multilingual(row, _spec("m0_multilingual_aya"))


def test_transform_rejects_row_with_no_language_signal() -> None:
    """No language / language_code at all → out-of-scope."""
    row = {"inputs": "x", "targets": "y"}
    with pytest.raises(ValueError, match="outside M0 smoke scope"):
        transform_aya_multilingual(row, _spec("m0_multilingual_aya"))


# ---------- Error surfaces ----------


def test_transform_raises_on_missing_inputs() -> None:
    row = {"inputs": "", "targets": "answer", "language_code": "de"}
    with pytest.raises(ValueError, match="inputs"):
        transform_aya_multilingual(row, _spec("m0_multilingual_aya"))


def test_transform_raises_on_missing_targets() -> None:
    row = {"inputs": "question", "targets": "", "language_code": "de"}
    with pytest.raises(ValueError, match="targets"):
        transform_aya_multilingual(row, _spec("m0_multilingual_aya"))


# ---------- normalize_multilingual_text ----------


def test_normalize_handles_german_eszett_casefold() -> None:
    """German ß casefolds to ss — important so 'GROSSE STRAßE' and
    'große straße' match. Plain `.lower()` doesn't do this."""
    a = normalize_multilingual_text("GROSSE STRAßE")
    b = normalize_multilingual_text("große straße")
    assert a == b


def test_normalize_does_nfc_compose() -> None:
    """Decomposed (e + combining acute) and composed (é) must compare
    equal."""
    decomposed = "café"
    composed = "café"
    assert normalize_multilingual_text(decomposed) == normalize_multilingual_text(composed)


def test_normalize_preserves_chinese_punctuation() -> None:
    """Chinese full-width punctuation carries meaning; do not strip."""
    text = "你好，世界。"
    out = normalize_multilingual_text(text)
    assert "，" in out
    assert "。" in out


def test_normalize_does_not_strip_english_articles() -> None:
    """The English-specific `normalize_text_answer` strips 'the' / 'a';
    the multilingual normalizer must NOT — English isn't this verifier's
    concern, and articles in other languages (German die / der) must
    survive."""
    out = normalize_multilingual_text("die Straße")
    assert "die" in out  # German article must survive


# ---------- score_multilingual_text ----------


def test_score_exact_match_returns_one() -> None:
    assert score_multilingual_text("Es ist drei Uhr.", "Es ist drei Uhr.") == 1.0


def test_score_contains_match_returns_one() -> None:
    assert score_multilingual_text(
        "Antwort: Es ist drei Uhr.",
        "Es ist drei Uhr.",
    ) == 1.0


def test_score_no_match_returns_zero() -> None:
    assert score_multilingual_text("nope", "Es ist drei Uhr.") == 0.0


def test_score_empty_expected_returns_zero() -> None:
    """Empty gold answer is a data-quality bug — must not be silently
    treated as a pass."""
    assert score_multilingual_text("any answer", "") == 0.0


# ---------- score_record dispatch ----------


def test_score_record_dispatches_multilingual_verifier() -> None:
    record = {
        "environment": "multilingual_instruct",
        "expected_answer": "Es ist drei Uhr.",
        "reward_config": {"verifier": "multilingual_exact_or_contains"},
        "extra_env_info": {"language_code": "de"},
    }
    candidate = "Es ist drei Uhr."
    score, diagnostics = score_record(candidate, record)
    assert score == 1.0
    assert diagnostics["exact_match"] is True
    assert diagnostics["contains_match"] is True
    assert "normalized_answer" in diagnostics


def test_score_record_multilingual_no_match() -> None:
    record = {
        "environment": "multilingual_instruct",
        "expected_answer": "Bonjour",
        "reward_config": {"verifier": "multilingual_exact_or_contains"},
        "extra_env_info": {"language_code": "fr"},
    }
    score, diagnostics = score_record("Hello", record)
    assert score == 0.0
    assert diagnostics["exact_match"] is False
    assert diagnostics["contains_match"] is False


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_multilingual_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_data_registry_does_not_yet_carry_m0_multilingual_aya_row() -> None:
    """task057 Session 1 deliberately defers adding the production
    data_registry row to a Session 1.5 follow-up once a real Aya commit
    SHA is verified against the live HF source. Lock the deferral so
    future PRs don't accidentally re-add it without a real pin (which
    would trigger the revision-pin audit blocker)."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    rows = [d for d in data_registry["datasets"] if d["id"] == "m0_multilingual_aya"]
    assert rows == [], (
        "m0_multilingual_aya row should NOT be in data_registry yet — "
        "pin a real Aya commit SHA first, then add the row in a follow-up"
    )


def test_env_registry_carries_new_multilingual_instruct_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "multilingual_instruct"),
        None,
    )
    assert env is not None
    assert env["reward"]["verifier"] == "multilingual_exact_or_contains"
    assert env["family"] == "multilingual"
    assert env["resources"]["sandbox"] == "none"
