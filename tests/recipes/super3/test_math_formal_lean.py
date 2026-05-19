"""Tests for ``math_formal_lean`` M0 env scaffold (task056 Session 2).

The data_registry.yaml row is intentionally absent today — math_formal_lean
is awaiting legal/share-alike clearance per docs/m0-dataset-expansion-plan.md
§6 Q1. These tests pin the code path so that the moment a source is
cleared (Nemotron-Math-Proofs-v1, mathlib4 extraction, LeanDojo-Bench,
…), the wiring is a single data_registry row + a re-prep run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


# ---------- transform_lean_proof_stub (M0 prepare) ----------


def _spec(*, environment: str = "math_formal_lean", fields: dict | None = None) -> dict:
    """Minimal spec for transform_lean_proof_stub. The real
    data_registry row will have many more fields, but the transformer
    only consults ``environment``, ``fields``, ``milestone``,
    ``use_stage``, and the metadata fields ``make_record`` /
    ``base_metadata`` need (including ``contamination_against`` per
    task058's data_registry schema bump)."""
    return {
        "environment": environment,
        "milestone": "M0",
        "hf_dataset": "stub/lean-proofs",
        "hf_config": None,
        "hf_split": "train",
        "hf_revision": "deadbeef",
        "source_url": "https://example.test/stub",
        "license": "unknown",
        "domain": "reasoning",
        "difficulty": "research",
        "reward_type": "lean_proof_stub",
        "contamination": "decontaminate against MiniF2F / mathlib4 eval",
        "contamination_against": ["minif2f", "mathlib4_test"],
        "use_stage": ["M0 data_env_foundation"],
        "fields": fields or {},
    }


def test_transform_lean_proof_stub_with_default_columns() -> None:
    """Default column names ``statement`` / ``proof`` produce a well-shaped record."""
    from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
        transform_lean_proof_stub,
    )

    row = {
        "statement": "theorem add_zero (n : Nat) : n + 0 = n",
        "proof": "by simp",
        "theorem_name": "add_zero",
        "language": "lean4",
    }
    record = transform_lean_proof_stub(row, _spec())

    assert record["environment"] == "math_formal_lean"
    assert record["question"].startswith("theorem add_zero")
    assert record["expected_answer"] == "by simp"
    assert record["reward_config"]["verifier"] == "lean_proof_stub"
    assert record["reward_config"]["checks"] == ["nonempty_after_strip"]
    # System prompt must be the dedicated Lean one (not a math-numeric leak).
    sys_msg = record["responses_create_params"]["input"][0]
    assert sys_msg["role"] == "system"
    assert "Lean" in sys_msg["content"] or "formal-proof" in sys_msg["content"]
    # User prompt names the language so the model knows which dialect.
    user_msg = record["responses_create_params"]["input"][1]
    assert user_msg["role"] == "user"
    assert "lean4" in user_msg["content"]
    # extra_env_info carries the round-trip-able payload for the M0 verifier
    # + M1 SFT builder.
    extra = record["extra_env_info"]
    assert extra["theorem_name"] == "add_zero"
    assert extra["language"] == "lean4"
    assert extra["statement_only"].startswith("theorem add_zero")
    assert extra["reference_proof"] == "by simp"


def test_transform_lean_proof_stub_respects_fields_remap() -> None:
    """Source-agnostic field rename — when a candidate dataset uses
    different column names (LeanDojo-Bench uses ``theorem_statement`` /
    ``tactic_proof``; mathlib4 extraction might use ``formal_statement``
    / ``formal_proof``), the data_registry row just declares a ``fields``
    map and the transformer routes accordingly."""
    from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
        transform_lean_proof_stub,
    )

    row = {
        "theorem_statement": "theorem foo : True",
        "tactic_proof": "trivial",
    }
    record = transform_lean_proof_stub(
        row,
        _spec(fields={"statement": "theorem_statement", "proof": "tactic_proof"}),
    )
    assert record["question"] == "theorem foo : True"
    assert record["expected_answer"] == "trivial"


def test_transform_lean_proof_stub_rejects_empty_statement() -> None:
    from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
        transform_lean_proof_stub,
    )

    row = {"statement": "   ", "proof": "by simp"}
    with pytest.raises(ValueError, match="non-empty"):
        transform_lean_proof_stub(row, _spec())


def test_transform_lean_proof_stub_defaults_language_to_lean4() -> None:
    from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
        transform_lean_proof_stub,
    )

    row = {"statement": "theorem foo : True", "proof": "trivial"}
    record = transform_lean_proof_stub(row, _spec())
    assert record["extra_env_info"]["language"] == "lean4"


def test_lean_proof_stub_registered_in_converters() -> None:
    from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (
        CONVERTERS,
        transform_lean_proof_stub,
    )

    assert CONVERTERS["lean_proof_stub"] is transform_lean_proof_stub


# ---------- M0 health-baseline verifier ----------


def test_lean_proof_stub_verifier_returns_one_for_nonempty_candidate() -> None:
    pytest.importorskip("yaml")  # dependency of run_m0_health_baseline imports
    from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (
        score_record,
    )

    record = {
        "reward_config": {"verifier": "lean_proof_stub"},
        "expected_answer": "by simp",
        "extra_env_info": {"language": "lean4"},
    }
    score, diagnostics = score_record("by simp", record)
    assert score == 1.0
    assert diagnostics["nonempty_proof"] is True
    assert diagnostics["proof_length"] > 0
    assert diagnostics["language"] == "lean4"
    assert "latency_ms" in diagnostics


def test_lean_proof_stub_verifier_returns_zero_for_empty_candidate() -> None:
    from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (
        score_record,
    )

    record = {
        "reward_config": {"verifier": "lean_proof_stub"},
        "expected_answer": "by simp",
        "extra_env_info": {"language": "lean4"},
    }
    for empty in ("", "   ", None):
        score, diagnostics = score_record(empty, record)
        assert score == 0.0, f"expected 0.0 for {empty!r}"
        assert diagnostics["nonempty_proof"] is False


def test_lean_proof_stub_verifier_preserves_language_field() -> None:
    """``language`` defaults to lean4 when the record doesn't carry it."""
    from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (
        score_record,
    )

    record = {
        "reward_config": {"verifier": "lean_proof_stub"},
        "expected_answer": "trivial",
        "extra_env_info": {"language": "lean3"},
    }
    _, diagnostics = score_record("trivial", record)
    assert diagnostics["language"] == "lean3"


# ---------- environment_registry.yaml entry ----------


def test_environment_registry_carries_math_formal_lean_entry() -> None:
    registry_path = (
        Path("src/nemotron/recipes/super3/milestones/m0_data_env/environment_registry.yaml")
    )
    with registry_path.open(encoding="utf-8") as f:
        registry = yaml.safe_load(f)
    env_ids = {env["id"] for env in registry["environments"]}
    assert "math_formal_lean" in env_ids
    lean_env = next(env for env in registry["environments"] if env["id"] == "math_formal_lean")
    assert lean_env["family"] == "reasoning"
    assert lean_env["reward"]["verifier"] == "lean_proof_stub"
    # task021 Session 1 telemetry contract — these are the fields the
    # M0 health-baseline emits (see score_record).
    expected_telemetry = {"reward", "nonempty_proof", "proof_length", "language", "latency_ms"}
    assert expected_telemetry <= set(lean_env["telemetry"])


# ---------- M1 SFT supervision builder ----------


def test_assistant_for_lean_proof_uses_expected_answer() -> None:
    from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
        ASSISTANT_BUILDERS,
        assistant_for_lean_proof,
    )

    assert ASSISTANT_BUILDERS["math_formal_lean"] is assistant_for_lean_proof

    record = {
        "expected_answer": "by\n  simp\n  ring",
        "extra_env_info": {"reference_proof": "should not be used as fallback"},
    }
    msg = assistant_for_lean_proof(record)
    assert msg == {"role": "assistant", "content": "by\n  simp\n  ring"}


def test_assistant_for_lean_proof_falls_back_to_extra_env_info() -> None:
    """When the canonical expected_answer is empty, the defensive copy
    in extra_env_info.reference_proof takes over."""
    from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
        assistant_for_lean_proof,
    )

    record = {
        "expected_answer": "",
        "extra_env_info": {"reference_proof": "trivial"},
    }
    msg = assistant_for_lean_proof(record)
    assert msg["content"] == "trivial"


def test_m1_use_by_env_carries_lean_capability_tag() -> None:
    from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (
        M1_USE_BY_ENV,
    )

    assert "math_formal_lean" in M1_USE_BY_ENV
    capabilities = M1_USE_BY_ENV["math_formal_lean"]
    assert any("formal" in cap or "Lean" in cap or "lean" in cap for cap in capabilities)


# ---------- Cross-registry: unified index awareness ----------


def test_unified_index_validates_clean_after_lean_env_addition() -> None:
    """task030 Session 1 unified index validation must remain clean
    after the math_formal_lean environment_registry row lands. (The
    data_registry side is unchanged — no Lean dataset is pinned yet.)"""
    from nemotron.recipes.super3.milestones.data_registries.unified_index_loader import (
        validate_unified_index,
    )

    issues = validate_unified_index()
    assert issues == [], (
        "live unified index has schema drift after math_formal_lean addition:\n"
        + "\n".join(issues)
    )
