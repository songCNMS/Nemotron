"""Tests for the SWE-Gym-Lite → swe2_openhands_trace converter (task017 Session 2).

Covers:

- ``transform_swe_gym_openhands_trace`` happy path on a synthetic
  SWE-Gym trajectory (full trajectory preserved, gold patch extracted,
  openhands_loop reward, sif_source defaulted to swegym).
- Patch resolution: prefer top-level ``patch`` / ``gold_patch`` field;
  fall back to trajectory ``submit_patch`` tool call; raise when both
  paths fail.
- Trajectory normalization: tool_call arguments decoded to dict
  regardless of JSON-string vs dict upstream serialization.
- Error surfaces: missing problem_statement / missing messages / no
  patch anywhere.
- Registry integration: ``m0_swe2_openhands_trace`` row +
  ``swe2_openhands_trace`` env row + converter wired into CONVERTERS;
  ``validate_registries`` clean.
- SWE2 bridge ``SWE2_ENV_MAP`` lights up with the new active mapping.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SWE2_OPENHANDS_TOOLS,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_swe_gym_openhands_trace,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m1_swe2.prepare_m1_swe2_jsonl import (  # noqa: E402
    SWE2_ENV_MAP,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def _spec(dataset_id: str) -> dict:
    registry = load_yaml(DATA_REGISTRY_PATH)
    for dataset in registry["datasets"]:
        if dataset["id"] == dataset_id:
            spec = dict(dataset)
            spec["milestone"] = registry["milestone"]
            return spec
    raise AssertionError(f"missing dataset {dataset_id}")


_GOLD_PATCH = (
    "diff --git a/src/parser.py b/src/parser.py\n"
    "--- a/src/parser.py\n"
    "+++ b/src/parser.py\n"
    "@@ -1,2 +1,2 @@\n"
    "-old\n+new\n"
)


def _swe_gym_trace_row(
    *,
    instance_id: str = "owner__repo-42",
    repo: str = "owner/repo",
    problem_statement: str = "Fix the parser to handle trailing commas.",
    gold_patch: str | None = _GOLD_PATCH,
    top_level_field: str = "patch",
    submit_patch_arguments: dict | str | None = None,
    messages_extra: list[dict] | None = None,
) -> dict:
    """Construct a synthetic SWE-Gym trajectory row."""
    messages = [
        {"role": "system", "content": "You are a SWE agent..."},
        {"role": "user", "content": problem_statement},
        {
            "role": "assistant",
            "content": "Let me check the parser.",
            "tool_calls": [
                {
                    "id": "call_0",
                    "type": "function",
                    "function": {
                        "name": "view_file",
                        "arguments": json.dumps({"path": "src/parser.py"}),
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_0", "content": "...file contents..."},
        {
            "role": "assistant",
            "content": "Now I'll fix it.",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "edit_file",
                        "arguments": json.dumps({
                            "path": "src/parser.py",
                            "old_text": "old",
                            "new_text": "new",
                        }),
                    },
                }
            ],
        },
    ]
    if submit_patch_arguments is not None:
        if isinstance(submit_patch_arguments, dict):
            args_payload = json.dumps(submit_patch_arguments)
        else:
            args_payload = submit_patch_arguments
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_submit",
                        "type": "function",
                        "function": {
                            "name": "submit_patch",
                            "arguments": args_payload,
                        },
                    }
                ],
            }
        )
    if messages_extra:
        messages.extend(messages_extra)

    row: dict = {
        "instance_id": instance_id,
        "repo": repo,
        "problem_statement": problem_statement,
        "messages": messages,
    }
    if gold_patch is not None:
        row[top_level_field] = gold_patch
    return row


# ---------- Module surface ----------


def test_system_prompt_for_swe2_openhands_trace_exists() -> None:
    assert "swe2_openhands_trace" in SYSTEM_PROMPTS
    assert "OpenHands" in SYSTEM_PROMPTS["swe2_openhands_trace"]


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("swe_gym_openhands_trace") is transform_swe_gym_openhands_trace


def test_swe2_openhands_tools_includes_submit_patch_and_run_shell() -> None:
    """SWE2 tools are richer than SWE1's pivot tools — agent needs full
    rollout capability (run_shell, run_tests, submit_patch)."""
    names = {t["function"]["name"] for t in SWE2_OPENHANDS_TOOLS}
    assert {"view_file", "search", "edit_file", "run_shell", "run_tests", "submit_patch"} <= names


# ---------- Happy path ----------


def test_transform_preserves_full_reference_trajectory() -> None:
    """Unlike SWE1 (first tool call only), SWE2 must keep every
    assistant + tool message so the policy can imitate / be judged
    against the whole rollout."""
    row = _swe_gym_trace_row()
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    trajectory = record["extra_env_info"]["reference_trajectory"]
    assert record["extra_env_info"]["trajectory_turns"] == len(trajectory) == len(row["messages"])
    # Tool-call arguments must be dicts (normalised from JSON strings)
    assistant_calls = [m for m in trajectory if m["role"] == "assistant" and m.get("tool_calls")]
    for message in assistant_calls:
        for call in message["tool_calls"]:
            assert isinstance(call["arguments"], dict)


def test_transform_extracts_gold_patch_from_top_level_patch_field() -> None:
    row = _swe_gym_trace_row(top_level_field="patch")
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    assert record["expected_answer"].startswith("diff --git")
    assert record["extra_env_info"]["gold_patch"] == record["expected_answer"]


def test_transform_extracts_gold_patch_from_gold_patch_field() -> None:
    """Some upstream snapshots use ``gold_patch`` instead of ``patch``."""
    row = _swe_gym_trace_row(top_level_field="gold_patch")
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    assert record["expected_answer"].startswith("diff --git")


def test_transform_emits_openhands_loop_verifier_and_full_tool_schema() -> None:
    row = _swe_gym_trace_row()
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    assert record["environment"] == "swe2_openhands_trace"
    assert record["reward_config"]["verifier"] == "openhands_loop"
    assert record["reward_config"]["match"] == ["patch_applies", "tests_pass"]
    names = {t["function"]["name"] for t in record["responses_create_params"]["tools"]}
    assert names == {
        "view_file",
        "search",
        "edit_file",
        "run_shell",
        "run_tests",
        "submit_patch",
    }


def test_transform_carries_sif_source_swegym_by_default() -> None:
    """Default sif_source is `swegym` since SWE-Gym is the upstream;
    operators with R2E-Gym sources override via spec or downstream tag."""
    row = _swe_gym_trace_row()
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    assert record["extra_env_info"]["sif_source"] == "swegym"


def test_transform_respects_explicit_sif_source_on_row() -> None:
    """If the row carries an explicit sif_source (mixed-family corpus),
    the converter preserves it instead of defaulting."""
    row = _swe_gym_trace_row()
    row["sif_source"] = "r2egym"
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    assert record["extra_env_info"]["sif_source"] == "r2egym"


# ---------- Patch fallback ----------


def test_transform_falls_back_to_submit_patch_tool_call_when_top_level_missing() -> None:
    """No top-level patch field — patch lives in a trajectory
    ``submit_patch`` tool call. The converter should still locate it."""
    row = _swe_gym_trace_row(
        gold_patch=None,
        submit_patch_arguments={"patch": "diff --git a/x b/x\n@@ -1 +1 @@\n-a\n+b\n"},
    )
    record = transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))
    assert "diff --git a/x b/x" in record["expected_answer"]


# ---------- Error surfaces ----------


def test_transform_raises_when_problem_statement_missing() -> None:
    row = _swe_gym_trace_row()
    row["problem_statement"] = ""
    with pytest.raises(ValueError, match="problem_statement"):
        transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))


def test_transform_raises_when_messages_missing() -> None:
    with pytest.raises(ValueError, match="messages trajectory"):
        transform_swe_gym_openhands_trace(
            {"instance_id": "x", "repo": "r", "problem_statement": "fix"},
            _spec("m0_swe2_openhands_trace"),
        )


def test_transform_raises_when_no_patch_anywhere() -> None:
    """Without a gold patch the openhands_loop reward signal degenerates —
    the converter must fail loudly instead of emitting a useless row."""
    row = _swe_gym_trace_row(gold_patch=None)  # also no submit_patch in messages
    with pytest.raises(ValueError, match="no gold patch"):
        transform_swe_gym_openhands_trace(row, _spec("m0_swe2_openhands_trace"))


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_swe2_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_data_registry_carries_new_swe2_openhands_trace_row() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    row = next(
        (d for d in data_registry["datasets"] if d["id"] == "m0_swe2_openhands_trace"),
        None,
    )
    assert row is not None
    assert row["environment"] == "swe2_openhands_trace"
    assert row["converter"] == "swe_gym_openhands_trace"
    assert row["hf_dataset"] == "SWE-Gym/SWE-Gym-Lite"
    assert row["reward_type"] == "openhands_loop"
    assert "SWE-Bench Verified" in row["contamination_against"]


def test_env_registry_carries_new_swe2_openhands_trace_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "swe2_openhands_trace"),
        None,
    )
    assert env is not None
    assert env["reward"]["verifier"] == "openhands_loop"
    assert env["resources"]["sandbox"] == "sif"
    assert env["resources"]["max_turns"] == 200


def test_swe2_env_map_lights_up_post_task017_session_2() -> None:
    """swe2_env_registry.yaml's `swegym` row flipped from m0_missing to
    active in this session — the bridge's auto-derived SWE2_ENV_MAP
    now carries the mapping. Previously asserted-empty in
    test_swe2_env_map_empty_today (flipped to lock the active state)."""
    assert SWE2_ENV_MAP == {"swe2_openhands_trace": "swe_agents"}
