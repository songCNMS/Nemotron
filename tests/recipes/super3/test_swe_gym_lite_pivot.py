"""Tests for the SWE-Gym-Lite → swe_pivot_tool_call converter (task016 Session 2).

Covers:

- ``transform_swe_gym_lite_pivot`` happy path on a synthetic SWE-Gym
  trajectory (first assistant tool call → expected_answer, argument_match
  reward, repo / instance_id metadata).
- First-tool-call selection: pick the *first* assistant message that
  carries ``tool_calls`` (skipping system / user / assistant-no-tool messages).
- pivot_type classification: exploration (view_file / search / ...) vs
  action (edit_file / run_tests / ...).
- Arguments normalization: JSON-string args and dict args both decode
  to a real dict on the output side.
- Error surfaces: missing problem_statement / missing messages / no
  tool calls in trajectory / malformed JSON arguments.
- Patch-only public SWE-Gym-Lite rows synthesize a read-only first
  pivot from the first modified file in the gold patch.
- Registry integration: ``m0_swe_pivot_tool_call`` row + new
  ``swe_pivot_tool_call`` env row both validate; converter is wired
  into ``CONVERTERS``.
- SWE1 bridge auto-picks up the active row (verified separately in
  test_m1_swe1_data_bridge.py — that suite's previous "today no
  active env" tests have been flipped here as part of Session 2).
"""

from __future__ import annotations

import json

import pytest

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SWE_PIVOT_EXPLORATION_TOOLS,
    SWE_PIVOT_TOOLS,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_swe_gym_lite_pivot,
    validate_registries,
)


def _spec(dataset_id: str) -> dict:
    registry = load_yaml(DATA_REGISTRY_PATH)
    for dataset in registry["datasets"]:
        if dataset["id"] == dataset_id:
            spec = dict(dataset)
            spec["milestone"] = registry["milestone"]
            return spec
    raise AssertionError(f"missing dataset {dataset_id}")


def _swe_gym_row(
    *,
    instance_id: str = "owner__repo-42",
    repo: str = "owner/repo",
    problem_statement: str = "Fix the bug where the parser drops trailing commas.",
    first_tool_name: str = "edit_file",
    first_tool_arguments: dict | str | None = None,
    preceding_messages: list[dict] | None = None,
    trailing_messages: list[dict] | None = None,
) -> dict:
    """Construct a synthetic SWE-Gym-Lite row.

    Layout follows the OpenAI agent trace convention SWE-Gym uses:
    ``messages`` is a list of {role, content?, tool_calls?, tool_call_id?}
    dicts; the first assistant message carrying ``tool_calls`` is the
    "pivot" the converter extracts.
    """
    if first_tool_arguments is None:
        first_tool_arguments = {"path": "src/parser.py", "old_text": "a", "new_text": "b"}
    if isinstance(first_tool_arguments, dict):
        arguments_payload = json.dumps(first_tool_arguments)
    else:
        arguments_payload = first_tool_arguments
    messages = list(preceding_messages or [
        {"role": "system", "content": "You are a SWE agent..."},
        {"role": "user", "content": problem_statement},
    ])
    messages.append(
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_0",
                    "type": "function",
                    "function": {
                        "name": first_tool_name,
                        "arguments": arguments_payload,
                    },
                }
            ],
        }
    )
    messages.extend(trailing_messages or [])
    return {
        "instance_id": instance_id,
        "repo": repo,
        "problem_statement": problem_statement,
        "messages": messages,
    }


# ---------- Module surface ----------


def test_system_prompt_for_swe_pivot_tool_call_exists() -> None:
    assert "swe_pivot_tool_call" in SYSTEM_PROMPTS
    assert "single next tool call" in SYSTEM_PROMPTS["swe_pivot_tool_call"]


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("swe_gym_lite_pivot") is transform_swe_gym_lite_pivot


def test_swe_pivot_tools_schema_lists_four_function_tools() -> None:
    """Lock the tool universe so the policy sees a stable schema —
    expanding it later is M2 territory."""
    names = {t["function"]["name"] for t in SWE_PIVOT_TOOLS}
    assert names == {"view_file", "search", "edit_file", "run_tests"}
    for tool in SWE_PIVOT_TOOLS:
        assert tool["type"] == "function"
        assert "parameters" in tool["function"]


def test_exploration_tool_set_includes_view_and_search() -> None:
    assert "view_file" in SWE_PIVOT_EXPLORATION_TOOLS
    assert "search" in SWE_PIVOT_EXPLORATION_TOOLS
    # Action-class tools must not be in the exploration set
    assert "edit_file" not in SWE_PIVOT_EXPLORATION_TOOLS
    assert "run_tests" not in SWE_PIVOT_EXPLORATION_TOOLS


# ---------- Happy path ----------


def test_transform_extracts_first_tool_call_as_expected_answer() -> None:
    row = _swe_gym_row(first_tool_name="edit_file")
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))

    assert record["environment"] == "swe_pivot_tool_call"
    assert record["reward_config"]["verifier"] == "argument_match"
    assert record["reward_config"]["match"] == ["name", "arguments"]
    gold = record["expected_answer"]
    assert gold["name"] == "edit_file"
    assert isinstance(gold["arguments"], dict)
    assert gold["arguments"]["path"] == "src/parser.py"
    assert record["extra_env_info"]["gold_tool_call"] == gold


def test_transform_sets_pivot_type_to_action_for_edit_file() -> None:
    row = _swe_gym_row(first_tool_name="edit_file")
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))
    assert record["extra_env_info"]["pivot_type"] == "action"


def test_transform_sets_pivot_type_to_exploration_for_view_file() -> None:
    """Pure exploration pivots must be emitted (not skipped) and tagged
    so downstream filters can distinguish them from action pivots."""
    row = _swe_gym_row(
        first_tool_name="view_file",
        first_tool_arguments={"path": "src/main.py"},
    )
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))
    assert record["extra_env_info"]["pivot_type"] == "exploration"


def test_transform_emits_swe_tool_schema_in_responses_create_params() -> None:
    row = _swe_gym_row()
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))
    tools = record["responses_create_params"]["tools"]
    names = {t["function"]["name"] for t in tools}
    assert names == {"view_file", "search", "edit_file", "run_tests"}


def test_transform_carries_repo_and_instance_id_into_extra_env_info() -> None:
    row = _swe_gym_row(instance_id="myrepo__issue-1", repo="org/myrepo")
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))
    assert record["extra_env_info"]["repo"] == "org/myrepo"
    assert record["extra_env_info"]["instance_id"] == "myrepo__issue-1"


def test_transform_synthesizes_view_file_pivot_from_patch_only_swegym_lite_row() -> None:
    """The pinned public SWE-Gym-Lite snapshot is patch-only (no
    ``messages`` trajectory). Data prep must still emit a usable SWE1
    pivot row instead of erroring every source row."""
    row = {
        "instance_id": "owner__repo-42",
        "repo": "owner/repo",
        "problem_statement": "Fix the parser.",
        "patch": (
            "diff --git a/src/parser.py b/src/parser.py\n"
            "--- a/src/parser.py\n"
            "+++ b/src/parser.py\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n"
        ),
    }
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))

    assert record["expected_answer"] == {
        "name": "view_file",
        "arguments": {"path": "src/parser.py"},
    }
    assert record["extra_env_info"]["pivot_type"] == "exploration"
    assert record["extra_env_info"]["pivot_source"] == "synthetic_from_gold_patch"


# ---------- First-tool-call selection ----------


def test_transform_skips_non_assistant_messages_to_find_first_tool_call() -> None:
    """If the trajectory has multiple turns, the converter must skip
    system / user / assistant-no-tool messages to find the first
    assistant message that emitted tool_calls."""
    row = _swe_gym_row(
        first_tool_name="run_tests",
        first_tool_arguments={"path": "tests/test_parser.py"},
        preceding_messages=[
            {"role": "system", "content": "..."},
            {"role": "user", "content": "Look at this bug..."},
            {"role": "assistant", "content": "Let me check the parser."},
            {"role": "user", "content": "Continue."},
        ],
    )
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))
    assert record["expected_answer"]["name"] == "run_tests"
    assert record["expected_answer"]["arguments"]["path"] == "tests/test_parser.py"


def test_transform_picks_first_tool_call_when_assistant_emits_multiple() -> None:
    """A single assistant message may carry multiple parallel tool_calls;
    the converter picks the first as the pivot."""
    row = {
        "instance_id": "x",
        "repo": "r",
        "problem_statement": "fix",
        "messages": [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"id": "call_0", "type": "function",
                     "function": {"name": "view_file",
                                  "arguments": json.dumps({"path": "a.py"})}},
                    {"id": "call_1", "type": "function",
                     "function": {"name": "edit_file",
                                  "arguments": json.dumps({"path": "a.py", "old_text": "x", "new_text": "y"})}},
                ],
            }
        ],
    }
    record = transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))
    assert record["expected_answer"]["name"] == "view_file"


# ---------- Arguments normalization ----------


def test_transform_accepts_arguments_as_already_parsed_dict() -> None:
    """OpenAI's spec stores ``arguments`` as a JSON string, but some
    upstreams (and downstream caches) hand back the parsed dict
    directly. The converter must handle both."""
    raw_row = {
        "instance_id": "x",
        "repo": "r",
        "problem_statement": "fix",
        "messages": [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_0",
                        "type": "function",
                        "function": {
                            "name": "search",
                            "arguments": {"query": "TODO"},
                        },
                    }
                ],
            }
        ],
    }
    record = transform_swe_gym_lite_pivot(raw_row, _spec("m0_swe_pivot_tool_call"))
    assert record["expected_answer"]["arguments"] == {"query": "TODO"}


def test_transform_accepts_empty_string_arguments_as_no_args() -> None:
    """run_tests with no path argument is legal; arguments=null should
    decode to {} rather than crash."""
    raw_row = {
        "instance_id": "x",
        "repo": "r",
        "problem_statement": "fix",
        "messages": [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_0",
                        "type": "function",
                        "function": {
                            "name": "run_tests",
                            "arguments": None,
                        },
                    }
                ],
            }
        ],
    }
    record = transform_swe_gym_lite_pivot(raw_row, _spec("m0_swe_pivot_tool_call"))
    assert record["expected_answer"]["arguments"] == {}


# ---------- Error surfaces ----------


def test_transform_raises_when_problem_statement_missing() -> None:
    row = _swe_gym_row(problem_statement="")
    with pytest.raises(ValueError, match="problem_statement"):
        transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))


def test_transform_raises_when_messages_field_missing() -> None:
    row = {"instance_id": "x", "repo": "r", "problem_statement": "fix"}
    with pytest.raises(ValueError, match="messages trajectory and patch fallback"):
        transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))


def test_transform_raises_when_no_assistant_tool_calls_in_trajectory() -> None:
    row = {
        "instance_id": "x",
        "repo": "r",
        "problem_statement": "fix",
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "I can't determine what to do."},
        ],
    }
    with pytest.raises(ValueError, match="no assistant message with tool_calls"):
        transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))


def test_transform_raises_on_malformed_json_arguments() -> None:
    row = _swe_gym_row(first_tool_arguments='{"path": "a.py", "old_text"')  # truncated JSON
    with pytest.raises(ValueError, match="malformed JSON arguments"):
        transform_swe_gym_lite_pivot(row, _spec("m0_swe_pivot_tool_call"))


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_swe_pivot_tool_call_env() -> None:
    """Adding the new env + data row + converter must keep
    `validate_registries` green — env IDs match, converter is wired,
    contamination_against is a non-empty list."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_data_registry_carries_new_swe_pivot_tool_call_row() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    row = next(
        (d for d in data_registry["datasets"] if d["id"] == "m0_swe_pivot_tool_call"),
        None,
    )
    assert row is not None, "data_registry missing m0_swe_pivot_tool_call row"
    assert row["environment"] == "swe_pivot_tool_call"
    assert row["converter"] == "swe_gym_lite_pivot"
    assert row["hf_dataset"] == "SWE-Gym/SWE-Gym-Lite"
    assert row["hf_revision"] == "f70b1a29ab120eb0a0ee7a1deb029825e735b2b0"
    assert row["hf_val_split"] is None
    assert row["reward_type"] == "argument_match"
    assert "SWE-Bench Lite" in row["contamination_against"]


def test_env_registry_carries_new_swe_pivot_tool_call_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "swe_pivot_tool_call"),
        None,
    )
    assert env is not None, "environment_registry missing swe_pivot_tool_call env"
    assert env["family"] == "software_engineering"
    assert env["reward"]["verifier"] == "argument_match"
    assert env["resources"]["max_turns"] == 1
