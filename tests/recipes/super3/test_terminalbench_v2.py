"""Tests for TerminalBench v2 -> terminal_workplace scaffold.

Session 1 intentionally stays sandbox-runnable: it defines the record
contract, registry shape, and verifier metadata without running a real
TerminalBench container/cluster smoke.
"""

from __future__ import annotations

from typing import Any

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SYSTEM_PROMPTS,
    TERMINAL_WORKPLACE_DEFAULT_TIMEOUT_S,
    TERMINAL_WORKPLACE_TIMEOUT_PROFILE,
    load_yaml,
    transform_terminalbench_v2,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)
from nemotron.recipes.super3.milestones.sandbox_containers.image_resolver import (  # noqa: E402
    resolve_image_for_env,
)


def _spec() -> dict[str, Any]:
    return {
        "id": "m2_terminalbench_v2_s1",
        "environment": "terminal_workplace",
        "domain": "terminal",
        "hf_dataset": "terminal-bench/terminal-bench-v2",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": "validation",
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://terminalbench.com/",
        "license": "unknown-pending-review",
        "converter": "terminalbench_v2",
        "difficulty": "terminal_workplace",
        "reward_type": "command_substring_match",
        "contamination": "synthetic test spec",
        "contamination_against": ["TerminalBench"],
        "milestone": "M2",
        "use_stage": ["M2 terminalbench scaffold"],
        "default_timeout_s": TERMINAL_WORKPLACE_DEFAULT_TIMEOUT_S,
    }


def _row(
    *,
    instruction_key: str = "instruction",
    command_key: str = "expected_command",
    timeout_s: int | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "task_id": "tb-v2-001",
        instruction_key: "Find every markdown file under the repo root.",
        command_key: "find . -name '*.md'",
        "category": "filesystem",
        "difficulty": "easy",
    }
    if timeout_s is not None:
        row["timeout_s"] = timeout_s
    return row


def test_converter_is_registered() -> None:
    assert CONVERTERS["terminalbench_v2"] is transform_terminalbench_v2


def test_system_prompt_for_terminal_workplace_exists() -> None:
    assert "terminal_workplace" in SYSTEM_PROMPTS
    assert "terminal workplace" in SYSTEM_PROMPTS["terminal_workplace"]


def test_transform_emits_terminal_workplace_record() -> None:
    record = transform_terminalbench_v2(_row(), _spec())
    assert record["environment"] == "terminal_workplace"
    assert record["question"] == "Find every markdown file under the repo root."
    assert record["expected_answer"] == "find . -name '*.md'"
    assert record["reward_config"]["verifier"] == "command_substring_match"
    assert record["reward_config"]["timeout_s"] == TERMINAL_WORKPLACE_DEFAULT_TIMEOUT_S
    assert record["reward_config"]["timeout_profile"] == TERMINAL_WORKPLACE_TIMEOUT_PROFILE


def test_transform_carries_explicit_extended_timeout_metadata() -> None:
    record = transform_terminalbench_v2(_row(timeout_s=420), _spec())
    assert record["extra_env_info"]["extended_timeout_s"] == 420
    assert record["extra_env_info"]["timeout_profile"] == TERMINAL_WORKPLACE_TIMEOUT_PROFILE
    assert record["extra_env_info"]["cluster_execution"]["required"] is False
    assert record["extra_env_info"]["terminalbench_task_id"] == "tb-v2-001"


@pytest.mark.parametrize("instruction_key", ["instruction", "prompt", "task", "description", "question"])
def test_transform_accepts_instruction_aliases(instruction_key: str) -> None:
    record = transform_terminalbench_v2(_row(instruction_key=instruction_key), _spec())
    assert record["question"] == "Find every markdown file under the repo root."


@pytest.mark.parametrize(
    "command_key",
    [
        "expected_command",
        "gold_command",
        "reference_command",
        "command",
        "cmd",
        "solution",
        "answer",
    ],
)
def test_transform_accepts_command_aliases(command_key: str) -> None:
    record = transform_terminalbench_v2(_row(command_key=command_key), _spec())
    assert record["expected_answer"] == "find . -name '*.md'"


def test_transform_rejects_missing_instruction() -> None:
    row = {"expected_command": "ls"}
    with pytest.raises(ValueError, match="missing instruction"):
        transform_terminalbench_v2(row, _spec())


def test_transform_rejects_missing_command() -> None:
    row = {"instruction": "List files."}
    with pytest.raises(ValueError, match="missing gold command"):
        transform_terminalbench_v2(row, _spec())


def test_score_record_reuses_command_substring_match_with_timeout_metadata() -> None:
    record = transform_terminalbench_v2(_row(timeout_s=420), _spec())
    score, diagnostics = score_record('find . -name "*.md"', record)
    assert score == 1.0
    assert diagnostics["command_match"] is True
    assert diagnostics["timeout_s"] == 420
    assert diagnostics["timeout_profile"] == TERMINAL_WORKPLACE_TIMEOUT_PROFILE


def test_registry_consistency_holds_after_terminal_workplace_env_addition() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)
    env = next(e for e in env_registry["environments"] if e["id"] == "terminal_workplace")
    assert env["reward"]["verifier"] == "command_substring_match"
    assert env["resources"]["timeout_s"] == TERMINAL_WORKPLACE_DEFAULT_TIMEOUT_S
    assert env["resources"]["sandbox"] == "terminal"


def test_terminal_workplace_resolves_to_terminal_sandbox_image() -> None:
    assert resolve_image_for_env("terminal_workplace") == "terminal:v0.1.0"
