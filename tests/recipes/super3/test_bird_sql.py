"""Tests for the BIRD SQL → sql_text_to_query env + converter
(task057 Session 3).

Covers:

- `transform_bird_sql` happy path: question + gold SQL + db_id → record
- Output: user message embeds Database / Question / Evidence sections
- Alternate gold-SQL column conventions: `SQL` / `sql` / `query` /
  `gold_sql` all accepted
- Cross-schema metadata: `db_id` + `question_id` + `difficulty`
  preserved in extra_env_info (BIRD's cross-schema generalization
  property is its central eval signal)
- `normalize_sql` semantics: lowercase / whitespace-collapse / backtick
  strip / trailing semicolon removal
- `score_sql_execution_match` semantics: exact / contains / empty
  expected
- `score_record` dispatches sql_execution_match; emits sql_match +
  normalized_sql diagnostics
- Error surfaces: missing question / missing gold SQL / missing db_id
- Registry integration: env_registry row present; data_registry row
  deferred (Session 3.5)
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
    SYSTEM_PROMPTS,
    bird_sql_execution_context,
    load_yaml,
    normalize_sql,
    score_sql_execution_match,
    score_sql_execution_match_with_diagnostics,
    transform_bird_sql,
    validate_registries,
)
from nemotron.recipes.super3.milestones.m0_data_env.run_m0_health_baseline import (  # noqa: E402
    score_record,
)


def _spec(dataset_id: str) -> dict:
    """Build a synthetic spec for the BIRD env.

    The m0_bird_sql data_registry row is deferred (Session 3.5) — we
    use a synthetic spec matching the shape the converter expects."""
    if dataset_id == "m0_bird_sql":
        return {
            "id": "m0_bird_sql",
            "environment": "sql_text_to_query",
            "domain": "structured_query",
            "hf_dataset": "bird-bench/bird",
            "hf_config": None,
            "hf_split": "train",
            "hf_val_split": "validation",
            "hf_revision": "synthetic-test-spec",
            "source_url": "https://huggingface.co/datasets/bird-bench/bird",
            "license": "cc-by-sa-4.0",
            "converter": "bird_sql",
            "difficulty": "sql_text_to_query",
            "reward_type": "sql_execution_match",
            "contamination": "synthetic test spec",
            "contamination_against": ["BIRD mini_dev", "Spider"],
            "milestone": "M0",
            "use_stage": ["M0 data_env_foundation"],
        }
    registry = load_yaml(DATA_REGISTRY_PATH)
    for dataset in registry["datasets"]:
        if dataset["id"] == dataset_id:
            spec = dict(dataset)
            spec["milestone"] = registry["milestone"]
            return spec
    raise AssertionError(f"missing dataset {dataset_id}")


def _bird_row(
    *,
    question: str = "How many movies are in the database?",
    gold_sql: str = "SELECT COUNT(*) FROM movies;",
    db_id: str = "movies_4_directors",
    sql_key: str = "SQL",
    evidence: str | None = None,
    difficulty: str | None = "easy",
    question_id: int | None = 42,
) -> dict[str, Any]:
    """Synthesize a BIRD row in the publish-time format."""
    row: dict[str, Any] = {
        "question": question,
        "db_id": db_id,
        sql_key: gold_sql,
    }
    if question_id is not None:
        row["question_id"] = question_id
    if difficulty is not None:
        row["difficulty"] = difficulty
    if evidence is not None:
        row["evidence"] = evidence
    return row


# ---------- Module surface ----------


def test_system_prompt_for_sql_text_to_query_exists() -> None:
    assert "sql_text_to_query" in SYSTEM_PROMPTS
    assert "SQL" in SYSTEM_PROMPTS["sql_text_to_query"]


def test_converter_is_registered_in_converters_map() -> None:
    assert CONVERTERS.get("bird_sql") is transform_bird_sql


# ---------- Happy path ----------


def test_transform_emits_record_for_valid_bird_row() -> None:
    row = _bird_row()
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    assert record["environment"] == "sql_text_to_query"
    assert record["question"] == "How many movies are in the database?"
    assert record["expected_answer"] == "SELECT COUNT(*) FROM movies;"
    assert record["reward_config"]["verifier"] == "sql_execution_match"


def test_transform_embeds_database_and_question_in_user_message() -> None:
    row = _bird_row(db_id="finance_2024", question="Top 5 customers by revenue.")
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    user_content = record["responses_create_params"]["input"][1]["content"]
    assert "Database: finance_2024" in user_content
    assert "Question: Top 5 customers by revenue." in user_content


def test_transform_embeds_evidence_when_present() -> None:
    row = _bird_row(
        question="Q?",
        evidence="Hint: customers table has revenue column.",
    )
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    user_content = record["responses_create_params"]["input"][1]["content"]
    assert "Evidence:" in user_content
    assert "Hint: customers table" in user_content
    assert record["extra_env_info"]["has_evidence"] is True


def test_transform_omits_evidence_section_when_absent() -> None:
    row = _bird_row(question="Q?", evidence=None)
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    user_content = record["responses_create_params"]["input"][1]["content"]
    assert "Evidence:" not in user_content
    assert record["extra_env_info"]["has_evidence"] is False


# ---------- Alternate gold-SQL column conventions ----------


@pytest.mark.parametrize("sql_key", ["SQL", "sql", "query", "gold_sql"])
def test_transform_accepts_alternate_gold_sql_keys(sql_key: str) -> None:
    """BIRD snapshots ship the gold SQL under different keys per
    version. Converter must handle all four."""
    row = _bird_row(sql_key=sql_key, gold_sql=f"SELECT * FROM t_{sql_key};")
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    assert record["expected_answer"] == f"SELECT * FROM t_{sql_key};"


# ---------- Cross-schema metadata ----------


def test_transform_preserves_db_id_for_cross_schema_stratification() -> None:
    """BIRD's central eval signal is cross-schema generalization;
    db_id must propagate to extra_env_info so downstream can
    stratify per-schema."""
    row = _bird_row(db_id="schema_7")
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    assert record["extra_env_info"]["db_id"] == "schema_7"


def test_transform_preserves_question_id_and_difficulty() -> None:
    row = _bird_row(question_id=123, difficulty="hard")
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    assert record["extra_env_info"]["question_id"] == 123
    assert record["extra_env_info"]["difficulty"] == "hard"


def test_transform_handles_missing_difficulty() -> None:
    row = _bird_row(difficulty=None)
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    assert record["extra_env_info"]["difficulty"] is None


def test_transform_marks_sql_execution_unavailable_without_fixture_context() -> None:
    row = _bird_row()
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    sql_execution = record["extra_env_info"]["sql_execution"]
    assert sql_execution["engine"] == "sqlite"
    assert sql_execution["db_id"] == "movies_4_directors"
    assert sql_execution["available"] is False


def test_transform_carries_local_sqlite_execution_context_when_present() -> None:
    row = _bird_row(
        db_id="movies_4_directors",
        gold_sql="SELECT COUNT(*) FROM movies;",
    )
    row["schema_sql"] = "CREATE TABLE movies (id INTEGER, title TEXT);"
    row["fixture_rows"] = {
        "movies": [
            {"id": 1, "title": "A"},
            {"id": 2, "title": "B"},
        ]
    }
    record = transform_bird_sql(row, _spec("m0_bird_sql"))
    sql_execution = record["extra_env_info"]["sql_execution"]
    assert sql_execution["available"] is True
    assert sql_execution["schema_sql"].startswith("CREATE TABLE movies")
    assert len(sql_execution["fixture_rows"]["movies"]) == 2


def test_bird_sql_execution_context_accepts_schema_aliases() -> None:
    context = bird_sql_execution_context(
        {
            "sqlite_schema": "CREATE TABLE movies (id INTEGER);",
            "sqlite_fixture_rows": {"movies": [{"id": 1}]},
            "order_sensitive": True,
        },
        db_id="movies",
    )
    assert context["available"] is True
    assert context["schema_sql"] == "CREATE TABLE movies (id INTEGER);"
    assert context["order_sensitive"] is True


# ---------- normalize_sql ----------


def test_normalize_sql_lowercases_and_collapses_whitespace() -> None:
    assert normalize_sql("SELECT   COUNT(*)\nFROM\tmovies") == "select count(*) from movies"


def test_normalize_sql_strips_trailing_semicolon() -> None:
    assert normalize_sql("SELECT * FROM t;") == "select * from t"
    assert normalize_sql("SELECT * FROM t  ;  ") == "select * from t"


def test_normalize_sql_strips_backticks() -> None:
    """BIRD schemas mix backtick-quoted vs unquoted identifiers across
    rows; normalize for consistency."""
    assert normalize_sql("SELECT `id` FROM `movies`") == "select id from movies"


def test_normalize_sql_handles_none_and_empty() -> None:
    assert normalize_sql(None) == ""
    assert normalize_sql("") == ""
    assert normalize_sql("   ") == ""


# ---------- score_sql_execution_match ----------


def test_score_exact_match_returns_one() -> None:
    assert score_sql_execution_match("SELECT * FROM t;", "select * from t") == 1.0


def test_score_contains_match_returns_one() -> None:
    """Candidate may include the gold as a substring (e.g., wrapped in
    a CTE or with extra leading comment); contains-match accepts."""
    assert score_sql_execution_match(
        "WITH foo AS (SELECT 1) SELECT count(*) FROM movies",
        "select count(*) from movies",
    ) == 1.0


def test_score_no_match_returns_zero() -> None:
    assert score_sql_execution_match("SELECT * FROM unrelated", "SELECT * FROM movies") == 0.0


def test_score_empty_expected_returns_zero() -> None:
    """Empty gold SQL is a data-quality bug — never silently a pass."""
    assert score_sql_execution_match("SELECT * FROM t", "") == 0.0


def test_score_with_diagnostics_falls_back_to_normalized_sql_without_context() -> None:
    score, diagnostics = score_sql_execution_match_with_diagnostics(
        "SELECT * FROM t;",
        "select * from t",
    )
    assert score == 1.0
    assert diagnostics["sql_execution_mode"] == "normalized_sql"
    assert diagnostics["sql_match"] is True


def test_score_with_local_sqlite_execution_context_matches_result_rows() -> None:
    context = {
        "sql_execution": {
            "engine": "sqlite",
            "schema_sql": "CREATE TABLE movies (id INTEGER, genre TEXT);",
            "fixture_rows": {
                "movies": [
                    {"id": 1, "genre": "comedy"},
                    {"id": 2, "genre": "drama"},
                    {"id": 3, "genre": "comedy"},
                ]
            },
        }
    }
    score, diagnostics = score_sql_execution_match_with_diagnostics(
        "SELECT COUNT(*) FROM movies WHERE genre = 'comedy'",
        "SELECT COUNT(*) FROM movies WHERE genre = 'comedy'",
        context,
    )
    assert score == 1.0
    assert diagnostics["sql_execution_mode"] == "local_sqlite"
    assert diagnostics["sql_execution_match"] is True


def test_score_with_local_sqlite_execution_context_detects_result_mismatch() -> None:
    context = {
        "sql_execution": {
            "engine": "sqlite",
            "schema_sql": "CREATE TABLE movies (id INTEGER);",
            "fixture_rows": {"movies": [{"id": 1}, {"id": 2}]},
        }
    }
    score, diagnostics = score_sql_execution_match_with_diagnostics(
        "SELECT COUNT(*) FROM movies WHERE id > 1",
        "SELECT COUNT(*) FROM movies",
        context,
    )
    assert score == 0.0
    assert diagnostics["sql_execution_mode"] == "local_sqlite"
    assert diagnostics["sql_execution_match"] is False


def test_score_with_local_sqlite_rejects_non_readonly_candidate() -> None:
    context = {
        "sql_execution": {
            "engine": "sqlite",
            "schema_sql": "CREATE TABLE movies (id INTEGER);",
            "fixture_rows": {"movies": [{"id": 1}]},
        }
    }
    score, diagnostics = score_sql_execution_match_with_diagnostics(
        "DELETE FROM movies",
        "SELECT COUNT(*) FROM movies",
        context,
    )
    assert score == 0.0
    assert diagnostics["candidate_error"] == "only SELECT/WITH queries are allowed"


def test_score_with_local_sqlite_rejects_unsafe_schema_token() -> None:
    context = {
        "sql_execution": {
            "engine": "sqlite",
            "schema_sql": "ATTACH DATABASE '/tmp/other.db' AS other;",
        }
    }
    score, diagnostics = score_sql_execution_match_with_diagnostics(
        "SELECT 1",
        "SELECT 1",
        context,
    )
    assert score == 0.0
    assert diagnostics["sql_execution_setup_error"] == (
        "schema_sql contains an unsafe SQLite token"
    )


# ---------- score_record dispatch ----------


def test_score_record_dispatches_sql_execution_match() -> None:
    record = {
        "environment": "sql_text_to_query",
        "expected_answer": "SELECT * FROM movies;",
        "reward_config": {"verifier": "sql_execution_match"},
        "extra_env_info": {"db_id": "movies_4"},
    }
    score, diagnostics = score_record("SELECT * FROM movies", record)
    assert score == 1.0
    assert diagnostics["sql_match"] is True
    assert "normalized_sql" in diagnostics


def test_score_record_sql_execution_match_no_match() -> None:
    record = {
        "environment": "sql_text_to_query",
        "expected_answer": "SELECT COUNT(*) FROM movies",
        "reward_config": {"verifier": "sql_execution_match"},
        "extra_env_info": {"db_id": "movies_4"},
    }
    score, diagnostics = score_record("INSERT INTO movies VALUES (1)", record)
    assert score == 0.0
    assert diagnostics["sql_match"] is False


def test_score_record_uses_local_sqlite_execution_context() -> None:
    record = {
        "environment": "sql_text_to_query",
        "expected_answer": "SELECT COUNT(*) FROM movies",
        "reward_config": {"verifier": "sql_execution_match"},
        "extra_env_info": {
            "db_id": "movies_4",
            "sql_execution": {
                "engine": "sqlite",
                "schema_sql": "CREATE TABLE movies (id INTEGER);",
                "fixture_rows": {"movies": [{"id": 1}, {"id": 2}]},
            },
        },
    }
    score, diagnostics = score_record("SELECT COUNT(*) FROM movies", record)
    assert score == 1.0
    assert diagnostics["sql_match"] is True
    assert diagnostics["sql_execution_mode"] == "local_sqlite"


# ---------- Error surfaces ----------


def test_transform_rejects_missing_question() -> None:
    row = _bird_row(question="")
    with pytest.raises(ValueError, match="question"):
        transform_bird_sql(row, _spec("m0_bird_sql"))


def test_transform_rejects_missing_gold_sql() -> None:
    row: dict[str, Any] = {"question": "Q?", "db_id": "s1"}  # no SQL/sql/query/gold_sql
    with pytest.raises(ValueError, match="gold SQL"):
        transform_bird_sql(row, _spec("m0_bird_sql"))


def test_transform_rejects_missing_db_id() -> None:
    row = _bird_row(db_id="")
    with pytest.raises(ValueError, match="db_id"):
        transform_bird_sql(row, _spec("m0_bird_sql"))


# ---------- Registry integration ----------


def test_registry_consistency_holds_with_new_sql_env() -> None:
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    validate_registries(data_registry, env_registry)


def test_env_registry_carries_new_sql_text_to_query_env() -> None:
    env_registry = load_yaml(ENV_REGISTRY_PATH)
    env = next(
        (e for e in env_registry["environments"] if e["id"] == "sql_text_to_query"),
        None,
    )
    assert env is not None
    assert env["family"] == "structured_query"
    assert env["reward"]["verifier"] == "sql_execution_match"
    assert env["resources"]["sandbox"] == "sql_sqlite"
    assert env["resources"]["tools"] == ["sqlite3"]
    required = env["health_check"]["required_fields"]
    assert any("db_id" in r for r in required)


def test_data_registry_does_not_yet_carry_m0_bird_sql_row() -> None:
    """task057 Session 3 defers the data_registry row to Session 3.5
    pending a real BIRD commit SHA pin (CC-BY-SA-4.0 license — task058
    cascade audit will flag at row-add time). Lock the deferral."""
    data_registry = load_yaml(DATA_REGISTRY_PATH)
    rows = [d for d in data_registry["datasets"] if d["id"] == "m0_bird_sql"]
    assert rows == [], (
        "m0_bird_sql row should NOT be in data_registry yet — pin BIRD "
        "commit SHA + lock mini_dev contamination split first"
    )
