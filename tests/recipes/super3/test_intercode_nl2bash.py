"""Tests for the intercode-nl2bash tier-2 converter (task057 Session 4).

Covers:

- `transform_intercode_nl2bash` happy path: nl + cmd → terminal_basic_shell
  record with command_substring_match verifier
- Alternate column conventions: nl/instruction/prompt for instruction;
  cmd/bash/command/response for the gold command
- M0 smoke cap: rows above `INTERCODE_NL2BASH_MAX_CMD_CHARS` (200) are
  rejected (drop nightmare rows; truncation changes shell semantics)
- `extra_env_info.source_dataset_kind` tagged as
  `intercode_nl2bash_tier2` for downstream stratification
- Error surfaces: missing instruction / missing command
- `normalize_command_text` enhancements: double-quote → single-quote
  canonicalization survives existing fenced-code-block + whitespace
  collapsing
- Registry integration: converter wired into CONVERTERS; data_registry
  row deferred (Session 4.5)
- Back-compat: existing tier-1 `transform_bash_command` still works
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
    INTERCODE_NL2BASH_MAX_CMD_CHARS,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_bash_command,
    transform_intercode_nl2bash,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    normalize_command_text,
    score_command,
    score_record,
)


def _spec(dataset_id: str = "m0_terminal_intercode") -> dict:
    """Build a synthetic spec for the intercode tier-2 source.

    The m0_terminal_intercode data_registry row is deferred (Session 4.5);
    tests use a synthetic spec for the existing terminal_basic_shell env."""
    return {
        "id": dataset_id,
        "environment": "terminal_basic_shell",
        "domain": "terminal",
        "hf_dataset": "epinnock/intercode-nl2bash-curated",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": "validation",
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://huggingface.co/datasets/epinnock/intercode-nl2bash-curated",
        "license": "cc-by-4.0",
        "converter": "intercode_nl2bash",
        "difficulty": "nl2bash_tier2",
        "reward_type": "command_substring_match",
        "contamination": "synthetic test spec",
        "contamination_against": ["TerminalBench"],
        "milestone": "M0",
        "use_stage": ["M0 data_env_foundation"],
    }


def _row(
    *,
    instruction: str = "List all .txt files in the current directory.",
    command: str = "ls *.txt",
    nl_key: str = "nl",
    cmd_key: str = "cmd",
) -> dict[str, Any]:
    return {nl_key: instruction, cmd_key: command}


# ---------- Module surface ----------


def test_max_cmd_chars_is_200_per_readme() -> None:
    """Lock the M0 smoke cap so a future drift is intentional."""
    assert INTERCODE_NL2BASH_MAX_CMD_CHARS == 200


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("intercode_nl2bash") is transform_intercode_nl2bash


def test_existing_bash_command_converter_still_registered() -> None:
    """Back-compat: tier-1 path remains."""
    assert CONVERTERS.get("bash_command") is transform_bash_command


# ---------- Happy path ----------


def test_transform_emits_record_for_intercode_native_format() -> None:
    row = _row(instruction="Find all txt files.", command="find . -name '*.txt'")
    record = transform_intercode_nl2bash(row, _spec())
    assert record["environment"] == "terminal_basic_shell"
    assert record["question"] == "Find all txt files."
    assert record["expected_answer"] == "find . -name '*.txt'"
    assert record["reward_config"]["verifier"] == "command_substring_match"


def test_transform_carries_source_dataset_kind_for_stratification() -> None:
    """Tier-1 vs tier-2 split needs to survive into M1 SFT prep so the
    health baseline can break down by data source."""
    record = transform_intercode_nl2bash(_row(), _spec())
    assert record["extra_env_info"]["source_dataset_kind"] == "intercode_nl2bash_tier2"


def test_transform_records_cmd_length_chars_for_telemetry() -> None:
    cmd = "ls *.txt"
    record = transform_intercode_nl2bash(_row(command=cmd), _spec())
    assert record["extra_env_info"]["cmd_length_chars"] == len(cmd)


# ---------- Alternate column conventions ----------


@pytest.mark.parametrize("nl_key", ["nl", "instruction", "prompt"])
def test_transform_accepts_each_instruction_key(nl_key: str) -> None:
    row = {nl_key: "List files.", "cmd": "ls"}
    record = transform_intercode_nl2bash(row, _spec())
    assert record["question"] == "List files."


@pytest.mark.parametrize("cmd_key", ["cmd", "bash", "command", "response"])
def test_transform_accepts_each_command_key(cmd_key: str) -> None:
    row = {"nl": "List files.", cmd_key: "ls -la"}
    record = transform_intercode_nl2bash(row, _spec())
    assert record["expected_answer"] == "ls -la"


# ---------- M0 smoke cap ----------


def test_transform_rejects_command_exceeding_smoke_cap() -> None:
    long_cmd = "echo " + "x" * INTERCODE_NL2BASH_MAX_CMD_CHARS
    row = _row(command=long_cmd)
    with pytest.raises(ValueError, match="exceeds M0 smoke cap"):
        transform_intercode_nl2bash(row, _spec())


def test_transform_accepts_command_exactly_at_cap() -> None:
    """Strict > cap means a row exactly at the cap passes."""
    cmd = "x" * INTERCODE_NL2BASH_MAX_CMD_CHARS
    record = transform_intercode_nl2bash(_row(command=cmd), _spec())
    assert record["extra_env_info"]["cmd_length_chars"] == INTERCODE_NL2BASH_MAX_CMD_CHARS


# ---------- Error surfaces ----------


def test_transform_rejects_missing_instruction() -> None:
    row = {"cmd": "ls"}
    with pytest.raises(ValueError, match="instruction"):
        transform_intercode_nl2bash(row, _spec())


def test_transform_rejects_missing_command() -> None:
    row = {"nl": "List files."}
    with pytest.raises(ValueError, match="gold command"):
        transform_intercode_nl2bash(row, _spec())


# ---------- normalize_command_text enhancement ----------


def test_normalize_command_text_canonicalizes_double_to_single_quotes() -> None:
    """task057 Session 4 enhancement: shell-equivalent quotes should
    compare equal so tier-2 stylistic differences don't false-negative
    the oracle baseline."""
    assert (
        normalize_command_text('find . -name "*.txt"')
        == normalize_command_text("find . -name '*.txt'")
    )


def test_normalize_command_text_still_collapses_whitespace() -> None:
    """Back-compat: existing behaviour preserved."""
    assert normalize_command_text("ls    -la\n") == "ls -la"


def test_normalize_command_text_still_extracts_fenced_code_block() -> None:
    """Back-compat: fenced code block extraction unchanged."""
    text = "Here's the command:\n```bash\nls -la\n```"
    assert normalize_command_text(text) == "ls -la"


def test_score_command_passes_for_mixed_quote_styles() -> None:
    """End-to-end: model emits double-quoted, gold has single-quoted —
    they should still match under the new normalization."""
    score = score_command('find . -name "*.txt"', "find . -name '*.txt'")
    assert score == 1.0


def test_score_record_dispatches_command_substring_match() -> None:
    """Sanity-check the dispatch path against the intercode shape."""
    record = {
        "environment": "terminal_basic_shell",
        "expected_answer": "ls -la",
        "reward_config": {"verifier": "command_substring_match"},
        "extra_env_info": {"expected_command": "ls -la"},
    }
    score, diagnostics = score_record("ls -la", record)
    assert score == 1.0
    assert diagnostics["command_match"] is True


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_intercode_converter() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_system_prompt_for_terminal_basic_shell_unchanged() -> None:
    """Sanity: env reused from tier-1; SYSTEM_PROMPTS entry preserved."""
    assert "terminal_basic_shell" in SYSTEM_PROMPTS


def test_data_registry_does_not_yet_carry_m0_terminal_intercode_row() -> None:
    """task057 Session 4 defers the data_registry row to Session 4.5
    pending a real intercode-nl2bash commit SHA pin. Lock the deferral."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    rows = [d for d in data_registry["datasets"] if d["id"] == "m0_terminal_intercode"]
    assert rows == [], (
        "m0_terminal_intercode row should NOT be in data_registry yet — "
        "pin intercode-nl2bash commit SHA first"
    )


# ---------- Back-compat for tier-1 ----------


def test_existing_aelhalili_tier1_row_unchanged_in_registry() -> None:
    """task057 Session 4 only ADDS a tier-2 converter; tier-1 row +
    converter stay intact (regression guard)."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    tier1 = next(
        (d for d in data_registry["datasets"] if d["id"] == "m0_terminal_bash_commands"),
        None,
    )
    assert tier1 is not None
    assert tier1["converter"] == "bash_command"
    assert tier1["hf_dataset"] == "aelhalili/bash-commands-dataset"
