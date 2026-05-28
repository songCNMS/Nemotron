"""AIME-25 / HMMT math-decontamination tests.

Split off from `test_m1_agentic_sft.py` because that module imports
`run_m1_sft_roundtrip_smoke` which hard-imports `pyarrow` — not
present on a clean sandbox. The decontamination logic only needs the
prepare-side surface, so a separate file keeps the new tests
collectable on sandbox CI.

See `docs/chat-template-consistency-review.md` predecessor work for
the related cross-stage hardening pattern, and
`workspace/tasks/task071*/qwen_original_vs_sft_math_pipeline_review_session82.md`
for the diagnosis that motivated this wiring.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


from nemotron.recipes.super3.milestones.m1_agentic_sft.prepare_m1_agentic_sft import (  # noqa: E402
    MATH_SUPERVISION_STRATEGY_V3,
    MATH_SUPERVISION_STRATEGY_V7,
    MATH_SUPERVISION_STRATEGY_V8,
    MATH_SUPERVISION_STRATEGY_V9,
    MATH_V3_FINAL_ANSWER_AUX_WEIGHT,
    MATH_V3_FORMAT_REPAIR_WEIGHT,
    MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT,
    _has_boxed_answer_near_end,
    decontaminate_math_rows,
    load_math_decontamination_corpus,
    prepare,
)


def _math_train_row(
    prompt: str,
    *,
    environment: str = "math_competition_numeric",
) -> dict:
    """Shape matches what convert_m0_record emits at the SFT prep stage."""
    return {
        "messages": [
            {"role": "system", "content": "You are a math reasoning assistant."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Step. \\boxed{1}"},
        ],
        "metadata": {
            "m0_environment": environment,
            "m0_split": "train",
        },
    }


# ---------- decontaminate_math_rows ----------


def test_decontaminate_drops_overlapping_aime_prompt_from_numinamath() -> None:
    contaminated_prompt = (
        "Find the number of ordered triples of positive integers (a, b, c) "
        "such that a + b + c = 50 and gcd(a, b, c) = 1. Place your final "
        "answer in a box."
    )
    safe_prompt = (
        "Write a short python script that prints the squares of the first "
        "five positive integers, then return the script verbatim."
    )
    rows = [
        _math_train_row(contaminated_prompt),
        _math_train_row(safe_prompt),
        # Same contaminated text on a non-math env must pass through —
        # decontamination is scoped to math_competition_numeric.
        _math_train_row(contaminated_prompt, environment="terminal_basic_shell"),
    ]
    corpus = [
        {"id": "aime25_p07", "prompt": contaminated_prompt},
        {"id": "hmmt_other", "prompt": "Unrelated HMMT prompt about something else."},
    ]

    kept, summary = decontaminate_math_rows(
        rows,
        corpus=corpus,
        ngram_size=5,
        blocker_threshold=0.5,
    )

    assert len(kept) == 2
    kept_user_prompts = {
        message["content"]
        for row in kept
        for message in row["messages"]
        if message["role"] == "user"
    }
    assert safe_prompt in kept_user_prompts
    # Non-math copy of the contaminated text stays — scope is correct.
    assert contaminated_prompt in kept_user_prompts
    assert summary["applied"] is True
    assert summary["dropped_rows"] == 1
    assert summary["scanned_rows"] == 2  # 2 math rows scanned, 1 skipped
    assert summary["corpus_size"] == 2


def test_decontaminate_passthrough_when_corpus_empty() -> None:
    rows = [_math_train_row("Some math prompt")]
    kept, summary = decontaminate_math_rows(rows, corpus=[])
    assert kept == rows
    assert summary["applied"] is False
    assert summary["dropped_rows"] == 0


def test_decontaminate_passthrough_when_no_math_rows() -> None:
    rows = [_math_train_row("Plain prompt", environment="terminal_basic_shell")]
    corpus = [{"id": "aime25_p07", "prompt": "Find the ordered triples..."}]
    kept, summary = decontaminate_math_rows(rows, corpus=corpus)
    assert kept == rows
    assert summary["applied"] is False
    assert summary["scanned_rows"] == 0


# ---------- load_math_decontamination_corpus ----------


def test_load_math_decontamination_corpus_reads_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "aime25_corpus.jsonl"
    path.write_text(
        json.dumps({"id": "p1", "prompt": "first eval prompt"})
        + "\n"
        + json.dumps({"id": "p2", "prompt": "second eval prompt"})
        + "\n",
        encoding="utf-8",
    )
    corpus = load_math_decontamination_corpus(path)
    assert [item["id"] for item in corpus] == ["p1", "p2"]


# ---------- prepare() guard tests ----------


def _base_record(environment: str, *, user_prompt: str = "User") -> dict:
    return {
        "environment": environment,
        "question": "Question?",
        "expected_answer": "Answer",
        "responses_create_params": {
            "input": [
                {"role": "system", "content": "System"},
                # convert_m0_record forwards this message verbatim into the SFT
                # user turn — that's the text the decontam scanner sees.
                {"role": "user", "content": user_prompt},
            ],
            "tools": [],
        },
        "extra_env_info": {},
    }


def _prepare_args(
    tmp_path: Path,
    *,
    strategy: str,
    corpus_path: Path | None = None,
    skip_check: bool = False,
):
    """Synthetic prepare() args wired with one contaminated and one clean
    NuminaMath row so the decontamination guard surface is exercised
    without needing a full M0 fixture.
    """
    m0_root = tmp_path / "m0"

    def write_split(environment: str, split: str, records: list[dict]) -> None:
        env_dir = m0_root / environment
        env_dir.mkdir(parents=True, exist_ok=True)
        with (env_dir / f"{split}-split.jsonl").open("w", encoding="utf-8") as f:
            for record in records:
                json.dump(record, f)
                f.write("\n")

    contaminated_prompt_text = (
        "Find the largest prime p such that p divides 50! + 1 and p < 200. "
        "Place your final answer in a box."
    )
    contaminated = _base_record(
        "math_competition_numeric", user_prompt=contaminated_prompt_text
    )
    contaminated["question"] = contaminated_prompt_text
    contaminated["expected_answer"] = "131"
    contaminated["extra_env_info"]["reference_solution"] = (
        "We test primes between 100 and 200 using Wilson's theorem. "
        "Step-by-step factor analysis yields \\boxed{131}."
    )
    clean_prompt_text = "Compute 7 + 5 step by step, then box the answer."
    clean = _base_record("math_competition_numeric", user_prompt=clean_prompt_text)
    clean["question"] = clean_prompt_text
    clean["expected_answer"] = "12"
    clean["extra_env_info"]["reference_solution"] = (
        "7 + 5 = 12. So the final answer is \\boxed{12}."
    )
    write_split("math_competition_numeric", "train", [contaminated, clean])
    write_split("math_competition_numeric", "val", [clean])

    class Args:
        pass

    Args.m0_input_dir = m0_root
    Args.output_dir = tmp_path / "out"
    Args.m0_health_baseline = None
    Args.max_records_per_env = None
    Args.max_val_shadow_per_env = None
    Args.overwrite = False
    Args.math_supervision_strategy = strategy
    Args.math_v3_verified_full_solution_weight = MATH_V3_VERIFIED_FULL_SOLUTION_WEIGHT
    Args.math_v3_final_answer_aux_weight = MATH_V3_FINAL_ANSWER_AUX_WEIGHT
    Args.math_v3_format_repair_weight = MATH_V3_FORMAT_REPAIR_WEIGHT
    Args.decontaminate_math_against_corpus = corpus_path
    Args.decontaminate_math_ngram_size = 5
    Args.decontaminate_math_blocker_threshold = 0.5
    Args.skip_math_decontamination_check = skip_check
    return Args


def test_prepare_v7_requires_decontamination_corpus(tmp_path: Path) -> None:
    args = _prepare_args(tmp_path, strategy=MATH_SUPERVISION_STRATEGY_V7)
    with pytest.raises(ValueError, match="decontaminate-math-against-corpus"):
        prepare(args)


def test_prepare_v8_requires_decontamination_corpus(tmp_path: Path) -> None:
    args = _prepare_args(tmp_path, strategy=MATH_SUPERVISION_STRATEGY_V8)
    with pytest.raises(ValueError, match="decontaminate-math-against-corpus"):
        prepare(args)


def test_prepare_v9_requires_decontamination_corpus(tmp_path: Path) -> None:
    args = _prepare_args(tmp_path, strategy=MATH_SUPERVISION_STRATEGY_V9)
    with pytest.raises(ValueError, match="decontaminate-math-against-corpus"):
        prepare(args)


def test_prepare_v7_skip_flag_allows_run_without_corpus(tmp_path: Path) -> None:
    args = _prepare_args(
        tmp_path, strategy=MATH_SUPERVISION_STRATEGY_V7, skip_check=True
    )
    manifest = prepare(args)
    assert manifest["math_decontamination"]["applied"] is False
    assert manifest["math_decontamination"]["skip_check"] is True
    assert manifest["math_decontamination"]["strategy_requires_corpus"] is True


def test_prepare_v3_does_not_require_corpus(tmp_path: Path) -> None:
    args = _prepare_args(tmp_path, strategy=MATH_SUPERVISION_STRATEGY_V3)
    manifest = prepare(args)
    assert manifest["math_decontamination"]["applied"] is False
    assert manifest["math_decontamination"]["strategy_requires_corpus"] is False


def test_prepare_v7_with_corpus_drops_contaminated_row(tmp_path: Path) -> None:
    corpus_path = tmp_path / "aime25_corpus.jsonl"
    corpus_path.write_text(
        json.dumps(
            {
                "id": "aime25_p07",
                "prompt": (
                    "Find the largest prime p such that p divides 50! + 1 "
                    "and p < 200. Place your final answer in a box."
                ),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    args = _prepare_args(
        tmp_path,
        strategy=MATH_SUPERVISION_STRATEGY_V7,
        corpus_path=corpus_path,
    )
    manifest = prepare(args)
    assert manifest["math_decontamination"]["applied"] is True
    assert manifest["math_decontamination"]["corpus_path"] == str(corpus_path)
    base = manifest["math_decontamination"]["base_train"]
    assert base["dropped_rows"] >= 1
    assert base["scanned_rows"] >= 1
    assert base["blocker_threshold"] == 0.5
    assert base["ngram_size"] == 5


# ---- _has_boxed_answer_near_end nested-brace handling ----


def test_has_boxed_answer_near_end_accepts_nested_brace_fraction() -> None:
    """Regression: the helper previously used a regex (``\\boxed{[^{}]+}``)
    that excluded nested braces, so legitimate scalar-fraction finals like
    ``\\boxed{\\frac{1}{2}}`` were silently rejected — even though
    ``_is_scalar_numeric_answer_text`` accepts ``\\frac{...}{...}``.
    The two checks must agree so the V4/V5/V7 hard-math filters don't
    drop valid scalar-fraction answers from their sidecar pools.
    """
    solution = (
        "We follow standard manipulation. Step 1: ... step 2: ... "
        "step 3: ... so the final answer is \\boxed{\\frac{1}{2}}."
    )
    assert _has_boxed_answer_near_end(solution, tail_chars=3000) is True


def test_has_boxed_answer_near_end_still_accepts_plain_integer() -> None:
    solution = "Steps ... so the final answer is \\boxed{42}."
    assert _has_boxed_answer_near_end(solution, tail_chars=3000) is True


def test_has_boxed_answer_near_end_rejects_no_boxed_and_far_away_boxed() -> None:
    # No boxed at all
    assert _has_boxed_answer_near_end("no boxed answer here at all", tail_chars=3000) is False
    # Boxed exists but is far from end of text — proximity check should fail
    far_away = "\\boxed{42}" + " " * 5000
    assert _has_boxed_answer_near_end(far_away, tail_chars=100) is False
    # Same far-away text but with a more generous tail — should pass
    assert _has_boxed_answer_near_end(far_away, tail_chars=10_000) is True
