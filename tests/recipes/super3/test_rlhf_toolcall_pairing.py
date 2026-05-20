"""Tests for the RLHF tool-call pairing converter (task068 Session 2).

Covers:

- `default_relevance_filter` — keyword match accepts; no keyword
  rejects; case-insensitive
- `default_gold_call_finder` — function-name match; required-arg
  tiebreak picks the most grounded candidate; no match returns None
- `_extract_function_call` for both Hermes formats (`tool_calls`-list
  + direct {name, arguments})
- `is_contaminated` — exact match / 5-gram match / clean prompt
- `build_eval_prompt_set` — produces normalized + 5-gram set
- `transform_rlhf_toolcall_pairing` orchestrator — filter order
  (relevance → match → contamination); output row shape matches
  Session 1 design doc reference; metadata.contamination_against
  carries all 4 eval baskets
"""

from __future__ import annotations

from typing import Any

import pytest


from nemotron.recipes.super3.milestones.m0_data_env.rlhf_toolcall_pairing import (  # noqa: E402
    PAIRED_CONTAMINATION_AGAINST,
    RELEVANCE_KEYWORDS,
    _extract_function_call,
    build_eval_prompt_set,
    default_gold_call_finder,
    default_relevance_filter,
    is_contaminated,
    transform_rlhf_toolcall_pairing,
)


def _hermes_row(
    *,
    function_name: str,
    arguments: dict[str, Any] | None = None,
    source_id: str = "h1",
    include_schema: bool = True,
) -> dict[str, Any]:
    """Synthesize a Hermes M0 row in the newer `tool_calls`-list format."""
    arguments = arguments or {}
    row: dict[str, Any] = {
        "id": source_id,
        "expected_answer": {
            "tool_calls": [
                {
                    "function": {
                        "name": function_name,
                        "arguments": arguments,
                    }
                }
            ]
        },
    }
    if include_schema:
        row["responses_create_params"] = {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "description": f"Mock {function_name} tool.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                arg: {"type": "string"}
                                for arg in arguments
                            },
                            "required": list(arguments),
                        },
                    },
                }
            ],
        }
    return row


def _helpsteer_row(prompt: str, row_id: str = "hs1") -> dict[str, Any]:
    return {"id": row_id, "prompt": prompt}


# ---------- Constants ----------


def test_paired_contamination_against_covers_session1_design() -> None:
    """Session 1 design doc names 4 eval baskets — lock the tuple."""
    assert PAIRED_CONTAMINATION_AGAINST == (
        "BFCL",
        "TauBench airline",
        "MCP-Mark",
        "HelpSteer1",
    )


def test_relevance_keywords_cover_design_doc_primitives() -> None:
    """Session 1 design lists specific keyword primitives; pin them so
    a drift in the keyword list is intentional."""
    for required in ("look up", "compute", "translate", "weather"):
        assert required in RELEVANCE_KEYWORDS


# ---------- Relevance filter ----------


def test_relevance_filter_accepts_keyword_match() -> None:
    assert default_relevance_filter("Look up the weather in Tokyo.") is True
    assert default_relevance_filter("Compute the area of a circle.") is True
    assert default_relevance_filter("Find me a restaurant near Times Square.") is True


def test_relevance_filter_rejects_no_keyword() -> None:
    assert default_relevance_filter("Compose a haiku about cherry blossoms.") is False
    assert default_relevance_filter("Tell me a joke.") is False


def test_relevance_filter_is_case_insensitive() -> None:
    assert default_relevance_filter("LOOK UP THE WEATHER") is True


# ---------- _extract_function_call ----------


def test_extract_function_call_from_tool_calls_list_format() -> None:
    row = _hermes_row(function_name="get_weather", arguments={"location": "Tokyo"})
    fn = _extract_function_call(row)
    assert fn is not None
    assert fn["name"] == "get_weather"
    assert fn["arguments"] == {"location": "Tokyo"}


def test_extract_function_call_from_direct_format() -> None:
    """Older Hermes rows store the call directly under expected_answer."""
    row = {
        "expected_answer": {
            "name": "get_weather",
            "arguments": {"location": "Paris"},
        }
    }
    fn = _extract_function_call(row)
    assert fn is not None
    assert fn["name"] == "get_weather"


def test_extract_function_call_returns_none_for_no_call() -> None:
    row = {"expected_answer": "just a string"}
    assert _extract_function_call(row) is None


# ---------- default_gold_call_finder ----------


def test_gold_call_finder_matches_by_function_name_substring() -> None:
    corpus = [
        _hermes_row(function_name="search_restaurant", source_id="h1"),
        _hermes_row(function_name="get_weather", source_id="h2"),
    ]
    prompt = "Look up the weather in Tokyo."
    match = default_gold_call_finder(prompt, corpus)
    assert match is not None
    assert match["id"] == "h2"


def test_gold_call_finder_tiebreaks_by_required_arg_overlap() -> None:
    """Two candidates' function names both match. The one whose
    required-arg names also appear in the prompt wins — more grounded."""
    corpus = [
        _hermes_row(
            function_name="get_weather",
            arguments={"location": "X"},
            source_id="h_with_location",
        ),
        _hermes_row(
            function_name="get_weather",
            arguments={"zip_code": "X"},
            source_id="h_with_zip",
        ),
    ]
    prompt = "Get the weather for my location."
    match = default_gold_call_finder(prompt, corpus)
    assert match is not None
    assert match["id"] == "h_with_location"


def test_gold_call_finder_handles_underscore_function_names() -> None:
    """`get_weather` should match prompts mentioning "weather" alone
    (trailing-fragment heuristic)."""
    corpus = [_hermes_row(function_name="get_weather", source_id="h1")]
    prompt = "What is the weather?"
    match = default_gold_call_finder(prompt, corpus)
    assert match is not None
    assert match["id"] == "h1"


def test_gold_call_finder_returns_none_when_no_match() -> None:
    corpus = [_hermes_row(function_name="get_weather")]
    prompt = "Compose a haiku."
    assert default_gold_call_finder(prompt, corpus) is None


def test_gold_call_finder_skips_hermes_rows_without_function_call() -> None:
    """Hermes corpus may have malformed rows; finder must skip them
    without raising."""
    corpus = [
        {"id": "h_bad", "expected_answer": "not a tool call"},
        _hermes_row(function_name="get_weather", source_id="h_good"),
    ]
    prompt = "Look up the weather."
    match = default_gold_call_finder(prompt, corpus)
    assert match is not None
    assert match["id"] == "h_good"


# ---------- Contamination ----------


def test_is_contaminated_exact_normalized_match() -> None:
    eval_set = build_eval_prompt_set(["Translate hello to French!"])
    # Same prompt, different casing + punctuation — normalized form
    # should be identical and trigger contamination
    assert is_contaminated("translate hello to french", eval_set) is True


def test_is_contaminated_five_gram_overlap() -> None:
    """A novel HelpSteer-2 prompt that shares a 5-word phrase with an
    eval prompt should be caught as contaminated."""
    eval_set = build_eval_prompt_set(
        ["Please translate the following passenger announcement to Spanish."]
    )
    candidate = "I need you to translate the following passenger announcement now."
    assert is_contaminated(candidate, eval_set) is True


def test_is_contaminated_clean_prompt_passes() -> None:
    eval_set = build_eval_prompt_set(
        ["Translate this airline announcement to French."]
    )
    candidate = "Look up the weather in Tokyo."
    assert is_contaminated(candidate, eval_set) is False


def test_is_contaminated_empty_eval_set_never_contaminates() -> None:
    assert is_contaminated("anything goes", frozenset()) is False


def test_is_contaminated_empty_prompt_not_contaminated() -> None:
    eval_set = build_eval_prompt_set(["foo bar baz qux quux"])
    assert is_contaminated("", eval_set) is False
    assert is_contaminated("   ", eval_set) is False


def test_build_eval_prompt_set_normalizes_and_adds_five_grams() -> None:
    s = build_eval_prompt_set(["This is a test of the system."])
    # Normalized full prompt
    assert "this is a test of the system" in s
    # 5-grams (this is a test of, is a test of the, ...)
    assert "this is a test of" in s
    assert "is a test of the" in s


# ---------- Orchestrator ----------


def test_orchestrator_emits_paired_row_for_clean_match() -> None:
    helpsteer = [_helpsteer_row("Look up the weather in Tokyo.")]
    hermes = [_hermes_row(function_name="get_weather", arguments={"location": "Tokyo"})]
    eval_set = frozenset()
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=eval_set
        )
    )
    assert len(rows) == 1
    row = rows[0]
    # task068 Session 3: converter now emits the M0 env name; the
    # M1 RLHF bridge maps it to the NeMo-Gym
    # `single_step_tool_use_with_argument_comparison` env at tag-record
    # time.
    assert row["environment"] == "rlhf_toolcall_paired"
    assert row["reward_config"]["verifier"] == "argument_match"
    assert row["expected_answer"]["name"] == "get_weather"
    assert row["expected_answer"]["arguments"] == {"location": "Tokyo"}
    assert row["metadata"]["contamination_against"] == list(
        PAIRED_CONTAMINATION_AGAINST
    )


def test_orchestrator_drops_prompts_failing_relevance_filter() -> None:
    """Example 2 from Session 1 design — eligible-but-no-Hermes-match
    inverts to non-eligible here (no keyword)."""
    helpsteer = [_helpsteer_row("Compose a haiku about cherry blossoms.")]
    hermes = [_hermes_row(function_name="get_weather")]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    assert rows == []


def test_orchestrator_drops_prompts_with_no_hermes_match() -> None:
    """Eligible (passes relevance filter) but no function-name match in
    the Hermes corpus → dropped."""
    helpsteer = [_helpsteer_row("Compute the area of a triangle.")]
    # Hermes corpus has nothing related to triangles or computation
    hermes = [_hermes_row(function_name="get_weather")]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    assert rows == []


def test_orchestrator_drops_contaminated_prompts() -> None:
    """Example 3 from Session 1 design: eligible + match but
    contaminated → dropped."""
    helpsteer = [_helpsteer_row("Translate the following passenger announcement.")]
    hermes = [_hermes_row(function_name="translate", arguments={"text": "x"})]
    eval_set = build_eval_prompt_set(
        ["Please translate the following passenger announcement to Spanish."]
    )
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=eval_set
        )
    )
    assert rows == []


def test_orchestrator_yields_kept_after_all_filters() -> None:
    """Example 4 from Session 1 design: passes all 3 filters → yielded."""
    helpsteer = [_helpsteer_row("Find me a restaurant near Times Square.")]
    hermes = [
        _hermes_row(
            function_name="search_restaurant",
            arguments={"location": "Times Square"},
            source_id="h_restaurant",
        )
    ]
    eval_set = frozenset()
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=eval_set
        )
    )
    assert len(rows) == 1
    assert rows[0]["expected_answer"]["name"] == "search_restaurant"


def test_orchestrator_skips_empty_prompts() -> None:
    helpsteer = [
        {"id": "h1", "prompt": ""},
        {"id": "h2"},  # no prompt field at all
        _helpsteer_row("Look up the weather."),
    ]
    hermes = [_hermes_row(function_name="get_weather")]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    assert len(rows) == 1
    assert rows[0]["extra_env_info"]["source_helpsteer2_id"] != ""


def test_orchestrator_propagates_source_ids_to_extra_env_info() -> None:
    """For audit / debugging: each paired row records both upstream
    row IDs so a downstream consumer can trace back."""
    helpsteer = [_helpsteer_row("Look up the weather.", row_id="hs_42")]
    hermes = [_hermes_row(function_name="get_weather", source_id="hermes_99")]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    assert rows[0]["extra_env_info"]["source_helpsteer2_id"] == "hs_42"
    assert rows[0]["extra_env_info"]["source_hermes_id"] == "hermes_99"


def test_orchestrator_attaches_tool_schema_from_hermes_row() -> None:
    """Output row's responses_create_params.tools should carry the
    schema matching the gold function name."""
    helpsteer = [_helpsteer_row("Look up the weather in Tokyo.")]
    hermes = [_hermes_row(function_name="get_weather", arguments={"location": "Tokyo"})]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    tools = rows[0]["responses_create_params"]["tools"]
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "get_weather"


def test_orchestrator_synthesises_minimal_schema_when_missing() -> None:
    """A Hermes row without an explicit tool schema in responses_create_params
    still produces a paired row — converter synthesizes a minimal schema
    so the output is well-formed."""
    helpsteer = [_helpsteer_row("Look up the weather.")]
    hermes = [
        _hermes_row(
            function_name="get_weather",
            include_schema=False,  # no responses_create_params.tools
        )
    ]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    assert len(rows) == 1
    tools = rows[0]["responses_create_params"]["tools"]
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "get_weather"


def test_orchestrator_accepts_custom_relevance_filter() -> None:
    """Operators can inject a stricter filter; only prompts passing the
    custom filter get paired."""
    helpsteer = [
        _helpsteer_row("Look up the weather.", row_id="hs_keep"),
        _helpsteer_row("Find me a restaurant.", row_id="hs_drop"),
    ]
    hermes = [
        _hermes_row(function_name="get_weather", source_id="h_weather"),
        _hermes_row(function_name="search_restaurant", source_id="h_restaurant"),
    ]

    def only_weather(prompt: str) -> bool:
        return "weather" in prompt.lower()

    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer,
            hermes_corpus=hermes,
            eval_prompt_set=frozenset(),
            relevance_filter=only_weather,
        )
    )
    assert len(rows) == 1
    assert rows[0]["extra_env_info"]["source_helpsteer2_id"] == "hs_keep"


def test_orchestrator_accepts_custom_gold_call_finder() -> None:
    """Operators can inject a different sourcing strategy; the converter
    just orchestrates."""
    helpsteer = [_helpsteer_row("Look up the weather.")]
    hermes = [_hermes_row(function_name="get_weather", source_id="h1")]

    seen_calls: list[str] = []

    def custom_finder(prompt: str, corpus):  # type: ignore[no-untyped-def]
        seen_calls.append(prompt)
        # Always return None to force a drop — proves the finder was
        # consulted even when no row matches
        return None

    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer,
            hermes_corpus=hermes,
            eval_prompt_set=frozenset(),
            gold_call_finder=custom_finder,
        )
    )
    assert rows == []
    assert seen_calls == ["Look up the weather."]


def test_orchestrator_match_strategy_metadata_lock() -> None:
    """The output's `match_strategy` field is "function_name_overlap"
    for the default finder. Locking this makes future strategy changes
    explicit."""
    helpsteer = [_helpsteer_row("Look up the weather.")]
    hermes = [_hermes_row(function_name="get_weather")]
    rows = list(
        transform_rlhf_toolcall_pairing(
            helpsteer, hermes_corpus=hermes, eval_prompt_set=frozenset()
        )
    )
    assert rows[0]["extra_env_info"]["match_strategy"] == "function_name_overlap"
