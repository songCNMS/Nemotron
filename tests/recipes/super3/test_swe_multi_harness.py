"""Tests for task026 Session 1 SWE multi-harness scaffold."""

from __future__ import annotations

from pathlib import Path

import pytest

from nemotron.recipes.super3.milestones.m1_swe2.swe_multi_harness import (
    ADAPTER_DECLARATIONS,
    HARNESS_CODEX,
    HARNESS_OPENCODE,
    HARNESS_OPENHANDS,
    KNOWN_HARNESS_IDS,
    REGISTRY_PATH,
    STATUS_PROTOCOL_READY,
    STATUS_SANDBOX_DECLARED,
    CodexLoopAdapter,
    OpenCodeLoopAdapter,
    build_harness_routes,
    load_swe_harness_registry,
    route_for_harness,
)
from nemotron.recipes.super3.milestones.m1_swe2.openhands_loop import Instance


def test_swe_harness_registry_loads_openhands_opencode_codex() -> None:
    rows = load_swe_harness_registry()
    harnesses = {row["harness_id"] for row in rows}
    assert harnesses == {HARNESS_OPENHANDS, HARNESS_OPENCODE, HARNESS_CODEX}
    assert harnesses <= KNOWN_HARNESS_IDS


def test_swe_harness_registry_path_lives_beside_openhands_loop() -> None:
    assert REGISTRY_PATH.is_file()
    assert REGISTRY_PATH.parent.name == "m1_swe2"
    assert (REGISTRY_PATH.parent / "openhands_loop.py").is_file()


def test_openhands_route_preserves_task070_protocol_path() -> None:
    route = route_for_harness(HARNESS_OPENHANDS)
    assert route.status == STATUS_PROTOCOL_READY
    assert route.nemo_gym_env == "swe_agents"
    assert route.mix == "swe2"
    assert route.m0_env_id == "swe2_openhands_trace"
    assert route.sif_source == "swegym"
    assert route.adapter_class.endswith("m1_swe2.openhands_loop.OpenHandsLoop")
    assert route.config_path.endswith("swebench_openhands_training.yaml")


def test_opencode_and_codex_are_sandbox_declarations_with_cluster_followup() -> None:
    routes = build_harness_routes()
    for harness_id in (HARNESS_OPENCODE, HARNESS_CODEX):
        route = routes[harness_id]
        declaration = ADAPTER_DECLARATIONS[harness_id]
        assert route.status == STATUS_SANDBOX_DECLARED
        assert route.adapter_class == declaration.adapter_class
        assert route.tool_format == declaration.tool_format
        assert route.cluster_smoke_required is True
        assert declaration.supports_sandbox_tests is True
        assert declaration.requires_cluster_smoke is True


def test_opencode_and_codex_adapter_symbols_are_declaration_only() -> None:
    instance = Instance(
        instance_id="demo__repo-1",
        repo="demo/repo",
        problem_statement="Fix the bug.",
        sif_path="/fake/path.sif",
    )
    for adapter in (OpenCodeLoopAdapter(), CodexLoopAdapter()):
        with pytest.raises(NotImplementedError, match="declaration-only"):
            adapter.rollout(instance)


def test_route_for_harness_rejects_unknown_harness() -> None:
    with pytest.raises(ValueError, match="unknown SWE harness"):
        route_for_harness("aider")


def test_harness_registry_rejects_unknown_status(tmp_path: Path) -> None:
    bad = tmp_path / "swe_harness_registry.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M2
harnesses:
  - harness_id: opencode
    nemo_gym_env: swe_agents_opencode
    mix: swe2
    adapter_class: nemotron.recipes.super3.milestones.m1_swe2.swe_multi_harness.OpenCodeLoopAdapter
    tool_format: opencode
    config_path: responses_api_agents/swe_agents/configs/swebench_opencode_training.yaml
    status: readyish
    cluster_smoke_required: true
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="status"):
        load_swe_harness_registry(bad)


def test_harness_registry_rejects_adapter_declaration_drift(tmp_path: Path) -> None:
    bad = tmp_path / "swe_harness_registry.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M2
harnesses:
  - harness_id: codex
    nemo_gym_env: swe_agents_codex
    mix: swe2
    adapter_class: wrong.CodexAdapter
    tool_format: codex
    config_path: responses_api_agents/swe_agents/configs/swebench_codex_training.yaml
    status: sandbox_declared
    cluster_smoke_required: true
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="adapter_class"):
        load_swe_harness_registry(bad)


def test_harness_registry_rejects_non_swe2_mix(tmp_path: Path) -> None:
    bad = tmp_path / "swe_harness_registry.yaml"
    bad.write_text(
        """schema_version: 1
milestone: M2
harnesses:
  - harness_id: opencode
    nemo_gym_env: swe_agents_opencode
    mix: swe1
    adapter_class: nemotron.recipes.super3.milestones.m1_swe2.swe_multi_harness.OpenCodeLoopAdapter
    tool_format: opencode
    config_path: responses_api_agents/swe_agents/configs/swebench_opencode_training.yaml
    status: sandbox_declared
    cluster_smoke_required: true
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="mix"):
        load_swe_harness_registry(bad)
