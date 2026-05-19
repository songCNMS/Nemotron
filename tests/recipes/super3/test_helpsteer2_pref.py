"""Tests for the HelpSteer-2 → helpsteer2_pref_compare converter (task018 Session 2).

Covers:

- ``transform_helpsteer2_pref`` happy path on both HelpSteer-2 flavors:
  explicit-pair rows (``response_a``/``b`` + ``preference_label``) and
  attribute-derived rows (aggregate ``helpfulness`` + ``coherence`` +
  ``correctness`` per side).
- Alternate column conventions: ``chosen``/``rejected`` as aliases for
  ``response_a``/``response_b``.
- Edge cases: tied scores fall back to "A"; one-sided missing attributes
  pick the side with data; explicit_label takes precedence over
  attribute-derived.
- Error surfaces: missing prompt / missing one or both responses /
  invalid preference_label / no labels or attributes at all.
- Registry integration: ``m0_helpsteer2_pref`` row +
  ``helpsteer2_pref_compare`` env row + ``helpsteer2_pref_pair``
  converter wired into CONVERTERS; ``validate_registries`` clean.
- RLHF pref data registry: helpsteer2 row carries ``m0_landed: true``
  pointing at the new M0 data row.
- RLHF env registry: ``genrm_compare`` stays ``blocked_external`` — the
  judge service is still a blocker; only the data-side cleared.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_helpsteer2_pref,
    validate_registries,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
RLHF_ENV_REGISTRY_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_rlhf/rlhf_env_registry.yaml"
)
RLHF_PREF_DATA_REGISTRY_PATH = (
    REPO_ROOT
    / "src/nemotron/recipes/super3/milestones/m1_rlhf/rlhf_pref_data_registry.yaml"
)


def _spec(dataset_id: str) -> dict:
    registry = load_yaml(DATA_REGISTRY_PATH)
    for dataset in registry["datasets"]:
        if dataset["id"] == dataset_id:
            spec = dict(dataset)
            spec["milestone"] = registry["milestone"]
            return spec
    raise AssertionError(f"missing dataset {dataset_id}")


def _explicit_pair_row(label: str = "A") -> dict:
    return {
        "prompt": "Explain quicksort in two sentences.",
        "response_a": "Quicksort picks a pivot and recursively sorts partitions.",
        "response_b": "It sorts things, you know, fast.",
        "preference_label": label,
    }


def _derived_pair_row(
    *,
    helpfulness_a: int = 4,
    helpfulness_b: int = 2,
    coherence_a: int = 4,
    coherence_b: int = 3,
    correctness_a: int = 4,
    correctness_b: int = 2,
) -> dict:
    return {
        "prompt": "Explain quicksort in two sentences.",
        "response_a": "Quicksort picks a pivot...",
        "response_b": "It sorts things fast.",
        "helpfulness_a": helpfulness_a,
        "helpfulness_b": helpfulness_b,
        "coherence_a": coherence_a,
        "coherence_b": coherence_b,
        "correctness_a": correctness_a,
        "correctness_b": correctness_b,
    }


# ---------- Module surface ----------


def test_system_prompt_for_helpsteer2_pref_compare_exists() -> None:
    assert "helpsteer2_pref_compare" in SYSTEM_PROMPTS


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("helpsteer2_pref_pair") is transform_helpsteer2_pref


# ---------- Happy path: explicit-pair ----------


def test_transform_explicit_pair_label_a_emits_a_as_expected_answer() -> None:
    row = _explicit_pair_row(label="A")
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["environment"] == "helpsteer2_pref_compare"
    assert record["expected_answer"] == "A"
    assert record["reward_config"]["verifier"] == "genrm_compare"
    assert record["extra_env_info"]["preference_label"] == "A"
    assert record["extra_env_info"]["label_derivation"] == "explicit_label"
    assert record["extra_env_info"]["completion_a"].startswith("Quicksort")
    assert record["extra_env_info"]["completion_b"].startswith("It sorts")


def test_transform_explicit_pair_label_b_emits_b() -> None:
    row = _explicit_pair_row(label="B")
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "B"


def test_transform_accepts_lowercase_preference_label() -> None:
    row = _explicit_pair_row(label="a")
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "A"


def test_transform_accepts_chosen_rejected_aliases() -> None:
    """Some HelpSteer-2 snapshots ship `chosen`/`rejected` instead of
    `response_a`/`response_b`. The converter must handle both
    conventions so a snapshot rename doesn't break the pipeline."""
    row = {
        "prompt": "Explain quicksort.",
        "chosen": "Quicksort picks a pivot.",
        "rejected": "It sorts things fast.",
        "preference_label": "A",
    }
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["extra_env_info"]["completion_a"].startswith("Quicksort")
    assert record["extra_env_info"]["completion_b"].startswith("It sorts")


# ---------- Happy path: attribute-derived ----------


def test_transform_attribute_derived_label_a_when_a_scores_higher() -> None:
    row = _derived_pair_row(
        helpfulness_a=4, helpfulness_b=2,
        coherence_a=4, coherence_b=3,
        correctness_a=4, correctness_b=2,
    )
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "A"
    assert record["extra_env_info"]["label_derivation"] == "aggregate_score"


def test_transform_attribute_derived_label_b_when_b_scores_higher() -> None:
    row = _derived_pair_row(
        helpfulness_a=1, helpfulness_b=4,
        coherence_a=2, coherence_b=4,
        correctness_a=2, correctness_b=4,
    )
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "B"


def test_transform_tied_score_falls_back_to_a_with_stable_ordering() -> None:
    """Tied aggregate scores default to "A" (stable ordering). Operators
    can post-filter ties via `label_derivation` metadata."""
    row = _derived_pair_row(
        helpfulness_a=3, helpfulness_b=3,
        coherence_a=3, coherence_b=3,
        correctness_a=3, correctness_b=3,
    )
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "A"


def test_transform_explicit_label_overrides_attribute_derivation() -> None:
    """If both an explicit ``preference_label`` and rating attributes
    are present, explicit wins — the human annotation is authoritative."""
    row = _derived_pair_row(
        helpfulness_a=1, helpfulness_b=4,  # attributes favor B
        coherence_a=1, coherence_b=4,
        correctness_a=1, correctness_b=4,
    )
    row["preference_label"] = "A"  # explicit label says A
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "A"
    assert record["extra_env_info"]["label_derivation"] == "explicit_label"


def test_transform_one_sided_missing_attributes_picks_present_side() -> None:
    """If one side has no rating attributes at all, treat the side with
    data as preferred (preserves signal over dropping the row)."""
    row = {
        "prompt": "Explain quicksort.",
        "response_a": "Quicksort picks a pivot.",
        "response_b": "It sorts fast.",
        "helpfulness_a": 4,
        "coherence_a": 4,
        # No _b attributes at all
    }
    record = transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))
    assert record["expected_answer"] == "A"


# ---------- Error surfaces ----------


def test_transform_raises_on_missing_prompt() -> None:
    row = _explicit_pair_row()
    row["prompt"] = ""
    with pytest.raises(ValueError, match="prompt"):
        transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))


def test_transform_raises_on_missing_response() -> None:
    row = _explicit_pair_row()
    row["response_a"] = ""
    with pytest.raises(ValueError, match="responses"):
        transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))


def test_transform_raises_on_invalid_preference_label() -> None:
    row = _explicit_pair_row(label="A")
    row["preference_label"] = "neither"
    with pytest.raises(ValueError, match="preference_label"):
        transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))


def test_transform_raises_when_no_label_or_attributes() -> None:
    row = {
        "prompt": "Explain quicksort.",
        "response_a": "Quicksort picks a pivot.",
        "response_b": "It sorts fast.",
    }
    with pytest.raises(ValueError, match="neither preference_label nor"):
        transform_helpsteer2_pref(row, _spec("m0_helpsteer2_pref"))


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_helpsteer2_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_data_registry_carries_new_m0_helpsteer2_pref_row() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    row = next(
        (d for d in data_registry["datasets"] if d["id"] == "m0_helpsteer2_pref"),
        None,
    )
    assert row is not None
    assert row["environment"] == "helpsteer2_pref_compare"
    assert row["converter"] == "helpsteer2_pref_pair"
    assert row["hf_dataset"] == "nvidia/HelpSteer2"
    assert row["license"] == "cc-by-4.0"
    assert row["reward_type"] == "genrm_compare"
    assert "MT-Bench" in row["contamination_against"]


def test_env_registry_carries_new_helpsteer2_pref_compare_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "helpsteer2_pref_compare"),
        None,
    )
    assert env is not None
    assert env["reward"]["verifier"] == "genrm_compare"
    assert env["resources"]["sandbox"] == "none"
    assert env["resources"]["max_turns"] == 1


# ---------- RLHF registries ----------


def test_rlhf_pref_data_registry_marks_helpsteer2_as_m0_landed() -> None:
    """RLHF pref-data candidate registry tracks which candidate has an
    M0 converter shipped. helpsteer2 must now carry m0_landed=True
    pointing at the new data row."""
    data = yaml.safe_load(RLHF_PREF_DATA_REGISTRY_PATH.read_text(encoding="utf-8"))
    helpsteer2 = next(
        (d for d in data["datasets"] if d["id"] == "helpsteer2"),
        None,
    )
    assert helpsteer2 is not None
    assert helpsteer2.get("m0_landed") is True
    assert helpsteer2.get("m0_data_row") == "m0_helpsteer2_pref"


def test_rlhf_env_registry_genrm_compare_stays_blocked_external() -> None:
    """Session 2 lands the data side. The judge service (task018
    Session 3) is the other blocker; until it lands, the env row must
    stay `blocked_external` (the bridge skips it; cluster smoke would
    fail without a judge). Test pins the status so a future PR doesn't
    accidentally flip it to active before the judge is up."""
    data = yaml.safe_load(RLHF_ENV_REGISTRY_PATH.read_text(encoding="utf-8"))
    genrm = next(
        (e for e in data["envs"] if e["nemo_gym_env"] == "genrm_compare"),
        None,
    )
    assert genrm is not None
    assert genrm["status"] == "blocked_external"
    # Note must reflect data-side clearance for human reviewers
    notes = str(genrm.get("notes") or "")
    assert "m0_helpsteer2_pref" in notes or "Session 2 landed" in notes
