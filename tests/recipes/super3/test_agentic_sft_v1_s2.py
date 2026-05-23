"""Tests for task031 Session 2 cross-harness Agentic SFT v1 routing."""

from __future__ import annotations

from pathlib import Path

from nemotron.recipes.super3.milestones.m1_agentic_sft.agentic_sft_v1 import (
    build_failure_repair_example,
    build_routed_failure_repair_examples,
    describe_agentic_sft_v1_schema,
    infer_harness_route,
)
from nemotron.recipes.super3.milestones.rollout_store import LocalRolloutStore


def _rollout(
    *,
    env_id: str,
    rollout_id: str,
    metadata: dict | None = None,
    trace: list[dict] | None = None,
) -> dict:
    return {
        "prompt_id": f"prompt-{rollout_id}",
        "model_version": "model-a@0002",
        "env_id": env_id,
        "rollout_id": rollout_id,
        "reward": 0.0,
        "terminal_reason": "failed",
        "trace": trace
        or [
            {
                "tool_name": "view_file",
                "argument_dict": {"path": "bug.py"},
                "observation": "trace observation",
            }
        ],
        "metrics": {"turn_count": 1},
        "metadata": {
            "prompt": f"Repair {rollout_id}.",
            "repair_target": f"Fixed {rollout_id}.",
            **(metadata or {}),
        },
    }


def test_schema_documents_cross_harness_routing_fields() -> None:
    metadata = describe_agentic_sft_v1_schema()["record_shape"]["metadata"]

    assert metadata["trace_harness"] == "openhands | opencode | codex | browser | terminal | generic"
    assert metadata["routing_family"] == "swe | browser | terminal | generic"
    assert metadata["cross_harness_route"] == "deterministic route contract"


def test_explicit_metadata_routes_openhands_opencode_and_codex() -> None:
    openhands = infer_harness_route(
        _rollout(
            env_id="swe_multi_harness",
            rollout_id="openhands",
            metadata={"harness": "OpenHands"},
        )
    )
    opencode = infer_harness_route(
        _rollout(
            env_id="swe_multi_harness",
            rollout_id="opencode",
            metadata={"trace_source": "open-code-local"},
        )
    )
    codex = infer_harness_route(
        _rollout(
            env_id="swe_multi_harness",
            rollout_id="codex",
            metadata={"source": "codex_cli_fixture"},
        )
    )

    assert (openhands.route_name, openhands.harness, openhands.reason) == (
        "swe_openhands_repair",
        "openhands",
        "metadata:harness",
    )
    assert (opencode.route_name, opencode.harness, opencode.source) == (
        "swe_opencode_repair",
        "opencode",
        "open_code_local",
    )
    assert (codex.route_name, codex.harness, codex.family) == (
        "swe_codex_repair",
        "codex",
        "swe",
    )


def test_env_and_tool_hints_route_browser_terminal_and_generic() -> None:
    browser = infer_harness_route(_rollout(env_id="browser_qa", rollout_id="browser"))
    terminal = infer_harness_route(_rollout(env_id="terminal_basic_shell", rollout_id="terminal"))
    tool_terminal = infer_harness_route(
        _rollout(
            env_id="unknown_env",
            rollout_id="tool-terminal",
            trace=[{"tool_name": "run_shell", "argument_dict": {"cmd": "pytest"}, "observation": "failed"}],
        )
    )
    generic = infer_harness_route(_rollout(env_id="math_reasoning_numeric", rollout_id="generic"))

    assert browser.route_name == "browser_repair"
    assert terminal.route_name == "terminal_repair"
    assert tool_terminal.route_name == "terminal_repair"
    assert generic.route_name == "generic_agentic_repair"
    assert generic.source == "local_synthetic"


def test_builder_attaches_route_metadata_without_breaking_failure_repair() -> None:
    example = build_failure_repair_example(
        _rollout(
            env_id="swe_multi_harness",
            rollout_id="route-metadata",
            metadata={"harness": "opencode", "repair_target": "Patch the failing file."},
        ),
        compact_reasoning_mode="compact",
    ).to_jsonable()

    assert example["metadata"]["trace_harness"] == "opencode"
    assert example["metadata"]["routing_family"] == "swe"
    assert example["metadata"]["route_name"] == "swe_opencode_repair"
    assert example["metadata"]["compact_reasoning_mode"] == "compact"
    assert example["metadata"]["supervision_family"] == "failure_rollout_repair"
    assert example["metadata"]["self_correction"] is True
    assert example["messages"][-1]["content"] == "Patch the failing file."


def test_routed_builder_orders_local_store_records_by_route(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_rollout(env_id="terminal_basic_shell", rollout_id="terminal"))
    store.write(_rollout(env_id="swe_multi_harness", rollout_id="codex", metadata={"source": "codex"}))
    store.write(_rollout(env_id="browser_qa", rollout_id="browser"))
    store.write(_rollout(env_id="swe_multi_harness", rollout_id="openhands", metadata={"harness": "openhands"}))
    store.write(
        dict(
            _rollout(env_id="swe_multi_harness", rollout_id="success", metadata={"harness": "opencode"}),
            reward=1.0,
            terminal_reason="solved",
        )
    )

    examples = build_routed_failure_repair_examples(store.iter_all())
    route_names = [example.to_jsonable()["metadata"]["route_name"] for example in examples]

    assert route_names == [
        "swe_openhands_repair",
        "swe_codex_repair",
        "browser_repair",
        "terminal_repair",
    ]


def test_routed_builder_filters_by_harness_or_route_name(tmp_path: Path) -> None:
    store = LocalRolloutStore(tmp_path)
    store.write(_rollout(env_id="swe_multi_harness", rollout_id="openhands", metadata={"harness": "openhands"}))
    store.write(_rollout(env_id="browser_qa", rollout_id="browser"))

    by_harness = build_routed_failure_repair_examples(store.iter_all(), route_filter="openhands")
    by_route = build_routed_failure_repair_examples(store.iter_all(), route_filter="browser_repair")

    assert [example.to_jsonable()["metadata"]["source_rollout_id"] for example in by_harness] == ["openhands"]
    assert [example.to_jsonable()["metadata"]["source_rollout_id"] for example in by_route] == ["browser"]
