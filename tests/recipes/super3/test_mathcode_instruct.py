"""Tests for the MathCodeInstruct → math_with_tools env + converter
(task057 Session 6).

Covers:

- `transform_mathcode_instruct` happy path (problem + solution +
  `\\boxed{}` final answer)
- Field-name alias resilience:
  - problem column: problem / question / instruction / input
  - solution column: solution / response / output / answer
- Code-block detection: fenced ` ```python ... ``` ` and
  `<python>...</python>` tagged forms
- Error surfaces: missing problem / missing solution / missing
  `\\boxed{}` final answer
- `math_with_tools_match` verifier: candidate boxed-match, fallback
  contains-match when candidate omits `\\boxed{}`, case + whitespace
  normalization, malformed flag, code-block detection on candidate
- `score_record` dispatch
- `is_numinamath_source_id` dedup helper
- Registry integration: env_registry row + verifier dispatch wired;
  data_registry row deferred (Session 6.5)
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
    PYTHON_CODE_BLOCK_RE,
    SYSTEM_PROMPTS,
    count_python_code_blocks,
    extract_boxed_answer,
    is_numinamath_source_id,
    load_yaml,
    transform_mathcode_instruct,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec() -> dict:
    """Synthetic spec for the math_with_tools env (data_registry row
    deferred to Session 6.5)."""
    return {
        "id": "m0_math_with_tools",
        "environment": "math_with_tools",
        "domain": "reasoning",
        "hf_dataset": "MathLLMs/MathCodeInstruct",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": "train",
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://huggingface.co/datasets/MathLLMs/MathCodeInstruct",
        "license": "apache-2.0",
        "converter": "mathcode_instruct",
        "difficulty": "math_with_tools",
        "reward_type": "math_with_tools_match",
        "contamination": "synthetic test spec",
        "contamination_against": ["MATH", "AIME", "NuminaMath"],
        "milestone": "M0",
        "use_stage": ["M0 data_env_foundation"],
    }


def _row(
    *,
    problem: str = "What is 12 + 7?",
    solution: str | None = (
        "We can verify with Python.\n"
        "```python\n"
        "print(12 + 7)\n"
        "```\n"
        "So the answer is \\boxed{19}."
    ),
    problem_key: str = "problem",
    solution_key: str = "solution",
) -> dict[str, Any]:
    row: dict[str, Any] = {problem_key: problem}
    if solution is not None:
        row[solution_key] = solution
    return row


# ---------- Module surface ----------


def test_system_prompt_for_math_with_tools_exists() -> None:
    assert "math_with_tools" in SYSTEM_PROMPTS
    assert "\\boxed" in SYSTEM_PROMPTS["math_with_tools"]
    assert "python" in SYSTEM_PROMPTS["math_with_tools"].lower()


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("mathcode_instruct") is transform_mathcode_instruct


def test_python_code_block_re_matches_fenced_form() -> None:
    text = "```python\nprint(1)\n```"
    assert PYTHON_CODE_BLOCK_RE.search(text) is not None


def test_python_code_block_re_matches_tagged_form() -> None:
    text = "<python>print(2)</python>"
    assert PYTHON_CODE_BLOCK_RE.search(text) is not None


# ---------- count_python_code_blocks ----------


def test_count_blocks_zero_for_no_code() -> None:
    assert count_python_code_blocks("just prose, no code.") == 0


def test_count_blocks_handles_none() -> None:
    assert count_python_code_blocks(None) == 0


def test_count_blocks_counts_fenced_block() -> None:
    text = "before\n```python\nx = 1\n```\nafter"
    assert count_python_code_blocks(text) == 1


def test_count_blocks_counts_tagged_block() -> None:
    text = "before <python>x = 1</python> after"
    assert count_python_code_blocks(text) == 1


def test_count_blocks_counts_multiple_blocks() -> None:
    text = (
        "```python\na = 1\n```\n"
        "<python>b = 2</python>\n"
        "```python\nc = 3\n```"
    )
    assert count_python_code_blocks(text) == 3


def test_count_blocks_ignores_non_python_fences() -> None:
    text = "```bash\nls -la\n```"
    assert count_python_code_blocks(text) == 0


# ---------- Happy path ----------


def test_transform_emits_record_with_boxed_answer() -> None:
    record = transform_mathcode_instruct(_row(), _spec())
    assert record["environment"] == "math_with_tools"
    assert record["expected_answer"] == "19"
    assert record["reward_config"]["verifier"] == "math_with_tools_match"


def test_transform_preserves_reference_solution() -> None:
    record = transform_mathcode_instruct(_row(), _spec())
    assert "```python" in record["extra_env_info"]["reference_solution"]
    assert "\\boxed{19}" in record["extra_env_info"]["reference_solution"]


def test_transform_sets_has_code_block_when_fenced_python_present() -> None:
    record = transform_mathcode_instruct(_row(), _spec())
    assert record["extra_env_info"]["has_code_block"] is True
    assert record["extra_env_info"]["code_block_count"] == 1


def test_transform_sets_has_code_block_when_tagged_python_present() -> None:
    row = _row(
        solution=(
            "Compute it:\n"
            "<python>print(3 * 7)</python>\n"
            "Answer: \\boxed{21}."
        )
    )
    record = transform_mathcode_instruct(row, _spec())
    assert record["extra_env_info"]["has_code_block"] is True
    assert record["expected_answer"] == "21"


def test_transform_handles_solution_without_code_block() -> None:
    """Some MathCodeInstruct rows are pure-CoT without code. The
    converter should still emit a record (the env-level health check
    will surface low has_code_block rates separately)."""
    row = _row(
        solution="Compute step by step: 12 + 7 = 19. So the answer is \\boxed{19}."
    )
    record = transform_mathcode_instruct(row, _spec())
    assert record["extra_env_info"]["has_code_block"] is False
    assert record["extra_env_info"]["code_block_count"] == 0
    assert record["expected_answer"] == "19"


def test_transform_extracts_last_boxed_when_multiple_present() -> None:
    """Intermediate `\\boxed{}` is used in some rows to highlight
    sub-results. Convention is last boxed = final answer."""
    row = _row(
        solution=(
            "First we get \\boxed{a/b}. After simplifying, the answer is "
            "\\boxed{42}."
        )
    )
    record = transform_mathcode_instruct(row, _spec())
    assert record["expected_answer"] == "42"


def test_transform_uses_system_prompt_in_input_messages() -> None:
    record = transform_mathcode_instruct(_row(), _spec())
    messages = record["responses_create_params"]["input"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPTS["math_with_tools"]
    assert messages[1]["role"] == "user"


# ---------- Field-name alias resilience ----------


@pytest.mark.parametrize(
    "problem_key", ["problem", "question", "instruction", "input"]
)
def test_transform_accepts_each_problem_field_alias(problem_key: str) -> None:
    row = _row(problem="Compute 1+1.", problem_key=problem_key)
    record = transform_mathcode_instruct(row, _spec())
    assert record["question"] == "Compute 1+1."


@pytest.mark.parametrize(
    "solution_key", ["solution", "response", "output", "answer"]
)
def test_transform_accepts_each_solution_field_alias(solution_key: str) -> None:
    row = _row(
        solution="Step. \\boxed{99}",
        solution_key=solution_key,
    )
    record = transform_mathcode_instruct(row, _spec())
    assert record["expected_answer"] == "99"


# ---------- Error surfaces ----------


def test_transform_rejects_missing_problem() -> None:
    row: dict[str, Any] = {"solution": "blah \\boxed{1}"}
    with pytest.raises(ValueError, match="problem"):
        transform_mathcode_instruct(row, _spec())


def test_transform_rejects_empty_problem() -> None:
    row: dict[str, Any] = {"problem": "   ", "solution": "x \\boxed{1}"}
    with pytest.raises(ValueError, match="problem"):
        transform_mathcode_instruct(row, _spec())


def test_transform_rejects_missing_solution() -> None:
    row: dict[str, Any] = {"problem": "What is X?"}
    with pytest.raises(ValueError, match="solution"):
        transform_mathcode_instruct(row, _spec())


def test_transform_rejects_solution_without_boxed_answer() -> None:
    row = _row(solution="The answer is just 19, no box.")
    with pytest.raises(ValueError, match="boxed"):
        transform_mathcode_instruct(row, _spec())


# ---------- math_with_tools_match verifier ----------


def test_score_record_dispatches_math_with_tools_match_boxed() -> None:
    record = {
        "environment": "math_with_tools",
        "expected_answer": "19",
        "reward_config": {"verifier": "math_with_tools_match"},
        "extra_env_info": {"has_code_block": True},
    }
    score, diagnostics = score_record(
        "Let me compute: ```python\nprint(12+7)\n```\nAnswer: \\boxed{19}.",
        record,
    )
    assert score == 1.0
    assert diagnostics["boxed_answer_extracted"] is True
    assert diagnostics["has_code_block_in_candidate"] is True


def test_score_record_math_with_tools_match_no_match() -> None:
    record = {
        "environment": "math_with_tools",
        "expected_answer": "19",
        "reward_config": {"verifier": "math_with_tools_match"},
        "extra_env_info": {"has_code_block": True},
    }
    score, diagnostics = score_record("Final answer: \\boxed{42}.", record)
    assert score == 0.0
    assert diagnostics["boxed_answer_extracted"] is True
    assert diagnostics["malformed_final_answer"] is False


def test_score_record_math_with_tools_match_falls_back_to_contains() -> None:
    """If candidate omits the `\\boxed{}` wrapper, oracle should still
    pass via whole-candidate contains-match on the gold token."""
    record = {
        "environment": "math_with_tools",
        "expected_answer": "19",
        "reward_config": {"verifier": "math_with_tools_match"},
        "extra_env_info": {"has_code_block": False},
    }
    score, diagnostics = score_record("The answer is 19.", record)
    assert score == 1.0
    assert diagnostics["boxed_answer_extracted"] is False
    assert diagnostics["malformed_final_answer"] is True


def test_score_record_math_with_tools_match_normalizes_whitespace() -> None:
    """Gold `19` should match candidate `\\boxed{ 19 }` after whitespace
    collapse."""
    record = {
        "environment": "math_with_tools",
        "expected_answer": "19",
        "reward_config": {"verifier": "math_with_tools_match"},
        "extra_env_info": {"has_code_block": False},
    }
    score, _ = score_record("Answer is \\boxed{ 19 }.", record)
    assert score == 1.0


def test_score_record_math_with_tools_match_emits_diagnostics_keys() -> None:
    """Lock the diagnostics shape — telemetry consumers depend on
    these exact keys."""
    record = {
        "environment": "math_with_tools",
        "expected_answer": "1",
        "reward_config": {"verifier": "math_with_tools_match"},
        "extra_env_info": {"has_code_block": False},
    }
    _, diagnostics = score_record("Answer: \\boxed{1}.", record)
    for key in (
        "normalized_answer",
        "boxed_answer_extracted",
        "has_code_block_in_candidate",
        "malformed_final_answer",
        "latency_ms",
    ):
        assert key in diagnostics


def test_score_record_math_with_tools_match_detects_candidate_code_block() -> None:
    """Candidate with `<python>` tag should set has_code_block_in_candidate."""
    record = {
        "environment": "math_with_tools",
        "expected_answer": "5",
        "reward_config": {"verifier": "math_with_tools_match"},
        "extra_env_info": {"has_code_block": True},
    }
    _, diagnostics = score_record(
        "<python>print(2 + 3)</python>\n\\boxed{5}",
        record,
    )
    assert diagnostics["has_code_block_in_candidate"] is True


# ---------- is_numinamath_source_id dedup helper ----------


def test_dedup_helper_returns_true_when_id_in_index() -> None:
    assert is_numinamath_source_id("nm-001", ["nm-001", "nm-002"]) is True


def test_dedup_helper_returns_false_when_id_not_in_index() -> None:
    assert is_numinamath_source_id("mci-001", ["nm-001"]) is False


def test_dedup_helper_handles_empty_source_id() -> None:
    """Empty source_id (rows without a stable id) shouldn't accidentally
    match an empty entry in the index."""
    assert is_numinamath_source_id("", ["nm-001"]) is False


def test_dedup_helper_handles_empty_index() -> None:
    assert is_numinamath_source_id("nm-001", []) is False


def test_dedup_helper_accepts_iterable_index() -> None:
    """Any Iterable[str] — generator, set, tuple — should work."""
    def gen() -> Any:
        yield "nm-001"
        yield "nm-002"
    assert is_numinamath_source_id("nm-001", gen()) is True


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_math_with_tools_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_env_registry_carries_new_math_with_tools_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "math_with_tools"),
        None,
    )
    assert env is not None
    assert env["family"] == "reasoning"
    assert env["reward"]["verifier"] == "math_with_tools_match"
    assert env["resources"]["sandbox"] == "none"
    required = env["health_check"]["required_fields"]
    assert any("has_code_block" in r for r in required)
    assert any("reference_solution" in r for r in required)


def test_env_registry_telemetry_lists_boxed_and_code_block_signals() -> None:
    """Lock the telemetry names so downstream dashboards keep working."""
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        e for e in env_registry["environments"] if e["id"] == "math_with_tools"
    )
    telemetry = env["telemetry"]
    assert "boxed_answer_extracted" in telemetry
    assert "has_code_block_in_candidate" in telemetry


def test_data_registry_does_not_yet_carry_m0_math_with_tools_row() -> None:
    """task057 Session 6 defers the data_registry row to Session 6.5
    pending real MathCodeInstruct SHA pin AND NuminaMath source_id
    index construction for cross-dataset dedup."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    rows = [
        d for d in data_registry["datasets"]
        if d["id"] == "m0_math_with_tools"
    ]
    assert rows == [], (
        "m0_math_with_tools row should NOT be in data_registry yet — "
        "Session 6.5 lands it after pinning a real commit SHA and "
        "building the NuminaMath source_id dedup index"
    )


# ---------- extract_boxed_answer round-trip (reused helper) ----------


def test_extract_boxed_answer_returns_last_when_multiple_present() -> None:
    """Sanity check that the existing helper behaves as the converter
    expects (last boxed = final answer)."""
    assert extract_boxed_answer("a \\boxed{1} b \\boxed{2}") == "2"
