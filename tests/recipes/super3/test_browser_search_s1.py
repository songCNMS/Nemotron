"""Tests for task022 Session 1 browser/search scaffold.

Session 1 is deliberately sandbox-only: it registers the browser/search
record contract, BrowseComp-style converter, and an offline verifier
stub without launching Playwright/Chromium or requiring cluster access.
"""

from __future__ import annotations

from typing import Any

from nemotron.recipes.super3.milestones.m0_data_env.prepare_m0_assets import (  # noqa: E402
    BROWSER_SEARCH_TOOLS,
    CONVERTERS,
    DATA_REGISTRY_PATH,
    ENV_REGISTRY_PATH,
    SYSTEM_PROMPTS,
    load_yaml,
    transform_browsecomp_grounded,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec(env: str = "browsecomp_grounded") -> dict[str, Any]:
    return {
        "id": "m0_browsecomp_grounded",
        "environment": env,
        "domain": "browser_search",
        "hf_dataset": "synthetic/browsecomp-grounded-placeholder",
        "hf_config": None,
        "hf_split": "train",
        "hf_val_split": None,
        "hf_revision": "synthetic-test-spec",
        "source_url": "https://example.invalid/browsecomp-placeholder",
        "license": "placeholder-pending-legal-review",
        "converter": "browsecomp_grounded",
        "difficulty": "browser_search_hard",
        "reward_type": "browser_grounded_answer_stub",
        "contamination": "synthetic test spec only; pin source before adding data_registry row",
        "contamination_against": ["BrowseComp held-out", "browser/search eval baskets"],
        "milestone": "M0",
        "use_stage": ["M2 browser/search expansion"],
    }


def _row() -> dict[str, Any]:
    return {
        "id": "bc-1",
        "question": "Which rover first drilled into a Mars rock?",
        "answer": "Curiosity",
        "supporting_urls": ["https://mars.nasa.gov/msl/"],
        "allowed_domains": ["mars.nasa.gov"],
        "evidence": ["NASA describes Curiosity's first drilling sample on Mars."],
    }


def test_browser_search_prompts_and_converter_are_registered() -> None:
    assert "browser_qa" in SYSTEM_PROMPTS
    assert "browsecomp_grounded" in SYSTEM_PROMPTS
    assert CONVERTERS.get("browsecomp_grounded") is transform_browsecomp_grounded


def test_transform_browsecomp_grounded_emits_browser_tool_record() -> None:
    record = transform_browsecomp_grounded(_row(), _spec())

    assert record["environment"] == "browsecomp_grounded"
    assert record["expected_answer"] == "Curiosity"
    assert record["reward_config"]["verifier"] == "browser_grounded_answer_stub"
    assert record["extra_env_info"]["requires_live_browser"] is False
    assert record["extra_env_info"]["cluster_execution"] == "deferred_to_task022_session_3"
    assert record["extra_env_info"]["seed_urls"] == ["https://mars.nasa.gov/msl/"]
    assert record["extra_env_info"]["allowed_domains"] == ["mars.nasa.gov"]
    assert "Use browser/search tools" in record["responses_create_params"]["input"][1]["content"]
    tool_names = {tool["function"]["name"] for tool in record["responses_create_params"]["tools"]}
    assert tool_names == {tool["function"]["name"] for tool in BROWSER_SEARCH_TOOLS}


def test_transform_browsecomp_grounded_accepts_prompt_final_answer_aliases() -> None:
    row = {
        "prompt": "What company created the original Macintosh?",
        "final_answer": "Apple",
        "urls": "https://www.apple.com/newsroom/",
    }
    record = transform_browsecomp_grounded(row, _spec(env="browser_qa"))

    assert record["environment"] == "browser_qa"
    assert record["question"] == "What company created the original Macintosh?"
    assert record["expected_answer"] == "Apple"
    assert record["extra_env_info"]["seed_urls"] == ["https://www.apple.com/newsroom/"]


def test_transform_browsecomp_grounded_rejects_missing_question_or_answer() -> None:
    try:
        transform_browsecomp_grounded({"answer": "A"}, _spec())
    except ValueError as exc:
        assert "question" in str(exc)
    else:
        raise AssertionError("missing question should raise")

    try:
        transform_browsecomp_grounded({"question": "Q?"}, _spec())
    except ValueError as exc:
        assert "answer" in str(exc)
    else:
        raise AssertionError("missing answer should raise")


def test_browser_grounded_answer_stub_scores_offline_without_browser_runtime() -> None:
    record = transform_browsecomp_grounded(_row(), _spec())
    score, diagnostics = score_record(
        "The answer is Curiosity. Source: https://mars.nasa.gov/msl/",
        record,
    )

    assert score == 1.0
    assert diagnostics["grounded_answer_match"] is True
    assert diagnostics["citation_url_count"] == 1
    assert diagnostics["browser_trace_present"] is False
    assert diagnostics["cluster_execution"] == "deferred"


def test_browser_grounded_answer_stub_reports_no_match() -> None:
    record = transform_browsecomp_grounded(_row(), _spec())
    score, diagnostics = score_record("The answer is Perseverance.", record)

    assert score == 0.0
    assert diagnostics["grounded_answer_match"] is False
    assert diagnostics["citation_url_count"] == 0


def test_registry_consistency_holds_with_browser_search_env_rows() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_environment_registry_carries_browser_search_scaffold_rows() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    by_id = {env["id"]: env for env in env_registry["environments"]}

    assert {"browser_qa", "browsecomp_grounded"} <= set(by_id)
    for env_id in ("browser_qa", "browsecomp_grounded"):
        env = by_id[env_id]
        assert env["family"] == "browser_search"
        assert env["reward"]["verifier"] == "browser_grounded_answer_stub"
        assert env["resources"]["sandbox"] == "playwright_chromium_cluster_deferred"
        assert "browser_trace_present" in env["telemetry"]


def test_data_registry_defers_browsecomp_row_until_source_pin() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    ids = {dataset["id"] for dataset in data_registry["datasets"]}

    assert "m0_browsecomp_grounded" not in ids
